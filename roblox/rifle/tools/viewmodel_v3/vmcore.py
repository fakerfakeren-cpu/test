"""Scar viewmodel: rig + animations, built from the user's real AutoBlaster viewmodel (game.rbxl).

Everything is computed in the HumanoidRootPart frame (HRP = identity), x right, y up, -z forward.
Rig follows the template / the user's Glock viewmodel:
    HumanoidRootPart -> Body (BodyJoint) -> RightArm (RightArmJoint)
                                         -> LeftArm (LeftArmJoint)
                                         -> Magazine (MagazineJoint)
                                         -> Slide (SlideJoint)
LeftArm hangs off Body, not the Magazine: the magazine is thrown, spins and swaps in the reload, and an arm parented
to it would need >180 degree joint rotations that Roblox can interpolate the long way round (the arm spins).
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
FOLLOW = 0.3   # how much the arms travel and turn with the gun (your Glock reload: right arm turns ~13 deg for ~44)


def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)


def rodrigues(axis, ang):
    x, y, z = unit(axis)
    K = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * (K @ K)


def rot_frac(R, k):
    """The same rotation as R about the same axis, scaled to fraction k of its angle."""
    ang = math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2)))
    if ang < 1e-9 or k == 0:
        return np.eye(3)
    axis = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    return rodrigues(axis, k * ang)


def upright(d):
    """Arm frame whose +Z points along d (hand -> shoulder), with its Y as close to world up as possible."""
    d = unit(d)
    up = np.array([0.0, 1.0, 0.0])
    y = unit(up - d * (up @ d))
    return np.stack([np.cross(y, d), y, d], 1)


def arm_cf(hand, shoulder, base):
    """Arm part: hand end on `hand`, pointing back at `shoulder`. Its frame is `base` swung by the smallest rotation
    that lines it up, so the arm never twists about its own length."""
    d = unit(shoulder - hand)
    z = base[:, 2]
    axis = np.cross(z, d)
    s, c = np.linalg.norm(axis), float(z @ d)
    R = base if s < 1e-12 else rodrigues(axis, math.atan2(s, c)) @ base
    M = np.eye(4); M[:3, :3] = R; M[:3, 3] = hand + ARM_HALF * d
    return M


class Rig:
    def __init__(self, S):
        self.S = S
        G0 = S['Body']
        self.G0 = G0
        # Gun pivot frame: at the grip top, axes aligned with the HRP (so Transform = gun motion as seen by the player)
        self.F0 = T(*pt(G0, PIVOT_BODY))
        self.mag_rel = inv(G0) @ S['Magazine']        # seated magazine in Body space (pure translation)
        self.slide_rel = inv(G0) @ S['Slide']
        rh = pt(G0, RIGHT_HAND_BODY)
        lh = pt(S['Magazine'], MAG_HOLD_MAG)
        self.shoulder_R = rh + 4.0 * unit(RIGHT_DIR)
        self.shoulder_L = lh + 4.0 * unit(LEFT_DIR)
        self.shoulder_R_body = pt(inv(G0), self.shoulder_R)   # the same shoulders, carried in the gun's frame
        self.shoulder_L_body = pt(inv(G0), self.shoulder_L)
        self.R_rest_R = upright(self.shoulder_R - rh)        # rest orientation of each arm (no twist)
        self.R_rest_L = upright(self.shoulder_L - lh)
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
            ('LeftArmJoint', 'Body', 'LeftArm', inv(R['Body']) @ R['LeftArm'] @ C1_arm, C1_arm),
            ('MagazineJoint', 'Body', 'Magazine', inv(R['Body']) @ R['Magazine'] @ C1_mag, C1_mag),
            ('SlideJoint', 'Body', 'Slide', inv(R['Body']) @ R['Slide'], np.eye(4)),
        ]

    def gun(self, D):
        """D: gun motion in the pivot frame -> Body CFrame (HRP frame)."""
        return self.F0 @ D @ inv(self.F0) @ self.G0

    def mag_in_gun(self, G, off=None):
        """Magazine CFrame for an offset (Body frame, about the top of the magazine); None = seated."""
        if off is None:
            return G @ self.mag_rel
        return G @ self.mag_rel @ T(*MAG_PIVOT_MAG) @ off @ T(*(-MAG_PIVOT_MAG))

    def pose(self, D, mag=None, slide_back=0.0, left_hand=None, sh_R=(0, 0, 0), sh_L=(0, 0, 0), follow=FOLLOW,
             D_follow=None):
        """mag: Magazine CFrame (HRP frame) or None for seated. sh_*: extra shoulder offsets (HRP frame).
        follow: fraction of the gun's travel and turn the arms take on (the rest comes from the hands moving).
        D_follow: a lagging copy of the gun motion for the arms to follow, so they drag behind and catch up."""
        G = self.gun(D)
        Mg = self.mag_in_gun(G) if mag is None else mag
        Sl = G @ self.slide_rel @ T(0, 0, -slide_back)
        lh = pt(Mg, MAG_HOLD_MAG) if left_hand is None else left_hand
        Gf = G if D_follow is None else self.gun(D_follow)
        turn = rot_frac(Gf[:3, :3] @ self.G0[:3, :3].T, follow)    # part of the gun's rotation since rest
        sR = (1 - follow) * self.shoulder_R + follow * pt(Gf, self.shoulder_R_body) + np.asarray(sh_R, float)
        sL = (1 - follow) * self.shoulder_L + follow * pt(Gf, self.shoulder_L_body) + np.asarray(sh_L, float)
        return {'HumanoidRootPart': np.eye(4), 'Body': G, 'Magazine': Mg, 'Slide': Sl,
                'RightArm': arm_cf(pt(G, RIGHT_HAND_BODY), sR, turn @ self.R_rest_R),
                'LeftArm': arm_cf(lh, sL, turn @ self.R_rest_L)}

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


KEYS6 = ('x', 'y', 'z', 'pitch', 'yaw', 'roll')
ARM_LAG = 0.18          # idle: the arms sway this many seconds behind the gun


def vec_of(p):
    return np.array([p[k] for k in KEYS6], float)


def p_of(v):
    return dict(zip(KEYS6, (float(a) for a in v)))


class Spring:
    """A damped spring chasing a target signal (overshoot and settle), solved once on a fine grid."""

    def __init__(self, target, t_end, omega, zeta, dt=1 / 1200):
        self.dt = dt
        n = int(round(t_end / dt)) + 1
        tg = np.array([target(i * dt) for i in range(n)], float)
        x, v = tg[0].copy(), np.zeros_like(tg[0])
        self.out = np.empty_like(tg)
        for i in range(n):
            self.out[i] = x
            v = v + (omega * omega * (tg[i] - x) - 2 * zeta * omega * v) * dt
            x = x + v * dt

    def __call__(self, t):
        f = min(max(t / self.dt, 0.0), len(self.out) - 1.000001)
        i = int(f); f -= i
        return self.out[i] * (1 - f) + self.out[i + 1] * f


def bounce(t, t0, omega=32.0, zeta=0.35):
    """Springy response to a hit at t0: jumps, peaks at 1, swings back past zero and settles."""
    if t <= t0:
        return 0.0
    wd = omega * math.sqrt(1 - zeta * zeta)
    tp = math.atan2(wd, zeta * omega) / wd
    peak = math.exp(-zeta * omega * tp) * math.sin(wd * tp)
    u = t - t0
    return math.exp(-zeta * omega * u) * math.sin(wd * u) / peak


def kick(t, t0, tau):
    """Impact response: 0 before t0, peaks (1.0) at t0 + tau, then dies away."""
    if t <= t0:
        return 0.0
    u = (t - t0) / tau
    return u * math.exp(1 - u)


IDLE_LEN = 4.0


def idle_params(t):
    w = 2 * math.pi / IDLE_LEN
    return dict(x=0.0055 * math.sin(w * t + 1.3),
                y=0.0095 * math.sin(w * t) + 0.003 * math.sin(2 * w * t + 0.7),
                z=0.004 * math.sin(2 * w * t),
                pitch=0.42 * math.sin(w * t + 0.4),
                yaw=0.28 * math.sin(w * t + 2.0),
                roll=0.48 * math.sin(w * t + 1.0))


def idle_D(t):
    return D_of(idle_params(t))


def idle_left_offset(t):
    w = 2 * math.pi / IDLE_LEN
    return np.array([0.004 * math.sin(w * t + 2.2), 0.005 * math.sin(2 * w * t + 0.3), 0.0])


def anim_idle(rig, t):
    p = idle_params(t)
    D = D_of(p)
    lh = pt(rig.mag_in_gun(rig.gun(D)), MAG_HOLD_MAG + idle_left_offset(t))
    return rig.pose(D, left_hand=lh, D_follow=idle_D(t - ARM_LAG))


EQUIP_LEN = 0.70
EQUIP_START = np.array([0.30, -1.00, 0.40, -38.0, -16.0, -30.0])   # x y z pitch yaw roll, below the screen


def _equip_target(t):
    e = 1 - (1 - min(max(t / 0.26, 0.0), 1.0)) ** 3          # fast, decelerating swing up
    return EQUIP_START * (1 - e)


_SPRINGS = {}


def _spring(name, make):
    if name not in _SPRINGS:
        _SPRINGS[name] = make()
    return _SPRINGS[name]


def equip_offsets(t):
    gun = _spring('equip_gun', lambda: Spring(_equip_target, EQUIP_LEN, omega=17.0, zeta=0.40))
    arm = _spring('equip_arm', lambda: Spring(gun, EQUIP_LEN, omega=11.0, zeta=0.60))
    fade = 1 - window(t, 0.52, 0.70)                         # settled exactly on the idle pose at the end
    return gun(t) * fade, arm(t) * fade


def anim_equip(rig, t):
    off, off_arm = equip_offsets(t)
    D = idle_D(t) @ D_of(p_of(off))                          # converges to the idle pose at the same clock time
    Df = idle_D(t - ARM_LAG) @ D_of(p_of(off_arm))           # arms drag behind the gun, then catch up
    G = rig.gun(D)
    # left hand comes up from below and slaps onto the magazine a beat after the gun arrives
    k = window(t, 0.08, 0.34)
    off_h = (1 - k) * np.array([-0.06, -0.40, 0.18]) + math.sin(math.pi * k) * np.array([-0.05, 0.07, 0.0])
    grab = 0.022 * bounce(t, 0.34, omega=30.0, zeta=0.40) * (1 - window(t, 0.55, 0.70))
    lh = pt(rig.mag_in_gun(G), MAG_HOLD_MAG + idle_left_offset(t) + np.array([0, grab, 0])) + off_h
    follow = 0.75 - (0.75 - FOLLOW) * window(t, 0.30, 0.60)   # arms come up with the gun, then settle
    return rig.pose(D, left_hand=lh, follow=follow, D_follow=Df)


SHOOT_LEN = 0.25
SHOOT_KICK = np.array([0.005, 0.018, 0.085, 2.6, 0.15, -0.45])  # x y z pitch yaw roll at the peak of the kick


def shoot_params(t):
    # peaks at 0.037 s, crosses zero right at the next shot (600 rpm), rebounds forward ~20 %, settles
    return p_of(SHOOT_KICK * bounce(t, 0.0, omega=34.0, zeta=0.42) * (1 - window(t, 0.20, 0.25)))


SHOOT_SLIDE = Curve([(0, 0.0), (0.017, 0.15), (0.033, 0.18), (0.05, 0.08), (0.067, 0.0), (0.25, 0.0)])


def anim_shoot(rig, t):
    return rig.pose(D_of(shoot_params(t)), slide_back=SHOOT_SLIDE(t))


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
THROW_SPIN = np.radians(np.array([-200.0, 0.0, 450.0]))      # deg/s about the magazine's own X and Z


TILT_V = vec_of(POSE_TILT)
CHARGE_V = vec_of(POSE_CHARGE)


def _reload_target(t):
    a, b, c = window(t, 0.02, 0.20), window(t, 0.90, 1.02), window(t, 1.14, 1.34)
    v = TILT_V * a + (CHARGE_V - TILT_V) * b - CHARGE_V * c
    # anticipation: a quick dip and counter-roll before tipping into the tilt
    v = v + math.sin(math.pi * window(t, 0.0, 0.07)) * np.array([0.0, -0.025, 0.0, -2.5, 0.0, 4.0])
    return v


def _reload_vec(t):
    target = _reload_target(t)
    sp = _spring('reload_gun', lambda: Spring(_reload_target, RELOAD_LEN, omega=20.0, zeta=0.42))
    end = 1 - window(t, 1.38, 1.50)                          # springs come to rest exactly at the end
    v = target + (sp(t) - target) * end
    hit = np.zeros(6)
    k = bounce(t, T_MAGOUT, 30.0, 0.40)                      # mag yanked down: gun dips
    hit += k * np.array([0.0, -0.022, 0.0, -1.4, 0.0, 0.0])
    k = bounce(t, T_THROW - 0.03, 24.0, 0.45)                # throw: gun counter-rotates
    hit += k * np.array([0.018, 0.0, 0.0, 0.0, 0.0, 3.0])
    k = bounce(t, T_MAGIN, 32.0, 0.32)                       # mag slammed home: gun bounces up
    hit += k * np.array([0.0, 0.05, 0.0, -2.8, 0.0, 0.0])
    k = bounce(t, T_MAGIN + 0.06, 36.0, 0.40)                # palm slap
    hit += k * np.array([0.0, 0.02, 0.0, -1.0, 0.0, 0.0])
    k = window(t, T_CHARGER, T_CHARGER + 0.05) * (1 - window(t, 1.13, 1.16))   # hauling on the handle
    hit += k * np.array([0.0, 0.0, 0.03, 0.0, 0.0, -1.5])
    k = math.sin(math.pi * window(t, T_CHARGER - 0.06, T_CHARGER))             # little push before the pull
    hit += k * np.array([0.0, 0.0, -0.012, 0.0, 0.0, 0.0])
    k = bounce(t, 1.13, 34.0, 0.38)                          # bolt slams home
    hit += k * np.array([0.0, 0.0, -0.022, 1.0, 0.0, 0.0])
    return v + hit * (1 - window(t, 1.40, 1.50))


def reload_params(t):
    return p_of(_reload_vec(t))


def reload_arm_params(t):
    """The gun motion as the arms feel it: the same moves, a beat late, with a softer overshoot."""
    arm = _spring('reload_arm', lambda: Spring(_reload_vec, RELOAD_LEN, omega=12.0, zeta=0.60))
    g = _reload_vec(t)
    return p_of(g + (arm(t) - g) * (1 - window(t, 1.38, 1.50)))


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
    # elbow: out on the throw, down for the fresh mag, up for the charging handle (no forearm twist)
    throw = math.sin(math.pi * window(t, 0.28, 0.52))
    low = math.sin(math.pi * window(t, 0.42, 0.72))
    ch = window(t, 0.92, 1.03) * (1 - window(t, 1.17, 1.36))
    sh_L = throw * np.array([-0.30, 0.10, 0.0]) + low * np.array([0.0, -0.25, 0.08]) + ch * np.array([-0.20, 0.25, 0.0])
    return rig.pose(D, mag=Mg, slide_back=sb, left_hand=lh, sh_L=sh_L, D_follow=D_of(reload_arm_params(t)))


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
