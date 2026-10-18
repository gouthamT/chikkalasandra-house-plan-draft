/* Shared geometry + collision logic (B2, multi-level). Used by the page and by the Node verification test. */
const BODY_LOW = 0.25;   // obstacles whose top is within this of the feet are stepped over
const BODY_HIGH = 1.75;  // obstacles starting this far above the feet don't block (headroom)
const MAX_STEP = 0.2;    // highest single rise the walker can climb

// Open door leaf, parked at 90° against the hinge side, as a thin box.
function leafRect(w, o) {
  const T = 0.04, L = o.b - o.a, hinge = o.hinge === 'b' ? o.b : o.a, inward = o.hinge === 'b' ? -1 : 1;
  const face = o.side > 0 ? (w.axis === 'x' ? w.z2 : w.x2) : (w.axis === 'x' ? w.z1 : w.x1);
  const u1 = inward > 0 ? hinge : hinge - T, u2 = inward > 0 ? hinge + T : hinge;
  const v1 = o.side > 0 ? face : face - L, v2 = o.side > 0 ? face + L : face;
  return w.axis === 'x' ? { x1: u1, x2: u2, z1: v1, z2: v2 } : { x1: v1, x2: v2, z1: u1, z2: u2 };
}

function buildSolids(P) {
  const out = [];
  for (const w of P.walls) {
    const alongX = w.axis === 'x';
    const lo = alongX ? w.x1 : w.z1, hi = alongX ? w.x2 : w.z2;
    const box = (a, b, y0, y1) => {
      if (b - a < 1e-6) return;
      out.push(alongX ? { x1: a, x2: b, z1: w.z1, z2: w.z2, y0, y1, id: w.id } : { x1: w.x1, x2: w.x2, z1: a, z2: b, y0, y1, id: w.id });
    };
    let cur = lo;
    for (const o of [...(w.open || [])].sort((p, q) => p.a - q.a)) {
      if (o.type === 'window' || (o.type === 'gate' && o.closed)) continue;
      box(cur, o.a, w.y0, w.y1);
      if (o.type === 'arch' && o.par > 0) box(o.a, o.b, w.y0, w.y0 + o.par);
      if (o.type === 'door' && !o.slide && o.side) {
        const r = leafRect(w, o); out.push({ ...r, y0: w.y0, y1: w.y0 + 2.05, id: w.id + '-leaf' });
      }
      cur = Math.max(cur, o.b);
    }
    box(cur, hi, w.y0, w.y1);
  }
  for (const f of P.furn) {
    if (f.solid === false) continue;
    out.push({ x1: f.x1, x2: f.x2, z1: f.z1, z2: f.z2, y0: f.y0, y1: f.y0 + f.h, id: f.id });
  }
  for (const d of P.decks) if (d.kind === 'step') out.push({ x1: d.x1, x2: d.x2, z1: d.z1, z2: d.z2, y0: d.y - 0.25, y1: d.y, id: d.id, step: true });
  for (const n of (P.neighbours || [])) out.push({ ...n, y0: -1, y1: 30, id: 'neighbour' });
  for (const n of (P.walkFence || [])) out.push({ ...n, y0: -1, y1: 30, id: 'fence' });
  out.spirals = P.spirals || [];
  return out;
}

// Highest walkable surface at (x,z) that is not above the walker's reach from `feet`.
// Spiral stair helpers. Angles in degrees: atan2(z - cz, x - cx), 0..360. Sector 0 is the landing tread at each floor.
function spiralAt(s, x, z) {
  const dx = x - s.cx, dz = z - s.cz, d = Math.hypot(dx, dz);
  let th = Math.atan2(dz, dx) * 180 / Math.PI; if (th < 0) th += 360;
  const k = Math.floor((((th - s.a0) % 360) + 360) % 360 / (360 / s.n)) % s.n;
  return { d, k };
}
function spiralHeights(s, k) {
  const hs = [], L = s.levels;
  for (let t = 0; t < L.length - 1; t++) hs.push(L[t] + k * s.rise);
  if (k === 0) hs.push(L[L.length - 1]);
  return hs;
}
function floorAt(P, x, z, feet) {
  let y = P.ground;
  const lim = feet + MAX_STEP + 1e-6;
  for (const d of P.decks) {
    if (!(x >= d.x1 && x <= d.x2 && z >= d.z1 && z <= d.z2 && d.y <= lim && d.y > y)) continue;
    if (d.hole && Math.hypot(x - d.hole.cx, z - d.hole.cz) < d.hole.r) continue;
    y = d.y;
  }
  for (const s of (P.spirals || [])) {
    const { d, k } = spiralAt(s, x, z);
    if (d > s.rOut) continue;
    for (const h of spiralHeights(s, k)) if (h <= lim && h > y) y = h;
  }
  return y;
}

function hitBox(S, x, z, feet, r) {
  for (const b of S) {
    if (b.y1 <= feet + BODY_LOW || b.y0 >= feet + BODY_HIGH) continue;
    const cx = Math.max(b.x1, Math.min(x, b.x2)), cz = Math.max(b.z1, Math.min(z, b.z2));
    const dx = x - cx, dz = z - cz, rr = b.step && b.y1 <= feet + 0.6 ? Math.min(r, 0.1) : r;  // feet, not shoulders, meet the next riser
    if (dx * dx + dz * dz < rr * rr) return b;
  }
  for (const s of (S.spirals || [])) {
    const L = s.levels;
    if (feet < L[0] - 0.3 || feet > L[L.length - 1] + 0.3) continue;
    const { d, k } = spiralAt(s, x, z);
    if (d < s.rIn + r) return { id: 'spiral-post' };
    if (Math.abs(d - s.rOut) < r) {                       // balustrade ring, open only at the landing treads
      const atFloor = L.some(l => Math.abs(feet - l) < 0.3);
      if (!(atFloor && s.gap.includes(k))) return { id: 'spiral-rail' };
    }
    for (const [ox, oz] of [[0, 0], [.12, 0], [-.12, 0], [0, .12], [0, -.12], [.085, .085], [-.085, .085], [.085, -.085], [-.085, -.085]]) {
      const q = spiralAt(s, x + ox, z + oz);
      if (q.d < s.rIn || q.d > s.rOut) continue;
      for (const h of spiralHeights(s, q.k)) if (h > feet + BODY_LOW && h - 0.25 < feet + BODY_HIGH) return { id: 'spiral-step' };
    }
  }
  return null;
}

function canStand(P, S, x, z, feet, r) {
  const B = P.bounds;
  if (x < B.x1 || x > B.x2 || z < B.z1 || z > B.z2) return false;
  const fy = floorAt(P, x, z, feet);
  return !hitBox(S, x, z, fy, r);
}

function roomAt(P, x, z, feet) {
  let best = null;
  for (const r of P.rooms) {
    if (!(x >= r.x1 && x <= r.x2 && z >= r.z1 && z <= r.z2)) continue;
    if (r.early) { if ((r.ymin === undefined || feet >= r.ymin) && (r.ymax === undefined || feet <= r.ymax)) return r; continue; }
    if (r.lv === -1 || r.lv === 0) { if (feet < 1.0 && !best) best = r; continue; }
    if (feet >= r.y - 0.6 && feet < r.y + 2.2) return r;
  }
  return best;
}

function levelOf(P, feet) {
  let lv = 0;
  P.levels.forEach((y, i) => { if (feet >= y - 0.8) lv = i; });
  return lv;
}

if (typeof module !== 'undefined') module.exports = { buildSolids, floorAt, hitBox, canStand, roomAt, levelOf, leafRect, spiralAt, spiralHeights, MAX_STEP };
