"""Generate plan.json (B10: best-Vastu straight stair). Stilt + 2 + roof garden.
B10: one straight stair along the south wall climbing WEST, stacked on every floor (foot at the back, top at the front).
Main door at the front in west padas 3-4; a locked entry hall runs beside the stair to its foot. Laundry and storage under it.
B9 notes follow.
B9: one straight stair along the south wall, starting just inside the main door at the front and climbing east, repeated
directly above itself on every floor (stacked). Laundry and storage sit under the ground flight. The first floor gains a
bedroom (north-centre, head south); the second floor keeps the B6 lounge, master and a guest room / study with ensuite.
Coordinates in metres. x: west->east from the road boundary. z: north->south from the north boundary. y: height.
"""
import json

Y = [0.0, 3.15, 6.30, 9.45]
CL = 3.0
G = -0.15
N0, N1, S1, S0 = 0.7, 0.93, 5.866, 6.096
W0, E1, E0 = 0.9, 11.26, 11.49
LANE = (4.866, 5.866)                     # the stair lane along the south wall
NR = 17
RISE = round(3.15 / NR, 5)
TREAD = 0.25
SF = 8.55                                 # foot of every flight (back)
SM1 = SF - 8 * TREAD                      # 6.55 rest landing (east edge)
SM0 = SM1 - 1.0                           # 5.55
ST = SM0 - 7 * TREAD                      # 3.80 top of every flight (front)
TL = SF + 1.0                             # 9.55 foot landing at the back
HOLE_E = SF - 1.0                         # 7.55: floors cover the four lowest treads of the flight below
GZ = (4.79, 4.84)                         # open (north) side of the stair: baluster screen
CAB_H = 2.4
CW = 4.65                                 # roof cabin west wall

walls, decks, slabs, furn, finishes, rooms, columns = [], [], [], [], [], [], []
balusters, rails, swalls = [], [], []
r3 = lambda v: round(v, 3)

def W(id, lv, axis, x1, x2, z1, z2, kind='ext', y0=None, y1=None, open=None):
    b = Y[lv] if lv >= 0 else 0
    walls.append(dict(id=id, lv=lv, axis=axis, x1=x1, x2=x2, z1=z1, z2=z2, kind=kind,
                      y0=round(b if y0 is None else y0, 3), y1=round(b + CL if y1 is None else y1, 3), open=open or []))

def F(id, lv, name, x1, x2, z1, z2, h, mat, y=0, **kw):
    d = dict(id=id, lv=lv, name=name, x1=x1, x2=x2, z1=z1, z2=z2, y0=round(Y[lv] + y if lv >= 0 else y, 3), h=h, mat=mat)
    d.update(kw); furn.append(d)

def FIN(lv, x1, x2, z1, z2, mat, y=0.0):
    finishes.append(dict(lv=lv, x1=x1, x2=x2, z1=z1, z2=z2, mat=mat, y=round(Y[lv] + y + 0.002, 3)))

def R(id, lv, name, x1, x2, z1, z2, spawn, notes, short=None, **kw):
    d = dict(id=id, lv=lv, name=name, short=short or name, x1=x1, x2=x2, z1=z1, z2=z2,
             y=Y[lv] if lv >= 0 else 0, spawn=spawn, notes=notes); d.update(kw); rooms.append(d)

# ---------------- structure ----------------
for x in (0.9, 4.6, 8.25, 11.11):
    columns.append(dict(x1=x, x2=r3(x + 0.38), z1=N0, z2=N1))
    columns.append(dict(x1=x, x2=r3(x + 0.38), z1=S1, z2=S0))

# ---------------- decks: floors keep a stairwell over the higher part of the flight below ----------------
decks.append(dict(id='stilt', x1=W0, x2=E0, z1=N0, z2=S0, y=Y[0], t=0.15, kind='slab'))
for lv in (1, 2, 3):
    for i, (x1, x2, z1, z2) in enumerate([(W0, ST, N0, S0), (ST, SF, N0, LANE[0]), (HOLE_E, SF, LANE[0], S0), (ST, HOLE_E, S1, S0), (SF, E0, N0, S0)]):
        decks.append(dict(id=f'slab{lv}{i}', x1=x1, x2=x2, z1=z1, z2=z2, y=Y[lv], t=0.15, kind='slab'))

# ---------------- the stair: one straight flight per storey, stacked, rising west ----------------
mid = lambda d: (d['x1'] + d['x2']) / 2
for f in range(3):
    b = Y[f]; st = []
    for i in range(1, 9):
        st.append(dict(id=f's{f}A{i}', x1=r3(SF - i * TREAD), x2=r3(SF - (i - 1) * TREAD), z1=LANE[0], z2=LANE[1], y=r3(b + i * RISE), t=0.3, kind='step'))
    st.append(dict(id=f's{f}M', x1=SM0, x2=SM1, z1=LANE[0], z2=LANE[1], y=r3(b + 9 * RISE), t=0.2, kind='step'))
    for j in range(1, 8):
        st.append(dict(id=f's{f}B{j}', x1=r3(SM0 - j * TREAD), x2=r3(SM0 - (j - 1) * TREAD), z1=LANE[0], z2=LANE[1], y=r3(b + (9 + j) * RISE), t=0.3, kind='step'))
    decks.extend(st)
    # stair side: a short solid wall that rakes with the flight (rounded top, timber handrail on it). You can walk under its high end.
    for k, d in enumerate(st):
        W(f'G{f}{k}', f, 'x', d['x1'], d['x2'], GZ[0], GZ[1], 'sguard', max(b, r3(d['y'] - 0.35)), r3(d['y'] + 0.95))
    pts = lambda z: [[r3(x), r3(d['y'] + 0.9), z] for d in st for x in ([d['x2'] - 0.05, mid(d), d['x1'] + 0.05] if d['x2'] - d['x1'] > 0.5 else [mid(d)])]
    top = [[SF, r3(b + 0.9)]] + [[p[0], p[1]] for p in pts(0)] + [[ST, r3(Y[f + 1] + 0.9)]]
    swalls.append(dict(kind='rake', z1=GZ[0], z2=GZ[1], pts=[[x, t, max(b, r3(t - 1.25))] for x, t in top]))
    rails.append(pts(5.83))
# floor edge of the stairwell on the upper floors: a 1.0 m knee wall with a rounded top and a handrail
for lv in (1, 2):
    W(f'K{lv}', lv, 'x', ST, HOLE_E, GZ[0], GZ[1], 'knee', Y[lv], Y[lv] + 1.0)
    swalls.append(dict(kind='knee', x1=ST, x2=HOLE_E, y0=Y[lv], y1=Y[lv] + 1.0, z1=GZ[0], z2=GZ[1], rail=[ST, 6.55]))

for x1, x2, gl in ((2.4, ST, False), (ST, HOLE_E, True), (HOLE_E, 7.665, False)):
    slabs.append(dict(x1=x1, x2=x2, z1=4.751, z2=S0, y=Y[3] + CAB_H + 0.15, t=0.15, glass=gl))   # skylight over the stairwell

# ---------------- compound + gates (pedestrian gate in west padas 3–4, Sugriva / Pushpadanta) ----------------
W('C1', -1, 'z', -0.15, 0, -0.15, 6.246, 'compound', G, 2.7, [
    dict(a=0.15, b=3.35, type='gate', closed=True, label='Car gate G1 (sliding, vertical timber battens)', rel_h=2.3),
    dict(a=3.6, b=4.74, type='gate', closed=False, rel_h=2.45, batten=True, label='Entrance gate G2: 1.14 m double door, vertical timber battens to match the car gate')])
W('C2', -1, 'x', 0, 12.342, -0.15, 0, 'compound', G, 1.8)
W('C3', -1, 'z', 12.192, 12.342, 0, 6.246, 'compound', G, 1.8)
W('C4', -1, 'x', 0, W0, S0, 6.246, 'compound', G, 2.7)
W('C5', -1, 'x', E0, 12.192, S0, 6.246, 'compound', G, 1.8)

# ---------------- stilt ----------------
W('S0s', 0, 'x', W0, E0, S1, S0)
W('S0md', 0, 'z', 2.4, 2.55, 3.6, S1, 'int', open=[dict(a=3.68, b=4.74, type='door', hinge='a', side=1, main=True, head=2.4,
    label='Main door D1: 1.06 × 2.40 m, rectangular, vertical timber battens to match the car gate')])
W('S0sw', 0, 'x', 2.55, TL, 3.6, 3.65, 'screen')            # steel-framed glass screen: stair, laundry and stores locked but full of light
W('S0ce', 0, 'z', TL, TL + 0.115, 3.6, S1, 'int')
W('S0fn', 0, 'x', TL + 0.115, E1, 3.485, 3.6, 'int', open=[dict(a=10.2, b=10.9, type='door', hinge='a', side=1, label='Store door (from car porch)')])
W('S0e', 0, 'z', E1, E0, 3.485, S1)
for i, x in enumerate((0.9, 4.6, 8.25, 11.11)):
    F(f'col{i}', 0, 'RCC column 230 × 380', x, r3(x + 0.38), N0, N1, CL, 'render')

# ---------------- upper floor shells ----------------
for lv in (1, 2):
    p = f'L{lv}'
    par, gl = (1.05, False) if lv == 1 else (0.45, True)
    lab = 'Loggia arch (first floor, open)' if lv == 1 else 'Glazed arch (second-floor lounge, openable steel-framed glass)'
    W(p + 'arch', lv, 'z', W0, 1.05, N0, S0, 'ext', open=[
        dict(a=1.15, b=3.15, type='arch', par=par, spring=1.8, glazed=gl, label=lab),
        dict(a=3.65, b=5.65, type='arch', par=par, spring=1.8, glazed=gl, label=lab)])
    W(p + 's', lv, 'x', 1.05, E0, S1, S0)

# first floor
W('L1e', 1, 'z', E1, E0, N1, S1, open=[dict(a=2.3, b=3.5, type='window', sill=1.05, head=2.1, label='Kitchen window over the counter (east, for fumes and light)')])
W('L1n', 1, 'x', 1.05, E0, N0, N1, open=[
    dict(a=2.85, b=3.35, type='window', sill=1.5, head=2.1, label='Bathroom high window (north)'),
    dict(a=4.3, b=5.5, type='window', sill=2.15, head=2.6, label='Bedroom 1 clerestory window (north, over the wardrobe)'),
    dict(a=5.95, b=6.45, type='window', sill=0.9, head=2.4, label='Living window left of the TV (north)'),
    dict(a=7.75, b=8.25, type='window', sill=0.9, head=2.4, label='Living window right of the TV (north)'),
    dict(a=9.1, b=9.9, type='window', sill=1.2, head=2.4, label='Kitchen window (north)')])
W('L1g', 1, 'z', 2.4, 2.55, N1, S1, 'glaze', open=[
    dict(a=1.0, b=2.1, type='window', sill=1.2, head=2.1, label='Bathroom window (obscure glass, to loggia)'),
    dict(a=2.45, b=3.6, type='door', slide=True, label='Steel-framed sliding door, bedroom 1 to loggia'),
    dict(a=3.95, b=5.7, type='window', sill=0.45, head=2.6, label='Landing window to loggia')])
W('L1ps', 1, 'x', 2.55, 3.965, 2.2, 2.315, 'int', open=[dict(a=2.75, b=3.45, type='door', hinge='a', side=-1, label='Bedroom 1 ensuite door')])
W('L1pe', 1, 'z', 3.85, 3.965, N1, 2.2, 'int')
W('L1bs', 1, 'x', 2.55, 5.715, 3.735, 3.85, 'int', open=[dict(a=2.75, b=3.45, type='door', slide=True, label='Bedroom 1 door (pocket slider, from the front hall)')])
W('L1be', 1, 'z', 5.6, 5.715, N1, 3.735, 'int')

# second floor (as B6, with the bedroom-2 room now a guest room / study)
W('L2e', 2, 'z', E1, E0, N1, S1, open=[dict(a=1.2, b=1.6, type='window', sill=1.0, head=2.1, label='Guest room side window (east)')])
W('L2n', 2, 'x', 1.05, E0, N0, N1, open=[
    dict(a=4.8, b=6.3, type='window', sill=0.9, head=2.4, label='Master bedroom window (north)'),
    dict(a=9.4, b=10.6, type='window', sill=0.9, head=2.4, label='Guest room / study window (north)')])
W('L2g', 2, 'z', 2.4, 2.55, N1, 2.565, 'int', open=[dict(a=1.1, b=2.2, type='window', sill=1.8, head=2.3, label='Ensuite high window (obscure glass)')])
W('L2rs', 2, 'x', 4.215, E1, 3.735, 3.85, 'int', open=[
    dict(a=6.85, b=7.5, type='door', slide=True, label='Master bedroom door (pocket slider, from the hall)'),
    dict(a=8.6, b=9.35, type='door', hinge='a', side=-1, label='Guest room / study door'),
    dict(a=9.9, b=10.6, type='door', hinge='a', side=1, label='Guest room ensuite door')])
W('L2ee', 2, 'z', 4.1, 4.215, N1, 3.85, open=[dict(a=1.75, b=2.44, type='door', slide=True, label='Master ensuite door (pocket slider)')], kind='int')
W('L2es', 2, 'x', 2.55, 4.1, 2.45, 2.565, 'int')
W('L2bw', 2, 'z', 7.53, 7.645, N1, 3.735, 'int')
W('L2fe', 2, 'z', TL, TL + 0.115, 3.85, S1, 'int')

# roof: the stair cabin now sits at the back, where the top flight arrives; the tank stands in the south-west corner
R3 = Y[3]
W('Rn', 3, 'x', W0, E0, N0, N1, 'parapet', R3, R3 + 1.0)
W('Rs1', 3, 'x', W0, 2.4, S1, S0, 'parapet', R3, R3 + 1.0)
W('Rs2', 3, 'x', 7.665, E0, S1, S0, 'parapet', R3, R3 + 1.0)
W('Rw', 3, 'z', W0, 1.13, N1, S1, 'parapet', R3, R3 + 1.0)
W('Re', 3, 'z', E1, E0, N1, S1, 'parapet', R3, R3 + 1.0)
W('Rcs', 3, 'x', 2.4, 7.665, S1, S0, 'ext', R3, R3 + CAB_H)
W('Rcn', 3, 'x', 2.4, 7.665, 4.751, LANE[0], 'ext', R3, R3 + CAB_H, [dict(a=2.62, b=3.42, type='door', hinge='a', side=-1, label='Door to the roof garden')])
W('Rcw', 3, 'z', 2.4, 2.55, LANE[0], S1, 'ext', R3, R3 + CAB_H)
W('Rce', 3, 'z', HOLE_E, 7.665, LANE[0], S1, 'ext', R3, R3 + CAB_H)

# ---------------- finishes ----------------
FIN(0, W0, 2.4, 3.6, S1, 'checker'); FIN(0, 2.55, TL, 3.65, S1, 'checker')
FIN(0, W0, E1, N1, 3.6, 'concrete'); FIN(0, TL + 0.115, E1, 3.6, S1, 'concrete')
for lv in (1, 2):
    FIN(lv, 1.05, 2.4, N1, S1, 'terracotta')
FIN(1, 2.55, 3.85, N1, 2.2, 'wet'); FIN(1, 3.965, 5.6, N1, 2.315, 'oxide'); FIN(1, 2.55, 5.6, 2.315, 3.735, 'oxide')
FIN(1, 2.55, SF, 3.85, LANE[0], 'stoneTile'); FIN(1, 2.55, ST, LANE[0], S1, 'stoneTile'); FIN(1, HOLE_E, SF, LANE[0], S1, 'stoneTile')
FIN(1, 5.715, E1, N1, 3.85, 'stoneTile'); FIN(1, SF, E1, 3.85, S1, 'stoneTile'); FIN(1, 6.0, 8.4, 1.6, 3.55, 'rug', 0.006)
FIN(2, 4.215, 7.53, N1, 3.735, 'oxide'); FIN(2, 2.55, 4.1, 2.565, 3.735, 'stoneTile'); FIN(2, 2.55, 4.1, N1, 2.45, 'wet'); FIN(2, 7.645, E1, N1, 3.735, 'oxide')
FIN(2, 2.55, TL, 3.85, LANE[0], 'stoneTile'); FIN(2, 2.55, ST, LANE[0], S1, 'stoneTile'); FIN(2, HOLE_E, TL, LANE[0], S1, 'stoneTile')
FIN(2, TL + 0.115, E1, 3.85, S1, 'wet'); FIN(2, 10.36, E1, 4.966, S1, 'wetdark', 0.005); FIN(2, 3.2, 4.1, N1, 1.7, 'wetdark', 0.005)
FIN(3, 1.13, E1, N1, 4.751, 'terracotta'); FIN(3, 7.665, E1, 4.751, S1, 'terracotta'); FIN(3, 1.13, 2.4, 4.751, S1, 'terracotta')
FIN(3, 2.55, ST, LANE[0], S1, 'stoneTile'); FIN(3, 1.9, 4.9, 1.75, 4.45, 'lawn', 0.01)

# ---------------- furniture: stilt ----------------
F('car', 0, 'Car (sub-4 m hatch/sedan, 4.00 × 1.75 m)', 1.3, 5.3, 0.95, 2.7, 1.5, 'car', shape='car')
F('bike', 0, 'Motorcycle (2.00 × 0.70 m)', 6.0, 8.0, 1.0, 1.7, 1.1, 'black', shape='bike')
F('sump', 0, 'Underground sump hatch (north-east)', 10.2, 11.0, 1.1, 1.9, 0.02, 'steel', solid=False)
F('scr1', 0, 'Planter + timber batten screen', 1.3, 2.4, 3.45, 3.6, 2.4, 'walnut', shape='screen')
F('pplant', 0, 'Entry planter (shade plants)', 1.5, 2.4, 5.45, S1, 0.45, 'render', shape='planter')
F('olive', 0, 'Potted olive tree', 0.95, 1.4, 4.9, 5.35, 0.5, 'terracotta', shape='pot')
F('shoe', 0, 'Shoe cabinet + bench', 2.55, 2.9, 4.95, S1, 0.9, 'walnut')
F('wmG', 0, 'Front-load washing machine (under the stair)', ST, 4.4, 5.266, S1, 0.85, 'white')
F('usG', 0, 'Compact utility sink (under the stair)', ST, 4.3, LANE[0] + 0.04, 5.24, 0.85, 'render')
F('lshelf', 0, 'Detergent shelf', ST, 4.4, 5.3, S1, 0.3, 'walnut', y=1.3, solid=False, shape='shelves')
F('lbask', 0, 'Laundry basket', 4.95, 5.35, 5.45, 5.8, 0.5, 'cane', solid=False)
F('ucup', 0, 'Storage cupboard under the rest landing', SM0 + 0.05, SM1, LANE[0] + 0.04, S1, 1.3, 'walnut')
F('ldrawer', 0, 'Pull-out drawers under the low end of the stair', SM1 + 0.05, 7.5, LANE[0] + 0.04, S1, 0.5, 'walnut')
F('store0', 0, 'Tall shallow shelving', SF + 0.05, TL, 3.7, 4.0, 2.2, 'walnut', shape='shelves')
F('shelf', 0, 'Store shelving', 10.9, E1, 3.7, 5.8, 2.0, 'walnut')
F('fbed2', 0, 'Front garden bed', 0.05, 0.85, 4.75, 6.05, 0.3, 'render', y=G, shape='planter')
F('tree', 0, 'Frangipani', 0.25, 0.65, 5.3, 5.7, 3.2, 'tree', y=G + 0.3, shape='tree', solid=False)
F('gl1', 0, 'Entrance gate leaf (open, timber battens)', 0.0, 0.57, 3.6, 3.65, 2.45, 'walnut', y=G, shape='battenleaf')
F('gl2', 0, 'Entrance gate leaf (open, timber battens)', 0.0, 0.57, 4.69, 4.74, 2.45, 'walnut', y=G, shape='battenleaf')

# ---------------- first floor ----------------
F('bp1a', 1, 'Loggia planter', 1.05, 1.4, 1.2, 3.1, 0.45, 'render', shape='planter')
F('bp1b', 1, 'Loggia planter', 1.05, 1.4, 3.7, 5.6, 0.45, 'render', shape='planter')
F('bch1', 1, 'Cane chair', 1.6, 2.15, 4.2, 4.75, 0.8, 'cane', shape='chair', back='x2')
F('btab', 1, 'Side table', 1.65, 2.05, 4.9, 5.3, 0.5, 'walnut')
F('bch2', 1, 'Cane chair', 1.6, 2.15, 5.3, 5.85, 0.8, 'cane', shape='chair', back='x2')
F('pwc', 1, 'WC', 3.2, 3.85, 1.0, 1.4, 0.42, 'ceramic', shape='wc')
F('pbas', 1, 'Basin', 2.55, 2.95, 0.95, 1.4, 0.85, 'ceramic')
F('b1bed', 1, 'Double bed 1.37 × 1.90 m (4.5 ft, head to the east)', 3.7, 5.6, 2.33, 3.7, 0.55, 'linen', shape='bed', head='x2')
F('b1wd', 1, 'Wardrobe 1.64 m (0.57 m deep, sliding doors)', 3.965, 5.6, N1, 1.5, 2.1, 'sage', shape='wardrobe')
F('tvc', 1, 'TV console (walnut, fluted)', 6.55, 7.65, N1, 1.28, 0.5, 'walnut')
F('tv', 1, 'TV (50")', 6.5, 7.7, N1, 0.98, 0.7, 'black', y=1.0, solid=False)
F('sofa', 1, '3-seater sofa 2.0 m facing the TV', 6.1, 8.1, 2.6, 3.45, 0.8, 'linen', shape='sofa', back='z2')
F('ctab', 1, 'Coffee table', 6.6, 7.6, 1.85, 2.25, 0.4, 'walnut')
F('arm1', 1, 'Armchair', 5.8, 6.45, 1.45, 2.1, 0.8, 'cane', shape='chair', back='x1')
F('run', 1, 'Cooking run on the east wall (cook faces east)', 10.66, E1, 2.25, 5.1, 0.9, 'walnut', shape='counterE', hob=[3.95, 4.55])
F('hood', 1, 'Chimney hood ducted out through the east wall', 10.76, E1, 3.95, 4.55, 0.55, 'steel', y=1.6, solid=False)
F('overE', 1, 'Overhead cabinets', 10.91, E1, 3.6, 5.1, 0.75, 'white', y=2.15, solid=False, shape='overheadE')
F('loftE', 1, 'Loft storage over the window', 10.76, E1, 2.145, 3.5, 0.7, 'white', y=2.2, solid=False)
F('pantry', 1, 'Tall pull-out pantry', 9.6, 10.5, 5.266, S1, 2.2, 'white', shape='tall')
F('fridge', 1, 'Refrigerator (double door)', 10.56, E1, 5.166, S1, 1.85, 'steel')
F('island', 1, 'Slim island with the kitchen sink, parallel to the counter: 1.40 × 0.60 m', 9.0, 9.6, 2.0, 3.4, 0.9, 'quartz', shape='islandZ', over=0)
F('pooja', 1, 'Open mandir unit (idols facing west)', 10.76, E1, 1.0, 2.0, 1.0, 'walnut', shape='pooja')
F('hseat', 1, 'Reading bench by the landing window', 2.55, 2.95, 5.0, 5.8, 0.45, 'walnut')

# ---------------- second floor (B6) ----------------
F('bp2a', 2, 'Indoor planter under the arch', 1.05, 1.4, 1.2, 3.1, 0.45, 'render', shape='planter')
F('seat', 2, 'Built-in window seat under the arch', 1.05, 1.6, 4.2, 5.6, 0.45, 'render', shape='bench')
F('arm', 2, 'Reading armchair', 1.55, 2.2, 1.35, 2.0, 0.8, 'cane', shape='chair', back='x1')
F('lsofaA', 2, 'L-shaped sofa (long side)', 2.6, 4.1, 2.565, 3.4, 0.8, 'linen', shape='sofa', back='z1')
F('lsofaB', 2, 'L-shaped sofa (return)', 3.25, 4.1, 3.4, 4.05, 0.8, 'linen', shape='sofa', back='x2', arms='end')
F('lctab', 2, 'Coffee table', 2.6, 3.1, 3.55, 4.0, 0.4, 'walnut')
F('mbed', 2, 'Queen bed 1.52 × 2.03 m (head to the south)', 4.9, 6.42, 1.705, 3.735, 0.55, 'linen', shape='bed', head='z2')
F('mbs1', 2, 'Bedside', 4.45, 4.85, 3.285, 3.735, 0.5, 'walnut')
F('mbs2', 2, 'Bedside', 6.47, 6.8, 3.335, 3.735, 0.5, 'walnut')
F('mwd', 2, 'Wardrobe 1.67 m + loft (0.45 m deep, sliding doors)', 7.08, 7.53, N1, 2.6, 2.9, 'walnut', shape='wardrobe')
F('eswc', 2, 'WC', 2.55, 3.2, 0.95, 1.35, 0.42, 'ceramic', shape='wc')
F('esbas', 2, 'Basin', 2.55, 3.0, 1.5, 1.95, 0.85, 'ceramic')
F('esgl', 2, 'Shower glass', 3.2, 4.1, 1.7, 1.72, 2.0, 'glass')
F('bed2', 2, 'Queen bed 1.52 × 2.03 m (head to the east)', 9.23, E1, 1.57, 3.09, 0.55, 'linen', shape='bed', head='x2')
F('bs2a', 2, 'Bedside', 10.81, E1, 1.07, 1.52, 0.5, 'walnut')
F('bs2b', 2, 'Bedside', 10.81, E1, 3.14, 3.59, 0.5, 'walnut')
F('wd2', 2, 'Wardrobe 1.62 m', 7.645, 8.245, N1, 2.55, 2.9, 'sage', shape='wardrobe')
F('e2wc', 2, 'WC', 10.61, E1, 4.2, 4.6, 0.42, 'ceramic', shape='wc')
F('e2bas', 2, 'Basin', 9.75, 10.25, 5.42, S1, 0.85, 'ceramic')
F('e2gl', 2, 'Shower glass', 10.34, 10.36, 5.1, 5.6, 2.0, 'glass')

# ---------------- roof ----------------
F('rpn', 3, 'Raised planter (herbs, curry leaf)', 1.13, 5.6, N1, 1.43, 0.5, 'render', shape='planter')
F('rpn2', 3, 'Raised planter (vegetables)', 5.7, 7.6, N1, 1.43, 0.5, 'render', shape='planter')
F('rps', 3, 'Raised planter (bougainvillea, ixora)', 7.8, E1, 5.366, S1, 0.5, 'render', shape='planter')
for i, (x, z) in enumerate([(1.6, 1.7), (4.9, 1.7), (1.6, 4.38), (4.9, 4.38)]):
    F(f'pp{i}', 3, 'Pergola post', x, r3(x + 0.12), z, r3(z + 0.12), 2.6, 'walnut')
F('perg', 3, 'Timber pergola', 1.6, 5.02, 1.7, 4.5, 0.2, 'walnut', y=2.6, shape='pergola', solid=False)
F('rbench', 3, 'Built-in bench', 1.75, 2.25, 2.0, 4.2, 0.45, 'render', shape='bench')
F('rtab', 3, 'Low table', 2.8, 3.6, 2.6, 3.4, 0.45, 'walnut')
F('solar', 3, 'Solar PV on raised frame', 8.6, 11.1, 1.1, 3.6, 0.08, 'solar', y=2.4, solid=False, shape='solar')
F('tank', 3, 'Overhead water tank 2,000 L (south-west, on the stair cabin)', 2.5, 3.72, 4.85, 5.95, 1.3, 'black', y=CAB_H + 0.3, solid=False, shape='tank')
F('lines', 3, 'Drying lines', 8.4, 11.0, 4.0, 5.1, 0.02, 'black', y=1.8, solid=False, shape='lines')

# ---------------- rooms ----------------
STAIR_NOTES = [
  'One straight stair, repeated directly above itself on every floor, along the south wall. It climbs towards the west: the Vastu-preferred direction (east to west), in the south of the plot.',
  'Each storey has 17 risers of about 185 mm (an odd number, as Vastu prefers) and 250 mm treads, 1.0 m wide, with a 1 m rest landing midway. No U or L turns.',
  'You arrive at the front of each floor facing west and turn right (clockwise) into the room. The next flight starts at the back, directly above the one you came up.',
  'The room side has a short solid wall that rises with the stair, with rounded edges and a timber handrail on top; the floor edge of each stairwell has a 1.0 m wall of the same kind. A second handrail runs on the south wall, and a skylight over the stairwell lights all three floors.',
  'The laundry and storage fit underneath the ground flight. Structurally each flight is an RCC waist slab from the floor beam to the rest-landing beam, carried on the south-wall columns.']
R('road', -1, 'Road (west)', -9, 0, -6, 12, [-2.4, 4.2, G], [
  'You are on the road, looking east: white render, a timber-batten car gate and a batten gate for people.',
  'The pedestrian gate and the main door both sit in the 3rd–4th of the nine west-side padas, counted from the south-west (Sugriva and Pushpadanta), the ones Vastu recommends for a west-facing entrance.'])
R('front', 0, 'Front garden & gates', 0, W0, 0, S0, [0.45, 4.2, G], [
  'The 0.9 m front setback stays unpaved: a planted bed with a frangipani and stepping stones from the gate.'], 'Front garden')
R('laundry', 0, 'Laundry under the stair', ST, SM0, LANE[0], S1, [4.75, 5.37, 0], [
  'The washing machine and utility sink sit under the high end of the stair, by the main door, with 2.2–2.7 m of headroom.',
  'Clothes go straight up the stair to dry on the roof.'], 'Laundry', early=True, ymax=0.5)
R('stairs', -1, 'Stair', ST, SF, LANE[0], LANE[1], [8.42, 5.37, round(RISE, 3)], STAIR_NOTES, early=True)
R('foyer', 0, 'Entrance foyer', 2.55, ST, 3.65, S1, [3.1, 4.3, 0], [
  'The main door is 1.06 × 2.40 m, rectangular, with the same vertical timber battens as the car gate. It faces west, in the auspicious padas, 2.4 m from the gate.',
  'Inside, a shoe cabinet and bench. The laundry is on your right under the stair; the entry hall runs straight ahead beside the stair to its foot.'])
R('utility', 0, 'Entry hall & stores', ST, TL, 3.65, S1, [5.0, 4.25, 0], [
  'A locked 1.2 m entry hall runs beside the stair, lit through the glass screen from the car porch. Under the stair: a cupboard below the rest landing and drawers below the low end. Tall cupboards stand at the far end.',
  'At the end, turn right round onto the first step: the stair climbs back towards the front, westwards, as Vastu prefers.',
  'Utility use at stilt level should be confirmed with the authority, as stilts are meant for parking.'], 'Entry hall')
R('store', 0, 'Store', TL + 0.115, E1, 3.6, S1, [10.55, 4.5, 0], ['A store opening off the car porch for tools, pump controls and garden things.'])
R('passage', 0, 'Entry porch', W0, 2.4, 3.6, S1, [1.6, 4.2, 0], [
  'A short planted porch under the first-floor loggia, with a black-and-white checkerboard floor, leads from the gate to the main door.'], 'Porch')
R('carbay', 0, 'Car porch (stilt)', W0, E1, N0, 3.6, [6.0, 2.6, 0], [
  'Your car parks in the north-west, which Vastu prefers for vehicles. The motorcycle is behind it, with room for a second car in tandem.',
  'The underground sump sits under the north-east end, where Vastu wants water storage below ground.'], 'Car porch')
R('sidepath', -1, 'North side setback', W0, 12.192, 0, N0, [6.0, 0.35, G], ['Kept open and unpaved. Vastu favours more openness to the north and east, and this strip lets the north windows breathe.'])
R('rear', -1, 'Rear setback', E0, 12.192, N0, S0, [11.85, 2.5, G], ['A 0.7 m rear setback for the rainwater recharge pit and the kitchen chimney outlet.'])

R('landing1', 1, 'First-floor stair foot', SF, TL, 3.85, S1, [9.05, 4.3, Y[1]], [
  'The next flight up starts here at the back, beside the kitchen, directly above the flight below.'], 'Stair foot')
R('pooja', 1, 'Pooja corner', 10.0, E1, N1, 2.1, [10.3, 1.5, Y[1]], [
  'An open mandir corner in the north-east (Ishanya), kept open and light, as Vastu likes.',
  'The walnut mandir unit stands against the east wall with the idols facing west, so you pray facing east. No toilet is near it.'], 'Pooja')
R('living', 1, 'Living room', 5.715, 9.0, N1, 3.85, [5.95, 3.7, Y[1]], [
  'The living room is now about 3.3 × 2.9 m, about 45% bigger: a 2.0 m three-seater, an armchair and a coffee table face a 50" TV between two north windows (window, TV, window), open to the kitchen.',
  'It grew because the bathroom moved inside bedroom 1, so the bedroom could shift west into space the hall did not need.',
  'The second-floor family lounge is the larger gathering space.'])
R('kitchen', 1, 'Kitchen', 9.0, E1, N1, S1, [9.9, 3.9, Y[1]], [
  'The kitchen is in the south-east (Agni corner), the Vastu-preferred spot. The hob is on the east wall, so the cook faces east.',
  'The sink is on a slim 1.40 × 0.60 m island parallel to the counter, with a 1.06 m aisle. A window over the counter and a ducted chimney take the fumes out.',
  'Storage: overheads and a loft on the east wall, and a tall pull-out pantry and the fridge on the south wall.'])
R('powder', 1, 'Bedroom 1 ensuite', 2.55, 3.85, N1, 2.2, [3.1, 1.9, Y[1]], [
  'The first-floor bathroom is now inside bedroom 1, in its north-west corner (a Vastu-preferred spot for toilets): WC, basin and a hand shower.',
  'Living-room guests reach it through the bedroom. It is ventilated through an obscure-glass window onto the loggia and a high north window.'], 'Ensuite')
R('bed1', 1, 'Bedroom 1', 2.55, 5.6, N1, 3.735, [3.0, 2.8, Y[1]], [
  'Bedroom 1 now runs from the loggia to the living-room wall, with its own bathroom in the north-west corner and a sliding door to the loggia.',
  'A 4.5 ft double bed with its head to the east (Vastu-preferred), a 1.64 m wardrobe along the north wall under a clerestory window. About 7 m² of bedroom floor plus the ensuite.',
  'It sits in the west-north of the floor, which Vastu suits for children or guests.'], 'Bedroom 1')
R('balc1', 1, 'First-floor loggia', 1.05, 2.4, N1, S1, [1.75, 2.4, Y[1]], ['A 1.35 m deep loggia behind two arches, reached from bedroom 1 by a steel-framed slider; the landing window looks onto it too. It shades the west glass.'], 'Loggia')
R('hall1', 1, 'Front hall & landing', 2.55, SF, 3.85, LANE[1], [3.2, 4.3, Y[1]], [
  'The stair arrives here at the front. Turn right: bedroom 1 is straight ahead, and the hall runs along the stair to the living room, kitchen and the next flight at the back.'], 'Hall')

R('lounge', 2, 'Family lounge', 1.05, 4.1, 2.565, S1, [2.35, 4.5, Y[2]], [
  'A family lounge where everyone can spend time together. You arrive into it straight off the stair at the front: turn right and you are in.',
  'The second-floor balcony is enclosed: steel-framed glass fills both arches above a 0.45 m sill and opens for breeze. An L-shaped sofa, a coffee table, a window seat, and no TV.',
  'The west glass gets afternoon sun. Use low-e glass and fit blinds or bamboo chiks inside the arches.'], 'Family lounge')
R('nook', 2, 'Reading nook', 1.05, 2.4, N1, 2.565, [1.9, 2.35, Y[2]], ['The north corner of the enclosed balcony: an armchair and an indoor planter under the glazed arch.'], 'Nook')
R('ensuite', 2, 'Master ensuite', 2.55, 4.1, N1, 2.45, [3.5, 2.1, Y[2]], ['A north-west ensuite (Vastu-friendly for toilets): shower, WC and basin, with a high obscure window and an exhaust duct.'], 'Ensuite')
R('master', 2, 'Master bedroom', 4.215, 7.53, N1, 3.735, [4.5, 2.4, Y[2]], [
  'About 9.3 m²: a queen bed with its head to the south, a 1.67 m wardrobe with a loft, a north window, and the ensuite through a pocket door.',
  'Vastu note: the master sits nearer the north-centre, which is weaker than the south-west (the stair takes the south). The bed faces correctly.'], 'Master')
R('hall2', 2, 'Upper hall', 4.1, TL, 3.85, S1, [5.0, 4.3, Y[2]], ['The hall runs from the lounge along the stair to the guest room and to the roof flight at the back.'], 'Hall')
R('bed2', 2, 'Guest room / study', 7.645, E1, N1, 3.735, [8.3, 3.2, Y[2]], [
  'A guest room or study: a queen bed with its head to the east, a 1.6 m wardrobe and its own ensuite.',
  'It sits in the north-east, which Vastu suits for study.'], 'Guest / study')
R('bath2', 2, 'Guest ensuite', TL + 0.115, E1, 3.85, S1, [10.2, 4.85, Y[2]], ['WC, basin and shower, in the south-east, a Vastu compromise noted in the report. Its exhaust duct runs to the roof.'], 'Ensuite')

R('cabin', 3, 'Stair cabin', 2.55, ST, LANE[0], S1, [3.15, 5.37, Y[3]], ['The stair lands at the front inside a small cabin under a glass skylight. The water tank sits on top, in the south-west.'], 'Cabin')
R('roof', 3, 'Roof garden', 1.13, 7.665, N1, S1, [3.0, 4.3, Y[3]], [
  'Turn right out of the cabin onto the garden: raised planters, a lawn under a timber pergola, a bench and a low table.',
  'The water tank sits on the cabin in the south-west, the heavy corner, as Vastu advises. The north-east of the roof is kept light: only solar panels and drying lines.'], 'Roof garden')
R('roofrear', 3, 'Drying deck', 7.665, E1, N1, S1, [9.9, 3.0, Y[3]], ['Drying lines in full sun beside raised solar panels.'], 'Drying deck')

tour = ['road', 'front', 'passage', 'carbay', 'foyer', 'laundry', 'utility', 'stairs', 'hall1', 'bed1', 'powder', 'balc1', 'living', 'kitchen', 'pooja', 'landing1',
        'lounge', 'nook', 'master', 'ensuite', 'hall2', 'bed2', 'bath2', 'cabin', 'roof', 'roofrear']

arrow = [[SF - 0.1, 5.37], [ST + 0.1, 5.37]]
stair = dict(balusters=balusters, rails=rails, walls=swalls, arrows={'0': arrow, '1': arrow, '2': arrow},
             ups={'0': [7.6, 5.25], '1': [7.6, 5.25], '2': [7.6, 5.25]}, dns={'1': [4.3, 5.25], '2': [4.3, 5.25], '3': [4.3, 5.25]},
             lamps=[[6.0, 2.7, 5.4], [6.0, 5.85, 5.4], [6.0, 9.0, 5.4], [4.5, 11.6, 5.4]])

plan = dict(version='B10 · 19 Oct 2026', levels=Y, ceiling=CL, ground=G,
            plot=dict(depth=12.192, width=6.096), setbacks=dict(front=0.9, rear=0.702, north=0.7, south=0),
            footprint=dict(x1=W0, x2=E0, z1=N0, z2=S0),
            bounds=dict(x1=-6, x2=12.19, z1=-1.5, z2=7.6),
            start=dict(x=-2.4, z=4.2, yaw=-1.5708),
            neighbours=[dict(x1=0.6, x2=12.6, z1=-3.2, z2=-1.0, h=9.6), dict(x1=0.6, x2=12.6, z1=7.1, z2=9.3, h=6.6), dict(x1=13.2, x2=16, z1=-3.2, z2=9.3, h=9.6)],
            walkFence=[dict(x1=0, x2=12.6, z1=-1.6, z2=-0.15), dict(x1=0, x2=12.6, z1=6.246, z2=7.7)],
            spirals=[], stairLane=dict(x1=ST, x2=SF, z1=LANE[0], z2=LANE[1]), stair=stair, columns=columns,
            walls=walls, decks=decks, slabs=slabs, furn=furn, finishes=finishes, rooms=rooms, tour=tour)
json.dump(plan, open('src/plan.json', 'w'), indent=1)
print(len(walls), 'walls', len(decks), 'decks', len(furn), 'furn', len(rooms), 'rooms', 'rise', RISE)
