"""Quick software preview of the exported OBJ (matplotlib): exterior view + one cutaway per floor."""
import sys, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

base = sys.argv[1]
kd, cur = {}, None
for line in open(base + '.mtl'):
    p = line.split()
    if not p: continue
    if p[0] == 'newmtl': cur = p[1]
    elif p[0] == 'Kd': kd[cur] = [float(t) for t in p[1:4]]
    elif p[0] == 'd': kd[cur] = kd[cur] + [float(p[1])]
V, F, obj, mat = [], [], None, None
for line in open(base + '.obj'):
    p = line.split()
    if not p: continue
    if p[0] == 'v': V.append([float(t) for t in p[1:4]])
    elif p[0] == 'o': obj = p[1]
    elif p[0] == 'usemtl': mat = p[1]
    elif p[0] == 'f': F.append(([int(t) - 1 for t in p[1:]], mat, obj))
V = np.array(V)
light = np.array([-0.5, 0.8, 0.35]); light /= np.linalg.norm(light)

def render(out, keep, elev, azim, xlim, ylim, zlim, title, size=(11, 7), cap=None):
    polys, cols, fl, fc = [], [], [], []
    for idx, m, o in F:
        pts = V[idx]
        if not keep(pts, o): continue
        if cap is not None:
            pts = pts.copy(); pts[:, 1] = np.minimum(pts[:, 1], cap)
            if np.ptp(pts[:, 0]) < 1e-6 and np.ptp(pts[:, 1]) < 1e-6 or np.ptp(pts[:, 2]) < 1e-6 and np.ptp(pts[:, 1]) < 1e-6: continue
        n = np.cross(pts[1] - pts[0], pts[2] - pts[1]); ln = np.linalg.norm(n)
        shade = 0.55 + 0.45 * abs(n @ light / ln) if ln > 0 else 0.8
        c = kd.get(m, [0.8, 0.8, 0.8, 1])
        a = c[3] if len(c) > 3 else 1
        flat = o.startswith(('floors_', 'slab_', 'site_')) and np.ptp(pts[:, 1]) < 1e-6
        (fl if flat else polys).append(pts[:, [0, 2, 1]]); (fc if flat else cols).append((*(np.clip(np.array(c[:3]) * shade, 0, 1)), 0.35 if a < 1 else 1))
    fig = plt.figure(figsize=size, dpi=110); ax = fig.add_subplot(111, projection='3d'); ax.computed_zorder = False
    ax.add_collection3d(Poly3DCollection(fl, facecolors=fc, edgecolors=(0, 0, 0, 0.08), linewidths=0.2, zorder=0))
    pc = Poly3DCollection(polys, facecolors=cols, edgecolors=(0, 0, 0, 0.12), linewidths=0.2, zorder=1); ax.add_collection3d(pc)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_zlim(*zlim); ax.set_box_aspect((xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0]))
    ax.view_init(elev=elev, azim=azim); ax.invert_yaxis(); ax.set_axis_off(); ax.set_title(title, fontsize=11)
    plt.tight_layout(); fig.savefig(out, facecolor='#f4f2ec'); plt.close(fig)

noctx = lambda pts, o: not o.startswith('site_neighbours')
render(base + '_exterior.png', lambda pts, o: noctx(pts, o) and pts[:, 0].min() > -3 and pts[:, 2].max() < 7.5, 18, -140, (-2, 12.5), (-0.5, 7), (-0.2, 12.5), 'Street view from the south-west (blockout)')
L = [0.0, 3.15, 6.30, 9.45]
for i, y in enumerate(L):
    cut = y + 1.6
    keep = lambda pts, o, y=y, cut=cut: not o.startswith('site') and pts[:, 1].min() < cut and pts[:, 1].min() >= y - 0.35 and not o.startswith('stair_cabin_roof') and not o.endswith(('_tv', '_hood', '_overE', '_loftE', '_perg', '_solar', '_lines', '_tank', '_shelf1'))
    render(base + f'_cutaway_{i}.png', keep, 55, -125, (0.6, 11.8), (0.4, 6.4), (y - 0.3, y + 2.5), ['Stilt', 'First floor', 'Second floor', 'Roof'][i] + ' cutaway (walls cut at 1.6 m)', cap=cut)
print('ok')
