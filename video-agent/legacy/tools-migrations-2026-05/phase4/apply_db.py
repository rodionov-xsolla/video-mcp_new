#!/usr/bin/env python3
"""
Phase 4 step 2: apply DB changes to game_assets.
Plan (2A + delete-dead):
  - 77 reusable refs  → PATCH url
  - game_tag normalize → PATCH game_tag  (Kekele/MLBB/MarvelSnap/Oxide → lowercase/kebab)
  - 48 episode-junk    → DELETE
  - 3 dead links       → DELETE (archer-mature-captain, Captain Janeway, king-rex)
  - 5 Cosplay          → keep url, game_tag normalize only
  - 1 empty (Lancelot) → keep, game_tag normalize only

--dry-run (default) prints the action plan. --apply executes.
"""
import csv, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
APPLY = "--apply" in sys.argv

GAME_TAG_NORMALIZE = {
    "Kekele": "kekele",
    "MLBB": "mlbb",
    "MarvelSnap": "marvel-snap",
    "Oxide": "oxide",
}

# Dead-link rows identified manually (files gone from storage)
DEAD_CHARACTER_NAMES = {
    ("star-trek-timelines", "archer-mature-captain", "reference_image"),
    ("star-trek-timelines", "Captain Janeway", "reference_image"),
    ("roblox", "king-rex", "reference_image"),
}

def rest(method, path, body=None, extra_headers=None):
    args = ["curl", "-sS", "--retry", "3", "--retry-delay", "2",
            "--connect-timeout", "10", "--max-time", "30",
            "-X", method, f"{SUPABASE_URL}/rest/v1/{path}",
            "-H", f"apikey: {KEY}",
            "-H", f"Authorization: Bearer {KEY}",
            "-H", "Content-Type: application/json",
            "-w", "\n%{http_code}"]
    for h in (extra_headers or []):
        args += ["-H", h]
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

rows = list(csv.DictReader(open(HERE / "db_url_mapping.tsv"), delimiter="\t"))

actions = []  # (id, action, detail)
for r in rows:
    rid = r["id"]
    gt = r["game_tag"]
    cn = r["character_name"]
    at = r["asset_type"]
    status = r["status"]
    new_url = r["new_url"]
    old_url = r["old_url"]

    is_dead = (gt, cn, at) in DEAD_CHARACTER_NAMES
    is_episode = status == "MAPPED" and "/public/episodes/" in new_url
    is_clean = status == "MAPPED" and "/public/assets/" in new_url
    norm_gt = GAME_TAG_NORMALIZE.get(gt)

    if is_dead:
        actions.append((rid, "DELETE", f"dead link: {gt}/{cn}/{at}"))
    elif is_episode:
        actions.append((rid, "DELETE", f"episode junk: {gt}/{cn} → {new_url.split('/public/')[-1]}"))
    elif is_clean:
        # king-rex clean but file missing → already caught by is_dead; here only valid ones
        patch = {"url": new_url}
        if norm_gt:
            patch["game_tag"] = norm_gt
        actions.append((rid, "PATCH", patch))
    else:
        # cosplay / empty / no-plan-keep → only game_tag normalize if needed
        if norm_gt:
            actions.append((rid, "PATCH", {"game_tag": norm_gt}))
        else:
            actions.append((rid, "NOOP", f"{gt}/{cn}/{at} status={status}"))

from collections import Counter
summ = Counter(a[1] for a in actions)
print("=== action plan ===", file=sys.stderr)
for k, v in summ.items():
    print(f"  {k:8} {v}", file=sys.stderr)
print(f"  TOTAL    {len(actions)}", file=sys.stderr)

if not APPLY:
    print("\nDRY-RUN. Sample actions:", file=sys.stderr)
    for rid, act, det in actions[:8]:
        print(f"  {act} {rid} :: {det}", file=sys.stderr)
    print("  ...", file=sys.stderr)
    print("\nRe-run with --apply to execute.", file=sys.stderr)
    sys.exit(0)

# Execute: PATCH first, DELETE last
log = open(HERE / "apply_db.log", "a")
import datetime
log.write(f"\n=== apply {datetime.datetime.now().isoformat()} ===\n")
stats = Counter()
for rid, act, det in actions:
    if act == "NOOP":
        stats["NOOP"] += 1
        continue
    if act == "PATCH":
        code, payload = rest("PATCH", f"game_assets?id=eq.{rid}", det,
                             extra_headers=["Prefer: return=minimal"])
        ok = code in (200, 204)
    elif act == "DELETE":
        code, payload = rest("DELETE", f"game_assets?id=eq.{rid}",
                             extra_headers=["Prefer: return=minimal"])
        ok = code in (200, 204)
    stats["OK" if ok else "FAIL"] += 1
    line = f"{'OK' if ok else 'FAIL'}\t{act}\t{rid}\t{code}\t{det}"
    log.write(line + "\n")
    if not ok:
        print(f"  FAIL {act} {rid} code={code}: {payload}", file=sys.stderr)

log.write(f"=== stats {dict(stats)} ===\n")
log.close()
print(f"\n[done] {dict(stats)}", file=sys.stderr)
