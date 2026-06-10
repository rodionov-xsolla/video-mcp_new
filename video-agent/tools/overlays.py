#!/usr/bin/env python3
"""
Генератор ОРИГИНАЛЬНЫХ графических оверлеев (НЕ субтитры).

Субтитры — это произнесённая речь, единый универсальный стиль, отдельный скрипт
(tools/add_subtitles.py). ЭТОТ скрипт рисует всё остальное «фирменное»:
название серии / title card, счётчик выживаемости (in-game POV), плашку исхода
(YOU DIED / YOU SURVIVED), номера топ-листа (#5..#1), имена позиций, слоган и
дисклеймер (fake-ad), и channel-bug (PNG-лого канала).

Контракт:
  • Спеки оверлеев лежат в storyboard.json: per-scene массив `overlays[]`
    (см. схему ниже) и опциональное top-level поле `channel_bug`.
  • Скрипт ЭМИТИТ filter_complex-фрагмент (drawtext-цепочку) на сцену — его
    editor вплетает в `[vk]`-ветку ДО concat (single-pass §0, без лишних
    перекодировок). channel_bug — PNG overlay ПОСЛЕ concat и ПОСЛЕ субтитров.
  • Скрипт НЕ запускает ffmpeg сам (кроме --check). Он печатает строку фильтра
    в stdout; пустой stdout = у сцены нет оверлеев (pass-through).

Схема overlays[] (в каждом clip/scene storyboard.json):
  {
    "type": "title|hud_counter|outcome_plate|rank_number|item_name|slogan|disclaimer",
    "text": "OSIAL\\nRISES",          // \\n → стопка drawtext-строк
    "position": "center|top-left|top-right|bottom-center|{x},{y}",
    "font": "ULT|TRJ|MED|ARI|IMPACT|MONT_BLACK|BEBAS",  // логический ключ (FONTS)
    "size": 130,
    "color": "white",                 // имя или RRGGBB
    "stroke": {"color": "black", "width": 4},
    "enable": [0.0, 5.0],             // [start,end] → between(t,..); ["gte", 13.5]; omit = весь клип
    "fade_in": 0.3,                   // опц. alpha-рампа от 0
    "opacity": 1.0,                   // опц. постоянная прозрачность
    "line_gap": 160                   // опц. шаг по y между строками (\\n), по умолчанию = size*1.25
  }

Usage:
  # фрагмент для одной сцены (editor зовёт в цикле K=1..N):
  python3 overlays.py storyboard.json --scene-index 3 --workdir build \\
      --input-label "[v3pre]" --output-label "[v3]"
  # все сцены разом (по строке на сцену с непустыми оверлеями):
  python3 overlays.py storyboard.json --emit-all --workdir build
  # channel-bug (после concat+ASS):
  python3 overlays.py storyboard.json --channel-bug --bug-png build/channel-bug.png \\
      --input-label "[vsub]" --output-label "[vout]"
  # валидация шрифтов до дорогого encode:
  python3 overlays.py storyboard.json --check
"""

import argparse
import json
import os
import sys


# ---------------------------------------------------------------------------
# Шрифты: логический ключ → список путей-кандидатов (первый существующий).
# Хардкод абсолютных путей в правилах непортативен — резолвим с фолбэками.
# ---------------------------------------------------------------------------

FONTS = {
    # «ультра» дисплейный — заголовки. Trajan/Impact как практичный фолбэк.
    "ULT": [
        "/Library/Fonts/TrajanPro-Bold.otf",
        os.path.expanduser("~/Library/Fonts/TrajanPro-Bold.otf"),
        "/Library/Fonts/Montserrat-Black.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
    "TRJ": [
        "/Library/Fonts/TrajanPro-Bold.otf",
        os.path.expanduser("~/Library/Fonts/TrajanPro-Bold.otf"),
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
    "MED": [  # средний вес для подплашек (hook_plate)
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
    "ARI": [  # Arial Unicode — нужен для ％ U+FF05 в счётчиках
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
    "IMPACT": [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Impact.ttf",
    ],
    "MONT_BLACK": [
        "/Library/Fonts/Montserrat-Black.ttf",
        os.path.expanduser("~/Library/Fonts/Montserrat-Black.ttf"),
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
    "BEBAS": [
        "/Library/Fonts/BebasNeue-Regular.ttf",
        os.path.expanduser("~/Library/Fonts/BebasNeue-Regular.ttf"),
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
}

# Имя цвета → ffmpeg-совместимое (ffmpeg понимает имена, но фиксируем набор)
NAMED_COLORS = {
    "white": "white", "black": "black", "red": "red", "green": "green",
    "yellow": "yellow", "blue": "blue", "gray": "gray", "lightgray": "0xBFBFBF",
    "orange": "orange",
}

# Именованные позиции → (x_expr, y_expr). Для title/outcome y часто переопределяется.
NAMED_POS = {
    "center": ("(w-text_w)/2", "(h-text_h)/2"),
    "top-left": ("40", "40"),
    "top-right": ("w-text_w-40", "80"),
    "bottom-center": ("(w-text_w)/2", "h-text_h-200"),
    "top-center": ("(w-text_w)/2", "200"),
}


def resolve_font(key: str) -> str | None:
    """Логический ключ или абсолютный путь → существующий путь шрифта."""
    if key and os.path.isabs(key) and os.path.isfile(key):
        return key
    for cand in FONTS.get(key, []):
        if os.path.isfile(cand):
            return cand
    return None


def resolve_color(c: str) -> str:
    if not c:
        return "white"
    if c.lower() in NAMED_COLORS:
        return NAMED_COLORS[c.lower()]
    hexc = c.lstrip("#").upper()
    if len(hexc) == 6:
        return f"0x{hexc}"
    return c


def _enable_expr(enable) -> str | None:
    if not enable:
        return None
    if isinstance(enable, (list, tuple)):
        if len(enable) == 2 and enable[0] == "gte":
            return f"gte(t,{float(enable[1])})"
        if len(enable) == 2:
            return f"between(t,{float(enable[0])},{float(enable[1])})"
    return None


def _alpha_expr(fade_in: float, opacity: float, enable) -> str | None:
    """alpha для drawtext (0..1). fade_in рампит от начала enable-окна."""
    base = opacity if opacity is not None else 1.0
    if not fade_in:
        return f"{base}" if base != 1.0 else None
    # старт окна
    t0 = 0.0
    if isinstance(enable, (list, tuple)) and len(enable) == 2 and enable[0] != "gte":
        t0 = float(enable[0])
    elif isinstance(enable, (list, tuple)) and len(enable) == 2 and enable[0] == "gte":
        t0 = float(enable[1])
    return f"if(lt(t-{t0},{fade_in}),(t-{t0})/{fade_in}*{base},{base})"


def _write_textfile(workdir: str, scene_idx, oi, li, text: str) -> str:
    os.makedirs(workdir, exist_ok=True)
    path = os.path.join(workdir, f"ovl-s{scene_idx}-{oi}-{li}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def build_overlay_drawtexts(ov: dict, scene_idx, oi: int, workdir: str) -> list[str]:
    """Один overlay-объект → список drawtext-фильтров (по строке на \\n)."""
    font = resolve_font(ov.get("font", "IMPACT"))
    if font is None:
        print(f"  [warn] шрифт '{ov.get('font')}' не найден — fallback Impact", file=sys.stderr)
        font = resolve_font("IMPACT")
    size = int(ov.get("size", 72))
    color = resolve_color(ov.get("color", "white"))
    stroke = ov.get("stroke") or {}
    bw = int(stroke.get("width", 0))
    bcolor = resolve_color(stroke.get("color", "black"))
    enable = ov.get("enable")
    en = _enable_expr(enable)
    alpha = _alpha_expr(ov.get("fade_in", 0), ov.get("opacity", 1.0), enable)

    # позиция
    pos = ov.get("position", "center")
    if isinstance(pos, str) and pos in NAMED_POS:
        x_expr, y_base = NAMED_POS[pos]
    elif isinstance(pos, str) and "," in pos:
        x_str, y_str = pos.split(",", 1)
        x_expr, y_base = x_str.strip(), y_str.strip()
    elif isinstance(pos, dict):
        x_expr, y_base = str(pos.get("x", "(w-text_w)/2")), str(pos.get("y", "200"))
    else:
        x_expr, y_base = NAMED_POS["center"]

    lines = str(ov.get("text", "")).split("\\n")
    if len(lines) == 1 and "\n" in lines[0]:
        lines = lines[0].split("\n")
    line_gap = int(ov.get("line_gap", round(size * 1.25)))

    filters = []
    for li, line in enumerate(lines):
        if not line.strip():
            continue
        tf = _write_textfile(workdir, scene_idx, oi, li, line)
        # y для многострочных: смещаем вниз; для center-выражений добавляем offset
        if li == 0:
            y_expr = y_base
        else:
            y_expr = f"({y_base})+{li * line_gap}"
        parts = [
            f"drawtext=textfile='{tf}'",
            f"fontfile='{font}'",
            f"fontsize={size}",
            f"fontcolor={color}",
            "expansion=none",
            f"x={x_expr}",
            f"y={y_expr}",
        ]
        if bw > 0:
            parts.append(f"borderw={bw}")
            parts.append(f"bordercolor={bcolor}")
        if en:
            parts.append(f"enable='{en}'")
        if alpha:
            parts.append(f"alpha='{alpha}'")
        filters.append(":".join(parts))
    return filters


def scene_fragment(scene: dict, scene_idx, workdir: str,
                   in_label: str, out_label: str) -> str:
    """Все оверлеи сцены → один filter-фрагмент '[in]drawtext,...[out]'.
    Пусто, если оверлеев нет."""
    overlays = scene.get("overlays") or []
    all_dt = []
    for oi, ov in enumerate(overlays):
        all_dt.extend(build_overlay_drawtexts(ov, scene_idx, oi, workdir))
    if not all_dt:
        return ""
    return f"{in_label}" + ",".join(all_dt) + f"{out_label}"


def scene_idx(s: dict):
    """Индекс сцены/клипа: поддержка `index` (scenes) и `call_index` (in-game-pov clips)."""
    return s.get("index", s.get("call_index", 0))


def find_scenes(sb: dict) -> list[dict]:
    arr = sb.get("scenes") or sb.get("clips") or []
    return sorted(arr, key=scene_idx)


def channel_bug_fragment(bug_label: str, in_label: str, out_label: str) -> str:
    """channel-bug: PNG 110×110, top-left 40,40, после concat+ASS.
    bug_label — РЕАЛЬНЫЙ лейбл входа PNG в ffmpeg (напр. '[5:v]', где 5 = индекс
    последнего '-i build/channel-bug.png'). Editor обязан добавить этот вход и
    передать его индекс через --bug-input-label.
    Фрагмент: [5:v]scale=110:110[bug];[vsub][bug]overlay=40:40[vout]
    """
    return (f"{bug_label}scale=110:110[bug];"
            f"{in_label}[bug]overlay=40:40:format=auto{out_label}")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard", help="путь к storyboard.json")
    ap.add_argument("--scene-index", type=int, default=None,
                    help="индекс сцены (1-based) — эмит фрагмента для неё")
    ap.add_argument("--emit-all", action="store_true",
                    help="по строке на каждую сцену с оверлеями: 'IDX<TAB>fragment'")
    ap.add_argument("--channel-bug", action="store_true",
                    help="эмит channel-bug overlay (после concat)")
    ap.add_argument("--bug-png", default=None, help="путь к PNG лого (для --channel-bug; проверка наличия)")
    ap.add_argument("--bug-input-label", default="[BUG:v]",
                    help="РЕАЛЬНЫЙ лейбл входа PNG в ffmpeg, напр. '[5:v]' (индекс -i channel-bug.png)")
    ap.add_argument("--workdir", default="build", help="куда писать textfile'ы")
    ap.add_argument("--input-label", default="[vin]")
    ap.add_argument("--output-label", default="[vout]")
    ap.add_argument("--check", action="store_true",
                    help="проверить наличие всех шрифтов, упомянутых в storyboard")
    args = ap.parse_args()

    with open(args.storyboard, encoding="utf-8") as f:
        sb = json.load(f)
    scenes = find_scenes(sb)

    if args.check:
        used = set()
        for s in scenes:
            for ov in (s.get("overlays") or []):
                used.add(ov.get("font", "IMPACT"))
        missing = [k for k in used if resolve_font(k) is None]
        for k in sorted(used):
            print(f"  font {k}: {resolve_font(k) or 'MISSING'}", file=sys.stderr)
        if missing:
            print(f"ERROR: шрифты не найдены: {missing}", file=sys.stderr)
            sys.exit(1)
        print("  [check] все шрифты найдены", file=sys.stderr)
        return

    if args.channel_bug:
        if not args.bug_png or not os.path.isfile(args.bug_png):
            print(f"ERROR: --bug-png не найден: {args.bug_png}", file=sys.stderr)
            sys.exit(1)
        if args.bug_input_label == "[BUG:v]":
            print("  [warn] --bug-input-label не задан: подставь РЕАЛЬНЫЙ индекс входа PNG "
                  "(напр. '[5:v]' где 5 = позиция '-i build/channel-bug.png' среди -i). "
                  "Сейчас в фрагменте плейсхолдер [BUG:v] — ffmpeg его не примет.", file=sys.stderr)
        print(channel_bug_fragment(args.bug_input_label, args.input_label, args.output_label))
        return

    if args.emit_all:
        for s in scenes:
            idx = scene_idx(s)
            frag = scene_fragment(s, idx, args.workdir,
                                  f"[v{idx}pre]", f"[v{idx}]")
            if frag:
                print(f"{idx}\t{frag}")
        return

    if args.scene_index is not None:
        match = next((s for s in scenes if scene_idx(s) == args.scene_index), None)
        if match is None:
            print(f"ERROR: сцена index={args.scene_index} не найдена", file=sys.stderr)
            sys.exit(1)
        frag = scene_fragment(match, args.scene_index, args.workdir,
                              args.input_label, args.output_label)
        if frag:
            print(frag)
        # пустой stdout = нет оверлеев (editor делает pass-through)
        return

    print("ERROR: укажи --scene-index, --emit-all, --channel-bug или --check", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
