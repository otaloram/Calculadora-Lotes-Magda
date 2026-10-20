"""MUNDO DINERO — pipeline de producción: guion → voz → escenas → montaje → MP4 + entregables.

Uso:
  python -m md.build episodes/nvidia [--tts edge|piper] [--jobs 4] [--preview] [--burn-subs]
"""
import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import yaml

from . import music, tts
from .style import FPS, H, W

ROOT = Path(__file__).resolve().parent.parent
MOOD_BY_CHAPTER = {"c1": "tension", "c2": "warm", "c3": "progress", "c4": "tech", "c5": "reflect"}
LEAD_IN = 0.3      # silencio antes de la primera palabra


def load_data(ep):
    out = {}
    for k, v in (ep.get("data") or {}).items():
        if k.endswith("_source") or k == "note":
            out[k] = v
            continue
        with open(ROOT / v) as f:
            out[k] = [(r["date"], float(r["adj_close"])) for r in csv.DictReader(f)]
    return out


def fmt_ts(s, srt=True):
    h, m = int(s // 3600), int(s % 3600 // 60)
    sec = s % 60
    return f"{h:02d}:{m:02d}:{int(sec):02d},{int((sec % 1) * 1000):03d}" if srt else f"{m:d}:{int(sec):02d}"


# ───────────────────────────── render de una escena (proceso hijo) ─────────────────────────────

def render_scene(job):
    from . import style, visuals
    from .visuals import Ctx, render_frame
    sc, dur, words, data, ep_root, chap_label, chap_num, fade_in, fade_out, out, preview, colors = job
    for name, rgb in (colors or {}).items():      # acentos por episodio (p. ej. verde/azul de la empresa)
        style.ACCENTS[name] = tuple(rgb)
        setattr(visuals, name.upper(), tuple(rgb))
    ctx = Ctx(dur, words, data, ep_root, chap_label, chap_num, sc)
    fps = 12 if preview else FPS
    n = max(1, int(round(dur * fps)))
    size = (W // 2, H // 2) if preview else (W, H)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
           "-crf", "26" if preview else "17", "-pix_fmt", "yuv420p", "-r", str(fps), str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        t = i / fps
        im = render_frame(sc, t, ctx, fade_in, fade_out)
        if preview:
            im = im.resize(size)
        p.stdin.write(im.tobytes())
    p.stdin.close()
    p.wait()
    if p.returncode:
        raise RuntimeError(f"ffmpeg falló en {sc['id']}")
    return sc["id"], n / fps


# ───────────────────────────── pipeline ─────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", help="carpeta del episodio (con episode.yaml)")
    ap.add_argument("--tts", default="edge", choices=["edge", "piper"])
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--preview", action="store_true", help="960x540 a 12 fps para revisar rápido")
    ap.add_argument("--burn-subs", action="store_true", help="quemar subtítulos en la imagen")
    ap.add_argument("--only", help="renderizar solo estas escenas (s05,s07) para revisar")
    ap.add_argument("--out", default="build")
    a = ap.parse_args()

    ep_dir = (ROOT / a.episode).resolve() if not Path(a.episode).is_absolute() else Path(a.episode)
    ep = yaml.safe_load((ep_dir / "episode.yaml").read_text())
    out = ROOT / a.out / ep["slug"]
    (out / "scenes").mkdir(parents=True, exist_ok=True)
    data = load_data(ep)
    t0 = time.time()
    log = lambda m: print(f"[{time.time() - t0:6.1f}s] {m}", flush=True)  # noqa: E731

    # ETAPA 1 — interpretación
    scenes = ep["scenes"]
    full = " ".join(s["text"] for s in scenes)
    nwords = len(full.split())
    log(f"Guion: {nwords} palabras, {len(scenes)} planos, estimado {nwords / 145 * 60:.0f}s a 145 ppm")

    # ETAPA 3 — locución (el video sigue a la voz)
    pron = ep.get("pronunciation", {})
    cache = ROOT / a.out / "tts-cache"
    timeline, cursor = [], LEAD_IN
    for i, sc in enumerate(scenes):
        say = tts.apply_pronunciation(sc.get("say", sc["text"]), pron)
        wav, d, tw = tts.synthesize(say, ep.get("voice", {}), a.tts, cache)
        words = tts.map_words(sc["text"], tw, d)
        pause = sc.get("pause", ep.get("pause", 0.35))
        start = cursor - (LEAD_IN if i == 0 else 0)
        voice_at = cursor
        dur = (voice_at - start) + d + pause
        timeline.append(dict(sc=sc, wav=wav, voice_dur=d, start=start, voice_at=voice_at, dur=dur,
                             words=[{**w, "start": w["start"] + (voice_at - start), "end": w["end"] + (voice_at - start)}
                                    for w in words]))
        cursor = start + dur
    total = cursor
    log(f"Locución lista: {total:.1f}s ({a.tts})")

    # narración continua
    narr = np.zeros(int(total * tts.SR), dtype=np.int16)
    for tl in timeline:
        with wave.open(str(tl["wav"])) as w:
            pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        s = int(tl["voice_at"] * tts.SR)
        narr[s:s + len(pcm)] = pcm[: len(narr) - s]
    with wave.open(str(out / "narration.wav"), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(tts.SR), w.writeframes(narr.tobytes())

    # ETAPA 4-6 — escenas y montaje
    chapters = ep["chapters"]
    chap_ids = list(chapters)
    jobs = []
    only = set(a.only.split(",")) if a.only else None
    for i, tl in enumerate(timeline):
        sc = tl["sc"]
        if only and sc["id"] not in only:
            continue
        prev_c = timeline[i - 1]["sc"]["chapter"] if i else None
        next_c = timeline[i + 1]["sc"]["chapter"] if i + 1 < len(timeline) else None
        fade_in = 0.4 if prev_c != sc["chapter"] else 0.0
        fade_out = 0.4 if next_c != sc["chapter"] else 0.0
        jobs.append((sc, tl["dur"], tl["words"], data, ep_dir, chapters[sc["chapter"]].upper(),
                     chap_ids.index(sc["chapter"]) + 1, fade_in, fade_out, out / "scenes" / f"{sc['id']}.mp4",
                     a.preview, ep.get("colors")))
    log(f"Renderizando {len(jobs)} escenas con {a.jobs} procesos…")
    with Pool(a.jobs) as pool:
        for sid, d in pool.imap_unordered(render_scene, jobs):
            print(f"   ✓ {sid} ({d:.1f}s)", flush=True)
    if only:
        log("Escenas parciales renderizadas en " + str(out / "scenes"))
        return

    concat = out / "scenes.txt"
    concat.write_text("".join(f"file 'scenes/{tl['sc']['id']}.mp4'\n" for tl in timeline))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy",
                    str(out / "video.mp4")], check=True)

    # ETAPA 7 — sonido
    sections, cur = [], None
    for tl in timeline:
        # `mood:` en la escena tiene prioridad (p. ej. el fracaso pide menos música)
        mood = tl["sc"].get("mood") or MOOD_BY_CHAPTER.get(tl["sc"]["chapter"], "reflect")
        if cur and cur[2] == mood:
            cur[1] = tl["start"] + tl["dur"]
        else:
            cur = [tl["start"], tl["start"] + tl["dur"], mood]
            sections.append(cur)
    music.render_score([tuple(s) for s in sections], total, out / "music.wav")
    log("Música generada")

    # ETAPA 8 — subtítulos
    srt = build_srt(timeline)
    (out / f"{ep['slug']}.es.srt").write_text(srt, encoding="utf-8")

    final = out / f"{ep['slug']}.mp4"
    vf = []
    if a.burn_subs:
        style = "FontName=Inter,FontSize=15,PrimaryColour=&H00DFE8ED,OutlineColour=&H80000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=36"
        vf = ["-vf", f"subtitles={out / (ep['slug'] + '.es.srt')}:fontsdir={ROOT / 'fonts'}:force_style='{style}'"]
    fc = ("[1:a]aformat=channel_layouts=stereo,asplit=2[v1][v2];"
          "[2:a]volume=0.22[m];[m][v1]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=600[md];"
          "[v2][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out / "video.mp4"), "-i", str(out / "narration.wav"),
                    "-i", str(out / "music.wav"), "-filter_complex", fc, "-map", "0:v", "-map", "[a]", *vf,
                    *(["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"] if vf else ["-c:v", "copy"]),
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(final)],
                   check=True)
    log(f"MP4 final: {final}")

    # ETAPA 9-10 — entregables y control de calidad
    deliverables(ep, timeline, total, out, a)
    qc = quality_control(final, ep, timeline, a)
    (out / "qc_report.json").write_text(json.dumps(qc, indent=2, ensure_ascii=False))
    log("Control de calidad: " + ("OK" if qc["passed"] else "CON OBSERVACIONES"))
    for k, v in qc["checks"].items():
        print(f"   {'✓' if v['ok'] else '✗'} {k}: {v['detail']}")
    shutil.rmtree(out / "scenes", ignore_errors=True) if not a.preview else None


def build_srt(timeline, max_chars=42, max_dur=3.6):
    cues = []
    for tl in timeline:
        cur, cs, ce = [], None, None
        for w in tl["words"]:
            s, e = tl["start"] + w["start"], tl["start"] + w["end"]
            line = " ".join(cur + [w["text"]])
            if cur and (len(line) > max_chars * 2 or e - cs > max_dur):
                cues.append((cs, ce, " ".join(cur)))
                cur, cs = [], None
            if cs is None:
                cs = s
            cur.append(w["text"])
            ce = e
            if w["text"][-1:] in ".?!" and len(" ".join(cur)) > 18:
                cues.append((cs, ce, " ".join(cur)))
                cur, cs = [], None
        if cur:
            cues.append((cs, ce, " ".join(cur)))
    out = []
    for i, (s, e, txt) in enumerate(cues, 1):
        e = max(e + 0.15, s + 0.8)
        if i < len(cues):
            e = min(e, cues[i][0] - 0.02)
        # dos líneas equilibradas
        if len(txt) > max_chars:
            ws = txt.split()
            best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(" ".join(ws[k:]))))
            txt = " ".join(ws[:best]) + "\n" + " ".join(ws[best:])
        out.append(f"{i}\n{fmt_ts(s)} --> {fmt_ts(e)}\n{txt}\n")
    return "\n".join(out)


def deliverables(ep, timeline, total, out, a):
    # capítulos con marcas de tiempo (YouTube)
    chaps, seen = [], set()
    for tl in timeline:
        c = tl["sc"]["chapter"]
        if c not in seen:
            seen.add(c)
            chaps.append((0.0 if not chaps else tl["start"], ep["chapters"][c]))
    chap_txt = "\n".join(f"{fmt_ts(s, srt=False)} {name}" for s, name in chaps)
    desc = (f"{ep['title']}\n\n"
            f"{ep.get('description', '')}\n\n"
            f"CAPÍTULOS\n{chap_txt}\n\n"
            "FUENTES\n" + "\n".join(f"• {s}" for s in ep.get("sources", [])) + "\n\n"
            "Las simulaciones son ilustrativas y no incluyen dividendos, impuestos, inflación ni costos de transacción. "
            "Las ilustraciones y esquemas están rotulados como tales. Este video no es una recomendación de compra o venta.\n\n"
            "#MundoDinero #Inversiones #Finanzas")
    (out / "youtube_description.txt").write_text(desc, encoding="utf-8")
    meta = {"title": ep["title"], "description": desc, "tags": ep.get("tags", []), "categoryId": "27",
            "defaultLanguage": "es", "defaultAudioLanguage": "es-419",
            "chapters": [{"start": s, "title": n} for s, n in chaps], "duration": total}
    (out / "youtube.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "guion.txt").write_text("\n\n".join(tl["sc"]["text"] for tl in timeline), encoding="utf-8")
    # registro de producción (desglose de planos)
    with open(out / "produccion_planos.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["id", "capitulo", "inicio", "fin", "duracion", "tipo_visual", "detalle", "narracion", "fuente",
                     "estado_verificacion"])
        for tl in timeline:
            sc, v = tl["sc"], tl["sc"]["visual"]
            src = ""
            if v["type"] == "chart":
                key = v.get("series") or next(k for k in ep["data"] if not k.endswith("_source") and k != "note")
                src = ep["data"].get(key + "_source", "")
            elif v["type"] in ("image", "product") and v.get("credit"):
                src = v["credit"]
            elif v["type"] in ("diagram", "product", "location", "people"):
                src = "Gráfico original MUNDO DINERO"
            wr.writerow([sc["id"], ep["chapters"][sc["chapter"]], f"{tl['start']:.2f}", f"{tl['start'] + tl['dur']:.2f}",
                         f"{tl['dur']:.2f}", v["type"], v.get("kind") or v.get("headline") or v.get("text") or v.get("name") or "",
                         sc["text"], src, sc.get("verification", "ver verificacion.md")])
    # miniatura
    from .thumbnail import make_thumbnail
    make_thumbnail(ep, out / "thumbnail.jpg")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def quality_control(final, ep, timeline, a):
    info = probe(final)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    au = [s for s in info["streams"] if s["codec_type"] == "audio"]
    dur = float(info["format"]["duration"])
    checks = {}
    want = (960, 540) if a.preview else (1920, 1080)
    checks["resolución"] = {"ok": (v["width"], v["height"]) == want, "detail": f"{v['width']}x{v['height']}"}
    checks["códec de video"] = {"ok": v["codec_name"] == "h264", "detail": v["codec_name"]}
    checks["audio AAC estéreo"] = {"ok": bool(au) and au[0]["codec_name"] == "aac" and au[0]["channels"] == 2,
                                   "detail": f"{au[0]['codec_name']} {au[0]['channels']}ch" if au else "sin audio"}
    lo, hi = ep.get("target_duration", [290, 315])
    checks["duración"] = {"ok": lo <= dur <= hi, "detail": f"{dur:.1f}s (objetivo {lo}–{hi}s)"}
    checks["cantidad de planos"] = {"ok": 45 <= len(timeline) <= 60, "detail": str(len(timeline))}
    # cuadros negros accidentales (fuera de los fundidos de capítulo)
    r = subprocess.run(["ffmpeg", "-i", str(final), "-vf", "blackdetect=d=0.5:pix_th=0.05", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    blacks = [l for l in r.stderr.splitlines() if "black_start" in l]
    checks["cuadros negros > 0,5s"] = {"ok": not blacks, "detail": f"{len(blacks)} tramos"}
    # silencios accidentales en la mezcla
    r = subprocess.run(["ffmpeg", "-i", str(final), "-af", "silencedetect=n=-45dB:d=2.5", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True)
    sil = [l for l in r.stderr.splitlines() if "silence_start" in l]
    checks["silencios > 2,5s"] = {"ok": not sil, "detail": f"{len(sil)} tramos"}
    # saturación
    r = subprocess.run(["ffmpeg", "-i", str(final), "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary"):]
    integ = next((l.split(":")[1].strip() for l in tail.splitlines() if l.strip().startswith("I:")), "?")
    peak = next((l.split(":")[1].strip() for l in tail.splitlines() if l.strip().startswith("Peak:")), "?")
    try:
        ok_peak = float(peak.split()[0]) <= -0.9
    except ValueError:
        ok_peak = False
    checks["loudness / saturación"] = {"ok": ok_peak, "detail": f"integrado {integ}, pico real {peak}"}
    checks["narración completa"] = {"ok": all(tl["voice_dur"] > 0.3 for tl in timeline),
                                    "detail": "todas las escenas tienen audio de voz"}
    checks["voz"] = {"ok": a.tts == "edge",
                     "detail": "es-AR-TomasNeural (rioplatense)" if a.tts == "edge" else
                     "PIPER DE PRUEBA — voz española no rioplatense; regenerar con --tts edge antes de publicar"}
    return {"file": str(final), "duration": dur, "passed": all(c["ok"] for c in checks.values()), "checks": checks,
            "not_automated": ["Exactitud editorial de cada dato (ver verificacion.md)",
                              "Pronunciación de nombres propios (escuchar)",
                              "Derechos de imágenes de archivo aportadas en assets/"]}


if __name__ == "__main__":
    sys.exit(main())
