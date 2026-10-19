"""Export plan.json as a Wavefront OBJ + MTL (metres, Y up, x = east, z = south) for Blender, Twinmotion, D5 Render, Lumion.
Usage: python3 export_obj.py [plan.json] [out_basename]
"""
import json, math, sys

P = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'plan.json'))
OUT = sys.argv[2] if len(sys.argv) > 2 else 'chikkalasandra_house'

MATS = {  # name: (rgb 0-1, opacity, roughness-ish Ns)
    'render': ((0.93, 0.925, 0.90), 1, 10), 'wall_interior': ((0.95, 0.937, 0.91), 1, 10), 'slab': ((0.91, 0.90, 0.875), 1, 10),
    'glass': ((0.74, 0.82, 0.83), 0.3, 200), 'walnut': ((0.43, 0.27, 0.16), 1, 60), 'white_lacquer': ((0.95, 0.945, 0.935), 1, 120),
    'quartz': ((0.957, 0.953, 0.94), 1, 160), 'sage': ((0.62, 0.69, 0.60), 1, 40), 'linen': ((0.91, 0.88, 0.83), 1, 5),
    'cane': ((0.78, 0.64, 0.42), 1, 20), 'black_steel': ((0.13, 0.13, 0.12), 1, 90), 'steel': ((0.72, 0.725, 0.705), 1, 150),
    'ceramic': ((0.965, 0.96, 0.945), 1, 200), 'terracotta': ((0.71, 0.35, 0.23), 1, 10), 'stone': ((0.78, 0.75, 0.69), 1, 30),
    'stair_tread': ((0.82, 0.80, 0.75), 1, 40), 'car_paint': ((0.42, 0.50, 0.55), 1, 150), 'planting': ((0.38, 0.50, 0.27), 1, 5),
    'solar': ((0.11, 0.16, 0.23), 1, 150), 'floor_stone': ((0.80, 0.78, 0.73), 1, 60), 'floor_oxide': ((0.66, 0.75, 0.59), 1, 80),
    'floor_terracotta': ((0.72, 0.39, 0.25), 1, 15), 'floor_wet': ((0.83, 0.83, 0.80), 1, 40), 'floor_wet_dark': ((0.66, 0.67, 0.64), 1, 40),
    'floor_checker': ((0.55, 0.55, 0.53), 1, 80), 'floor_concrete': ((0.65, 0.64, 0.61), 1, 10), 'lawn': ((0.44, 0.56, 0.28), 1, 5),
    'rug': ((0.85, 0.81, 0.74), 1, 2), 'ground_grass': ((0.56, 0.60, 0.45), 1, 2), 'asphalt': ((0.33, 0.34, 0.35), 1, 5),
    'neighbour': ((0.85, 0.835, 0.80), 1, 5), 'gate_timber': ((0.43, 0.27, 0.16), 1, 40), 'tree_trunk': ((0.43, 0.35, 0.28), 1, 5),
}
FURN_MAT = {'render': 'render', 'walnut': 'walnut', 'white': 'white_lacquer', 'quartz': 'quartz', 'sage': 'sage', 'linen': 'linen',
            'cane': 'cane', 'black': 'black_steel', 'steel': 'steel', 'ceramic': 'ceramic', 'terracotta': 'terracotta', 'glass': 'glass',
            'car': 'car_paint', 'tree': 'planting', 'solar': 'solar'}
FIN_MAT = {'stoneTile': 'floor_stone', 'oxide': 'floor_oxide', 'terracotta': 'floor_terracotta', 'wet': 'floor_wet', 'wetdark': 'floor_wet_dark',
           'checker': 'floor_checker', 'concrete': 'floor_concrete', 'lawn': 'lawn', 'rug': 'rug'}

V, groups = [], {}          # groups[(object name, material)] = list of faces (vertex index tuples)
cur = ['scene']

def obj(name): cur[0] = name

def face(mat, idx): groups.setdefault((cur[0], mat), []).append(idx)

def box(x1, x2, y0, y1, z1, z2, mat):
    if x2 - x1 < 1e-4 or y1 - y0 < 1e-4 or z2 - z1 < 1e-4: return
    b = len(V) + 1
    for y in (y0, y1):
        for x, z in ((x1, z1), (x2, z1), (x2, z2), (x1, z2)): V.append((x, y, z))
    # bottom 0-3, top 4-7; counter-clockwise seen from outside
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        face(mat, tuple(b + i for i in f))

def quad_floor(x1, x2, z1, z2, y, mat):
    b = len(V) + 1
    for x, z in ((x1, z1), (x1, z2), (x2, z2), (x2, z1)): V.append((x, y, z))
    face(mat, (b, b + 1, b + 2, b + 3))

def rod(a, c, r, mat):
    """Square-section bar between two 3D points."""
    d = [c[i] - a[i] for i in range(3)]; L = math.sqrt(sum(t * t for t in d))
    if L < 1e-4: return
    d = [t / L for t in d]
    up = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)
    u = (d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0]); n = math.sqrt(sum(t * t for t in u)); u = [t / n * r for t in u]
    w = (d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0])
    b = len(V) + 1
    for p in (a, c):
        for su, sw in ((-1, -1), (1, -1), (1, 1), (-1, 1)): V.append(tuple(p[i] + su * u[i] + sw * w[i] for i in range(3)))
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        face(mat, tuple(b + i for i in f))

def wall_piece(w, a, b, y0, y1, mat):
    if w['axis'] == 'x': box(a, b, y0, y1, w['z1'], w['z2'], mat)
    else: box(w['x1'], w['x2'], y0, y1, a, b, mat)

def glass_pane(w, a, b, y0, y1):
    if w['axis'] == 'x':
        m = (w['z1'] + w['z2']) / 2; box(a, b, y0, y1, m - 0.008, m + 0.008, 'glass')
        for x in (a, b - 0.035): box(x, x + 0.035, y0, y1, m - 0.025, m + 0.025, 'black_steel')
        for y in (y0, y1 - 0.035): box(a, b, y, y + 0.035, m - 0.025, m + 0.025, 'black_steel')
    else:
        m = (w['x1'] + w['x2']) / 2; box(m - 0.008, m + 0.008, y0, y1, a, b, 'glass')
        for z in (a, b - 0.035): box(m - 0.025, m + 0.025, y0, y1, z, z + 0.035, 'black_steel')
        for y in (y0, y1 - 0.035): box(m - 0.025, m + 0.025, y, y + 0.035, a, b, 'black_steel')

def leaf_rect(w, o):
    T, L = 0.04, o['b'] - o['a']
    hinge = o['b'] if o.get('hinge') == 'b' else o['a']; inward = -1 if o.get('hinge') == 'b' else 1
    face_ = (w['z2'] if w['axis'] == 'x' else w['x2']) if o['side'] > 0 else (w['z1'] if w['axis'] == 'x' else w['x1'])
    u1, u2 = (hinge, hinge + T) if inward > 0 else (hinge - T, hinge)
    v1, v2 = (face_, face_ + L) if o['side'] > 0 else (face_ - L, face_)
    return (u1, u2, v1, v2) if w['axis'] == 'x' else (v1, v2, u1, u2)

# ---------------- context ----------------
obj('site_ground'); box(-12, 18, P['ground'] - 0.1, P['ground'], -6, 13, 'ground_grass')
obj('site_road'); quad_floor(-9, 0, -6, 12, P['ground'] + 0.002, 'asphalt')
obj('site_neighbours')
for n in P['neighbours']: box(n['x1'], n['x2'], P['ground'], n['h'], n['z1'], n['z2'], 'neighbour')

# ---------------- structure ----------------
lvname = lambda y: 'stilt' if y < 1 else 'first' if y < 4.5 else 'second' if y < 7.6 else 'roof'
for d in P['decks']:
    if d['kind'] == 'slab':
        obj(f"slab_{lvname(d['y'])}"); box(d['x1'], d['x2'], d['y'] - d['t'], d['y'], d['z1'], d['z2'], 'slab' if d['y'] > 0.5 else 'stone')
    else:
        obj('stair_treads'); box(d['x1'], d['x2'], d['y'] - 0.2, d['y'], d['z1'], d['z2'], 'stair_tread')
for s in P['slabs']:
    obj('stair_cabin_roof')
    if s.get('glass'):
        box(s['x1'], s['x2'], s['y'] - 0.03, s['y'], s['z1'], s['z2'], 'glass')
        x = s['x1'] + 0.6
        while x < s['x2']: box(x - 0.02, x + 0.02, s['y'] - 0.06, s['y'], s['z1'], s['z2'], 'black_steel'); x += 0.6
    else: box(s['x1'], s['x2'], s['y'] - s['t'], s['y'], s['z1'], s['z2'], 'slab')
obj('columns')
L3 = P['levels'][3]
for c in P['columns']: box(c['x1'], c['x2'], -1.2 if False else P['ground'], L3, c['z1'], c['z2'], 'render')

# ---------------- walls with openings ----------------
for w in P['walls']:
    kind = w['kind']
    if kind == 'sguard': continue
    lv = w['lv']; name = 'walls_boundary' if lv == -1 and not w['id'].startswith('CORE') else 'walls_stair_core' if w['id'].startswith('CORE') else f"walls_{['stilt', 'first', 'second', 'roof'][lv]}"
    obj(name)
    y0, y1 = w['y0'], w['y1']
    lo, hi = (w['x1'], w['x2']) if w['axis'] == 'x' else (w['z1'], w['z2'])
    if kind == 'screen':
        glass_pane(w, lo, hi, y0, y1)
        n = max(1, round((hi - lo) / 0.45))
        for i in range(1, n):
            u = lo + (hi - lo) * i / n
            if w['axis'] == 'x': m = (w['z1'] + w['z2']) / 2; box(u - 0.012, u + 0.012, y0, y1, m - 0.025, m + 0.025, 'black_steel')
        continue
    if kind == 'rail':
        ax = w['axis'] == 'x'; c = (w['z1'] + w['z2']) / 2 if ax else (w['x1'] + w['x2']) / 2
        u = lo + 0.05
        while u < hi:
            box(u - 0.009, u + 0.009, y0, y1 - 0.05, c - 0.009, c + 0.009, 'black_steel') if ax else box(c - 0.009, c + 0.009, y0, y1 - 0.05, u - 0.009, u + 0.009, 'black_steel'); u += 0.11
        box(lo, hi, y1 - 0.05, y1, c - 0.04, c + 0.04, 'walnut') if ax else box(c - 0.04, c + 0.04, y1 - 0.05, y1, lo, hi, 'walnut')
        continue
    mat = 'wall_interior' if kind in ('int', 'guard') else 'render'
    curx = lo
    for o in sorted(w.get('open', []), key=lambda o: o['a']):
        wall_piece(w, curx, o['a'], y0, y1, mat)
        a, b = o['a'], o['b']
        t = o['type']
        if t == 'window':
            wall_piece(w, a, b, y0, y0 + o['sill'], mat); wall_piece(w, a, b, y0 + o['head'], y1, mat); glass_pane(w, a, b, y0 + o['sill'], y0 + o['head'])
        elif t == 'door':
            head = o.get('head', 2.6 if o.get('slide') else 2.1)
            wall_piece(w, a, b, y0 + head, y1, mat)
            if o.get('slide'): glass_pane(w, a, b, y0, y0 + head) if kind == 'glaze' else None
            elif o.get('side'):
                x1_, x2_, z1_, z2_ = leaf_rect(w, o)
                box(x1_, x2_, y0, y0 + head - 0.05, z1_, z2_, 'gate_timber' if o.get('main') else 'black_steel' if w['id'].startswith('Rc') else 'walnut')
        elif t == 'gate':
            top = y0 + o['rel_h']
            wall_piece(w, a, b, top, y1, mat)
            if o.get('closed'):
                xb = w['x1'] - 0.005; z = a + 0.03
                box(xb - 0.03, xb, y0 + 0.05, top, a, b, 'gate_timber')
                while z < b - 0.02: box(xb - 0.075, xb - 0.03, y0 + 0.05, top, z, z + 0.045, 'walnut'); z += 0.075
        elif t == 'arch':
            r = (b - a) / 2; cxa = a + r; N = 18
            if o['par'] > 0: wall_piece(w, a, b, y0, y0 + o['par'], mat)
            for i in range(N):
                u1, u2 = a + (b - a) * i / N, a + (b - a) * (i + 1) / N; um = (u1 + u2) / 2
                top = y0 + o['spring'] + math.sqrt(max(0, r * r - (um - cxa) ** 2))
                wall_piece(w, u1, u2, top, y1, mat)
                if o.get('glazed'):
                    m = (w['x1'] + w['x2']) / 2
                    box(m - 0.008, m + 0.008, y0 + o['par'], top, u1, u2, 'glass')
            if o.get('glazed'):
                m = (w['x1'] + w['x2']) / 2
                box(m - 0.02, m + 0.02, y0 + o['par'], y0 + o['spring'] + r, cxa - 0.02, cxa + 0.02, 'black_steel')
                box(m - 0.02, m + 0.02, y0 + o['spring'] - 0.02, y0 + o['spring'] + 0.02, a, b, 'black_steel')
        curx = max(curx, b)
    wall_piece(w, curx, hi, y0, y1, mat)

# ---------------- stair balusters + handrails ----------------
obj('stair_balustrade')
st = P.get('stair') or {}
for bl in st.get('balusters', []):
    x = bl['x1'] + 0.055
    while x < bl['x2'] - 0.005: box(x - 0.009, x + 0.009, bl['y0'], bl['y1'], bl['z'] - 0.009, bl['z'] + 0.009, 'black_steel'); x += 0.11
for pts in st.get('rails', []):
    for i in range(1, len(pts)): rod(pts[i - 1], pts[i], 0.022, 'walnut')

# ---------------- floor finishes ----------------
for f in P['finishes']:
    obj(f"floors_{['stilt', 'first', 'second', 'roof'][f['lv']]}"); quad_floor(f['x1'], f['x2'], f['z1'], f['z2'], f['y'], FIN_MAT.get(f['mat'], 'floor_stone'))

# ---------------- furniture (simplified shapes) ----------------
for f in P['furn']:
    x1, x2, z1, z2, y0, h = f['x1'], f['x2'], f['z1'], f['z2'], f['y0'], f['h']; y1 = y0 + h
    m = FURN_MAT.get(f['mat'], 'white_lacquer'); sh = f.get('shape')
    obj('furniture_' + f['id'])
    if sh == 'car':
        box(x1, x2, y0 + 0.18, y0 + 0.85, z1, z2, 'car_paint'); box(x1 + 0.9, x2 - 0.7, y0 + 0.85, y0 + 1.42, z1 + 0.1, z2 - 0.1, 'glass')
        box(x1 + 0.95, x2 - 0.75, y0 + 1.42, y0 + 1.5, z1 + 0.12, z2 - 0.12, 'car_paint')
        for x in (x1 + 0.45, x2 - 0.95):
            for z in (z1, z2 - 0.2): box(x, x + 0.5, y0, y0 + 0.6, z, z + 0.2, 'black_steel')
    elif sh == 'tree':
        cx, cz = (x1 + x2) / 2, (z1 + z2) / 2
        box(cx - 0.06, cx + 0.06, y0, y0 + h * 0.55, cz - 0.06, cz + 0.06, 'tree_trunk'); box(cx - 0.8, cx + 0.8, y0 + h * 0.5, y1, cz - 0.8, cz + 0.8, 'planting')
    elif sh in ('planter', 'pot'):
        box(x1, x2, y0, y1, z1, z2, 'render' if sh == 'planter' else 'terracotta'); box(x1 + 0.04, x2 - 0.04, y1, y1 + 0.35, z1 + 0.04, z2 - 0.04, 'planting')
    elif sh == 'sofa':
        box(x1, x2, y0, y0 + 0.45, z1, z2, 'linen'); bk = f.get('back', 'z2')
        if bk == 'z1': box(x1, x2, y0 + 0.45, y1, z1, z1 + 0.22, 'linen')
        elif bk == 'z2': box(x1, x2, y0 + 0.45, y1, z2 - 0.22, z2, 'linen')
        elif bk == 'x1': box(x1, x1 + 0.22, y0 + 0.45, y1, z1, z2, 'linen')
        else: box(x2 - 0.22, x2, y0 + 0.45, y1, z1, z2, 'linen')
    elif sh == 'bed':
        box(x1, x2, y0, y0 + 0.32, z1, z2, 'walnut'); box(x1 + 0.02, x2 - 0.02, y0 + 0.32, y1, z1 + 0.02, z2 - 0.02, 'linen')
        hd = f.get('head', 'z2')
        if hd == 'x2': box(x2 - 0.05, x2, y0, y0 + 1.15, z1, z2, 'walnut')
        elif hd == 'x1': box(x1, x1 + 0.05, y0, y0 + 1.15, z1, z2, 'walnut')
        elif hd == 'z2': box(x1, x2, y0, y0 + 1.15, z2 - 0.05, z2, 'walnut')
        else: box(x1, x2, y0, y0 + 1.15, z1, z1 + 0.05, 'walnut')
    elif sh in ('counterE', 'islandZ'):
        box(x1, x2, y0, y1 - 0.04, z1, z2, 'walnut' if sh == 'counterE' else 'white_lacquer'); box(x1, x2, y1 - 0.04, y1, z1, z2, 'quartz')
        if sh == 'counterE': box(x2 - 0.02, x2, y1, y0 + 2.15, z1, z2, 'stone'); box(x1 + 0.1, x2 - 0.06, y1, y1 + 0.008, f['hob'][0], f['hob'][1], 'black_steel')
        if sh == 'islandZ': cx, cz = (x1 + x2) / 2, (z1 + z2) / 2; box(cx - 0.2, cx + 0.22, y1, y1 + 0.004, cz - 0.3, cz + 0.3, 'steel')
    elif sh == 'pergola':
        for z in (z1, z2 - 0.12): box(x1, x2, y0, y0 + 0.15, z, z + 0.12, 'walnut')
        x = x1
        while x < x2: box(x, x + 0.06, y0 + 0.15, y0 + 0.22, z1 - 0.1, z2 + 0.1, 'walnut'); x += 0.22
    elif sh == 'solar':
        box(x1, x2, y0 + 0.25, y0 + 0.3, z1, z2, 'solar')
        for x, z in ((x1 + 0.1, z1 + 0.1), (x2 - 0.15, z1 + 0.1), (x1 + 0.1, z2 - 0.15), (x2 - 0.15, z2 - 0.15)): box(x, x + 0.05, L3, y0 + 0.25, z, z + 0.05, 'steel')
    elif sh == 'tank':
        box(x1, x2, y0, y1, z1, z2, 'black_steel')
    elif sh == 'lines':
        z = z1
        while z <= z2: box(x1, x2, y0, y0 + 0.01, z, z + 0.01, 'black_steel'); z += 0.35
        for x in (x1, x2 - 0.04): box(x, x + 0.04, L3, y0 + 0.05, z1, z2, 'black_steel')
    elif sh == 'battenleaf':
        box(x1, x2, y0, y1, z1, z2, 'gate_timber')
    elif sh == 'shelves':
        for k in range(4): box(x1, x2, y0 + k * h / 3, y0 + k * h / 3 + 0.03, z1, z2, 'walnut')
    elif sh == 'pooja':
        box(x1, x2, y0, y0 + 0.8, z1, z2, 'walnut'); box(x1 + 0.05, x2, y0 + 0.8, y0 + 0.82, z1, z2, 'quartz'); box(x2 - 0.06, x2, y0 + 0.82, y0 + 1.9, z1, z2, 'walnut')
    elif sh == 'chair':
        box(x1, x2, y0 + 0.36, y0 + 0.44, z1, z2, 'cane'); bk = f.get('back', 'x1')
        if bk == 'x1': box(x1, x1 + 0.06, y0 + 0.44, y1, z1, z2, 'walnut')
        elif bk == 'x2': box(x2 - 0.06, x2, y0 + 0.44, y1, z1, z2, 'walnut')
        for x in (x1 + 0.03, x2 - 0.07):
            for z in (z1 + 0.03, z2 - 0.07): box(x, x + 0.04, y0, y0 + 0.36, z, z + 0.04, 'black_steel')
    elif sh == 'bench':
        box(x1, x2, y0, y1, z1, z2, 'render'); box(x1, x2, y1, y1 + 0.06, z1, z2, 'walnut')
    else:
        box(x1, x2, y0, y1, z1, z2, m)

# ---------------- write ----------------
with open(OUT + '.mtl', 'w') as fm:
    fm.write('# Chikkalasandra House materials\n')
    for n, (rgb, d, ns) in MATS.items():
        fm.write(f'\nnewmtl {n}\nKa 0 0 0\nKd {rgb[0]:.3f} {rgb[1]:.3f} {rgb[2]:.3f}\nKs 0.04 0.04 0.04\nNs {ns}\nd {d}\nillum {4 if d < 1 else 2}\n')
nf = 0
with open(OUT + '.obj', 'w') as fo:
    fo.write(f"# Chikkalasandra House {P['version']} - blockout model\n# Units: metres. Y up. x = east (from the road boundary), z = south (from the north boundary).\n")
    fo.write(f'mtllib {OUT.split("/")[-1]}.mtl\n')
    for v in V: fo.write(f'v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n')
    byobj = {}
    for (o, m), fs in groups.items(): byobj.setdefault(o, []).append((m, fs))
    for o, lst in byobj.items():
        fo.write(f'o {o}\n')
        for m, fs in lst:
            fo.write(f'usemtl {m}\n')
            for f in fs: fo.write('f ' + ' '.join(map(str, f)) + '\n'); nf += 1
print(len(V), 'vertices', nf, 'faces', len(byobj), 'objects')
