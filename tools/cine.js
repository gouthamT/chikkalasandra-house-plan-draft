// Builds the cinematic camera route: a real walkable path (same collision rules as the walkthrough) between every tour stop.
// Run from the repo root after the generator: node tools/cine.js  (adds P.cine to plan.json)
const fs = require('fs');
const P = JSON.parse(fs.readFileSync('src/plan.json', 'utf8'));
const { buildSolids, floorAt, canStand, MAX_STEP } = require('../src/shared.js');
const S = buildSolids(P);
const G = 0.05, X0 = -4, X1 = 12.19, Z0 = -0.2, Z1 = 6.2;
const NX = Math.round((X1 - X0) / G), NZ = Math.round((Z1 - Z0) / G);
const cx = i => X0 + i * G, cz = k => Z0 + k * G;
const key = (i, k, f) => `${i},${k},${Math.round(f * 100)}`;
const DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];

// distance-to-obstacle penalty keeps the camera off walls and furniture
function clearance(x, z, f) { for (const r of [0.45, 0.38, 0.3]) if (canStand(P, S, x, z, f, r)) return r; return 0.22; }

function astar(a, b, r) {
  const si = Math.round((a[0] - X0) / G), sk = Math.round((a[1] - Z0) / G);
  const ti = Math.round((b[0] - X0) / G), tk = Math.round((b[1] - Z0) / G);
  const f0 = floorAt(P, cx(si), cz(sk), a[2]);
  const open = [[0, si, sk, f0]], g = new Map(), from = new Map();
  g.set(key(si, sk, f0), 0);
  const h = (i, k, f) => Math.hypot((i - ti) * G, (k - tk) * G) + Math.abs(f - b[2]) * 2.5;
  let n = 0;
  while (open.length) {
    // binary-heap-free: pop the min (open list stays small enough with a good heuristic)
    let bi = 0; for (let q = 1; q < open.length; q++) if (open[q][0] < open[bi][0]) bi = q;
    const [, i, k, f] = open[bi]; open[bi] = open[open.length - 1]; open.pop();
    if (Math.abs(i - ti) <= 1 && Math.abs(k - tk) <= 1 && Math.abs(f - b[2]) < 0.05) {
      const out = []; let c = key(i, k, f);
      while (c) { const [ii, kk, ff] = c.split(',').map(Number); out.push([cx(ii), ff / 100, cz(kk)]); c = from.get(c); }
      return out.reverse();
    }
    if (++n > 400000) break;
    const gc = g.get(key(i, k, f));
    for (const [di, dk] of DIRS) {
      const ni = i + di, nk = k + dk;
      if (ni < 0 || nk < 0 || ni >= NX || nk >= NZ) continue;
      const x = cx(ni), z = cz(nk);
      const nf = floorAt(P, x, z, f);
      if (nf - f > MAX_STEP + 1e-6 || f - nf > 0.5) continue;
      if (!canStand(P, S, x, z, f, r)) continue;
      if (di && dk && (!canStand(P, S, cx(i + di), cz(k), f, r) || !canStand(P, S, cx(i), cz(k + dk), f, r))) continue;
      const cl = clearance(x, z, nf);
      const step = Math.hypot(di, dk) * G * (1 + (0.45 - cl) * 6);
      const kk = key(ni, nk, nf), ng = gc + step;
      if (g.has(kk) && g.get(kk) <= ng) continue;
      g.set(kk, ng); from.set(kk, key(i, k, f)); open.push([ng + h(ni, nk, nf), ni, nk, nf]);
    }
  }
  return null;
}

const stops = P.tour.map(id => P.rooms.find(r => r.id === id));
let pts = [], marks = [];
for (let s = 0; s < stops.length; s++) {
  const r = stops[s];
  if (s === 0) { pts.push([r.spawn[0], r.spawn[2], r.spawn[1]]); marks.push({ i: 0, id: r.id }); continue; }
  const a = pts[pts.length - 1];
  const seg = astar([a[0], a[2], a[1]], [r.spawn[0], r.spawn[1], r.spawn[2]], 0.26) || astar([a[0], a[2], a[1]], [r.spawn[0], r.spawn[1], r.spawn[2]], 0.22);
  if (!seg) { console.error('no route to', r.id); process.exit(1); }
  pts.push(...seg.slice(1)); marks.push({ i: pts.length - 1, id: r.id });
}
// smooth (moving average) while pinning the stops, then thin to ~0.15 m spacing
const sm = pts.map((p, i) => {
  const w = 7; let sx = 0, sy = 0, sz = 0, n = 0;
  for (let j = Math.max(0, i - w); j <= Math.min(pts.length - 1, i + w); j++) { sx += pts[j][0]; sy += pts[j][1]; sz += pts[j][2]; n++; }
  return [sx / n, sy / n, sz / n];
});
for (const m of marks) sm[m.i] = pts[m.i];
const keep = new Set(marks.map(m => m.i)), out = [], map = {};
for (let i = 0; i < sm.length; i++) if (i % 3 === 0 || keep.has(i)) { if (keep.has(i)) map[i] = out.length; out.push(sm[i].map(v => +v.toFixed(3))); }
P.cine = { pts: out, stops: marks.map(m => ({ i: map[m.i], id: m.id })) };
fs.writeFileSync('src/plan.json', JSON.stringify(P, null, 1));
let len = 0; for (let i = 1; i < out.length; i++) len += Math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1], out[i][2] - out[i - 1][2]);
console.log('cine route', out.length, 'points,', len.toFixed(1), 'm,', P.cine.stops.length, 'stops');
