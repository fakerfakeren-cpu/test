import sys, importlib
mod = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else 'model3d')
V, group_of = mod.V, mod.group_of
def find(sol):
    bad = set()
    for (i,j,k) in sol:
        # check 3 axis-planes for edge-only diagonal contacts
        for a,b in (((1,0,0),(0,1,0)),((1,0,0),(0,0,1)),((0,1,0),(0,0,1))):
            for sa in (1,-1):
                for sb in (1,-1):
                    d=(i+sa*a[0]+sb*b[0], j+sa*a[1]+sb*b[1], k+sa*a[2]+sb*b[2])
                    e1=(i+sa*a[0], j+sa*a[1], k+sa*a[2]); e2=(i+sb*b[0], j+sb*b[1], k+sb*b[2])
                    if d in sol and e1 not in sol and e2 not in sol:
                        bad.add(tuple(sorted([(i,j,k),d])))
    return bad
for g in ('Body','Magazine','Slide','Trigger'):
    sol={v for v in V if group_of(V[v]['part'])==g}
    b=find(sol)
    print(g,len(b))
    for p,q in sorted(b)[:40]:
        print('  ',p,V[p]['part'],(V[p]['x'],V[p]['y']),'<->',q,V[q]['part'],(V[q]['x'],V[q]['y']))
