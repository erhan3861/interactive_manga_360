import json
import urllib.request
import urllib.parse
import uuid
import os
import sys
import time

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def get_history(prompt_id):
    try:
        req = urllib.request.Request(f"http://{SERVER_ADDRESS}/history/{prompt_id}")
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {}

def get_queue():
    try:
        req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt")
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {}

def wait_for_completion(prompt_id, check_interval=5):
    print(f"Waiting for execution of prompt {prompt_id}...")
    start_time = time.time()
    last_print = 0
    
    while True:
        hist = get_history(prompt_id)
        if prompt_id in hist:
            elapsed = time.time() - start_time
            print(f"\nPrompt {prompt_id} completed successfully in {elapsed:.1f}s ({elapsed/60:.2f} min)!")
            return hist[prompt_id]
        
        # Check if error occurred
        q = get_queue()
        queue_running = q.get("queue_running", [])
        queue_pending = q.get("queue_pending", [])
        
        is_running = any(item[1] == prompt_id for item in queue_running)
        is_pending = any(item[1] == prompt_id for item in queue_pending)
        
        now = time.time()
        if now - last_print >= check_interval:
            status_str = "RUNNING in GPU" if is_running else ("PENDING in Queue" if is_pending else "PROCESSING / DECODING")
            elapsed = now - start_time
            print(f"[{elapsed:.0f}s elapsed] Status: {status_str}...")
            last_print = now
            
        time.sleep(check_interval)

if __name__ == "__main__":
    workflow_path = r"C:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\workflow_pablo_orbit360.json"
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        wf = json.load(f)
    
    # Input Image
    wf["1"]["inputs"]["image"] = "pablo_scene_01_v2.png"
    
    # Pablo Dawson's Recommended Settings:
    # 768x768, 73 frames (3s at 24fps), 28 steps, CFG 1.0, LoRA strength 1.0
    wf["6"]["inputs"]["width"] = 768
    wf["6"]["inputs"]["height"] = 768
    wf["6"]["inputs"]["length"] = 73
    wf["8"]["inputs"]["steps"] = 28
    
    print("=======================================================")
    print("Triggering Pablo Dawson MiniMax-H3 360° Orbit Workflow")
    print("Image: pablo_scene_01_v2.png (scene_01_v2.png)")
    print("Base: minimax_h3_fl2va_pruned_int8_convrot.safetensors")
    print("LoRA: minimax_h3_flf2v_lora_v1.safetensors (Strength: 1.0)")
    print("Resolution: 768x768 | Length: 73 frames | Steps: 28")
    print("=======================================================")
    
    res = queue_prompt(wf)
    if "error" in res:
        print("ERROR queueing prompt:", json.dumps(res, indent=2))
        sys.exit(1)
        
    prompt_id = res.get("prompt_id")
    print(f"Queued successfully! Prompt ID: {prompt_id}")
    
    result = wait_for_completion(prompt_id)
    outputs = result.get("outputs", {})
    print("\nOutputs Generated:")
    print(json.dumps(outputs, indent=2))
