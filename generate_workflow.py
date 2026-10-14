import json
import urllib.request
import urllib.parse
import os
import sys

def build_minimax_orb360_workflow(
    ref_image_name="selman_scene_01.png",
    prompt_text="ORB360_CW 360-degree camera orbit around the character in <Picture 1>, freeze time bullet-time, high contrast crisp manga ink lines, masterwork detailed manga panel",
    steps=8,
    cfg=1.0,
    width=832,
    height=480,
    length=124
):
    """
    Builds a complete ComfyUI API workflow dictionary for MiniMax-H3 + ORB360 LoRA.
    """
    workflow = {
        # 1. Load Image (Manga Reference)
        "1": {
            "class_type": "LoadImage",
            "inputs": {
                "image": ref_image_name
            }
        },
        # 2. Diffusion Model Checkpoint
        "2": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
                "weight_dtype": "default"
            }
        },
        # 3. Apply ORB360 LoRA
        "3": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["2", 0],
                "lora_name": "minimax_h3_orb360_step1500.safetensors",
                "strength_model": 1.0
            }
        },
        # 4. CLIP / Vision Text Encoder
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
        # 6. Audio VAE
        "6": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "minimax_h3_audio_vae_fp32.safetensors"
            }
        },
        # 7. MiniMax H3 Reference to Video Conditioning
        "7": {
            "class_type": "MiniMaxH3ReferenceToVideo",
            "inputs": {
                "clip": ["4", 0],
                "vae": ["5", 0],
                "audio_vae": ["6", 0],
                "prompt": prompt_text,
                "width": width,
                "height": height,
                "length": length,
                "ref_image_size": "match",
                "ref_image_1": ["1", 0]
            }
        },
        # 8. Empty Negative Conditioning
        "8": {
            "class_type": "ConditioningZeroOut",
            "inputs": {
                "conditioning": ["7", 0]
            }
        },
        # 9. KSampler
        "9": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["3", 0],
                "positive": ["7", 0],
                "negative": ["8", 0],
                "latent_image": ["7", 1],
                "seed": 42,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        # 10. VAE Decode
        "10": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["9", 0],
                "vae": ["5", 0]
            }
        },
        # 11. Save Animated Output (or VHS Video)
        "11": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["10", 0],
                "filename_prefix": "MiniMax_ORB360_Manga",
                "fps": 24,
                "lossless": False,
                "quality": 85,
                "method": "fast"
            }
        }
    }
    return workflow

if __name__ == "__main__":
    wf = build_minimax_orb360_workflow()
    out_file = r"C:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\workflow_minimax_orb360.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print(f"Workflow saved to: {out_file}")
