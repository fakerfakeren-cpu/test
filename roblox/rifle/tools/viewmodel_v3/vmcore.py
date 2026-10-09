"""Scar viewmodel: rig + animations, built from the user's real AutoBlaster viewmodel (game.rbxl).

Everything is computed in the HumanoidRootPart frame (HRP = identity), x right, y up, -z forward.
Rig follows the template / the user's Glock viewmodel:
    HumanoidRootPart -> Body (BodyJoint) -> RightArm (RightArmJoint)
                                         -> Magazine (MagazineJoint) -> LeftArm (LeftArmJoint)
                                         -> Slide (SlideJoint)
Rest pose (all Transforms identity) = the hip holding pose, gun exactly where the user has it now.
Roblox joint rule: Part1 = Part0 * C0 * Transform * C1^-1.
"""
import json
import math
import numpy as np

# ---------------------------------------------------------------- CFrame helpers (4x4)

def T(x=0.0, y=0.0, z=0.0):
    M = np.eye(4); M[:3, 3] = (x, y, z); return M


def Rx(a):
    c, s = math.cos(a), math.sin(a); M = np.eye(4); M[1:3, 1:3] = [[c, -s], [s, c]]; return M


def Ry(a):
    c, s = math.cos(a), math.sin(a); M = np.eye(4); M[0, 0] = c; M[0, 2] = s; M[2, 0] = -s; M[2, 2] = c; return M


def Rz(a):
    c, s = math.cos(a), math.sin(a); M = np.eye(4); M[0:2, 0:2] = [[c, -s], [s, c]]; return M


def inv(M):
    R = M[:3, :3]; p = M[:3, 3]; I = np.eye(4); I[:3, :3] = R.T; I[:3, 3] = -R.T @ p; return I


def from_list(v):
    """[x,y,z, R00..R22] -> 4x4"""
    M = np.eye(4); M[:3, 3] = v[:3]; M[:3, :3] = np.array(v[3:12]).reshape(3, 3); return M


def to_list(M):
    return list(M[:3, 3]) + list(M[:3, :3].reshape(-1))


def ortho(M):
    """Re-orthonormalise rotation (Gram-Schmidt on columns, keep Z then Y)."""
    R = M[:3, :3]
    z = R[:, 2] / np.linalg.norm(R[:, 2])
    y = R[:, 1] - z * (z @ R[:, 1]); y /= np.linalg.norm(y)
    x = np.cross(y, z)
    N = M.copy(); N[:3, :3] = np.stack([x, y, z], 1); return N


def rot_xyz(pitch, yaw, roll):
    """Gun-style rotation: yaw about Y, then pitch about X, then roll about Z (degrees)."""
    return Ry(math.radians(yaw)) @ Rx(math.radians(pitch)) @ Rz(math.radians(roll))


def pt(M, p):
    return M[:3, :3] @ np.asarray(p, float) + M[:3, 3]

# ---------------------------------------------------------------- curves


class Curve:
    """Monotone-preserving cubic (PCHIP) through keys; flat ends. keys: [(t, value), ...]"""

    def __init__(self, keys):
        keys = sorted(keys)
        self.t = np.array([k[0] for k in keys], float)
        self.v = np.array([k[1] for k in keys], float)
        n = len(self.t)
        h = np.diff(self.t); d = np.diff(self.v) / h if n > 1 else np.array([])
        m = np.zeros(n)
        for i in range(1, n - 1):
            if d[i - 1] * d[i] <= 0:
                m[i] = 0.0
            else:
                w1 = 2 * h[i] + h[i - 1]; w2 = h[i] + 2 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
        self.m = m  # end slopes 0: every move starts and ends at rest

    def __call__(self, t):
        tt, v, m = self.t, self.v, self.m
        if t <= tt[0]:
            return v[0]
        if t >= tt[-1]:
            return v[-1]
        i = int(np.searchsorted(tt, t) - 1)
        h = tt[i + 1] - tt[i]; s = (t - tt[i]) / h
        h00 = 2 * s ** 3 - 3 * s ** 2 + 1; h10 = s ** 3 - 2 * s ** 2 + s
        h01 = -2 * s ** 3 + 3 * s ** 2; h11 = s ** 3 - s ** 2
        return h00 * v[i] + h10 * h * m[i] + h01 * v[i + 1] + h11 * h * m[i + 1]


def curves(table):
    """table: {name: [(t, v), ...]} -> {name: Curve}"""
    return {k: Curve(v) for k, v in table.items()}


def smoother(x):
    x = min(max(x, 0.0), 1.0); return x * x * x * (x * (6 * x - 15) + 10)


def window(t, a, b):
    """0 before a, 1 after b, smootherstep between."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return smoother((t - a) / (b - a))

# ---------------------------------------------------------------- scene from the user's place


def load_scene(game_json):
    d = json.load(open(game_json))
    inst = {x['ref']: x for x in d['instances']}

    def name(r): return inst[r]['props'].get('Name', '?')

    def path(r):
        parts = []
        while r in inst:
            parts.append(name(r)); r = inst[r]['parent']
        return '.'.join(reversed(parts))
    base = 'ReplicatedStorage.Blaster.ViewModels.AutoBlaster'
    by_path = {path(r): x for r, x in inst.items() if path(r).startswith(base)}

    def cfp(p): return from_list(by_path[base + p]['props']['CFrame'])
    H = cfp('.HumanoidRootPart')
    S = {
        'H_world': H,
        'Body': inv(H) @ cfp('.Scar.Body'),
        'Magazine': inv(H) @ cfp('.Scar.Magazine'),
        'Slide': inv(H) @ cfp('.Scar.Slide'),
        'RightArm_old': inv(H) @ cfp('.RightArm'),
        'LeftArm_old': inv(H) @ cfp('.LeftArm'),
        'muzzle_local': from_list(by_path[base + '.Scar.Body.MuzzleAttachment']['props']['CFrame']),
        'arm_size': np.array(by_path[base + '.RightArm']['props']['size']),
        'sizes': {k: np.array(by_path[base + p]['props']['size']) for k, p in
                  (('Body', '.Scar.Body'), ('Magazine', '.Scar.Magazine'), ('Slide', '.Scar.Slide'),
                   ('HumanoidRootPart', '.HumanoidRootPart'), ('RightArm', '.RightArm'), ('LeftArm', '.LeftArm'))},
        'inst': inst, 'by_path': by_path, 'base': base,
    }
    return S

# ---------------------------------------------------------------- rig layout (Body-local / part-local points)

# Body local: +Z = muzzle, +X = player's LEFT (the Body is turned 180 deg in the viewmodel), +Y up.
PIVOT_BODY = np.array([0.0, -0.10, -0.45])     # top of the pistol grip: the gun turns about the right hand
RIGHT_HAND_BODY = np.array([-0.20, -0.30, -0.575])  # right-arm front end, wrapped on the pistol grip
LEFT_HAND_BODY = np.array([0.06, -0.08, 0.70])  # left-arm front end, under the handguard just ahead of the magwell
MAG_GRAB_MAG = np.array([0.12, -0.12, 0.0])     # left hand on the magazine (player's side, lower half)
MAG_PIVOT_MAG = np.array([0.0, 0.28, 0.0])      # magazine joint at the top of the magazine (where it seats)
CHARGER_GRAB_SLIDE = np.array([0.26, -0.08, -0.04])  # left hand pinching the charging handle (outboard side)

# Arm directions in the rest pose (unit vectors from the hand back to the shoulder, HRP frame)
RIGHT_DIR = np.array([0.30, -0.55, 0.78])
LEFT_DIR = np.array([-0.22, -0.78, 0.58])
ARM_HALF = 2.0                                  # arms are 0.6 x 0.6 x 4, hand at local z = -2


class Rig:
    def __init__(self, S):
        self.S = S
        G0 = S['Body']
        self.G0 = G0
        # Gun pivot frame: at the grip top, axes aligned with the HRP (so Transform = gun motion as seen by the player)
        p = pt(G0, PIVOT_BODY)
        self.F0 = T(*p)
        self.mag_rel = inv(G0) @ S['Magazine']        # seated magazine in Body space (pure translation)
        self.slide_rel = inv(G0) @ S['Slide']
        rh = pt(G0, RIGHT_HAND_BODY); lh = pt(G0, LEFT_HAND_BODY)
        self.shoulder_R = rh + 4.0 * RIGHT_DIR / np.linalg.norm(RIGHT_DIR)
        self.shoulder_L = lh + 4.0 * LEFT_DIR / np.linalg.norm(LEFT_DIR)
        # Rest poses = hip holding pose
        self.rest = self.pose(np.eye(4), np.eye(4), 0.0, rh, lh)
        R = self.rest
        # Joints: (name, Part0, Part1, C0, C1) with rest Transform = identity
        C1_body = inv(G0) @ self.F0                      # pivot at the grip top, HRP-aligned axes
        C1_arm = T(0, 0, -ARM_HALF)                      # template: joint at the hand end of the arm
        C1_mag = T(*MAG_PIVOT_MAG)
        self.joints = [
            ('BodyJoint', 'HumanoidRootPart', 'Body', np.eye(4) @ R['Body'] @ C1_body, C1_body),
            ('RightArmJoint', 'Body', 'RightArm', inv(R['Body']) @ R['RightArm'] @ C1_arm, C1_arm),
            ('MagazineJoint', 'Body', 'Magazine', inv(R['Body']) @ R['Magazine'] @ C1_mag, C1_mag),
            ('LeftArmJoint', 'Magazine', 'LeftArm', inv(R['Magazine']) @ R['LeftArm'] @ C1_arm, C1_arm),
            ('SlideJoint', 'Body', 'Slide', inv(R['Body']) @ R['Slide'], np.eye(4)),
        ]

    def arm(self, hand, shoulder):
        d = shoulder - hand; d /= np.linalg.norm(d)
        up = np.array([0.0, 1.0, 0.0])
        y = up - d * (up @ d); y /= np.linalg.norm(y)
        x = np.cross(y, d)
        M = np.eye(4); M[:3, :3] = np.stack([x, y, d], 1); M[:3, 3] = hand + ARM_HALF * d
        return M

    def gun(self, D):
        """D: gun motion in the pivot frame -> Body CFrame (HRP frame)."""
        return self.F0 @ D @ inv(self.F0) @ self.G0

    def pose(self, D, mag_off, slide_back, right_hand=None, left_hand=None):
        G = self.gun(D)
        Mg = G @ self.mag_rel @ T(*MAG_PIVOT_MAG) @ mag_off @ T(*(-MAG_PIVOT_MAG))
        Sl = G @ self.slide_rel @ T(0, 0, -slide_back)
        rh = pt(G, RIGHT_HAND_BODY) if right_hand is None else right_hand
        lh = pt(G, LEFT_HAND_BODY) if left_hand is None else left_hand
        return {'HumanoidRootPart': np.eye(4), 'Body': G, 'Magazine': Mg, 'Slide': Sl,
                'RightArm': self.arm(rh, self.shoulder_R), 'LeftArm': self.arm(lh, self.shoulder_L)}

    def solve(self, W):
        """World poses (HRP frame) -> Transform per joint name."""
        out = {}
        for name, p0, p1, C0, C1 in self.joints:
            out[name] = ortho(inv(C0) @ inv(W[p0]) @ W[p1] @ C1)
        return out

    def replay(self, transforms):
        """Transforms per joint -> world poses, walking the hierarchy (independent check of solve)."""
        W = {'HumanoidRootPart': np.eye(4)}
        pending = list(self.joints)
        while pending:
            rest = []
            for j in pending:
                name, p0, p1, C0, C1 = j
                if p0 in W:
                    W[p1] = W[p0] @ C0 @ transforms.get(name, np.eye(4)) @ inv(C1)
                else:
                    rest.append(j)
            pending = rest
        return W

# ---------------------------------------------------------------- animations


def gun_D(c, t):
    return T(c['x'](t), c['y'](t), c['z'](t)) @ rot_xyz(c['pitch'](t), c['yaw'](t), c['roll'](t))


IDLE_LEN = 4.0


def idle_D(t):
    w = 2 * math.pi / IDLE_LEN
    x = 0.004 * math.sin(w * t + 1.3)
    y = 0.007 * math.sin(w * t) + 0.002 * math.sin(2 * w * t + 0.7)
    z = 0.003 * math.sin(2 * w * t)
    pitch = 0.30 * math.sin(w * t + 0.4)
    yaw = 0.20 * math.sin(w * t + 2.0)
    roll = 0.35 * math.sin(w * t + 1.0)
    return T(x, y, z) @ rot_xyz(pitch, yaw, roll)


def idle_left_offset(t):
    w = 2 * math.pi / IDLE_LEN
    return np.array([0.004 * math.sin(w * t + 2.2), 0.005 * math.sin(2 * w * t + 0.3), 0.0])


def anim_idle(rig, t):
    D = idle_D(t)
    G = rig.gun(D)
    lh = pt(G, LEFT_HAND_BODY + idle_left_offset(t))
    return rig.pose(D, np.eye(4), 0.0, None, lh)


EQUIP_LEN = 0.70
EQUIP = curves({
    'x':     [(0, 0.28), (0.20, 0.05), (0.34, -0.010), (0.48, 0.002), (0.60, 0.0)],
    'y':     [(0, -0.95), (0.20, -0.10), (0.34, 0.022), (0.48, -0.004), (0.60, 0.0)],
    'z':     [(0, 0.40), (0.20, 0.07), (0.34, -0.012), (0.48, 0.002), (0.60, 0.0)],
    'pitch': [(0, -34.0), (0.20, -5.0), (0.34, 2.6), (0.48, -0.5), (0.60, 0.0)],
    'yaw':   [(0, -14.0), (0.20, -2.0), (0.34, 0.8), (0.48, -0.15), (0.60, 0.0)],
    'roll':  [(0, -26.0), (0.20, -5.0), (0.34, 2.2), (0.48, -0.4), (0.60, 0.0)],
})


def anim_equip(rig, t):
    D = idle_D(t) @ gun_D(EQUIP, t)          # converges to the idle pose at the same clock time
    G = rig.gun(D)
    # left hand reaches the handguard a beat after the gun arrives
    k = window(t, 0.10, 0.38)
    off = (1 - k) * np.array([-0.06, -0.40, 0.18]) + math.sin(math.pi * k) * np.array([-0.04, 0.05, 0.0])
    grab = window(t, 0.36, 0.42) * (1 - window(t, 0.42, 0.52)) * 0.018   # small squeeze as it lands
    lh_body = LEFT_HAND_BODY + idle_left_offset(t) + np.array([0, grab, 0])
    lh = pt(G, lh_body) + (rig.F0[:3, :3] @ off)
    return rig.pose(D, np.eye(4), 0.0, None, lh)


SHOOT_LEN = 0.25
SHOOT = curves({
    'x':     [(0, 0.0), (0.017, 0.004), (0.033, 0.005), (0.067, 0.002), (0.10, 0.0005), (0.25, 0.0)],
    'y':     [(0, 0.0), (0.017, 0.011), (0.033, 0.018), (0.067, 0.009), (0.10, 0.002), (0.15, -0.001), (0.25, 0.0)],
    'z':     [(0, 0.0), (0.017, 0.068), (0.033, 0.082), (0.067, 0.034), (0.10, 0.009), (0.15, -0.004), (0.25, 0.0)],
    'pitch': [(0, 0.0), (0.017, 1.7), (0.033, 2.4), (0.067, 1.1), (0.10, 0.32), (0.15, -0.12), (0.25, 0.0)],
    'yaw':   [(0, 0.0), (0.017, 0.12), (0.033, 0.15), (0.067, 0.06), (0.25, 0.0)],
    'roll':  [(0, 0.0), (0.017, -0.35), (0.033, -0.45), (0.067, -0.20), (0.10, -0.05), (0.25, 0.0)],
})
SHOOT_SLIDE = Curve([(0, 0.0), (0.017, 0.15), (0.033, 0.18), (0.05, 0.08), (0.067, 0.0), (0.25, 0.0)])


def anim_shoot(rig, t):
    return rig.pose(gun_D(SHOOT, t), np.eye(4), SHOOT_SLIDE(t))


RELOAD_LEN = 1.50
# gun: tilt to bring the magwell to the left hand, jolt on mag out / mag in, turn for the charging handle, settle
RELOAD = curves({
    'x':     [(0, 0), (0.20, -0.20), (0.30, -0.21), (0.62, -0.21), (0.86, -0.20), (1.00, -0.10), (1.12, -0.10), (1.36, 0.005), (1.50, 0)],
    'y':     [(0, 0), (0.20, 0.18), (0.28, 0.18), (0.32, 0.21), (0.40, 0.19), (0.62, 0.18), (0.84, 0.19), (0.875, 0.23), (0.93, 0.18),
              (1.02, 0.05), (1.06, 0.045), (1.11, 0.055), (1.36, -0.008), (1.50, 0)],
    'z':     [(0, 0), (0.20, -0.12), (0.98, -0.12), (1.03, -0.10), (1.08, -0.07), (1.12, -0.11), (1.36, 0.004), (1.50, 0)],
    'pitch': [(0, 0), (0.20, 12.0), (0.28, 12.5), (0.31, 14.5), (0.40, 12.6), (0.62, 12.2), (0.84, 12.0), (0.875, 9.5), (0.93, 12.2),
              (1.02, 5.0), (1.08, 4.0), (1.12, 5.2), (1.36, -1.0), (1.50, 0)],
    'yaw':   [(0, 0), (0.20, 14.0), (0.62, 15.0), (0.86, 14.5), (1.02, 8.0), (1.12, 8.0), (1.36, -0.8), (1.50, 0)],
    'roll':  [(0, 0), (0.20, -28.0), (0.28, -29.0), (0.31, -31.0), (0.40, -29.5), (0.62, -29.0), (0.86, -28.5), (0.89, -26.0),
              (0.95, -30.0), (1.02, -40.0), (1.12, -40.0), (1.36, 2.0), (1.50, 0)],
})
# magazine offset, Body-local (+X = player's left, +Z = muzzle), about the top of the magazine
MAG = curves({
    'x':     [(0, 0), (17 / 60, 0), (0.33, 0.01), (0.40, 0.15), (0.50, 0.55), (0.58, 0.55), (0.66, 0.25), (0.75, 0.06), (0.81, 0.015), (52 / 60, 0)],
    'y':     [(0, 0), (17 / 60, 0), (0.33, -0.12), (0.40, -0.55), (0.50, -2.00), (0.58, -2.00), (0.66, -0.90), (0.75, -0.30), (0.81, -0.08),
              (52 / 60, 0)],
    'z':     [(0, 0), (17 / 60, 0), (0.40, -0.04), (0.50, -0.15), (0.58, -0.12), (0.66, -0.02), (0.75, 0.02), (52 / 60, 0)],
    'rx':    [(0, 0), (17 / 60, 0), (0.40, -10.0), (0.50, -30.0), (0.58, 25.0), (0.66, 15.0), (0.75, 5.0), (0.81, 1.5), (52 / 60, 0)],
    'rz':    [(0, 0), (17 / 60, 0), (0.40, 6.0), (0.50, 18.0), (0.58, 14.0), (0.66, 8.0), (0.75, 2.0), (52 / 60, 0)],
})
RELOAD_SLIDE = Curve([(0, 0), (1.033, 0), (1.083, 0.47), (1.10, 0.47), (1.125, 0.0), (1.50, 0)])


def mag_off(t):
    c = MAG
    return T(c['x'](t), c['y'](t), c['z'](t)) @ Rx(math.radians(c['rx'](t))) @ Rz(math.radians(c['rz'](t)))


def anim_reload(rig, t):
    D = gun_D(RELOAD, t)
    G = rig.gun(D)
    mo = mag_off(t)
    sb = RELOAD_SLIDE(t)
    P = rig.pose(D, mo, sb)
    Mg, Sl = P['Magazine'], P['Slide']
    guard = pt(G, LEFT_HAND_BODY)
    on_mag = pt(Mg, MAG_GRAB_MAG)
    # hand pushes the new magazine home, then a short upward tap
    tap = window(t, 52 / 60, 0.89) * (1 - window(t, 0.90, 0.95)) * 0.035
    on_mag = on_mag + G[:3, :3] @ np.array([0, tap, 0])
    # the hand rides the handle back, then lets go: the handle snaps forward, the hand stays back and opens
    held = min(sb, 0.47) if t < 1.10 else 0.47
    on_charger = pt(G @ rig.slide_rel @ T(0, 0, -held), CHARGER_GRAB_SLIDE)
    released = window(t, 1.10, 1.15)
    on_charger = on_charger + G[:3, :3] @ (np.array([0.08, 0.04, 0.0]) * released)
    w_mag = window(t, 0.08, 0.24) * (1 - window(t, 0.90, 1.02))
    w_ch = window(t, 0.90, 1.02) * (1 - window(t, 1.12, 1.32))
    w_guard = 1 - w_mag - w_ch
    lh = w_guard * guard + w_mag * on_mag + w_ch * on_charger
    # arcs: hand lifts away from the gun while travelling between holds (no clipping through the receiver)
    lift = (math.sin(math.pi * window(t, 0.08, 0.24)) * np.array([0.10, -0.06, 0.04])
            + math.sin(math.pi * window(t, 0.90, 1.02)) * np.array([0.14, 0.04, 0.02])
            + math.sin(math.pi * window(t, 1.12, 1.32)) * np.array([0.12, -0.10, 0.0]))
    lh = lh + G[:3, :3] @ lift
    P['LeftArm'] = rig.arm(lh, rig.shoulder_L)
    return P


ANIMS = {
    # name: (length, fps, loop, priority enum value, sampler, markers [(time, name, value)], keyed joints)
    'Idle':   (IDLE_LEN, 30, True, 0, anim_idle, [], None),
    'Equip':  (EQUIP_LEN, 60, False, 2, anim_equip, [(0.0, 'Sound', 'Equip')], None),
    'Shoot':  (SHOOT_LEN, 60, False, 3, anim_shoot, [(0.0, 'RandomSound', 'Shoot')], ('BodyJoint', 'SlideJoint')),
    'Reload': (RELOAD_LEN, 60, False, 4, anim_reload,
               [(17 / 60, 'Sound', 'MagOut'), (52 / 60, 'Sound', 'MagIn'), (62 / 60, 'Sound', 'Charger')], None),
}
# Roblox Enum.AnimationPriority: Idle = 0, Movement = 1, Action = 2, Action2 = 3, Action3 = 4, Action4 = 5, Core = 1000


def sample(rig, name):
    length, fps, loop, prio, fn, markers, keyed = ANIMS[name]
    n = int(round(length * fps))
    frames = []
    for i in range(n + 1):
        t = round(i / fps, 6)
        W = fn(rig, t)
        frames.append((t, W, rig.solve(W)))
    return frames
