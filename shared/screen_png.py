"""把模拟器里的屏幕（或程序的 stdout）渲染成 PNG。

图片是**产物**，不只是输入：一次读图如果没有落成仓库里的图或断言，这次读图就是纯消耗。
用法：
    python shared/screen_png.py problems/07-io/window-notepad --input "HELLO\u001b" \
        --out docs/images/window-notepad.png
    python shared/screen_png.py problems/07-io/prefix-dictionary \
        --input "1 cat 1 dog 2 c 3\n" --out docs/images/dict.png --stdout
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import asm86  # noqa: E402
import fasm  # noqa: E402

ROOT = HERE.parent
FONTS = [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]


def _font(size=14):
    from PIL import ImageFont
    for f in FONTS:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def screen_png(text: str, out: Path, cols=80, rows=25, cell=(8, 16), margin=8):
    from PIL import Image, ImageDraw
    font = _font(14)
    w = margin * 2 + cols * cell[0]
    h = margin * 2 + rows * cell[1]
    img = Image.new("RGB", (w, h), (12, 12, 12))
    draw = ImageDraw.Draw(img)
    lines = text.split("\n")
    for r in range(rows):
        line = lines[r] if r < len(lines) else ""
        for c, ch in enumerate(line[:cols]):
            if ch.strip():
                draw.text((margin + c * cell[0], margin + r * cell[1]),
                          ch, font=font, fill=(120, 220, 120))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def stdout_png(text: str, out: Path, cols=60, cell=(8, 16), margin=10):
    from PIL import Image, ImageDraw
    font = _font(14)
    lines = [ln.rstrip("\r") for ln in text.split("\n") if ln.strip() or True]
    if lines and lines[-1] == "":
        lines.pop()
    rows = max(1, len(lines))
    w = margin * 2 + cols * cell[0]
    h = margin * 2 + rows * cell[1]
    img = Image.new("RGB", (w, h), (12, 12, 12))
    draw = ImageDraw.Draw(img)
    for r, line in enumerate(lines):
        draw.text((margin, margin + r * cell[1]), line[:cols], font=font,
                  fill=(220, 220, 200))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("problem")
    ap.add_argument("--input", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--stdout", action="store_true", help="渲染 stdout 而不是屏幕")
    ns = ap.parse_args(argv)

    prob = Path(ns.problem).resolve()
    binp = ROOT / "build" / (prob.name + ".png.bin")
    ok, log = fasm.assemble(prob / "main.asm", binp)
    if not ok:
        print(log)
        return 1
    res = asm86.run_program(binp.read_bytes(), ns.input)
    if res["error"]:
        print("运行错误:", res["error"])
        return 1
    text = res["stdout"] if ns.stdout else res["screen"]
    out = Path(ns.out)
    if ns.stdout:
        stdout_png(text, out)
    else:
        screen_png(text, out)
    print("wrote", out, out.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
