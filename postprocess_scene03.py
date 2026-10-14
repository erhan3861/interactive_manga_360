import os
import sys
import time
from PIL import Image, ImageSequence, ImageDraw

OUTPUT_DIR = r"C:\Users\hp\AppData\Local\Comfy-Desktop\ComfyUI-Shared\output"
TARGET_WEBP = os.path.join(OUTPUT_DIR, "MATLOWAI_ORB360_Scene03_00001_.webp")
FRAMES_DIR = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames_scene03"
COMPARE_IMAGE = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\compare_angles_scene03.png"
MP4_OUTPUT = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\orbit_scene03.mp4"

os.makedirs(FRAMES_DIR, exist_ok=True)

def process_output():
    print(f"[+] Output detected: {TARGET_WEBP}")
    im = Image.open(TARGET_WEBP)
    
    frames = []
    for i, frame in enumerate(ImageSequence.Iterator(im)):
        frame_rgb = frame.convert("RGB")
        frame_name = f"frame_{i:04d}.png"
        frame_rgb.save(os.path.join(FRAMES_DIR, frame_name))
        frames.append(frame_rgb)
        
    total_frames = len(frames)
    print(f"[+] Total Scene 03 frames extracted: {total_frames}")
    
    if total_frames > 0:
        indices = [0, total_frames // 4, total_frames // 2, (3 * total_frames) // 4]
        labels = [
            "Frame 0: 0 deg (Front - Boy & Bird at River)",
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
        print(f"[+] Scene 03 4-angle comparison saved to: {COMPARE_IMAGE}")
        
    try:
        import cv2, numpy as np
        w, h = frames[0].size
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(MP4_OUTPUT, fourcc, 24.0, (w, h))
        for f in frames:
            frame_cv = cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR)
            out.write(frame_cv)
        out.release()
        print(f"[+] Scene 03 MP4 video written to: {MP4_OUTPUT}")
    except Exception as e:
        print(f"[*] MP4 note: {e}")

if __name__ == "__main__":
    if "--watch" in sys.argv:
        print("[*] Watching for Scene 03 output: MATLOWAI_ORB360_Scene03_00001_.webp...")
        while True:
            if os.path.exists(TARGET_WEBP):
                size = os.path.getsize(TARGET_WEBP)
                if size > 500000: # at least 500KB
                    time.sleep(5) # wait for buffer to flush
                    try:
                        process_output()
                        break
                    except Exception as err:
                        print(f"[*] Still writing or error ({err}), waiting 5s...")
                        time.sleep(5)
                else:
                    print(f"[*] File detected but still writing ({size} bytes)...")
                    time.sleep(5)
            else:
                time.sleep(10)
    else:
        if os.path.exists(TARGET_WEBP) and os.path.getsize(TARGET_WEBP) > 500000:
            process_output()
        else:
            print("[*] Scene 03 output not ready yet.")
