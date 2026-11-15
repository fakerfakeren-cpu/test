#!/usr/bin/env python3
"""Download real elevation and land cover around Sofia for the Evil Sofia map.

Writes tools/geodata/sofia_geodata.npz with two arrays on one regular lat/lon grid:
  elevation  int16, metres     (AWS Terrain Tiles, Terrarium encoding, zoom 11; SRTM and other sources)
  landcover  uint8, ESA WorldCover 2021 classes (10 tree cover, 20 shrubland, 30 grassland, 40 cropland,
             50 built-up, 60 bare/sparse, 70 snow, 80 water, 90 wetland, 95 mangrove, 100 moss)
Data: ESA WorldCover 2021 (CC BY 4.0, (c) ESA WorldCover project / Copernicus Sentinel data 2021);
AWS Terrain Tiles (Mapzen / Linux Foundation; SRTM and other public sources).

Downloads go to tools/geodata/cache/ (about 175 MB, not committed). Requires: numpy pillow scipy tifffile, curl.
Usage:  python3 tools/fetch_geodata.py      (run from the evil-sofia/ folder)
"""
import math
import os
import subprocess
import numpy as np
import tifffile
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, "tools", "geodata")
CACHE = os.path.join(GEO, "cache")
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = 42.15, 43.25, 21.60, 25.05
RES = 0.0005          # degrees per grid cell (about 55 m north-south, 41 m east-west)
ZOOM = 11


def fetch(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["curl", "-sSf", "-m", "900", "--retry", "3", "-o", path + ".part", url], check=True)
    os.replace(path + ".part", path)
    return path


lats = LAT_MAX - (np.arange(round((LAT_MAX - LAT_MIN) / RES)) + 0.5) * RES
lons = LON_MIN + (np.arange(round((LON_MAX - LON_MIN) / RES)) + 0.5) * RES
LAT, LON = np.meshgrid(lats, lons, indexing="ij")

# ---------------------------------------------------------------- elevation (Terrarium PNG tiles)
n = 2 ** ZOOM


def tile_xy(lat, lon):
    x = (lon + 180) / 360 * n
    y = (1 - np.arcsinh(np.tan(np.radians(lat))) / math.pi) / 2 * n
    return x, y


tx0, ty0 = (int(v) for v in tile_xy(LAT_MAX, LON_MIN))
tx1, ty1 = (int(v) for v in tile_xy(LAT_MIN, LON_MAX))
mosaic = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), np.float32)
for tx in range(tx0, tx1 + 1):
    for ty in range(ty0, ty1 + 1):
        p = fetch(f"https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{ZOOM}/{tx}/{ty}.png",
                  os.path.join(CACHE, "terrarium", str(ZOOM), str(tx), f"{ty}.png"))
        rgb = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
        mosaic[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = \
            rgb[..., 0] * 256 + rgb[..., 1] + rgb[..., 2] / 256 - 32768
print(f"elevation: {(tx1 - tx0 + 1) * (ty1 - ty0 + 1)} tiles")
gx, gy = tile_xy(LAT, LON)
elev = ndi.map_coordinates(mosaic, [(gy - ty0) * 256 - 0.5, (gx - tx0) * 256 - 0.5], order=1, mode="nearest")
elevation = np.clip(np.round(elev), -500, 9000).astype(np.int16)

# ---------------------------------------------------------------- land cover (ESA WorldCover 2021, 3x3 degree COG tiles)
landcover = np.zeros(LAT.shape, np.uint8)
for lon0 in range(int(LON_MIN // 3 * 3), int(LON_MAX), 3):
    lat0 = int(LAT_MIN // 3 * 3)
    name = f"ESA_WorldCover_10m_2021_v200_N{lat0:02d}E{lon0:03d}_Map.tif"
    p = fetch(f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/{name}",
              os.path.join(CACHE, "worldcover", name))
    with tifffile.TiffFile(p) as tif:
        level = tif.series[0].levels[2]          # 4x overview: 1/3000 degree per pixel
        arr = level.asarray()
    per_deg = arr.shape[1] / 3
    sel = (LON >= lon0) & (LON < lon0 + 3) & (LAT >= lat0) & (LAT < lat0 + 3)
    rows = np.clip(((lat0 + 3 - LAT[sel]) * per_deg).astype(int), 0, arr.shape[0] - 1)
    cols = np.clip(((LON[sel] - lon0) * per_deg).astype(int), 0, arr.shape[1] - 1)
    landcover[sel] = arr[rows, cols]
    print(f"land cover: {name}")

np.savez_compressed(os.path.join(GEO, "sofia_geodata.npz"), elevation=elevation, landcover=landcover,
                    bounds=np.array([LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, RES]))
print("elevation range", int(elevation.min()), int(elevation.max()), "m; land cover classes",
      sorted(set(np.unique(landcover).tolist())))
