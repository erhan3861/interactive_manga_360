import json
import os

def build_pablo_orbit_workflow(
    image_name="selman_scene_01.png",
    width=768,
    height=768,
    length=73,
    steps=28,
    seed=42
):
    """
    Pablo Dawson MiniMax-H3 360° Orbit LoRA (FL2VA first-and-last-frame) ComfyUI Workflow.
    Verbatim prompt and official parameters.
    """
    prompt_text = (
        "One frozen instant. Only the camera moves. In a continuous 360 orbit. "
        "Preserve every person and object in exactly the same world position, orientation, shape and pose throughout the shot. "
        "Airborne objects remain suspended at the captured height and angle: no wobbling, shaking, spinning, drifting, falling or continued action. "
        "Keep faces, hands, clothing, liquids and the background motionless while retaining their natural appearance. "
        "Camera parallax is the only source of apparent movement. No cuts, zoom, morphing or added objects."
    )

    workflow = {
        # 1. Load Single Input Image
        "1": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_name
            }
        },
        # 2. Diffusion Model: FL2VA Pruned INT8 ConvRot
        "2": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
                "weight_dtype": "default"
            }
        },
        # 3. LoRA: Pablo Dawson's 360 Orbit LoRA (Strength 1.0)
        "3": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["2", 0],
                "lora_name": "minimax_h3_flf2v_lora_v1.safetensors",
                "strength_model": 1.0
            }
        },
        # 4. CLIP / Vision Text Encoder (Qwen3-VL 32B)
        "4": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
                "type": "minimax"
            }
        },
        # 5. Video VAE
        "5": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "minimax_h3_video_vae_fp16.safetensors"
            }
        },
        # 6. MiniMax H3 Image to Video (First-and-Last Frame Anchor)
        # Girdi görseli hem first_frame hem de last_frame'e bağlanır!
        "6": {
            "class_type": "MiniMaxH3ImageToVideo",
            "inputs": {
                "clip": ["4", 0],
                "vae": ["5", 0],
                "prompt": prompt_text,
                "width": width,
                "height": height,
                "length": length, # 73 frames (3 seconds at 24fps)
                "first_frame": ["1", 0], # Frame 0
                "last_frame": ["1", 0]   # Frame 72 (Exact loop back!)
            }
        },
        # 7. Conditioning Zero Out (Negative not needed for guidance-distilled model)
        "7": {
            "class_type": "ConditioningZeroOut",
            "inputs": {
                "conditioning": ["6", 0]
            }
        },
        # 8. KSampler (Euler / Simple, 28 steps, CFG 1.0)
        "8": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["3", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["6", 1],
                "seed": seed,
                "steps": steps,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        # 9. VAE Decode
        "9": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["8", 0],
                "vae": ["5", 0]
            }
        },
        # 10. Save Animated WEBP / Video Output
        "10": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["9", 0],
                "filename_prefix": "PabloDawson_360_Orbit",
                "fps": 24,
                "lossless": False,
                "quality": 90,
                "method": "default"
            }
        }
    }
    return workflow

if __name__ == "__main__":
    wf = build_pablo_orbit_workflow()
    out_file = r"C:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\workflow_pablo_orbit360.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print(f"Pablo Dawson 360 Orbit Workflow saved to: {out_file}")
