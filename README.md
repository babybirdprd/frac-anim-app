How This Works
Upload a ZIP containing your PNG frames.
The script unzips them into a temporary folder.
It renames them in a simple sequence (frame_0001.png, frame_0002.png, etc.) so FFmpeg can read them via frame_%04d.png.
Choose Frame Rate (30 or 60).
Choose Scaling (no scaling, 512×512, or 100×100).
Set Bitrate (e.g. 200k).
Click “Encode to WebM.”
The app runs a two-pass encode.
Returns either the path to the .webm file or a warning/error message.
Check “Status / Info.”
If the file is under 256 KB, you’ll see a path to the final .webm.
If over 256 KB, it warns you but still gives a path.
Click “Download WebM.”
Gradio will provide a download link if a valid file was produced.
Note: For local usage, Gradio spawns a local server at http://127.0.0.1:7860 (by default). You can open that in your browser to use the UI. If you want to share publicly, you can enable the share=True flag in demo.launch() or deploy on a platform like Hugging Face Spaces.

Usage Tips
Large Sequences

If you have many frames or large frames, uploading a big ZIP might be slow.
If this is local, it’s fine—just keep an eye on disk usage.
Two-Pass for Consistency

This approach is still your best bet for hitting a stable, predictable file size.
If it’s still too big, lower the bitrate or reduce resolution/fps.
No Audio

We’re using -an, so no audio track is included.
Alpha

We keep -pix_fmt yuva420p and -auto-alt-ref 0 for VP9 alpha.
File Size Check

After encoding, we check if the .webm is bigger than 256 KB.
You’ll see a warning if it is.
