#!/usr/bin/env python3
"""
Storage migration planner. Walks the Supabase `assets` bucket, applies
mapping rules, and emits a TSV plan. No mutation in --dry-run (default).

Output columns: old_bucket, old_path, new_bucket, new_path, rule, confidence, notes
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

SOURCE_BUCKETS = ["assets"]  # also walk these top-level buckets
DRY_RUN = "--apply" not in sys.argv
OUT_TSV = Path(__file__).parent.parent / "tools" / "migration-plan.tsv"
APPLY_LOG = Path(__file__).parent.parent / "tools" / "migration-apply.log"

# Optional --filter <prefix> restricts apply to rows whose old_path starts with prefix
FILTER_PREFIX = None
if "--filter" in sys.argv:
    i = sys.argv.index("--filter")
    if i + 1 < len(sys.argv):
        FILTER_PREFIX = sys.argv[i + 1]

# ---------- Supabase helpers ----------

def curl_json(method: str, url: str, body=None, retries=4):
    args = ["curl", "-sS", "--retry", "3", "--retry-delay", "2",
            "--connect-timeout", "10", "--max-time", "60",
            "-X", method, url,
            "-H", f"Authorization: Bearer {SERVICE_KEY}",
            "-H", "Content-Type: application/json",
            "-w", "\n%{http_code}"]
    if body is not None:
        args += ["-d", json.dumps(body)]
    import time
    last_err = None
    for attempt in range(retries):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0:
            out = r.stdout.rsplit("\n", 1)
            try:
                http_code = int(out[-1])
            except ValueError:
                last_err = f"bad http code: {out[-1]!r}"
                time.sleep(2 ** attempt)
                continue
            payload_text = out[0]
            try:
                payload = json.loads(payload_text) if payload_text else None
            except json.JSONDecodeError:
                payload = payload_text
            return http_code, payload
        last_err = f"curl exit {r.returncode}: {r.stderr.strip()[:200]}"
        time.sleep(2 ** attempt)
    raise RuntimeError(f"curl failed after {retries} attempts: {last_err}")

def ensure_bucket(name: str, public=True):
    code, payload = curl_json("GET", f"{SUPABASE_URL}/storage/v1/bucket/{name}")
    if code == 200:
        return False
    not_found = code == 404 or (isinstance(payload, dict) and payload.get("error") == "Bucket not found")
    if not_found:
        code2, payload2 = curl_json("POST", f"{SUPABASE_URL}/storage/v1/bucket",
                                    {"id": name, "name": name, "public": public})
        if code2 not in (200, 201):
            raise RuntimeError(f"failed to create bucket {name}: code={code2} payload={payload2}")
        return True
    raise RuntimeError(f"unexpected GET bucket status {code}: {payload}")

def object_exists(bucket: str, path: str) -> bool:
    args = ["curl", "-sS", "--retry", "3", "--retry-delay", "2",
            "--connect-timeout", "10", "--max-time", "30",
            "-o", "/dev/null", "-w", "%{http_code}",
            "-I", f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}",
            "-H", f"Authorization: Bearer {SERVICE_KEY}"]
    import time
    for attempt in range(4):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip() == "200"
        time.sleep(2 ** attempt)
    return False  # treat unreachable as "not exists" so we attempt copy and let copy fail-loud

def storage_copy(src_bucket: str, src_path: str, dst_bucket: str, dst_path: str):
    """Server-side copy. Supabase v1 API."""
    body = {
        "bucketId": src_bucket,           # source bucket
        "sourceKey": src_path,
        "destinationBucket": dst_bucket,
        "destinationKey": dst_path,
    }
    code, payload = curl_json("POST", f"{SUPABASE_URL}/storage/v1/object/copy", body)
    return code, payload

def storage_list(bucket: str, prefix: str, limit=1000, offset=0):
    body = json.dumps({"prefix": prefix, "limit": limit, "offset": offset})
    result = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         f"{SUPABASE_URL}/storage/v1/object/list/{bucket}",
         "-H", f"Authorization: Bearer {SERVICE_KEY}",
         "-H", "Content-Type: application/json",
         "-d", body],
        capture_output=True, check=True, text=True,
    )
    return json.loads(result.stdout)

def walk_bucket(bucket: str, prefix=""):
    """Yield every file path under prefix (recursive BFS)."""
    queue = [prefix]
    while queue:
        p = queue.pop(0)
        offset = 0
        while True:
            items = storage_list(bucket, p, limit=1000, offset=offset)
            if not items:
                break
            for it in items:
                name = it["name"]
                full = f"{p}{name}" if p == "" or p.endswith("/") else f"{p}/{name}"
                if it.get("id") is None:  # folder marker
                    queue.append(full + "/")
                else:
                    yield full
            if len(items) < 1000:
                break
            offset += 1000

# ---------- Mapping rules ----------

GAME_ALIASES = {
    "marvel snap": "marvel-snap",
    "marvel-snap": "marvel-snap",
    "MarvelSnap": "marvel-snap",
    "MLBB": "mlbb",
    "mlbb": "mlbb",
    "Kekele": "kekele",
    "kekele": "kekele",
    "Oxide": "oxide",
    "oxide": "oxide",
    "roblox": "roblox",
    "star-trek-timelines": "star-trek-timelines",
}

# Top-level dirs in `assets` that aren't games but should funnel into a game
ORPHAN_ROOTS = {
    "motion-dance-bts": ("roblox", "_unsorted/motion-dance-bts"),
    "motion-dance-test": ("roblox", "_unsorted/motion-dance-test"),
    "motion-dance-tpol": ("roblox", "_unsorted/motion-dance-tpol"),
    "motion-test": ("roblox", "_unsorted/motion-test"),
}

# Known characters that contain a hyphen — used to peel variant suffix.
# Order matters: longer prefix first.
MULTIWORD_CHARS = [
    "uhura-kelvin", "jadzia-dax", "carol-marcus",
    "michael-burnham", "seven-of-nine",
    "annika-hansen",
    "jake-news", "sarah-news", "chad-news",
    "bacon-bob", "bacon-hair", "chad-sigma", "y2k-girl", "y2k-blonde",
    "rich-player", "parkour-girl", "preppy-girl",
    "king-rex",
    "captain-america",
]

# Canonical character slugs: anything in `aliases` maps to `canonical`.
CHARACTER_CANONICAL = [
    ("kirk",         ["captain-kirk", "kirk"]),
    ("picard",       ["captain-picard", "picard"]),
    ("janeway",      ["captain-janeway", "janeway"]),
    ("worf",         ["commander-worf", "worf"]),
    ("data",         ["commander-data", "data"]),
    ("annika",       ["child-annika", "annika", "annika-hansen"]),
    ("captain-america", ["captain-america-ref", "captain-america-cosmic", "captain-america"]),
]
# Build flat alias → canonical map
ALIAS_TO_CANONICAL = {}
for canon, aliases in CHARACTER_CANONICAL:
    for a in aliases:
        ALIAS_TO_CANONICAL[a] = canon

# Tokens that, when sitting at the end of a stem, are variants (not character names).
KNOWN_VARIANTS = {
    "young", "mature", "cadet", "child", "adult", "borg", "borg-drone",
    "canonical", "initiate", "prophet", "old", "new", "kelvin",
    "captain", "boy", "girl", "pixar", "pixar-3d", "cosmic",
    "v2", "v3", "v4", "v5",
}

DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
SCENE_RE = re.compile(r"^scene-(\d+)(?:-(end|start))?(?:-v\d+)?\.(png|jpg|jpeg)$", re.I)
EP_SCENE_RE = re.compile(r"^ep(\d+)-scene-(\d+).*\.(png|jpg)$", re.I)

# ---------- Filename classifiers ----------

def slug_from_avatar(name: str):
    # kirk-avatar-ref.png -> kirk
    # chad-news-avatar-ref.png -> chad-news
    # captain-america-cosmic.png -> captain-america-cosmic (no -avatar suffix; treat full)
    # q-avatar.png -> q
    m = re.match(r"^(.+?)(?:-avatar(?:-ref)?)?\.(png|jpg|jpeg)$", name, re.I)
    if not m:
        return None
    base = m.group(1)
    return base

def canonicalize(slug: str) -> str:
    """Map an alias to its canonical character slug."""
    return ALIAS_TO_CANONICAL.get(slug, slug)

# Noise tokens that show up inside slugs but aren't part of the character name
# (e.g. "uhura-character-ref" → the middle "character" is filler).
NOISE_TOKENS = {"character", "ref", "the", "a", "an"}

def strip_noise(parts):
    return [p for p in parts if p not in NOISE_TOKENS]

def parse_character_variant(stem: str):
    """
    Returns (canonical_character_slug or None, variant_or_None).
    Returns (None, None) when the stem is pure noise (e.g. "character").
    """
    s = stem
    s = DATE_RE.sub("", s).strip("-")
    s = re.sub(r"-ref(-v\d+)?$", "", s)
    version = None
    m = re.search(r"-v(\d+)$", s)
    if m:
        version = "v" + m.group(1)
        s = s[: m.start()]

    # MULTIWORD_CHARS prefix match BEFORE noise-stripping (in case multi-word includes "character")
    for ch in MULTIWORD_CHARS:
        if s == ch:
            return canonicalize(ch), version
        if s.startswith(ch + "-"):
            rest = s[len(ch) + 1:]
            return canonicalize(ch), rest if rest else version

    parts = s.split("-")
    parts = strip_noise(parts)
    if not parts:
        return None, version  # signal "no real name"

    # Peel KNOWN_VARIANTS tokens off the tail iteratively
    peeled = []
    while len(parts) > 1 and parts[-1] in KNOWN_VARIANTS:
        peeled.insert(0, parts.pop())
    if version:
        peeled.append(version)
    if peeled:
        return canonicalize("-".join(parts)), "-".join(peeled)
    return canonicalize("-".join(parts)), version

def classify_refs_file(game: str, filename: str):
    """
    Map a file under assets/{game}/refs/{filename} to (new_bucket, new_path, rule, confidence, notes).
    """
    name = filename
    lower = name.lower()
    stem, _, ext = name.rpartition(".")
    if not ext:
        return ("assets", f"{game}/_unsorted/{name}", "no-extension", "low", "no extension")
    ext = ext.lower()

    # 1. video (cta, opener, title-card)
    if ext in ("mp4", "mov"):
        bn = lower
        # rename: news-cta.mp4 -> branding/news-cta.mp4
        return ("assets", f"{game}/branding/{name}", "branding-video", "high", "")

    # 2. bg-*.{png,jpg}
    if re.match(r"^bg-", lower):
        loc_name = re.sub(r"^bg-", "", name)
        # strip trailing date / -v2 / etc to canonicalize
        return ("assets", f"{game}/locations/{loc_name}", "location-bg", "high", "")

    # 3. opener/title-card stills
    if re.match(r"^(opener|news-title-card|.*-title-card)", lower):
        return ("assets", f"{game}/branding/{name}", "branding-still", "high", "")

    # 4. ep{N}-bg-ref-{loc}.png
    m = re.match(r"^ep(\d+)-bg-ref-(.+)$", lower)
    if m:
        ep, rest = m.group(1), m.group(2)
        return ("episodes", f"{game}/ep{ep}-unknown-date/refs/bg-{rest}", "episode-bg-ref", "medium", f"ep{ep}, format unknown")

    # 5. ep{N}-character-ref-{name}.png
    m = re.match(r"^ep(\d+)-character-ref-(.+?)\.(png|jpg)$", lower)
    if m:
        ep, charname = m.group(1), m.group(2)
        return ("episodes", f"{game}/ep{ep}-unknown-date/refs/character-ref-{charname}.{m.group(3)}", "episode-character-ref", "medium", f"ep{ep} duplicate of base character")

    # 6. ep{N}-scene-K.png
    m = EP_SCENE_RE.match(name)
    if m:
        ep, sc, ext2 = m.group(1), m.group(2), m.group(3)
        return ("episodes", f"{game}/ep{ep}-unknown-date/scenes/scene-{sc}.{ext2}", "episode-scene", "medium", f"ep{ep}")

    # 7. scene-K{-end|-start|-v2|-{char}-{date}}.png
    m = re.match(r"^scene-(\d+)(.*)\.(png|jpg)$", name)
    if m:
        sc, tail, ext2 = m.group(1), m.group(2), m.group(3)
        # extract date from tail if any
        d = DATE_RE.search(tail)
        date_part = d.group(1) if d else "unknown-date"
        # extract character name if any
        # tail like "-end" or "-jadzia-dax-2026-05-24" or "-v2"
        clean_tail = DATE_RE.sub("", tail).strip("-").strip()
        # heuristic format guess from character → character-story
        format_guess = "character-story" if clean_tail and clean_tail not in ("end", "start") and not clean_tail.startswith("v") else "unknown-format"
        suffix = ""
        if clean_tail in ("end", "start"):
            suffix = f"-{clean_tail}"
        episode_dir = f"{date_part}-{format_guess}"
        return ("episodes", f"{game}/{episode_dir}/scenes/scene-{sc}{suffix}.{ext2}", "scene-in-refs", "medium", f"orig tail '{tail}', clean '{clean_tail}'")

    # 8. {something}-avatar-ref.png  or  {something}-avatar.png
    if re.search(r"-avatar(-ref)?\.(png|jpg)$", lower):
        slug = slug_from_avatar(name)
        return ("assets", f"{game}/characters/{slug}/avatar.{ext}", "character-avatar", "high", "")

    # 9. {character}-sheet.png
    m = re.match(r"^(.+)-sheet\.(png|jpg)$", lower)
    if m:
        ch_raw = m.group(1)
        ch, var = parse_character_variant(ch_raw)
        if not ch:
            return ("assets", f"{game}/_unsorted/{name}", "sheet-no-character", "low", "stem was pure noise")
        if var:
            return ("assets", f"{game}/characters/{ch}/variants/{var}.{ext}", "character-sheet-variant", "high", f"sheet, variant={var}")
        return ("assets", f"{game}/characters/{ch}/sheet.{ext}", "character-sheet", "high", "")

    # 10. character-ref-{name}.png  → characters/{name}/sheet.png
    m = re.match(r"^character-ref-(.+?)\.(png|jpg)$", lower)
    if m:
        ch, var = parse_character_variant(m.group(1))
        if not ch:
            return ("assets", f"{game}/_unsorted/{name}", "character-ref-no-name", "low", "")
        if var:
            return ("assets", f"{game}/characters/{ch}/variants/{var}.{ext}", "character-ref-variant", "high", f"variant={var}")
        return ("assets", f"{game}/characters/{ch}/sheet.{ext}", "character-ref", "high", "")

    # 11. {character}-{variant}-ref(-DATE).png  or  {character}-{variant}-ref-v2.png
    m = re.match(r"^(.+?)-ref(-v\d+)?(-\d{4}-\d{2}-\d{2})?\.(png|jpg)$", lower)
    if m:
        base = m.group(1)
        ch, var = parse_character_variant(base)
        if not ch:
            return ("assets", f"{game}/_unsorted/{name}", "bare-ref-no-character", "low", "stem was pure noise")
        if var:
            return ("assets", f"{game}/characters/{ch}/variants/{var}.{ext}", "character-variant-ref", "high", f"variant={var}")
        return ("assets", f"{game}/characters/{ch}/sheet.{ext}", "character-bare-ref", "medium", "no variant")

    # 12. ref-frame-* / ref-{ambiguous} → _unsorted
    if re.match(r"^ref-frame-", lower):
        return ("assets", f"{game}/_unsorted/{name}", "ref-frame-unsorted", "high", "composition ref, not a character")

    # 12b. ref-{character}(-v\d+)?.{ext}  e.g. ref-king-rex-v3
    if re.match(r"^ref-", lower):
        m = re.match(r"^ref-(.+?)(-v\d+)?\.(png|jpg)$", lower)
        if m:
            base = m.group(1)
            ver = m.group(2)  # "-v3" or None
            ch, var = parse_character_variant(base)
            if not ch:
                return ("assets", f"{game}/_unsorted/{name}", "ref-prefix-no-character", "low", "")
            if ver:
                ver = ver.lstrip("-")  # "v3"
                # combine with any variant peeled by parser
                full_var = f"{var}-{ver}" if var else ver
                return ("assets", f"{game}/characters/{ch}/variants/{full_var}.{ext}", "ref-prefix-version", "high", f"variant={full_var}")
            if var:
                return ("assets", f"{game}/characters/{ch}/variants/{var}.{ext}", "ref-prefix-variant", "medium", "")
            return ("assets", f"{game}/characters/{ch}/sheet.{ext}", "ref-prefix-sheet", "low", "ambiguous")
        return ("assets", f"{game}/_unsorted/{name}", "ref-prefix-unknown", "low", "")

    # 13. _identity-*.jpg
    if name.startswith("_identity-"):
        slug = re.sub(r"^_identity-", "", stem)
        return ("assets", f"{game}/characters/{slug}/identity.{ext}", "identity-prefix", "medium", "")

    # 14. spock-on-location-vulcan-academy.png  → it's a character-in-location combo (1 file)
    if "-on-location-" in lower:
        return ("assets", f"{game}/_unsorted/{name}", "character-on-location", "low", "manual decision needed")

    # 15. seven-on-location-riker-chair.png
    if re.match(r"^seven-on-", lower):
        return ("assets", f"{game}/_unsorted/{name}", "character-on-location", "low", "manual decision needed")

    # 16. catch-all character variant from filename (no -ref/-sheet suffix)
    # e.g. archer-mature-2026-05-27.png handled here
    # Tokens that should bail out — clearly not a character
    if stem in {"character"} or re.match(r"^scene-", lower):
        return ("assets", f"{game}/_unsorted/{name}", "ambiguous-name", "high", "not a character (literal 'character.png' or stray scene)")

    base = re.sub(r"-v\d+$", "", stem)
    base = DATE_RE.sub("", base).strip("-")
    ch, var = parse_character_variant(base)
    if var:
        return ("assets", f"{game}/characters/{ch}/variants/{var}.{ext}", "fallback-variant", "low", f"guessed variant={var}")
    if ch:
        return ("assets", f"{game}/characters/{ch}/sheet.{ext}", "fallback-character", "low", "no variant detected")

    return ("assets", f"{game}/_unsorted/{name}", "unknown", "low", "no rule matched")

def classify_tts_file(game: str, filename: str, parent_format=None):
    """Map an assets/{game}/tts/{filename} to episodes bucket."""
    name = filename
    lower = name.lower()
    d = DATE_RE.search(lower)
    date_part = d.group(1) if d else "unknown-date"
    # format guess from filename keywords
    fmt = parent_format
    if not fmt:
        for keyword in ("character-story", "redcon", "what-if-lore", "top-list", "fun-news",
                        "serial-drama", "comedy-sketch", "gameplay-avatar", "news",
                        "motion-dance", "reddit-story"):
            if keyword in lower:
                fmt = keyword
                break
    fmt = fmt or "unknown-format"
    return ("episodes", f"{game}/{date_part}-{fmt}/tts/{name}", "tts", "medium", f"date={date_part} fmt={fmt}")

def classify_gameplay_file(game: str, filename: str):
    # Normalize: lowercase, replace spaces and underscores with hyphens
    normalized = re.sub(r"[\s_]+", "-", filename).lower()
    note = "" if normalized == filename else f"renamed from '{filename}'"
    return ("assets", f"{game}/gameplay/{normalized}", "gameplay-keep", "high", note)

def classify_avatar_file(game: str, filename: str):
    if "." not in filename:
        return ("assets", f"{game}/_unsorted/{filename}", "avatar-unknown", "low", "")
    stem, ext = filename.rsplit(".", 1)
    ext = ext.lower()
    # Strip -avatar(-ref)? if present
    stem2 = re.sub(r"-avatar(-ref)?$", "", stem)
    ch, var = parse_character_variant(stem2)
    if not ch:
        return ("assets", f"{game}/_unsorted/{filename}", "avatar-unparsed", "low", "")
    if var:
        return ("assets", f"{game}/characters/{ch}/avatar-{var}.{ext}", "avatar-variant", "high", f"variant={var}")
    return ("assets", f"{game}/characters/{ch}/avatar.{ext}", "avatar-folder", "high", "")

# ---------- Top-level path router ----------

def route(old_bucket: str, old_path: str):
    """Return (new_bucket, new_path, rule, confidence, notes) for one old path."""
    parts = old_path.split("/")
    p0 = parts[0]

    # 0. ignore _tmp/
    if p0 == "_tmp":
        return ("_skip", "", "tmp-skip", "high", "ignore temp")

    # 1. shared/ - keep as is (multi-game)
    if p0 == "shared":
        return ("assets", old_path, "shared-keep", "high", "multi-game shared")

    # 2. nested 'assets/...' inside assets bucket (legacy bug)
    if p0 == "assets":
        inner = "/".join(parts[1:])
        nb, np_, rule, conf, note = route(old_bucket, inner)
        return (nb, np_, "denest+" + rule, conf, "stripped nested 'assets/' prefix; " + note)

    # 3. nested 'videos/...' inside assets bucket → videos bucket
    if p0 == "videos":
        return ("videos", "/".join(parts[1:]), "denest-videos", "high", "cross-bucket: assets/videos → videos")

    # 4. nested 'tts/{game}/...' inside assets bucket
    if p0 == "tts":
        if len(parts) >= 3:
            game = GAME_ALIASES.get(parts[1], parts[1])
            inner = "/".join(parts[2:])
            return classify_tts_file(game, inner.split("/")[-1])
        return ("episodes", f"unknown-game/unknown-date-unknown-format/tts/{'/'.join(parts[1:])}", "orphan-tts", "low", "")

    # 5. nested 'music/{file}' inside assets bucket
    if p0 == "music":
        return ("music", "/".join(parts[1:]), "denest-music", "medium", "cross-bucket: assets/music → music; mood unknown")

    # 6. orphan top-level format dirs that funnel to a game
    if p0 in ORPHAN_ROOTS:
        game, prefix = ORPHAN_ROOTS[p0]
        inner = "/".join(parts[1:])
        return ("assets", f"{game}/{prefix}/{inner}", "orphan-funnel", "low", f"funneled '{p0}' → {game}/{prefix}")

    # 7. game-prefixed paths
    if p0 in GAME_ALIASES:
        game = GAME_ALIASES[p0]
        if len(parts) < 2:
            return ("assets", old_path, "game-root", "low", "")
        sub = parts[1]
        rest = parts[2:]
        return route_inside_game(game, sub, rest, old_path)

    # 8. unknown top-level
    return ("assets", f"_unsorted/{old_path}", "unknown-toplevel", "low", "")

def route_inside_game(game: str, sub: str, rest, old_path):
    """Route a path of shape assets/{game}/{sub}/{rest...}."""
    filename = rest[-1] if rest else sub
    deep = "/".join(rest)

    # 0. Top-level file inside game folder (no subfolder) — sub IS the filename
    if not rest and "." in sub:
        # {game}/{file}
        ext = sub.rsplit(".", 1)[-1].lower()
        if ext in ("mp4", "mov"):
            return ("assets", f"{game}/branding/{sub}", "toplevel-branding-video", "high", "top-level mp4 inside game")
        if ext in ("png", "jpg", "jpeg"):
            return ("assets", f"{game}/branding/{sub}", "toplevel-branding-image", "medium", "top-level image inside game")
        return ("assets", f"{game}/_unsorted/{sub}", "toplevel-misc", "low", "top-level non-media")

    # Standard subfolders
    if sub == "refs":
        if len(rest) == 0:
            return ("assets", f"{game}/_unsorted/refs", "refs-empty", "low", "")
        if len(rest) == 1:
            return classify_refs_file(game, rest[0])
        # nested e.g. ep6/...
        # path like refs/ep6/something.png → episode-specific
        if rest[0].startswith("ep"):
            return ("episodes", f"{game}/{rest[0]}-unknown-date/refs/{'/'.join(rest[1:])}", "refs-nested-ep", "medium", "")
        return ("assets", f"{game}/_unsorted/refs/{deep}", "refs-nested-unknown", "low", "")

    if sub == "bg-refs":
        # bg-refs/{date}/{file} or bg-refs/{file}
        fname = rest[-1]
        loc_name = re.sub(r"^bg-", "", fname)
        return ("assets", f"{game}/locations/{loc_name}", "bg-refs-folder", "high", f"original folder: bg-refs/{'/'.join(rest[:-1])}/")

    if sub == "avatars":
        if len(rest) == 1:
            return classify_avatar_file(game, rest[0])
        return ("assets", f"{game}/_unsorted/avatars/{deep}", "avatars-nested", "low", "")

    if sub == "gameplay":
        if len(rest) == 1:
            return classify_gameplay_file(game, rest[0])
        return ("assets", f"{game}/gameplay/{deep}", "gameplay-nested", "medium", "")

    if sub == "tts":
        # path like tts/{file} or tts/ep2/clip-N.mp3
        if len(rest) == 1:
            return classify_tts_file(game, rest[0])
        if rest[0].startswith("ep") and len(rest) >= 2:
            return ("episodes", f"{game}/{rest[0]}-unknown-date/tts/{rest[-1]}", "tts-ep-nested", "medium", "")
        return ("episodes", f"{game}/unknown-date-unknown-format/tts/{deep}", "tts-deep-nested", "low", "")

    if sub == "scenes":
        # scenes/{date}/{format}/{file}  OR scenes/{name-cs}/{file}  OR scenes/{file}
        if len(rest) == 1:
            fname = rest[0]
            # {char}-cs-scene-K(-end)?.png — character story for {char}, no date
            m_cs = re.match(r"^(.+?)-cs-scene-(\d+)(-end|-start)?\.(png|jpg|jpeg|mp4)$", fname.lower())
            if m_cs:
                char_slug = canonicalize(m_cs.group(1))
                sc = m_cs.group(2)
                suffix = m_cs.group(3) or ""
                ext_ = m_cs.group(4)
                return ("episodes", f"{game}/unknown-date-character-story/{char_slug}/scenes/scene-{sc}{suffix}.{ext_}",
                        "scenes-cs-prefix", "high", f"char={char_slug}")
            m = SCENE_RE.match(fname)
            if m:
                return ("episodes", f"{game}/unknown-date-unknown-format/scenes/{fname}", "scenes-bare", "low", "")
            return ("episodes", f"{game}/unknown-date-unknown-format/scenes/{fname}", "scenes-bare-misc", "low", "")
        if DATE_RE.match(rest[0]):
            # scenes/{date}/{format}/{file}
            date = rest[0]
            if len(rest) >= 3:
                fmt = rest[1]
                fname = rest[-1]
                # subdir under format e.g. scene-1/
                middle = "/".join(rest[2:-1])
                middle_part = f"/{middle}" if middle else ""
                return ("episodes", f"{game}/{date}-{fmt}/scenes{middle_part}/{fname}", "scenes-date-format", "high", "")
            return ("episodes", f"{game}/{date}-unknown-format/scenes/{rest[-1]}", "scenes-date-only", "medium", "")
        # named subdir like worf-cs, spock-cs, character-story-2026-05-06, ep1
        first = rest[0]
        d = DATE_RE.search(first)
        date_part = d.group(1) if d else "unknown-date"
        fmt_guess = "character-story" if "-cs" in first or "character-story" in first else "unknown-format"
        char_in_name = re.sub(r"(-cs|-character-story)(-\d{4}-\d{2}-\d{2})?$", "", first)
        fname = rest[-1]
        # bg-* files inside scenes/{epN-or-named}/ are location refs for that episode
        if re.match(r"^bg-", fname.lower()) and fname.lower().endswith((".png", ".jpg", ".jpeg")):
            return ("episodes", f"{game}/{date_part}-{fmt_guess}/{char_in_name}/refs/{fname}",
                    "scenes-named-bg-ref", "medium", f"bg-ref inside scenes/{first}/")
        # ep{N} dirs — distinct namespace to avoid collisions with worf-cs etc
        if re.match(r"^ep\d+", first):
            return ("episodes", f"{game}/{first}-unknown-date/scenes/{fname}", "scenes-ep-dir", "high", "")
        return ("episodes", f"{game}/{date_part}-{fmt_guess}/{char_in_name}/scenes/{fname}", "scenes-named", "medium", f"original dir '{first}'")

    if sub == "videos":
        # cross-bucket
        return ("videos", f"{game}/{deep}", "game-videos-cross", "high", "")

    if sub == "music":
        return ("music", f"unknown-mood/{deep}", "game-music-cross", "low", "mood unknown")

    if sub == "episodes":
        # roblox/episodes/{file} — looks like a finished video uploaded under wrong path
        return ("videos", f"{game}/unknown-date/{deep}", "game-episodes-cross", "medium", "looks like final mp4")

    if sub == "branding":
        return ("assets", f"{game}/branding/{deep}", "already-branding", "high", "already in target shape")

    if sub == "characters" or sub == "locations":
        return ("assets", f"{game}/{sub}/{deep}", "already-target", "high", "already in target shape")

    # Episode-named top-level dirs inside a game: ep1-en, ep2, ep2-en, ep3-en, ep3, character-story-2026-05-07, comedy-sketch, motion-dance
    if re.match(r"^ep\d+", sub):
        # ep1-en/scene-1/file.png  → episodes/{game}/{sub}/scenes/scene-1/file.png
        if rest and rest[0].startswith("scene-"):
            return ("episodes", f"{game}/{sub}-unknown-date/scenes/{deep}", "episode-dir-scene", "medium", f"original {sub}/")
        if rest and rest[0] == "refs":
            return ("episodes", f"{game}/{sub}-unknown-date/refs/{'/'.join(rest[1:])}", "episode-dir-refs", "medium", "")
        if rest and rest[0] == "tts":
            return ("episodes", f"{game}/{sub}-unknown-date/tts/{'/'.join(rest[1:])}", "episode-dir-tts", "medium", "")
        if rest and rest[0] == "scenes":
            return ("episodes", f"{game}/{sub}-unknown-date/scenes/{'/'.join(rest[1:])}", "episode-dir-scenes", "medium", "")
        # bare files in ep{N}/ — classify by name
        if rest and len(rest) == 1:
            fname = rest[0]
            lower = fname.lower()
            if lower.startswith("tts-") and lower.endswith(".mp3"):
                return ("episodes", f"{game}/{sub}-unknown-date/tts/{fname}", "episode-dir-tts-bare", "medium", "")
            if lower.startswith("scene-") and lower.endswith((".png", ".jpg", ".mp4")):
                return ("episodes", f"{game}/{sub}-unknown-date/scenes/{fname}", "episode-dir-scene-bare", "medium", "")
        return ("episodes", f"{game}/{sub}-unknown-date/{deep}", "episode-dir-bare", "low", "")

    if sub.startswith("character-story"):
        d = DATE_RE.search(sub)
        date = d.group(1) if d else "unknown-date"
        return ("episodes", f"{game}/{date}-character-story/{deep}", "character-story-dir", "medium", f"original {sub}")

    if sub == "comedy-sketch":
        if rest and DATE_RE.match(rest[0]):
            date = rest[0]
            return ("episodes", f"{game}/{date}-comedy-sketch/{'/'.join(rest[1:])}", "comedy-sketch-date", "high", "")
        return ("episodes", f"{game}/unknown-date-comedy-sketch/{deep}", "comedy-sketch", "medium", "")

    if sub == "motion-dance":
        if rest and DATE_RE.match(rest[0]):
            date = rest[0]
            return ("episodes", f"{game}/{date}-motion-dance/{'/'.join(rest[1:])}", "motion-dance-date", "high", "")
        return ("episodes", f"{game}/unknown-date-motion-dance/{deep}", "motion-dance", "medium", "")

    # Unknown subdir
    return ("assets", f"{game}/_unsorted/{sub}/{deep}", "unknown-subdir", "low", f"subdir '{sub}' not recognized")

# ---------- Main ----------

def resolve_collisions(rows):
    """For destinations targeted by >1 source, append `-c2`, `-c3` etc. to all but the first.
    Skips `_skip` and `_unsorted/` paths.
    Returns (new_rows, collisions_list).
    """
    from collections import defaultdict
    seen = defaultdict(list)  # dest_key → list of row indices
    for i, r in enumerate(rows):
        nb, np_ = r[2], r[3]
        if nb == "_skip":
            continue
        seen[f"{nb}::{np_}"].append(i)

    collisions = []
    for key, idxs in seen.items():
        if len(idxs) > 1:
            # Keep first as-is; rename others
            for n, i in enumerate(idxs):
                if n == 0:
                    note = rows[i][6] + (" | first-of-collision" if rows[i][6] else "first-of-collision")
                    rows[i] = rows[i][:6] + (note,)
                    continue
                old_bucket, old_path, new_bucket, new_path, rule, conf, notes = rows[i]
                # split into dir + name.ext
                if "." in new_path.rsplit("/", 1)[-1]:
                    base, _, ext = new_path.rpartition(".")
                    new_path2 = f"{base}-c{n+1}.{ext}"
                else:
                    new_path2 = f"{new_path}-c{n+1}"
                new_notes = (notes + " | " if notes else "") + f"COLLISION (n={n+1}/{len(idxs)}); renamed from {new_path}"
                rows[i] = (old_bucket, old_path, new_bucket, new_path2, rule, conf, new_notes)
                collisions.append((key, len(idxs), old_path, new_path2))
    return rows, collisions

def main():
    rows = []
    for bucket in SOURCE_BUCKETS:
        print(f"[walk] bucket={bucket}", file=sys.stderr)
        count = 0
        for path in walk_bucket(bucket):
            count += 1
            nb, np_, rule, conf, note = route(bucket, path)
            rows.append((bucket, path, nb, np_, rule, conf, note))
        print(f"[walk] bucket={bucket} files={count}", file=sys.stderr)

    rows, collisions = resolve_collisions(rows)

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_TSV, "w") as f:
        f.write("old_bucket\told_path\tnew_bucket\tnew_path\trule\tconfidence\tnotes\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    # Collisions report
    coll_tsv = OUT_TSV.parent / "migration-plan-collisions.tsv"
    with open(coll_tsv, "w") as f:
        f.write("dest_key\tnum_sources\trenamed_source\trenamed_dest\n")
        for c in collisions:
            f.write("\t".join(str(x) for x in c) + "\n")

    # Summary
    from collections import Counter
    by_conf = Counter(r[5] for r in rows)
    by_rule = Counter(r[4] for r in rows)
    by_target_bucket = Counter(r[2] for r in rows)
    print(f"\n[summary] total rows: {len(rows)}", file=sys.stderr)
    print(f"[summary] by confidence: {dict(by_conf)}", file=sys.stderr)
    print(f"[summary] by target bucket: {dict(by_target_bucket)}", file=sys.stderr)
    print(f"[summary] collisions: {len(collisions)} renames across {len({c[0] for c in collisions})} dest paths", file=sys.stderr)
    print(f"[summary] by rule (top 30):", file=sys.stderr)
    for rule, n in by_rule.most_common(30):
        print(f"    {rule:30} {n}", file=sys.stderr)
    print(f"\n[output] plan:       {OUT_TSV}", file=sys.stderr)
    print(f"[output] collisions: {coll_tsv}", file=sys.stderr)

    if not DRY_RUN:
        apply_plan(rows)

def apply_plan(rows):
    # Filter
    if FILTER_PREFIX:
        rows = [r for r in rows if r[1].startswith(FILTER_PREFIX)]
        print(f"[apply] filter={FILTER_PREFIX!r} → {len(rows)} rows", file=sys.stderr)

    # Skip _skip rows
    rows = [r for r in rows if r[2] != "_skip"]
    print(f"[apply] will copy {len(rows)} files", file=sys.stderr)

    # Ensure target buckets exist
    target_buckets = sorted({r[2] for r in rows})
    for b in target_buckets:
        created = ensure_bucket(b, public=True)
        print(f"[bucket] {b}: {'created' if created else 'ok'}", file=sys.stderr)

    APPLY_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_f = open(APPLY_LOG, "a")
    import datetime
    log_f.write(f"\n=== apply run {datetime.datetime.now().isoformat()} filter={FILTER_PREFIX!r} ===\n")

    stats = {"OK": 0, "SKIP_EXISTS": 0, "FAIL": 0}
    for i, (sb, sp, db, dp, rule, conf, notes) in enumerate(rows, 1):
        if object_exists(db, dp):
            stats["SKIP_EXISTS"] += 1
            log_f.write(f"SKIP_EXISTS\t{sb}/{sp}\t→\t{db}/{dp}\n")
            print(f"[{i}/{len(rows)}] SKIP {sp} (dest exists)", file=sys.stderr)
            continue
        code, payload = storage_copy(sb, sp, db, dp)
        if code in (200, 201):
            stats["OK"] += 1
            log_f.write(f"OK\t{sb}/{sp}\t→\t{db}/{dp}\n")
            print(f"[{i}/{len(rows)}] OK   {sp}", file=sys.stderr)
        else:
            stats["FAIL"] += 1
            log_f.write(f"FAIL\t{code}\t{sb}/{sp}\t→\t{db}/{dp}\t{payload}\n")
            print(f"[{i}/{len(rows)}] FAIL code={code} {sp}: {payload}", file=sys.stderr)

    log_f.write(f"=== summary: {stats} ===\n")
    log_f.close()
    print(f"\n[apply] done: {stats}", file=sys.stderr)
    print(f"[apply] log:  {APPLY_LOG}", file=sys.stderr)

if __name__ == "__main__":
    main()
