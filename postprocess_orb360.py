import os
import sys
import time
import json
import urllib.request
import subprocess

OUTPUT_DIR = r"C:\Users\hp\AppData\Local\Comfy-Desktop\ComfyUI-Shared\output"
TARGET_WEBP = os.path.join(OUTPUT_DIR, "MATLOWAI_ORB360_Ref2VA_00001_.webp")
FRAMES_DIR = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames_orb360"
MP4_OUTPUT = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\orbit_orb360.mp4"
COMPARE_IMAGE = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\compare_angles_orb360.png"

PROMPT_ID = "51e9b116-e59a-4289-832b-5c9497cc3308"

def check_history():
    try:
        url = f"http://127.0.0.1:8188/history/{PROMPT_ID}"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if PROMPT_ID in data:
                return True
    except Exception:
        pass
    return False

def process_output():
    print(f"[+] Output detected: {TARGET_WEBP}")
    os.makedirs(FRAMES_DIR, exist_ok=True)
    
    # 1. Convert WebP to MP4
    print("[+] Converting WebP to MP4...")
    subprocess.run([
        "ffmpeg", "-y", "-i", TARGET_WEBP,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        MP4_OUTPUT
    ], check=True)
    
    # 2. Extract frames
    print("[+] Extracting frames to frames_orb360/...")
    subprocess.run([
        "ffmpeg", "-y", "-i", TARGET_WEBP,
        os.path.join(FRAMES_DIR, "frame_%04d.png")
    ], check=True)
    
    frames = sorted([f for f in os.listdir(FRAMES_DIR) if f.startswith("frame_") and f.endswith(".png")])
    total_frames = len(frames)
    print(f"[+] Total frames extracted: {total_frames}")
    
    if total_frames > 0:
        # Create 4-angle contact sheet (0%, 25%, 50%, 75%)
        indices = [0, total_frames // 4, total_frames // 2, (3 * total_frames) // 4]
        from PIL import Image, ImageDraw, ImageFont
        
        sample_imgs = []
        labels = ["0 deg (Front)", "90 deg (Side)", "180 deg (Back)", "270 deg (Opposite Side)"]
        for idx, lbl in zip(indices, labels):
            idx = min(idx, total_frames - 1)
            img_path = os.path.join(FRAMES_DIR, frames[idx])
            im = Image.open(img_path).convert("RGB")
            draw = ImageDraw.Draw(im)
            draw.text((20, 20), f"Frame {idx}: {lbl}", fill=(255, 230, 0))
            sample_imgs.append(im)
            
        w, h = sample_imgs[0].size
        contact_sheet = Image.new("RGB", (w * 2, h * 2))
        contact_sheet.paste(sample_imgs[0], (0, 0))
        contact_sheet.paste(sample_imgs[1], (w, 0))
        contact_sheet.paste(sample_imgs[2], (0, h))
        contact_sheet.paste(sample_imgs[3], (w, h))
        contact_sheet.save(COMPARE_IMAGE)
        print(f"[+] Multi-angle comparison saved to: {COMPARE_IMAGE}")

        # 4. Copy to frames/ for instant Three.js index.html integration
        MAIN_FRAMES_DIR = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames"
        import shutil
        for i, f in enumerate(frames):
            src = os.path.join(FRAMES_DIR, f)
            dst = os.path.join(MAIN_FRAMES_DIR, f"frame_{i:03d}.png")
            shutil.copy2(src, dst)
        print(f"[+] All {len(frames)} frames synced to {MAIN_FRAMES_DIR} for Three.js WebGL viewer!")

if __name__ == "__main__":
    if "--watch" in sys.argv:
        print("[*] Watching for output file MATLOWAI_ORB360_Ref2VA_00001_.webp...")
        while True:
            if os.path.exists(TARGET_WEBP):
                time.sleep(3)  # wait for file write to fully settle
                process_output()
                break
            time.sleep(15)
    else:
        if os.path.exists(TARGET_WEBP):
            process_output()
        else:
            print("[*] Output not ready yet.")
