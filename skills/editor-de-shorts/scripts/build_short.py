"""Monta um YouTube Short vertical: narracao + musica sintetizada + imagens com Ken Burns + legendas karaoke.
Uso: python build_short.py projeto.json saida.mp4 [voz.wav]
  - sem voz.wav: gera narracao com edge-tts (voz e velocidade do projeto)
  - com voz.wav: usa o audio pronto; precisa de words.json (gerado por transcrever.py) na mesma pasta do audio
"""
import asyncio, os, subprocess, sys, math, json
import numpy as np
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROJ_FILE = os.path.abspath(sys.argv[1]); PROJ = json.load(open(PROJ_FILE, encoding="utf-8"))
HERE = os.path.dirname(PROJ_FILE)
IMG = os.path.join(HERE, PROJ.get("imagens", "imgs"))
TMP = os.path.join(HERE, "tmp"); os.makedirs(TMP, exist_ok=True)
OUT = sys.argv[2]
W, H, FPS, SR = 1080, 1920, 30, 44100
VOICE, RATE = PROJ.get("voz_sintetica", "pt-BR-AntonioNeural"), PROJ.get("velocidade", "+22%")

SCENES = [(c["imagem"], c["texto"], c["etiqueta"]) for c in PROJ["cenas"]]  # (imagem, texto falado, etiqueta no topo)
# tomadas extras dentro de cada cena: (imagem, palavra do roteiro onde a imagem entra; None = inicio da cena)
SHOTS = {int(k): [tuple(x) for x in v] for k, v in PROJ.get("tomadas", {}).items()}
GAP = 0.08
# animacoes opcionais: modulo do projeto com frame(nome, lt, dur, t) -> PIL RGB WxH e, opcional, sfx(nome, sr) -> np.array
ANIM = None
if PROJ.get("animacoes"):
    import importlib.util
    _sp = importlib.util.spec_from_file_location("animacoes", os.path.join(HERE, PROJ["animacoes"]))
    ANIM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(ANIM)
TAIL = 1.3

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

# ---------- 1. Narracao ----------
async def tts(i, text):
    mp3 = os.path.join(TMP, f"v{i:02d}.mp3"); words = []
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    with open(mp3, "wb") as f:
        async for c in comm.stream():
            if c["type"] == "audio": f.write(c["data"])
            elif c["type"] == "WordBoundary":
                words.append((c["offset"] / 1e7, (c["offset"] + c["duration"]) / 1e7, c["text"]))
    return mp3, words

async def all_tts():
    return [await tts(i, s[1]) for i, s in enumerate(SCENES)]

VOICE_FILE = sys.argv[3] if len(sys.argv) > 3 else None  # audio pronto (ex.: AI Studio) + words.json do Whisper

def norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if c.isalnum())

def align_external(path):
    """Usa o audio externo: casa as palavras do roteiro com os tempos do Whisper."""
    import difflib
    wh = json.load(open(os.path.join(os.path.dirname(os.path.abspath(path)), "words.json"), encoding="utf-8"))
    wsub = []  # subtokens do whisper com tempo
    for a0, a1, w in wh:
        parts = [norm(p) for p in w.replace("-", " ").split() if norm(p)]
        for k, p in enumerate(parts):
            d = (a1 - a0) / len(parts); wsub.append((p, a0 + k * d, a0 + (k + 1) * d))
    sw, ssub = [], []  # palavras do roteiro e seus subtokens
    for si, s in enumerate(SCENES):
        for w in s[1].split():
            idx = []
            for p in w.replace("-", " ").split():
                if norm(p): idx.append(len(ssub)); ssub.append(norm(p))
            if idx: sw.append((si, w, idx))
    tm = [None] * len(ssub)
    sm = difflib.SequenceMatcher(None, ssub, [x[0] for x in wsub], autojunk=False)
    for a, b, size in sm.get_matching_blocks():
        for k in range(size): tm[a + k] = (wsub[b + k][1], wsub[b + k][2])
    known = [i for i, x in enumerate(tm) if x]
    for i in range(len(tm)):  # interpola o que nao casou
        if tm[i]: continue
        lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
        t0 = tm[lo][1] if lo is not None else 0.0; t1 = tm[hi][0] if hi is not None else t0 + 0.3
        n0 = lo if lo is not None else -1; n1 = hi if hi is not None else len(tm)
        f0 = (i - n0) / (n1 - n0); f1 = (i + 1 - n0) / (n1 - n0)
        tm[i] = (t0 + (t1 - t0) * f0, t0 + (t1 - t0) * f1)
    print(f"alinhamento: {len(known)}/{len(ssub)} palavras casadas")
    return [(si, tm[idx[0]][0], tm[idx[-1]][1], w) for si, w, idx in sw]

if VOICE_FILE:
    voice = decode(VOICE_FILE)
    aw = align_external(VOICE_FILE)
    starts = [min(a0 for si, a0, a1, w in aw if si == k) for k in range(len(SCENES))]
    starts = [0.0] + [max(0.0, s - 0.12) for s in starts[1:]]
    end_speech = max(a1 for _, _, a1, _ in aw)
    TOTAL = max(len(voice) / SR, end_speech + TAIL)
    voice = np.concatenate([voice, np.zeros(int(TOTAL * SR) - len(voice), np.float32)]); voice *= 0.9 / np.max(np.abs(voice))
    scenes = []
    for k in range(len(SCENES)):
        e = starts[k + 1] if k + 1 < len(SCENES) else TOTAL
        scenes.append(dict(img=SCENES[k][0], tag=SCENES[k][2], start=starts[k], dur=e - starts[k],
                           words=[(a0, a1, w) for si, a0, a1, w in aw if si == k]))
    res = []
else:
    print("TTS..."); res = asyncio.run(all_tts())
    voice_parts, scenes, t = [], [], 0.0
for i, (mp3, words) in enumerate(res):
    a = decode(mp3)
    nz = np.nonzero(np.abs(a) > 0.01)[0]  # corta silencio do comeco/fim
    s0 = max(0, nz[0] - int(0.03 * SR)); s1 = min(len(a), nz[-1] + int(0.06 * SR))
    a = a[s0:s1]; off = s0 / SR
    dur = len(a) / SR + (TAIL if i == len(res) - 1 else GAP)
    voice_parts.append(np.concatenate([a, np.zeros(int(round(dur * SR)) - len(a), np.float32)]))
    scenes.append(dict(img=SCENES[i][0], tag=SCENES[i][2], start=t, dur=dur,
                       words=[(t + a0 - off, t + a1 - off, w) for a0, a1, w in words]))
    t += dur
if not VOICE_FILE:
    TOTAL = t
    voice = np.concatenate(voice_parts); voice *= 0.9 / np.max(np.abs(voice))
print(f"duracao total {TOTAL:.1f}s")

shots = []
for k, s in enumerate(scenes):
    pos, starts = 0, []
    for img, anchor in SHOTS.get(k, [(s["img"], None)]):
        if anchor is None: starts.append((img, s["start"])); continue
        j = next((j for j in range(pos, len(s["words"])) if norm(s["words"][j][2]) == norm(anchor)), None)
        if j is None:
            sys.exit(f"tomada {img!r} na cena {k}: palavra {anchor!r} nao achada em {[w[2] for w in s['words'][pos:]]}")
        starts.append((img, s["words"][j][0] - 0.05)); pos = j + 1
    for m, (img, st) in enumerate(starts):
        en = starts[m + 1][1] if m + 1 < len(starts) else s["start"] + s["dur"]
        shots.append(dict(img=img, tag=s["tag"], start=st, dur=en - st, scene_cut=(m == 0)))
print(f"{len(shots)} tomadas")

# ---------- 2. Musica (sintetizada, sem direitos autorais) ----------
print("musica...")
rng = np.random.default_rng(7)
n = len(voice); tt = np.arange(n) / SR
bpm = 104; beat = 60 / bpm; bar = 4 * beat
def note(m): return 440 * 2 ** ((m - 69) / 12)
chords = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]  # Am F C G
music = np.zeros(n, np.float32)
def add(sig, at):
    i0 = int(at * SR)
    if i0 >= n: return
    seg = sig[: n - i0]; music[i0:i0 + len(seg)] += seg
nb = int(TOTAL / bar) + 2
for b in range(nb):
    ch = chords[b % 4]; t0 = b * bar
    L = int(bar * SR); x = np.arange(L) / SR
    env = np.minimum(1, x / 0.3) * np.minimum(1, (bar - x) / 0.4)
    pad = sum(np.sin(2 * np.pi * note(m) * x) + 0.25 * np.sin(2 * np.pi * note(m) * 2.01 * x) for m in ch)
    add((0.05 * env * pad).astype(np.float32), t0)
    for k in range(8):  # arpejo "marimba" nas colcheias
        m = ch[[0, 1, 2, 1, 0, 2, 1, 2][k]] + 12
        Lp = int(0.35 * SR); xp = np.arange(Lp) / SR
        pl = np.sin(2 * np.pi * note(m) * xp) * np.exp(-xp * 14) + 0.3 * np.sin(2 * np.pi * note(m) * 4 * xp) * np.exp(-xp * 30)
        add((0.09 * pl).astype(np.float32), t0 + k * beat / 2)
    for k in range(4):
        Lk = int(0.3 * SR); xk = np.arange(Lk) / SR  # bumbo
        f = 45 + 80 * np.exp(-xk * 30); ph = 2 * np.pi * np.cumsum(f) / SR
        add((0.35 * np.sin(ph) * np.exp(-xk * 12)).astype(np.float32), t0 + k * beat)
        if k % 2 == 0:  # baixo
            Lb = int(beat * 1.8 * SR); xb = np.arange(Lb) / SR
            add((0.16 * np.sin(2 * np.pi * note(ch[0] - 24) * xb) * np.exp(-xb * 2.5)).astype(np.float32), t0 + k * beat)
        Lh = int(0.06 * SR); hn = np.diff(rng.standard_normal(Lh + 1)).astype(np.float32)  # chimbal
        add(0.035 * hn * np.exp(-np.arange(Lh) / SR * 60), t0 + k * beat + beat / 2)
        if k in (1, 3):  # palma
            Lc = int(0.12 * SR); cn = rng.standard_normal(Lc).astype(np.float32)
            add(0.05 * cn * np.exp(-np.arange(Lc) / SR * 35), t0 + k * beat)
fade = np.minimum(1, np.minimum(tt / 0.5, (TOTAL - tt) / 1.2)).clip(0, 1)
music = music / np.max(np.abs(music)) * fade

# ducking: musica baixa quando ha voz
envv = np.abs(voice); k = int(0.15 * SR)
envv = np.convolve(envv, np.ones(k) / k, mode="same")
duck = np.where(envv > 0.02, 0.10, 0.16)
duck = np.convolve(duck, np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")

# whoosh nas transicoes
fx = np.zeros(n, np.float32)
for s in shots[1:]:
    L = int(0.4 * SR); nz = rng.standard_normal(L).astype(np.float32); y = np.zeros(L, np.float32); acc = 0.0
    for j in range(L):
        p = j / L; a = 0.02 + 0.5 * math.sin(math.pi * p) ** 2
        acc += a * (nz[j] - acc); y[j] = acc
    y *= np.sin(np.pi * np.arange(L) / L) ** 2
    i0 = int((s["start"] - 0.2) * SR); seg = y[: n - i0]
    fx[i0:i0 + len(seg)] += (0.5 if s["scene_cut"] else 0.25) * seg / np.max(np.abs(y))

# efeitos sonoros das animacoes (ex.: sino de round, explosao)
if ANIM is not None and hasattr(ANIM, "sfx"):
    for s in shots:
        if not s["img"].startswith("@"): continue
        y = ANIM.sfx(s["img"][1:], SR, s["dur"])
        if y is None: continue
        i0 = int(s["start"] * SR); seg = y[: n - i0]; fx[i0:i0 + len(seg)] += seg.astype(np.float32) / 0.18

mix = voice + music * duck + 0.18 * fx
mix = (mix / max(1.0, np.max(np.abs(mix)) / 0.97)).astype(np.float32)
wav = os.path.join(TMP, "mix.wav")
import wave
with wave.open(wav, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------- 3. Video ----------
print("video...")
FONT = "C:/Windows/Fonts/segoeuib.ttf"
fcap = ImageFont.truetype(FONT, 96); ftag = ImageFont.truetype(FONT, 58)
YEL = (255, 222, 0); WHITE = (255, 255, 255)

# ponto de interesse (fracao x, y) para imagens cujo assunto nao esta no centro
FOCUS = {k: tuple(v) for k, v in PROJ.get("foco", {}).items()}

def cover(im, w, h, focus=(0.5, 0.5)):
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r + 1), int(im.height * r + 1)), Image.LANCZOS)
    x = int(min(max(focus[0] * im.width - w / 2, 0), im.width - w))
    y = int(min(max(focus[1] * im.height - h / 2, 0), im.height - h))
    return im.crop((x, y, x + w, y + h))

def prep(code):
    im = Image.open(os.path.join(IMG, code + ".jpg")).convert("RGB")
    bg = cover(im, W // 4, H // 4).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    bg = Image.eval(bg, lambda v: int(v * 0.45))
    portrait = im.width / im.height < 0.8
    if portrait: fg_box = (W, H)  # tela cheia
    else: fg_box = (W, int(W * 1.1))  # bloco central quase quadrado
    src = cover(im, int(fg_box[0] * 1.45), int(fg_box[1] * 1.45), FOCUS.get(code, (0.5, 0.5)))
    return dict(bg=bg, src=src, box=fg_box, portrait=portrait)

cache = {}
def ease(x): return 1 - (1 - x) ** 3

# legendas: grupos de ate 3 palavras
groups = []
for s in scenes:
    ws = s["words"]; cur = []
    for w in ws:
        cur.append(w)
        if len(cur) == 3 or w[2].endswith((".", ",", "?", "!", ":")): groups.append(cur); cur = []
    if cur: groups.append(cur)

cap_cache = {}
def caption_img(gi, hi):
    key = (gi, hi)
    if key in cap_cache: return cap_cache[key]
    ws = [w[2].upper().strip(".,!?:") for w in groups[gi]]
    sp = fcap.getlength(" "); lens = [fcap.getlength(w) for w in ws]
    tw = int(sum(lens) + sp * (len(ws) - 1)) + 40
    img = Image.new("RGBA", (tw, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(img); x = 20
    for j, w in enumerate(ws):
        d.text((x, 10), w, font=fcap, fill=YEL if j == hi else WHITE, stroke_width=9, stroke_fill=(0, 0, 0))
        x += lens[j] + sp
    if tw > W - 60: img = img.resize((W - 60, int(150 * (W - 60) / tw)), Image.LANCZOS)
    cap_cache[key] = img; return img

tag_cache = {}
def tag_img(text):
    if text in tag_cache: return tag_cache[text]
    tw = int(ftag.getlength(text)) + 60
    img = Image.new("RGBA", (tw, 100), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, tw - 1, 99), 24, fill=(255, 222, 0, 245))
    d.text((30, 12), text, font=ftag, fill=(15, 15, 15))
    tag_cache[text] = img; return img

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-i", wav, "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "21", "-b:v", "10M",
                        "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
nf = int(TOTAL * FPS)
for f in range(nf):
    t = f / FPS
    si = max(i for i, s in enumerate(shots) if s["start"] <= t + 1e-6); s = shots[si]
    lt = t - s["start"]; p = lt / s["dur"]
    if s["img"].startswith("@"):
        frame = ANIM.frame(s["img"][1:], lt, s["dur"], t); P = dict(portrait=True)
    else:
        frame = None
        if s["img"] not in cache: cache[s["img"]] = prep(s["img"])
        P = cache[s["img"]]
    if frame is None:  # foto com Ken Burns; sub-corte no meio de tomadas longas (jump cut)
        half = s["dur"] > 3.6 and p >= 0.5
        pp = (p - 0.5) * 2 if half else (p * 2 if s["dur"] > 3.6 else p)
        z0, z1 = ((1.45, 1.2) if half else (1.15, 1.35)) if si % 2 == 0 else ((1.2, 1.45) if half else (1.35, 1.12))
        z = z0 + (z1 - z0) * pp
        punch = 1 + 0.12 * (1 - ease(min(1, lt / 0.25)))  # zoom-soco na entrada da cena
        z = z / punch if si else z
        sw, sh = P["src"].size; bw, bh = P["box"]
        cw, ch = sw / z, sh / z
        dx = (0.08 if half else -0.06) * sw * (pp - 0.5) * (1 if si % 2 else -1)
        cx, cy = sw / 2 + dx, sh / 2
        cx = min(max(cx, cw / 2), sw - cw / 2); cy = min(max(cy, ch / 2), sh - ch / 2)
        fg = P["src"].resize((bw, bh), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
        frame = P["bg"].copy()
        fy = 0 if P["portrait"] else 300
        frame.paste(fg, (0, fy))
        if not P["portrait"]:
            d = ImageDraw.Draw(frame); d.rectangle((0, fy - 6, W, fy - 1), fill=YEL); d.rectangle((0, fy + bh, W, fy + bh + 5), fill=YEL)
    # etiqueta no topo
    tg = tag_img(s["tag"]); ty = 150 if P["portrait"] else 170
    k = ease(min(1, lt / 0.2)); tx = int((W - tg.width) / 2 - (1 - k) * 300) if si == 0 or shots[si - 1]["tag"] != s["tag"] else (W - tg.width) // 2
    frame.paste(tg, (tx, ty), tg)
    # legenda karaoke
    for gi, g in enumerate(groups):
        if g[0][0] - 0.05 <= t < (groups[gi + 1][0][0] - 0.05 if gi + 1 < len(groups) else TOTAL):
            hi = max([j for j, w in enumerate(g) if w[0] <= t + 0.02] or [0])
            ci = caption_img(gi, hi); ga = t - (g[0][0] - 0.05)
            sc = 0.8 + 0.2 * ease(min(1, ga / 0.12))
            if sc < 1: ci = ci.resize((int(ci.width * sc), int(ci.height * sc)), Image.BILINEAR)
            frame.paste(ci, ((W - ci.width) // 2, 1620 - ci.height // 2), ci)
            break
    # flash branco no corte
    if si and lt < 0.07: frame = Image.blend(frame, Image.new("RGB", (W, H), WHITE), 0.55 * (1 - lt / 0.07))
    # barra de progresso
    d = ImageDraw.Draw(frame); d.rectangle((0, 0, int(W * t / TOTAL), 10), fill=YEL)
    enc.stdin.write(frame.tobytes())
    if f % 300 == 0: print(f"  frame {f}/{nf}")
enc.stdin.close(); enc.wait()
json.dump([dict(start=s["start"], dur=s["dur"], img=s["img"]) for s in shots], open(os.path.join(TMP, "timeline.json"), "w"), indent=1)
print("OK", OUT, f"{TOTAL:.1f}s")
