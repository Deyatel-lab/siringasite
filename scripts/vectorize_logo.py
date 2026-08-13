from pathlib import Path

import vtracer
from PIL import Image, ImageFilter, ImageOps

root = Path(__file__).resolve().parents[1]
src = root / "assets" / "logo_siringa.png"
trace_png = root / "assets" / "_logo_trace_src.png"
out_svg = root / "assets" / "logo_siringa.svg"
out_png = root / "assets" / "logo_siringa_hq.png"

im = Image.open(src).convert("RGBA")
alpha = im.getchannel("A")

# Upsample alpha, soft blur, hard threshold -> clean silhouette
scale = 16
hi = alpha.resize((alpha.width * scale, alpha.height * scale), Image.Resampling.LANCZOS)
hi = hi.filter(ImageFilter.GaussianBlur(radius=1.4))
mask = hi.point(lambda a: 255 if a >= 90 else 0)

# Tiny morphological close via max/min filters to fill pinholes
mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))

pad = 64
padded_mask = ImageOps.expand(mask, border=pad, fill=0)

# Trace black logo on white
trace_rgb = ImageOps.invert(Image.merge("RGB", (padded_mask, padded_mask, padded_mask)))
trace_rgb.save(trace_png)

vtracer.convert_image_to_svg_py(
    str(trace_png),
    str(out_svg),
    colormode="binary",
    hierarchical="cutout",
    mode="spline",
    filter_speckle=8,
    color_precision=6,
    layer_difference=16,
    corner_threshold=80,
    length_threshold=5.0,
    max_iterations=12,
    splice_threshold=40,
    path_precision=2,
)

svg_text = out_svg.read_text(encoding="utf-8")
# Drop page-sized white fill rectangles if present
cleaned_paths = []
for chunk in svg_text.split("<path "):
    if not cleaned_paths:
        cleaned_paths.append(chunk)
        continue
    lower = chunk.lower()
    if 'fill="#ffffff"' in lower or "fill=\"white\"" in lower or 'fill="#fff"' in lower:
        continue
    chunk = chunk.replace('fill="#000000"', 'fill="#1C1C1E"').replace('fill="black"', 'fill="#1C1C1E"')
    cleaned_paths.append("<path " + chunk)
svg_text = "".join(cleaned_paths)
svg_text = svg_text.replace("<svg", '<svg role="img" aria-label="Сиринга"', 1)
out_svg.write_text(svg_text, encoding="utf-8")

# Crisp transparent PNG fallback
solid = Image.new("RGBA", padded_mask.size, (28, 28, 30, 255))
solid.putalpha(padded_mask)
bbox = solid.getbbox()
if bbox:
    solid = solid.crop(bbox)

target_w = 1200
ratio = target_w / solid.width
solid = solid.resize(
    (target_w, max(1, int(solid.height * ratio))),
    Image.Resampling.LANCZOS,
)
solid.save(out_png, "PNG", optimize=True)

trace_png.unlink(missing_ok=True)
print(f"svg {out_svg.stat().st_size} bytes")
print(f"png {out_png} {solid.size}")
# quick transparency sanity check
a = solid.getchannel("A")
vals = list(a.getdata())
print("opaque%", round(100 * sum(1 for v in vals if v > 200) / len(vals), 1))
print("transparent%", round(100 * sum(1 for v in vals if v < 10) / len(vals), 1))
