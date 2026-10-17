"""Third-person R15 rig, Scar hold, arm IK and the Idle/Shoot/Reload character animations.

Everything is in rig space (the R15 export: character faces -Z, +X is its right). Joints follow Roblox:
    Part1 = Part0 * C0 * Transform * C1^-1,   C0 = (joint - centre0), C1 = (joint - centre1), no rotation.
Pose.CFrame in a KeyframeSequence is that Transform. Every Transform made here is a pure rotation, so the
animations also play on R15 bodies with other proportions (the hands then land less exactly).

The gun is welded to RightHand by the Tool's RightGrip (Handle = RightHand * RightGripAttachment * Grip^-1), so
the animations move the arms, torso and head only; the gun goes wherever the right hand takes it.
"""
import json

import numpy as np

ARM_JOINTS = ('Shoulder', 'Elbow', 'Wrist')
ARM_PARTS = ('UpperArm', 'LowerArm', 'Hand')
JOINTS = [('Waist', 'LowerTorso', 'UpperTorso'), ('Neck', 'UpperTorso', 'Head')]
for _s in ('Right', 'Left'):
    JOINTS += [(_s + 'Shoulder', 'UpperTorso', _s + 'UpperArm'), (_s + 'Elbow', _s + 'UpperArm', _s + 'LowerArm'),
               (_s + 'Wrist', _s + 'LowerArm', _s + 'Hand')]
JOINT_OF = {p1: j for j, p0, p1 in JOINTS}


# ---------------------------------------------------------------- maths
def rx(a):
    c, s = np.cos(a), np.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(a):
    c, s = np.cos(a), np.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def cf(R=None, p=None):
    M = np.eye(4)
    if R is not None: M[:3, :3] = R
    if p is not None: M[:3, 3] = p
    return M


def inv(M):
    R = M[:3, :3]; out = np.eye(4); out[:3, :3] = R.T; out[:3, 3] = -R.T @ M[:3, 3]; return out


def rv2R(v):
    a = np.linalg.norm(v)
    if a < 1e-12: return np.eye(3)
    k = v / a; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * K @ K


def R2rv(R):
    c = np.clip((np.trace(R) - 1) / 2, -1, 1); a = np.arccos(c)
    if a < 1e-9: return np.zeros(3)
    if a > np.pi - 1e-6:
        w, V = np.linalg.eigh((R + R.T) / 2 - np.eye(3)); return V[:, -1] * a
    return a / (2 * np.sin(a)) * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])


def angle(R):
    return np.degrees(np.linalg.norm(R2rv(R)))


def deg(*a):
    return np.radians(a)


# ---------------------------------------------------------------- rig from the user's glTF export
def _qmat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def _world(g):
    W = {}

    def go(i, P):
        n = g['nodes'][i]
        M = cf(_qmat(n.get('rotation', [0, 0, 0, 1])), n.get('translation', [0, 0, 0]))
        W[n.get('name')] = (P @ M, np.array(n.get('scale', [1, 1, 1]), float))
        for c in n.get('children', []): go(c, P @ M)
    for r in g['scenes'][0]['nodes']: go(r, np.eye(4))
    return W


class Rig:
    def __init__(self, gltf_path):
        g = json.load(open(gltf_path))
        W = _world(g); R0 = inv(W['Rig'][0])
        at = lambda n: R0 @ W[n][0]                                  # noqa: E731
        self.jpos = {j: at(p1)[:3, 3] for j, p0, p1 in JOINTS}       # joint nodes sit at their joints
        self.centre, self.size = {}, {}
        for n in ['LowerTorso', 'UpperTorso'] + [s + p for s in ('Right', 'Left') for p in ARM_PARTS + ('UpperLeg', 'LowerLeg', 'Foot')]:
            self.centre[n] = at(n + '_Geo')[:3, 3]; self.size[n] = W[n + '_Geo'][1]
        self.centre['Head'] = at('FaceCenter_Att')[:3, 3]; self.size['Head'] = np.array([1.25, 1.25, 1.25])
        self.parent = {p1: p0 for j, p0, p1 in JOINTS}
        self.C0 = {j: cf(p=self.jpos[j] - self.centre[p0]) for j, p0, p1 in JOINTS}
        self.C1i = {j: cf(p=self.centre[p1] - self.jpos[j]) for j, p0, p1 in JOINTS}
        # the gun exactly as exported (Tool.Grip at its default), relative to the RightGripAttachment
        A_world = at('RightGrip_Att')
        self.A_local = inv(cf(p=self.centre['RightHand'])) @ A_world   # RightGripAttachment.CFrame
        body = at('Body')
        self.P_export = inv(A_world) @ body
        self.gun_parts = {n: inv(body) @ at(n) for n in ('Body', 'Magazine', 'Slide')}
        self.gun_size = {n: W[n][1] for n in ('Body', 'Magazine', 'Slide')}
        self.muzzle = (inv(body) @ at('Muzzle_Att'))[:3, 3]

    def fk(self, Tm, look=None):
        """World CFrame of each animated part. Tm: joint -> 3x3 rotation (missing = identity).
        look = (waistPitch, neckPitch, neckYaw, armPitch): the LookReplication script's C0 offsets."""
        C0 = dict(self.C0)
        if look is not None:
            wp, npch, ny, ap = look
            C0['Waist'] = C0['Waist'] @ cf(rx(wp))
            C0['Neck'] = C0['Neck'] @ cf(ry(ny) @ rx(npch))                    # CFrame.fromEulerAnglesYXZ(p, yaw, 0)
            C0['RightShoulder'] = C0['RightShoulder'] @ cf(rx(ap))
            C0['LeftShoulder'] = C0['LeftShoulder'] @ cf(rx(ap))
        out = {'LowerTorso': cf(p=self.centre['LowerTorso'])}
        for j, p0, p1 in JOINTS:
            out[p1] = out[p0] @ C0[j] @ cf(Tm.get(j, np.eye(3))) @ self.C1i[j]
        return out

    def joint_world(self, W, j):
        p0 = [q0 for jj, q0, q1 in JOINTS if jj == j][0]
        return W[p0] @ self.C0[j]


# ---------------------------------------------------------------- arm IK
class ArmIK:
    """Shoulder (3 dof) + elbow hinge (+ forearm roll on the right arm). Places the wrist joint on a target;
    soft terms keep the elbow near a preferred point, the wrist bend small and the motion continuous."""

    def __init__(self, rig, side, roll):
        self.rig, self.s, self.roll = rig, side, roll
        self.x = np.array([0.0, 0, 0, 1.2, 0.0])

    def chain(self, UT, x):
        r, s = self.rig, self.s
        Ts, Te = rv2R(x[:3]), rx(x[3]) @ ry(x[4] if self.roll else 0.0)
        UA = UT @ r.C0[s + 'Shoulder'] @ cf(Ts) @ r.C1i[s + 'Shoulder']
        LA = UA @ r.C0[s + 'Elbow'] @ cf(Te) @ r.C1i[s + 'Elbow']
        return Ts, Te, UA, LA, (UA @ r.C0[s + 'Elbow'])[:3, 3], (LA @ r.C0[s + 'Wrist'])[:3, 3]

    def solve(self, UT, wrist_target, elbow_pref, hand_R=None, w_wrist=0.6, iters=40):
        x = self.x.copy(); prev = self.x.copy()

        def res(x):
            Ts, Te, UA, LA, E, Wp = self.chain(UT, x)
            r = [40.0 * (Wp - wrist_target), 1.0 * (E - elbow_pref), 0.35 * (x - prev)]
            r.append([30.0 * max(0.0, 0.15 - x[3]), 30.0 * max(0.0, x[3] - 2.45)])
            if hand_R is not None:
                r.append(w_wrist * R2rv(LA[:3, :3].T @ hand_R))
            return np.concatenate([np.ravel(v) for v in r])
        lam = 1e-3
        f = res(x); cost = f @ f
        for _ in range(iters):
            J = np.empty((len(f), len(x)))
            for k in range(len(x)):
                d = np.zeros(len(x)); d[k] = 1e-6; J[:, k] = (res(x + d) - f) / 1e-6
            while True:
                step = np.linalg.solve(J.T @ J + lam * np.eye(len(x)), -J.T @ f)
                f2 = res(x + step); c2 = f2 @ f2
                if c2 < cost: x, f, cost, lam = x + step, f2, c2, lam * 0.3; break
                lam *= 10
                if lam > 1e8: break
            if lam > 1e8 or np.linalg.norm(step) < 1e-9: break
        self.x = x
        Ts, Te, UA, LA, E, Wp = self.chain(UT, x)
        return Ts, Te, LA, np.linalg.norm(Wp - wrist_target)


# ---------------------------------------------------------------- curves
def pchip(ts, vs, t):
    """Monotone cubic (no overshoot between keys), per column."""
    ts = np.asarray(ts, float); vs = np.asarray(vs, float)
    if vs.ndim == 1: vs = vs[:, None]
    h = np.diff(ts); dl = np.diff(vs, axis=0) / h[:, None]
    m = np.zeros_like(vs)
    for i in range(1, len(ts) - 1):
        a, b = dl[i - 1], dl[i]; w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
        m[i] = np.where(a * b > 0, (w1 + w2) / (w1 / np.where(a == 0, 1, a) + w2 / np.where(b == 0, 1, b)), 0)
    i = int(np.clip(np.searchsorted(ts, t, side='right') - 1, 0, len(ts) - 2))
    u = (t - ts[i]) / h[i]
    h00, h10, h01, h11 = 2 * u**3 - 3 * u**2 + 1, u**3 - 2 * u**2 + u, -2 * u**3 + 3 * u**2, u**3 - u**2
    return h00 * vs[i] + h10 * h[i] * m[i] + h01 * vs[i + 1] + h11 * h[i] * m[i + 1]


def track(keys, t):
    """keys: [(time, values...)] -> values at t."""
    return pchip([k[0] for k in keys], [k[1:] for k in keys], t)


# ---------------------------------------------------------------- the hold
# Body-local points on the user's Scar (Body +Z = muzzle, +Y = top, +X = the gun's left side)
GRIP = np.array([0.0, -0.42, -0.68])         # pistol grip: right hand centre
MAG = np.array([0.04, -0.40, -0.15])         # back of the magazine / magwell, held low: left hand centre
CHARGER = np.array([0.42, 0.30, 0.43])       # charging handle on the gun's left side
BUTT = np.array([0.0, 0.09, -1.825])


class Stance:
    """Base pose: torso yaw/lean, head, and the gun in UpperTorso space."""

    def __init__(self, rig, yaw, lean, gun_pos):
        self.rig = rig
        self.waist = ry(yaw) @ rx(-lean)
        self.UT0 = rig.fk({'Waist': self.waist})['UpperTorso']
        G = cf(ry(np.pi), gun_pos)                       # muzzle along -Z (where the character looks), top up
        self.gun_UT = inv(self.UT0) @ G                  # the gun rides with the upper torso


def torso_points(rig, waist):
    UT = rig.fk({'Waist': waist})['UpperTorso']
    sr = (UT @ rig.C0['RightShoulder'])[:3, 3]; sl = (UT @ rig.C0['LeftShoulder'])[:3, 3]
    return UT, sr, sl


def box_pen(M, size, p):
    """Penetration depth of points p (..., 3) into the box (M, size); negative = distance outside."""
    p = np.asarray(p, float)
    q = np.abs((p - M[:3, 3]) @ M[:3, :3]) - np.asarray(size) / 2
    inside = np.all(q < 0, axis=-1)
    return np.where(inside, -np.max(q, axis=-1), -np.linalg.norm(np.maximum(q, 0), axis=-1))


def stance_cost(rig, yaw, lean, Gp):
    """Cost of a base hold; Gp: (N, 3) candidate Body centres (gun level, muzzle along -Z). Returns (cost, dr, dl, pen)."""
    waist = ry(yaw) @ rx(-lean)
    UT, sr, sl = torso_points(rig, waist)
    head0 = cf(p=rig.centre['Head'])
    Rg = ry(np.pi)
    pt = lambda b: Gp + Rg @ b                                       # noqa: E731
    dr = np.linalg.norm(pt(GRIP) - sr, axis=1); dl = np.linalg.norm(pt(MAG) - sl, axis=1)
    pos = lambda v: np.maximum(v, 0)                                 # noqa: E731
    c = 6 * (pos(1.25 - dr) ** 2 + pos(dr - 1.5) ** 2) + 6 * (pos(1.35 - dl) ** 2 + pos(dl - 1.6) ** 2) + 200 * pos(dl - 1.66) ** 2 + 200 * pos(dr - 1.66) ** 2
    pen = box_pen(UT, rig.size['UpperTorso'], pt(BUTT))
    c += 3 * (pen - 0.15) ** 2
    for z in np.linspace(-0.9, 1.8, 10):                             # receiver and barrel stay out of the body
        for y in (0.62, -0.05):
            p = pt(np.array([0, y, z]))
            c += 10 * pos(box_pen(UT, rig.size['UpperTorso'] + 0.2, p)) ** 2 + 10 * pos(box_pen(head0, rig.size['Head'] + 0.15, p)) ** 2
    for z in np.linspace(-1.8, -0.9, 4):                             # the stock clears the head
        c += 10 * pos(box_pen(head0, rig.size['Head'] + 0.1, pt(np.array([0, 0.43, z])))) ** 2
    by = Gp[:, 1] + 0.262
    c += 0.5 * (by - 3.8) ** 2 + 0.2 * ((np.degrees(yaw) + 25) / 10) ** 2 + 0.1 * (np.degrees(lean) / 10) ** 2
    return c, dr, dl, pen


def search_stance(rig, top=5):
    g = np.stack(np.meshgrid(np.arange(-0.1, 1.01, 0.05), np.arange(3.3, 4.31, 0.05), np.arange(-0.6, -2.21, -0.05), indexing='ij'), -1).reshape(-1, 3)
    g[:, 1] -= 0.262
    rows = []
    for yaw in deg(*range(-15, -56, -5)):
        for lean in deg(0, 5, 10, 15):
            c, dr, dl, pen = stance_cost(rig, yaw, lean, g)
            for i in np.argsort(c)[:3]:
                rows.append((c[i], yaw, lean, g[i].copy(), dr[i], dl[i], pen[i]))
    rows.sort(key=lambda r: r[0])
    return rows[:top]


# ---------------------------------------------------------------- base hold: near-square, gun straight ahead
# A square torso keeps the gun in line with the body from every angle, and keeps LookReplication's arm pitch on the
# character's own right axis. R15 arms are short for this gun, so it sits just right of centre (x 0.1) at chest
# height, with enough slack in the left arm that recoil and the reload don't snap it straight.
BASE_YAW, BASE_LEAN = np.radians(-15), np.radians(10)
BASE_GUN = np.array([0.10, 3.39, -1.60])           # Body centre: bore at y 3.65, butt tucked 0.12 into the chest
HEAD_TILT = np.eye(3)                              # head level and facing forward
POUCH = np.array([-0.75, -0.85, -0.65])            # UpperTorso-local: front of the belt, left side
ELBOW_OUT = {'Right': np.array([0.45, -0.55, 0.15]), 'Left': np.array([-0.30, -0.60, 0.05])}  # UpperTorso-local


def gun_offset(dp, roll, pitch_up, yaw_left):
    """Gun move about the pistol grip: roll + = top to the right, pitch + = muzzle up, yaw + = muzzle left."""
    R = rz(np.radians(roll)) @ rx(np.radians(-pitch_up)) @ ry(np.radians(yaw_left))
    return cf(p=dp), cf(p=GRIP) @ cf(R) @ cf(p=-GRIP)


def idle_channels(t):
    w = 2 * np.pi
    torso = (0.8 * np.sin(w * t / 4 + 1.0), 0.7 * np.sin(w * t / 2), 0.0)
    gun = (0, 0.015 * np.sin(w * t / 2 - 0.6), 0, 0.6 * np.sin(w * t / 4), 0.4 * np.sin(w * t / 2 - 1.2), 0)
    return torso, gun, ('gun', MAG)


def _kick(t):
    """0 -> 1 at 33 ms -> damped swing back, exactly 0 at the end (0.2 s)."""
    a = np.sin(np.pi / 2 * min(t / 0.033, 1.0)) if t < 0.033 else np.exp(-(t - 0.033) / 0.045) * np.cos(2 * np.pi * (t - 0.033) / 0.30)
    end = np.exp(-(0.2 - 0.033) / 0.045) * np.cos(2 * np.pi * (0.2 - 0.033) / 0.30)
    return a - end * max(0.0, (t - 0.033) / (0.2 - 0.033)) ** 2


def shoot_channels(t):
    k, k2 = _kick(t), _kick(max(0.0, t - 0.012))
    torso = (0.0, -1.6 * k2, 0.0)
    gun = (0, 0.03 * k, 0.10 * k, 0.0, 6.0 * k2, 0.6 * k2)
    return torso, gun, ('gun', MAG)


RELOAD_GUN = [  # t, dx, dy, dz, roll, pitch_up, yaw_left
    (0.00, 0, 0, 0, 0, 0, 0),
    (0.16, -0.12, -0.12, 0.22, 28, 10, 6),
    (0.24, -0.12, -0.17, 0.22, 30, 9, 6),       # mag yanked out: gun dragged down
    (0.32, -0.12, -0.11, 0.22, 30, 10, 6),
    (0.72, -0.12, -0.12, 0.22, 30, 10, 6),
    (0.83, -0.12, -0.06, 0.22, 32, 13, 6),      # new mag shoved home: gun bumps up
    (0.92, -0.12, -0.11, 0.22, 33, 11, 7),
    (1.03, -0.10, -0.10, 0.20, 38, 13, 10),     # cant further for the charging handle
    (1.15, -0.10, -0.08, 0.26, 39, 12, 10),     # handle pulled: gun tugged back
    (1.21, -0.10, -0.10, 0.18, 36, 13, 10),     # released: bolt slams, gun snaps forward
    (1.50, 0, 0, 0, 0, 0, 0),
]
RELOAD_TORSO = [(0.00, 0, 0, 0), (0.16, 3, 4, 0), (0.50, 3, 6, 4), (0.83, 3, 4, 0), (1.15, 2, 5, 0), (1.50, 0, 0, 0)]
RELOAD_LEFT = [  # t, space, point (Body-local for 'gun', UpperTorso-local for 'torso')
    (0.00, 'gun', MAG), (0.08, 'gun', MAG),
    (0.20, 'gun', np.array([0.04, -0.62, 0.12])),     # grab the bottom of the magazine
    (0.30, 'gun', np.array([0.30, -1.25, 0.0])),      # yank it out, down and away
    (0.46, 'torso', POUCH), (0.56, 'torso', POUCH),   # fresh one from the belt
    (0.72, 'gun', np.array([0.10, -1.00, 0.0])),      # up under the magwell
    (0.83, 'gun', MAG),                               # in
    (0.92, 'gun', np.array([0.60, -0.25, 0.30])),     # round the gun's left side, not through it
    (1.01, 'gun', CHARGER + np.array([0.22, -0.02, 0.06])),  # in from the side
    (1.07, 'gun', CHARGER),
    (1.15, 'gun', CHARGER + np.array([0, 0, -0.42])), # rack
    (1.22, 'gun', CHARGER + np.array([0.25, 0.06, -0.40])),
    (1.50, 'gun', MAG),
]


def reload_channels(t):
    torso = tuple(track(RELOAD_TORSO, t))
    gun = tuple(track(RELOAD_GUN, t))
    return torso, gun, ('keys', RELOAD_LEFT)


# name: (length, fps, loop, priority token, channels)
ANIMS = {
    'Idle': (4.0, 30, True, 2, idle_channels),      # Action: above the Animate script's toolnone (Idle) and walk
    'Shoot': (0.2, 60, False, 3, shoot_channels),   # Action2
    'Reload': (1.5, 60, False, 4, reload_channels), # Action3
}


class Poser:
    def __init__(self, rig):
        self.rig = rig
        self.base = Stance(rig, BASE_YAW, BASE_LEAN, BASE_GUN)
        self.ik = {'Right': ArmIK(rig, 'Right', True), 'Left': ArmIK(rig, 'Left', False)}
        # right hand: straight wrist in the base hold defines how the gun sits in the hand (-> Tool.Grip)
        G0 = self.base.UT0 @ self.base.gun_UT
        self.K_h = None
        Tm, W = self._arms(self.base.UT0, G0, (G0 @ np.append(MAG, 1))[:3], straight_right=True)
        self.K_h = inv(W['RightHand']) @ G0
        for s in self.ik: self.ik[s].x0 = self.ik[s].x.copy()
        # Tool.Grip so that Handle = RightHand * RightGripAttachment * Grip^-1 puts the gun there (default Grip = identity)
        self.grip = self.rig.P_export @ inv(self.K_h) @ self.rig.A_local

    def reset(self):
        for s in self.ik: self.ik[s].x = self.ik[s].x0.copy()

    def _elbow_pref(self, UT, side, hand_pt):
        sh = (UT @ self.rig.C0[side + 'Shoulder'])[:3, 3]
        return (sh + hand_pt) / 2 + UT[:3, :3] @ ELBOW_OUT[side]

    def _arms(self, UT, G, left_pt, straight_right=False):
        r = self.rig; Tm = {}
        hand_off = {s: (r.centre[s + 'Hand'] - r.jpos[s + 'Wrist']) for s in ('Right', 'Left')}
        for side in ('Right', 'Left'):
            ik = self.ik[side]
            if side == 'Right' and not straight_right:
                H = G @ inv(self.K_h)
                target = (H @ np.append(-hand_off['Right'], 1))[:3]          # wrist joint from the hand frame
                Ts, Te, LA, err = ik.solve(UT, target, self._elbow_pref(UT, side, H[:3, 3]), hand_R=H[:3, :3])
                Tw = LA[:3, :3].T @ H[:3, :3]
            else:
                pt = (G @ np.append(GRIP, 1))[:3] if side == 'Right' else left_pt
                Rla = None
                for _ in range(4):                                             # straight wrist: hand centre on the point
                    d = hand_off[side] if Rla is None else Rla @ hand_off[side]
                    Ts, Te, LA, err = ik.solve(UT, pt - d, self._elbow_pref(UT, side, pt))
                    Rla = LA[:3, :3]
                Tw = np.eye(3)
            Tm[side + 'Shoulder'], Tm[side + 'Elbow'], Tm[side + 'Wrist'] = Ts, Te, Tw
            Tm['_err' + side] = err
        W = r.fk({k: v for k, v in Tm.items() if not k.startswith('_')} | {'Waist': self.base.waist})
        return Tm, W

    def pose(self, anim, t):
        r = self.rig
        torso, gun, left = ANIMS[anim][4](t)
        waist = self.base.waist @ ry(np.radians(torso[0])) @ rx(np.radians(-torso[1])) @ rz(np.radians(torso[2]))
        UT = r.fk({'Waist': waist})['UpperTorso']
        dp, Rg = gun_offset(np.asarray(gun[:3], float), *gun[3:])
        G = UT @ inv(self.base.UT0) @ dp @ self.base.UT0 @ self.base.gun_UT @ Rg
        if left[0] == 'gun':
            lp = (G @ np.append(left[1], 1))[:3]
        else:  # keyed: every key converted to Body-local at its own time, then interpolated there
            keys = []
            for kt, space, p in left[1]:
                if space == 'gun':
                    keys.append((kt, *p))
                else:
                    Tt, Gt = self._torso_gun(anim, kt)
                    keys.append((kt, *(inv(Gt) @ Tt @ np.append(p, 1))[:3]))
            lp = (G @ np.append(track(keys, t), 1))[:3]
        Tm, _ = self._arms(UT, G, lp)
        Tm['Waist'] = waist
        Tm['Neck'] = waist.T @ HEAD_TILT          # head stays level and forward while the torso turns
        W = r.fk({k: v for k, v in Tm.items() if not k.startswith('_')})
        return Tm, W, G, lp

    def _torso_gun(self, anim, t):
        torso, gun, _ = ANIMS[anim][4](t)
        waist = self.base.waist @ ry(np.radians(torso[0])) @ rx(np.radians(-torso[1])) @ rz(np.radians(torso[2]))
        UT = self.rig.fk({'Waist': waist})['UpperTorso']
        dp, Rg = gun_offset(np.asarray(gun[:3], float), *gun[3:])
        return UT, UT @ inv(self.base.UT0) @ dp @ self.base.UT0 @ self.base.gun_UT @ Rg

    def sample(self, anim):
        length, fps, loop, prio, fn = ANIMS[anim]
        self.reset()
        n = int(round(length * fps))
        out = []
        for i in range(n + 1):
            t = i / fps
            if anim != 'Reload':                   # small motions: solve every frame from the same start (exact loop)
                self.reset()
            Tm, W, G, lp = self.pose(anim, t)
            out.append((t, Tm, W, G, lp))
        if loop:                                   # close the loop exactly (the IK warm start drifts by ~0.01 deg)
            out[-1] = (out[-1][0],) + out[0][1:]
        return out
