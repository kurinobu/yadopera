#!/usr/bin/env python3
"""
PWA用アイコン生成: 192x192 と 512x512、円形外側を透過。
入力: docs/pic の BackgroundEraser PNG
出力: frontend/public/pwa-192x192.png, pwa-512x512.png
"""
from pathlib import Path
from PIL import Image
import math

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "docs" / "pic"
OUT_DIR = PROJECT_ROOT / "frontend" / "public"

# 入力: 3つのうち先頭を使用（必要なら変更可）
SRC_GLOB = "BackgroundEraser_*.png"
SIZES = (192, 512)


def apply_circular_mask(im: Image.Image) -> Image.Image:
    """画像に円形マスクを適用し、外側を透過させる。"""
    w, h = im.size
    radius = min(w, h) / 2.0
    cx, cy = w / 2.0, h / 2.0
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    pixels = im.load()
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            if math.sqrt(dx * dx + dy * dy) > radius:
                pixels[x, y] = (0, 0, 0, 0)
    return im


def main():
    src_files = sorted(SRC_DIR.glob(SRC_GLOB))
    if not src_files:
        raise SystemExit(f"No source image found in {SRC_DIR} with pattern {SRC_GLOB}")
    src_path = src_files[0]
    print(f"Source: {src_path}")

    img = Image.open(src_path).convert("RGBA")
    img = apply_circular_mask(img)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        out_path = OUT_DIR / f"pwa-{size}x{size}.png"
        resized.save(out_path, "PNG", optimize=True)
        print(f"Saved: {out_path} ({size}x{size})")


if __name__ == "__main__":
    main()
