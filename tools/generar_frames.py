"""Genera los frames de una serie: la imagen base depende de quién habla
y el texto se coloca como en la referencia (pregunta arriba a la izquierda,
respuesta a la derecha, entre comillas).

Uso: python3 tools/generar_frames.py guiones/puerta-abierta.json
Salida: series/<nombre>/NN-<who>.png
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = f"{cur} {word}".strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def block(draw, text, size, x, y, max_w, align):
    font = ImageFont.truetype(FONT, size)
    for line in wrap(draw, f"“{text}”", font, max_w):
        w = draw.textlength(line, font=font)
        draw.text((x if align == "left" else x - w, y), line, font=font, fill="white")
        y += int(size * 1.25)
    return y


def frame(who, text, text2, base):
    img = Image.open(base).convert("RGB")
    d = ImageDraw.Draw(img)
    W, H = img.size
    m = int(W * 0.08)
    if who == "gris":
        block(d, text, int(W * 0.055), m, int(H * 0.06), W - 2 * m, "left")
    elif who == "palido":
        block(d, text, int(W * 0.048), W - m, int(H * 0.08), int(W * 0.68), "right")
    else:
        y = block(d, text, int(W * 0.055), m, int(H * 0.04), W - 2 * m, "left")
        block(d, text2, int(W * 0.048), W - m, y + int(H * 0.015), int(W * 0.68), "right")
    return img


def main(path):
    path = Path(path)
    out = ROOT / "series" / path.stem
    out.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(json.loads(path.read_text()), 1):
        img = frame(f["who"], f["text"], f.get("text2"), ROOT / "assets/base" / f"{f['who']}.png")
        img.save(out / f"{i:02d}-{f['who']}.png")
    print(out, i, "frames")


if __name__ == "__main__":
    main(sys.argv[1])
