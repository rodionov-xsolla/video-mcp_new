#!/usr/bin/env python3
"""
Унифицированный ASS-генератор субтитров для видео-пайплайна.

ОДИН универсальный стиль для ВСЕХ форматов. Никаких per-format пресетов,
масок, secondary-style, marginv-оверрайдов, offset/atempo. Это by-design —
субтитры обязаны выглядеть одинаково в каждом ролике.

ДВА ПРИНЦИПА (нарушение любого = вернулись к старому хаосу):

  1. Whisper даёт ТОЛЬКО тайм-коды. Текст для отрисовки — канонический из
     storyboard.json (ровно то, что Sound озвучивал). Whisper-транскрипт может
     галлюцинировать / перевирать слова (особенно Chatterbox-клоны) — мы его
     НЕ показываем. Канонические слова выравниваются по whisper-таймингам
     (forced alignment, difflib + интерполяция).

  2. Whisper гоняется по ФИНАЛЬНОЙ смикшированной речевой дорожке
     (build/voice-final.wav — пост-atempo, пост-adelay, пост-concat, до bg-music).
     Тогда тайминги корректны ПО ПОСТРОЕНИЮ: нет второго таймлайна, с которым
     можно разойтись. Поэтому offset/atempo/verify-audio больше не нужны и удалены.

УНИВЕРСАЛЬНЫЙ СТИЛЬ:
    Helvetica Bold 72, UPPERCASE, белый текст + чёрная обводка 6px,
    bottom-center, MarginV=520 (~27% от низа, над UI TikTok/Reels/Shorts),
    MarginL/R=100 (anti-overflow). Чанки по 4 слова. WrapStyle=0 переносит
    длинный чанк на 2 сбалансированные строки.

ПРАВИЛА ЧАНКИНГА (строгие):
    1. Граница предложения — твёрдая: чанк не содержит конец одного предложения
       и начало следующего (режем текст на предложения по .!?…, чанкуем внутри).
    2. target = 4 слова.
    3. Нет осиротевшего одного слова: минимум 2 слова в чанке (ребаланс внутри
       предложения, 5 слов = 3+2, не 4+1). Исключение — предложение из 1 слова.

Usage:
  # Канонический вызов из editor pipeline:
  python3 add_subtitles.py build/voice-final.wav build/subs.ass \\
      --storyboard storyboard.json --lang en --main-dur 44.96

  # Только timings JSON (опционально, whisper-based):
  python3 add_subtitles.py build/voice-final.wav out.timings.json \\
      --emit-timings --storyboard storyboard.json

Stdout: путь итогового файла. Stderr: прогресс.
FFMPEG: ищется по нескольким путям (для ffprobe длительности).
"""

import argparse
import difflib
import json
import math
import os
import re
import string
import subprocess
import sys

# ---------------------------------------------------------------------------
# FFmpeg locator (нужен только для ffprobe длительности)
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
# ЕДИНЫЙ универсальный стиль (PrimaryColour и т.д. в BGR &HAABBGGRR)
# ---------------------------------------------------------------------------

UNIVERSAL_STYLE = {
    "name": "Default",
    "fontname": "Helvetica",
    "fontsize": 72,             # уменьшено с 84 — 4-словный CAPS-чанк влезает в marginl/r=100
    "primary": "&H00FFFFFF",    # белый
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
    "borderstyle": 1,           # 1 = outline + drop shadow (НЕ opaque box)
    "outline": 6,
    "shadow": 0,
    "alignment": 2,             # bottom-center
    "marginl": 100,
    "marginr": 100,
    "marginv": 520,             # ~27% от низа 1920 — над TikTok/Reels/Shorts UI
    "encoding": 1,
}

CHUNK_TARGET = 4

# Пунктуация конца предложения (твёрдая граница чанка)
SENT_END = set(".!?…")
# Внутренняя пунктуация — предпочтительный (мягкий) разрыв
INNER_PUNCT = set(",;:—")


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------

def strip_outer_punct(word: str) -> str:
    """Срезает обрамляющую пунктуацию, оставляя апострофы внутри слова."""
    return word.strip(string.punctuation + "—–«»“”‘’")


def norm_token(word: str) -> str:
    """Нормализация для сопоставления: lowercase без обрамляющей пунктуации."""
    return strip_outer_punct(word).lower()


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
# Канонический текст из storyboard.json
#   single-voice: top-level .tts.full_text (или строка .tts)
#   multi-voice:  .scenes[].tts / .clips[].tts в порядке index (skip null)
# ---------------------------------------------------------------------------

def canonical_text_from_storyboard(sb_path: str) -> str:
    with open(sb_path, encoding="utf-8") as f:
        sb = json.load(f)

    # single-voice: один монолог на весь ролик
    tts = sb.get("tts")
    if isinstance(tts, dict) and tts.get("full_text", "").strip():
        return tts["full_text"].strip()
    if isinstance(tts, str) and tts.strip():
        return tts.strip()

    # multi-voice: собрать реплики сцен по порядку index
    arr = sb.get("scenes") or sb.get("clips") or []
    arr = sorted(arr, key=lambda x: x.get("index", 0))
    parts = []
    for s in arr:
        t = s.get("tts") or s.get("character_speech") or s.get("narration")
        if t and str(t).strip() and str(t).strip().lower() != "null":
            parts.append(str(t).strip())
    return " ".join(parts)


def lang_from_storyboard(sb_path: str) -> str:
    """Язык whisper из storyboard: tts.language_code или top-level language. Берём первые 2 буквы."""
    try:
        with open(sb_path, encoding="utf-8") as f:
            sb = json.load(f)
    except Exception:
        return "en"
    tts = sb.get("tts")
    code = ""
    if isinstance(tts, dict):
        code = tts.get("language_code", "") or ""
    code = code or sb.get("language", "") or "en"
    return (code[:2] or "en").lower()


# ---------------------------------------------------------------------------
# Whisper — ТОЛЬКО тайм-коды (текст из транскрипта не показываем)
# ---------------------------------------------------------------------------

def whisper_words(audio_path: str, lang: str) -> list[tuple[float, float, str]]:
    print(f"  [whisper] транскрибирую {os.path.basename(audio_path)} (только тайминги) ...",
          file=sys.stderr)
    from faster_whisper import WhisperModel
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, word_timestamps=True, language=lang)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append((w.start, w.end, w.word.strip()))
    print(f"  [whisper] {len(words)} слов", file=sys.stderr)
    return words


# ---------------------------------------------------------------------------
# Forced alignment: канонические слова ← whisper-тайминги
# ---------------------------------------------------------------------------

def force_align(
    canon_tokens: list[str],
    w_words: list[tuple[float, float, str]],
    total_dur: float,
) -> tuple[list[tuple[float, float]], float]:
    """Возвращает (timings, ratio): timings[i] = (start,end) для canon_tokens[i],
    ratio — доля сматченных канонических слов (для warn о расхождении).
    """
    n = len(canon_tokens)
    timings: list[tuple[float, float] | None] = [None] * n

    if not w_words:
        # Нет таймингов вовсе — равномерно по total_dur (последний резерв)
        if n:
            step = total_dur / n
            timings = [(i * step, (i + 1) * step) for i in range(n)]
        return [t for t in timings], 0.0

    c_norm = [norm_token(t) for t in canon_tokens]
    w_norm = [norm_token(w[2]) for w in w_words]

    sm = difflib.SequenceMatcher(a=c_norm, b=w_norm, autojunk=False)
    matched = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                ws = w_words[j1 + k]
                timings[i1 + k] = (ws[0], ws[1])
                matched += 1
        else:
            # canon[i1:i2] соответствует whisper[j1:j2] (любая сторона может быть пустой)
            cnt = i2 - i1
            if cnt <= 0:
                continue
            if j2 > j1:
                span_s = w_words[j1][0]
                span_e = w_words[j2 - 1][1]
                step = (span_e - span_s) / cnt if cnt else 0.0
                for k in range(cnt):
                    timings[i1 + k] = (span_s + k * step, span_s + (k + 1) * step)
            # если whisper-сторона пуста — оставляем None, заполним интерполяцией ниже

    # Заполнить оставшиеся None интерполяцией между известными соседями
    _fill_none(timings, total_dur)
    # Монотонность
    _enforce_monotonic(timings)

    ratio = matched / n if n else 1.0
    return [t for t in timings], ratio


def _fill_none(timings: list, total_dur: float) -> None:
    n = len(timings)
    # первый известный
    first = next((i for i in range(n) if timings[i] is not None), None)
    if first is None:
        # вообще ничего — равномерно
        step = total_dur / n if n else 0.0
        for i in range(n):
            timings[i] = (i * step, (i + 1) * step)
        return
    # головной хвост None
    if first > 0:
        s0 = timings[first][0]
        step = s0 / (first + 1) if first else 0.0
        for i in range(first):
            timings[i] = (i * step, (i + 1) * step)
    # внутренние/хвостовые
    i = first
    while i < n:
        if timings[i] is not None:
            i += 1
            continue
        # gap [i .. j-1]
        j = i
        while j < n and timings[j] is None:
            j += 1
        left_end = timings[i - 1][1]
        right_start = timings[j][0] if j < n else total_dur
        cnt = j - i
        step = (right_start - left_end) / cnt if cnt else 0.0
        for k in range(cnt):
            timings[i + k] = (left_end + k * step, left_end + (k + 1) * step)
        i = j


def _enforce_monotonic(timings: list) -> None:
    prev_e = 0.0
    for i, (s, e) in enumerate(timings):
        s = max(s, prev_e)
        e = max(e, s)
        timings[i] = (s, e)
        prev_e = e


# ---------------------------------------------------------------------------
# Чанкинг (строгие правила)
# ---------------------------------------------------------------------------

def split_sentences(tokens: list[str]) -> list[list[int]]:
    """Индексы токенов сгруппированы по предложениям (граница по .!?…)."""
    sentences: list[list[int]] = []
    cur: list[int] = []
    for idx, tok in enumerate(tokens):
        cur.append(idx)
        if tok and tok[-1] in SENT_END:
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    return sentences


def chunk_sentence(sent_idxs: list[int], target: int) -> list[list[int]]:
    """Делит ОДНО предложение на чанки. Гарантии: нет чанка из 1 слова
    (кроме предложения из 1 слова целиком); размеры сбалансированы; ≤ ~target.
    """
    n = len(sent_idxs)
    if n <= 1:
        return [sent_idxs]               # одиночное слово — неизбежно
    if n <= target:
        return [sent_idxs]               # помещается в один чанк (>=2 слов)

    # k = минимальное число чанков, чтобы каждый был ≤ target.
    # Для target=4 это всегда даёт размеры ≥2 (orphan невозможен).
    k = math.ceil(n / target)
    base, rem = divmod(n, k)
    sizes = [base + (1 if i < rem else 0) for i in range(k)]
    # подстраховка: если вдруг где-то 1 — уменьшаем k
    while k > 1 and min(sizes) < 2:
        k -= 1
        base, rem = divmod(n, k)
        sizes = [base + (1 if i < rem else 0) for i in range(k)]

    out: list[list[int]] = []
    p = 0
    for s in sizes:
        out.append(sent_idxs[p:p + s])
        p += s
    return out


def build_chunks(tokens: list[str], target: int) -> list[list[int]]:
    chunks: list[list[int]] = []
    for sent in split_sentences(tokens):
        chunks.extend(chunk_sentence(sent, target))
    return chunks


# ---------------------------------------------------------------------------
# Построение ASS
# ---------------------------------------------------------------------------

def _style_line(style: dict) -> str:
    return (
        f"Style: {style['name']},{style['fontname']},{style['fontsize']},"
        f"{style['primary']},{style['secondary']},{style['outline_col']},{style['back']},"
        f"{style['bold']},{style['italic']},{style['underline']},{style['strike']},"
        f"{style['scalex']},{style['scaley']},{style['spacing']},{style['angle']},"
        f"{style['borderstyle']},{style['outline']},{style['shadow']},"
        f"{style['alignment']},{style['marginl']},{style['marginr']},{style['marginv']},"
        f"{style['encoding']}"
    )


def build_ass(events: list[tuple[float, float, str]]) -> str:
    header_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        ("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
         "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
         "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
         "Alignment, MarginL, MarginR, MarginV, Encoding"),
        _style_line(UNIVERSAL_STYLE),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    out = ["\n".join(header_lines)]
    for start, end, text in events:
        out.append(
            f"Dialogue: 0,{fmt_ass_time(start)},{fmt_ass_time(end)},"
            f"{UNIVERSAL_STYLE['name']},,0,0,0,,{text}"
        )
    return "\n".join(out) + "\n"


def assemble_events(
    canon_tokens: list[str],
    timings: list[tuple[float, float]],
    chunks: list[list[int]],
    voice_dur: float,
    main_dur: float | None,
) -> list[tuple[float, float, str]]:
    """Чанки → ASS-события. Плотная пульсация (конец чанка = старт следующего).
    Последнее событие клампится к main_dur (или voice_dur)."""
    events: list[tuple[float, float, str]] = []
    n = len(chunks)
    cap = main_dur if main_dur is not None else voice_dur
    for j, group in enumerate(chunks):
        start = timings[group[0]][0]
        if j + 1 < n:
            end = timings[chunks[j + 1][0]][0]
        else:
            end = min(timings[group[-1]][1], cap)
        # display: UPPERCASE, без обрамляющей пунктуации
        words = [strip_outer_punct(canon_tokens[i]) for i in group]
        text = " ".join(w for w in words if w).upper()
        if not text:
            continue
        # main_dur кламп: выкидываем целиком за границей, обрезаем пересекающие
        if main_dur is not None:
            if start >= main_dur:
                continue
            end = min(end, main_dur)
        if end <= start:
            end = start + 0.30
        events.append((start, end, text))
    return events


# ---------------------------------------------------------------------------
# Timings JSON (опциональный режим, whisper-based, без --text)
# ---------------------------------------------------------------------------

def emit_timings_json(out_path: str, text: str, duration: float,
                      words: list[tuple[float, float, str]]) -> None:
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
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # 2 позиционных (audio, output) или legacy 3 (video, audio, output)
    ap.add_argument("paths", nargs="+",
                    help="audio output  (или legacy: video audio output)")
    ap.add_argument("--storyboard", default=None,
                    help="путь к storyboard.json — источник КАНОНИЧЕСКОГО текста (обяз. для бёрна)")
    ap.add_argument("--lang", default=None, help="язык для whisper (по умолчанию из storyboard language_code)")
    ap.add_argument("--main-dur", type=float, default=None,
                    help="конец последнего story-клипа (до CTA) — кламп субтитров")
    ap.add_argument("--emit-ass-only", action="store_true",
                    help="только ASS (канонический режим; по умолчанию, если output .ass)")
    ap.add_argument("--emit-timings", action="store_true",
                    help="только timings JSON (whisper-based, опционально)")
    ap.add_argument("--min-align-ratio", type=float, default=0.5,
                    help="порог forced-alignment: ниже → exit 1 (защита от не того аудио/языка)")
    args = ap.parse_args()

    # ---- позиционные: поддержка legacy 3-арг вызова -----------------------
    pos = args.paths
    if len(pos) == 3:
        # legacy: первый — видео ('-' или путь), отбрасываем
        if pos[0] == "-" or os.path.exists(pos[0]):
            print(f"  [compat] отбрасываю legacy video-аргумент '{pos[0]}'", file=sys.stderr)
            audio, output = pos[1], pos[2]
        else:
            audio, output = pos[1], pos[2]
    elif len(pos) == 2:
        audio, output = pos[0], pos[1]
    else:
        print("ERROR: ожидаю 2 позиционных аргумента: <audio> <output>", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(audio):
        print(f"ERROR: аудио не найдено: {audio}", file=sys.stderr)
        sys.exit(1)

    voice_dur = get_duration(audio)

    # ---- ГАРД voice-final.wav: длительность должна ≈ MAIN_DUR (картинная дорожка) ----
    # Самый частый баг сборки multi-voice voice-final: реплики склеены подряд БЕЗ тишины
    # под немые action-сцены → дорожка сильно короче картинки → субтитры уезжают по абсолютному
    # времени. Whisper выровняет слова по аудио, но аудио ≠ таймлайн видео. Ловим здесь.
    if args.main_dur is not None and not args.emit_timings:
        if voice_dur < args.main_dur * 0.6:
            print(f"ERROR: voice-final ({voice_dur:.1f}s) сильно короче MAIN_DUR "
                  f"({args.main_dur:.1f}s). Похоже, при сборке build/voice-final.wav пропущена "
                  f"тишина под немые/action-сцены — субтитры уедут по абсолютному времени. "
                  f"Пересобери voice-final как [aout] минус bg-music (editor.md §6.1).",
                  file=sys.stderr)
            sys.exit(1)
        if voice_dur > args.main_dur + 1.0:
            print(f"  [warn] voice-final ({voice_dur:.1f}s) длиннее MAIN_DUR ({args.main_dur:.1f}s) — "
                  f"последние слова будут обрезаны клампом. Подгони atempo, чтобы речь влезала в картинку.",
                  file=sys.stderr)

    # ---- язык whisper: явный --lang, иначе из storyboard, иначе en --------
    lang = args.lang or (lang_from_storyboard(args.storyboard) if args.storyboard else "en")
    print(f"  [lang] whisper language = {lang}", file=sys.stderr)

    # ---- timings-only режим (опционально) ---------------------------------
    if args.emit_timings:
        words = whisper_words(audio, lang)
        text = canonical_text_from_storyboard(args.storyboard) if args.storyboard else \
            " ".join(w for (_, _, w) in words)
        emit_timings_json(output, text, voice_dur, words)
        print(f"  [timings] {output} ({len(words)} слов)", file=sys.stderr)
        print(output)
        return

    # ---- канонический текст -----------------------------------------------
    if not args.storyboard:
        print("ERROR: --storyboard обязателен для бёрна (источник текста)", file=sys.stderr)
        sys.exit(1)
    canon_text = canonical_text_from_storyboard(args.storyboard)
    if not canon_text.strip():
        # Нет реплик во всём ролике — пустой ASS (бёрн = no-op)
        with open(output, "w", encoding="utf-8") as f:
            f.write(build_ass([]))
        print("  [subs] канонический текст пуст — пустой ASS", file=sys.stderr)
        print(output)
        return

    canon_tokens = [t for t in re.split(r"\s+", canon_text.strip()) if t]

    # ---- whisper тайминги + forced alignment ------------------------------
    w_words = whisper_words(audio, lang)
    timings, ratio = force_align(canon_tokens, w_words, voice_dur)
    if ratio < args.min_align_ratio:
        print(f"ERROR: forced-alignment ratio {ratio:.2f} < {args.min_align_ratio:.2f} — "
              f"whisper-транскрипт сильно разошёлся с каноном. Вероятные причины: не тот язык "
              f"(сейчас lang={lang} — проверь storyboard language_code), не то аудио в "
              f"voice-final.wav, или музыка/шум в дорожке. Чини источник, а не порог. "
              f"(Осознанно занизить можно через --min-align-ratio.)", file=sys.stderr)
        sys.exit(1)
    print(f"  [align] ratio {ratio:.2f} OK ({len(canon_tokens)} канонических слов)",
          file=sys.stderr)

    # ---- чанкинг ----------------------------------------------------------
    chunks = build_chunks(canon_tokens, CHUNK_TARGET)

    # ---- события + кламп --------------------------------------------------
    events = assemble_events(canon_tokens, timings, chunks, voice_dur, args.main_dur)

    # sanity: последнее слово не должно выходить за аудио + 50мс
    if timings:
        last_end = timings[-1][1]
        if last_end > voice_dur + 0.05:
            print(f"  [warn] последнее слово кончается на {last_end:.2f}s > аудио {voice_dur:.2f}s "
                  f"(whisper мог округлить).", file=sys.stderr)

    ass = build_ass(events)
    with open(output, "w", encoding="utf-8") as f:
        f.write(ass)
    print(f"  [subs] {output}: {len(events)} событий, {len(chunks)} чанков, "
          f"style=universal(72,CAPS,mv520)", file=sys.stderr)
    print(output)


# ===========================================================================
# === LEGACY (dead path, never invoked) =====================================
# Сохранено для истории / возможного возврата. НЕ вызывается из main().
# Старый пропорциональный тайминг из текста (источник «съезжания»), караоке
# и second-speaker — заведомо отключены архитектурным решением.
# ===========================================================================

_MIN_WORD_S = 0.15
_MAX_WORD_S = 0.60


def _legacy_proportional_timings(text: str, duration: float):
    """LEGACY. Пропорциональные тайминги из текста (БЕЗ whisper). Не использовать —
    не попадает в реальные паузы, был источником рассинхрона."""
    raw_tokens = [t for t in re.split(r"\s+", text.strip()) if t]
    if not raw_tokens:
        return []
    weights = [max(1, len(strip_outer_punct(tok))) for tok in raw_tokens]
    total_w = sum(weights)
    durs = [duration * w / total_w for w in weights]
    durs = [max(_MIN_WORD_S, min(_MAX_WORD_S, d)) for d in durs]
    scale = duration / sum(durs)
    durs = [d * scale for d in durs]
    out, cursor = [], 0.0
    for tok, d in zip(raw_tokens, durs):
        out.append((cursor, cursor + d, tok))
        cursor += d
    if out:
        s, _, w = out[-1]
        out[-1] = (s, duration, w)
    return out


def _legacy_apply_highlight_words(chunk_clean, chunk_orig, chunk_start, highlight_color):
    """LEGACY. Караоке word-by-word подсветка (\\kf). Отключено — единый белый стиль."""
    word_durs_cs = [max(5, int(round((we - ws) * 100))) for (ws, we, _) in chunk_orig]
    parts = [f"{{\\2c&H{highlight_color}&}}"]
    for word, cs in zip(chunk_clean, word_durs_cs):
        if word:
            parts.append(f"{{\\kf{cs}}}{word} ")
    return "".join(parts).rstrip()


def _legacy_parse_secondary_style(spec, base):
    """LEGACY. Второй стиль спикера. Отключено — вся речь одним стилем."""
    name, _, rest = spec.partition("=")
    parts = [p.strip() for p in rest.split(",")]
    return dict(base, name=name.strip())


if __name__ == "__main__":
    main()
