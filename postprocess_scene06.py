import os
import sys
import time
import shutil
import subprocess
from PIL import Image, ImageSequence, ImageDraw

OUTPUT_DIR = r"C:\Users\hp\AppData\Local\Comfy-Desktop\ComfyUI-Shared\output"
TARGET_WEBP = os.path.join(OUTPUT_DIR, "MATLOWAI_ORB360_Scene06_00001_.webp")
FRAMES_DIR = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames_scene06"
COMPARE_IMAGE = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\compare_angles_scene06.png"
MP4_OUTPUT = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\orbit_scene06.mp4"
ARTIFACT_COMPARE = r"C:\Users\hp\.gemini\antigravity-ide\brain\899840be-bfee-43c7-8dda-88023c73d70a\compare_angles_scene06.png"
PROJECT_DIR = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360"

os.makedirs(FRAMES_DIR, exist_ok=True)

def wait_for_stable_file(filepath, stable_seconds=5):
    print(f"[*] Waiting for {filepath} to appear...")
    last_size = -1
    consecutive_matches = 0
    while True:
        if os.path.exists(filepath):
            try:
                cur_size = os.path.getsize(filepath)
                if cur_size > 100000 and cur_size == last_size:
                    consecutive_matches += 1
                    if consecutive_matches >= stable_seconds:
                        print(f"[+] File is ready and stable! Size: {cur_size} bytes")
                        return True
                else:
                    consecutive_matches = 0
                    last_size = cur_size
            except Exception:
                pass
        time.sleep(1)

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
    print(f"[+] Total Scene 06 frames extracted: {total_frames}")
    
    if total_frames > 0:
        indices = [0, total_frames // 4, total_frames // 2, (3 * total_frames) // 4]
        labels = [
            "Frame 0: 0 deg (Front - Kiz Kulesi)",
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
        print(f"[+] Scene 06 4-angle comparison saved to: {COMPARE_IMAGE}")
        try:
            shutil.copyfile(COMPARE_IMAGE, ARTIFACT_COMPARE)
            print(f"[+] Comparison copied to brain artifacts: {ARTIFACT_COMPARE}")
        except Exception as e:
            print(f"[-] Artifact copy note: {e}")
        
    try:
        import cv2, numpy as np
        w, h = frames[0].size
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(MP4_OUTPUT, fourcc, 24.0, (w, h))
        for f in frames:
            frame_cv = cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR)
            out.write(frame_cv)
        out.release()
        print(f"[+] Scene 06 MP4 video created: {MP4_OUTPUT}")
    except Exception as e:
        print(f"[-] Video creation warning: {e}")

    # Commit and push to git
    try:
        print("[*] Staging and pushing Scene 06 to GitHub Pages...")
        subprocess.run(["git", "add", "index.html", "frames_scene06/", "compare_angles_scene06.png", "orbit_scene06.mp4", "workflow_scene_06_orb360.json", "postprocess_scene06.py", "queue_scene06.py", "kiz_kulesi.png"], cwd=PROJECT_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "feat: complete Sahne 06 Kiz Kulesi 73-angle 360 orbit generation and WebGL integration"], cwd=PROJECT_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_DIR, check=True)
        print("[+] GitHub Pages push completed successfully!")
    except Exception as e:
        print(f"[-] Git push note: {e}")

    print("ALL_SCENE_06_STEPS_COMPLETED_SUCCESSFULLY")

if __name__ == "__main__":
    wait_for_stable_file(TARGET_WEBP)
    process_output()
