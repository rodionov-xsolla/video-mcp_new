#!/usr/bin/env python3
"""Growtopia NPC sprite/portrait parser.

Pulls NPC portraits from the Growtopia Fandom wiki via the MediaWiki API
(no HTML scraping) and saves them locally as reference images.

Source category: https://growtopia.fandom.com/wiki/Category:NPCs

Usage:
    python3 tools/growtopia_parser.py --dry-run             # list NPCs, download nothing
    python3 tools/growtopia_parser.py --limit 1             # test: first NPC only
    python3 tools/growtopia_parser.py --preprocess          # full run + NB2-ready PNGs
    python3 tools/growtopia_parser.py --out /abs/dir        # custom output dir

With --preprocess, each raw sprite (refs/{slug}.*) also yields a single-frame,
nearest-neighbor-upscaled PNG in refs/nb2/{slug}.png ready to feed to NB2.

Local only — does NOT upload to Supabase. A manifest (npcs.json) is written
alongside the images as a ready-made map for a future upload step.
"""

import argparse
import hashlib
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

# python.org builds on macOS often ship without a CA bundle; prefer certifi.
try:
    import certifi

    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = ssl.create_default_context()

API = "https://growtopia.fandom.com/api.php"
CATEGORY = "Category:NPCs"
UA = "growtopia-video-pipeline/1.0 (asset reference parser; contact: k.nazarov@xsolla.com)"
DELAY = 0.3  # seconds between API calls — be polite to the wiki

# Known non-sprite wiki template/maintenance images (md5). When a page has no real
# character sprite, pageimages returns one of these — treat as "no image".
JUNK_HASHES = {
    "79c76f06a9507b0dd85aeb7d905af949",  # "REPORT" maintenance banner
}

DEFAULT_OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "games", "growtopia", "assets", "refs"
)


def api_get(params):
    """One MediaWiki API request → parsed JSON."""
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        return json.loads(resp.read().decode("utf-8"))


def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "npc"


def list_npcs():
    """All article-namespace (ns=0) members of Category:NPCs, in wiki order."""
    npcs, cmcontinue = [], None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": CATEGORY,
            "cmlimit": "500",
            "cmnamespace": "0",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue
        data = api_get(params)
        # Skip system/pseudo entities (e.g. "@System") — not real character NPCs.
        npcs.extend(
            m["title"] for m in data["query"]["categorymembers"] if not m["title"].startswith("@")
        )
        cont = data.get("continue")
        if not cont:
            break
        cmcontinue = cont["cmcontinue"]
        time.sleep(DELAY)
    return npcs


def file_url(file_title):
    """Resolve a File: page to its direct image URL."""
    info = api_get({"action": "query", "titles": file_title, "prop": "imageinfo", "iiprop": "url"})
    page = next(iter(info["query"]["pages"].values()))
    infos = page.get("imageinfo")
    return infos[0]["url"] if infos else None


def growsprite_url(title):
    """The canonical in-game sprite for a Growtopia NPC/item page.

    Most pages render the sprite as a window-crop of a shared atlas
    (ItemSprites.png) inside <span class="growsprite"><img src=...>. That crop URL
    returns exactly the NPC's pixel sprite — the right reference for a pixel-art
    title, unlike the promo renders/screenshots that pageimages tends to pick.
    """
    data = api_get({"action": "parse", "page": title, "prop": "text"})
    body = data.get("parse", {}).get("text", {}).get("*")
    if not body:
        return None, None

    def norm(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())

    want = norm(title)
    sprites = list(re.finditer(r'class="growsprite">\s*<img[^>]*\bsrc="([^"]+)"', body))
    if not sprites:
        return None, None

    # Pick the growsprite whose nearest preceding card headline matches this NPC;
    # decorative growsprites elsewhere on the page have no matching headline.
    matched, in_card = None, None
    for m in sprites:
        pre = body[: m.start()]
        hid = re.findall(r'mw-headline"\s+id="([^"]+)"', pre)
        if hid and norm(hid[-1]) == want and matched is None:
            matched = m
        if "card-header" in pre[-400:] and in_card is None:
            in_card = m
    pick = matched or in_card
    if not pick:
        return None, None
    return html.unescape(pick.group(1)), "atlas-crop"


def main_image(title):
    """Sprite URL for an NPC page.

    Priority: the canonical atlas sprite (growsprite), then a standalone file named
    "*Sprite*", then a file matching the NPC title, then the lead image, then the
    first image on the page. The wiki's "lead image" (pageimages) is often a promo
    render or gameplay screenshot, so it is a last resort.
    """
    gs, tag = growsprite_url(title)
    if gs:
        return gs, tag

    # No canonical atlas sprite. Only accept a standalone file explicitly named as a
    # sprite — anything else on these pages (UI dialogs, posters, gameplay shots,
    # user photos) is junk for a pixel-art reference, so we return nothing instead.
    imgs = api_get({"action": "query", "titles": title, "prop": "images", "imlimit": "50"})
    page = next(iter(imgs["query"]["pages"].values()))
    sprite = next(
        (
            im["title"]
            for im in page.get("images", [])
            if "sprite" in im["title"].lower()
            and im["title"].lower().endswith((".png", ".webp", ".jpg", ".jpeg", ".gif"))
        ),
        None,
    )
    if sprite:
        url = file_url(sprite)
        if url:
            return url, sprite.replace("File:", "")
    return None, None


def sniff_ext(data, fallback=".png"):
    """Real image extension from magic bytes — Fandom serves WebP under .PNG names."""
    if data[:8].startswith(b"\x89PNG"):
        return ".png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    if data[:4] in (b"GIF8",):
        return ".gif"
    return fallback


def preprocess_sprite(src_path, out_dir, target=512):
    """Turn a raw sprite sheet into a single-frame, NB2-ready PNG.

    Sprite sheets are square frames laid out in a horizontal row, so frame count
    = width / height. Take the first (idle/front) frame and upscale it with
    nearest-neighbor so the hard pixel edges survive (bilinear would blur them).
    No vision, no model — pure arithmetic. Returns the written path.
    """
    from PIL import Image  # lazy: only needed when --preprocess is on

    im = Image.open(src_path).convert("RGBA")
    W, H = im.size
    n = W // H if (H and W > H and W % H == 0) else 1  # square frames in a row
    fw = W // n
    frame = im.crop((0, 0, fw, H))
    longest = max(frame.size)
    scale = max(1, target // longest)  # integer scale keeps pixels crisp
    big = frame.resize((frame.size[0] * scale, frame.size[1] * scale), Image.NEAREST)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, os.path.splitext(os.path.basename(src_path))[0] + ".png")
    big.save(out)
    return out, n, scale, big.size


def download(url, dest_base):
    """Fetch the image and save it with the extension matching its real format.
    dest_base is the path without extension; returns the actual written path."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp:
        data = resp.read()
    md5 = hashlib.md5(data).hexdigest()
    if md5 in JUNK_HASHES:
        return None, md5  # wiki template/placeholder, not a real sprite
    dest = dest_base + sniff_ext(data)
    with open(dest, "wb") as f:
        f.write(data)
    return dest, md5


def main():
    ap = argparse.ArgumentParser(description="Parse Growtopia NPC portraits from the Fandom wiki.")
    ap.add_argument("--limit", type=int, default=0, help="max NPCs to process (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="list NPCs, download nothing")
    ap.add_argument("--out", default=DEFAULT_OUT, help="output directory for images + manifest")
    ap.add_argument(
        "--preprocess",
        action="store_true",
        help="also emit NB2-ready PNGs (first frame, nearest-neighbor upscale) into out/nb2/",
    )
    ap.add_argument("--scale-target", type=int, default=512, help="target px for NB2 upscale")
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)

    print(f"[+] Fetching NPC list from {CATEGORY} ...", file=sys.stderr)
    npcs = list_npcs()
    if args.limit:
        npcs = npcs[: args.limit]
    print(f"[+] {len(npcs)} NPC(s) to process", file=sys.stderr)

    manifest_path = os.path.join(out, "npcs.json")
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = {e["name"]: e for e in json.load(f)}

    for i, name in enumerate(npcs, 1):
        slug = slugify(name)
        dest_base = os.path.join(out, slug)

        if args.dry_run:
            print(f"  {i}. {name}  ->  {slug}.*")
            continue

        if name in manifest and os.path.exists(os.path.join(out, manifest[name]["file"])):
            print(f"  {i}. {name}  (skip, already downloaded)", file=sys.stderr)
            continue

        try:
            url, wiki_file = main_image(name)
            time.sleep(DELAY)
            if not url:
                print(f"  {i}. {name}  ->  NO IMAGE FOUND", file=sys.stderr)
                continue
            dest, _ = download(url, dest_base)
            if not dest:
                print(f"  {i}. {name}  ->  SKIP (wiki placeholder, no real sprite)", file=sys.stderr)
                continue
            fname = os.path.basename(dest)
            entry = {
                "name": name,
                "slug": slug,
                "file": fname,
                "source_url": url,
                "wiki_page": "https://growtopia.fandom.com/wiki/" + urllib.parse.quote(name.replace(" ", "_")),
                "wiki_file": wiki_file,
            }
            size = os.path.getsize(dest)
            note = f"  {i}. {name}  ->  {fname}  ({size} bytes)"
            if args.preprocess:
                try:
                    nb2_path, n, scale, dims = preprocess_sprite(
                        dest, os.path.join(out, "nb2"), args.scale_target
                    )
                    entry["nb2_file"] = os.path.join("nb2", os.path.basename(nb2_path))
                    note += f"  | nb2: {os.path.basename(nb2_path)} ({dims[0]}x{dims[1]}, {n}f x{scale})"
                except Exception as e:
                    note += f"  | nb2 FAILED: {e}"
            manifest[name] = entry
            print(note, file=sys.stderr)
        except Exception as e:
            print(f"  {i}. {name}  ->  ERROR: {e}", file=sys.stderr)

    if not args.dry_run:
        with open(manifest_path, "w") as f:
            json.dump(list(manifest.values()), f, ensure_ascii=False, indent=2)
        print(f"[+] Manifest: {manifest_path} ({len(manifest)} entries)", file=sys.stderr)


if __name__ == "__main__":
    main()
