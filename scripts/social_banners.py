"""Render sharing cards from the repository's historical fire records.

Run `py scripts/social_banners.py` with Pillow installed. Typography and
colors follow the site's Fira Sans / Chulapa Deeply configuration.
Bundled municipal centers and regional geometry come from mapSpain (IGN).
"""

import csv
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "scripts/assets"
ORANGE = "#ff550b"
SCALE = 2


def render(width, height, filename):
    sx, sy = width / 1280 * SCALE, height / 640 * SCALE
    canvas = Image.new("RGB", (width*SCALE, height*SCALE), "black")
    draw = ImageDraw.Draw(canvas)

    def project(lon, lat):
        inset_shift = 160 if lat < 36.4 and lon < -8 else 0
        return ((565 + (lon + 10) * 48 + inset_shift) * sx,
                (95 + (44.5 - lat) * 52) * sy)

    regions = json.loads((ASSETS / "regions.geojson").read_text())
    for feature in regions["features"]:
        geometry = feature["geometry"]
        polygons = ([geometry["coordinates"]] if geometry["type"] == "Polygon"
                    else geometry["coordinates"])
        for polygon in polygons:
            points = [project(*point[:2]) for point in polygon[0]]
            draw.polygon(points, fill="#191919", outline="#383838", width=2)
            for ring in polygon[1:]:
                draw.polygon([project(*point[:2]) for point in ring], fill="black")

    with (ASSETS / "municipal-centers.csv").open(encoding="utf-8") as stream:
        centers = {row["codmun"].zfill(5): (float(row["lon"]), float(row["lat"]))
                   for row in csv.DictReader(stream)}
    totals = {}
    with (ROOT / "rdata/gif_d2010.csv").open(encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    for row in records:
        code = row["codmun"].zfill(5)
        if code not in centers:
            raise ValueError(f"Missing municipal center: {code}")
        totals[code] = totals.get(code, 0) + float(row["area_forestal_ha"])

    glow = Image.new("RGB", canvas.size)
    glow_draw = ImageDraw.Draw(glow)
    for code, area in totals.items():
        x, y = project(*centers[code])
        r = max(1.6, math.sqrt(area) * .047) * sx
        glow_draw.ellipse((x-r*2, y-r*2, x+r*2, y+r*2), fill="#b62203")
    from PIL import ImageChops
    canvas = ImageChops.add(canvas, glow.filter(ImageFilter.GaussianBlur(12*SCALE)))
    draw = ImageDraw.Draw(canvas)
    for code, area in sorted(totals.items(), key=lambda item: -item[1]):
        x, y = project(*centers[code])
        r = max(1.6, math.sqrt(area) * .047) * sx
        draw.ellipse((x-r, y-r, x+r, y+r), fill=ORANGE)

    mask = Image.new("L", canvas.size)
    ramp = [round(255 * (1 - max(0, min(1, (x/canvas.width - .34)/.29))))
            for x in range(canvas.width)]
    mask.putdata(ramp * canvas.height)
    canvas = Image.composite(Image.new("RGB", canvas.size), canvas, mask)
    draw = ImageDraw.Draw(canvas)

    def text(x, y, value, size, color="white", bold=False):
        font = ImageFont.truetype(str(ASSETS / "fira-sans" /
            ("FiraSans-Bold.ttf" if bold else "FiraSans-Regular.ttf")), round(size*sx))
        draw.text((round(x*sx), round(y*sy)), value, font=font,
                  fill=color, anchor="lt")

    years = sorted({record["date"][:4] for record in records})
    text(64, 66, f"DATOS ABIERTOS · {years[0]}–{years[-1]}", 20, ORANGE, True)
    for y, title in [(140, "Grandes"), (230, "incendios"), (320, "forestales")]:
        text(60, y, title, 80, bold=True)
    text(64, 435, "España, incendio a incendio.", 27, "#cccccc")
    text(64, 477, "A partir de 500 ha forestales.", 25, "#cccccc")
    text(64, 565, "Explora el mapa. Descarga los datos.", 20)
    draw.rectangle((948*sx, 596*sy, width*SCALE, height*SCALE), fill="black")
    text(966, 607, "Datos: MITECO · Mapa: IGN", 12, "#cccccc")
    canvas = canvas.resize((width, height), Image.Resampling.LANCZOS)
    path = ROOT / "assets" / filename
    canvas.save(path, quality=95, subsampling=0, optimize=True)
    print(f"{filename}: {width} × {height}; {len(records)} fire records")


if __name__ == "__main__":
    render(1200, 630, "social-preview.jpg")
    render(1280, 640, "github-preview.jpg")
