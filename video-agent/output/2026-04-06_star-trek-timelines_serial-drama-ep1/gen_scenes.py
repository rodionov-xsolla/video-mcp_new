import os, base64, json, time
import requests

FAL_KEY = "dff9117d-ae65-4d35-8f1a-f0ff3ce93f00:ce1711fa645b80544670263a40cf5313"
OUT = "/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1"
REFS = f"{OUT}/scenes/refs"
HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

def fal_submit(endpoint, payload_dict):
    r = requests.post(f"https://queue.fal.run/{endpoint}", json=payload_dict, headers=HEADERS)
    d = r.json()
    return d.get("request_id")

def fal_wait(endpoint, request_id, label):
    # Status/result always use base model path (not /edit sub-path)
    base = "/".join(endpoint.split("/")[:2])  # e.g. fal-ai/nano-banana-2
    for i in range(60):
        time.sleep(5)
        r = requests.get(f"https://queue.fal.run/{base}/requests/{request_id}/status", headers=HEADERS)
        if not r.text.strip():
            print(f"  [{i+1}] {label}: empty response, retrying...", flush=True)
            continue
        try:
            state = r.json().get("status", "unknown")
        except Exception:
            print(f"  [{i+1}] {label}: bad response: {r.text[:100]}", flush=True)
            continue
        print(f"  [{i+1}] {label}: {state}", flush=True)
        if state == "COMPLETED":
            r2 = requests.get(f"https://queue.fal.run/{base}/requests/{request_id}", headers=HEADERS)
            return r2.json()["images"][0]["url"]
    return None

def ref_b64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

def download(url, path):
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"  saved: {path}", flush=True)

def gen_edit(prompt, refs, width, height, out_path, label):
    image_urls = [ref_b64(r) for r in refs]
    rid = fal_submit("fal-ai/nano-banana-2/edit", {
        "prompt": prompt,
        "image_urls": image_urls,
        "image_size": {"width": width, "height": height},
        "num_inference_steps": 30,
        "guidance_scale": 7.5
    })
    print(f"Submitted {label}: {rid}", flush=True)
    url = fal_wait("fal-ai/nano-banana-2/edit", rid, label)
    if url:
        download(url, out_path)
    return url

def gen_txt2img(prompt, width, height, out_path, label):
    rid = fal_submit("fal-ai/nano-banana-2", {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_inference_steps": 30,
        "guidance_scale": 7.5
    })
    print(f"Submitted {label}: {rid}", flush=True)
    url = fal_wait("fal-ai/nano-banana-2", rid, label)
    if url:
        download(url, out_path)
    return url

# ── Scene 2 already saved ─────────────────────────────────────────────────
print("scene-2: already saved", flush=True)

# ── Scene 3: Worf 1:1 (dialogue) ─────────────────────────────────────────
gen_edit(
    "Star Trek cinematic 3D animation, semi-realistic Pixar 3D Commander Worf, imposing Klingon-Human, prominent forehead ridges, dark skin, fierce certain expression, TNG command red uniform, broad shoulders, low angle looking up at his imposing figure, holding Starfleet PADD, red alert atmosphere, LCARS tactical panels behind him, slight opening of mouth showing teeth for lipsync, 1:1 square composition",
    [f"{REFS}/worf-ref.png"], 1080, 1080,
    f"{OUT}/scenes/scene-3/scene-3.png", "scene-3-worf"
)

# ── Scene 4 START: Chekov behind porthole (action) ────────────────────────
gen_edit(
    "Star Trek cinematic 3D animation, semi-realistic Pixar 3D Ensign Pavel Chekov, young face, bowl-cut dark hair, TOS gold Starfleet uniform, pressed against thick airlock porthole glass from inside, both hands flat on the glass, face close to the surface, his breath beginning to fog the cold metal, viewed from outside, desperate wide eyes locked on camera, red warning indicator above the door unlit yet, 9:16 vertical composition",
    [f"{REFS}/chekov-ref.png"], 608, 1080,
    f"{OUT}/scenes/scene-4/scene-4-start.png", "scene-4-start"
)

# ── Scene 4 END: Chekov frost, sliding hands ──────────────────────────────
gen_edit(
    "Star Trek cinematic 3D animation, semi-realistic Pixar 3D Ensign Chekov, same porthole perspective, frost now crystallizing on the inner glass edges, Chekov hands sliding slowly down the surface, tears on his face, the red SEALED indicator on the wall behind him inside the airlock now blinking on, his image beginning to dim as the outer pressure door starts to descend from above, 9:16 vertical composition",
    [f"{REFS}/chekov-ref.png"], 608, 1080,
    f"{OUT}/scenes/scene-4/scene-4-end.png", "scene-4-end"
)

# ── Scene 5: Kirk extreme close-up 1:1 ───────────────────────────────────
gen_edit(
    "Star Trek cinematic 3D animation, semi-realistic Pixar 3D Captain Kirk, extreme close-up face only, jaw locked with absolute command, eyes burning cold and certain, barely parted lips showing teeth, red alert light from the side casting deep shadow across half his face, the weight of a captain who will not negotiate, 1:1 square composition",
    [f"{REFS}/kirk-ref.png"], 1080, 1080,
    f"{OUT}/scenes/scene-5/scene-5.png", "scene-5-kirk"
)

# ── Scene 6: Worf three-quarter 1:1 ──────────────────────────────────────
gen_edit(
    "Star Trek cinematic 3D animation, semi-realistic Pixar 3D Commander Worf, medium shot, body turned three-quarters — the posture of a soldier caught between two loyalties, eyes not fully meeting camera, PADD lowered at his side, jaw set with the weight of the order, slight opening of mouth showing teeth for lipsync, dim red atmosphere, 1:1 square composition",
    [f"{REFS}/worf-ref.png"], 1080, 1080,
    f"{OUT}/scenes/scene-6/scene-6.png", "scene-6-worf"
)

print("=== Batch 1 complete (scenes 3-6) ===", flush=True)

# ── Scene 7 START: Corridor over-shoulder, porthole lit ───────────────────
gen_txt2img(
    "Star Trek cinematic 3D animation, semi-realistic Pixar-quality characters, Enterprise airlock corridor wide shot, viewed from behind Kirk shoulder, Kirk and Worf standing side by side facing the airlock door, the porthole still lit from inside Chekov silhouette faintly visible through the glass, the corridor narrow and cold, red emergency lighting, deep shadow between the two men, 9:16 vertical composition",
    608, 1080,
    f"{OUT}/scenes/scene-7/scene-7-start.png", "scene-7-start"
)

# ── Scene 7 END: Corridor, porthole dark, Chekov gone ─────────────────────
gen_txt2img(
    "Star Trek cinematic 3D animation, semi-realistic Pixar-quality characters, Enterprise airlock corridor, same perspective — but the porthole is now dark and empty, the outer door fully sealed, SEALED indicator burning red above it, two figures Kirk and Worf standing rigid, their two reflections ghostly in the black sealed door, absolute silence rendered in steel and shadow, 9:16 vertical composition",
    608, 1080,
    f"{OUT}/scenes/scene-7/scene-7-end.png", "scene-7-end"
)

# ── Scene 8: Kirk profile 1:1 ─────────────────────────────────────────────
gen_edit(
    "Star Trek cinematic 3D animation, semi-realistic Pixar 3D Captain Kirk, profile close-up side view, jaw set like iron, eyes looking slightly off camera toward Worf, the sealed airlock door reflected as a tiny red light in his eye, gold uniform collar edge visible, deep shadow, the face of a man who already knows the truth and is giving Worf one chance, slight parting of lips showing teeth, 1:1 square composition",
    [f"{REFS}/kirk-ref.png"], 1080, 1080,
    f"{OUT}/scenes/scene-8/scene-8.png", "scene-8-kirk"
)

# ── Scene 9 START: Worf meeting Kirk gaze ────────────────────────────────
gen_edit(
    "Star Trek cinematic 3D animation, semi-realistic Pixar 3D Commander Worf, medium close-up facing camera directly, meeting Kirk gaze, eyes carrying the full weight of a secret he cannot speak, jaw locked, the red sealed door glowing behind him, one beat before the answer — the last moment of his silence being a choice, 9:16 vertical composition",
    [f"{REFS}/worf-ref.png"], 608, 1080,
    f"{OUT}/scenes/scene-9/scene-9-start.png", "scene-9-start"
)

# ── Scene 9 END: Worf eyes drop ───────────────────────────────────────────
gen_edit(
    "Star Trek cinematic 3D animation, semi-realistic Pixar 3D Commander Worf, same close-up — but his eyes have dropped to the floor, chin barely lowered, the weight of it pulling his gaze down, jaw tightening with what he cannot say, the sealed door still burning red behind him, the silence stretching into something terrible, 9:16 vertical composition",
    [f"{REFS}/worf-ref.png"], 608, 1080,
    f"{OUT}/scenes/scene-9/scene-9-end.png", "scene-9-end"
)

print("=== ALL SCENES COMPLETE ===", flush=True)
