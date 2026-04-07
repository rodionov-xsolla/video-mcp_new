import base64, json, time, requests

FAL_KEY = "dff9117d-ae65-4d35-8f1a-f0ff3ce93f00:ce1711fa645b80544670263a40cf5313"
OUT = "/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1"
HEADERS = {"Authorization": f"Key {FAL_KEY}"}
ENDPOINT = "fal-ai/kling-video/v2.6/pro/image-to-video"

# Pre-fetched fal.media URLs (from NB2 generation request IDs)
SCENE_URLS = {
    "scene-1-start": "https://v3b.fal.media/files/b/0a952ca1/IL8IRfKz9BXF264syK9g1_IqIuFomt.png",
    "scene-1-end":   "https://v3b.fal.media/files/b/0a952ca5/gX915d3zJb72cgGXAQN-G_aisqAn8P.png",
    "scene-4-start": "https://v3b.fal.media/files/b/0a952ce4/yzsarvat2ZT7y6GTEQjqm_gURfAt6v.png",
    "scene-4-end":   "https://v3b.fal.media/files/b/0a952ce9/W3Gm9qwEmeRZudToDxlTR_BzWSXRE2.png",
    "scene-7-start": "https://v3b.fal.media/files/b/0a952cfc/vv9XJkrBc-NbLraZ2bX-5_AHmV0gop.png",
    "scene-7-end":   "https://v3b.fal.media/files/b/0a952d00/A4cVG8PvSv4sWdx8rVw3q_1316Ub6t.png",
    "scene-9-start": "https://v3b.fal.media/files/b/0a952d08/Rtq3ScwUnIZ7ZoaO2-2L9_vOHHNQjR.png",
    "scene-9-end":   "https://v3b.fal.media/files/b/0a952d0d/r7A30QEpb9sXYultfY3BU_PVPmc77e.png",
}

def fal_submit(payload_dict):
    r = requests.post(
        f"https://queue.fal.run/{ENDPOINT}",
        json=payload_dict,
        headers={**HEADERS, "Content-Type": "application/json"}
    )
    return r.json().get("request_id")

def fal_wait(request_id, label):
    # Status/result always use base model path: fal-ai/kling-video
    STATUS_BASE = "fal-ai/kling-video"
    for i in range(80):
        time.sleep(10)
        r = requests.get(
            f"https://queue.fal.run/{STATUS_BASE}/requests/{request_id}/status",
            headers=HEADERS
        )
        if not r.text.strip():
            print(f"  [{i+1}] {label}: empty, retry...", flush=True)
            continue
        state = r.json().get("status", "unknown")
        print(f"  [{i+1}] {label}: {state}", flush=True)
        if state == "COMPLETED":
            r2 = requests.get(
                f"https://queue.fal.run/{STATUS_BASE}/requests/{request_id}",
                headers=HEADERS
            )
            return r2.json()["video"]["url"]
        if state == "FAILED":
            print(f"  FAILED: {r.json()}", flush=True)
            return None
    return None

def download(url, path):
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)
    size = len(r.content)
    print(f"  saved: {path} ({size:,} bytes)", flush=True)
    return size

def gen_i2v(scene_key, motion_prompt, out_path, label):
    print(f"\n=== {label} ===", flush=True)
    start_url = SCENE_URLS[f"{scene_key}-start"]
    end_url = SCENE_URLS[f"{scene_key}-end"]
    print(f"  start: {start_url[:60]}...", flush=True)
    print(f"  end:   {end_url[:60]}...", flush=True)

    rid = fal_submit({
        "prompt": motion_prompt,
        "start_image_url": start_url,
        "end_image_url": end_url,
        "duration": "5",
        "generate_audio": False,
        "negative_prompt": "blur, distort, low quality, static, freeze, morphing faces"
    })
    print(f"  Submitted: {rid}", flush=True)
    url = fal_wait(rid, label)
    if url:
        size = download(url, out_path)
        return size > 10000
    return False

# scene-1 already saved (13MB)
print("scene-1: already saved", flush=True)

# ── Scene 4: Chekov airlock ────────────────────────────────────────────────
gen_i2v(
    "scene-4",
    "Camera holds steady at the porthole glass in close-up. Chekov's breath fogs the surface in slow waves. His hands press harder — then begin to slide. Frost crystallizes at the glass edges. The SEALED indicator behind him blinks on — once, twice — then stays red. The outer pressure door begins to descend from the top of frame, millimeter by millimeter, cutting off the light. His eyes never leave the camera.",
    f"{OUT}/scenes/scene-4/scene-4.mp4",
    "scene-4 chekov airlock"
)

# ── Scene 7: Corridor, porthole goes dark ─────────────────────────────────
gen_i2v(
    "scene-7",
    "Camera holds over Kirk's shoulder. The porthole light dims. Chekov's silhouette fades. The outer pressure door descends the final inch and seals with a heavy resonant clunk. The SEALED indicator locks on. Silence. Kirk and Worf stand motionless. Their ghostly reflections appear in the dark sealed door. Kirk's fist slowly clenches at his side. Nobody moves. Camera holds the stillness.",
    f"{OUT}/scenes/scene-7/scene-7.mp4",
    "scene-7 corridor sealed"
)

# ── Scene 9: Worf eyes drop (cliffhanger) ────────────────────────────────
gen_i2v(
    "scene-9",
    "Camera pushes in slowly on Worf's face. His eyes hold Kirk's gaze for one beat. Two beats. The red SEALED light pulses behind him. Three beats. Then — almost imperceptibly — his eyes drop. Not a blink. A surrender. His jaw tightens. He says nothing. Camera holds on the downward gaze. The sealed door pulses red once more. Cut to black.",
    f"{OUT}/scenes/scene-9/scene-9.mp4",
    "scene-9 worf eyes drop"
)

print("\n=== ALL 4 KLING I2V CLIPS DONE ===", flush=True)
