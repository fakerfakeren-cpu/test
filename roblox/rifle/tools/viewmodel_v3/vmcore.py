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
MAG_HOLD_MAG = np.array([0.10, -0.14, 0.02])    # left-arm front end holding the magazine: lower half, player's side
MAG_PIVOT_MAG = np.array([0.0, 0.28, 0.0])      # magazine joint at the top of the magazine (where it seats)
CHARGER_GRAB_SLIDE = np.array([0.26, -0.08, -0.04])  # left hand pinching the charging handle (outboard side)

# Arm directions in the rest pose (unit vectors from the hand back to the shoulder, HRP frame)
RIGHT_DIR = np.array([0.30, -0.55, 0.78])
LEFT_DIR = np.array([-0.22, -0.78, 0.58])
ARM_HALF = 2.0                                  # arms are 0.6 x 0.6 x 4, hand at local z = -2
SHOULDER_STAY = 0.3   # how much each shoulder stays put in the camera frame (0 = rides fully with the gun)


def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)


class Rig:
    def __init__(self, S):
        self.S = S
        G0 = S['Body']
        self.G0 = G0
        # Gun pivot frame: at the grip top, axes aligned with the HRP (so Transform = gun motion as seen by the player)
        self.F0 = T(*pt(G0, PIVOT_BODY))
        self.mag_rel = inv(G0) @ S['Magazine']        # seated magazine in Body space (pure translation)
        self.slide_rel = inv(G0) @ S['Slide']
        self.shoulder_R = pt(G0, RIGHT_HAND_BODY) + 4.0 * unit(RIGHT_DIR)
        self.shoulder_L = pt(S['Magazine'], MAG_HOLD_MAG) + 4.0 * unit(LEFT_DIR)
        self.shoulder_R_body = pt(inv(G0), self.shoulder_R)   # the same shoulders, carried in the gun's frame
        self.shoulder_L_body = pt(inv(G0), self.shoulder_L)
        # Rest poses = hip holding pose (left hand on the magazine)
        self.rest = self.pose(np.eye(4))
        R = self.rest
        # Joints: (name, Part0, Part1, C0, C1) with rest Transform = identity
        C1_body = inv(G0) @ self.F0                      # pivot at the grip top, HRP-aligned axes
        C1_arm = T(0, 0, ARM_HALF)                       # joint at the shoulder end, like the Glock viewmodel
        C1_mag = T(*MAG_PIVOT_MAG)
        self.joints = [
            ('BodyJoint', 'HumanoidRootPart', 'Body', np.eye(4) @ R['Body'] @ C1_body, C1_body),
            ('RightArmJoint', 'Body', 'RightArm', inv(R['Body']) @ R['RightArm'] @ C1_arm, C1_arm),
            ('MagazineJoint', 'Body', 'Magazine', inv(R['Body']) @ R['Magazine'] @ C1_mag, C1_mag),
            ('LeftArmJoint', 'Magazine', 'LeftArm', inv(R['Magazine']) @ R['LeftArm'] @ C1_arm, C1_arm),
            ('SlideJoint', 'Body', 'Slide', inv(R['Body']) @ R['Slide'], np.eye(4)),
        ]

    def arm(self, hand, shoulder, roll=0.0):
        """Arm part with its hand end on `hand`, pointing back at `shoulder`, twisted `roll` degrees about its length."""
        d = unit(shoulder - hand)
        up = np.array([0.0, 1.0, 0.0])
        y = unit(up - d * (up @ d))
        x = np.cross(y, d)
        if roll:
            c, s = math.cos(math.radians(roll)), math.sin(math.radians(roll))
            x, y = c * x + s * y, -s * x + c * y
        M = np.eye(4); M[:3, :3] = np.stack([x, y, d], 1); M[:3, 3] = hand + ARM_HALF * d
        return M

    def gun(self, D):
        """D: gun motion in the pivot frame -> Body CFrame (HRP frame)."""
        return self.F0 @ D @ inv(self.F0) @ self.G0

    def mag_in_gun(self, G, off=None):
        """Magazine CFrame for an offset (Body frame, about the top of the magazine); None = seated."""
        if off is None:
            return G @ self.mag_rel
        return G @ self.mag_rel @ T(*MAG_PIVOT_MAG) @ off @ T(*(-MAG_PIVOT_MAG))

    def pose(self, D, mag=None, slide_back=0.0, left_hand=None, sh_R=(0, 0, 0), sh_L=(0, 0, 0), roll_R=0.0, roll_L=0.0):
        """mag: Magazine CFrame (HRP frame) or None for seated. sh_*: shoulder offsets, roll_*: forearm twist (deg)."""
        G = self.gun(D)
        Mg = self.mag_in_gun(G) if mag is None else mag
        Sl = G @ self.slide_rel @ T(0, 0, -slide_back)
        lh = pt(Mg, MAG_HOLD_MAG) if left_hand is None else left_hand
        # shoulders mostly ride with the gun (the arms move with it, like the template), a little stays with the camera
        k = SHOULDER_STAY
        sR = (1 - k) * pt(G, self.shoulder_R_body) + k * self.shoulder_R
        sL = (1 - k) * pt(G, self.shoulder_L_body) + k * self.shoulder_L
        return {'HumanoidRootPart': np.eye(4), 'Body': G, 'Magazine': Mg, 'Slide': Sl,
                'RightArm': self.arm(pt(G, RIGHT_HAND_BODY), sR + np.asarray(sh_R, float), roll_R),
                'LeftArm': self.arm(lh, sL + np.asarray(sh_L, float), roll_L)}

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


def D_of(p):
    return T(p['x'], p['y'], p['z']) @ rot_xyz(p['pitch'], p['yaw'], p['roll'])


def gun_D(c, t):
    return D_of({k: c[k](t) for k in ('x', 'y', 'z', 'pitch', 'yaw', 'roll')})


def kick(t, t0, tau):
    """Impact response: 0 before t0, peaks (1.0) at t0 + tau, then dies away."""
    if t <= t0:
        return 0.0
    u = (t - t0) / tau
    return u * math.exp(1 - u)


IDLE_LEN = 4.0


def idle_params(t):
    w = 2 * math.pi / IDLE_LEN
    return dict(x=0.004 * math.sin(w * t + 1.3),
                y=0.007 * math.sin(w * t) + 0.002 * math.sin(2 * w * t + 0.7),
                z=0.003 * math.sin(2 * w * t),
                pitch=0.30 * math.sin(w * t + 0.4),
                yaw=0.20 * math.sin(w * t + 2.0),
                roll=0.35 * math.sin(w * t + 1.0))


def idle_D(t):
    return D_of(idle_params(t))


def idle_left_offset(t):
    w = 2 * math.pi / IDLE_LEN
    return np.array([0.004 * math.sin(w * t + 2.2), 0.005 * math.sin(2 * w * t + 0.3), 0.0])


def anim_idle(rig, t):
    p = idle_params(t)
    D = D_of(p)
    lh = pt(rig.mag_in_gun(rig.gun(D)), MAG_HOLD_MAG + idle_left_offset(t))
    return rig.pose(D, left_hand=lh)


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
    # left hand comes up from below and takes the magazine a beat after the gun arrives
    k = window(t, 0.10, 0.38)
    off = (1 - k) * np.array([-0.06, -0.40, 0.18]) + math.sin(math.pi * k) * np.array([-0.04, 0.05, 0.0])
    grab = window(t, 0.36, 0.42) * (1 - window(t, 0.42, 0.52)) * 0.018   # small squeeze as it lands
    lh = pt(rig.mag_in_gun(G), MAG_HOLD_MAG + idle_left_offset(t) + np.array([0, grab, 0])) + off
    return rig.pose(D, left_hand=lh)       # the arms come up with the gun: their shoulders ride with it


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
    return rig.pose(gun_D(SHOOT, t), slide_back=SHOOT_SLIDE(t))


# ---- reload: 1.5 s (= the tool's reloadTime). Mag out, flicked away spinning, fresh mag from below, seat, tap,
#      rack the charging handle, back to the hold. Sound events are frame-aligned.
RELOAD_LEN = 1.50
T_MAGOUT, T_MAGIN, T_CHARGER = 14 / 60, 50 / 60, 64 / 60
T_THROW = 0.38            # magazine leaves the hand
T_SWAP = 0.56             # fresh magazine is in the hand (hand and old mag both off-screen)
POSE_TILT = dict(x=-0.18, y=0.16, z=-0.10, pitch=11.0, yaw=13.0, roll=-27.0)
POSE_CHARGE = dict(x=-0.09, y=0.05, z=-0.10, pitch=5.0, yaw=8.0, roll=-40.0)
GRAVITY = np.array([0.0, -22.0, 0.0])
THROW_LIFT = np.array([-1.5, -3.5, 1.2])                     # fling it down and out to the left, past the camera
THROW_SPIN = np.radians(np.array([-260.0, 0.0, 820.0]))      # deg/s about the magazine's own X and Z


def reload_params(t):
    a, b, c = window(t, 0.0, 0.22), window(t, 0.92, 1.04), window(t, 1.16, 1.44)
    p = {k: POSE_TILT[k] * a + (POSE_CHARGE[k] - POSE_TILT[k]) * b - POSE_CHARGE[k] * c for k in POSE_TILT}
    s = math.sin(math.pi * window(t, 1.36, 1.50))          # small settle as it lands back in the hold
    p['pitch'] -= 0.8 * s; p['roll'] += 1.5 * s; p['y'] -= 0.006 * s
    fade = 1 - window(t, 1.40, 1.50)
    k = kick(t, T_MAGOUT, 0.05) * fade                     # mag yanked down: gun dips
    p['y'] -= 0.02 * k; p['pitch'] -= 1.2 * k
    k = kick(t, T_THROW - 0.04, 0.06) * fade               # throw: gun counter-rotates
    p['roll'] += 2.5 * k; p['x'] += 0.015 * k
    k = kick(t, T_MAGIN, 0.045) * fade                     # mag seated: gun pushed up
    p['y'] += 0.04 * k; p['pitch'] -= 2.2 * k
    k = kick(t, T_MAGIN + 0.06, 0.04) * fade               # palm slap
    p['y'] += 0.018 * k; p['pitch'] -= 0.8 * k
    k = window(t, T_CHARGER, T_CHARGER + 0.05) * (1 - window(t, 1.13, 1.16))   # hauling on the handle
    p['z'] += 0.03 * k; p['roll'] -= 1.5 * k
    k = kick(t, 1.13, 0.04) * fade                         # bolt slams home
    p['z'] -= 0.02 * k; p['pitch'] += 0.8 * k
    return p


def mag_pull(t):
    """Magazine offset while the hand still has it: straight out, then a flick that accelerates into the release."""
    u = window(t, T_MAGOUT, 0.31)
    v = min(max((t - 0.31) / (T_THROW - 0.31), 0.0), 1.0) ** 2
    return T(0.05 * v, -0.34 * u - 0.22 * v, 0.0) @ Rx(math.radians(-6.0 * u - 10.0 * v)) @ Rz(math.radians(28.0 * v))


NEW_MAG = curves({   # fresh magazine, Body frame, from below the screen up to just under the magwell
    'x':  [(T_SWAP, 0.45), (0.66, 0.20), (0.75, 0.03)],
    'y':  [(T_SWAP, -2.10), (0.66, -0.90), (0.75, -0.16)],
    'z':  [(T_SWAP, -0.10), (0.66, -0.03), (0.75, 0.02)],
    'rx': [(T_SWAP, 22.0), (0.66, 14.0), (0.75, 5.0)],
    'rz': [(T_SWAP, 14.0), (0.66, 7.0), (0.75, 1.0)],
})


def mag_new(t):
    if t <= 0.75:
        c = {k: v(t) for k, v in NEW_MAG.items()}
    else:            # last push accelerates into the magwell so it seats with a hit, not a glide
        f = 1 - min((t - 0.75) / (T_MAGIN - 0.75), 1.0) ** 2
        c = {k: v(0.75) * f for k, v in NEW_MAG.items()}
    return T(c['x'], c['y'], c['z']) @ Rx(math.radians(c['rx'])) @ Rz(math.radians(c['rz']))


def _held_mag(rig, t):
    return rig.mag_in_gun(rig.gun(D_of(reload_params(t))), mag_pull(t))


def _release(rig):
    """Magazine pose, velocity and hand velocity at the moment it leaves the hand."""
    if not hasattr(rig, '_rel'):
        e = 1e-4
        M0, Mm = _held_mag(rig, T_THROW), _held_mag(rig, T_THROW - e)
        v = (M0[:3, 3] - Mm[:3, 3]) / e
        hv = (pt(M0, MAG_HOLD_MAG) - pt(Mm, MAG_HOLD_MAG)) / e
        rig._rel = (M0, v, hv)
    return rig._rel


def thrown_mag(rig, t):
    M0, v, _ = _release(rig)
    dt = t - T_THROW
    M = np.eye(4)
    M[:3, 3] = M0[:3, 3] + (v + THROW_LIFT) * dt + 0.5 * GRAVITY * dt * dt
    w = THROW_SPIN * dt
    M[:3, :3] = (M0 @ Rx(w[0]) @ Rz(w[2]))[:3, :3]
    return M


RELOAD_SLIDE = Curve([(0, 0), (T_CHARGER, 0), (1.117, 0.47), (1.13, 0.47), (1.155, 0.0), (1.50, 0)])


def anim_reload(rig, t):
    p = reload_params(t)
    D = D_of(p)
    G = rig.gun(D)
    Rg = G[:3, :3]
    if t < T_THROW:
        Mg = rig.mag_in_gun(G, mag_pull(t))
    elif t < T_SWAP:
        Mg = thrown_mag(rig, t)
    elif t < T_MAGIN:
        Mg = rig.mag_in_gun(G, mag_new(t))
    else:
        Mg = rig.mag_in_gun(G)
    sb = RELOAD_SLIDE(t)
    if t < T_THROW:
        lh = pt(Mg, MAG_HOLD_MAG)
    elif t < T_SWAP:
        # follow through after the flick, then drop out of view to take a fresh magazine
        M0, _, hv = _release(rig)
        tau = 0.05
        a = pt(M0, MAG_HOLD_MAG) + hv * tau * (1 - math.exp(-(t - T_THROW) / tau))
        Gs = rig.gun(D_of(reload_params(T_SWAP)))
        b = pt(rig.mag_in_gun(Gs, mag_new(T_SWAP)), MAG_HOLD_MAG)
        u = window(t, T_THROW, T_SWAP)
        lh = (1 - u) * a + u * b
    else:
        dip = math.sin(math.pi * window(t, T_MAGIN + 0.01, T_MAGIN + 0.07))   # hand drops a touch and slaps up
        on_mag = pt(Mg, MAG_HOLD_MAG) + Rg @ np.array([0.0, -0.06 * dip, 0.0])
        held = min(sb, 0.47) if t < 1.13 else 0.47        # hand rides the handle back, stays back when it lets go
        on_ch = pt(G @ rig.slide_rel @ T(0, 0, -held), CHARGER_GRAB_SLIDE)
        on_ch = on_ch + Rg @ (np.array([0.08, 0.04, 0.0]) * window(t, 1.13, 1.17))
        w = window(t, 0.92, 1.03) * (1 - window(t, 1.17, 1.36))
        lh = (1 - w) * on_mag + w * on_ch
        lh = lh + Rg @ (math.sin(math.pi * window(t, 0.92, 1.03)) * np.array([0.14, 0.06, 0.02])
                        + math.sin(math.pi * window(t, 1.17, 1.36)) * np.array([0.12, -0.10, 0.0]))
    # elbow swings out a little on the throw (shoulder offset in the gun's frame); no forearm twist
    throw = math.sin(math.pi * window(t, 0.28, 0.52))
    sh_L = Rg @ (throw * np.array([0.25, 0.08, 0.0]))
    return rig.pose(D, mag=Mg, slide_back=sb, left_hand=lh, sh_L=sh_L)


ANIMS = {
    # name: (length, fps, loop, priority enum value, sampler, markers [(time, name, value)], keyed joints)
    'Idle':   (IDLE_LEN, 30, True, 0, anim_idle, [], None),
    'Equip':  (EQUIP_LEN, 60, False, 2, anim_equip, [(0.0, 'Sound', 'Equip')], None),
    'Shoot':  (SHOOT_LEN, 60, False, 3, anim_shoot, [(0.0, 'RandomSound', 'Shoot')], ('BodyJoint', 'SlideJoint')),
    'Reload': (RELOAD_LEN, 60, False, 4, anim_reload,
               [(T_MAGOUT, 'Sound', 'MagOut'), (T_MAGIN, 'Sound', 'MagIn'), (T_CHARGER, 'Sound', 'Charger')], None),
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
