#!/usr/bin/env python3
"""
EP14 Neuvillette TTS resume — uses request_ids from the first run.
Also polls music. Converts downloaded WAVs and any remaining clips.
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

# Request IDs from the first run
TTS_IDS = {
    1: "019f93fc-423f-7362-b90e-f6c5f28b173e",
    2: "019f93fc-4aa2-7712-ba8e-6270ee65efc4",
    3: "019f93fc-51a6-7a51-82a9-e774632a0e3c",
    4: "019f93fc-5bad-71d0-ad4d-6536bea6a981",
    5: "019f93fc-65e5-75c1-9fc1-bf64198b8576",
    6: "019f93fc-6de4-7d80-89e0-05a085a3ab32",
    7: "019f93fc-7ac1-7302-8ce1-ea070c7fc9eb",
}
MUSIC_ID = "019f93fc-82e6-78b2-bc9e-5f558cc59cc9"

CLIPS = [
    {"clip_id": 1, "text": "Five hundred years. I could not weep. I watched and endured every unanswered prayer.", "exaggeration": 0.65, "cfg": 0.6, "temperature": 0.75},
    {"clip_id": 2, "text": "Grab free Primogems from the link in bio. Now — here's my story.", "exaggeration": 0.45, "cfg": 0.5, "temperature": 0.7},
    {"clip_id": 3, "text": "I was the Dragon of Water before laws existed. These tides were mine.", "exaggeration": 0.6, "cfg": 0.55, "temperature": 0.75},
    {"clip_id": 4, "text": "They called me Iudex. I wore the title like armor, hiding what I truly was.", "exaggeration": 0.55, "cfg": 0.55, "temperature": 0.75},
    {"clip_id": 5, "text": "A prophecy: Fontaine's people would dissolve. My power was bound. I could not act.", "exaggeration": 0.7, "cfg": 0.6, "temperature": 0.75},
    {"clip_id": 6, "text": "Furina bore the burden for five centuries. She sacrificed herself. I could not save her.", "exaggeration": 0.7, "cfg": 0.6, "temperature": 0.75},
    {"clip_id": 7, "text": "Then I wept. My tears fell as rain over Fontaine — grief, relief, and something like hope.", "exaggeration": 0.6, "cfg": 0.55, "temperature": 0.7},
]

def curl_json(method, url, body_file=None):
    cmd = ["curl", "-s", "-X", method, url,
           "-H", f"Authorization: Key {FAL_KEY}",
           "-H", "Content-Type: application/json"]
    if body_file:
        cmd += ["-d", f"@{body_file}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    raw = result.stdout.strip() or result.stderr.strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        print(f"  PARSE ERROR: {raw[:200]}")
        return {}

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
        status = resp.get("status", "UNKNOWN")
        print(f"  [{label}] {status}")
        if status == "COMPLETED":
            return True
        elif status == "FAILED":
            print(f"  [{label}] FAILED: {resp}")
            return False
        time.sleep(15)
    print(f"  [{label}] TIMEOUT")
    return False

def get_result(base, req_id):
    return curl_json("GET", f"https://queue.fal.run/{base}/requests/{req_id}")

def ffprobe_duration(path):
    """ffprobe outputs JSON to stderr on this system."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True
    )
    raw = r.stdout.strip() or r.stderr.strip()
    if not raw:
        return 0.0
    try:
        data = json.loads(raw)
        return float(data.get("format", {}).get("duration", 0))
    except Exception:
        # fallback: try parsing stderr
        try:
            return float(r.stderr.strip())
        except Exception:
            return 0.0

def convert_wav_to_mp3(wav_path, clip_id):
    scene_dir = f"{OUTPUT_DIR}/scenes/scene-{clip_id}"
    mp3_path = f"{scene_dir}/scene-{clip_id}.mp3"
    os.makedirs(scene_dir, exist_ok=True)
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  scene-{clip_id}: ffmpeg error: {result.stderr[-300:]}")
        return 0, 0
    mp3_size = os.path.getsize(mp3_path)
    dur = ffprobe_duration(mp3_path)
    return dur, mp3_size

def download_and_process(audio_url, clip_id):
    wav_path = f"/tmp/tts-{clip_id}.wav"
    subprocess.run(["curl", "-sSL", "-o", wav_path, audio_url], check=True)
    wav_size = os.path.getsize(wav_path)
    print(f"  scene-{clip_id}: WAV {wav_size} bytes")
    return convert_wav_to_mp3(wav_path, clip_id)

def download_music(audio_url):
    dest = f"{OUTPUT_DIR}/bg-music.mp3"
    subprocess.run(["curl", "-sSL", "-o", dest, audio_url], check=True)
    size = os.path.getsize(dest)
    dur = ffprobe_duration(dest)
    return dur, size


# ========== MAIN ==========

durations = {}
sizes = {}

# Check which clips already have WAV downloaded (from first run)
print("=== Checking existing WAVs ===")
for clip in CLIPS:
    cid = clip["clip_id"]
    wav_path = f"/tmp/tts-{cid}.wav"
    mp3_path = f"{OUTPUT_DIR}/scenes/scene-{cid}/scene-{cid}.mp3"

    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 5000:
        print(f"  scene-{cid}: WAV present ({os.path.getsize(wav_path)} bytes) → converting")
        dur, sz = convert_wav_to_mp3(wav_path, cid)
        if sz > 0:
            durations[cid] = dur
            sizes[cid] = sz
            print(f"  scene-{cid}: {dur:.2f}s, {sz/1024:.1f}KB ✓")
        else:
            print(f"  scene-{cid}: conversion FAILED, will re-generate")
    else:
        print(f"  scene-{cid}: WAV missing, will poll from API")

# Poll any clips whose WAV wasn't available
missing = [c for c in CLIPS if c["clip_id"] not in durations]
if missing:
    print(f"\n=== Polling missing clips: {[c['clip_id'] for c in missing]} ===")

for clip in missing:
    cid = clip["clip_id"]
    req_id = TTS_IDS[cid]
    print(f"\nPolling scene-{cid} ({req_id})...")
    ok = poll("fal-ai/chatterbox", req_id, f"scene-{cid}")
    if ok:
        res = get_result("fal-ai/chatterbox", req_id)
        audio_url = res.get("audio", {}).get("url")
        if audio_url:
            dur, sz = download_and_process(audio_url, cid)
            if sz > 0:
                durations[cid] = dur
                sizes[cid] = sz
                print(f"  scene-{cid}: {dur:.2f}s, {sz/1024:.1f}KB ✓")
            else:
                print(f"  scene-{cid}: conversion FAILED")
        else:
            print(f"  scene-{cid}: no audio URL in result: {res}")
            # Resubmit
            print(f"  Resubmitting scene-{cid}...")
            new_id = submit_chatterbox(clip)
            if new_id:
                ok2 = poll("fal-ai/chatterbox", new_id, f"scene-{cid}-retry")
                if ok2:
                    res2 = get_result("fal-ai/chatterbox", new_id)
                    url2 = res2.get("audio", {}).get("url")
                    if url2:
                        dur, sz = download_and_process(url2, cid)
                        durations[cid] = dur
                        sizes[cid] = sz
    else:
        print(f"  scene-{cid}: FAILED, resubmitting...")
        new_id = submit_chatterbox(clip)
        if new_id:
            ok2 = poll("fal-ai/chatterbox", new_id, f"scene-{cid}-retry")
            if ok2:
                res2 = get_result("fal-ai/chatterbox", new_id)
                url2 = res2.get("audio", {}).get("url")
                if url2:
                    dur, sz = download_and_process(url2, cid)
                    durations[cid] = dur
                    sizes[cid] = sz

# Poll bg-music
print(f"\n=== Polling bg-music ({MUSIC_ID}) ===")
music_dur = 0
music_size = 0
ok = poll("fal-ai/minimax-music", MUSIC_ID, "bg-music")
if ok:
    res = get_result("fal-ai/minimax-music", MUSIC_ID)
    music_url = (res.get("audio") or {}).get("url") or (res.get("audio_file") or {}).get("url")
    if music_url:
        music_dur, music_size = download_music(music_url)
        print(f"  bg-music.mp3: {music_dur:.2f}s, {music_size/1024:.1f}KB ✓")
    else:
        print(f"  bg-music: no URL in result: {res}")
        print("  Resubmitting music...")
        new_music_id = submit_music()
        ok2 = poll("fal-ai/minimax-music", new_music_id, "bg-music-retry")
        if ok2:
            res2 = get_result("fal-ai/minimax-music", new_music_id)
            url2 = (res2.get("audio") or {}).get("url") or (res2.get("audio_file") or {}).get("url")
            if url2:
                music_dur, music_size = download_music(url2)
else:
    print("  Music FAILED, resubmitting...")
    new_music_id = submit_music()
    ok2 = poll("fal-ai/minimax-music", new_music_id, "bg-music-retry")
    if ok2:
        res2 = get_result("fal-ai/minimax-music", new_music_id)
        url2 = (res2.get("audio") or {}).get("url") or (res2.get("audio_file") or {}).get("url")
        if url2:
            music_dur, music_size = download_music(url2)
            print(f"  bg-music.mp3: {music_dur:.2f}s, {music_size/1024:.1f}KB ✓")

# ========== FINAL REPORT ==========
print("\n" + "="*55)
print("FINAL REPORT — EP14 Neuvillette TTS + Music")
print("="*55)
total_tts = 0
all_ok = True
for cid in range(1, 8):
    dur = durations.get(cid, 0.0)
    sz = sizes.get(cid, 0)
    status = "✓" if sz > 5120 else "⚠ <5KB"
    print(f"  scene-{cid}.mp3  {dur:.2f}s  {sz/1024:.1f}KB  {status}")
    total_tts += dur
    if sz <= 5120:
        all_ok = False

atempo = total_tts / 35.0 if total_tts > 0 else 0
atempo_ok = atempo <= 1.4
print(f"\nTotal TTS:   {total_tts:.2f}s")
print(f"Timeline:    35.0s")
print(f"atempo:      {atempo:.3f}×  {'✓ (≤1.4×)' if atempo_ok else '⚠ EXCEEDS 1.4×!'}")

ms_ok = music_size > 5120
print(f"\nbg-music.mp3  {music_dur:.2f}s  {music_size/1024:.1f}KB  {'✓' if ms_ok else '⚠ <5KB'}")
print("="*55)
print(f"All files >5KB: {'YES' if all_ok and ms_ok else 'NO — see warnings above'}")
