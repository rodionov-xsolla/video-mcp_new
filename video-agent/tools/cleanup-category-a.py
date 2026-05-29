#!/usr/bin/env python3
"""
Category A safe-delete: legacy bug folders + temp + orphans.
Lists with --dry-run (default), deletes with --apply.
"""
import json, os, subprocess, sys

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
APPLY = "--apply" in sys.argv

PREFIXES_TO_DELETE = [
    # _tmp test artifacts
    "_tmp/",
    # nested bug: assets/assets/{game}/... (legacy upload-asset.sh bug)
    "assets/",
    # nested bug: assets/videos/{game}/...
    "videos/",
    # nested bug: assets/tts/{game}/...
    "tts/",
    # nested bug: single mp3 dropped into assets/music/
    "music/",
    # orphan top-level dirs (no game prefix; migrated to roblox/_unsorted/)
    "motion-dance-bts/",
    "motion-dance-test/",
    "motion-dance-tpol/",
    "motion-test/",
]
BUCKET = "assets"

def curl(method, url, body=None):
    args = ["curl", "-sS", "--retry", "3", "--retry-delay", "2",
            "--connect-timeout", "10", "--max-time", "30",
            "-X", method, url,
            "-H", f"Authorization: Bearer {SERVICE_KEY}",
            "-H", "Content-Type: application/json",
            "-w", "\n%{http_code}"]
    if body is not None:
        args += ["-d", json.dumps(body)]
    r = subprocess.run(args, capture_output=True, text=True, check=True)
    out = r.stdout.rsplit("\n", 1)
    code = int(out[-1])
    try:
        payload = json.loads(out[0]) if out[0] else None
    except json.JSONDecodeError:
        payload = out[0]
    return code, payload

def walk(prefix):
    """Yield all file paths under prefix (recursive)."""
    queue = [prefix]
    while queue:
        p = queue.pop(0)
        offset = 0
        while True:
            code, items = curl("POST", f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET}",
                                {"prefix": p, "limit": 1000, "offset": offset})
            if not items:
                break
            for it in items:
                name = it["name"]
                full = p + name
                if it.get("id") is None:
                    queue.append(full + "/")
                else:
                    yield full
            if len(items) < 1000:
                break
            offset += 1000

def bulk_delete(paths, batch=100):
    """Supabase bulk delete: DELETE /storage/v1/object/{bucket} with {prefixes: [...]}."""
    deleted = 0
    for i in range(0, len(paths), batch):
        chunk = paths[i:i+batch]
        code, payload = curl("DELETE", f"{SUPABASE_URL}/storage/v1/object/{BUCKET}",
                              {"prefixes": chunk})
        if code == 200:
            n = len(payload) if isinstance(payload, list) else len(chunk)
            deleted += n
            print(f"  deleted batch {i}-{i+len(chunk)}: {n} ok", file=sys.stderr)
        else:
            print(f"  FAIL batch {i}: code={code} payload={payload}", file=sys.stderr)
    return deleted

def main():
    all_paths = []
    for prefix in PREFIXES_TO_DELETE:
        files = list(walk(prefix))
        print(f"[{prefix}] {len(files)} files", file=sys.stderr)
        all_paths.extend(files)

    print(f"\nTotal to delete: {len(all_paths)}", file=sys.stderr)
    if not APPLY:
        print("\nDRY-RUN — re-run with --apply to actually delete.", file=sys.stderr)
        for p in all_paths[:30]:
            print(f"  {p}")
        if len(all_paths) > 30:
            print(f"  ... and {len(all_paths)-30} more")
        return

    print("\nApplying delete...", file=sys.stderr)
    n = bulk_delete(all_paths)
    print(f"\n[done] deleted {n}/{len(all_paths)}", file=sys.stderr)

if __name__ == "__main__":
    main()
