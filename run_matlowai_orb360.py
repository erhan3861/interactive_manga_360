import json
import urllib.request
import urllib.parse
import uuid
import os
import sys
import time

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())

def build_workflow(image_name="pablo_scene_01_v2.png", width=768, height=768, length=73, steps=16, seed=42):
    prompt_text = (
        "ORB360_CW smooth clockwise 360-degree camera orbit around the subject in <Picture 1>, "
        "full circular camera rotation around the boy and bird, freeze time bullet-time, "
        "dramatic cinematic lighting, masterwork quality, clean background parallax"
    )

    workflow = {
        # 1. Load Reference Image
        "1": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_name
            }
        },
        # 2. Ref2VA Base Model
        "2": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
                "weight_dtype": "default"
            }
        },
        # 3. MATLOWAI ORB360 LoRA (568MB)
        "3": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["2", 0],
                "lora_name": "minimax_h3_orb360_step1500.safetensors",
                "strength_model": 1.0
            }
        },
        # 4. Text/Vision Encoder (Qwen3-VL 32B)
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
        # 8. Negative Conditioning (Zero Out for guidance-distilled model)
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
                "seed": seed,
                "steps": steps,
                "cfg": 1.0,
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
        # 11. Save Animated WEBP
        "11": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["10", 0],
                "filename_prefix": "MATLOWAI_ORB360_Ref2VA",
                "fps": 24.0,
                "lossless": False,
                "quality": 90,
                "method": "default"
            }
        }
    }
    return workflow

def queue_prompt(workflow):
    p = {"prompt": workflow, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def get_history(prompt_id):
    try:
        req = urllib.request.Request(f"http://{SERVER_ADDRESS}/history/{prompt_id}")
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except:
        return {}

def wait_for_completion(prompt_id, check_interval=5):
    print(f"Waiting for prompt {prompt_id} to finish...")
    start_time = time.time()
    last_print = 0
    while True:
        hist = get_history(prompt_id)
        if prompt_id in hist:
            elapsed = time.time() - start_time
            print(f"\nExecution finished in {elapsed:.1f}s ({elapsed/60:.2f} min)!")
            return hist[prompt_id]
        now = time.time()
        if now - last_print >= check_interval:
            print(f"[{now - start_time:.0f}s elapsed] Processing Ref2VA + ORB360 on GPU...", flush=True)
            last_print = now
        time.sleep(check_interval)

if __name__ == "__main__":
    wf = build_workflow(image_name="pablo_scene_01_v2.png", width=768, height=768, length=73, steps=16)
    
    # Save workflow file
    out_json = r"C:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\workflow_matlowai_orb360.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print(f"Workflow saved: {out_json}")
    
    print("\nQueuing Ref2VA + ORB360_CW workflow to ComfyUI...")
    res = queue_prompt(wf)
    prompt_id = res.get("prompt_id")
    print(f"Successfully queued! Prompt ID: {prompt_id}")
    
    result = wait_for_completion(prompt_id)
    outputs = result.get("outputs", {})
    print("Outputs generated:")
    print(json.dumps(outputs, indent=2))
