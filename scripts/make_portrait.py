#!/usr/bin/env python3
import sys
import os
import numpy as np
from PIL import Image, ImageEnhance

RAMP = " .`:-=+*cs#%@"
COLS = 90
ROW_RATIO = 0.48
CHAR_W = 7.74
FONT_SIZE = 12.9
LINE_H = 15
ROW_DELAY = 0.09
FAMILY = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FG_LIGHT = "#6e7681"
FG_DARK = "#c9d1d9"

def prep(path):
    src = Image.open(path).convert("RGBA")
    # Composite over white background
    white = Image.new("RGBA", src.size, (255, 255, 255, 255))
    comp = Image.alpha_composite(white, src).convert("L")
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(comp)
    enhanced = enhancer.enhance(1.7)
    
    arr = np.array(enhanced)
    # Apply darkening curve
    darkened = (255.0 * (arr / 255.0) ** 1.5).astype("uint8")
    return Image.fromarray(darkened)

def to_lines(img, cols=COLS):
    w, h = img.size
    rows = int(cols * (h / w) * ROW_RATIO)
    img_resized = img.resize((cols, rows), Image.LANCZOS)
    
    px = list(img_resized.getdata())
    n = len(RAMP)

    out = []
    for r in range(rows):
        chars = []
        for c in range(cols):
            val = px[r * cols + c]
            idx = min(n - 1, int((1 - val / 255.0) ** 1.0 * n))
            chars.append(RAMP[idx])
        out.append("".join(chars).rstrip())

    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out

def build_svg(lines, cols=COLS):
    pad = 14
    width = int(cols * CHAR_W + pad * 2)
    height = len(lines) * LINE_H + pad * 2

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
         f'height="{height}" viewBox="0 0 {width} {height}" '
         f'font-family="{FAMILY}">',
         f'<style>.a{{fill:{FG_LIGHT}}}'
         f'@media(prefers-color-scheme:dark){{.a{{fill:{FG_DARK}}}}}</style>']

    for i, line in enumerate(lines):
        y = pad + i * LINE_H
        begin = f"{i * ROW_DELAY:.2f}s"
        end = f"{(i + 1) * ROW_DELAY:.2f}s"
        w = max(len(line), 1) * CHAR_W
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        p.append(f'<clipPath id="c{i}"><rect x="{pad}" y="{y}" '
                 f'height="{LINE_H}" width="0">'
                 f'<animate attributeName="width" from="0" to="{w:.1f}" '
                 f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
                 f'</rect></clipPath>')
        p.append(f'<g clip-path="url(#c{i})"><text xml:space="preserve" '
                 f'x="{pad}" y="{y + 11.2:.1f}" class="a" '
                 f'font-size="{FONT_SIZE}">{safe}</text></g>')
        p.append(f'<rect y="{y + 1}" width="6" height="12" class="a" opacity="0">'
                 f'<animate attributeName="x" from="{pad}" to="{pad + w:.1f}" '
                 f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
                 f'<set attributeName="opacity" to="0.8" begin="{begin}"/>'
                 f'<set attributeName="opacity" to="0" begin="{end}"/></rect>')

    p.append("</svg>")
    return "".join(p)

def main():
    photo_path = sys.argv[1] if len(sys.argv) > 1 else r"A:\ANKITESH\Github\ChatGPT Image Jul 21, 2026, 09_03_09 PM.png"
    out_svg = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ascii.svg")
    
    img = prep(photo_path)
    lines = to_lines(img, cols=COLS)
    
    svg = build_svg(lines, cols=COLS)
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {out_svg} ({len(lines)} lines)")

if __name__ == "__main__":
    main()
