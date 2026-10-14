import os
import sys
import time
from PIL import Image, ImageSequence, ImageDraw

OUTPUT_DIR = r"C:\Users\hp\AppData\Local\Comfy-Desktop\ComfyUI-Shared\output"
TARGET_WEBP = os.path.join(OUTPUT_DIR, "MATLOWAI_ORB360_Scene05_00001_.webp")
FRAMES_DIR = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames_scene05"
COMPARE_IMAGE = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\compare_angles_scene05.png"
MP4_OUTPUT = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\orbit_scene05.mp4"

os.makedirs(FRAMES_DIR, exist_ok=True)

def process_output():
    print(f"[+] Output detected and validated: {TARGET_WEBP}")
    im = Image.open(TARGET_WEBP)
    
    frames = []
    for i, frame in enumerate(ImageSequence.Iterator(im)):
        frame_rgb = frame.convert("RGB")
        frame_name = f"frame_{i:04d}.png"
        frame_rgb.save(os.path.join(FRAMES_DIR, frame_name))
        frames.append(frame_rgb)
        
    total_frames = len(frames)
    print(f"[+] Total Scene 05 frames extracted: {total_frames}")
    
    if total_frames > 0:
        indices = [0, total_frames // 4, total_frames // 2, (3 * total_frames) // 4]
        labels = [
            "Frame 0: 0 deg (Front - Kaplumbaga Terbiyecisi)",
            f"Frame {indices[1]}: 90 deg (Side Profile)",
            f"Frame {indices[2]}: 180 deg (Back Angle)",
            f"Frame {indices[3]}: 270 deg (Opposite Side)"
        ]
        
        sample_imgs = []
        for idx, lbl in zip(indices, labels):
            sample = frames[idx].copy()
            draw = ImageDraw.Draw(sample)
            draw.rectangle([10, 10, 520, 50], fill=(0, 0, 0, 180))
            draw.text((20, 20), lbl, fill=(255, 230, 0))
            sample_imgs.append(sample)
            
        w, h = sample_imgs[0].size
        contact_sheet = Image.new("RGB", (w * 2, h * 2))
        contact_sheet.paste(sample_imgs[0], (0, 0))
        contact_sheet.paste(sample_imgs[1], (w, 0))
        contact_sheet.paste(sample_imgs[2], (0, h))
        contact_sheet.paste(sample_imgs[3], (w, h))
        contact_sheet.save(COMPARE_IMAGE)
        print(f"[+] Scene 05 4-angle comparison saved to: {COMPARE_IMAGE}")
        
    try:
        import cv2, numpy as np
        w, h = frames[0].size
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(MP4_OUTPUT, fourcc, 24.0, (w, h))
        for f in frames:
            frame_cv = cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR)
            out.write(frame_cv)
        out.release()
        print(f"[+] Scene 05 MP4 video created: {MP4_OUTPUT}")
    except Exception as e:
        print(f"[-] Video creation warning: {e}")

if __name__ == "__main__":
    if os.path.exists(TARGET_WEBP):
        process_output()
    else:
        print(f"Waiting for {TARGET_WEBP}...")
        while not os.path.exists(TARGET_WEBP):
            time.sleep(3)
        process_output()
