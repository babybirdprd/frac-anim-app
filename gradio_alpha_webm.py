import os
import shutil
import tempfile
import subprocess
import gradio as gr

def encode_webm(
    zip_file,       # The uploaded zip of PNG frames
    frame_rate,     # "30" or "60"
    scale_option,   # "512x512", "100x100", or "No scaling"
    video_bitrate,  # e.g. "200k"
):
    """
    Takes a zip file of PNG frames (with alpha),
    does a two-pass VP9 encode with alpha (no audio),
    optionally scales to 512x512 or 100x100,
    returns a path to the final .webm file.
    """
    # Create a temp directory
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, "output.webm")
    stats_file = os.path.join(temp_dir, "ffmpeg2pass.log")

    # Unzip the frames into temp_dir
    if zip_file is None:
        return None
    
    zip_input_path = zip_file.name
    shutil.unpack_archive(zip_input_path, temp_dir)

    # Now we have a bunch of PNGs in temp_dir. We need an ffmpeg pattern.
    # Let's assume frames are named something like frame_0001.png, etc.
    # We'll guess or force them to a sorted naming if needed.
    # For simplicity, let's rename them to frame_%04d.png
    # in alphabetical order:
    all_files = sorted(os.listdir(temp_dir))
    png_files = [f for f in all_files if f.lower().endswith(".png")]
    if not png_files:
        return "No PNG files found in the zip."

    # rename them in order so we have frame_0001.png, frame_0002.png, etc.
    for i, f in enumerate(png_files, start=1):
        src = os.path.join(temp_dir, f)
        dst = os.path.join(temp_dir, f"frame_{i:04d}.png")
        os.rename(src, dst)

    input_pattern = os.path.join(temp_dir, "frame_%04d.png")

    # Build scale filter if needed
    vf_filter = None
    if scale_option == "512x512":
        vf_filter = "scale=512:512"
    elif scale_option == "100x100":
        vf_filter = "scale=100:100"

    # Pass 1 command
    pass1_cmd = [
        "ffmpeg", "-y",
        "-framerate", frame_rate,
        "-i", input_pattern
    ]
    if vf_filter:
        pass1_cmd += ["-vf", vf_filter]
    pass1_cmd += [
        "-c:v", "libvpx-vp9",
        "-b:v", video_bitrate,
        "-minrate", video_bitrate,
        "-maxrate", video_bitrate,
        "-pix_fmt", "yuva420p",
        "-auto-alt-ref", "0",
        "-pass", "1",
        "-an",
        "-f", "null",
        os.devnull if os.name != "nt" else "NUL"
    ]

    # Pass 2 command
    pass2_cmd = [
        "ffmpeg", "-y",
        "-framerate", frame_rate,
        "-i", input_pattern
    ]
    if vf_filter:
        pass2_cmd += ["-vf", vf_filter]
    pass2_cmd += [
        "-c:v", "libvpx-vp9",
        "-b:v", video_bitrate,
        "-minrate", video_bitrate,
        "-maxrate", video_bitrate,
        "-pix_fmt", "yuva420p",
        "-auto-alt-ref", "0",
        "-pass", "2",
        "-an",
        output_file
    ]

    try:
        # Run pass 1
        subprocess.run(pass1_cmd, check=True)
        # Run pass 2
        subprocess.run(pass2_cmd, check=True)

        # Clean up stats file
        if os.path.exists(stats_file):
            os.remove(stats_file)

        # Check size
        size_kb = os.path.getsize(output_file) / 1024
        if size_kb > 256:
            return f"Warning: final file is {size_kb:.1f} KB (> 256 KB). Download anyway:\n{output_file}"
        else:
            return output_file
    except subprocess.CalledProcessError as e:
        return f"Error: {str(e)}"


def download_webm(webm_path):
    """
    Gradio expects a function that returns a path or file-like object
    to serve as a downloadable. We'll just return the same path we got.
    """
    if not webm_path or not os.path.exists(webm_path):
        return None
    return webm_path


# Build the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Alpha WebM Encoder (Two-Pass VP9) - Gradio Demo")

    with gr.Row():
        zip_input = gr.File(label="Upload a ZIP of PNG frames (with alpha)")

        with gr.Column():
            frame_rate = gr.Radio(
                choices=["30", "60"],
                value="30",
                label="Frame Rate"
            )
            scale_option = gr.Radio(
                choices=["No scaling", "512x512", "100x100"],
                value="512x512",
                label="Scaling"
            )
            video_bitrate = gr.Textbox(
                value="200k",
                label="Video Bitrate (e.g. 200k)"
            )

    encode_button = gr.Button("Encode to WebM")
    result_text = gr.Textbox(label="Status / Info", interactive=False)
    download_button = gr.Button("Download WebM")
    download_file = gr.File(label="Downloadable WebM", interactive=False)

    def encode_and_report(zip_file, frame_rate, scale_option, video_bitrate):
        webm_path_or_msg = encode_webm(zip_file, frame_rate, scale_option, video_bitrate)
        return str(webm_path_or_msg)

    encode_button.click(
        fn=encode_and_report,
        inputs=[zip_input, frame_rate, scale_option, video_bitrate],
        outputs=result_text
    )

    def do_download(path_str):
        # If the string starts with 'Warning:' or 'Error:', there's no actual file to return
        if path_str.startswith("Warning: final file") or path_str.startswith("Error"):
            # Attempt to parse out the file path after a newline
            lines = path_str.split("\n")
            if len(lines) > 1 and os.path.exists(lines[-1]):
                return lines[-1]
            else:
                return None
        if os.path.exists(path_str):
            return path_str
        return None

    download_button.click(
        fn=do_download,
        inputs=result_text,
        outputs=download_file
    )

demo.launch()
