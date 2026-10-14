import json
import urllib.request
import uuid

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())

with open(r"c:\Users\hp\OneDrive\Documents\metafor\interactive_manga_360\workflow_scene_05_orb360.json", "r", encoding="utf-8") as f:
    wf = json.load(f)

p = {"prompt": wf, "client_id": CLIENT_ID}
data = json.dumps(p).encode('utf-8')
req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("QUEUED_SUCCESS:", res.get("prompt_id"))
except Exception as e:
    print("QUEUE_ERROR:", e)
