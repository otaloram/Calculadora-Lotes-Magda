"""Locución sintética.

Motores:
  edge   — Microsoft Edge TTS (voz es-AR-TomasNeural, rioplatense). Gratis, requiere internet.
           Devuelve marcas de tiempo por palabra.
  piper  — Piper offline (respaldo para pruebas). Voz española no rioplatense, menor calidad.
"""
import asyncio
import hashlib
import json
import os
import re
import subprocess
import wave
from pathlib import Path

SR = 48000


def apply_pronunciation(s: str, table: dict) -> str:
    for k in sorted(table, key=len, reverse=True):
        s = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", table[k], s)
    return s


def _to_wav(src: Path, dst: Path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", str(SR),
                    "-sample_fmt", "s16", str(dst)], check=True)


def wav_duration(p: Path) -> float:
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def _trim_silence(p: Path):
    """Recorta silencios del principio y del final (las pausas las controla el montaje)."""
    tmp = p.with_suffix(".trim.wav")
    af = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,"
          "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(p), "-af", af, str(tmp)], check=True)
    tmp.replace(p)


async def _edge(text, voice, rate, pitch, mp3: Path):
    import edge_tts
    kw = dict(rate=rate, pitch=pitch)
    try:
        com = edge_tts.Communicate(text, voice, boundary="WordBoundary", **kw)
    except TypeError:                      # versiones antiguas
        com = edge_tts.Communicate(text, voice, **kw)
    words = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"text": ch["text"], "start": ch["offset"] / 1e7,
                              "end": (ch["offset"] + ch["duration"]) / 1e7})
    return words


def _piper(text, out: Path):
    exe = os.environ.get("PIPER_BIN", "piper")
    model = os.environ["PIPER_MODEL"]
    subprocess.run([exe, "-m", model, "-f", str(out), "--sentence_silence", "0.25"], input=text.encode(),
                   check=True, capture_output=True)


def synthesize(text: str, cfg: dict, engine: str, cache: Path):
    """Devuelve (wav, duración, palabras_tts). Cachea por hash del texto + voz."""
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(json.dumps([text, engine, cfg.get("edge"), cfg.get("rate"), cfg.get("pitch"),
                                   os.environ.get("PIPER_MODEL")]).encode()).hexdigest()[:16]
    wav, meta = cache / f"{key}.wav", cache / f"{key}.json"
    if wav.exists() and meta.exists():
        m = json.loads(meta.read_text())
        return wav, m["dur"], m["words"]
    words = []
    if engine == "edge":
        mp3 = cache / f"{key}.mp3"
        for attempt in range(4):
            try:
                words = asyncio.run(_edge(text, cfg.get("edge", "es-AR-TomasNeural"), cfg.get("rate", "+0%"),
                                          cfg.get("pitch", "+0Hz"), mp3))
                break
            except Exception:
                if attempt == 3:
                    raise
        _to_wav(mp3, wav)
        mp3.unlink(missing_ok=True)
        # edge no agrega silencio inicial significativo; conservamos las marcas tal cual
    else:
        raw = cache / f"{key}.raw.wav"
        _piper(text, raw)
        _to_wav(raw, wav)
        raw.unlink(missing_ok=True)
        _trim_silence(wav)
    dur = wav_duration(wav)
    if not words:
        words = estimate_words(text, dur)
    meta.write_text(json.dumps({"dur": dur, "words": words}))
    return wav, dur, words


def estimate_words(text: str, dur: float):
    """Marcas aproximadas proporcionales a la longitud (cuando el motor no las provee)."""
    toks = text.split()
    weights = [len(w) + 2 + (6 if w[-1:] in ".,:;?" else 0) for w in toks]
    tot = sum(weights) or 1
    out, acc = [], 0.0
    for w, k in zip(toks, weights):
        s = dur * acc / tot
        acc += k
        out.append({"text": w, "start": s, "end": dur * acc / tot})
    return out


def map_words(original: str, tts_words: list, dur: float):
    """Proyecta las palabras del texto original (subtítulos) sobre la línea de tiempo real
    de la voz, usando la fracción acumulada de caracteres como referencia."""
    toks = original.split()
    if not toks:
        return []
    if not tts_words:
        return estimate_words(original, dur)
    tl = [len(w["text"]) + 1 for w in tts_words]
    tt = sum(tl)
    knots, acc = [], 0
    for w, k in zip(tts_words, tl):
        knots.append((acc / tt, w["start"]))
        acc += k
    knots.append((1.0, tts_words[-1]["end"]))

    def at(fr):
        for (f0, t0), (f1, t1) in zip(knots, knots[1:]):
            if fr <= f1:
                return t0 + (t1 - t0) * ((fr - f0) / (f1 - f0) if f1 > f0 else 0)
        return knots[-1][1]

    ol = [len(w) + 1 for w in toks]
    ot = sum(ol)
    out, acc = [], 0
    for w, k in zip(toks, ol):
        s = at(acc / ot)
        acc += k
        out.append({"text": w, "start": s, "end": at(acc / ot)})
    return out
