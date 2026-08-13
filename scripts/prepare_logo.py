"""Build a readable web logo from the small source PNG.

Keeps soft anti-aliased strokes (no binary threshold / vector trace).
"""

from pathlib import Path

from PIL import Image, ImageFilter

root = Path(__file__).resolve().parents[1]
src = root / "assets" / "logo_siringa.png"
out = root / "assets" / "logo_siringa_hq.png"

im = Image.open(src).convert("RGBA")

# 4x LANCZOS keeps letterforms; light unsharp makes thin strokes pop on light bg
hi = im.resize((im.width * 4, im.height * 4), Image.Resampling.LANCZOS)
r, g, b, a = hi.split()

# Solid dark ink; readability comes from original alpha (anti-aliased edges)
ink = Image.new("L", hi.size, 20)
logo = Image.merge("RGBA", (ink, ink, ink, a))

# Mild unsharp on alpha only would be complex; sharpen RGB+A together gently
logo = logo.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))

# Re-apply cleaned alpha so sharpening doesn't muddy transparency
a2 = a.point(lambda v: 0 if v < 8 else v)
logo.putalpha(a2)

bbox = logo.getbbox()
if bbox:
    pad = 12
    logo = logo.crop(
        (
            max(bbox[0] - pad, 0),
            max(bbox[1] - pad, 0),
            min(bbox[2] + pad, logo.width),
            min(bbox[3] + pad, logo.height),
        )
    )

logo.save(out, "PNG", optimize=True)
print(f"saved {out} {logo.size}")
