"""Watches the client log for camera-pack signals and takes screenshots (F2 + X framebuffer fallback).
usage: shot_driver.py <client.log> <gamedir> <out_dir> <client_pid>"""
import glob
import os
import signal
import subprocess
import sys
import threading
import time

log, gamedir, out, pid = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
os.makedirs(out, exist_ok=True)
shots_dir = os.path.join(gamedir, "screenshots")


def xdo(*keys):
    subprocess.run(["xdotool", "mousemove", "640", "360"], check=False)
    for k in keys:
        subprocess.run(["xdotool", "key", k], check=False)


def take(name):
    time.sleep(12)
    before = set(glob.glob(os.path.join(shots_dir, "*.png")))
    xdo("F2")
    subprocess.run(["import", "-window", "root", os.path.join(out, f"{name}_x11.png")], check=False)
    for _ in range(40):
        time.sleep(0.5)
        new = set(glob.glob(os.path.join(shots_dir, "*.png"))) - before
        if new:
            time.sleep(1)
            os.replace(sorted(new)[0], os.path.join(out, f"{name}.png"))
            print(f"[driver] saved {name}.png", flush=True)
            return
    print(f"[driver] F2 screenshot missing for {name} (X11 capture kept)", flush=True)


def alive():
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


t0 = time.time()
pos = 0
threads = []
joined_hud = False
while time.time() - t0 < 1500 and alive():
    time.sleep(1)
    if not os.path.exists(log):
        continue
    with open(log, encoding="utf-8", errors="replace") as f:
        f.seek(pos)
        chunk = f.read()
        pos = f.tell()
    for line in chunk.splitlines():
        if "[CAM] ready" in line and not joined_hud:
            joined_hud = True
            time.sleep(3)
            xdo("F1")
            print("[driver] HUD hidden", flush=True)
        elif "[CAM] shot " in line:
            name = line.split("[CAM] shot ", 1)[1].strip().split()[0]
            th = threading.Thread(target=take, args=(name,))
            th.start()
            threads.append(th)
        elif "[CAM] done" in line:
            for th in threads:
                th.join()
            print("[driver] all poses done", flush=True)
            os.kill(pid, signal.SIGTERM)
            sys.exit(0)
for th in threads:
    th.join()
print("[driver] timeout or client exited", flush=True)
if alive():
    os.kill(pid, signal.SIGTERM)
