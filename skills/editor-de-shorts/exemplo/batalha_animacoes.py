"""Animacoes desenhadas por codigo para o video Tardigrado vs Agua-viva.
frame(nome, lt, dur, t) -> PIL RGB 1080x1920   |   sfx(nome, sr) -> np.array (ou None)
Area livre: y 280..1480 (etiqueta em cima, legenda em y=1620)."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FBL = "C:/Windows/Fonts/seguibl.ttf"
YEL, WHITE, BLACK = (255, 222, 0), (255, 255, 255), (0, 0, 0)
BODY, OUT, SEG = (232, 172, 112), (110, 62, 34), (196, 132, 80)
BELL, BELL_OUT, TENT, STOM = (236, 226, 255, 205), (150, 120, 205, 255), (232, 214, 250, 230), (226, 56, 46)
ICE = (150, 210, 255)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):  # ease-out com passada (efeito "slam")
    x = clamp(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def seg(p, a, b): return clamp((p - a) / (b - a))
def mixc(c1, c2, a): return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(len(c1)))

_font = {}
def font(sz):
    if sz not in _font: _font[sz] = ImageFont.truetype(FBL, sz)
    return _font[sz]

def txt(fr, s, size, xy, fill=WHITE, stroke=10, sc=1.0, rot=0.0, sfill=BLACK, alpha=1.0):
    if sc <= 0.01 or alpha <= 0.01: return
    f = font(size); b = f.getbbox(s, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 8, b[3] - b[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - b[0], 4 - b[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    fr.paste(im, (int(xy[0] - im.width / 2), int(xy[1] - im.height / 2)), im)

def put(fr, sp, cx, cy, rot=0.0, alpha=1.0, flip=False):
    if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    if rot: sp = sp.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1: sp = sp.copy(); sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
    fr.paste(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)), sp)

def shake(fr, amt, t):
    if amt < 0.5: return fr
    dx = int(amt * math.sin(t * 91)); dy = int(amt * math.cos(t * 77))
    out = Image.new("RGB", (W, H), BLACK); out.paste(fr, (dx, dy)); return out

# ---------------- fundos ----------------
_bg = {}
def grad(c1, c2, key=None):
    key = key or (c1, c2)
    if key not in _bg:
        a = np.linspace(0, 1, H)[:, None, None]
        arr = (np.array(c1)[None, None] * (1 - a) + np.array(c2)[None, None] * a) * np.ones((1, W, 1))
        _bg[key] = Image.fromarray(arr.astype(np.uint8), "RGB")
    return _bg[key].copy()

def sea(t):
    fr = grad((8, 40, 90), (4, 120, 150))
    d = ImageDraw.Draw(fr); rnd = random.Random(3)
    for i in range(26):
        x = rnd.uniform(0, W); sp = rnd.uniform(60, 160); r = rnd.uniform(5, 16)
        y = H - ((t * sp + rnd.uniform(0, H)) % (H + 100))
        x += 14 * math.sin(t * 2 + i)
        d.ellipse((x - r, y - r, x + r, y + r), outline=(170, 230, 255), width=3)
    for i in range(5):  # raios de luz
        x = 120 + i * 220 + 40 * math.sin(t * 0.6 + i)
        d.polygon([(x - 30, 0), (x + 30, 0), (x + 160, H), (x + 40, H)], fill=mixc((8, 40, 90), (60, 150, 190), 0.25))
    return fr

def space(t, seed=5):
    fr = grad((2, 2, 12), (14, 10, 40), key="space")
    d = ImageDraw.Draw(fr); rnd = random.Random(seed)
    for i in range(160):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H); r = rnd.choice([1, 1, 2, 2, 3])
        b = int(160 + 95 * (0.5 + 0.5 * math.sin(t * rnd.uniform(1, 4) + i)))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(b, b, b))
    return fr

def burst(t, c1, c2, cx=W / 2, cy=880, n=18, speed=0.4):
    fr = Image.new("RGB", (W, H), c1); d = ImageDraw.Draw(fr); R = 2400
    for i in range(n):
        if i % 2: continue
        a0 = (i / n) * 2 * math.pi + t * speed; a1 = a0 + 2 * math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c2)
    return fr

def confetti(fr, lt, n=70, seed=1, y0=-50):
    d = ImageDraw.Draw(fr); rnd = random.Random(seed)
    cols = [(255, 222, 0), (255, 80, 80), (80, 200, 255), (120, 255, 120), (255, 140, 230)]
    for i in range(n):
        x = rnd.uniform(0, W) + 40 * math.sin(lt * 3 + i); vy = rnd.uniform(300, 700)
        y = y0 + (lt * vy + rnd.uniform(-900, 0))
        if y < -20 or y > H: continue
        a = lt * 6 + i; s = 14
        pts = [(x + s * math.cos(a + k * math.pi / 2) * (1 if k % 2 else 0.5), y + s * math.sin(a + k * math.pi / 2)) for k in range(4)]
        d.polygon(pts, fill=cols[i % 5])

def floor(fr, y, c=(60, 40, 30)):
    ImageDraw.Draw(fr).rectangle((0, y, W, H), fill=c)

# ---------------- personagens ----------------
def tardi(t, s=1.0, walk=0.0, curl=0.0, eyes="open", tint=None, tint_a=0.0, glasses=False, look=1.0, mustache=False):
    k = 2 * s; im = Image.new("RGBA", (int(600 * k), int(460 * k)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = mixc(BODY, tint, tint_a) if tint else BODY
    out = mixc(OUT, tint, tint_a * 0.5) if tint else OUT
    sgc = mixc(SEG, tint, tint_a) if tint else SEG
    dark = mixc(col, (0, 0, 0), 0.22)
    def E(cx, cy, rx, ry, fill, w=0, o=None):
        d.ellipse(((cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k), fill=fill, outline=o or out, width=int(w * k))
    c = clamp(curl)
    cx, cy = 290 + 20 * c, 240; rx, ry = 215 * (1 - 0.42 * c), 112 * (1 + 0.22 * c)
    ls = 1 - c
    if ls > 0.05:
        for side, (off, cc) in enumerate([((26, -14), dark), ((0, 0), col)]):
            for i, x in enumerate([150, 235, 320, 400]):
                ph = t * 11 + i * 1.7 + side * 3.1
                lift = walk * max(0, math.sin(ph)) * 16; sw = walk * math.cos(ph) * 12
                lx = cx + (x - 290) * (1 - 0.42 * c) + off[0] + sw; ly = cy + ry * 0.78 + 28 * ls - lift + off[1]
                E(lx, ly, 32 * ls, 48 * ls, cc, 6)
                for j in (-1, 0, 1):
                    d.line(((lx + j * 12 * ls) * k, (ly + 42 * ls) * k, (lx + j * 16 * ls) * k, (ly + 60 * ls) * k), fill=out, width=int(5 * k))
    E(cx, cy, rx, ry, col, 7)
    E(cx - 30, cy - ry * 0.45, rx * 0.55, ry * 0.22, mixc(col, WHITE, 0.25))
    for j in range(1, 5):
        x = cx - rx + j * 2 * rx / 5.4
        d.arc(((x - 26) * k, (cy - ry * 0.88) * k, (x + 26) * k, (cy + ry * 0.88) * k), -75, 75, fill=sgc, width=int(6 * k))
    hr = 98 * (1 - 0.45 * c); hx = cx + rx * 0.8 - 10 * c; hy = cy - 18
    E(hx, hy, hr, hr * 0.95, col, 7)
    if c < 0.85:
        sx, sy = hx + hr * 0.86, hy + 22
        E(sx, sy, 27 * ls, 23 * ls, mixc(col, (180, 90, 60), 0.4), 5)
        E(sx + 5, sy, 10 * ls, 9 * ls, (90, 35, 25))
    E(hx + 22, hy + 30, 17, 10, mixc(col, (255, 110, 120), 0.55))
    if c > 0.6 and eyes == "open": eyes = "sleep"
    if eyes == "open" and (t % 3.3) < 0.11: eyes = "sleep"
    er = 27 * (1 - 0.35 * c)
    for ex, ey in ((hx - 22, hy - 28), (hx + 40, hy - 26)):
        if eyes in ("open", "scared"):
            E(ex, ey, er, er * 1.1, WHITE, 5)
            pr = 8 if eyes == "scared" else 13
            E(ex + 6 * look, ey + 3, pr, pr * 1.1, BLACK)
            E(ex + 6 * look + 4, ey - 4, 4, 4, WHITE)
        elif eyes == "sleep":
            d.arc(((ex - er) * k, (ey - er * 0.6) * k, (ex + er) * k, (ey + er * 0.8) * k), 10, 170, fill=out, width=int(6 * k))
        elif eyes == "happy":
            d.arc(((ex - er) * k, (ey - er * 0.4) * k, (ex + er) * k, (ey + er * 1.2) * k), 200, 340, fill=out, width=int(7 * k))
        elif eyes == "dizzy":
            for a in (45, 135):
                ca, sa = math.cos(math.radians(a)) * er, math.sin(math.radians(a)) * er
                d.line(((ex - ca) * k, (ey - sa) * k, (ex + ca) * k, (ey + sa) * k), fill=out, width=int(7 * k))
    if glasses:
        for ex, ey in ((hx - 22, hy - 28), (hx + 40, hy - 26)):
            d.rounded_rectangle(((ex - 34) * k, (ey - 22) * k, (ex + 34) * k, (ey + 24) * k), int(14 * k), fill=(15, 15, 20))
            d.line(((ex - 20) * k, (ey - 10) * k, (ex - 6) * k, (ey - 16) * k), fill=(120, 120, 140), width=int(4 * k))
        d.line(((hx + 10) * k, (hy - 30) * k, (hx + 8) * k, (hy - 30) * k), fill=(15, 15, 20), width=int(8 * k))
    if mustache:
        d.arc(((hx + 30) * k, (hy + 30) * k, (hx + 110) * k, (hy + 70) * k), 180, 360, fill=(235, 235, 235), width=int(12 * k))
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)

def medusa(t, s=1.0, eyes="open", tint=None, tint_a=0.0, melt=0.0, tent=1.0, pulse=1.0, mouth="smile"):
    k = 2 * s; im = Image.new("RGBA", (int(520 * k), int(660 * k)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bell = mixc(BELL, tint + (215,), tint_a) if tint else BELL
    bo = mixc(BELL_OUT, tint + (255,), tint_a * 0.6) if tint else BELL_OUT
    tc = mixc(TENT, tint + (230,), tint_a) if tint else TENT
    ps = pulse * math.sin(t * 3.4)
    cx = 260; rim = 270 + 150 * melt; a = 172 * (1 + 0.06 * ps) * (1 + 0.55 * melt); h = 215 * (1 - 0.08 * ps) * (1 - 0.7 * melt)
    L = 300 * tent * (1 - melt)
    if L > 5:
        n = 17
        for i in range(n):
            x0 = cx - a * 0.92 + 2 * a * 0.92 * i / (n - 1)
            pts = [((x0 + 18 * math.sin(t * 2.6 + j * 0.55 + i * 0.8) * j / 10) * k, (rim + L * j / 10 * (0.75 + 0.25 * math.sin(i * 1.3) ** 2)) * k) for j in range(11)]
            d.line(pts, fill=tc, width=int(4 * k), joint="curve")
    if melt > 0.02:
        d.ellipse(((cx - a * 1.25) * k, (rim - 10) * k, (cx + a * 1.25) * k, (rim + 26 + 20 * melt) * k), fill=bell)
    pts = [(cx - a * math.cos(u), rim - h * math.sin(u) ** 0.85) for u in np.linspace(0, math.pi, 40)]
    pts += [(x, rim + 9 * math.sin(x * 0.09 + t * 5)) for x in np.linspace(cx + a, cx - a, 24)]
    pk = [(x * k, y * k) for x, y in pts]
    d.polygon(pk, fill=bell); d.line(pk + [pk[0]], fill=bo, width=int(6 * k), joint="curve")
    d.line([((cx - a * 0.9 + 2 * a * 0.9 * q) * k, (rim - 14) * k) for q in (0, 1)], fill=mixc(bell, (255, 255, 255, 255), 0.5), width=int(7 * k))
    sy = rim - h * 0.2; sr = 34 * (h / 215) ** 0.5
    def E(x, y, rx, ry, fill, w=0, o=None):
        d.ellipse(((x - rx) * k, (y - ry) * k, (x + rx) * k, (y + ry) * k), fill=fill, outline=o, width=int(w * k))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        E(cx + dx * sr * 0.9, sy + dy * sr * 0.6, sr * 0.8, sr * 0.65, STOM)
    E(cx, sy, sr * 0.7, sr * 0.6, mixc(STOM, (255, 160, 120), 0.4))
    E(cx - a * 0.48, rim - h * 0.78, a * 0.16, h * 0.1, (255, 255, 255, 235))
    ey = rim - h * 0.66; er = 25
    if eyes == "open" and (t % 2.9) < 0.11: eyes = "sleep"
    for ex in (cx - 62, cx + 62):
        if eyes in ("open", "scared"):
            E(ex, ey, er, er * 1.12, WHITE, 5, (70, 50, 110))
            pr = 8 if eyes == "scared" else 13
            E(ex + 3, ey + 4, pr, pr * 1.1, (20, 10, 40)); E(ex + 7, ey - 3, 4, 4, WHITE)
        elif eyes == "sleep":
            d.arc(((ex - er) * k, (ey - er * 0.6) * k, (ex + er) * k, (ey + er * 0.8) * k), 10, 170, fill=(70, 50, 110), width=int(6 * k))
        elif eyes == "happy":
            d.arc(((ex - er) * k, (ey - er * 0.4) * k, (ex + er) * k, (ey + er * 1.2) * k), 200, 340, fill=(70, 50, 110), width=int(7 * k))
        elif eyes == "dizzy":
            for aa in (45, 135):
                ca, sa = math.cos(math.radians(aa)) * er, math.sin(math.radians(aa)) * er
                d.line(((ex - ca) * k, (ey - sa) * k, (ex + ca) * k, (ey + sa) * k), fill=(70, 50, 110), width=int(7 * k))
        E(ex + (14 if ex > cx else -14), ey + 34, 15, 8, (255, 160, 190, 255))
    my = ey + 36
    if mouth == "smile":
        d.arc(((cx - 22) * k, (my - 16) * k, (cx + 22) * k, (my + 14) * k), 20, 160, fill=(70, 50, 110), width=int(6 * k))
    elif mouth == "o":
        E(cx, my + 4, 12, 15, (70, 30, 60))
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)

def ball(s, col=(250, 170, 200)):
    k = 2; r = int(60 * s); im = Image.new("RGBA", (r * 2 * k + 8, r * 2 * k + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((4, 4, 4 + r * 2 * k, 4 + r * 2 * k), fill=col + (230,), outline=(160, 90, 140), width=6 * k)
    d.ellipse((r * k * 0.5, r * k * 0.4, r * k * 0.9, r * k * 0.7), fill=(255, 255, 255, 220))
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)

def polyp(fr, t, cx, base, g):
    """polipo (fase bebe) crescendo de baixo para cima; g 0..1"""
    if g <= 0: return
    d = ImageDraw.Draw(fr); hgt = 380 * g
    pts = [(cx + 14 * math.sin(t * 2 + q * 3), base - hgt * q) for q in np.linspace(0, 1, 16)]
    d.line(pts, fill=(205, 150, 120), width=22, joint="curve")
    hx, hy = pts[-1]
    for i in range(12):
        a = math.pi + i * math.pi / 11; L = 90 * g
        d.line([(hx, hy), (hx + L * math.cos(a) + 8 * math.sin(t * 4 + i), hy + L * math.sin(a) * 0.9)], fill=(240, 205, 225), width=8)
    d.ellipse((hx - 40 * g, hy - 34 * g, hx + 40 * g, hy + 30 * g), fill=(240, 120, 110), outline=(150, 70, 70), width=5)
    for ex in (-14, 14):
        d.ellipse((hx + ex - 7 * g, hy - 8 * g, hx + ex + 7 * g, hy + 6 * g), fill=WHITE)
        d.ellipse((hx + ex - 3 * g, hy - 4 * g, hx + ex + 3 * g, hy + 3 * g), fill=BLACK)

def zzz(fr, cx, cy, lt):
    for i in range(3):
        ph = (lt * 0.8 + i / 3) % 1
        txt(fr, "Z", 60 + 30 * i, (cx + 60 * ph + 30 * i, cy - 200 * ph), fill=WHITE, stroke=6, alpha=1 - ph)

def stars_ring(fr, cx, cy, lt, r=110):
    d = ImageDraw.Draw(fr)
    for i in range(4):
        a = lt * 5 + i * math.pi / 2; x = cx + r * math.cos(a); y = cy + r * 0.35 * math.sin(a)
        pts = [(x + 26 * (1 if j % 2 == 0 else 0.45) * math.cos(j * math.pi / 5 - math.pi / 2), y + 26 * (1 if j % 2 == 0 else 0.45) * math.sin(j * math.pi / 5 - math.pi / 2)) for j in range(10)]
        d.polygon(pts, fill=YEL, outline=BLACK)

def pill(fr, s, cy, sc=1.0, col=(230, 40, 40), cx=W / 2):
    if sc <= 0.01: return
    f = font(58); tw = f.getlength(s) + 70
    im = Image.new("RGBA", (int(tw), 110), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tw - 1, 109), 40, fill=col + (255,), outline=WHITE, width=6)
    d.text((35, 14), s, font=f, fill=WHITE)
    im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
    fr.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

_img = {}
def photo(name, size):
    key = (name, size)
    if key not in _img:
        im = Image.open(os.path.join(HERE, "imgs", name + ".jpg")).convert("RGB"); im.thumbnail(size); _img[key] = im
    return _img[key]

def circle_photo(fr, name, cx, cy, r):
    im = photo(name, (2 * r, 2 * r)).resize((2 * r, 2 * r))
    m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    fr.paste(im, (int(cx - r), int(cy - r)), m)

def health(fr, x0, y, frac, col, label, right=False):
    d = ImageDraw.Draw(fr); w = 420
    d.rounded_rectangle((x0, y, x0 + w, y + 46), 12, fill=(40, 40, 40), outline=WHITE, width=4)
    fw = int((w - 12) * clamp(frac))
    if fw > 4:
        if right: d.rounded_rectangle((x0 + w - 6 - fw, y + 6, x0 + w - 6, y + 40), 8, fill=col)
        else: d.rounded_rectangle((x0 + 6, y + 6, x0 + 6 + fw, y + 40), 8, fill=col)
    txt(fr, label, 40, (x0 + w / 2, y + 82), stroke=6)

# ---------------- cenas ----------------
ROUNDS = {1: ("VELHICE", "relogio"), 2: ("FRIO", "floco"), 3: ("SECA", "sol"), 4: ("RADIAÇÃO", "radiacao"), 5: ("ESPAÇO", "foguete"), 6: ("TIRO", "alvo")}

def icon(fr, kind, cx, cy, r, t):
    d = ImageDraw.Draw(fr)
    if kind == "relogio":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=BLACK, width=14)
        for i in range(12):
            a = i * math.pi / 6; d.line((cx + 0.8 * r * math.cos(a), cy + 0.8 * r * math.sin(a), cx + 0.92 * r * math.cos(a), cy + 0.92 * r * math.sin(a)), fill=BLACK, width=8)
        for L, sp, wd in ((0.5, 1.5, 16), (0.75, 9, 10)):
            a = t * sp - math.pi / 2; d.line((cx, cy, cx + L * r * math.cos(a), cy + L * r * math.sin(a)), fill=BLACK, width=wd)
    elif kind == "floco":
        for i in range(6):
            a = i * math.pi / 3 + t * 0.8; ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
            d.line((cx, cy, ex, ey), fill=(220, 245, 255), width=22)
            for sgn in (-1, 1):
                mx, my = cx + 0.6 * r * math.cos(a), cy + 0.6 * r * math.sin(a); b = a + sgn * 0.7
                d.line((mx, my, mx + 0.3 * r * math.cos(b), my + 0.3 * r * math.sin(b)), fill=(220, 245, 255), width=16)
    elif kind == "sol":
        for i in range(12):
            a = i * math.pi / 6 + t * 0.6
            d.line((cx + 0.7 * r * math.cos(a), cy + 0.7 * r * math.sin(a), cx + 1.05 * r * math.cos(a), cy + 1.05 * r * math.sin(a)), fill=(255, 150, 0), width=22)
        d.ellipse((cx - 0.6 * r, cy - 0.6 * r, cx + 0.6 * r, cy + 0.6 * r), fill=(255, 200, 0), outline=(255, 120, 0), width=10)
    elif kind == "radiacao":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YEL, outline=BLACK, width=12)
        for i in range(3):
            a0 = math.degrees(t * 1.2) + i * 120
            d.pieslice((cx - 0.85 * r, cy - 0.85 * r, cx + 0.85 * r, cy + 0.85 * r), a0, a0 + 60, fill=BLACK)
        d.ellipse((cx - 0.3 * r, cy - 0.3 * r, cx + 0.3 * r, cy + 0.3 * r), fill=YEL)
        d.ellipse((cx - 0.18 * r, cy - 0.18 * r, cx + 0.18 * r, cy + 0.18 * r), fill=BLACK)
    elif kind == "foguete":
        cy += 10 * math.sin(t * 20)
        d.polygon([(cx - 0.35 * r, cy + 0.6 * r), (cx, cy + 1.3 * r + 20 * math.sin(t * 40)), (cx + 0.35 * r, cy + 0.6 * r)], fill=(255, 140, 0))
        d.rounded_rectangle((cx - 0.35 * r, cy - 0.6 * r, cx + 0.35 * r, cy + 0.65 * r), 30, fill=WHITE, outline=BLACK, width=10)
        d.polygon([(cx - 0.35 * r, cy - 0.55 * r), (cx, cy - 1.2 * r), (cx + 0.35 * r, cy - 0.55 * r)], fill=(230, 40, 40), outline=BLACK)
        d.ellipse((cx - 0.17 * r, cy - 0.3 * r, cx + 0.17 * r, cy + 0.04 * r), fill=(80, 180, 255), outline=BLACK, width=8)
        for sgn in (-1, 1):
            d.polygon([(cx + sgn * 0.35 * r, cy + 0.2 * r), (cx + sgn * 0.7 * r, cy + 0.75 * r), (cx + sgn * 0.35 * r, cy + 0.6 * r)], fill=(230, 40, 40), outline=BLACK)
    elif kind == "alvo":
        for i, c in enumerate([(230, 40, 40), WHITE, (230, 40, 40), WHITE, (230, 40, 40)]):
            rr = r * (1 - i * 0.19); d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=c, outline=BLACK, width=6)

def scene_round(n, lt, dur, t):
    name, ic = ROUNDS[n]
    fr = burst(t, (200, 30, 40), (240, 70, 50)) if n % 2 else burst(t, (20, 60, 170), (40, 100, 220))
    k = back(lt / 0.35); sc = 3 - 2 * k if lt < 0.35 else 1 + 0.03 * math.sin(lt * 8)
    txt(fr, f"ROUND {n}", 190, (W / 2, 640), fill=YEL, stroke=16, sc=max(0.05, sc), rot=-4)
    icon(fr, ic, W / 2, 1000, int(170 * back(seg(lt, 0.2, 0.55))) or 1, t)
    txt(fr, name, 130, (W / 2, 1320), stroke=14, sc=back(seg(lt, 0.3, 0.6)))
    return shake(fr, 30 * (1 - seg(lt, 0.3, 0.6)) * (lt > 0.3), t)

def scene_placar(tt, mm, lt, t):
    scorer = "m" if (tt, mm) == (0, 1) else "t"
    fr = burst(t, (25, 25, 45), (45, 45, 80), speed=0.2)
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle((60, 560, W - 60, 1300), 50, fill=(20, 20, 30), outline=YEL, width=10)
    txt(fr, "PLACAR", 80, (W / 2, 640), fill=YEL, stroke=8)
    put(fr, tardi(t, 0.62, eyes="happy" if scorer == "t" and lt > 0.35 else "open"), 290, 820)
    put(fr, medusa(t, 0.48, eyes="happy" if scorer == "m" and lt > 0.35 else "open"), 790, 830)
    flip = seg(lt, 0.25, 0.45)
    old = (tt - (scorer == "t"), mm - (scorer == "m"))
    for i, (v, o) in enumerate(((tt, old[0]), (mm, old[1]))):
        x = 290 if i == 0 else 790; mine = (i == 0) == (scorer == "t")
        val = v if (not mine or flip >= 0.5) else o
        sc = 1 if not mine else (1 - flip * 2 if flip < 0.5 else (flip - 0.5) * 2) * 1.0
        sc = max(0.05, sc) * (1 + 0.15 * math.sin(lt * 10) * (mine and flip >= 1))
        txt(fr, str(val), 230, (x, 1130), fill=YEL if mine else WHITE, stroke=14, sc=sc)
    txt(fr, "X", 110, (W / 2, 1130), stroke=10)
    if lt > 0.4:
        x = 290 if scorer == "t" else 790
        txt(fr, "+1", 120, (x + 150, 1000 - 120 * seg(lt, 0.4, 1.2)), fill=(120, 255, 120), stroke=10, alpha=1 - seg(lt, 1.0, 1.4))
        confetti(fr, lt - 0.4, n=50, seed=4)
    return fr

def frame(nome, lt, dur, t):
    p = lt / max(dur, 0.01)
    if nome.startswith("round"): return scene_round(int(nome[5:]), lt, dur, t)
    if nome.startswith("placar_") and nome != "placar_final":
        a, b = nome.split("_")[1:]; return scene_placar(int(a), int(b), lt, t)
    fn = globals().get("sc_" + nome)
    if fn is None: raise ValueError("animacao desconhecida: " + nome)
    return fn(lt, dur, p, t)

def sc_vs(lt, dur, p, t):
    fr = Image.new("RGB", (W, H)); d = ImageDraw.Draw(fr)
    d.polygon([(0, 0), (W * 0.62, 0), (W * 0.38, H), (0, H)], fill=(200, 40, 40))
    d.polygon([(W * 0.62, 0), (W, 0), (W, H), (W * 0.38, H)], fill=(30, 80, 200))
    k = ease(lt / 0.45)
    put(fr, tardi(t, 0.95, walk=1 if lt < 0.45 else 0.2, glasses=lt > 1.2), -300 + 560 * k, 1130 + 10 * math.sin(lt * 6))
    put(fr, medusa(t, 0.9), W + 300 - 520 * k, 700 + 20 * math.sin(lt * 3))
    health(fr, 40, 300, 1, (90, 220, 90), "TARDÍGRADO")
    health(fr, W - 460, 300, 1, (90, 220, 90), "ÁGUA-VIVA", right=True)
    if lt > 0.4:
        if int(lt * 12) % 5 == 0:  # raio
            pts = [(W * 0.55, 420)]; rnd = random.Random(int(lt * 12))
            for i in range(8): pts.append((W * 0.5 + rnd.uniform(-90, 90), 420 + (i + 1) * 120))
            d.line(pts, fill=(255, 255, 200), width=12)
        txt(fr, "VS", 300, (W / 2, 930), fill=YEL, stroke=20, sc=max(0.05, 3 - 2 * back((lt - 0.4) / 0.3)), rot=-8)
    return shake(fr, 28 * (1 - seg(lt, 0.45, 0.8)) * (lt > 0.45), t)

def stage(t, col=(30, 20, 40)):
    fr = grad((10, 8, 20), col, key=("stage", col)); d = ImageDraw.Draw(fr)
    d.polygon([(W / 2 - 80, 0), (W / 2 + 80, 0), (W / 2 + 460, 1350), (W / 2 - 460, 1350)], fill=(70, 60, 90))
    d.ellipse((W / 2 - 460, 1270, W / 2 + 460, 1430), fill=(110, 100, 130))
    return fr

def sc_tardi_apresenta(lt, dur, p, t):
    fr = stage(t); k = ease(lt / 0.9)
    put(fr, tardi(t, 1.45, walk=1 - k * 0.7), -400 + 940 * k, 1000 + 8 * math.sin(lt * 10))
    d = ImageDraw.Draw(fr); a = seg(lt, 0.8, 1.2)
    if a > 0:
        x0, x1 = W / 2 - 330, W / 2 - 330 + 660 * a; d.line((x0, 1440, x1, 1440), fill=YEL, width=10)
        d.line((x0, 1415, x0, 1465), fill=YEL, width=10); d.line((x1, 1415, x1, 1465), fill=YEL, width=10)
        txt(fr, "0,5 mm", 90, (W / 2, 1360 if False else 520), fill=YEL, stroke=10, sc=back(seg(lt, 0.9, 1.3)))
    return fr

def sc_medusa_apresenta(lt, dur, p, t):
    fr = sea(t); k = ease(lt / 0.8)
    put(fr, medusa(t, 1.45), W / 2, 2100 - 1200 * k + 30 * math.sin(lt * 2.2))
    pill(fr, "SEM CÉREBRO", 1280, back(seg(lt, 0.6, 0.9)))
    pill(fr, "SEM CORAÇÃO", 1420, back(seg(lt, 1.0, 1.3)))
    txt(fr, "4,5 mm", 90, (W / 2, 450), fill=YEL, stroke=10, sc=back(seg(lt, 0.3, 0.6)))
    return fr

def belt(fr, cx, cy, s, t):
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle((cx - 330 * s, cy - 55 * s, cx + 330 * s, cy + 55 * s), int(30 * s), fill=(30, 30, 30), outline=(200, 160, 0), width=max(1, int(8 * s)))
    d.ellipse((cx - 150 * s, cy - 120 * s, cx + 150 * s, cy + 120 * s), fill=(250, 200, 30), outline=(170, 120, 0), width=max(1, int(12 * s)))
    d.ellipse((cx - 95 * s, cy - 75 * s, cx + 95 * s, cy + 75 * s), fill=(255, 230, 90))
    gl = (t * 1.5) % 2
    if gl < 1: d.line((cx - 150 * s + 300 * s * gl, cy - 110 * s, cx - 190 * s + 300 * s * gl, cy + 110 * s), fill=WHITE, width=max(1, int(18 * s)))

def ring(fr):
    d = ImageDraw.Draw(fr)
    d.polygon([(0, 1250), (W, 1250), (W, 1500), (0, 1500)], fill=(60, 110, 200))
    for i, y in enumerate((760, 900, 1040)):
        d.line((0, y, W, y + 30), fill=(230, 40, 40), width=16)
    for x in (40, W - 40):
        d.rectangle((x - 20, 680, x + 20, 1260), fill=(200, 200, 210))

def sc_ringue(lt, dur, p, t):
    fr = grad((10, 10, 30), (40, 30, 70), key="ringue"); ring(fr)
    hop = abs(math.sin(lt * 7)) * 50
    put(fr, tardi(t, 0.8, walk=0.6), 270, 1150 - hop)
    put(fr, medusa(t, 0.75), 810, 1000 - abs(math.sin(lt * 7 + 1)) * 50, flip=True)
    txt(fr, "6 ROUNDS", 150, (W / 2, 440), fill=YEL, stroke=14, sc=back(seg(lt, 0, 0.35)))
    if p > 0.55: belt(fr, W / 2, 640, 0.75 * back(seg(p, 0.55, 0.7)), t)
    return fr

def sc_medusa_rejuvenesce(lt, dur, p, t, cycle=None):
    fr = sea(t); cx, cy = W / 2, 900
    q = p if cycle is None else cycle
    if q < 0.4:
        s = 1.4 * (1 - 0.85 * (q / 0.4) ** 2)
        put(fr, medusa(t, s, tent=1 - q / 0.4, eyes="scared" if q > 0.1 else "open"), cx, cy)
    elif q < 0.55:
        sp = ball(1.0 + 0.1 * math.sin(lt * 20)); put(fr, sp, cx, 1250)
    else:
        polyp(fr, t, cx, 1380, ease(seg(q, 0.55, 0.85)))
        if q > 0.8 and cycle is None: txt(fr, "BEBÊ DE NOVO!", 110, (W / 2, 480), fill=YEL, stroke=12, sc=back(seg(q, 0.8, 0.9)))
    return fr

def sc_medusa_loop(lt, dur, p, t):
    per = 1.25; n = int(lt / per); q = (lt % per) / per
    q2 = 0.55 + 0.3 * seg(q, 0, 0.35) if q < 0.35 else (0.85 * 0 + (q - 0.35) / 0.65 * 0.4)  # polipo -> medusa adulta -> encolhe
    fr = sea(t)
    if q < 0.35: polyp(fr, t, W / 2, 1380, 1 - seg(q, 0.2, 0.35))
    if q >= 0.2 and q < 0.7:
        g = ease(seg(q, 0.2, 0.5)); s = 0.2 + 1.1 * g - 0.9 * seg(q, 0.55, 0.7)
        put(fr, medusa(t, max(0.15, s), tent=g), W / 2, 900)
    if q >= 0.7: put(fr, ball(1.0), W / 2, 1250 - 300 * (1 - seg(q, 0.7, 0.85)))
    txt(fr, f"x{n + 1}", 200, (W / 2, 470), fill=YEL, stroke=14, sc=1 + 0.3 * (1 - seg(q, 0, 0.2)))
    return fr

def sc_tardi_fantasma(lt, dur, p, t):
    fr = grad((30, 30, 50), (60, 60, 80), key="cemit"); d = ImageDraw.Draw(fr)
    d.rectangle((0, 1300, W, H), fill=(40, 70, 40))
    d.rounded_rectangle((W / 2 - 200, 820, W / 2 + 200, 1340), 190, fill=(140, 140, 150), outline=(70, 70, 80), width=10)
    txt(fr, "R.I.P.", 100, (W / 2, 1000), fill=(60, 60, 70), stroke=0)
    txt(fr, "2 ANOS", 70, (W / 2, 1130), fill=(60, 60, 70), stroke=0)
    g = ease(seg(lt, 0.3, 2.0))
    sp = tardi(t, 0.8, eyes="sleep", tint=(230, 240, 255), tint_a=0.85)
    put(fr, sp, W / 2 + 40 * math.sin(lt * 3), 1250 - 650 * g, alpha=0.75)
    hx = W / 2 + 40 * math.sin(lt * 3) + 120; hy = 1250 - 650 * g - 170
    ImageDraw.Draw(fr).ellipse((hx - 90, hy - 22, hx + 90, hy + 22), outline=YEL, width=12)
    return fr

def thermo(fr, x, y, temp, tmin=-272, tmax=30):
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle((x - 40, y, x + 40, y + 700), 40, fill=WHITE, outline=BLACK, width=8)
    d.ellipse((x - 75, y + 650, x + 75, y + 800), fill=(40, 140, 255), outline=BLACK, width=8)
    f = (temp - tmin) / (tmax - tmin); top = y + 30 + (1 - f) * 640
    d.rectangle((x - 20, top, x + 20, y + 690), fill=(40, 140, 255))
    txt(fr, f"{int(temp)} °C", 90, (x + 10, y - 70), fill=(200, 235, 255), stroke=10)

def sc_tardi_gelo(lt, dur, p, t):
    fr = grad((10, 40, 90), (150, 210, 255), key="gelo")
    temp = 25 - 297 * ease(seg(p, 0.0, 0.45))
    thermo(fr, 170, 560, temp)
    fz = seg(p, 0.15, 0.5); broke = p > 0.72
    cx, cy = 690, 1060
    if not broke:
        jit = 6 * math.sin(lt * 60) * (1 - fz)
        put(fr, tardi(t, 0.85, eyes="scared" if fz < 1 else "sleep", tint=ICE, tint_a=0.6 * fz), cx + jit, cy)
        if fz > 0:
            ice = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ice)
            d.rounded_rectangle((cx - 300, cy - 260, cx + 300, cy + 260), 40, fill=(200, 235, 255, int(150 * fz)), outline=(255, 255, 255, int(255 * fz)), width=10)
            d.line((cx - 230, cy - 200, cx - 120, cy - 230), fill=(255, 255, 255, int(220 * fz)), width=14)
            if p > 0.55:
                rnd = random.Random(2); x, y = cx - 40, cy - 260
                for i in range(int(8 * seg(p, 0.55, 0.72))):
                    nx, ny = x + rnd.uniform(-60, 60), y + 65; d.line((x, y, nx, ny), fill=(20, 60, 120, 255), width=8); x, y = nx, ny
            fr.paste(ice, (0, 0), ice)
    else:
        q = seg(p, 0.72, 1.0); rnd = random.Random(9); d = ImageDraw.Draw(fr)
        for i in range(14):
            a = rnd.uniform(0, 2 * math.pi); v = rnd.uniform(400, 900)
            x = cx + math.cos(a) * v * q * 1.5; y = cy + math.sin(a) * v * q * 1.5 + 900 * q * q
            sz = rnd.uniform(30, 70); d.polygon([(x, y - sz), (x + sz, y), (x, y + sz * 0.6), (x - sz * 0.8, y)], fill=(210, 240, 255), outline=WHITE)
        put(fr, tardi(t, 0.95, glasses=True, eyes="happy"), cx, cy - 20 * abs(math.sin(lt * 6)))
        txt(fr, "DE BOA", 120, (cx, 640), fill=YEL, stroke=12, sc=back(seg(p, 0.75, 0.85)))
    return shake(fr, 25 * (0.72 < p < 0.78), t)

def sc_tardi_ovo(lt, dur, p, t):
    fr = grad((120, 190, 240), (230, 245, 255), key="ovo"); floor(fr, 1320, (230, 240, 250))
    put(fr, tardi(t, 0.95, eyes="happy" if p > 0.4 else "open", tint=ICE, tint_a=0.5 * (1 - seg(p, 0, 0.4))), 420, 1150)
    if p > 0.35:
        k = back(seg(p, 0.35, 0.55)); d = ImageDraw.Draw(fr); ex, ey = 820, 1230 - 40 * abs(math.sin(lt * 5)) * (p > 0.55)
        rot = 12 * math.sin(lt * 8)
        egg = Image.new("RGBA", (200, 260), (0, 0, 0, 0)); ImageDraw.Draw(egg).ellipse((10, 10, 190, 250), fill=(255, 250, 235), outline=(150, 130, 100), width=8)
        egg = egg.resize((max(1, int(200 * k)), max(1, int(260 * k))))
        put(fr, egg, ex, ey, rot=rot)
        txt(fr, "PLOFT!", 110, (820, 940), fill=YEL, stroke=12, sc=back(seg(p, 0.35, 0.5)), alpha=1 - seg(p, 0.6, 0.8))
    txt(fr, "30 ANOS NO GELO", 90, (W / 2, 480), fill=WHITE, stroke=12, sc=back(seg(lt, 0, 0.3)))
    return fr

def sc_medusa_picole(lt, dur, p, t):
    fr = grad((80, 170, 240), (200, 235, 255), key="picole"); cy = -600 + 1550 * back(seg(lt, 0, 0.5))
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle((W / 2 - 50, cy + 330, W / 2 + 50, cy + 680), 40, fill=(215, 170, 110), outline=(140, 100, 50), width=8)
    pop = Image.new("RGBA", (560, 760), (0, 0, 0, 0)); pd = ImageDraw.Draw(pop)
    pd.rounded_rectangle((0, 0, 559, 759), 180, fill=(255, 170, 210, 255), outline=(200, 90, 140, 255), width=12)
    put(fr, pop, W / 2, cy - 40)
    put(fr, medusa(t, 0.85, eyes="scared", mouth="o", tint=(200, 230, 255), tint_a=0.4, pulse=0, tent=0.6), W / 2, cy - 30)
    d = ImageDraw.Draw(fr)
    for i in range(6):
        a = lt * 2 + i; x = W / 2 + 230 * math.cos(a * 1.3 + i); y = cy - 40 + 330 * math.sin(a + i * 2)
        d.line((x - 18, y, x + 18, y), fill=WHITE, width=6); d.line((x, y - 18, x, y + 18), fill=WHITE, width=6)
    return shake(fr, 20 * (0.45 < lt < 0.6), t)

def sc_tardi_tun(lt, dur, p, t):
    fr = grad((255, 190, 80), (240, 140, 60), key="deserto"); floor(fr, 1280, (220, 170, 100))
    icon(fr, "sol", 860, 470, 110, t)
    c = ease(seg(p, 0.15, 0.6))
    cx, cy = W / 2, 1140 + 40 * c
    d = ImageDraw.Draw(fr); rnd = random.Random(11)
    if 0.05 < p < 0.7:
        for i in range(8):  # gotas saindo do corpo
            ph = (lt * 1.3 + i / 8) % 1; a = rnd.uniform(-2.6, -0.5)
            x = cx + math.cos(a) * (120 + 380 * ph); y = cy + math.sin(a) * (120 + 380 * ph)
            d.ellipse((x - 16, y - 22, x + 16, y + 22), fill=(80, 170, 255), outline=WHITE, width=3)
    put(fr, tardi(t, 0.95 * (1 - 0.15 * c), curl=c, walk=0.4 * (1 - c), eyes="scared" if c < 0.5 else "sleep", tint=(200, 150, 90), tint_a=0.4 * c), cx, cy)
    if p > 0.6:
        zzz(fr, cx + 150, cy - 140, lt)
        txt(fr, "ANOS DEPOIS...", 100, (W / 2, 520), fill=WHITE, stroke=12, sc=back(seg(p, 0.65, 0.8)))
    return fr

def sc_tardi_acorda(lt, dur, p, t):
    fr = grad((150, 210, 255), (240, 250, 255), key="acorda"); floor(fr, 1280, (120, 170, 90))
    cx, cy = W / 2, 1180; d = ImageDraw.Draw(fr)
    hit = 0.35
    if p < hit:
        y = 300 + (cy - 420) * (p / hit) ** 2
        d.polygon([(cx, y - 70), (cx - 45, y + 10), (cx + 45, y + 10)], fill=(60, 150, 255)); d.ellipse((cx - 45, y - 30, cx + 45, y + 55), fill=(60, 150, 255), outline=WHITE, width=4)
    c = 1 - ease(seg(p, hit + 0.05, 0.7))
    if hit <= p < hit + 0.25:
        q = seg(p, hit, hit + 0.25)
        for i in range(8):
            a = math.pi + i * math.pi / 7; r = 80 + 220 * q
            d.ellipse((cx + r * math.cos(a) - 14, cy - 140 + r * math.sin(a) * 0.6 - 14, cx + r * math.cos(a) + 14, cy - 140 + r * math.sin(a) * 0.6 + 14), fill=(60, 150, 255))
    put(fr, tardi(t, 0.95 * (1 - 0.15 * c), curl=c, walk=0.5 * (p > 0.7), eyes="sleep" if c > 0.5 else ("happy" if p > 0.85 else "open")), cx, cy - 30 * (1 - c) * abs(math.sin(lt * 7)) * (p > 0.7))
    if p < hit: zzz(fr, cx + 120, cy - 120, lt)
    if p > 0.75: txt(fr, "BOM DIA!", 120, (W / 2, 520), fill=YEL, stroke=12, sc=back(seg(p, 0.75, 0.88)))
    return fr

def sc_medusa_derrete(lt, dur, p, t):
    fr = grad((255, 200, 90), (250, 150, 70), key="praia"); floor(fr, 1300, (235, 205, 140))
    icon(fr, "sol", 200, 480, 110, t)
    m = ease(seg(p, 0.05, 0.6))
    put(fr, medusa(t, 1.1, melt=m, eyes="dizzy" if m > 0.6 else "scared", mouth="o", pulse=1 - m), W / 2, 1300 - 260 * 1.1 + 160 * m * 1.1 - 60)
    if p > 0.55: txt(fr, "PLOFT", 140, (W / 2, 620), fill=WHITE, stroke=14, sc=back(seg(p, 0.55, 0.7)), rot=6)
    return fr

def sc_barras_radiacao(lt, dur, p, t):
    fr = grad((20, 30, 10), (60, 80, 20), key="rad")
    for i in range(6):
        icon(fr, "radiacao", 100 + (i * 197) % W, (300 + i * 260 + lt * 120) % 1400 + 300, 45, t + i)
    d = ImageDraw.Draw(fr); base = 1420
    hh = 18 * ease(seg(p, 0.0, 0.2))
    d.rectangle((150, base - hh, 400, base), fill=(230, 60, 60), outline=WHITE, width=6)
    txt(fr, "HUMANO", 60, (275, base - hh - 140), stroke=8); txt(fr, "10 Gy", 70, (275, base - hh - 60), fill=(255, 120, 120), stroke=8)
    g = ease(seg(p, 0.25, 0.8)); top = base - 740 * g
    d.rectangle((640, top, 900, base), fill=(90, 230, 90), outline=WHITE, width=6)
    txt(fr, f"{int(5000 * g):,} Gy".replace(",", "."), 90, (770, top - 260 if g > 0 else base - 200), fill=YEL, stroke=10)
    put(fr, tardi(t, 0.5, glasses=p > 0.8, eyes="happy" if p > 0.8 else "open"), 770, top - 110)
    return fr

def sc_tardi_escudo(lt, dur, p, t):
    fr = grad((5, 10, 30), (10, 40, 70), key="escudo"); cx, cy = W / 2, 980
    rnd = random.Random(7); d = ImageDraw.Draw(fr); R = 400
    for i in range(30):
        ph = (lt * 0.9 + rnd.random()) % 1; x = rnd.uniform(60, W - 60); y = 250 + ph * 1300
        dist = math.hypot(x - cx, y - cy)
        if dist < R + 20: continue
        d.line((x, y - 40, x, y), fill=YEL, width=8)
    glow = 0.5 + 0.5 * math.sin(lt * 5)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(80, 220, 255, 60), outline=(150, 240, 255, int(180 + 70 * glow)), width=14)
    fr.paste(sh, (0, 0), sh)
    for i in range(24):  # DNA girando atras
        y = cy - 330 + i * 28; a = lt * 3 + i * 0.5
        x1, x2 = cx - 260 + 60 * math.sin(a), cx - 260 - 60 * math.sin(a)
        d.line((x1, y, x2, y), fill=(150, 200, 255), width=4)
        d.ellipse((x1 - 9, y - 9, x1 + 9, y + 9), fill=(255, 90, 140)); d.ellipse((x2 - 9, y - 9, x2 + 9, y + 9), fill=(90, 200, 255))
    put(fr, tardi(t, 0.8, glasses=True), cx + 60, cy + 40)
    txt(fr, "PROTEÍNA DSUP", 100, (W / 2, 450), fill=(150, 240, 255), stroke=12, sc=back(seg(lt, 0.1, 0.4)))
    return fr

def sc_tardi_espaco(lt, dur, p, t):
    fr = space(t); circle_photo(fr, "terra", 900, 1450, 420)
    d = ImageDraw.Draw(fr); icon(fr, "sol", 140, 420, 90, t)
    for i in range(5):
        ph = (lt * 1.2 + i / 5) % 1; x = 140 + (W / 2 - 140) * ph; y = 420 + (900 - 420) * ph
        d.line((x - 30, y - 30, x + 30, y + 30), fill=YEL, width=10)
    sp = tardi(t, 0.85, eyes="scared" if (lt % 3) < 1.5 else "open")
    put(fr, sp, W / 2, 920 + 40 * math.sin(lt * 1.5), rot=10 * math.sin(lt * 0.8))
    txt(fr, "NO VÁCUO!", 110, (W / 2, 1300), fill=WHITE, stroke=12, sc=back(seg(lt, 0.2, 0.5)))
    return fr

def sc_tardi_lua(lt, dur, p, t):
    fr = space(t, 8); circle_photo(fr, "terra", 830, 520, 120)
    d = ImageDraw.Draw(fr); d.ellipse((-700, 1150, W + 700, 3200), fill=(170, 170, 175))
    for x, y, r in ((200, 1300, 60), (700, 1240, 40), (900, 1400, 80), (420, 1450, 35)):
        d.ellipse((x - r, y - r * 0.4, x + r, y + r * 0.4), fill=(130, 130, 135))
    d.line((300, 1260, 300, 980), fill=WHITE, width=8); d.rectangle((300, 980, 460, 1080), fill=(240, 240, 240))
    txt(fr, "TARDI", 40, (380, 1030), fill=(200, 40, 40), stroke=0)
    put(fr, tardi(t, 0.85, curl=1), 640, 1170)
    zzz(fr, 740, 1060, lt)
    return fr

def sc_medusa_espaco(lt, dur, p, t):
    fr = space(t, 3); pop = 0.55
    if p < pop:
        s = 0.8 + 0.9 * (p / pop) ** 2
        put(fr, medusa(t, s, eyes="scared", mouth="o", pulse=3 * p), W / 2 + 10 * math.sin(lt * 50) * p, 950)
    else:
        q = seg(p, pop, 1); rnd = random.Random(4); d = ImageDraw.Draw(fr)
        for i in range(30):
            a = rnd.uniform(0, 2 * math.pi); v = rnd.uniform(200, 700) * ease(q)
            x, y = W / 2 + math.cos(a) * v, 950 + math.sin(a) * v; r = rnd.uniform(10, 26)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(240, 200, 240) if i % 3 else STOM)
        txt(fr, "POP!", 220, (W / 2, 950), fill=YEL, stroke=16, sc=back(seg(q, 0, 0.25)), rot=-6)
    return shake(fr, 30 * (pop < p < pop + 0.08), t)

def sc_tardi_tiro(lt, dur, p, t):
    fr = grad((60, 70, 90), (120, 130, 150), key="lab"); floor(fr, 1380, (70, 70, 80)); d = ImageDraw.Draw(fr)
    for r in range(9):  # parede
        for c in range(3):
            x0 = W - 230 + (c * 80 + (40 if r % 2 else 0)) % 240; y0 = 640 + r * 82
            d.rectangle((x0, y0, x0 + 76, y0 + 78), fill=(170, 70, 50), outline=(110, 40, 30), width=4)
    cxn, cyn = 210, 1180
    can = Image.new("RGBA", (520, 220), (0, 0, 0, 0)); cd = ImageDraw.Draw(can)
    cd.rounded_rectangle((0, 40, 500, 180), 40, fill=(60, 60, 70), outline=BLACK, width=8); cd.rectangle((470, 20, 520, 200), fill=(40, 40, 50))
    fire, hit = 0.22, 0.5
    if p < fire:
        put(fr, tardi(t, 0.42, eyes="scared"), cxn + 210, cyn - 120)
    put(fr, can, cxn + 60, cyn, rot=12)
    sp = 0
    if fire <= p < hit:
        q = (p - fire) / (hit - fire); x = cxn + 300 + (W - 230 - 160 - cxn - 300) * q; y = cyn - 150 - 220 * math.sin(q * math.pi * 0.8)
        for i in range(6): d.line((x - 120 - i * 40, y - 40 + i * 16, x - 300 - i * 40, y - 40 + i * 16), fill=WHITE, width=6)
        put(fr, tardi(t, 0.42, curl=0.5, eyes="scared"), x, y, rot=-360 * q * 2)
        sp = q
        if q < 0.25: txt(fr, "BANG!", 150, (cxn + 360, cyn - 300), fill=YEL, stroke=14, sc=back(q / 0.15), rot=8)
    if p >= hit:
        sp = 1; q = seg(p, hit, 1)
        y = min(1260, 900 + 900 * q * q)
        put(fr, tardi(t, 0.5, eyes="dizzy" if q < 0.7 else "happy"), W - 420, y)
        stars_ring(fr, W - 380, y - 140, lt)
        txt(fr, "POW!", 170, (W - 300, 760), fill=YEL, stroke=14, sc=back(seg(q, 0, 0.12)), rot=-10, alpha=1 - seg(q, 0.5, 0.7))
        if q > 0.7: txt(fr, "SOBREVIVEU!", 110, (W / 2, 1060), fill=(120, 255, 120), stroke=12, sc=back(seg(q, 0.7, 0.85)))
    kmh = 3240 * ease(clamp(sp))
    d.rounded_rectangle((W / 2 - 330, 300, W / 2 + 330, 470), 30, fill=(20, 20, 20), outline=YEL, width=8)
    txt(fr, f"{int(kmh):,} km/h".replace(",", "."), 110, (W / 2, 385), fill=YEL, stroke=0)
    return shake(fr, 30 * ((fire < p < fire + 0.05) or (hit < p < hit + 0.06)), t)

def sc_medusa_suco(lt, dur, p, t):
    fr = burst(t, (255, 170, 200), (255, 200, 220), speed=0.3); d = ImageDraw.Draw(fr)
    k = back(seg(lt, 0, 0.4)); cx, cy = W / 2, 1000
    gw, gh = 300 * k, 520 * k
    if k > 0.05:
        d.line((cx + 60 * k, cy - gh / 2 - 180 * k, cx + 140 * k, cy + gh / 3), fill=(80, 200, 120), width=max(1, int(24 * k)))
        d.polygon([(cx - gw, cy - gh / 2), (cx + gw, cy - gh / 2), (cx + gw * 0.8, cy + gh / 2), (cx - gw * 0.8, cy + gh / 2)], fill=(240, 120, 170), outline=WHITE)
        d.ellipse((cx - gw, cy - gh / 2 - 30 * k, cx + gw, cy - gh / 2 + 30 * k), fill=(255, 160, 200), outline=WHITE, width=6)
        for ex in (-80, 80):
            d.ellipse((cx + ex * k - 34 * k, cy - 60 * k, cx + ex * k + 34 * k, cy + 10 * k), fill=WHITE, outline=BLACK, width=4)
            ang = lt * 6; d.ellipse((cx + ex * k + 12 * math.cos(ang) * k - 14 * k, cy - 25 * k + 12 * math.sin(ang) * k - 14 * k, cx + ex * k + 12 * math.cos(ang) * k + 14 * k, cy - 25 * k + 12 * math.sin(ang) * k + 14 * k), fill=BLACK)
    txt(fr, "SUCO DE ÁGUA-VIVA", 80, (W / 2, 450), fill=WHITE, stroke=10, sc=back(seg(lt, 0.3, 0.6)))
    return fr

def sc_placar_final(lt, dur, p, t):
    fr = burst(t, (200, 140, 0), (255, 200, 30), speed=0.5)
    put(fr, tardi(t, 0.95, eyes="happy", glasses=True), W / 2 - 40, 1050 - abs(math.sin(lt * 6)) * 70)
    belt(fr, W / 2 - 20, 1160 - abs(math.sin(lt * 6)) * 70, 0.55, t)
    put(fr, medusa(t, 0.4, eyes="dizzy"), 900, 1380, rot=80)
    txt(fr, "5 X 1", 220, (W / 2, 560), fill=WHITE, stroke=16, sc=back(seg(lt, 0, 0.35)))
    txt(fr, "NOCAUTE!", 140, (W / 2, 780), fill=(230, 30, 30), stroke=14, sc=back(seg(lt, 0.8, 1.1)), rot=-6)
    confetti(fr, lt, n=90)
    return fr

def sc_plot_twist(lt, dur, p, t):
    fr = grad((40, 0, 0), (0, 0, 0), key="twist")
    sc = back(seg(lt, 0, 0.3)); g = 14 * (int(lt * 20) % 3 == 0)
    txt(fr, "PLOT", 230, (W / 2 - g, 780), fill=(255, 40, 40), stroke=0, sc=sc, alpha=0.7)
    txt(fr, "PLOT", 230, (W / 2 + g, 780), fill=(40, 200, 255), stroke=0, sc=sc, alpha=0.7)
    txt(fr, "PLOT", 230, (W / 2, 780), fill=WHITE, stroke=12, sc=sc)
    txt(fr, "TWIST", 230, (W / 2, 1040), fill=YEL, stroke=14, sc=back(seg(lt, 0.25, 0.55)))
    return shake(fr, 18, t)

def sc_tardi_pause(lt, dur, p, t):
    fr = grad((20, 20, 40), (50, 40, 90), key="pause"); d = ImageDraw.Draw(fr)
    play = p > 0.33; age = seg(p, 0.6, 1.0)
    if not play:
        put(fr, tardi(t, 1.25, curl=1), W / 2, 1150); zzz(fr, W / 2 + 200, 1000, lt)
        d.rounded_rectangle((W / 2 - 150, 420, W / 2 - 60, 720), 20, fill=WHITE); d.rounded_rectangle((W / 2 + 60, 420, W / 2 + 150, 720), 20, fill=WHITE)
    else:
        c = 1 - ease(seg(p, 0.33, 0.45))
        put(fr, tardi(t, 1.25, curl=c, walk=0.6 * (1 - age), eyes="open" if age < 0.7 else "sleep", tint=(200, 200, 200), tint_a=0.7 * age, mustache=age > 0.3), W / 2, 1150)
        if p < 0.42: d.polygon([(W / 2 - 100, 420), (W / 2 - 100, 720), (W / 2 + 150, 570)], fill=WHITE)
        else: icon(fr, "relogio", W / 2, 570, 170 * back(seg(p, 0.42, 0.5)) + 1, t * (4 + 10 * age))
    return fr

def lemniscate(fr, cx, cy, a, t, col):
    d = ImageDraw.Draw(fr)
    pts = [(cx + a * math.cos(u) / (1 + math.sin(u) ** 2), cy + a * math.sin(u) * math.cos(u) / (1 + math.sin(u) ** 2)) for u in np.linspace(0, 2 * math.pi, 120)]
    d.line(pts + [pts[0]], fill=col, width=26, joint="curve")
    u = t * 2.2; x = cx + a * math.cos(u) / (1 + math.sin(u) ** 2); y = cy + a * math.sin(u) * math.cos(u) / (1 + math.sin(u) ** 2)
    d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=WHITE)

def sc_medusa_infinito(lt, dur, p, t):
    fr = sea(t)
    lemniscate(fr, W / 2, 520, 420 * back(seg(lt, 0, 0.4)) + 1, t, YEL)
    put(fr, medusa(t, 1.1, eyes="happy"), W / 2, 1060 + 25 * math.sin(lt * 2))
    txt(fr, "PRA SEMPRE", 110, (W / 2, 1420), fill=WHITE, stroke=12, sc=back(seg(lt, 0.3, 0.6)))
    return fr

def podium(fr, x, top, w, col, label):
    d = ImageDraw.Draw(fr); d.rectangle((x - w / 2, top, x + w / 2, 1480), fill=col, outline=WHITE, width=8)
    for i, line in enumerate(label.split("\n")): txt(fr, line, 56, (x, top + 70 + i * 66), stroke=6)

def sc_veredito(lt, dur, p, t):
    fr = burst(t, (20, 30, 70), (35, 50, 110), speed=0.15)
    k1 = back(seg(lt, 0, 0.4)); k2 = back(seg(p, 0.5, 0.65))
    if k1 > 0.02:
        podium(fr, 280, 1480 - 420 * k1, 440, (200, 120, 40), "MAIS\nRESISTENTE")
        put(fr, tardi(t, 0.85, glasses=True, eyes="happy"), 280, 1480 - 420 * k1 - 170)
    if k2 > 0.02:
        podium(fr, 800, 1480 - 420 * k2, 440, (150, 80, 200), "MAIS\nIMORTAL")
        put(fr, medusa(t, 0.78, eyes="happy"), 800, 1480 - 420 * k2 - 300)
    return fr

def sc_fusao(lt, dur, p, t):
    fr = burst(t, (255, 120, 0), (255, 190, 0), speed=1.2)
    m = 0.3
    if p < m:
        q = ease(p / m)
        put(fr, tardi(t, 0.8, walk=1), 200 + 340 * q, 1150)
        put(fr, medusa(t, 0.75), 880 - 340 * q, 700 + 250 * q)
        if q > 0.8: ImageDraw.Draw(fr).rectangle((0, 0, W, H), fill=WHITE)
    else:
        cx, cy = W / 2, 1150 - abs(math.sin(lt * 5)) * 40
        put(fr, tardi(t, 0.95, eyes="happy"), cx, cy)
        put(fr, medusa(t, 0.62, eyes="happy"), cx + 160, cy - 260)
        d = ImageDraw.Draw(fr); rnd = random.Random(int(lt * 15))
        for i in range(3):
            pts = [(cx + rnd.uniform(-450, 450), 500)]
            for j in range(6): pts.append((pts[-1][0] + rnd.uniform(-60, 60), pts[-1][1] + 160))
            d.line(pts, fill=(170, 230, 255), width=8)
        txt(fr, "TARDIVIVA", 170, (W / 2, 520), fill=WHITE, stroke=16, sc=back(seg(p, m, m + 0.15)), rot=-4)
        txt(fr, "INVENCÍVEL", 90, (W / 2, 690), fill=(230, 30, 30), stroke=10, sc=back(seg(p, m + 0.2, m + 0.35)))
    return shake(fr, 25 * (m - 0.03 < p < m + 0.08), t)

def sc_cta(lt, dur, p, t):
    fr = grad((20, 20, 40), (60, 30, 90), key="cta"); d = ImageDraw.Draw(fr)
    put(fr, tardi(t, 0.85, walk=0.3), 280, 820 - abs(math.sin(lt * 5)) * 30)
    put(fr, medusa(t, 0.75), 820, 740)
    a = 1 + 0.08 * math.sin(lt * 8); b = 1 + 0.08 * math.sin(lt * 8 + math.pi)
    pill(fr, "TIME TARDÍGRADO", 1070, 1.2 * a * back(seg(lt, 0.2, 0.5)), col=(210, 120, 40), cx=W / 2)
    pill(fr, "TIME ÁGUA-VIVA", 1230, 1.2 * b * back(seg(lt, 0.4, 0.7)), col=(150, 80, 200), cx=W / 2)
    sub = p > 0.75
    pill(fr, "INSCRITO!" if sub else "INSCREVA-SE", 1400, back(seg(p, 0.5, 0.6)) * (1.15 if sub else 1.2 + 0.06 * math.sin(lt * 10)), col=(120, 120, 120) if sub else (230, 20, 20), cx=W / 2)
    if 0.6 < p < 0.85:  # cursor clicando
        q = seg(p, 0.6, 0.75); x = W / 2 + 300 - 200 * q; y = 1650 - 220 * q
        d.polygon([(x, y), (x, y + 80), (x + 22, y + 60), (x + 40, y + 98), (x + 54, y + 90), (x + 36, y + 54), (x + 62, y + 54)], fill=WHITE, outline=BLACK)
    txt(fr, "COMENTA AÍ!", 110, (W / 2, 450), fill=YEL, stroke=12, sc=back(seg(lt, 0, 0.3)))
    return fr

# ---------------- efeitos sonoros ----------------
def _env(n, sr, dec): return np.exp(-np.arange(n) / sr * dec)
def _bell(sr, f=880, dur=1.2):
    n = int(dur * sr); x = np.arange(n) / sr
    y = sum(a * np.sin(2 * np.pi * f * m * x) for m, a in ((1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)))
    return y * _env(n, sr, 3.5)
def _boom(sr, dur=0.9):
    n = int(dur * sr); x = np.arange(n) / sr; f = 30 + 90 * np.exp(-x * 8)
    y = np.sin(2 * np.pi * np.cumsum(f) / sr) * _env(n, sr, 4) + 0.3 * np.random.default_rng(1).standard_normal(n) * _env(n, sr, 12)
    return y
def _chime(sr):
    out = np.zeros(int(0.9 * sr))
    for i, f in enumerate((784, 988, 1319)):
        b = _bell(sr, f, 0.6) * 0.5; i0 = int(i * 0.09 * sr); out[i0:i0 + len(b)] += b[: len(out) - i0]
    return out
def _slide(sr, f0, f1, dur):
    n = int(dur * sr); x = np.arange(n) / sr; f = f0 + (f1 - f0) * x / dur
    return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.minimum(1, (dur - x) * 8)
def _noise(sr, dur, dec):
    n = int(dur * sr); return np.random.default_rng(3).standard_normal(n) * _env(n, sr, dec)

def sfx(nome, sr, dur=3.0):
    def norm(y, v): return (y / (np.max(np.abs(y)) + 1e-9) * v).astype(np.float32)
    if nome.startswith("round"):
        a = _bell(sr, 1250, 1.0); y = np.concatenate([a[: int(0.22 * sr)], a]); return norm(y, 0.35)
    if nome.startswith("placar_") and nome != "placar_final": return norm(_chime(sr), 0.3)
    if nome in ("vs", "plot_twist"):
        if nome == "vs": return norm(_boom(sr), 0.5)
        out = np.zeros(int(1.8 * sr))
        for i, f in enumerate((98, 92, 73)):
            n = int((0.35 if i < 2 else 0.9) * sr); x = np.arange(n) / sr
            s = np.sign(np.sin(2 * np.pi * f * x)) * 0.5 + np.sin(2 * np.pi * f * 2 * x) * 0.3
            i0 = int(i * 0.4 * sr); out[i0:i0 + n] += s * np.minimum(1, (n / sr - x) * 6)
        return norm(out, 0.32)
    if nome == "tardi_fantasma": return norm(_slide(sr, 300, 700, 1.0) * 0.5 + _slide(sr, 302, 703, 1.0) * 0.5, 0.12)
    if nome in ("medusa_derrete",): return norm(_slide(sr, 1100, 250, 0.9), 0.15)
    if nome == "tardi_acorda": return norm(_slide(sr, 400, 1200, 0.35), 0.15)
    if nome == "medusa_picole": return norm(_bell(sr, 1600, 0.4), 0.2)
    if nome == "tardi_ovo":
        b = _slide(sr, 500, 160, 0.15); i0 = int(0.35 * dur * sr); y = np.zeros(i0 + len(b)); y[i0:] += b; return norm(y, 0.2)
    if nome == "medusa_espaco":
        b = _noise(sr, 0.3, 25); i0 = int(0.55 * dur * sr); y = np.zeros(i0 + len(b)); y[i0:i0 + len(b)] += b; return norm(y, 0.4)
    if nome == "tardi_tiro":
        b = _boom(sr, 0.6) + _noise(sr, 0.6, 10); i0 = int(0.22 * dur * sr); y = np.zeros(i0 + len(b)); y[i0:] += b
        return norm(y, 0.45)
    if nome in ("placar_final", "fusao"): return norm(_chime(sr) + np.concatenate([_boom(sr, 0.9)[:int(0.9 * sr)], np.zeros(0)]), 0.4)
    if nome == "medusa_suco": return norm(_noise(sr, 0.4, 8), 0.2)
    return None
