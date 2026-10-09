"""Render the Scar viewmodel exactly as the game frames it.

In-game camera (from the user's ViewModelController + Constants):
  model:PivotTo(camera.CFrame * VIEW_MODEL_OFFSET * adsShift), VIEW_MODEL_OFFSET = (0.9, -1.3, -1.3),
  pivot = HumanoidRootPart.  => hip camera = HRP * (-0.9, 1.3, 1.3), FOV 70.
  ADS (adsOffset (0.9, -0.2, 0), adsFov 40) => camera = HRP * (0, 1.1, 1.3), FOV 40.
Arms are drawn as their 0.6 x 0.6 x 4 parts (in game the controller hides them and welds a sleeve mesh on the
same spot; that mesh's exact shape is not in the place file).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from meshrender import raster, box_tris, shade, load  # noqa: E402

HIP_CAM = np.eye(4); HIP_CAM[:3, 3] = (-0.9, 1.3, 1.3)
ADS_CAM = np.eye(4); ADS_CAM[:3, 3] = (0.0, 1.1, 1.3)
SLEEVE = (176, 150, 128)


class Scene:
    def __init__(self, gltf, arm_size):
        self.mesh = load(gltf)
        self.arm = box_tris(np.asarray(arm_size))
        self.armcol = shade(self.arm, SLEEVE)

    def tris(self, W):
        Ts, Cs = [], []
        for name, (Tm, C) in self.mesh.items():
            M = W[name]; Ts.append(Tm @ M[:3, :3].T + M[:3, 3]); Cs.append(C)
        for name in ('RightArm', 'LeftArm'):
            M = W[name]; Ts.append(self.arm @ M[:3, :3].T + M[:3, 3]); Cs.append(self.armcol)
        return np.concatenate(Ts), np.concatenate(Cs)


def view(scene, W, cam=HIP_CAM, fov=70, Wd=640, Hd=360, ss=2, crosshair=False):
    Tw, C = scene.tris(W)
    iv = np.linalg.inv(cam)
    Tc = Tw @ iv[:3, :3].T + iv[:3, 3]
    f = (Hd * ss / 2) / np.tan(np.radians(fov / 2))
    img = Image.fromarray(raster(Tc, C, Wd * ss, Hd * ss, f, bg=(122, 134, 148))).resize((Wd, Hd), Image.BOX)
    if crosshair:
        d = ImageDraw.Draw(img); cx, cy = Wd // 2, Hd // 2
        d.line([(cx - 8, cy), (cx + 8, cy)], fill=(255, 40, 40)); d.line([(cx, cy - 8), (cx, cy + 8)], fill=(255, 40, 40))
    return img


def outside(scene, W, yaw=125, pitch=16, scale=95, Wd=420, Hd=360, ss=2, centre=(0.0, 0.2, -1.2)):
    Tw, C = scene.tris(W)
    y, p = np.radians(yaw), np.radians(pitch)
    fwd = np.array([np.sin(y) * np.cos(p), -np.sin(p), -np.cos(y) * np.cos(p)])
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    R = np.stack([right, up, -fwd])
    Tc = (Tw - np.array(centre)) @ R.T
    return Image.fromarray(raster(Tc, C, Wd * ss, Hd * ss, scale * ss, ortho=True, bg=(122, 134, 148))).resize((Wd, Hd), Image.BOX)


def label(img, text):
    d = ImageDraw.Draw(img); d.rectangle([0, 0, 8 + 7 * len(text), 16], fill=(20, 20, 20)); d.text((4, 2), text, fill=(255, 255, 255))
    return img
