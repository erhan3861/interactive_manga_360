import os
import shutil
from PIL import Image, ImageSequence, ImageDraw

WEBP_PATH = r"C:\Users\hp\AppData\Local\Comfy-Desktop\ComfyUI-Shared\output\MATLOWAI_ORB360_Ref2VA_00001_.webp"
FRAMES_DIR = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames_orb360"
MAIN_FRAMES_DIR = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames"
COMPARE_IMAGE = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\compare_angles_orb360.png"
MP4_OUTPUT = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\orbit_orb360.mp4"

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(MAIN_FRAMES_DIR, exist_ok=True)

print(f"[+] Loading animated WebP from: {WEBP_PATH}")
im = Image.open(WEBP_PATH)

frames = []
for i, frame in enumerate(ImageSequence.Iterator(im)):
    frame_rgb = frame.convert("RGB")
    frame_name = f"frame_{i:04d}.png"
    main_frame_name = f"frame_{i:03d}.png"
    
    # Save to frames_orb360
    frame_rgb.save(os.path.join(FRAMES_DIR, frame_name))
    # Also sync directly to main frames directory for Three.js
    frame_rgb.save(os.path.join(MAIN_FRAMES_DIR, main_frame_name))
    frames.append(frame_rgb)

total_frames = len(frames)
print(f"[+] Total frames extracted and synced: {total_frames}")

# Create contact sheet with 4 angles (0 deg, 90 deg, 180 deg, 270 deg)
if total_frames > 0:
    indices = [0, total_frames // 4, total_frames // 2, (3 * total_frames) // 4]
    labels = ["Frame 0: 0 deg (Front)", f"Frame {indices[1]}: 90 deg (Side Profile)", f"Frame {indices[2]}: 180 deg (Back View)", f"Frame {indices[3]}: 270 deg (Opposite Side)"]
    
    sample_imgs = []
    for idx, lbl in zip(indices, labels):
        sample = frames[idx].copy()
        draw = ImageDraw.Draw(sample)
        # Draw background banner for label
        draw.rectangle([10, 10, 480, 50], fill=(0, 0, 0, 180))
        draw.text((20, 20), lbl, fill=(255, 230, 0))
        sample_imgs.append(sample)
        
    w, h = sample_imgs[0].size
    contact_sheet = Image.new("RGB", (w * 2, h * 2))
    contact_sheet.paste(sample_imgs[0], (0, 0))
    contact_sheet.paste(sample_imgs[1], (w, 0))
    contact_sheet.paste(sample_imgs[2], (0, h))
    contact_sheet.paste(sample_imgs[3], (w, h))
    contact_sheet.save(COMPARE_IMAGE)
    print(f"[+] 4-angle 360 orbit comparison saved to: {COMPARE_IMAGE}")

# Convert to MP4 using OpenCV or imageio
try:
    import cv2
    w, h = frames[0].size
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(MP4_OUTPUT, fourcc, 24.0, (w, h))
    for f in frames:
        import numpy as np
        frame_cv = cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR)
        out.write(frame_cv)
    out.release()
    print(f"[+] Video successfully written to: {MP4_OUTPUT}")
except Exception as e:
    print(f"[*] OpenCV MP4 write note: {e}")
