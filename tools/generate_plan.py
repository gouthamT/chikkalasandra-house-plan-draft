"""Generate plan.json (B7: front U-turn stair). Stilt + 2 + roof garden.
B7: the stair is a stacked dog-leg (U-turn) at the front south-west corner on every floor. You arrive at the front and
carry on up from the same landing. Bedroom 2 moves to the first floor (north-east); the second floor is the family
lounge plus a large master suite. Coordinates in metres. x: west->east from the road boundary. z: north->south from
the north boundary. y: height.
"""
import json

Y = [0.0, 3.15, 6.30, 9.45]
CL = 3.0
G = -0.15
N0, N1, S1, S0 = 0.7, 0.93, 5.866, 6.096
W0, E1, E0 = 0.9, 11.26, 11.49
NR = 17
RISE = round(3.15 / NR, 5)
TREAD = 0.25
LN = (3.75, 4.75)            # north lane: flight A, rises east
SP = (4.75, 4.866)           # central RCC spine wall
LS = (4.866, 5.866)          # south lane: flight B, rises west
AX0 = 3.8                    # foot of flight A (west edge of the stair), landing is west of here
MX0 = AX0 + 8 * TREAD        # 5.80: half landing starts
MX1 = MX0 + 1.0              # 6.80: half landing ends at the core east wall
BX0 = MX0 - 7 * TREAD        # 4.05: top of flight B
CE = (6.8, 6.915)            # core east wall
GZ = (3.70, 3.75)            # open (north) side of flight A: balusters
CAB_H = 2.4
CABN = (3.635, 3.75)         # roof cabin north wall

walls, decks, slabs, furn, finishes, rooms, columns = [], [], [], [], [], [], []
balusters, rails = [], []

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

r3 = lambda v: round(v, 3)

# ---------------- structure ----------------
for x in (0.9, 4.6, 8.25, 11.11):
    columns.append(dict(x1=x, x2=r3(x + 0.38), z1=N0, z2=N1))
    columns.append(dict(x1=x, x2=r3(x + 0.38), z1=S1, z2=S0))

# ---------------- decks: slabs with the stairwell left open ----------------
decks.append(dict(id='stilt', x1=W0, x2=E0, z1=N0, z2=S0, y=Y[0], t=0.15, kind='slab'))
for lv in (1, 2, 3):
    for i, (x1, x2, z1, z2) in enumerate([(W0, AX0, N0, S0), (AX0, BX0, LS[0], S0), (AX0, MX1, N0, LN[0]), (BX0, MX1, S1, S0), (MX1, E0, N0, S0)]):
        decks.append(dict(id=f'slab{lv}{i}', x1=x1, x2=x2, z1=z1, z2=z2, y=Y[lv], t=0.15, kind='slab'))

# ---------------- the U-turn stair, repeated on every floor ----------------
for f in range(3):
    b = Y[f]
    A = []
    for i in range(1, 9):
        d = dict(id=f's{f}A{i}', x1=r3(AX0 + (i - 1) * TREAD), x2=r3(AX0 + i * TREAD), z1=LN[0], z2=LN[1], y=r3(b + i * RISE), t=0.3, kind='step')
        decks.append(d); A.append(d)
    M = dict(id=f's{f}M', x1=MX0, x2=MX1, z1=LN[0], z2=LS[1], y=r3(b + 9 * RISE), t=0.2, kind='step'); decks.append(M)
    B = []
    for j in range(1, 8):
        d = dict(id=f's{f}B{j}', x1=r3(MX0 - j * TREAD), x2=r3(MX0 - (j - 1) * TREAD), z1=LS[0], z2=LS[1], y=r3(b + (9 + j) * RISE), t=0.3, kind='step')
        decks.append(d); B.append(d)
    # open side of flight A + half landing: a baluster screen from the floor of the room beside it up to handrail height
    if f >= 1:
        for k, d in enumerate(A + [M]):
            W(f'G{f}{k}', f, 'x', d['x1'], d['x2'], GZ[0], GZ[1], 'sguard', Y[f], r3(d['y'] + 0.95))
            balusters.append(dict(x1=d['x1'], x2=d['x2'], z=sum(GZ) / 2, y0=Y[f], y1=r3(d['y'] + 0.9)))
    mid = lambda d: (d['x1'] + d['x2']) / 2
    hy = lambda d: r3(d['y'] + 0.9)
    my = hy(M)
    # outer handrail: along A (north), round the half landing, back along B on the south wall
    rails.append([[mid(d), hy(d), 3.77] for d in A] + [[MX0 + 0.1, my, 3.77], [MX1 - 0.04, my, 3.77], [MX1 - 0.04, my, 5.83]] +
                 [[MX0 - 0.02, my, 5.83]] + [[mid(d), hy(d), 5.83] for d in B])
    # inner handrails on both faces of the spine wall
    rails.append([[mid(d), hy(d), 4.72] for d in A] + [[MX0 + 0.12, my, 4.72]])
    rails.append([[MX0 + 0.12, my, 4.895]] + [[mid(d), hy(d), 4.895] for d in B])

for x1, x2, gl in ((2.4, AX0, False), (AX0, CE[0], True), (CE[0], CE[1], False)):
    slabs.append(dict(x1=x1, x2=x2, z1=CABN[0], z2=S0, y=Y[3] + CAB_H + 0.15, t=0.15, glass=gl))

# ---------------- compound + gates ----------------
W('C1', -1, 'z', -0.15, 0, -0.15, 6.246, 'compound', G, 2.7, [
    dict(a=0.15, b=3.35, type='gate', closed=True, label='Car gate G1 (sliding, vertical timber battens)', rel_h=2.3),
    dict(a=3.6, b=4.74, type='gate', closed=False, rel_h=2.45, batten=True, label='Entrance gate G2: 1.14 m double door, vertical timber battens to match the car gate')])
W('C2', -1, 'x', 0, 12.342, -0.15, 0, 'compound', G, 1.8)
W('C3', -1, 'z', 12.192, 12.342, 0, 6.246, 'compound', G, 1.8)
W('C4', -1, 'x', 0, W0, S0, 6.246, 'compound', G, 2.7)
W('C5', -1, 'x', E0, 12.192, S0, 6.246, 'compound', G, 1.8)

# ---------------- stair core walls, continuous through every floor ----------------
W('CORE', -1, 'x', AX0, MX0, SP[0], SP[1], 'int', 0, Y[3] + 1.0)                  # spine wall between the two flights
W('CORE2', -1, 'z', CE[0], CE[1], 3.6, S1, 'int', 0, Y[3] + CAB_H)               # east wall of the stair core

# ---------------- stilt ----------------
W('S0s', 0, 'x', W0, E0, S1, S0)
W('S0md', 0, 'z', 2.4, 2.55, 3.6, S1, 'int', open=[dict(a=3.68, b=4.74, type='door', hinge='a', side=1, main=True, head=2.4,
    label='Main door D1: 1.06 × 2.40 m, rectangular, vertical timber battens to match the car gate')])
W('S0sw', 0, 'x', 2.55, CE[0], 3.6, 3.65, 'screen')       # steel-framed glass screen: the stair stays locked but full of light
W('S0fn', 0, 'x', 9.8, E1, 3.485, 3.6, 'int', open=[dict(a=10.2, b=10.9, type='door', hinge='a', side=1, label='Store door (from car porch)')])
W('S0fe', 0, 'z', 9.8, 9.915, 3.6, S1, 'int')
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
W('L1e', 1, 'z', E1, E0, N1, S1, open=[
    dict(a=1.0, b=1.5, type='window', sill=1.0, head=2.1, label='Bedroom 2 side window (east)'),
    dict(a=3.95, b=4.75, type='window', sill=1.05, head=2.1, label='Kitchen window over the counter (east, for fumes and light)')])
W('L1n', 1, 'x', 1.05, E0, N0, N1, open=[
    dict(a=2.85, b=3.35, type='window', sill=1.5, head=2.1, label='Bathroom high window (north)'),
    dict(a=4.5, b=4.95, type='window', sill=0.9, head=2.4, label='Living window left of the TV (north)'),
    dict(a=6.15, b=6.6, type='window', sill=0.9, head=2.4, label='Living window right of the TV (north)'),
    dict(a=6.95, b=7.45, type='window', sill=0.9, head=2.4, label='Pooja corner window (north)'),
    dict(a=9.9, b=10.7, type='window', sill=0.9, head=2.4, label='Bedroom 2 window (north)')])
W('L1g', 1, 'z', 2.4, 2.55, N1, S1, 'glaze', open=[
    dict(a=1.0, b=2.1, type='window', sill=1.2, head=2.1, label='Bathroom window (obscure glass, to loggia)'),
    dict(a=2.45, b=3.65, type='door', slide=True, label='Steel-framed sliding door, hall to loggia'),
    dict(a=3.95, b=5.7, type='window', sill=0.45, head=2.6, label='Landing window to loggia')])
W('L1ps', 1, 'x', 2.55, 4.315, 2.2, 2.315, 'int', open=[dict(a=2.75, b=3.45, type='door', hinge='b', side=-1, label='Common bathroom door')])
W('L1pe', 1, 'z', 4.2, 4.315, N1, 2.2, 'int')
W('L1bw', 1, 'z', 8.0, 8.115, N1, 3.815, 'int', open=[dict(a=2.95, b=3.65, type='door', hinge='b', side=1, label='Bedroom 2 door')])
W('L1bs', 1, 'x', 8.115, E1, 3.7, 3.815, 'int')

# second floor
W('L2e', 2, 'z', E1, E0, N1, S1, open=[dict(a=3.3, b=4.1, type='window', sill=0.9, head=2.1, label='Master bedroom window (east)')])
W('L2n', 2, 'x', 1.05, E0, N0, N1, open=[
    dict(a=2.7, b=4.3, type='window', sill=0.9, head=2.4, label='Family lounge window (north, over the sofa)'),
    dict(a=5.0, b=5.6, type='window', sill=1.8, head=2.3, label='Ensuite high window (obscure glass)'),
    dict(a=7.6, b=9.0, type='window', sill=0.9, head=2.4, label='Master bedroom window (north)'),
    dict(a=9.8, b=10.6, type='window', sill=0.9, head=2.4, label='Master bedroom window (north-east)')])
W('L2ew', 2, 'z', 4.6, 4.715, N1, 2.515, 'int')
W('L2es', 2, 'x', 4.715, CE[0], 2.4, 2.515, 'int')
W('L2mw', 2, 'z', CE[0], CE[1], N1, 3.6, 'int', open=[
    dict(a=1.6, b=2.3, type='door', slide=True, label='Master ensuite door (pocket slider)'),
    dict(a=2.75, b=3.55, type='door', slide=True, label='Master bedroom door (pocket slider, from the hall)')])

# roof
R3 = Y[3]
W('Rn', 3, 'x', W0, E0, N0, N1, 'parapet', R3, R3 + 1.0)
W('Rs1', 3, 'x', W0, 2.4, S1, S0, 'parapet', R3, R3 + 1.0)
W('Rs2', 3, 'x', CE[1], E0, S1, S0, 'parapet', R3, R3 + 1.0)
W('Rw', 3, 'z', W0, 1.13, N1, S1, 'parapet', R3, R3 + 1.0)
W('Re', 3, 'z', E1, E0, N1, S1, 'parapet', R3, R3 + 1.0)
W('Rcs', 3, 'x', 2.4, CE[0], S1, S0, 'ext', R3, R3 + CAB_H)
W('Rcn', 3, 'x', 2.4, CE[0], CABN[0], CABN[1], 'ext', R3, R3 + CAB_H, [dict(a=2.65, b=3.45, type='door', hinge='a', side=-1, label='Door to roof garden')])
W('Rcw', 3, 'z', 2.4, 2.55, CABN[1], S1, 'ext', R3, R3 + CAB_H, [dict(a=4.3, b=5.3, type='window', sill=1.0, head=2.1, label='Stair cabin window (west)')])
W('Rrl', 3, 'z', AX0 - 0.05, AX0, LN[0], SP[0], 'rail', R3, R3 + 1.0)      # guard where the top flight drops away

# ---------------- finishes ----------------
FIN(0, W0, 2.4, 3.6, S1, 'checker'); FIN(0, 2.55, CE[0], 3.65, S1, 'checker')
FIN(0, W0, E1, N1, 3.6, 'concrete'); FIN(0, CE[1], 9.8, 3.6, S1, 'concrete'); FIN(0, 9.915, E1, 3.6, S1, 'concrete')
for lv in (1, 2):
    FIN(lv, 1.05, 2.4, N1, S1, 'terracotta')
FIN(1, 2.55, 4.2, N1, 2.2, 'wet'); FIN(1, 3.52, 4.2, N1, 1.6, 'wetdark', 0.005)
FIN(1, 2.55, 8.0, 2.315, GZ[0], 'stoneTile'); FIN(1, 4.315, 8.0, N1, 2.315, 'stoneTile'); FIN(1, 2.55, AX0, GZ[0], S1, 'stoneTile'); FIN(1, AX0, BX0, LS[0], S1, 'stoneTile')
FIN(1, CE[0], 8.0, GZ[0], 3.815, 'stoneTile'); FIN(1, CE[1], E1, 3.815, S1, 'stoneTile'); FIN(1, 8.115, E1, N1, 3.7, 'oxide')
FIN(1, 4.9, 6.2, 1.45, 2.95, 'rug', 0.006)
FIN(2, 2.55, 4.6, N1, GZ[0], 'oxide'); FIN(2, 4.6, CE[0], 2.515, GZ[0], 'stoneTile'); FIN(2, 2.55, AX0, GZ[0], S1, 'stoneTile'); FIN(2, AX0, BX0, LS[0], S1, 'stoneTile')
FIN(2, 4.715, CE[0], N1, 2.4, 'wet'); FIN(2, 4.715, 5.6, N1, 1.9, 'wetdark', 0.005); FIN(2, CE[1], E1, N1, S1, 'oxide')
FIN(2, 2.75, 3.95, 1.85, 2.75, 'rug', 0.006)
FIN(3, 1.13, E1, N1, CABN[0], 'terracotta'); FIN(3, CE[1], E1, CABN[0], S1, 'terracotta'); FIN(3, 1.13, 2.4, CABN[0], S1, 'terracotta')
FIN(3, 2.55, AX0, CABN[1], S1, 'stoneTile'); FIN(3, AX0, BX0, LS[0], S1, 'stoneTile'); FIN(3, 1.9, 4.85, 1.75, 3.4, 'lawn', 0.01)

# ---------------- furniture: stilt ----------------
F('car', 0, 'Car (sub-4 m hatch/sedan, 4.00 × 1.75 m)', 1.3, 5.3, 0.95, 2.7, 1.5, 'car', shape='car')
F('bike', 0, 'Motorcycle (2.00 × 0.70 m)', 7.3, 9.3, 4.4, 5.1, 1.1, 'black', shape='bike')
F('sump', 0, 'Underground sump hatch (north-east)', 10.2, 11.0, 1.1, 1.9, 0.02, 'steel', solid=False)
F('scr1', 0, 'Planter + timber batten screen', 1.3, 2.4, 3.45, 3.6, 2.4, 'walnut', shape='screen')
F('pplant', 0, 'Entry planter (shade plants)', 1.5, 2.4, 5.45, S1, 0.45, 'render', shape='planter')
F('olive', 0, 'Potted olive tree', 0.95, 1.4, 4.9, 5.35, 0.5, 'terracotta', shape='pot')
F('shoe', 0, 'Shoe cabinet + bench', 2.55, 2.9, 4.95, S1, 0.9, 'walnut')
F('wmG', 0, 'Front-load washing machine (end of the laundry nook)', 5.2, 5.8, LS[0], 5.466, 0.85, 'white')
F('usG', 0, 'Utility sink', 5.3, 5.8, 5.466, S1, 0.85, 'render')
F('lshelf', 0, 'Detergent shelves on the spine wall', 4.3, 5.1, LS[0], 5.08, 0.4, 'walnut', y=1.3, solid=False, shape='shelves')
F('lbask', 0, 'Laundry basket', 4.4, 4.8, 5.45, 5.8, 0.5, 'cane', solid=False)
F('ucup', 0, 'Cupboard under the half landing', 5.85, CE[0], GZ[0], S1, 1.3, 'walnut')
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
F('pwc', 1, 'WC', 2.55, 2.95, 1.0, 1.65, 0.42, 'ceramic', shape='wc')
F('pbas', 1, 'Basin', 3.0, 3.4, N1, 1.38, 0.85, 'ceramic')
F('pgl', 1, 'Shower glass', 3.5, 3.52, N1, 1.6, 2.0, 'glass')
F('tvc', 1, 'TV console (walnut, fluted)', 5.0, 6.1, N1, 1.28, 0.5, 'walnut')
F('tv', 1, 'TV (45")', 5.05, 6.05, N1, 0.98, 0.6, 'black', y=1.0, solid=False)
F('sofa', 1, 'Sofa 1.6 m facing the TV wall', 4.75, 6.35, 2.2, 3.05, 0.8, 'linen', shape='sofa', back='z2')
F('ctab', 1, 'Coffee table', 5.2, 5.9, 1.6, 1.95, 0.4, 'walnut')
F('pooja', 1, 'Open mandir unit (idols facing west)', 7.5, 8.0, 1.0, 2.0, 1.0, 'walnut', shape='pooja')
F('run', 1, 'Cooking run on the east wall (cook faces east)', 10.66, E1, 3.815, S1, 0.9, 'walnut', shape='counterE', hob=[4.95, 5.55])
F('hood', 1, 'Chimney hood ducted out through the east wall', 10.76, E1, 4.95, 5.55, 0.55, 'steel', y=1.6, solid=False)
F('overE', 1, 'Overhead cabinets', 10.91, E1, 4.8, S1, 0.75, 'white', y=2.15, solid=False, shape='overheadE')
F('loftE', 1, 'Loft storage over the window', 10.76, E1, 3.815, 4.75, 0.7, 'white', y=2.2, solid=False)
F('island', 1, 'Slim island with the kitchen sink, parallel to the counter: 1.00 × 0.60 m', 9.0, 9.6, 4.05, 5.05, 0.9, 'quartz', shape='islandZ', over=0)
F('fridge', 1, 'Refrigerator (double door)', CE[1], 7.615, 5.166, S1, 1.85, 'steel')
F('pantry', 1, 'Tall pull-out pantry', 7.7, 8.65, 5.266, S1, 2.2, 'white', shape='tall')
F('wd2', 1, 'Wardrobe 1.60 m + loft (0.55 m deep)', 8.115, 9.715, N1, 1.48, 2.6, 'sage', shape='wardrobe')
F('bed2', 1, 'Queen bed 1.52 × 2.03 m (head to the east)', 9.23, E1, 2.1, 3.62, 0.55, 'linen', shape='bed', head='x2')
F('bs2a', 1, 'Bedside', 10.81, E1, 1.6, 2.05, 0.5, 'walnut')

# ---------------- second floor ----------------
F('bp2a', 2, 'Indoor planter under the arch', 1.05, 1.4, 1.2, 3.1, 0.45, 'render', shape='planter')
F('seat', 2, 'Built-in window seat under the arch', 1.05, 1.6, 4.2, 5.6, 0.45, 'render', shape='bench')
F('arm', 2, 'Reading armchair', 1.55, 2.2, 1.35, 2.0, 0.8, 'cane', shape='chair', back='x1')
F('lsofaA', 2, 'L-shaped sofa (long side, under the north window)', 2.6, 4.45, N1, 1.78, 0.8, 'linen', shape='sofa', back='z1')
F('lsofaB', 2, 'L-shaped sofa (return)', 3.6, 4.45, 1.78, 2.45, 0.8, 'linen', shape='sofa', back='x2', arms='end')
F('lctab', 2, 'Coffee table', 2.8, 3.4, 2.0, 2.5, 0.4, 'walnut')
F('eswc', 2, 'WC', 5.75, 6.4, 0.95, 1.35, 0.42, 'ceramic', shape='wc')
F('esbas', 2, 'Basin', 5.75, 6.2, 2.0, 2.4, 0.85, 'ceramic')
F('esgl', 2, 'Shower glass', 5.6, 5.62, N1, 1.9, 2.0, 'glass')
F('mbed', 2, 'King bed 1.83 × 2.03 m (head to the east)', 9.23, E1, 1.3, 3.13, 0.55, 'linen', shape='bed', head='x2')
F('mbs1', 2, 'Bedside', 10.81, E1, N1, 1.25, 0.5, 'walnut')
F('mbs2', 2, 'Bedside', 10.81, E1, 3.18, 3.63, 0.5, 'walnut')
F('marm', 2, 'Armchair', 7.6, 8.25, 1.0, 1.65, 0.8, 'cane', shape='chair', back='x1')
F('mdesk', 2, 'Writing desk', CE[1], 7.5, 3.9, 5.1, 0.75, 'walnut')
F('mwd', 2, 'Wardrobe wall 2.60 m + loft (sliding doors)', 7.6, 10.2, 5.266, S1, 2.9, 'walnut', shape='wardrobe', face='z1')
F('mdress', 2, 'Dressing table', 10.45, E1, 5.4, S1, 0.75, 'walnut')

# ---------------- roof ----------------
F('rpn', 3, 'Raised planter (herbs, curry leaf)', 1.13, 5.6, N1, 1.43, 0.5, 'render', shape='planter')
F('rpn2', 3, 'Raised planter (vegetables)', 5.7, 7.6, N1, 1.43, 0.5, 'render', shape='planter')
F('rpw', 3, 'Raised planter (bougainvillea)', 1.13, 1.63, 3.9, 5.8, 0.5, 'render', shape='planter')
F('rps', 3, 'Raised planter (ixora, jasmine)', 7.8, E1, 5.366, S1, 0.5, 'render', shape='planter')
for i, (x, z) in enumerate([(1.6, 1.6), (4.88, 1.6), (1.6, 3.33), (4.88, 3.33)]):
    F(f'pp{i}', 3, 'Pergola post', x, r3(x + 0.12), z, r3(z + 0.12), 2.6, 'walnut')
F('perg', 3, 'Timber pergola', 1.6, 5.0, 1.6, 3.45, 0.2, 'walnut', y=2.6, shape='pergola', solid=False)
F('rbench', 3, 'Built-in bench', 1.75, 2.25, 1.85, 3.2, 0.45, 'render', shape='bench')
F('rtab', 3, 'Low table', 2.8, 3.6, 2.2, 2.9, 0.45, 'walnut')
F('solar', 3, 'Solar PV on raised frame', 8.6, 11.1, 1.1, 3.6, 0.08, 'solar', y=2.4, solid=False, shape='solar')
F('tank', 3, 'Overhead water tank 2,000 L (south-west, on the stair cabin)', 2.5, 3.72, 4.7, 5.8, 1.3, 'black', y=CAB_H + 0.3, solid=False, shape='tank')
F('lines', 3, 'Drying lines', 7.4, 10.6, 4.1, 5.2, 0.02, 'black', y=1.8, solid=False, shape='lines')

# ---------------- rooms ----------------
STAIR_NOTES = [
  'One U-turn (dog-leg) stair, stacked in the same spot on every floor at the front south-west corner. You arrive at the front and the next flight starts from the same landing, so you never walk through a floor to go up.',
  'Each storey has 17 risers of about 185 mm (an odd number, as Vastu prefers) and 250 mm treads: 9 risers east along the north lane, a 1.0 m half landing where you turn, then 8 risers back west along the south wall.',
  'It climbs east, turns south and comes back west: clockwise in plan, in the south-west, the arrangement Vastu prefers for stairs.',
  'Flights are 1.0 m wide. The room side is an open screen of slim black-steel balusters (gaps under 100 mm) from the floor up to a timber handrail, so light passes through. There are handrails on both sides of every flight, and a glass skylight over the stairwell on the roof.',
  'Structure: a 115 mm RCC spine wall runs up the middle and an RCC wall closes the east side. Each flight is a waist slab from the floor beam to the half-landing beam. The core also stiffens the frame against sway.']
R('road', -1, 'Road (west)', -9, 0, -6, 12, [-2.4, 4.2, G], [
  'You are on the road, looking east: white render, a timber-batten car gate and a batten gate for people.',
  'The pedestrian gate and the main door both sit in the 3rd–4th of the nine west-side padas, counted from the south-west (Sugriva and Pushpadanta), the ones Vastu recommends for a west-facing entrance.'])
R('front', 0, 'Front garden & gates', 0, W0, 0, S0, [0.45, 4.2, G], [
  'The 0.9 m front setback stays unpaved: a planted bed with a frangipani and stepping stones from the gate.'], 'Front garden')
R('laundry', 0, 'Laundry nook', BX0, MX0, LS[0], S1, [4.4, 5.2, 0], [
  'The laundry sits under the upper flight, inside the locked foyer: a front-load washer and a utility sink at the end of the nook, a basket and shelves on the spine wall.',
  'There is 2.2–2.9 m of headroom where you stand, and 1.6–1.8 m over the machine. A cupboard under the half landing holds the ironing board and cleaning things.',
  'Clothes still dry on the roof deck. Under-stair use at stilt level should be confirmed with the authority, as stilts are meant for parking.'], 'Laundry', early=True, ymax=0.5)
R('stairs', -1, 'Stair', AX0, CE[0], LN[0], S1, [3.93, 4.25, round(RISE, 3)], STAIR_NOTES, early=True)
R('foyer', 0, 'Entrance foyer', 2.55, AX0, 3.65, S1, [3.1, 4.3, 0], [
  'The main door is 1.06 × 2.40 m, rectangular, with the same vertical timber battens as the car gate. It faces west and now sits right at the front, 2.4 m from the gate.',
  'Step in and the stair starts straight ahead: turn left onto the first flight. The door locks the stair and the whole house above. A glass screen lets the car porch light in without opening the stair to it.',
  'A shoe cabinet and bench stand beside the door, and the laundry nook opens off the foyer.'])
R('passage', 0, 'Entry porch', W0, 2.4, 3.6, S1, [1.6, 4.2, 0], [
  'A short planted porch under the first-floor loggia, with a black-and-white checkerboard floor, leads from the gate to the main door.'], 'Porch')
R('carbay', 0, 'Car porch (stilt)', W0, E1, N0, 3.6, [6.0, 2.6, 0], [
  'Your car parks in the north-west, which Vastu prefers for vehicles. Moving the stair to the front frees the whole back half of the stilt.',
  'The underground sump sits under the north-east end, where Vastu wants water storage below ground.'], 'Car porch')
R('bikebay', 0, 'Bike bay & workshop', CE[1], 9.8, 3.6, S1, [7.4, 4.0, 0], [
  'The space behind the stair is now a covered bay for the motorcycle, bicycles and a workbench, opening straight off the car porch.'], 'Bike bay')
R('store', 0, 'Store', 9.915, E1, 3.6, S1, [10.55, 4.5, 0], ['A store opening off the car porch for tools, pump controls and garden things.'])
R('sidepath', -1, 'North side setback', W0, 12.192, 0, N0, [6.0, 0.35, G], ['Kept open and unpaved. Vastu favours more openness to the north and east, and this strip lets the north windows breathe.'])
R('rear', -1, 'Rear setback', E0, 12.192, N0, S0, [11.85, 2.5, G], ['A 0.7 m rear setback for the rainwater recharge pit and the kitchen chimney outlet.'])

R('balc1', 1, 'First-floor loggia', 1.05, 2.4, N1, S1, [1.75, 2.4, Y[1]], ['A 1.35 m deep loggia behind two arches, reached from the hall by a 1.2 m steel-framed slider. It shades the west glass.'], 'Loggia')
R('powder', 1, 'Common bathroom', 2.55, 4.2, N1, 2.2, [3.1, 1.9, Y[1]], [
  'A full bathroom in the north-west: WC, basin and a walk-in shower. North-west is a Vastu-preferred spot for toilets.',
  'It now also serves bedroom 2 on this floor. It is ventilated through an obscure-glass window onto the loggia and a high north window.'], 'Bath')
R('hall1', 1, 'First-floor hall & landing', 2.55, AX0, 2.315, S1, [3.15, 4.3, Y[1]], [
  'You come up the last flight facing the front, and the floor opens to your right: turn right and you are in the hall.',
  'The next flight up starts from this same landing. A 1.2 m slider opens to the loggia, the bathroom is to the left, and ahead the living room, pooja corner and kitchen run in one open space.'], 'Hall')
R('living', 1, 'Living room', 4.315, CE[0], N1, GZ[0], [4.5, 3.35, Y[1]], [
  'The living room sits in the north of the floor, which Vastu likes for living spaces. The TV is on the north wall between two windows (window, TV, window).',
  'The sofa faces the TV. Behind it a 0.65 m walk runs along the stair screen to the kitchen and bedroom 2, so nobody crosses in front of the TV.',
  'The centre of the plot (Brahmasthan) stays open floor: no walls, columns or plumbing there.'])
R('pooja', 1, 'Pooja corner', CE[0], 8.0, N1, 3.815, [7.0, 1.5, Y[1]], [
  'An open mandir unit stands against the bedroom wall with the idols facing west, so you pray facing east. It sits in the north, with a north window beside it and open floor in front.',
  'No toilet is behind or above it, and the hob is well away.'], 'Pooja')
R('kitchen', 1, 'Kitchen', CE[1], E1, 3.815, S1, [8.0, 4.4, Y[1]], [
  'The kitchen stays in the south-east (Agni corner), the Vastu-preferred spot, with the hob on the east wall so the cook faces east.',
  'The sink is on a slim 1.0 × 0.6 m island parallel to the counter, with a 1.06 m aisle between them. The window over the counter opens for fumes, and the chimney ducts straight out through the east wall.',
  'The fridge and a tall pull-out pantry line the south wall, with overheads and a loft on the east wall.',
  'It is a little smaller than before (about 9.8 m²) because bedroom 2 took the north-east of this floor.'])
R('bed2', 1, 'Bedroom 2', 8.115, E1, N1, GZ[0], [8.6, 2.6, Y[1]], [
  'Bedroom 2 has moved down to the first floor, at the back in the north-east, so the stair never passes through anyone\'s room. You reach it past the pooja corner.',
  'A queen bed with its head to the east, a 1.6 m wardrobe with a loft, and windows to the north and east. Vastu suits the north-east for children or study.',
  'It shares the common bathroom at the front of this floor.'], 'Bedroom 2')

R('ensuite', 2, 'Master ensuite', 4.715, CE[0], N1, 2.4, [6.45, 1.65, Y[2]], ['Shower, WC and basin, with a high obscure north window and an exhaust duct. It opens from the bedroom through a pocket slider.',
  'Vastu note: north-centre is a compromise for a toilet (the west and north-west are better, but the front now holds the lounge and stair).'], 'Ensuite')
R('master', 2, 'Master suite', CE[1], E1, N1, S1, [7.6, 2.6, Y[2]], [
  'The master now takes the whole back half of the floor, about 21 m²: a king bed with its head to the east, an armchair, a writing desk and a 2.6 m wardrobe wall with a dressing table.',
  'Windows face north and east for morning light. You enter from the hall by a pocket slider, and the ensuite is next door.',
  'Vastu note: the south-west, the ideal master corner, holds the stair. The bed faces correctly and the room is in the quieter rear of the house.'], 'Master')
R('lounge', 2, 'Family lounge', 1.05, 4.6, N1, GZ[0], [2.3, 3.2, Y[2]], [
  'A family lounge where everyone can spend time together, right at the top of the stair: turn right off the last step and you are in it.',
  'The second-floor balcony is enclosed: steel-framed glass fills both arches above a 0.45 m sill and opens for breeze. An L-shaped sofa sits under a new north window, with a reading chair and planter by the north arch.',
  'There is no TV. It is a place to talk, read and watch the evening sky. The west glass gets afternoon sun, so use low-e glass and blinds or bamboo chiks inside the arches.'], 'Family lounge')
R('nook', 2, 'Window-seat bay', 1.05, 2.55, GZ[0], S1, [2.0, 4.0, Y[2]], ['A built-in window seat under the south arch, beside the stair landing.'], 'Bay')
R('hall2', 2, 'Upper hall & landing', 2.55, CE[0], 2.515, S1, [3.15, 4.3, Y[2]], ['From the landing, the lounge is to your right and a short hall along the stair screen leads to the master suite. The roof flight starts from this same landing.'], 'Hall')

R('cabin', 3, 'Stair cabin', 2.55, AX0, CABN[1], S1, [3.15, 4.3, Y[3]], ['The stair arrives inside a small cabin with a west window and a glass skylight over the stairwell. Turn right and step out onto the garden.'], 'Cabin')
R('roof', 3, 'Roof garden', 1.13, CE[0], N1, S1, [3.2, 3.25, Y[3]], [
  'Raised planters, a lawn under a timber pergola, a bench and a low table, on the front half of the roof.',
  'The water tank sits on the stair cabin in the south-west, the heavy corner, as Vastu advises. The north-east of the roof is kept light: only solar panels and drying lines.'], 'Roof garden')
R('roofrear', 3, 'Drying deck', CE[1], E1, N1, S1, [9.9, 3.0, Y[3]], ['Drying lines sit in full sun beside raised solar panels.'], 'Drying deck')

tour = ['road', 'front', 'passage', 'carbay', 'bikebay', 'foyer', 'laundry', 'stairs', 'hall1', 'balc1', 'powder', 'living', 'pooja', 'kitchen', 'bed2',
        'hall2', 'lounge', 'nook', 'ensuite', 'master', 'cabin', 'roof', 'roofrear']

# plan arrows for the stair: (x, z) polyline going up from each floor
arrow = [[AX0 + 0.1, 4.25], [MX0 + 0.5, 4.25], [MX0 + 0.5, 5.37], [BX0 + 0.05, 5.37]]
stair = dict(balusters=balusters, rails=rails, arrow=arrow, up=[4.5, 4.12], dn=[4.6, 5.52], lamps=[[5.3, 2.7, 4.8], [5.3, 5.85, 4.8], [5.3, 9.0, 4.8], [5.3, 11.6, 4.8]])

plan = dict(version='B7 · 19 Oct 2026', levels=Y, ceiling=CL, ground=G,
            plot=dict(depth=12.192, width=6.096), setbacks=dict(front=0.9, rear=0.702, north=0.7, south=0),
            footprint=dict(x1=W0, x2=E0, z1=N0, z2=S0),
            bounds=dict(x1=-6, x2=12.19, z1=-1.5, z2=7.6),
            start=dict(x=-2.4, z=4.2, yaw=-1.5708),
            neighbours=[dict(x1=0.6, x2=12.6, z1=-3.2, z2=-1.0, h=9.6), dict(x1=0.6, x2=12.6, z1=7.1, z2=9.3, h=6.6), dict(x1=13.2, x2=16, z1=-3.2, z2=9.3, h=9.6)],
            walkFence=[dict(x1=0, x2=12.6, z1=-1.6, z2=-0.15), dict(x1=0, x2=12.6, z1=6.246, z2=7.7)],
            spirals=[], stairLane=dict(x1=AX0, x2=MX1, z1=LN[0], z2=LS[1]), stair=stair, columns=columns,
            walls=walls, decks=decks, slabs=slabs, furn=furn, finishes=finishes, rooms=rooms, tour=tour)
json.dump(plan, open('src/plan.json', 'w'), indent=1)
print(len(walls), 'walls', len(decks), 'decks', len(furn), 'furn', len(rooms), 'rooms', 'rise', RISE)
