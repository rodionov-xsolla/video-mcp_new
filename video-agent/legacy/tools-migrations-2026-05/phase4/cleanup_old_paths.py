#!/usr/bin/env python3
"""
Phase 4b: delete OLD storage paths that have a verified NEW copy.
Safety rules:
  - only delete source paths from migration-plan.tsv
  - skip if old == new (already-target rows)
  - skip _skip target rows
  - skip shared/ (multi-game, not migrated)
  - verify NEW copy returns 200 before deleting OLD
  - never delete anything outside the migration plan's source set
--dry-run (default) lists. --apply deletes.
"""
import csv, json, os, subprocess, sys, urllib.parse
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent
PLAN = HERE.parent / "migration-plan.tsv"
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
APPLY = "--apply" in sys.argv

def head(bucket, path):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{urllib.parse.quote(path)}"
    r = subprocess.run(["curl","-sS","--retry","2","--connect-timeout","10","--max-time","30",
                        "-o","/dev/null","-w","%{http_code}","-I",url,
                        "-H",f"Authorization: Bearer {KEY}"],
                       capture_output=True,text=True)
    return r.stdout.strip()

def bulk_delete(bucket, paths, batch=100):
    deleted=0
    for i in range(0,len(paths),batch):
        chunk=paths[i:i+batch]
        r=subprocess.run(["curl","-sS","--retry","2","--connect-timeout","10","--max-time","60",
                          "-X","DELETE",f"{SUPABASE_URL}/storage/v1/object/{bucket}",
                          "-H",f"apikey: {KEY}","-H",f"Authorization: Bearer {KEY}",
                          "-H","Content-Type: application/json",
                          "-w","\n%{http_code}",
                          "-d",json.dumps({"prefixes":chunk})],
                         capture_output=True,text=True)
        out=r.stdout.rsplit("\n",1)
        code=int(out[-1]) if out[-1].isdigit() else 0
        if code==200:
            try: n=len(json.loads(out[0]))
            except Exception: n=len(chunk)
            deleted+=n
            print(f"  deleted {bucket} batch {i}-{i+len(chunk)}: {n}",file=sys.stderr)
        else:
            print(f"  FAIL {bucket} batch {i}: code={code} {out[0][:200]}",file=sys.stderr)
    return deleted

# Build candidate delete set from plan
rows=[]
with open(PLAN) as f:
    next(f)
    for line in f:
        p=line.rstrip("\n").split("\t")
        if len(p)<7: continue
        ob,op,nb,np_,rule,conf,note=p
        rows.append((ob,op,nb,np_,rule,conf,note))

# CRITICAL invariant: never delete a file that is itself a migration DESTINATION.
# The plan was regenerated after copy, so new files got re-walked as sources.
dest_set=set()
for ob,op,nb,np_,rule,conf,note in rows:
    if nb=="_skip": continue
    dest_set.add(f"{nb}/{np_}")

candidates=defaultdict(list)   # source_bucket -> [(op,nb,np_)]
skipped_same=0
skipped_shared=0
skipped_skip=0
skipped_is_dest=0
skipped_already=0
for ob,op,nb,np_,rule,conf,note in rows:
    if nb=="_skip": skipped_skip+=1; continue
    if op.startswith("shared/"): skipped_shared+=1; continue
    if ob==nb and op==np_: skipped_same+=1; continue        # old==new
    if rule.startswith("already"): skipped_already+=1; continue  # re-walked new file
    if f"{ob}/{op}" in dest_set:                            # source IS a migration target
        skipped_is_dest+=1; continue
    candidates[ob].append((op,nb,np_))

print("=== candidate sources to delete ===",file=sys.stderr)
total=sum(len(v) for v in candidates.values())
print(f"  total candidates: {total}",file=sys.stderr)
print(f"  skipped already-target(same): {skipped_same}",file=sys.stderr)
print(f"  skipped already-* rule: {skipped_already}",file=sys.stderr)
print(f"  skipped source-is-a-dest: {skipped_is_dest}",file=sys.stderr)
print(f"  skipped shared/: {skipped_shared}",file=sys.stderr)
print(f"  skipped _skip: {skipped_skip}",file=sys.stderr)

# Verify new copy exists before marking old for delete
to_delete=defaultdict(list)
missing_new=[]
for ob, items in candidates.items():
    for op,nb,np_ in items:
        code=head(nb,np_)
        if code=="200":
            to_delete[ob].append(op)
        else:
            missing_new.append((ob,op,nb,np_,code))

print(f"\n=== verification ===",file=sys.stderr)
print(f"  safe to delete (new copy 200): {sum(len(v) for v in to_delete.values())}",file=sys.stderr)
print(f"  WITHHELD (new copy missing): {len(missing_new)}",file=sys.stderr)
for m in missing_new[:20]:
    print(f"    WITHHELD {m[4]} {m[0]}/{m[1]} → {m[2]}/{m[3]}",file=sys.stderr)

# Write delete manifest
with open(HERE/"delete_manifest.tsv","w") as f:
    f.write("bucket\tpath\n")
    for b,paths in to_delete.items():
        for p in paths:
            f.write(f"{b}\t{p}\n")

if not APPLY:
    print(f"\nDRY-RUN. Manifest: {HERE/'delete_manifest.tsv'}",file=sys.stderr)
    print("Re-run with --apply to delete.",file=sys.stderr)
    sys.exit(0)

print("\n=== applying delete ===",file=sys.stderr)
grand=0
for b,paths in to_delete.items():
    grand+=bulk_delete(b,paths)
print(f"\n[done] deleted {grand} old files",file=sys.stderr)
