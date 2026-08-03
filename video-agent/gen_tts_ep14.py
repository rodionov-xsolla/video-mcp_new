#!/usr/bin/env python3
"""
EP14 Neuvillette TTS re-generation.
Generates per-clip Chatterbox TTS (7 clips individually) + MiniMax Music bg track.
"""
import json
import os
import subprocess
import time
import sys

FAL_KEY = os.environ.get("FAL_KEY", "")
if not FAL_KEY:
    sys.exit("FAL_KEY not set")

OUTPUT_DIR = "/Users/clawbot/.openclaw/workspace/video-mcp-new/video-agent/output/2026-07-24/genshin-impact/character-story/20260724-110414-55868"
VOICE_REF_URL = "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/genshin-impact/characters/neuvillette/voice-1.mp3"

CLIPS = [
    {
        "clip_id": 1,
        "text": "Five hundred years. I could not weep. I watched and endured every unanswered prayer.",
        "exaggeration": 0.65, "cfg": 0.6, "temperature": 0.75,
    },
    {
        "clip_id": 2,
        "text": "Grab free Primogems from the link in bio. Now — here's my story.",
        "exaggeration": 0.45, "cfg": 0.5, "temperature": 0.7,
    },
    {
        "clip_id": 3,
        "text": "I was the Dragon of Water before laws existed. These tides were mine.",
        "exaggeration": 0.6, "cfg": 0.55, "temperature": 0.75,
    },
    {
        "clip_id": 4,
        "text": "They called me Iudex. I wore the title like armor, hiding what I truly was.",
        "exaggeration": 0.55, "cfg": 0.55, "temperature": 0.75,
    },
    {
        "clip_id": 5,
        "text": "A prophecy: Fontaine's people would dissolve. My power was bound. I could not act.",
        "exaggeration": 0.7, "cfg": 0.6, "temperature": 0.75,
    },
    {
        "clip_id": 6,
        "text": "Furina bore the burden for five centuries. She sacrificed herself. I could not save her.",
        "exaggeration": 0.7, "cfg": 0.6, "temperature": 0.75,
    },
    {
        "clip_id": 7,
        "text": "Then I wept. My tears fell as rain over Fontaine — grief, relief, and something like hope.",
        "exaggeration": 0.6, "cfg": 0.55, "temperature": 0.7,
    },
]

def curl_json(method, url, body_file=None, extra_headers=None):
    cmd = ["curl", "-s", "-X", method, url,
           "-H", f"Authorization: Key {FAL_KEY}",
           "-H", "Content-Type: application/json"]
    if body_file:
        cmd += ["-d", f"@{body_file}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not result.stdout.strip():
        return {}
    return json.loads(result.stdout)

def submit_chatterbox(clip):
    body = {
        "text": clip["text"],
        "audio_url": VOICE_REF_URL,
        "exaggeration": clip["exaggeration"],
        "cfg": clip["cfg"],
        "temperature": clip["temperature"],
    }
    body_file = f"/tmp/tts-cb-{clip['clip_id']}.json"
    with open(body_file, "w") as f:
        json.dump(body, f, ensure_ascii=False)
    resp = curl_json("POST", "https://queue.fal.run/fal-ai/chatterbox/text-to-speech", body_file)
    req_id = resp.get("request_id")
    print(f"  scene-{clip['clip_id']}: submitted → {req_id}")
    return req_id

def submit_music():
    body = {
        "prompt": "dark melancholic orchestral with gentle water motifs, emotional and cinematic, instrumental, no vocals, no lyrics, suitable for a vertical short video",
        "is_instrumental": True,
        "duration": 45,
    }
    with open("/tmp/music-body.json", "w") as f:
        json.dump(body, f)
    resp = curl_json("POST", "https://queue.fal.run/fal-ai/minimax-music/v2.6", "/tmp/music-body.json")
    req_id = resp.get("request_id")
    print(f"  bg-music: submitted → {req_id}")
    return req_id

def poll(base, req_id, label, max_wait=600):
    start = time.time()
    while time.time() - start < max_wait:
        resp = curl_json("GET", f"https://queue.fal.run/{base}/requests/{req_id}/status")
        status = resp.get("status", "")
        print(f"  [{label}] status: {status}")
        if status == "COMPLETED":
            return True
        elif status == "FAILED":
            print(f"  [{label}] FAILED: {resp}")
            return False
        time.sleep(15)
    print(f"  [{label}] TIMEOUT after {max_wait}s")
    return False

def get_result(base, req_id):
    return curl_json("GET", f"https://queue.fal.run/{base}/requests/{req_id}")

def ffprobe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True, text=True
    )
    data = json.loads(r.stdout)
    return float(data["format"]["duration"])

def download_convert_clip(audio_url, clip_id):
    wav_path = f"/tmp/tts-{clip_id}.wav"
    scene_dir = f"{OUTPUT_DIR}/scenes/scene-{clip_id}"
    mp3_path = f"{scene_dir}/scene-{clip_id}.mp3"
    os.makedirs(scene_dir, exist_ok=True)

    subprocess.run(["curl", "-sSL", "-o", wav_path, audio_url], check=True)
    wav_size = os.path.getsize(wav_path)
    print(f"  scene-{clip_id}: WAV downloaded {wav_size} bytes")

    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path],
        capture_output=True, check=True
    )
    mp3_size = os.path.getsize(mp3_path)
    dur = ffprobe_duration(mp3_path)
    print(f"  scene-{clip_id}: MP3 saved → {mp3_size/1024:.1f}KB, {dur:.2f}s")
    return dur, mp3_size

def download_music(audio_url):
    dest = f"{OUTPUT_DIR}/bg-music.mp3"
    subprocess.run(["curl", "-sSL", "-o", dest, audio_url], check=True)
    size = os.path.getsize(dest)
    dur = ffprobe_duration(dest)
    print(f"  bg-music.mp3: {size/1024:.1f}KB, {dur:.2f}s")
    return dur, size


# === PHASE 1: Submit all TTS ===
print("\n=== Phase 1: Submit TTS (batch 1: clips 1-4) ===")
tts_ids = {}
for clip in CLIPS[:4]:
    tts_ids[clip["clip_id"]] = submit_chatterbox(clip)
    time.sleep(1)

print("\n=== Phase 1b: Submit TTS (batch 2: clips 5-7) + music ===")
for clip in CLIPS[4:]:
    tts_ids[clip["clip_id"]] = submit_chatterbox(clip)
    time.sleep(1)

music_id = submit_music()

# === PHASE 2: Poll + download TTS ===
print("\n=== Phase 2: Poll & download TTS ===")
durations = {}
sizes = {}

for clip in CLIPS:
    cid = clip["clip_id"]
    req_id = tts_ids[cid]
    print(f"\nPolling scene-{cid} ({req_id})...")
    ok = poll("fal-ai/chatterbox", req_id, f"scene-{cid}")
    if ok:
        res = get_result("fal-ai/chatterbox", req_id)
        audio_url = res.get("audio", {}).get("url")
        if audio_url:
            dur, sz = download_convert_clip(audio_url, cid)
            durations[cid] = dur
            sizes[cid] = sz
        else:
            print(f"  scene-{cid}: ERROR - no audio URL. Response: {res}")
    else:
        print(f"  scene-{cid}: generation FAILED")

# === PHASE 3: Poll + download music ===
print(f"\n=== Phase 3: Poll & download bg-music ({music_id}) ===")
ok = poll("fal-ai/minimax-music", music_id, "bg-music")
music_dur = 0
music_size = 0
if ok:
    res = get_result("fal-ai/minimax-music", music_id)
    music_url = res.get("audio", {}).get("url") or res.get("audio_file", {}).get("url")
    if music_url:
        music_dur, music_size = download_music(music_url)
    else:
        print(f"  bg-music: ERROR - no audio URL. Response: {res}")
else:
    print("  bg-music: FAILED")

# === REPORT ===
print("\n" + "="*50)
print("FINAL REPORT — EP14 Neuvillette TTS + Music")
print("="*50)
total_tts = 0
for cid in range(1, 8):
    dur = durations.get(cid, 0)
    sz = sizes.get(cid, 0)
    ok_str = "OK" if sz > 5120 else "WARNING: <5KB"
    print(f"  scene-{cid}.mp3: {dur:.2f}s | {sz/1024:.1f}KB | {ok_str}")
    total_tts += dur

atempo = total_tts / 35.0 if total_tts > 0 else 0
print(f"\nTotal TTS duration: {total_tts:.2f}s")
print(f"Timeline: 35.0s")
print(f"Expected atempo: {atempo:.3f}x {'OK (≤1.4)' if atempo <= 1.4 else 'WARNING: >1.4!'}")
print(f"\nbg-music.mp3: {music_dur:.2f}s | {music_size/1024:.1f}KB | {'OK' if music_size > 5120 else 'WARNING'}")
print("="*50)
