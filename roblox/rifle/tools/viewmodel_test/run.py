import subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
LUAU = os.path.join(here, '..', 'luau', 'luau')
setup = open('/home/user/test/roblox/rifle/viewmodel/ScarViewmodelSetup.lua').read()
def run(variant, twice=False):
    parts = [open(os.path.join(here, 'mock.luau')).read(), f'VARIANT = {variant}\n', open(os.path.join(here, 'scene.luau')).read()]
    for _ in range(2 if twice else 1):
        parts.append('do local ok, err = pcall(function()\n' + setup + '\nend)\nif not ok then print("SETUP ERROR: " .. tostring(err)) end end\n')
    parts.append('for _, l in ipairs(OUTPUT) do RAWPRINT(l) end\n')
    parts.append(open(os.path.join(here, 'driver.luau')).read())
    src = os.path.join(here, f'_run_{variant}{"_twice" if twice else ""}.luau')
    open(src, 'w').write('\n'.join(parts))
    r = subprocess.run([LUAU, src], capture_output=True, text=True)
    return r.stdout + r.stderr
if __name__ == '__main__':
    v = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    out = run(v, twice=(len(sys.argv) > 2 and sys.argv[2] == 'twice'))
    open(os.path.join(here, f'out_{v}.txt'), 'w').write(out)
    for line in out.splitlines():
        if not line.startswith('F '): print(line)
