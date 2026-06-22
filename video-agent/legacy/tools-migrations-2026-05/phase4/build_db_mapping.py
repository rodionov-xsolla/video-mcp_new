#!/usr/bin/env python3
"""
Phase 4 step 1: build DB url-migration mapping.
Reads game_assets_backup.json + migration-plan.tsv, produces:
  - db_url_mapping.tsv  (id, game_tag, char, type, old_url, new_url, status, note)
No DB writes. Pure analysis.
"""
import json, sys, os, urllib.parse
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent
PLAN = HERE.parent / "migration-plan.tsv"
BACKUP = HERE / "game_assets_backup.json"
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")

PUBLIC_PREFIX = "/storage/v1/object/public/"

# Build plan lookup: old "bucket/path" -> "new_bucket/new_path"
plan = {}
with open(PLAN) as f:
    next(f)  # header
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 7:
            continue
        ob, op, nb, np_, rule, conf, note = parts
        if nb == "_skip":
            continue
        plan[f"{ob}/{op}"] = f"{nb}/{np_}"

def url_to_bucketpath(url):
    """Extract 'bucket/path' from a Supabase public URL. Returns None if not a storage URL."""
    if not url or PUBLIC_PREFIX not in url:
        return None
    tail = url.split(PUBLIC_PREFIX, 1)[1]
    return urllib.parse.unquote(tail)

rows = json.load(open(BACKUP))
out = []
stats = defaultdict(int)

for r in rows:
    rid = r["id"]
    url = r.get("url") or ""
    bp = url_to_bucketpath(url)
    if bp is None:
        # Not a storage URL (e.g. Cosplay sources, or empty)
        if not url:
            status, new_url, note = "EMPTY_URL", "", "no url in row"
        elif "Cosplay%20sources" in url or "Cosplay sources" in url:
            status, new_url, note = "EXTERNAL_KEEP", url, "Cosplay sources bucket — not migrated"
        else:
            status, new_url, note = "UNKNOWN_URL", url, "url not a public storage url"
        stats[status] += 1
        out.append((rid, r["game_tag"], r.get("character_name") or "", r["asset_type"], url, new_url, status, note))
        continue

    if bp in plan:
        new_bp = plan[bp]
        new_url = f"{SUPABASE_URL}{PUBLIC_PREFIX}{new_bp}"
        status, note = "MAPPED", ""
    else:
        # Source not in plan — maybe already new-style, or king-rex (missing), or deleted
        new_url = url
        status, note = "NO_PLAN_ENTRY", f"bucket/path not in migration plan: {bp}"
    stats[status] += 1
    out.append((rid, r["game_tag"], r.get("character_name") or "", r["asset_type"], url, new_url, status, note))

# Write mapping
with open(HERE / "db_url_mapping.tsv", "w") as f:
    f.write("id\tgame_tag\tcharacter_name\tasset_type\told_url\tnew_url\tstatus\tnote\n")
    for o in out:
        f.write("\t".join(str(x) for x in o) + "\n")

print("=== status counts ===", file=sys.stderr)
for k, v in sorted(stats.items()):
    print(f"  {k:18} {v}", file=sys.stderr)

# Detect UNIQUE conflicts: after remap, would two rows of same (game_tag, char, type) point differently?
# Also detect game_tag normalization needs.
print("\n=== game_tag values (need normalization?) ===", file=sys.stderr)
tags = defaultdict(int)
for r in rows:
    tags[r["game_tag"]] += 1
for t, n in sorted(tags.items()):
    print(f"  {t!r:30} {n}", file=sys.stderr)

# Detect duplicate (game_tag, character_name, asset_type) — current UNIQUE key
print("\n=== current duplicate keys (game_tag, char, type) ===", file=sys.stderr)
keys = defaultdict(list)
for r in rows:
    k = (r["game_tag"], r.get("character_name"), r["asset_type"])
    keys[k].append(r["id"])
dup = {k: v for k, v in keys.items() if len(v) > 1}
if not dup:
    print("  (none)", file=sys.stderr)
for k, ids in dup.items():
    print(f"  {k} → {len(ids)} rows: {ids}", file=sys.stderr)

# Detect duplicate by URL (same file, multiple rows)
print("\n=== duplicate by old_url (same file registered multiple times) ===", file=sys.stderr)
byurl = defaultdict(list)
for r in rows:
    if r.get("url"):
        byurl[r["url"]].append((r["id"], r["game_tag"], r.get("character_name"), r["asset_type"]))
dupurl = {k: v for k, v in byurl.items() if len(v) > 1}
if not dupurl:
    print("  (none)", file=sys.stderr)
for u, items in dupurl.items():
    short = u.split(PUBLIC_PREFIX)[-1] if PUBLIC_PREFIX in u else u
    print(f"  {short}", file=sys.stderr)
    for it in items:
        print(f"      {it}", file=sys.stderr)

print(f"\n[output] {HERE / 'db_url_mapping.tsv'}", file=sys.stderr)
