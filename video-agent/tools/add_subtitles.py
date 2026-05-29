#!/usr/bin/env python3
"""
Унифицированный ASS-генератор субтитров для видео-пайплайна.

Два канонических стилевых пресета (выбор делает оркестратор, не редактор):

  --style bold       punchy social-video подписи: Helvetica Bold 96, КАПС,
                     2 слова на чанк (или перенос на пунктуации), MarginV=520,
                     MarginL/R=100 (safe-zone от overflow на длинных парах).
                     Для фастпейс-форматов (serial-drama, news, dance-battle,
                     standard, top-list narrator).

  --style narrative  читаемые длинные строки: Helvetica Bold 84, Sentence case,
                     4-6 слов на чанк, MarginV=420. Для нарративных форматов
                     (what-if-lore, redcon, character-story, reddit-story).

  --style none       (не для этого скрипта — оркестратор просто не вызывает его)

ОБОСНОВАНИЕ MarginV (safe-zone TikTok/Reels/Shorts):
    UI соцсетей (caption-bar, username, right-rail actions) перекрывает нижние
    25-30% кадра 1080×1920. При PlayResY=1920:
      MarginV=520 (~27% от низа) → BOLD: гарантированно над UI на любой
        вертикальной платформе, переживает рывки UI.
      MarginV=420 (~22% от низа) → NARRATIVE: длиннее, спокойнее, чуть ниже
        допустимо — narrative не конкурирует с быстрой сменой UI.
    Меньшие значения трогать без причины НЕ НАДО.

Источник таймингов:
  --text "..."       пропорциональные тайминги из известного текста +
                     длительности MP3. БЕЗ Whisper, БЕЗ внешних API.
                     Используется ВСЕГДА в нашем пайплайне (TTS-текст известен).

  (нет --text)       fallback на faster-whisper (медленно, может галлюцинировать).
                     Только если текст реально неизвестен.

Оверрайды:
  --offset SECS              сдвиг всех таймкодов (pre-delay титульной карточки,
                             например 5с для redcon / what-if-lore).
  --mask                     BorderStyle=4 (полупрозрачный фоновый бокс) вместо 1.
                             Для what-if-real-life (маскировка артефактов Kling).
  --secondary-style SPEC     добавить второй стиль для двух-спикерных форматов.
                             SPEC = "Name=color,size,italic,marginv"
                             например: "Customer=lightgray,52,1,120"
  --highlight-words          каждое слово получает inline-тег цвета на свой
                             интервал (word-by-word акцент) для
                             gameplay-ai-avatar, reddit-story.
  --highlight-color HEX      ASS-цвет для --highlight-words (по умолчанию
                             0000FFFF = жёлтый).
  --marginv N                принудительный MarginV (переопределяет пресет;
                             используется gameplay-ai-avatar для split-seam).
  --emit-timings PATH        НЕ генерировать ASS, а просто сохранить
                             timings JSON (используется sound-ролью).

Usage:
  # Канонический вызов из editor pipeline:
  python3 add_subtitles.py - SCENE.mp3 build/subs.ass \\
      --emit-ass-only --duration 4.23 --text "..." --style bold \\
      [--offset 5] [--mask] [--highlight-words] [--marginv 800]

  # Sound-роль: только timings JSON:
  python3 add_subtitles.py - SCENE.mp3 SCENE.timings.json \\
      --emit-timings --text "..."

Stdout: путь итогового файла. Stderr: прогресс.
FFMPEG: ищется по нескольким путям, требуется libass для бёрна.
"""

import argparse
import json
import os
import re
import string
import subprocess
import sys

# ---------------------------------------------------------------------------
# FFmpeg locator
# ---------------------------------------------------------------------------

FFMPEG = "/usr/local/bin/ffmpeg-full/ffmpeg"
if not os.path.isfile(FFMPEG):
    for _alt in [
        "/opt/homebrew/Cellar/ffmpeg-full/8.1.1/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ]:
        if os.path.isfile(_alt):
            FFMPEG = _alt
            break


# ---------------------------------------------------------------------------
# Стилевые пресеты (см. docstring выше для обоснования)
# ---------------------------------------------------------------------------

# Каждый пресет — словарь с готовыми ASS V4+ полями + параметры чанкинга.
# PrimaryColour, OutlineColour, BackColour в BGR (&HAABBGGRR где AA — alpha-inv).
# &H00FFFFFF = непрозрачный белый, &H00000000 = непрозрачный чёрный.

BOLD_STYLE = {
    "name": "Default",
    "fontname": "Helvetica",
    "fontsize": 96,             # снижено с 108 — длинные UPPERCASE-пары
                                # ("SYSTEMIC OPPRESSION") вылазили за кадр
    "primary": "&H00FFFFFF",   # белый
    "secondary": "&H000000FF",
    "outline_col": "&H00000000",  # чёрный
    "back": "&H00000000",
    "bold": 1,
    "italic": 0,
    "underline": 0,
    "strike": 0,
    "scalex": 100,
    "scaley": 100,
    "spacing": 0,
    "angle": 0,
    "borderstyle": 1,           # 1=outline+drop shadow, 4=opaque box
    "outline": 6,
    "shadow": 0,
    "alignment": 2,             # bottom-center
    "marginl": 100,             # safe-zone слева (было 60) — anti-overflow
    "marginr": 100,             # safe-zone справа (было 60) — anti-overflow
    "marginv": 520,             # ~27% от низа 1920 — над TikTok/Reels UI
    "encoding": 1,
    # чанкинг:
    "chunk_target": 2,          # 2 слова на чанк
    "uppercase": True,
}

NARRATIVE_STYLE = {
    "name": "Default",
    "fontname": "Helvetica",
    "fontsize": 84,
    "primary": "&H00FFFFFF",
    "secondary": "&H000000FF",
    "outline_col": "&H00000000",
    "back": "&H00000000",
    "bold": 1,
    "italic": 0,
    "underline": 0,
    "strike": 0,
    "scalex": 100,
    "scaley": 100,
    "spacing": 0,
    "angle": 0,
    "borderstyle": 1,
    "outline": 5,
    "shadow": 0,
    "alignment": 2,
    "marginl": 80,
    "marginr": 80,
    "marginv": 420,             # ~22% от низа — narrative-сабы длиннее
    "encoding": 1,
    "chunk_target": 5,          # 4-6 слов, переносим на пунктуации
    "uppercase": False,
}

PRESETS = {
    "bold": BOLD_STYLE,
    "narrative": NARRATIVE_STYLE,
}

# Знаки, на которых принудительно режем чанк (естественные паузы)
PUNCT_BREAK = set(".,!?;:—")


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------

def strip_outer_punct(word: str) -> str:
    """Срезает обрамляющую пунктуацию, оставляя апострофы внутри слова."""
    return word.strip(string.punctuation + "—–«»""''")


def get_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        text=True,
    )
    return float(out.strip())


def fmt_ass_time(sec: float) -> str:
    if sec < 0:
        sec = 0.0
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# ---------------------------------------------------------------------------
# Пропорциональные тайминги (БЕЗ Whisper)
#
# Принцип: текст известен (мы его сами TTS-им). MP3 duration известен.
# Каждое слово получает длительность пропорционально количеству символов,
# с минимумом 0.15с и максимумом 0.6с на слово, потом всё масштабируется
# точно под duration. Ошибка ±100мс на слово — для 2-словных чанков
# по 0.5-1с это невидимо.
# ---------------------------------------------------------------------------

MIN_WORD_S = 0.15
MAX_WORD_S = 0.60


def proportional_timings(text: str, duration: float) -> list[tuple[float, float, str]]:
    """text + длительность MP3 → список (start, end, word) с пунктуацией в word."""
    # Разбить по пробелам, сохранить пунктуацию внутри токенов
    raw_tokens = [t for t in re.split(r"\s+", text.strip()) if t]
    if not raw_tokens:
        return []

    # Веса пропорционально len(strip_outer_punct(word)) (без обрамляющей пунктуации)
    weights = []
    for tok in raw_tokens:
        core = strip_outer_punct(tok)
        # Защита от пустого ядра (одиночная пунктуация типа "—")
        weights.append(max(1, len(core)))
    total_w = sum(weights)

    # Первое приближение длительностей
    durs = [duration * w / total_w for w in weights]

    # Клипуем по min/max
    durs = [max(MIN_WORD_S, min(MAX_WORD_S, d)) for d in durs]

    # После клиппинга сумма поплыла — масштабируем линейно
    scale = duration / sum(durs)
    durs = [d * scale for d in durs]

    # Собираем тайминги
    out = []
    cursor = 0.0
    for tok, d in zip(raw_tokens, durs):
        out.append((cursor, cursor + d, tok))
        cursor += d
    # Финальный snap последнего слова к точной длительности
    if out:
        last_s, _, last_w = out[-1]
        out[-1] = (last_s, duration, last_w)
    return out


# ---------------------------------------------------------------------------
# Whisper fallback (медленный путь — только когда --text не передан)
# ---------------------------------------------------------------------------

def whisper_transcribe(mp3_path: str, lang: str) -> list[tuple[float, float, str]]:
    print(
        f"  [whisper FALLBACK] передайте --text для быстрого пути. "
        f"транскрибирую {os.path.basename(mp3_path)} ...",
        file=sys.stderr,
    )
    from faster_whisper import WhisperModel
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(mp3_path, word_timestamps=True, language=lang)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append((w.start, w.end, w.word.strip()))
    print(f"  [whisper] {len(words)} слов", file=sys.stderr)
    return words


# ---------------------------------------------------------------------------
# Чанкинг (2-словные удары или перенос на пунктуации)
# ---------------------------------------------------------------------------

def chunk_words(
    words: list[tuple[float, float, str]],
    target: int,
    clip_dur: float,
) -> list[tuple[float, float, list[str]]]:
    """Группирует в чанки. Перенос когда: достигли target ИЛИ слово
    оканчивается на пунктуацию из PUNCT_BREAK. Каждый чанк живёт до начала
    следующего (или до clip_dur для последнего)."""
    chunks_raw: list[list[tuple[float, float, str]]] = []
    cur: list[tuple[float, float, str]] = []
    for w in words:
        cur.append(w)
        ends_in_punct = bool(w[2]) and w[2][-1] in PUNCT_BREAK
        if len(cur) >= target or ends_in_punct:
            chunks_raw.append(cur)
            cur = []
    if cur:
        chunks_raw.append(cur)

    result = []
    for j, group in enumerate(chunks_raw):
        start = group[0][0]
        # окончание чанка = начало следующего (плотная пульсация)
        if j + 1 < len(chunks_raw):
            end = chunks_raw[j + 1][0][0]
        else:
            end = clip_dur
        clean = [strip_outer_punct(w[2]) for w in group]
        result.append((start, end, clean))
    return result


# ---------------------------------------------------------------------------
# Построение ASS
# ---------------------------------------------------------------------------

def _style_line(style: dict) -> str:
    """V4+ Style: строка из словаря пресета."""
    return (
        f"Style: {style['name']},{style['fontname']},{style['fontsize']},"
        f"{style['primary']},{style['secondary']},{style['outline_col']},{style['back']},"
        f"{style['bold']},{style['italic']},{style['underline']},{style['strike']},"
        f"{style['scalex']},{style['scaley']},{style['spacing']},{style['angle']},"
        f"{style['borderstyle']},{style['outline']},{style['shadow']},"
        f"{style['alignment']},{style['marginl']},{style['marginr']},{style['marginv']},"
        f"{style['encoding']}"
    )


def parse_secondary_style(spec: str, base: dict) -> dict:
    """SPEC = "Name=color,size,italic,marginv"
    color может быть hex (BBGGRR) или именованный (lightgray, yellow, white).
    """
    name, _, rest = spec.partition("=")
    name = name.strip()
    parts = [p.strip() for p in rest.split(",")]
    color_token = parts[0] if len(parts) > 0 and parts[0] else "FFFFFF"
    size = int(parts[1]) if len(parts) > 1 and parts[1] else base["fontsize"]
    italic = int(parts[2]) if len(parts) > 2 and parts[2] else 0
    marginv = int(parts[3]) if len(parts) > 3 and parts[3] else base["marginv"]

    NAMED = {
        "white": "FFFFFF",
        "black": "000000",
        "lightgray": "BFBFBF",
        "gray": "808080",
        "yellow": "00FFFF",   # BBGGRR
        "red": "0000FF",
        "green": "00FF00",
        "blue": "FF0000",
    }
    if color_token.lower() in NAMED:
        hex6 = NAMED[color_token.lower()]
    else:
        hex6 = color_token.upper().lstrip("#")
        if len(hex6) == 6:
            # Передан RRGGBB — конвертируем в BBGGRR
            rr, gg, bb = hex6[0:2], hex6[2:4], hex6[4:6]
            hex6 = bb + gg + rr
    primary = f"&H00{hex6}"

    out = dict(base)
    out.update({
        "name": name,
        "primary": primary,
        "fontsize": size,
        "italic": italic,
        "marginv": marginv,
    })
    return out


def apply_highlight_words(
    chunk_clean: list[str],
    chunk_orig: list[tuple[float, float, str]],
    chunk_start: float,
    highlight_color: str,
) -> str:
    """Для --highlight-words: каждое слово оборачиваем в тег цвета с задержкой
    от начала чанка, используя \\k или просто \\c (без караоке-эффекта, чтобы
    libass отрисовало стабильно).

    Подсветка: текущее слово окрашено в highlight_color, остальные белые.
    Реализация через \\k (центисекунды) с включением primary='white' и
    secondary=highlight (наоборот, secondary видна до момента \\k).

    Простой способ: статическая раскраска через \\c на интервалах. Но это
    требует разрезать чанк на N событий. Чтобы не размножать события,
    используем \\k-караоке: secondary — это акцентный цвет, primary — белый.
    """
    # Используем караоке-теги \kf (fill karaoke): до \kf секции текст secondary,
    # после — primary. Чтобы получить «текущее слово акцентом, остальные белым»,
    # надо менять secondary → primary посимвольно. Но классический эффект
    # subtitle karaoke (фронт-runner — secondary, после — primary) хорошо
    # читается и привычен.
    #
    # Включаем secondary = highlight_color (как акцентная подсветка фронт-раннера)
    # через override-тег \3c (outline) НЕ трогаем. \2c устанавливает secondary,
    # \kf X — karaoke fill за X*10мс.

    # Вычислим длительность каждого слова в чанке
    word_durs_cs = []  # в центисекундах
    for i, (ws, we, _) in enumerate(chunk_orig):
        word_durs_cs.append(max(5, int(round((we - ws) * 100))))

    # Собираем строку: \2c для акцентного цвета secondary, потом \kfXX <word>
    parts = [f"{{\\2c&H{highlight_color}&}}"]
    for word, cs in zip(chunk_clean, word_durs_cs):
        if not word:
            continue
        parts.append(f"{{\\kf{cs}}}{word} ")
    text = "".join(parts).rstrip()
    return text


def build_ass(
    chunks: list[tuple[float, float, list[str]]],
    chunks_raw: list[list[tuple[float, float, str]]],
    style: dict,
    secondary,
    highlight_words: bool,
    highlight_color: str,
) -> str:
    # PlayResY=1920 → MarginV, FontSize в пикселях родного 1080×1920 канваса.
    header_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        ("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
         "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
         "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
         "Alignment, MarginL, MarginR, MarginV, Encoding"),
        _style_line(style),
    ]
    if secondary is not None:
        header_lines.append(_style_line(secondary))

    header_lines += [
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    out = ["\n".join(header_lines)]
    for (start, end, clean_words), group in zip(chunks, chunks_raw):
        text_plain = " ".join(w for w in clean_words if w)
        if style["uppercase"]:
            text_plain = text_plain.upper()

        if highlight_words:
            # Регистр применяем к каждому слову отдельно перед оборачиванием
            words_cased = [
                (w.upper() if style["uppercase"] else w) for w in clean_words if w
            ]
            text = apply_highlight_words(
                words_cased, group, start, highlight_color,
            )
        else:
            text = text_plain

        out.append(
            f"Dialogue: 0,{fmt_ass_time(start)},{fmt_ass_time(end)},"
            f"{style['name']},,0,0,0,,{text}"
        )

    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Timings JSON emit (для sound-роли)
# ---------------------------------------------------------------------------

def emit_timings_json(
    out_path: str,
    text: str,
    duration: float,
    words: list[tuple[float, float, str]],
) -> None:
    payload = {
        "duration_s": round(duration, 3),
        "text": text,
        "words": [
            {"text": w, "start": round(s, 3), "end": round(e, 3)}
            for (s, e, w) in words
        ],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help='путь к видео или "-" если только аудио')
    ap.add_argument("audio", help="путь к MP3 (TTS)")
    ap.add_argument("output", help="путь итогового .ass / .json (или .mp4 для legacy burn-in)")

    # Источник таймингов
    ap.add_argument("--text", default=None,
                    help="известный текст диалога — БЕЗ Whisper, пропорциональные тайминги")
    ap.add_argument("--lang", default="en",
                    help="язык для whisper fallback (используется только без --text)")

    # Стиль
    ap.add_argument("--style", choices=["bold", "narrative"], default="bold",
                    help="стилевой пресет (выбирает оркестратор по формату)")
    ap.add_argument("--mask", action="store_true",
                    help="BorderStyle=4 (полупрозрачный фоновый бокс) — для what-if-real-life")
    ap.add_argument("--secondary-style", default=None,
                    help='второй стиль: "Name=color,size,italic,marginv"')
    ap.add_argument("--marginv", type=int, default=None,
                    help="принудительный MarginV (переопределяет пресет)")

    # Подсветка слов
    ap.add_argument("--highlight-words", action="store_true",
                    help="word-by-word акцент (gameplay-ai-avatar, reddit-story)")
    ap.add_argument("--highlight-color", default="00FFFF",
                    help='цвет акцента в BBGGRR без префикса (по умолчанию жёлтый "00FFFF")')

    # Тайм-шифты
    ap.add_argument("--offset", "--start-offset", dest="offset", type=float, default=0.0,
                    help="сдвиг всех таймкодов вперёд (pre-delay титульной карточки)")
    ap.add_argument("--atempo", type=float, default=1.0,
                    help="audio speedup factor; тайминги делятся на atempo")
    ap.add_argument("--duration", type=float, default=None,
                    help="принудительная длительность клипа (для --emit-ass-only без видео)")

    # Режимы вывода
    ap.add_argument("--emit-ass-only", action="store_true",
                    help="только ASS, без бёрна (канонический пайплайн)")
    ap.add_argument("--emit-timings", action="store_true",
                    help="только timings JSON (для sound-роли)")

    args = ap.parse_args()

    if args.atempo < 1.0 or args.atempo > 1.5:
        print(f"ERROR: --atempo должен быть в [1.0, 1.5], получено {args.atempo}",
              file=sys.stderr)
        sys.exit(1)

    # ---- 1. Определяем длительность клипа --------------------------------
    if args.duration is not None:
        clip_dur = float(args.duration)
    elif args.video and args.video != "-" and os.path.exists(args.video):
        clip_dur = get_duration(args.video)
    elif os.path.exists(args.audio):
        clip_dur = get_duration(args.audio)
    else:
        print("ERROR: не могу определить длительность (нет видео, нет аудио, нет --duration)",
              file=sys.stderr)
        sys.exit(1)

    # ---- 2. Источник таймингов -------------------------------------------
    if args.text:
        # Быстрый путь: пропорциональные тайминги из известного текста
        # Длительность аудио берём отдельно (без atempo — тайминги для исходного MP3)
        audio_dur = get_duration(args.audio) if os.path.exists(args.audio) else clip_dur
        words = proportional_timings(args.text, audio_dur)
        print(f"  [text] {len(words)} слов из --text, audio_dur={audio_dur:.2f}s",
              file=sys.stderr)
    else:
        words = whisper_transcribe(args.audio, args.lang)

    if not words:
        print("ERROR: 0 слов", file=sys.stderr)
        sys.exit(1)

    # atempo (тайминги делим)
    if args.atempo != 1.0:
        words = [(s / args.atempo, e / args.atempo, w) for (s, e, w) in words]

    # offset (сдвиг вперёд)
    if args.offset != 0.0:
        off = args.offset
        words = [(s + off, e + off, w) for (s, e, w) in words]

    # ---- 3. Режим emit-timings: пишем JSON и выходим ---------------------
    if args.emit_timings:
        # Для timings JSON фиксируем оригинальную длительность аудио
        text_source = args.text or " ".join(w for (_, _, w) in words)
        audio_dur = get_duration(args.audio) if os.path.exists(args.audio) else clip_dur
        emit_timings_json(args.output, text_source, audio_dur, words)
        print(f"  [timings] {args.output} ({len(words)} слов)", file=sys.stderr)
        print(args.output)
        return

    # ---- 4. Выбираем пресет и применяем оверрайды ------------------------
    style = dict(PRESETS[args.style])
    if args.mask:
        style["borderstyle"] = 4
    if args.marginv is not None:
        style["marginv"] = args.marginv

    secondary = None
    if args.secondary_style:
        secondary = parse_secondary_style(args.secondary_style, style)

    # ---- 5. Чанкинг ------------------------------------------------------
    # Группируем "сырые" слова (с пунктуацией) в чанки
    target = style["chunk_target"]

    # Собираем чанки сразу с очисткой и с сохранением оригиналов параллельно
    chunks_raw: list[list[tuple[float, float, str]]] = []
    cur: list[tuple[float, float, str]] = []
    for w in words:
        cur.append(w)
        ends_in_punct = bool(w[2]) and w[2][-1] in PUNCT_BREAK
        if len(cur) >= target or ends_in_punct:
            chunks_raw.append(cur)
            cur = []
    if cur:
        chunks_raw.append(cur)

    chunks: list[tuple[float, float, list[str]]] = []
    for j, group in enumerate(chunks_raw):
        start = group[0][0]
        if j + 1 < len(chunks_raw):
            end = chunks_raw[j + 1][0][0]
        else:
            end = max(group[-1][1], clip_dur + args.offset)
        clean = [strip_outer_punct(w[2]) for w in group]
        chunks.append((start, end, clean))

    print(f"  [subs] {len(chunks)} чанков, style={args.style}, "
          f"marginv={style['marginv']}, mask={'on' if args.mask else 'off'}, "
          f"highlight={'on' if args.highlight_words else 'off'}",
          file=sys.stderr)

    # ---- 6. Сборка ASS ---------------------------------------------------
    ass_content = build_ass(
        chunks,
        chunks_raw,
        style,
        secondary,
        args.highlight_words,
        args.highlight_color,
    )

    # ---- 7. Запись --------------------------------------------------------
    ass_only = args.emit_ass_only or args.output.lower().endswith(".ass")

    if ass_only:
        ass_path = args.output if args.output.lower().endswith(".ass") else args.output + ".ass"
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
        print(f"  [ass-only] {ass_path} ({len(chunks)} чанков)", file=sys.stderr)
        print(ass_path)
        return

    # Legacy burn-in путь
    if not args.video or args.video == "-" or not os.path.exists(args.video):
        print("ERROR: burn-in требует валидный путь к видео (используйте --emit-ass-only)",
              file=sys.stderr)
        sys.exit(1)

    ass_path = args.output.replace(".mp4", ".ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    tmp_output = args.output + ".tmp.mp4"
    cmd = [FFMPEG, "-y", "-i", args.video, "-vf", f"subtitles={ass_path}",
           "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "copy",
           tmp_output]
    print(f"  [ffmpeg] burn-in ...", file=sys.stderr)
    log_path = args.output.replace(".mp4", ".ffmpeg.log")
    with open(log_path, "w") as log_f:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=log_f)
    if result.returncode != 0:
        with open(log_path) as f:
            tail = f.readlines()[-40:]
        print("".join(tail), file=sys.stderr)
        if os.path.exists(tmp_output):
            os.remove(tmp_output)
        sys.exit(1)

    try:
        out_dur = get_duration(tmp_output)
    except Exception as e:
        print(f"ERROR: ffprobe на бёрнутом видео ({e})", file=sys.stderr)
        os.remove(tmp_output)
        sys.exit(1)
    if abs(out_dur - clip_dur) > 0.5:
        print(f"ERROR: output dur {out_dur:.2f}s != input {clip_dur:.2f}s",
              file=sys.stderr)
        os.remove(tmp_output)
        sys.exit(1)

    os.replace(tmp_output, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
