"""Generate plan.json (B6: B5 + enclosed second-floor family lounge): stilt + 2 + roof garden, stacked straight stairs.
B5: larger open kitchen in the south-east with east-facing cooking, sink on the island, east window + chimney duct;
first-floor bedroom reduced to a study / guest room in the north-west; pooja in the north-east; powder room in the
north-west; bigger second-floor master with a north-west ensuite; 17-riser stairs; Vastu and structural notes.
Coordinates in metres. x: west->east from the road boundary. z: north->south from the north boundary. y: height.
"""
import json

Y = [0.0, 3.15, 6.30, 9.45]
CL = 3.0
G = -0.15
N0, N1, S1, S0 = 0.7, 0.93, 5.866, 6.096
W0, E1, E0 = 0.9, 11.26, 11.49
LANE = (4.866, 5.866)
NR = 17                                   # odd number of risers per storey
RISE = round(3.15 / NR, 5)
TREAD = 0.25
SFOOT = 8.55
SMID1 = SFOOT - 8 * TREAD                 # 6.55: flight 1 = 9 risers
SMID0 = SMID1 - 1.0                       # 5.55: half landing 1.0 m
STOP = round(SMID0 - 7 * TREAD, 3)        # 3.80: flight 2 = 8 risers
HOLE_E = 7.55                             # slab covers the lane east of here (headroom ≥ 2.1 m over steps 1-4)
FOOT_E = 9.55
CAB_H = 2.4

walls, decks, slabs, furn, finishes, rooms, columns = [], [], [], [], [], [], []

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

# ---------------- structure: column grid (230 × 380), continuous from footing to roof ----------------
for x in (0.9, 4.6, 8.25, 11.11):
    columns.append(dict(x1=x, x2=round(x + 0.38, 3), z1=N0, z2=N1))
    columns.append(dict(x1=x, x2=round(x + 0.38, 3), z1=S1, z2=S0))

# ---------------- decks ----------------
decks.append(dict(id='stilt', x1=W0, x2=E0, z1=N0, z2=S0, y=Y[0], t=0.15, kind='slab'))
for lv in (1, 2, 3):
    for i, (x1, x2, z1, z2) in enumerate([(W0, STOP, N0, S0), (STOP, HOLE_E, N0, LANE[0]), (STOP, HOLE_E, S1, S0), (HOLE_E, E0, N0, S0)]):
        decks.append(dict(id=f'slab{lv}{i}', x1=x1, x2=x2, z1=z1, z2=z2, y=Y[lv], t=0.15, kind='slab'))
for f in range(3):
    b = Y[f]
    for i in range(1, 9):
        decks.append(dict(id=f's{f}A{i}', x1=round(SFOOT - i * TREAD, 3), x2=round(SFOOT - (i - 1) * TREAD, 3), z1=LANE[0], z2=LANE[1], y=round(b + i * RISE, 3), t=0.3, kind='step'))
    decks.append(dict(id=f's{f}M', x1=SMID0, x2=SMID1, z1=LANE[0], z2=LANE[1], y=round(b + 9 * RISE, 3), t=0.2, kind='step'))
    for j in range(1, 8):
        decks.append(dict(id=f's{f}B{j}', x1=round(SMID0 - j * TREAD, 3), x2=round(SMID0 - (j - 1) * TREAD, 3), z1=LANE[0], z2=LANE[1], y=round(b + (9 + j) * RISE, 3), t=0.3, kind='step'))
for x1, x2, gl in ((2.4, STOP, False), (STOP, HOLE_E, True), (HOLE_E, 7.665, False)):
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
W('S0sw', 0, 'x', 5.1, 8.435, 4.79, 4.84, 'screen')
W('S0lp', 0, 'z', 5.1, 5.215, LANE[0], S1, 'int', 0, 1.7)   # locked partition closing the laundry nook from the stair void   # steel-framed glass screen: secure but full of light
W('S0md', 0, 'z', 8.435, 8.55, 3.6, 4.751, 'int', open=[dict(a=3.62, b=4.68, type='door', hinge='a', side=1, main=True, head=2.4, label='Main door D1: 1.06 × 2.40 m, rectangular, vertical timber battens to match the car gate')])
W('S0fn', 0, 'x', 8.435, E1, 3.485, 3.6, 'int', open=[dict(a=10.2, b=10.9, type='door', hinge='a', side=1, label='Store door (from car porch)')])
W('S0fe', 0, 'z', 9.8, 9.915, 3.6, S1, 'int')
W('S0e', 0, 'z', E1, E0, 3.485, S1)
for i, x in enumerate((0.9, 4.6, 8.25, 11.11)):
    F(f'col{i}', 0, 'RCC column 230 × 380', x, round(x + 0.38, 3), N0, N1, CL, 'render')

# ---------------- upper floor shells ----------------
for lv in (1, 2):
    p = f'L{lv}'
    if lv == 1:
        W(p + 'arch', lv, 'z', W0, 1.05, N0, S0, 'ext', open=[
            dict(a=1.15, b=3.15, type='arch', par=1.05, spring=1.8, label='Loggia arch (first floor, open)'),
            dict(a=3.65, b=5.65, type='arch', par=1.05, spring=1.8, label='Loggia arch (first floor, open)')])
    else:
        W(p + 'arch', lv, 'z', W0, 1.05, N0, S0, 'ext', open=[
            dict(a=1.15, b=3.15, type='arch', par=0.45, spring=1.8, glazed=True, label='Glazed arch (second-floor lounge, openable steel-framed glass)'),
            dict(a=3.65, b=5.65, type='arch', par=0.45, spring=1.8, glazed=True, label='Glazed arch (second-floor lounge, openable steel-framed glass)')])
    W(p + 's', lv, 'x', 1.05, E0, S1, S0)
    W(p + 'rail', lv, 'x', STOP, HOLE_E, 4.79, 4.84, 'rail', Y[lv], Y[lv] + 1.0)   # open balustrade over the stairwell

# first floor
W('L1e', 1, 'z', E1, E0, N1, S1, open=[dict(a=2.3, b=3.5, type='window', sill=1.05, head=2.1, label='Kitchen window over the counter (east, for fumes and light)')])
W('L1n', 1, 'x', 1.05, E0, N0, N1, open=[
    dict(a=4.15, b=5.4, type='window', sill=0.9, head=2.4, label='Study window (north)'),
    dict(a=5.8, b=6.25, type='window', sill=0.9, head=2.4, label='Living window left of the TV (north)'),
    dict(a=7.45, b=7.95, type='window', sill=0.9, head=2.4, label='Living window right of the TV (north)'),
    dict(a=8.25, b=9.95, type='window', sill=1.2, head=2.4, label='Kitchen window (north, above shelves)')])
W('L1g', 1, 'z', 2.4, 2.55, N1, S1, 'glaze', open=[
    dict(a=1.0, b=2.1, type='window', sill=1.2, head=2.1, label='Powder room window (obscure glass, to loggia)'),
    dict(a=2.5, b=4.6, type='door', slide=True, label='Steel-framed sliding door, hall to loggia'),
    dict(a=4.95, b=5.7, type='window', sill=0.45, head=2.6, label='Landing window to loggia')])
W('L1ps', 1, 'x', 2.55, 3.965, 2.2, 2.315, 'int', open=[dict(a=2.75, b=3.45, type='door', hinge='a', side=-1, label='Powder room door')])
W('L1pe', 1, 'z', 3.85, 3.965, N1, 3.515, 'int', open=[dict(a=2.6, b=3.3, type='door', hinge='b', side=1, label='Study / guest room door')])
W('L1ss', 1, 'x', 3.965, 5.715, 3.4, 3.515, 'int')
W('L1se', 1, 'z', 5.6, 5.715, N1, 3.4, 'int')

# second floor
W('L2e', 2, 'z', E1, E0, N1, S1, open=[dict(a=1.2, b=1.6, type='window', sill=1.0, head=2.1, label='Bedroom 2 side window (east)')])
W('L2n', 2, 'x', 1.05, E0, N0, N1, open=[
    dict(a=4.8, b=6.3, type='window', sill=0.9, head=2.4, label='Master bedroom window (north)'),
    dict(a=9.4, b=10.6, type='window', sill=0.9, head=2.4, label='Bedroom 2 window (north)')])
W('L2g', 2, 'z', 2.4, 2.55, N1, 2.565, 'int', open=[dict(a=1.1, b=2.2, type='window', sill=1.8, head=2.3, label='Ensuite high window (obscure glass)')])
W('L2rs', 2, 'x', 4.215, E1, 3.735, 3.85, 'int', open=[
    dict(a=6.85, b=7.5, type='door', slide=True, label='Master bedroom door (pocket slider, from the hall)'),
    dict(a=8.6, b=9.35, type='door', hinge='a', side=-1, label='Bedroom 2 door'),
    dict(a=9.9, b=10.6, type='door', hinge='a', side=1, label='Bedroom 2 ensuite door')])
W('L2ee', 2, 'z', 4.1, 4.215, N1, 3.85, 'int', open=[
    dict(a=1.75, b=2.44, type='door', slide=True, label='Master ensuite door (pocket slider)')])
W('L2es', 2, 'x', 2.55, 4.1, 2.45, 2.565, 'int')
W('L2bw', 2, 'z', 7.53, 7.645, N1, 3.735, 'int')
W('L2fe', 2, 'z', FOOT_E, FOOT_E + 0.115, 3.85, S1, 'int')

# roof
R3 = Y[3]
W('Rn', 3, 'x', W0, E0, N0, N1, 'parapet', R3, R3 + 1.0)
W('Rs1', 3, 'x', W0, 2.4, S1, S0, 'parapet', R3, R3 + 1.0)
W('Rs2', 3, 'x', 7.665, E0, S1, S0, 'parapet', R3, R3 + 1.0)
W('Rw', 3, 'z', W0, 1.13, N1, S1, 'parapet', R3, R3 + 1.0)
W('Re', 3, 'z', E1, E0, N1, S1, 'parapet', R3, R3 + 1.0)
W('Rcs', 3, 'x', 2.4, 7.665, S1, S0, 'ext', R3, R3 + CAB_H)
W('Rcn', 3, 'x', 2.4, 7.665, 4.751, LANE[0], 'ext', R3, R3 + CAB_H, [dict(a=2.62, b=3.42, type='door', hinge='a', side=-1, label='Door to roof garden')])
W('Rcw', 3, 'z', 2.4, 2.55, LANE[0], S1, 'ext', R3, R3 + CAB_H)
W('Rce', 3, 'z', HOLE_E, 7.665, LANE[0], S1, 'ext', R3, R3 + CAB_H)

# ---------------- finishes ----------------
FIN(0, W0, 8.435, 3.6, 4.751, 'checker'); FIN(0, W0, STOP, 4.751, S1, 'checker'); FIN(0, 8.55, 9.8, 3.6, S1, 'checker')
FIN(0, W0, E1, N1, 3.485, 'concrete'); FIN(0, 9.915, E1, 3.6, S1, 'concrete')
for lv in (1, 2):
    FIN(lv, 1.05, 2.4, N1, S1, 'terracotta')
FIN(1, 2.55, 3.85, 2.315, S1, 'stoneTile'); FIN(1, 3.85, E1, 3.515, 4.751, 'stoneTile'); FIN(1, 5.715, E1, N1, 3.515, 'stoneTile')
FIN(1, HOLE_E, E1, LANE[0], S1, 'stoneTile'); FIN(1, 3.965, 5.6, N1, 3.4, 'oxide'); FIN(1, 2.55, 3.85, N1, 2.2, 'wet')
FIN(1, 10.16, E1, N1, 2.03, 'oxide')
FIN(2, 4.215, 7.53, N1, 3.735, 'oxide'); FIN(2, 2.55, 4.1, 2.565, 3.735, 'stoneTile'); FIN(2, 2.55, 4.1, N1, 2.45, 'wet'); FIN(2, 7.645, E1, N1, 3.735, 'oxide')
FIN(2, 2.55, FOOT_E, 3.85, 4.751, 'stoneTile'); FIN(2, 2.55, STOP, 4.751, S1, 'stoneTile'); FIN(2, HOLE_E, FOOT_E, LANE[0], S1, 'stoneTile')
FIN(2, FOOT_E + 0.115, E1, 3.85, S1, 'wet'); FIN(2, 10.36, E1, 4.966, S1, 'wetdark', 0.005); FIN(2, 3.2, 4.1, N1, 1.7, 'wetdark', 0.005)
FIN(3, 1.13, E1, N1, 4.751, 'terracotta'); FIN(3, 7.665, E1, 4.751, S1, 'terracotta'); FIN(3, 1.13, 2.4, 4.751, S1, 'terracotta')
FIN(3, 2.55, STOP, LANE[0], S1, 'stoneTile'); FIN(3, 1.9, 4.9, 1.75, 4.45, 'lawn', 0.01)
FIN(1, 6.1, 7.5, 1.6, 2.9, 'rug', 0.006)

# ---------------- furniture ----------------
F('car', 0, 'Car (sub-4 m hatch/sedan, 4.00 × 1.75 m)', 1.3, 5.3, 0.95, 2.7, 1.5, 'car', shape='car')
F('bike', 0, 'Motorcycle (2.00 × 0.70 m)', 6.0, 8.0, 1.0, 1.7, 1.1, 'black', shape='bike')
F('sump', 0, 'Underground sump hatch (north-east)', 10.2, 11.0, 1.1, 1.9, 0.02, 'steel', solid=False)
F('scr1', 0, 'Planter + timber batten screen', 1.4, 2.9, 3.45, 3.6, 2.4, 'walnut', shape='screen')
F('scr2', 0, 'Planter + timber batten screen', 3.9, 7.2, 3.45, 3.6, 2.4, 'walnut', shape='screen')
F('pplant', 0, 'Entry planter (shade plants)', 1.3, 3.0, 5.45, S1, 0.45, 'render', shape='planter')
F('olive', 0, 'Potted olive tree', 0.95, 1.4, 4.9, 5.35, 0.5, 'terracotta', shape='pot')
F('wmG', 0, 'Front-load washing machine (under the stair)', 3.85, 4.45, 5.22, S1, 0.85, 'white')
F('usG', 0, 'Utility sink', 4.5, 5.0, 5.37, S1, 0.85, 'render')
F('lshelf', 0, 'Detergent shelves', 3.85, 5.0, 5.6, S1, 0.6, 'walnut', y=1.25, solid=False, shape='shelves')
F('lbask', 0, 'Laundry basket (under the sink)', 4.55, 4.95, 5.45, 5.8, 0.5, 'cane', solid=False)
F('green', 0, 'Wall planters on the stair wall', 4.2, 8.0, 4.62, 4.751, 0.25, 'render', y=1.1, shape='planter', solid=False)
F('shoe', 0, 'Shoe cabinet + bench', 9.45, 9.8, 4.0, 5.4, 0.9, 'walnut')
F('shelf', 0, 'Store shelving', 10.9, E1, 3.7, 5.8, 2.0, 'walnut')
F('fbed2', 0, 'Front garden bed', 0.05, 0.85, 4.75, 6.05, 0.3, 'render', y=G, shape='planter')
F('tree', 0, 'Frangipani', 0.25, 0.65, 5.3, 5.7, 3.2, 'tree', y=G + 0.3, shape='tree', solid=False)
F('gl1', 0, 'Entrance gate leaf (open, timber battens)', 0.0, 0.57, 3.6, 3.65, 2.45, 'walnut', y=G, shape='battenleaf')
F('gl2', 0, 'Entrance gate leaf (open, timber battens)', 0.0, 0.57, 4.69, 4.74, 2.45, 'walnut', y=G, shape='battenleaf')

for lv in (1, 2):
    F(f'bp{lv}a', lv, 'Indoor planter under the arch' if lv == 2 else 'Loggia planter', 1.05, 1.4, 1.2, 3.1, 0.45, 'render', shape='planter')
    if lv == 1: F('bp1b', 1, 'Loggia planter', 1.05, 1.4, 3.7, 5.6, 0.45, 'render', shape='planter')
F('bch1', 1, 'Cane chair', 1.6, 2.15, 4.2, 4.75, 0.8, 'cane', shape='chair', back='x2')
F('btab', 1, 'Side table', 1.65, 2.05, 4.9, 5.3, 0.5, 'walnut')
F('bch2', 1, 'Cane chair', 1.6, 2.15, 5.3, 5.85, 0.8, 'cane', shape='chair', back='x2')
# powder room (north-west)
F('pwc', 1, 'WC', 3.2, 3.85, 1.0, 1.4, 0.42, 'ceramic', shape='wc')
F('pbas', 1, 'Basin', 2.55, 2.95, 0.95, 1.4, 0.85, 'ceramic')
# study / guest room (north-west)
F('sofabed', 1, 'Sofa-cum-bed 2.0 × 0.9 m (sleep with head to the south)', 4.7, 5.6, 1.3, 3.3, 0.45, 'linen', shape='sofabed')
F('desk1', 1, 'Desk with shelves over', 3.965, 4.6, N1, 1.5, 0.75, 'walnut')
F('shelf1', 1, 'Wall shelves over the desk', 3.965, 4.6, N1, 1.2, 0.9, 'walnut', y=1.2, solid=False, shape='shelves')
# living (north / centre)
F('tvc', 1, 'TV console (walnut, fluted)', 6.3, 7.4, N1, 1.33, 0.5, 'walnut')
F('tv', 1, 'TV (45")', 6.35, 7.35, N1, 0.98, 0.6, 'black', y=1.0, solid=False)
F('sofa', 1, 'Sofa 1.6 m (backed against the stair railing)', 6.35, 7.95, 3.8, 4.65, 0.8, 'linen', shape='sofa', back='z2')
F('ctab', 1, 'Coffee table', 6.65, 7.65, 2.4, 2.95, 0.4, 'walnut')
F('frames', 1, 'Family-memory wall (on the stairwell wall)', 4.2, 6.6, 4.715, 4.751, 1.0, 'black', y=1.2, shape='frames', solid=False)
# kitchen (east / south-east)
F('run', 1, 'Cooking run on the east wall (cook faces east)', 10.66, E1, 2.25, 5.1, 0.9, 'walnut', shape='counterE', hob=[3.95, 4.55])
F('hood', 1, 'Chimney hood ducted out through the east wall', 10.76, E1, 3.95, 4.55, 0.55, 'steel', y=1.6, solid=False)
F('overE', 1, 'Overhead cabinets', 10.91, E1, 3.6, 5.1, 0.75, 'white', y=2.15, solid=False, shape='overheadE')
F('loftE', 1, 'Loft storage over the window', 10.76, E1, 2.145, 3.5, 0.7, 'white', y=2.2, solid=False)
F('pantry', 1, 'Tall pull-out pantry', 9.55, 10.5, 5.266, S1, 2.2, 'white', shape='tall')
F('fridge', 1, 'Refrigerator (double door)', 10.56, E1, 5.166, S1, 1.85, 'steel')
F('island', 1, 'Slim island with the kitchen sink, parallel to the counter: 1.60 × 0.60 m', 9.0, 9.6, 2.3, 3.9, 0.9, 'quartz', shape='islandZ', over=0)
F('sofa2', 1, 'Sofa 1.4 m backed onto the island', 8.05, 8.95, 1.75, 3.15, 0.8, 'linen', shape='sofa', back='x2')
F('pooja', 1, 'Open mandir unit (idols facing west)', 10.76, E1, 1.0, 2.0, 1.0, 'walnut', shape='pooja')

# second floor
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

# roof
F('rpn', 3, 'Raised planter (herbs, curry leaf)', 1.13, 5.6, N1, 1.43, 0.5, 'render', shape='planter')
F('rps', 3, 'Raised planter (bougainvillea, ixora)', 7.8, E1, 5.366, S1, 0.5, 'render', shape='planter')
for i, (x, z) in enumerate([(1.6, 1.7), (4.9, 1.7), (1.6, 4.38), (4.9, 4.38)]):
    F(f'pp{i}', 3, 'Pergola post', x, x + 0.12, z, z + 0.12, 2.6, 'walnut')
F('perg', 3, 'Timber pergola', 1.6, 5.02, 1.7, 4.5, 0.2, 'walnut', y=2.6, shape='pergola', solid=False)
F('rbench', 3, 'Built-in bench', 1.75, 2.25, 2.0, 4.2, 0.45, 'render', shape='bench')
F('rtab', 3, 'Low table', 2.8, 3.6, 2.6, 3.4, 0.45, 'walnut')
F('rpn2', 3, 'Raised planter (vegetables)', 5.7, 7.6, N1, 1.43, 0.5, 'render', shape='planter')
F('solar', 3, 'Solar PV on raised frame', 8.6, 11.1, 1.1, 3.6, 0.08, 'solar', y=2.4, solid=False, shape='solar')
F('tank', 3, 'Overhead water tank 2,000 L (south-west)', 2.5, 3.72, 4.85, 5.95, 1.3, 'black', y=CAB_H + 0.3, solid=False, shape='tank')
F('lines', 3, 'Drying lines', 8.4, 11.0, 4.0, 5.1, 0.02, 'black', y=1.8, solid=False, shape='lines')

# ---------------- rooms ----------------
STAIR_NOTES = [
  'The same straight stair repeats on every floor, directly above the one below: 17 risers of about 185 mm (an odd number, as Vastu prefers), 250 mm treads, 1.0 m wide, with a half landing.',
  'It climbs westwards along the south wall and you turn right (clockwise) at the top: stairs in the south, ascending clockwise, is the Vastu-preferred arrangement.',
  'The stair is open on its room side: slim black-steel balusters at child-safe spacing (under 100 mm gaps) with a timber handrail, plus a second handrail on the wall side. Light reaches it from every room and from a skylight over the stairwell on the roof.',
  'At ground level a steel-framed glass screen replaces the railing, so the stair stays locked behind the main door but still gets light.',
  'Structurally each flight is an RCC waist slab spanning from the floor beam to the half-landing beam, carried on the south-wall columns and the stairwell beam.']
R('road', -1, 'Road (west)', -9, 0, -6, 12, [-2.4, 4.2, G], [
  'You are on the road, looking east: white render, a timber-batten car gate and an arched steel-and-glass gate for people.',
  'The pedestrian gate and the main door both sit in the 3rd–4th of the nine west-side padas, counted from the south-west (Sugriva and Pushpadanta), the ones Vastu recommends for a west-facing entrance.'])
R('front', 0, 'Front garden & gates', 0, W0, 0, S0, [0.45, 4.2, G], [
  'The 0.9 m front setback stays unpaved: a planted bed with a frangipani and stepping stones from the arched gate.'], 'Front garden')
R('laundry', 0, 'Laundry under the stair', STOP, 5.1, LANE[0], S1, [3.5, 5.3, 0], [
  'The laundry nook is under the high end of the stair: a front-load washer, a utility sink, a basket and detergent shelves, with 2.3–2.7 m of headroom over them.',
  'It opens off the planted entry passage, so wet clothes never cross the living floors. A low partition behind it closes off the space under the stair.',
  'Clothes still dry on the roof deck. Under-stair use at stilt level should be confirmed with the authority, as stilts are meant for parking.'], 'Laundry', early=True, ymax=0.5)
R('stairs', -1, 'Stair', STOP, SFOOT, LANE[0], LANE[1], [8.42, 5.37, round(RISE, 3)], STAIR_NOTES, early=True)
R('foyer', 0, 'Entrance foyer', 8.55, 9.8, 3.6, S1, [9.1, 4.3, 0], [
  'The main door is now 1.06 × 2.40 m, rectangular, with the same vertical timber battens as the car gate. It opens inwards, faces west, and locks the stair and the whole house above.',
  'Inside: a shoe cabinet and bench. Turn right twice and the stair runs straight up.'])
R('store', 0, 'Store', 9.915, E1, 3.6, S1, [10.55, 4.5, 0], ['A store opening off the car porch for tools, pump controls and garden things.'])
R('passage', 0, 'Entry passage', W0, 8.435, 3.45, S1, [1.6, 4.2, 0], [
  'A planted entry walk from the arched gate to the main door, with a black-and-white checkerboard floor.'])
R('carbay', 0, 'Car porch (stilt)', W0, E1, N0, 3.45, [6.0, 2.6, 0], [
  'Your car parks in the north-west, which Vastu prefers for vehicles. The motorcycle is behind it, with room for a second car in tandem.',
  'The underground sump sits under the north-east end, where Vastu wants water storage below ground.'], 'Car porch')
R('sidepath', -1, 'North side setback', W0, 12.192, 0, N0, [6.0, 0.35, G], ['Kept open and unpaved. Vastu favours more openness to the north and east, and this strip lets the north windows breathe.'])
R('rear', -1, 'Rear setback', E0, 12.192, N0, S0, [11.85, 2.5, G], ['A 0.7 m rear setback for the rainwater recharge pit and the kitchen chimney outlet.'])

R('balc1', 1, 'First-floor loggia', 1.05, 2.4, N1, S1, [1.75, 2.4, Y[1]], ['A 1.35 m deep loggia behind two arches, reached from the hall by a 2.1 m steel-framed slider. It shades the west glass.'], 'Loggia')
R('powder', 1, 'Common bathroom', 2.55, 3.85, N1, 2.2, [3.1, 1.9, Y[1]], [
  'A compact wet room in the north-west: WC, basin and a hand shower. North-west is a Vastu-preferred spot for toilets.',
  'It is ventilated through an obscure-glass window onto the loggia.'], 'Bath')
R('study', 1, 'Study / guest room', 3.965, 5.6, N1, 3.4, [4.3, 2.8, Y[1]], [
  'The first-floor bedroom has shrunk, as you asked, into a study with a sofa-cum-bed for guests. North-west is where Vastu puts guest rooms.',
  'Desk and shelves sit under the north window. Sleep with the head to the south.'], 'Study / guest')
R('hall1', 1, 'First-floor hall', 2.55, 5.715, 2.315, 4.866, [3.2, 4.3, Y[1]], [
  'You arrive here from the stair and turn right. A 2.1 m slider opens to the loggia, and the bathroom and study are on the left. Ahead, the living room and kitchen form one open space.'], 'Hall')
R('pooja', 1, 'Pooja corner', 10.0, E1, N1, 2.1, [10.3, 1.5, Y[1]], [
  'The pooja room is now an open mandir corner. Its partition walls and the shelves along the north wall are gone, so the north-east stays open and light, which Vastu likes for Ishanya.',
  'A walnut mandir unit stands against the east wall with the idols facing west, so you pray facing east. It is well away from the hob, and no toilet is anywhere near.'], 'Pooja')
R('living', 1, 'Living room', 5.715, 8.0, N1, 4.751, [5.95, 2.2, Y[1]], [
  'The living room sits in the north and centre of the floor. Vastu likes living spaces to the north, and the centre (Brahmasthan) open: no walls, columns or plumbing there.',
  'It is one open space with the kitchen, about 8.7 m long from the study wall to the east window.',
  'The TV now sits on the north wall between two windows (window, TV, window). The main sofa backs onto the stair railing and faces it.',
  'A second sofa backs onto the kitchen island and faces the living room, making a cosy seating group. The walkway to the kitchen and stair runs between the two sofas.'])
R('landing1', 1, 'First-floor stair landing', 8.55, FOOT_E, LANE[0], S1, [9.05, 5.35, Y[1]], ['The next flight up starts here, at the back of the kitchen.'], 'Landing')
R('kitchen', 1, 'Kitchen', 8.0, E1, N1, S1, [9.9, 3.9, Y[1]], [
  'The kitchen is now about 2.5 times bigger and sits in the south-east (Agni corner), the Vastu-preferred spot. The hob is on the east wall, so the cook faces east.',
  'The island runs parallel to the counter: a slim 1.60 × 0.60 m island holding the kitchen sink, with the tap on the kitchen side. A sofa backs onto its living-room side. The aisle to the counter is 1.06 m, so the sink-to-hob triangle is a single step.',
  'The counter is now sink-free: one long run for prep and cooking. The window at its north end stays clear for light and fumes.',
  'For fumes, the chimney ducts straight out through the east wall, and a 1.2 m window beside it opens for cross-ventilation with the north window.',
  'Storage: overheads and a loft on the east wall, a tall pull-out pantry and the fridge on the south wall, and island cupboards. The north wall is now left open, with just the window.'])

R('lounge', 2, 'Family lounge', 1.05, 4.1, 2.565, S1, [2.35, 4.5, Y[2]], [
  'A family lounge where everyone can spend time together. The second-floor balcony is now enclosed: steel-framed glass fills both arches above a 0.45 m sill, and the glass opens for breeze.',
  'It joins the front of the floor, so the lounge is about 12 m², including a reading nook in the north corner. You step into it straight off the stair: turn right and you are in.',
  'It has an L-shaped sofa along the ensuite and master walls, a coffee table, a built-in window seat under the south arch, and no TV. It is a place to talk, read and watch the evening sky.',
  'The west glass gets afternoon sun. Use low-e glass and fit blinds or exterior bamboo chiks inside the arches.'], 'Family lounge')
R('nook', 2, 'Reading nook', 1.05, 2.4, N1, 2.565, [1.9, 2.35, Y[2]], ['The north corner of the enclosed balcony: an armchair and an indoor planter under the glazed arch.'], 'Nook')
R('ensuite', 2, 'Master ensuite', 2.55, 4.1, N1, 2.45, [3.5, 2.1, Y[2]], ['A north-west ensuite (Vastu-friendly for toilets): shower, WC and basin. Its door now opens from the bedroom side, with a high obscure window and an exhaust duct.'], 'Ensuite')
R('master', 2, 'Master bedroom', 4.215, 7.53, N1, 3.735, [4.5, 2.4, Y[2]], [
  'The master is now about 9.3 m², against 11.5 m² before. It gave its front corner to the family lounge, and its door opens off the hall.',
  'The queen bed has its head to the south. There is a 1.67 m wardrobe with a loft, a north window, and the ensuite through a pocket door.',
  'Vastu note: the master now sits nearer the north-centre, which is weaker than the west. The bed still faces correctly.'], 'Master')
R('hall2', 2, 'Upper hall', 4.1, FOOT_E, 3.85, S1, [5.0, 4.3, Y[2]], ['From the lounge the hall runs along the stairwell to bedroom 2 and to the roof stair at the back.'], 'Hall')
R('bed2', 2, 'Bedroom 2', 7.645, E1, N1, 3.735, [8.3, 3.2, Y[2]], [
  'A queen bed with its head to the east, a 1.6 m wardrobe and its own ensuite.',
  'It sits in the north-east, which Vastu prefers for children or study rather than for the head of the house.'], 'Bedroom 2')
R('bath2', 2, 'Bedroom 2 ensuite', FOOT_E + 0.115, E1, 3.85, S1, [10.2, 4.85, Y[2]], ['WC, basin and shower, in the south-east, a Vastu compromise noted in the report. Its exhaust duct runs to the roof.'], 'Ensuite')

R('roof', 3, 'Roof garden', 1.13, 7.665, N1, S1, [3.0, 4.3, Y[3]], [
  'The stair lands at the front inside a small cabin. Turn right onto the garden: raised planters, a lawn under a timber pergola, a bench and a low table.',
  'The water tank sits on the cabin in the south-west, the heavy corner, as Vastu advises. The north-east of the roof is kept light: only solar panels and drying lines.'], 'Roof garden')
R('roofrear', 3, 'Drying deck', 7.665, E1, N1, S1, [9.9, 3.0, Y[3]], ['Drying lines sit in full sun beside raised solar panels.'], 'Drying deck')

tour = ['road', 'front', 'passage', 'carbay', 'foyer', 'stairs', 'hall1', 'balc1', 'powder', 'study', 'living', 'kitchen', 'pooja',
        'landing1', 'lounge', 'nook', 'master', 'ensuite', 'hall2', 'bed2', 'bath2', 'roof', 'roofrear']

plan = dict(version='B6 · 18 Oct 2026', levels=Y, ceiling=CL, ground=G,
            plot=dict(depth=12.192, width=6.096), setbacks=dict(front=0.9, rear=0.702, north=0.7, south=0),
            footprint=dict(x1=W0, x2=E0, z1=N0, z2=S0),
            bounds=dict(x1=-6, x2=12.19, z1=-1.5, z2=7.6),
            start=dict(x=-2.4, z=4.2, yaw=-1.5708),
            neighbours=[dict(x1=0.6, x2=12.6, z1=-3.2, z2=-1.0, h=9.6), dict(x1=0.6, x2=12.6, z1=7.1, z2=9.3, h=6.6), dict(x1=13.2, x2=16, z1=-3.2, z2=9.3, h=9.6)],
            walkFence=[dict(x1=0, x2=12.6, z1=-1.6, z2=-0.15), dict(x1=0, x2=12.6, z1=6.246, z2=7.7)],
            spirals=[], stairLane=dict(x1=STOP, x2=SFOOT, z1=LANE[0], z2=LANE[1], hole=HOLE_E), columns=columns,
            walls=walls, decks=decks, slabs=slabs, furn=furn, finishes=finishes, rooms=rooms, tour=tour)
json.dump(plan, open('src/plan.json', 'w'), indent=1)
print(len(walls), 'walls', len(decks), 'decks', len(furn), 'furn', len(rooms), 'rooms', 'rise', RISE, 'top', STOP)
