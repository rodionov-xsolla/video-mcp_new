import json, time, requests

FAL_KEY = "dff9117d-ae65-4d35-8f1a-f0ff3ce93f00:ce1711fa645b80544670263a40cf5313"
OUT = "/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1"
HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

# Image URLs for dialogue scenes
SCENE_IMG_URLS = {
    "scene-2": "https://v3b.fal.media/files/b/0a952cb3/Drasx_59Fv-NumhZHLbP5_8Dnnv9Wa.png",
    "scene-3": "https://v3b.fal.media/files/b/0a952cdf/B_UdH7fu_x5Ah3ROsQ79v_8hEsuwyl.png",
    "scene-5": "https://v3b.fal.media/files/b/0a952cee/h5Z_d_ALvXsO4xKVuusGp_qa443BVv.png",
    "scene-6": "https://v3b.fal.media/files/b/0a952cf7/9DG0PVRZLtlk4xKgaT3d-_EXFD8GT7.png",
    "scene-8": "https://v3b.fal.media/files/b/0a952d04/GXhPBAcFIbdstBtam7G7G_lZArt44M.png",
}

def fal_submit(endpoint, payload):
    r = requests.post(f"https://queue.fal.run/{endpoint}", json=payload, headers=HEADERS)
    d = r.json()
    rid = d.get("request_id")
    if not rid:
        print(f"  ERROR submit: {d}", flush=True)
    return rid

def fal_wait(base_endpoint, request_id, label, result_key="audio"):
    for i in range(80):
        time.sleep(8)
        r = requests.get(f"https://queue.fal.run/{base_endpoint}/requests/{request_id}/status", headers=HEADERS)
        if not r.text.strip():
            print(f"  [{i+1}] {label}: empty, retry...", flush=True)
            continue
        try:
            state = r.json().get("status", "unknown")
        except Exception:
            print(f"  [{i+1}] {label}: bad json: {r.text[:80]}", flush=True)
            continue
        print(f"  [{i+1}] {label}: {state}", flush=True)
        if state == "COMPLETED":
            r2 = requests.get(f"https://queue.fal.run/{base_endpoint}/requests/{request_id}", headers=HEADERS)
            d = r2.json()
            if result_key == "audio":
                return d["audio"]["url"]
            elif result_key == "video":
                return d["video"]["url"]
        if state == "FAILED":
            print(f"  FAILED: {r.json()}", flush=True)
            return None
    return None

def download(url, path):
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"  saved {path.split('/')[-1]} ({len(r.content):,} bytes)", flush=True)
    return url  # return the fal.media URL for reuse in Avatar

def gen_tts(text, voice, stability, language_code, out_path, label):
    print(f"\n── TTS {label} ({voice}) ──", flush=True)
    rid = fal_submit("fal-ai/elevenlabs/tts/eleven-v3", {
        "text": text,
        "voice": voice,
        "stability": stability,
        "language_code": language_code
    })
    if not rid:
        return None
    print(f"  Submitted: {rid}", flush=True)
    # Status base is fal-ai/elevenlabs (not the full tts/eleven-v3 path)
    url = fal_wait("fal-ai/elevenlabs", rid, label, result_key="audio")
    if url:
        download(url, out_path)
    return url  # fal.media URL (reuse for Avatar)

def gen_avatar(image_url, audio_url, motion_prompt, out_path, label):
    print(f"\n── AVATAR {label} ──", flush=True)
    rid = fal_submit("fal-ai/kling-video/ai-avatar/v2/standard", {
        "image_url": image_url,
        "audio_url": audio_url,
        "motion_prompt": motion_prompt
    })
    if not rid:
        return None
    print(f"  Submitted: {rid}", flush=True)
    # Kling Avatar status base is fal-ai/kling-video (same as I2V)
    url = fal_wait("fal-ai/kling-video", rid, label, result_key="video")
    if url:
        r = requests.get(url)
        with open(out_path, "wb") as f:
            f.write(r.content)
        print(f"  saved {out_path.split('/')[-1]} ({len(r.content):,} bytes)", flush=True)
    return url

# ══════════════════════════════════════════════════════════════
# SCENE 2 — Kirk: TTS already saved, run Avatar directly
# ══════════════════════════════════════════════════════════════
tts2_url = "https://v3b.fal.media/files/b/0a952e19/h0lfzOuMdnoZeFU67hM8X_output.mp3"
print(f"\n── TTS scene-2: already saved ──", flush=True)
gen_avatar(
    SCENE_IMG_URLS["scene-2"], tts2_url,
    "Sudden sharp command. Kirk's jaw snaps shut after speaking — no hesitation, no explanation. Eyes narrow slightly, brow lowers. One micro-tilt of the head forward — the posture of absolute authority. Lips barely move. Every muscle controlled.",
    f"{OUT}/scenes/scene-2/scene-2.mp4", "scene-2-kirk"
)

# ══════════════════════════════════════════════════════════════
# SCENE 3 — Worf: «Капитан. Чехов — агент врага. Улики получены час назад.»
# ══════════════════════════════════════════════════════════════
tts3_url = gen_tts(
    "Капитан. Чехов — агент врага. Улики получены час назад.", "George", 0.20, "ru",
    f"{OUT}/scenes/scene-3/tts-3.mp3", "scene-3"
)
gen_avatar(
    SCENE_IMG_URLS["scene-3"], tts3_url,
    "Worf reports without emotion — a soldier delivering facts. Head slightly bowed in duty, not shame. Jaw barely moves. Eyes direct and unflinching. When he says the last words — a single beat of pause, brow lowering just slightly — the weight of how recently this happened.",
    f"{OUT}/scenes/scene-3/scene-3.mp4", "scene-3-worf"
)

# ══════════════════════════════════════════════════════════════
# SCENE 4 — Chekov TTS overlay only (no Avatar — behind glass)
# ══════════════════════════════════════════════════════════════
gen_tts(
    "Капитан!! Это подстава — я клянусь вам!!", "Charlie", 0.05, "ru",
    f"{OUT}/scenes/scene-4/tts-4.mp3", "scene-4-chekov"
)
print("  scene-4: TTS saved — will be overlaid on I2V clip (no lipsync, behind glass)", flush=True)

# ══════════════════════════════════════════════════════════════
# SCENE 5 — Kirk: «Отмените процедуру. Это приказ.»
# ══════════════════════════════════════════════════════════════
tts5_url = gen_tts(
    "Отмените процедуру. Это приказ.", "Daniel", 0.05, "ru",
    f"{OUT}/scenes/scene-5/tts-5.mp3", "scene-5"
)
gen_avatar(
    SCENE_IMG_URLS["scene-5"], tts5_url,
    "The quietest and most dangerous Kirk. Lips barely part — words come out flat, no inflection, no anger. Eyes absolutely still, locked like targeting sensors. A single slow exhale visible in the chest. After speaking — zero reaction, zero wait. He already expects to be obeyed.",
    f"{OUT}/scenes/scene-5/scene-5.mp4", "scene-5-kirk"
)

# ══════════════════════════════════════════════════════════════
# SCENE 6 — Worf: «Не могу, капитан. Приказ подписан флот-адмиралом. Лично.»
# ══════════════════════════════════════════════════════════════
tts6_url = gen_tts(
    "Не могу, капитан. Приказ подписан флот-адмиралом. Лично.", "George", 0.40, "ru",
    f"{OUT}/scenes/scene-6/tts-6.mp3", "scene-6"
)
gen_avatar(
    SCENE_IMG_URLS["scene-6"], tts6_url,
    "Worf speaks slowly — each word costing him something. Body rigid, eyes not fully meeting camera. Jaw tightens on 'не могу'. After 'флот-адмиралом' — a micro-pause, brow creasing with internal conflict. 'Лично' delivered with a weight that says he knows exactly how wrong this is. After speaking — lips press together. He does not look up.",
    f"{OUT}/scenes/scene-6/scene-6.mp4", "scene-6-worf"
)

# ══════════════════════════════════════════════════════════════
# SCENE 8 — Kirk: «Ворф. Кто на самом деле дал тебе этот приказ.»
# ══════════════════════════════════════════════════════════════
tts8_url = gen_tts(
    "Ворф. Кто на самом деле дал тебе этот приказ.", "Daniel", 0.55, "ru",
    f"{OUT}/scenes/scene-8/tts-8.mp3", "scene-8"
)
gen_avatar(
    SCENE_IMG_URLS["scene-8"], tts8_url,
    "Kirk speaks in profile, gaze fixed on Worf. Ice cold. Not a question — a statement. Lips part just enough for the words, then close like a vault. Eyes never blink, never shift. He already knows the answer. He is giving Worf exactly one chance to say it himself. After the last word — total stillness.",
    f"{OUT}/scenes/scene-8/scene-8.mp4", "scene-8-kirk"
)

print("\n=== PHASE 5 COMPLETE ===", flush=True)
