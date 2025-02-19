from PIL import Image, ImageDraw
import os
import zipfile

def create_dummy_frames(num_frames=10, width=512, height=512, output_dir='dummy_frames'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i in range(num_frames):
        # Create an image with a transparent background
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Draw a moving semi-transparent red circle for visual interest
        radius = 50
        x = int((width - 2 * radius) * i / (num_frames - 1)) + radius
        y = height // 2
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 0, 0, 128))
        frame_filename = os.path.join(output_dir, f"frame_{i+1:04d}.png")
        img.save(frame_filename)
    # Zip the generated frames
    zip_filename = "dummy_frames.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    return zip_filename

if __name__ == "__main__":
    zip_path = create_dummy_frames(num_frames=10)
    print("Created test zip file:", zip_path)
