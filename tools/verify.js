// B2 verification: 3D reachability (stairs included), clearances, overlaps. Run: node verify.js
const P = require('../src/plan.json');
const { buildSolids, floorAt, canStand, roomAt, MAX_STEP } = require('../src/shared.js');
const S = buildSolids(P);
const G = 0.05, X0 = -4, X1 = 12.19, Z0 = -0.2, Z1 = 6.2;
const NX = Math.round((X1 - X0) / G), NZ = Math.round((Z1 - Z0) / G);
const key = (i, k, f) => `${i},${k},${Math.round(f * 100)}`;

function explore(r) {
  const seen = new Map();
  const si = Math.round((P.start.x - X0) / G), sk = Math.round((P.start.z - Z0) / G);
  const f0 = floorAt(P, P.start.x, P.start.z, P.ground);
  const q = [[si, sk, f0]]; seen.set(key(si, sk, f0), [si, sk, f0]);
  while (q.length) {
    const [i, k, f] = q.pop();
    for (const [di, dk] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const ni = i + di, nk = k + dk;
      if (ni < 0 || nk < 0 || ni >= NX || nk >= NZ) continue;
      const x = X0 + ni * G, z = Z0 + nk * G;
      const nf = floorAt(P, x, z, f);
      if (nf - f > MAX_STEP + 1e-6) continue;
      if (f - nf > 0.5) continue;                 // treat drops > 0.5 m as falls: never part of a valid route
      if (!canStand(P, S, x, z, f, r)) continue;
      const kk = key(ni, nk, nf);
      if (seen.has(kk)) continue;
      seen.set(kk, [ni, nk, nf]); q.push([ni, nk, nf]);
    }
  }
  return [...seen.values()];
}

function report(r) {
  const cells = explore(r), hit = {};
  for (const [i, k, f] of cells) { const room = roomAt(P, X0 + i * G, Z0 + k * G, f); if (room) hit[room.id] = (hit[room.id] || 0) + 1; }
  return { hit, cells };
}
const a = report(0.22), b = report(0.30);
console.log('Zone reachability from the road (walker 0.44 m wide / 0.60 m comfortable):');
for (const rm of P.rooms) console.log(rm.id.padEnd(9), a.hit[rm.id] ? 'OK ' : 'NO ', '| 0.60m:', b.hit[rm.id] ? 'OK' : 'NO');

// spawn points standable?
const bad = P.rooms.filter(rm => { const [x, z, y] = rm.spawn; return !canStand(P, S, x, z, y, 0.22) || Math.abs(floorAt(P, x, z, y) - y) > 0.01; });
console.log('\nSpawn points not standable:', bad.length ? bad.map(r => r.id) : 'none');

// max level reached
console.log('Highest floor reached:', Math.max(...a.cells.map(c => c[2])).toFixed(2), 'm');

// overlaps: solid furniture vs walls & furniture on same level band
const walls = S.filter(s => /^(C\d|S0|L\d|R|CORE)/.test(s.id) && !s.id.endsWith('-leaf'));
const furn = P.furn.filter(f => f.solid !== false).map(f => ({ ...f, y1: f.y0 + f.h }));
const ov = (p, q) => Math.min(p.x2, q.x2) - Math.max(p.x1, q.x1) > 0.005 && Math.min(p.z2, q.z2) - Math.max(p.z1, q.z1) > 0.005 && Math.min(p.y1, q.y1) - Math.max(p.y0, q.y0) > 0.005;
const leaves = S.filter(s => s.id.endsWith('-leaf'));
const issues = [];
for (const f of furn) for (const w of walls) if (ov(f, w)) issues.push(`${f.id} × wall ${w.id}`);
for (const f of furn) for (const l of leaves) if (ov(f, l)) issues.push(`${f.id} × door leaf ${l.id}`);
for (let i = 0; i < furn.length; i++) for (let j = i + 1; j < furn.length; j++) if (ov(furn[i], furn[j])) issues.push(`${furn[i].id} × ${furn[j].id}`);
console.log('\nOverlaps:', issues.length ? issues : 'none');

// headroom over stair flights (clear height from tread to underside of the flight/slab above)
let minHead = 99;
for (const d of P.decks.filter(d => d.kind === 'step')) {
  const cx = (d.x1 + d.x2) / 2, cz = (d.z1 + d.z2) / 2;
  for (const e of P.decks) {
    if (e === d || !(cx >= e.x1 && cx <= e.x2 && cz >= e.z1 && cz <= e.z2)) continue;
    const under = e.y - (e.t || 0.15);
    if (e.y > d.y + 0.01) minHead = Math.min(minHead, under - d.y);
  }
}
console.log('Minimum stair headroom:', minHead.toFixed(2), 'm');

console.log('\nOpenings:');
for (const w of P.walls) for (const o of (w.open || [])) console.log(`${w.id.padEnd(6)} ${o.type.padEnd(6)} ${(o.b - o.a).toFixed(2)} m  ${o.label}`);

const fp = P.footprint, plot = P.plot.depth * P.plot.width, foot = (fp.x2 - fp.x1) * (fp.z2 - fp.z1);
console.log(`\nPlot ${plot.toFixed(2)} m² | footprint ${foot.toFixed(2)} m² (${(100 * foot / plot).toFixed(1)}%) | two floors ${(2 * foot).toFixed(2)} m² FAR ${(2 * foot / plot).toFixed(2)}`);
console.log('Tour stops reachable:', P.tour.every(id => a.hit[id]));
