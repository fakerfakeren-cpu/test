"""Download a vanilla Minecraft version (server jar, and optionally client + libraries + assets).
usage: python3 fetch_mc.py <version> <outdir> [--client]"""
import concurrent.futures as cf
import hashlib
import json
import os
import sys
import urllib.request

MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"


def get(url, path=None, sha1=None):
    if path and os.path.exists(path) and (sha1 is None or hashlib.sha1(open(path, "rb").read()).hexdigest() == sha1):
        return path
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            break
        except Exception:
            if attempt == 3:
                raise
    if path is None:
        return data
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path


def rules_ok(rules, features=None):
    if not rules:
        return True
    allowed = False
    for r in rules:
        match = True
        os_ = r.get("os")
        if os_:
            if "name" in os_ and os_["name"] != "linux":
                match = False
            if "arch" in os_ and os_["arch"] not in ("x86_64", "amd64"):
                match = False
        feats = r.get("features")
        if feats:
            for k, v in feats.items():
                if bool((features or {}).get(k)) != v:
                    match = False
        if match:
            allowed = r["action"] == "allow"
    return allowed


def main():
    version, out = sys.argv[1], sys.argv[2]
    want_client = "--client" in sys.argv
    os.makedirs(out, exist_ok=True)
    manifest = json.loads(get(MANIFEST))
    print("latest:", manifest["latest"])
    entry = next((v for v in manifest["versions"] if v["id"] == version), None)
    if entry is None:
        print("versions:", [v["id"] for v in manifest["versions"][:15]])
        sys.exit(f"version {version} not in manifest")
    vj_path = get(entry["url"], os.path.join(out, f"{version}.json"))
    vj = json.load(open(vj_path))
    print("version type:", vj.get("type"), "java:", vj.get("javaVersion"), "main:", vj.get("mainClass"))
    get(vj["downloads"]["server"]["url"], os.path.join(out, "server.jar"), vj["downloads"]["server"]["sha1"])
    if not want_client:
        return
    get(vj["downloads"]["client"]["url"], os.path.join(out, "client.jar"), vj["downloads"]["client"]["sha1"])
    jobs = []
    cp = []
    for lib in vj["libraries"]:
        if not rules_ok(lib.get("rules")):
            continue
        art = lib.get("downloads", {}).get("artifact")
        if art:
            p = os.path.join(out, "libraries", art["path"])
            jobs.append((art["url"], p, art.get("sha1")))
            cp.append(p)
        nat = lib.get("natives", {}).get("linux")
        if nat:
            c = lib["downloads"]["classifiers"][nat.replace("${arch}", "64")]
            p = os.path.join(out, "libraries", c["path"])
            jobs.append((c["url"], p, c.get("sha1")))
            cp.append(p)  # legacy natives jars: LWJGL 3 can also load from the classpath
    ai = vj["assetIndex"]
    idx_path = get(ai["url"], os.path.join(out, "assets", "indexes", ai["id"] + ".json"))
    objs = json.load(open(idx_path))["objects"]
    for name, o in objs.items():
        h = o["hash"]
        jobs.append((f"https://resources.download.minecraft.net/{h[:2]}/{h}",
                     os.path.join(out, "assets", "objects", h[:2], h), h))
    print(f"downloading {len(jobs)} files")
    with cf.ThreadPoolExecutor(32) as ex:
        list(ex.map(lambda j: get(*j), jobs))
    with open(os.path.join(out, "classpath.json"), "w") as f:
        json.dump(cp + [os.path.join(out, "client.jar")], f)
    print("client ready")


if __name__ == "__main__":
    main()
