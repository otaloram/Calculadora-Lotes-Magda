"""Música original procedural (sin licencias de terceros).

Cada capítulo tiene un estado de ánimo; los cambios se funden suavemente.
La pista se mezcla muy por debajo de la voz y además se atenúa con sidechain.
"""
import numpy as np

SR = 48000
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def hz(name: str) -> float:
    n, o = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE[n] + 12 * (o - 4) - 9) / 12)


MOODS = {
    # apertura y desplomes: tensión, poca instrumentación, pulso grave
    "tension": dict(chords=[["A2", "E3", "C4"], ["F2", "C3", "A3"], ["A2", "E3", "B3"], ["E2", "B2", "G#3"]],
                    pad=0.55, pulse=0.35, arp=0.0, bright=0.2),
    # fundación: cálido y discreto
    "warm": dict(chords=[["F2", "C3", "E4", "A3"], ["C3", "G3", "E4"], ["A2", "E3", "C4"], ["G2", "D3", "B3"]],
                 pad=0.6, pulse=0.0, arp=0.12, bright=0.35),
    # fracaso: casi silencio para que pese la voz
    "sparse": dict(chords=[["D2", "A2"], ["A#1", "F2"]], pad=0.35, pulse=0.15, arp=0.0, bright=0.1),
    # recuperación: progresión moderada
    "progress": dict(chords=[["C3", "G3", "E4"], ["G2", "D3", "B3"], ["A2", "E3", "C4"], ["F2", "C3", "A3"]],
                     pad=0.5, pulse=0.0, arp=0.25, bright=0.5),
    # CUDA e IA: atmósfera tecnológica contemporánea
    "tech": dict(chords=[["D3", "A3", "F4"], ["A#2", "F3", "D4"], ["C3", "G3", "E4"], ["A2", "E3", "C4"]],
                 pad=0.4, pulse=0.2, arp=0.35, bright=0.55),
    # reflexión y cierre
    "reflect": dict(chords=[["A2", "E3", "C4"], ["F2", "C3", "A3"], ["C3", "G3", "E4"], ["G2", "D3", "B3"]],
                    pad=0.5, pulse=0.0, arp=0.08, bright=0.3),
}


def _pad(freqs, n, bright):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            ph = np.random.uniform(0, 2 * np.pi)
            out += np.sin(2 * np.pi * ff * t + ph) + bright * 0.35 * np.sin(4 * np.pi * ff * t + ph)
    return out / (len(freqs) * 3)


def _env(n, att, rel):
    e = np.ones(n)
    a, r = min(int(att * SR), n // 2), min(int(rel * SR), n // 2)
    if a < 2 or r < 2:
        return e
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] = np.minimum(e[-r:], np.linspace(1, 0, r) ** 2)
    return e


def render_section(mood: str, dur: float, seed: int = 0) -> np.ndarray:
    np.random.seed(seed)
    m = MOODS[mood]
    n = int(dur * SR)
    out = np.zeros(n)
    chord_len = 6.0
    i, k = 0, 0
    while i < n:
        L = min(int((chord_len + 2.0) * SR), n - i)
        ch = [hz(x) for x in m["chords"][k % len(m["chords"])]]
        seg = _pad(ch, L, m["bright"]) * _env(L, 1.8, 2.2) * m["pad"]
        out[i:i + L] += seg
        if m["arp"] > 0:      # arpegio pulsado y apagado
            step = int(SR * 60 / 84 / 2)
            for j, s in enumerate(range(0, L - step, step)):
                f = ch[j % len(ch)] * 2
                tt = np.arange(step * 2) / SR
                pl = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 7) * m["arp"]
                e = min(len(pl), n - (i + s))
                out[i + s:i + s + e] += pl[:e]
        if m["pulse"] > 0:    # latido grave
            beat = int(SR * 60 / 62)
            for s in range(0, L - beat, beat):
                tt = np.arange(int(0.5 * SR)) / SR
                kk = np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 9) * m["pulse"]
                e = min(len(kk), n - (i + s))
                out[i + s:i + s + e] += kk[:e]
        i += int(chord_len * SR)
        k += 1
    return out


def render_score(sections, total: float, out_path):
    """sections: lista de (inicio, fin, mood). Escribe WAV estéreo 48 kHz."""
    import wave
    n = int(total * SR)
    mix = np.zeros(n)
    xf = 2.5
    for idx, (a, b, mood) in enumerate(sections):
        a2, b2 = max(0, a - xf / 2), min(total, b + xf / 2)
        seg = render_section(mood, b2 - a2, seed=idx)
        seg *= _env(len(seg), xf, xf if b2 < total else 3.5)
        s = int(a2 * SR)
        mix[s:s + len(seg)] += seg[: n - s]
    # reverberación barata: ecos difusos
    wet = np.zeros_like(mix)
    for d, g in ((0.071, 0.35), (0.113, 0.28), (0.167, 0.22), (0.241, 0.16), (0.337, 0.11)):
        k = int(d * SR)
        wet[k:] += mix[:-k] * g
    mix = mix + wet
    mix /= max(1e-6, np.abs(mix).max())
    mix *= 0.8
    # leve estéreo por retardo
    dl = int(0.012 * SR)
    left = mix
    right = np.concatenate([np.zeros(dl), mix[:-dl]])
    st = np.stack([left, right], axis=1)
    pcm = (st * 32767).astype("<i2")
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
