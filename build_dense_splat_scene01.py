import os
import glob
import numpy as np
from PIL import Image

def generate_dense_splat_ply(frames_dir, output_ply_path, num_sample_frames=36, resolution=256, step_sample=3):
    """
    Builds a high-density, multi-angle 3D Gaussian Splat-style Point Cloud (.ply)
    from 360-degree orbital frames, including surface normals for full 6-DOF viewing
    (top-down, low-angle, diagonals, free orbit) without modifying the original PLY.
    """
    frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
    if not frame_files:
        raise ValueError(f"No frames found in {frames_dir}")
        
    total_frames = len(frame_files)
    print(f"[+] Found {total_frames} frames. Sampling {num_sample_frames} high-density angles...")
    
    selected_indices = np.linspace(0, total_frames - 1, num_sample_frames, dtype=int)
    
    all_points = []
    all_normals = []
    all_colors = []
    
    orbit_radius = 2.6
    center_y = 0.95
    
    for idx in selected_indices:
        fpath = frame_files[idx]
        angle_rad = (idx / total_frames) * 2.0 * np.pi
        
        # Camera position on orbit
        cam_x = np.sin(angle_rad) * orbit_radius
        cam_z = np.cos(angle_rad) * orbit_radius
        cam_y = center_y
        
        img = Image.open(fpath).convert("RGB")
        img = img.resize((resolution, resolution), Image.Resampling.BILINEAR)
        arr = np.array(img, dtype=np.float32)
        
        h, w, _ = arr.shape
        
        # Camera basis vectors
        forward = -np.array([cam_x, 0, cam_z], dtype=np.float32)
        forward /= np.linalg.norm(forward)
        right = np.array([forward[2], 0, -forward[0]], dtype=np.float32)
        up = np.array([0, 1.0, 0], dtype=np.float32)
        
        for y in range(0, h, step_sample):
            for x in range(0, w, step_sample):
                nx = (x / (w - 1.0)) * 2.0 - 1.0
                ny = -((y / (h - 1.0)) * 2.0 - 1.0)
                
                dist_from_center = np.sqrt(nx**2 + ny**2)
                if dist_from_center > 1.15:
                    continue
                    
                # Volumetric depth profile: central subject (boy & bird) is closer to origin
                depth = orbit_radius - (1.0 - min(1.0, dist_from_center * 0.75)) * 1.35
                
                # 3D world position
                pos = np.array([cam_x, cam_y, cam_z], dtype=np.float32) + forward * depth + right * (nx * 0.95) + up * (ny * 0.95)
                
                # Normal vector facing towards camera viewpoint
                norm = np.array([cam_x - pos[0], cam_y - pos[1], cam_z - pos[2]], dtype=np.float32)
                norm_len = np.linalg.norm(norm)
                if norm_len > 1e-4:
                    norm /= norm_len
                else:
                    norm = np.array([0, 1.0, 0], dtype=np.float32)
                    
                rgb = arr[y, x]
                all_points.append(pos)
                all_normals.append(norm)
                all_colors.append(rgb.astype(np.uint8))
                
    pts = np.array(all_points, dtype=np.float32)
    norms = np.array(all_normals, dtype=np.float32)
    cols = np.array(all_colors, dtype=np.uint8)
    
    num_pts = len(pts)
    print(f"[+] Total Dense 3D Splat Points: {num_pts}. Writing to {output_ply_path}...")
    
    with open(output_ply_path, "w", encoding="utf-8") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write("comment Dense Multi-Angle 3D Gaussian Splat Model for Scene 01\n")
        f.write(f"element vertex {num_pts}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property float nx\n")
        f.write("property float ny\n")
        f.write("property float nz\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        for i in range(num_pts):
            p = pts[i]
            n = norms[i]
            c = cols[i]
            f.write(f"{p[0]:.4f} {p[1]:.4f} {p[2]:.4f} {n[0]:.4f} {n[1]:.4f} {n[2]:.4f} {c[0]} {c[1]} {c[2]}\n")
            
    size_mb = os.path.getsize(output_ply_path) / (1024 * 1024)
    print(f"[+] Successfully generated Dense Splat PLY: {output_ply_path} ({size_mb:.2f} MB, {num_pts} points)")

if __name__ == "__main__":
    frames_dir = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\frames"
    output_ply = r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\scene_01_dense_splat.ply"
    generate_dense_splat_ply(frames_dir, output_ply, num_sample_frames=36, resolution=256, step_sample=3)
