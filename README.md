# WebM Encoder

This script allows you to easily create WebM videos from PNG frame sequences.

## How It Works

1. Upload a ZIP containing your PNG frames.
2. The script unzips them into a temporary folder and renames them sequentially.
3. Choose Frame Rate (30 or 60 fps).
4. Select Scaling options (no scaling, 512×512, or 100×100).
5. Set Bitrate (e.g., 200k).
6. Click "Encode to WebM" to run a two-pass encode.
7. The app returns the path to the .webm file or a warning/error message.
8. Check "Status / Info" for the file path or warnings.
9. Click "Download WebM" to get the final file.

## Usage Tips

### Large Sequences
For many or large frames, be mindful of disk usage when uploading big ZIP files.

### Two-Pass Encoding
This method ensures stable and predictable file sizes. Adjust bitrate or reduce resolution/fps if the file is too large.

### No Audio
The script uses `-an`, so no audio track is included.

### Alpha Channel
We maintain `-pix_fmt yuva420p` and `-auto-alt-ref 0` for VP9 alpha support.

### File Size Check
The script warns you if the output .webm is larger than 256 KB.

## Local Usage
Gradio spawns a local server at http://127.0.0.1:7860 by default. Open this in your browser to use the UI.

## Public Sharing
Enable `share=True` in `demo.launch()` or deploy on platforms like Hugging Face Spaces for public access.
