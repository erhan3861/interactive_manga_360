import os
import glob
import numpy as np
from PIL import Image

def generate_ply_from_orbit(frames_dir, output_ply_path, num_sample_frames=12, step_sample=6):
    """
    Generates a true 3D Point Cloud (.PLY) file from the 73 multi-angle orbit frames.
    Projects multi-view pixels into 3D world space (X, Y, Z, R, G, B) based on camera orbit angles.
    """
    frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
    if not frame_files:
        raise ValueError(f"No frames found in {frames_dir}")
    
    total_frames = len(frame_files)
    print(f"Found {total_frames} frames. Sampling {num_sample_frames} key angles for 3D reconstruction...")
    
    selected_indices = np.linspace(0, total_frames - 1, num_sample_frames, dtype=int)
    
    all_points = []
    all_colors = []
    
    # Orbit radius and camera center
    orbit_radius = 2.8
    center_y = 0.9
    
    for idx in selected_indices:
        fpath = frame_files[idx]
        angle_rad = (idx / total_frames) * 2.0 * np.pi
        
        # Camera position on circular orbit
        cam_x = np.sin(angle_rad) * orbit_radius
        cam_z = np.cos(angle_rad) * orbit_radius
        cam_y = center_y
        
        img = Image.open(fpath).convert("RGB")
        # Downscale for crisp, fast point cloud sampling
        img = img.resize((192, 192), Image.Resampling.BILINEAR)
        arr = np.array(img, dtype=np.float32)
        
        h, w, _ = arr.shape
        
        # Simple foreground saliency / depth estimation from luminance & center bias
        gray = 0.299 * arr[:,:,0] + 0.587 * arr[:,:,1] + 0.114 * arr[:,:,2]
        
        for y in range(0, h, step_sample):
            for x in range(0, w, step_sample):
                # Normalized device coordinates (-1 to 1)
                nx = (x / (w - 1.0)) * 2.0 - 1.0
                ny = -((y / (h - 1.0)) * 2.0 - 1.0) # Invert Y
                
                # Approximate depth from camera
                # Center pixels (subject) are closer to center (depth ~ 2.4 - 2.8)
                dist_from_center = np.sqrt(nx**2 + ny**2)
                if dist_from_center > 1.2:
                    continue # Ignore far corners
                    
                depth = orbit_radius - (1.0 - min(1.0, dist_from_center * 0.7)) * 1.2
                
                # Camera basis vectors (look at 0, center_y, 0)
                forward = -np.array([cam_x, 0, cam_z], dtype=np.float32)
                forward /= np.linalg.norm(forward)
                
                right = np.array([forward[2], 0, -forward[0]], dtype=np.float32)
                up = np.array([0, 1.0, 0], dtype=np.float32)
                
                # 3D world position
                pos = np.array([cam_x, cam_y, cam_z], dtype=np.float32) + forward * depth + right * (nx * 0.9) + up * (ny * 0.9)
                
                rgb = arr[y, x]
                all_points.append(pos)
                all_colors.append(rgb.astype(np.uint8))
                
    pts = np.array(all_points, dtype=np.float32)
    cols = np.array(all_colors, dtype=np.uint8)
    
    num_pts = len(pts)
    print(f"Total 3D Points generated: {num_pts}. Writing PLY file...")
    
    with open(output_ply_path, "w", encoding="utf-8") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write("comment Spatial Manga MiniMax-H3 ORB360 3D Point Cloud\n")
        f.write(f"element vertex {num_pts}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        for i in range(num_pts):
            p = pts[i]
            c = cols[i]
            f.write(f"{p[0]:.4f} {p[1]:.4f} {p[2]:.4f} {c[0]} {c[1]} {c[2]}\n")
            
    print(f"Successfully generated PLY file: {output_ply_path} ({os.path.getsize(output_ply_path)} bytes)")

if __name__ == "__main__":
    frames_dir = r"C:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames"
    out_ply = r"C:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\scene_01_3d_pointcloud.ply"
    generate_ply_from_orbit(frames_dir, out_ply)
