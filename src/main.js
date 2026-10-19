(() => {
const P = JSON.parse(document.getElementById('planData').textContent);
const S = buildSolids(P);
const R = 0.22, EYE = 1.6;
const LEVEL_NAMES = ['Stilt · parking', 'First floor · +3.15 m', 'Second floor · +6.30 m', 'Roof garden · +9.45 m'];
const LEVEL_SHORT = ['STILT', 'FIRST FLOOR', 'SECOND FLOOR', 'ROOF'];
const ftIn = m => { const t = Math.round(m / 0.0254), f = Math.floor(t / 12); return `${f}'-${t - f * 12}"`; };
const dimTxt = (a, b) => `${a.toFixed(2)} × ${b.toFixed(2)} m · ${ftIn(a)} × ${ftIn(b)} · ${(a * b).toFixed(1)} m²`;

/* ---------------- tabs ---------------- */
const tabs = document.querySelectorAll('nav button');
let active = 'walk';
tabs.forEach(b => b.addEventListener('click', () => {
  active = b.dataset.tab;
  tabs.forEach(t => t.setAttribute('aria-selected', t === b));
  ['walk', 'plan', 'report'].forEach(id => document.getElementById(id).hidden = id !== active);
  if (active === 'walk') resize(); else if (document.pointerLockElement) document.exitPointerLock();
}));

/* ================= DRAWINGS (built first so they work even without WebGL) ================= */
const PS = 56, POX = 150, POY = 70;
const X = x => POX + x * PS, Z = z => POY + z * PS;
const T = (x, y, t, cls, anchor = 'middle', extra = '') => `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" class="${cls}" text-anchor="${anchor}" ${extra}>${t}</text>`;
const RC = (x1, x2, z1, z2, cls, extra = '') => `<rect x="${X(x1).toFixed(1)}" y="${Z(z1).toFixed(1)}" width="${((x2 - x1) * PS).toFixed(1)}" height="${((z2 - z1) * PS).toFixed(1)}" class="${cls}" ${extra}/>`;
const onLevel = (lv, item) => item.lv === lv || (item.lv === -1 && (lv === 0 || String(item.id).startsWith('CORE')));
const LABEL_POS = { front: [0.45, 2.0], passage: [1.65, 4.9], carbay: [3.3, 3.12], foyer: [3.2, 5.6], laundry: [4.62, 5.78], bikebay: [8.3, 3.95], store: [10.55, 4.25],
  balc1: [1.72, 2.2], powder: [3.3, 1.95], hall1: [3.17, 3.1], living: [5.55, 3.4], kitchen: [8.1, 4.4], pooja: [7.35, 2.6], bed2: [8.85, 2.4],
  lounge: [2.6, 3.1], nook: [1.8, 5.75], master: [8.3, 3.7], ensuite: [6.1, 2.25], hall2: [5.7, 3.1], cabin: [3.17, 5.3], roof: [3.4, 1.3], roofrear: [9.6, 4.4] };
function planSvg(lv) {
  const W = POX + 12.6 * PS + 40, H = POY + 6.3 * PS + 40;
  let s = `<defs><pattern id="chk${lv}" width="16.8" height="16.8" patternUnits="userSpaceOnUse"><rect width="16.8" height="16.8" fill="var(--panel)"/><rect width="8.4" height="8.4" fill="var(--line)"/><rect x="8.4" y="8.4" width="8.4" height="8.4" fill="var(--line)"/></pattern><marker id="ah${lv}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--ink)"/></marker></defs>`;
  s += `<rect x="${X(-2.2)}" y="${Z(-0.5)}" width="${2.2 * PS - 6}" height="${7.1 * PS}" class="pl-road"/>` + T(X(-1.75), Z(3.05), 'ROAD · WEST', 'pl-small', 'middle', `transform="rotate(-90 ${X(-1.75)} ${Z(3.05)})" style="font-size:11px;letter-spacing:.3em"`);
  for (const f of P.finishes.filter(f => f.lv === lv)) s += f.mat === 'checker' ? RC(f.x1, f.x2, f.z1, f.z2, '', `fill="url(#chk${lv})"`) : RC(f.x1, f.x2, f.z1, f.z2, 'pl-fl-' + f.mat);
  s += RC(0, 12.192, 0, 6.096, 'pl-plot');
  const sb = P.setbacks;
  if (lv === 0) {
    s += `<line x1="${X(sb.front)}" y1="${Z(0)}" x2="${X(sb.front)}" y2="${Z(6.096)}" class="pl-set"/><line x1="${X(12.192 - sb.rear)}" y1="${Z(0)}" x2="${X(12.192 - sb.rear)}" y2="${Z(6.096)}" class="pl-set"/><line x1="${X(0)}" y1="${Z(sb.north)}" x2="${X(12.192)}" y2="${Z(sb.north)}" class="pl-set"/>`;
    s += T(X(6.0), Z(0.45), 'NORTH SIDE SETBACK 0.70 · OPEN', 'pl-settext') + T(X(11.84), Z(3.05), 'REAR SETBACK 0.70', 'pl-settext', 'middle', `transform="rotate(90 ${X(11.84)} ${Z(3.05)})"`);
  }
  const base = P.levels[lv];
  for (const d of P.decks.filter(d => d.kind === 'step')) {
    const rel = d.y - base;
    if ((rel > 0 && rel <= 1.6) || (rel <= 0 && rel > -1.6)) s += RC(d.x1, d.x2, d.z1, d.z2, 'pl-step');
    else if (rel > 1.6 && rel < 3.15) s += RC(d.x1, d.x2, d.z1, d.z2, 'pl-step', 'stroke-dasharray="2 2"');
  }
  const SL = P.stairLane, sp = P.spirals[0], ST = P.stair;
  if (ST && lv < 3) s += `<path d="M${ST.arrow.map(([x, z]) => `${X(x).toFixed(1)} ${Z(z).toFixed(1)}`).join(' L')}" class="pl-arrow" fill="none" marker-end="url(#ah${lv})"/>` + T(X(ST.up[0]), Z(ST.up[1]), 'UP', 'pl-small');
  if (ST && lv >= 1) s += T(X(ST.dn[0]), Z(ST.dn[1]), 'DN', 'pl-small');
  if (lv >= 1 && sp) {
    const cx = X(sp.cx), cy = Z(sp.cz), R = sp.rOut * PS;
    s += `<circle cx="${cx}" cy="${cy}" r="${R}" class="pl-step"/><circle cx="${cx}" cy="${cy}" r="${sp.rIn * PS}" class="pl-wall"/>`;
    for (let k = 0; k < sp.n; k++) { const a = (sp.a0 + k * 360 / sp.n) * Math.PI / 180; s += `<line x1="${cx + Math.cos(a) * sp.rIn * PS}" y1="${cy + Math.sin(a) * sp.rIn * PS}" x2="${cx + Math.cos(a) * R}" y2="${cy + Math.sin(a) * R}" class="pl-swing" style="stroke-dasharray:none"/>`; }
    if (lv < 3) { const a1 = (sp.a0 + 11.25) * Math.PI / 180, a2 = (sp.a0 + 300) * Math.PI / 180, rr = R * .62;
      s += `<path d="M${cx + Math.cos(a1) * rr} ${cy + Math.sin(a1) * rr} A${rr} ${rr} 0 1 1 ${cx + Math.cos(a2) * rr} ${cy + Math.sin(a2) * rr}" class="pl-arrow" marker-end="url(#ah${lv})"/>` + T(cx, cy + R * .2, 'UP', 'pl-small'); }
  }
  for (const f of P.furn.filter(f => f.lv === lv)) {
    if (['tv', 'over', 'frames', 'ucan', 'lines', 'tank', 'tree'].includes(f.id)) continue;
    const cls = f.shape === 'car' || f.shape === 'bike' ? 'pl-vehicle' : ['planter', 'screen', 'pot'].includes(f.shape) ? 'pl-plant' : 'pl-furn';
    s += RC(f.x1, f.x2, f.z1, f.z2, cls, 'rx="2"' + (f.solid === false ? ' stroke-dasharray="3 2"' : ''));
    if (f.shape === 'island') s += RC(f.x1, f.x2, f.z2, f.z2 + .3, 'pl-furn', 'stroke-dasharray="3 2"');
    if (f.shape === 'islandSink') s += RC(f.x1, f.x2, f.z1 - .25, f.z1, 'pl-furn', 'stroke-dasharray="3 2"') + `<rect x="${X((f.x1 + f.x2) / 2 - .3).toFixed(1)}" y="${Z((f.z1 + f.z2) / 2 - .05).toFixed(1)}" width="${.6 * PS}" height="${.35 * PS}" rx="4" class="pl-swing" style="stroke-dasharray:none"/>` + T(X((f.x1 + f.x2) / 2), Z(f.z2) - 4, 'SINK', 'pl-small');
    if (f.shape === 'islandZ' && f.sink !== false) s += ((f.over ?? .25) > 0 ? RC(f.x1 - (f.over ?? .25), f.x1, f.z1, f.z2, 'pl-furn', 'stroke-dasharray="3 2"') : '') + `<rect x="${X((f.x1 + f.x2) / 2 - .2).toFixed(1)}" y="${Z((f.z1 + f.z2) / 2 - .3).toFixed(1)}" width="${.4 * PS}" height="${.6 * PS}" rx="4" class="pl-swing" style="stroke-dasharray:none"/>` + T(X((f.x1 + f.x2) / 2), Z(f.z1) - 4, 'SINK', 'pl-small');
    if (f.shape === 'counterE' && f.sink) s += `<rect x="${X(f.x1 + .08).toFixed(1)}" y="${Z(f.sink[0]).toFixed(1)}" width="${(f.x2 - f.x1 - .18) * PS}" height="${(f.sink[1] - f.sink[0]) * PS}" rx="4" class="pl-swing" style="stroke-dasharray:none"/>` + T(X(f.x1) - 4, Z((f.sink[0] + f.sink[1]) / 2) + 3, 'SINK 2', 'pl-small', 'end');
    if (f.shape === 'counterE') { const cx = X((f.x1 + f.x2) / 2); for (const zz of [f.hob[0] + .15, f.hob[1] - .15]) s += `<circle cx="${cx}" cy="${Z(zz)}" r="6" class="pl-swing" style="stroke-dasharray:none"/>`; s += T(cx - 12, Z((f.hob[0] + f.hob[1]) / 2) + 3, 'HOB', 'pl-small', 'end'); }
  }
  if (lv === 0) s += T(X(3.3), Z(1.95), 'CAR 4.00 × 1.75', 'pl-small') + T(X(8.3), Z(4.82), 'BIKE', 'pl-small') + RC(5.6, 10.9, 0.98, 3.35, 'pl-vehicle', 'rx="2" opacity=".55"') + T(X(8.25), Z(2.25), '2ND CAR (TANDEM)', 'pl-small');
  for (const w of P.walls.filter(w => onLevel(lv, w))) {
    const alongX = w.axis === 'x', lo = alongX ? w.x1 : w.z1, hi = alongX ? w.x2 : w.z2;
    const cls = w.kind === 'compound' || w.kind === 'parapet' ? 'pl-cwall' : w.kind === 'rail' || w.kind === 'sguard' ? 'pl-rail' : w.kind === 'screen' ? 'pl-win' : 'pl-wall';
    const piece = (a, b, c) => alongX ? RC(a, b, w.z1, w.z2, c) : RC(w.x1, w.x2, a, b, c);
    const mid = alongX ? (w.z1 + w.z2) / 2 : (w.x1 + w.x2) / 2;
    let cur = lo;
    for (const o of [...(w.open || [])].sort((p, q) => p.a - q.a)) {
      s += piece(cur, o.a, cls);
      if (o.type === 'window') s += piece(o.a, o.b, 'pl-win') + (alongX ? `<line x1="${X(o.a)}" y1="${Z(mid)}" x2="${X(o.b)}" y2="${Z(mid)}" class="pl-door"/>` : `<line x1="${X(mid)}" y1="${Z(o.a)}" x2="${X(mid)}" y2="${Z(o.b)}" class="pl-door"/>`);
      if (o.type === 'arch' && o.par > 0) s += o.glazed ? piece(o.a, o.b, 'pl-win') + `<line x1="${X(mid)}" y1="${Z(o.a)}" x2="${X(mid)}" y2="${Z(o.b)}" class="pl-door"/>` : piece(o.a, o.b, 'pl-par');
      if (o.type === 'gate' && o.closed) s += piece(o.a, o.b, 'pl-win') + `<line x1="${X(mid)}" y1="${Z(o.a)}" x2="${X(mid)}" y2="${Z(o.b)}" class="pl-swing"/>`;
      if (o.type === 'door' && o.slide && !alongX) s += `<line x1="${X(mid) - 2}" y1="${Z(o.a)}" x2="${X(mid) - 2}" y2="${Z((o.a + o.b) / 2 + .1)}" class="pl-door" style="stroke-width:2"/><line x1="${X(mid) + 2}" y1="${Z((o.a + o.b) / 2 - .1)}" x2="${X(mid) + 2}" y2="${Z(o.b)}" class="pl-door" style="stroke-width:2"/>`;
      if (o.type === 'door' && o.side) {
        const r = leafRect(w, o), L = (o.b - o.a) * PS;
        const hinge = o.hinge === 'b' ? o.b : o.a, other = o.hinge === 'b' ? o.a : o.b, face = o.side > 0 ? (alongX ? w.z2 : w.x2) : (alongX ? w.z1 : w.x1);
        s += RC(r.x1, r.x2, r.z1, r.z2, 'pl-door');
        if (alongX) { const tipY = Z(face) + o.side * L, sweep = (o.side > 0) === (other > hinge) ? 0 : 1; s += `<path d="M${X(hinge)} ${tipY} A${L} ${L} 0 0 ${sweep} ${X(other)} ${Z(face)}" class="pl-swing"/>`; }
        else { const tipX = X(face) + o.side * L, sweep = (o.side > 0) === (other > hinge) ? 1 : 0; s += `<path d="M${tipX} ${Z(hinge)} A${L} ${L} 0 0 ${sweep} ${X(face)} ${Z(other)}" class="pl-swing"/>`; }
      }
      cur = Math.max(cur, o.b);
    }
    s += piece(cur, hi, cls);
  }
  for (const c of (P.columns || [])) s += RC(c.x1, c.x2, c.z1, c.z2, 'pl-col');
  for (const r of P.rooms.filter(r => (r.lv === lv || (lv === 0 && r.lv === -1)) && LABEL_POS[r.id])) {
    if (r.id === 'stairs' || r.id === 'spiral') continue;
    const [lx, lz] = LABEL_POS[r.id], w = r.x2 - r.x1, d = r.z2 - r.z1;
    if (r.id === 'front') { s += T(X(lx), Z(4.45), 'FRONT GARDEN', 'pl-small', 'middle', `transform="rotate(-90 ${X(lx)} ${Z(4.45)})"`); continue; }
    s += T(X(lx), Z(lz), r.short, 'pl-label');
    if (!['front', 'stairs', 'spiral', 'hall2', 'hall1', 'passage', 'landing1', 'kitchen', 'pooja', 'powder', 'ensuite', 'laundry', 'cabin', 'nook', 'foyer'].includes(r.id)) s += T(X(lx), Z(lz) + 13, `${w.toFixed(2)} × ${d.toFixed(2)}`, 'pl-dim');
  }
  if (lv === 3) s += T(X(5.3), Z(3.45), 'STAIR CABIN · TANK + SKYLIGHT OVER', 'pl-small') + T(X(9.8), Z(1.15), 'SOLAR OVER DRYING DECK', 'pl-small');
  if (lv === 0) s += T(X(5.3), Z(3.5), 'GLASS SCREEN', 'pl-small');
  const chain = lv === 0 ? [0, 0.9, 2.4, 3.8, 6.915, 9.8, 11.49, 12.192] : lv === 3 ? [0.9, 2.4, 6.915, 11.49] : lv === 1 ? [0.9, 2.4, 4.2, 6.8, 8.0, 11.49] : [0.9, 2.4, 4.6, 6.915, 11.49];
  const yT = POY - 30;
  s += `<line x1="${X(chain[0])}" y1="${yT}" x2="${X(chain[chain.length - 1])}" y2="${yT}" class="pl-dline"/>`;
  chain.forEach((v, i) => { s += `<line x1="${X(v)}" y1="${yT - 5}" x2="${X(v)}" y2="${yT + 5}" class="pl-dline"/>`; if (i) { const a = chain[i - 1]; s += T(X((a + v) / 2), yT - 6, (v - a).toFixed(2), 'pl-dim'); } });
  const xL = POX - 40, ch2 = [0, 0.7, 6.096];
  s += `<line x1="${xL}" y1="${Z(0)}" x2="${xL}" y2="${Z(6.096)}" class="pl-dline"/>`;
  ch2.forEach((v, i) => { s += `<line x1="${xL - 5}" y1="${Z(v)}" x2="${xL + 5}" y2="${Z(v)}" class="pl-dline"/>`; if (i) s += T(xL - 7, Z((ch2[i - 1] + v) / 2) + 3, (v - ch2[i - 1]).toFixed(2), 'pl-dim', 'end'); });
  const nx = W - 34, ny = 34;
  s += `<path d="M${nx} ${ny - 16} L${nx + 7} ${ny + 7} L${nx} ${ny + 2} L${nx - 7} ${ny + 7} Z" class="pl-wall"/>` + T(nx, ny + 21, 'N', 'pl-dim');
  return { svg: s, W, H };
}
function buildElevation() {
  const ES = 44, OX = 40, base = 620, ex = z => OX + z * ES, ey = y => base - y * ES;
  const Wd = OX * 2 + 6.4 * ES, H = base + 40, yTop = P.levels[3];
  let s = `<rect x="0" y="0" width="${Wd + 120}" height="${H}" class="el-sky"/>`;
  s += `<rect x="${ex(3.635)}" y="${ey(yTop + 2.55)}" width="${(6.096 - 3.635) * ES}" height="${2.55 * ES}" class="el-back"/>`;
  s += `<rect x="${ex(4.3)}" y="${ey(yTop + 2.1)}" width="${1.0 * ES}" height="${1.1 * ES}" class="el-glass"/>`;
  s += `<rect x="${ex(4.7)}" y="${ey(yTop + 2.7 + 1.3)}" width="${1.1 * ES}" height="${1.3 * ES}" class="el-back"/>`;
  s += `<rect x="${ex(0.7)}" y="${ey(yTop + 1.0)}" width="${(6.096 - 0.7) * ES}" height="${(yTop + 1.0) * ES}" class="el-render"/>`;
  s += `<rect x="${ex(0.93)}" y="${ey(3.0)}" width="${(5.866 - 0.93) * ES}" height="${3.0 * ES}" class="el-void"/>`;
  for (const lv of [1, 2]) {
    const y0 = P.levels[lv];
    for (const [a, b] of [[1.15, 3.15], [3.65, 5.65]]) {
      const r = (b - a) / 2, sp = y0 + 1.8;
      s += `<path d="M${ex(a)} ${ey(y0)} V${ey(sp)} A${r * ES} ${r * ES} 0 0 1 ${ex(b)} ${ey(sp)} V${ey(y0)} Z" class="${lv === 2 ? 'el-glass' : 'el-void'}"/>`;
      if (lv === 2) s += `<path d="M${ex(a + r)} ${ey(y0 + .45)} V${ey(sp + r)} M${ex(a)} ${ey(sp)} H${ex(b)} M${ex(a + r / 2)} ${ey(y0 + .45)} V${ey(sp)} M${ex(b - r / 2)} ${ey(y0 + .45)} V${ey(sp)}" class="el-steel"/>`;
      s += `<rect x="${ex(a + .1)}" y="${ey(y0 + 1.3)}" width="${(b - a - .2) * ES}" height="${0.3 * ES}" class="el-plant"/>`;
      s += `<rect x="${ex(a)}" y="${ey(y0 + (lv === 2 ? .45 : 1.05))}" width="${(b - a) * ES}" height="${(lv === 2 ? .45 : 1.05) * ES}" class="el-render"/>`;
    }
  }
  s += `<rect x="${ex(1.5)}" y="${ey(yTop + 2.8)}" width="${2.05 * ES}" height="${0.2 * ES}" class="el-wood"/>`;
  for (const z of [1.6, 3.33]) s += `<rect x="${ex(z)}" y="${ey(yTop + 2.6)}" width="${.12 * ES}" height="${1.6 * ES}" class="el-wood"/>`;
  s += `<path d="M${ex(-0.15)} ${ey(-0.15)} V${ey(2.7)} H${ex(6.246)} V${ey(-0.15)} Z" class="el-render"/>`;
  s += `<rect x="${ex(0.15)}" y="${ey(2.15)}" width="${3.2 * ES}" height="${2.3 * ES}" class="el-gate"/>`;
  for (let z = 0.18; z < 3.33; z += 0.075) s += `<line x1="${ex(z)}" y1="${ey(-0.1)}" x2="${ex(z)}" y2="${ey(2.15)}" class="el-batten"/>`;
  { const a = 3.6, b = 4.74, top = -0.15 + 2.45;
    s += `<rect x="${ex(a)}" y="${ey(top)}" width="${(b - a) * ES}" height="${(top + .15) * ES}" class="el-gate"/>`;
    for (let z = a + .03; z < b - .02; z += .075) s += `<line x1="${ex(z)}" y1="${ey(-0.1)}" x2="${ex(z)}" y2="${ey(top - .02)}" class="el-batten"/>`; }
  s += `<rect x="${ex(5.48)}" y="${ey(2.75)}" width="4" height="${0.15 * ES}" class="el-wood"/><circle cx="${ex(5.5)}" cy="${ey(3.3)}" r="${0.6 * ES}" class="el-plant"/>`;
  s += `<line x1="0" y1="${ey(-0.15)}" x2="${Wd}" y2="${ey(-0.15)}" class="el-ground"/>`;
  P.levels.forEach((y, i) => { s += `<line x1="${ex(6.3)}" y1="${ey(y)}" x2="${ex(6.55)}" y2="${ey(y)}" class="pl-dline"/>` + T(ex(6.6), ey(y) + 3, `+${y.toFixed(2)} ${['STILT', 'FIRST', 'SECOND', 'ROOF'][i]}`, 'pl-dim', 'start'); });
  s += T(ex(0.7), ey(-0.15) + 18, 'NORTH', 'pl-small', 'start') + T(ex(6.096), ey(-0.15) + 18, 'SOUTH', 'pl-small', 'end');
  const svg = document.getElementById('elevSvg'); svg.setAttribute('viewBox', `0 0 ${Wd + 120} ${H}`); svg.style.minWidth = '440px'; svg.style.maxWidth = '640px'; svg.innerHTML = s;
}
function buildTables() {
  const order = [[0, ['passage', 'foyer', 'laundry', 'carbay', 'bikebay', 'store']], [1, ['balc1', 'powder', 'living', 'pooja', 'kitchen', 'bed2']], [2, ['lounge', 'nook', 'ensuite', 'master']], [3, ['roof', 'roofrear']]];
  const floorName = ['Stilt', 'First floor', 'Second floor', 'Roof'];
  const fl = { lounge: 'Terracotta + oxide', nook: 'Terracotta', hall1: 'Stone-look porcelain', powder: 'Anti-skid tile', study: 'Green oxide', pooja: 'Stone-look porcelain', balc1: 'Terracotta', balc2: 'Terracotta', living: 'Stone-look porcelain', kitchen: 'Stone-look porcelain', hall2: 'Stone-look porcelain', bath1: 'Anti-skid tile', bath2: 'Anti-skid tile', ensuite: 'Anti-skid tile', bed1: 'Green oxide', bed2: 'Green oxide', master: 'Green oxide', roof: 'Terracotta + lawn', roofrear: 'Terracotta', passage: 'Checkerboard marble', foyer: 'Checkerboard marble', landing1: 'Stone-look porcelain', store: 'Concrete', carbay: 'Concrete pavers', laundry: 'Checkerboard marble', bikebay: 'Concrete', cabin: 'Stone-look porcelain' };
  let rows = '';
  for (const [lv, ids] of order) {
    rows += `<tr class="sub"><td colspan="6">${floorName[lv]}</td></tr>`;
    for (const id of ids) { const r = P.rooms.find(q => q.id === id), w = r.x2 - r.x1, d = r.z2 - r.z1;
      rows += `<tr><td>${r.name}</td><td class="n">${w.toFixed(2)} × ${d.toFixed(2)} m</td><td class="n">${ftIn(w)} × ${ftIn(d)}</td><td class="n">${(w * d).toFixed(1)} m²</td><td class="n">${(w * d * 10.764).toFixed(0)} sq ft</td><td>${fl[id]}</td></tr>`; }
  }
  const fp = P.footprint, foot = (fp.x2 - fp.x1) * (fp.z2 - fp.z1), plot = P.plot.depth * P.plot.width;
  rows += `<tr class="sub"><td>Built-up, first + second floors</td><td></td><td></td><td class="n">${(2 * foot).toFixed(1)} m²</td><td class="n">${(2 * foot * 10.764).toFixed(0)} sq ft</td><td>FAR ${(2 * foot / plot).toFixed(2)} of 1.75 · stilt and stair cabin excluded</td></tr>`;
  document.getElementById('areaTable').innerHTML = `<thead><tr><th>Room</th><th>Clear size</th><th>Feet</th><th>Area</th><th></th><th>Floor finish</th></tr></thead><tbody>${rows}</tbody>`;
  document.getElementById('kpis').innerHTML = `<div><b>${(2 * foot).toFixed(1)} m²</b><span>built-up on two floors (${(2 * foot * 10.764).toFixed(0)} sq ft)</span></div><div><b>${(2 * foot / plot).toFixed(2)}</b><span>FAR used of 1.75</span></div><div><b>${(100 * foot / plot).toFixed(0)}%</b><span>ground coverage (check cap)</span></div><div><b>2 + lounge</b><span>bedrooms, plus the family lounge</span></div><div><b>${P.rooms.length} / ${P.rooms.length}</b><span>zones reached in walk test</span></div>`;
  let dr = '';
  const lvName = w => w.lv === -1 ? (w.id.startsWith('CORE') ? 'All floors' : 'Boundary') : floorName[w.lv];
  for (const w of P.walls) for (const o of (w.open || [])) {
    const h = o.type === 'window' ? `sill ${o.sill.toFixed(2)} · head ${o.head.toFixed(2)}` : o.type === 'arch' ? (o.par ? `parapet ${o.par.toFixed(2)} · springs ${o.spring.toFixed(2)}` : `springs ${o.spring.toFixed(2)}`) : o.type === 'gate' ? `height ${o.rel_h.toFixed(2)}` : o.slide ? 'head 2.60' : 'head 2.10';
    dr += `<tr><td>${o.label}</td><td class="n">${(o.b - o.a).toFixed(2)} m</td><td class="n">${ftIn(o.b - o.a)}</td><td class="n">${h}</td><td>${lvName(w)}</td></tr>`;
  }
  document.getElementById('doorTable').innerHTML = `<thead><tr><th>Opening</th><th>Clear width</th><th>Feet</th><th>Height (m, from floor)</th><th>Level</th></tr></thead><tbody>${dr}</tbody>`;
}
{
  const host = document.getElementById('plans'); let html = '';
  const titles = ['Stilt floor · ±0.00: parking, porch, foyer, U-turn stair, laundry', 'First floor · +3.15: loggia, living, pooja, kitchen + island, bedroom 2, bath', 'Second floor · +6.30: family lounge, master suite', 'Roof · +9.45: garden, stair cabin, solar, drying'];
  for (let lv = 0; lv < 4; lv++) { const { svg, W, H } = planSvg(lv); html += `<h3>${titles[lv]}</h3><div class="svgbox"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${titles[lv]}">${svg}</svg></div>`; }
  host.innerHTML = html;
  buildElevation(); buildTables();
}

/* ================= 3D ================= */
let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
function canvasTex(size, draw) {
  const c = document.createElement('canvas'); c.width = c.height = size;
  draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.encoding = THREE.sRGBEncoding; t.anisotropy = 4;
  return t;
}
function mottle(g, s, base, spots, n, rmin, rmax, a) {
  if (base) { g.fillStyle = base; g.fillRect(0, 0, s, s); }
  for (let i = 0; i < n; i++) {
    g.globalAlpha = a * rnd(); g.fillStyle = spots[i % spots.length];
    const x = rnd() * s, y = rnd() * s, r = rmin + rnd() * (rmax - rmin);
    for (const dx of [-s, 0, s]) for (const dy of [-s, 0, s]) { g.beginPath(); g.arc(x + dx, y + dy, r, 0, 7); g.fill(); }
  }
  g.globalAlpha = 1;
}
function grain(g, s, base, dark, light) {
  g.fillStyle = base; g.fillRect(0, 0, s, s);
  for (let y = 0; y < s; y += 2) { g.globalAlpha = .1 + .2 * rnd(); g.fillStyle = rnd() > .5 ? dark : light; g.fillRect(0, y, s, 1 + rnd() * 2); }
  g.globalAlpha = 1;
}
function grout(g, s, nx, ny, col, w) { g.strokeStyle = col; g.lineWidth = w; for (let i = 0; i <= nx; i++) { g.beginPath(); g.moveTo(i * s / nx, 0); g.lineTo(i * s / nx, s); g.stroke(); } for (let j = 0; j <= ny; j++) { g.beginPath(); g.moveTo(0, j * s / ny); g.lineTo(s, j * s / ny); g.stroke(); } }
const TEX = {
  stoneTile: canvasTex(512, (g, s) => { mottle(g, s, '#cdc7bb', ['#d8d3c8', '#bfb8ab', '#c7c1b4'], 220, 10, 60, .35);
    g.strokeStyle = 'rgba(255,255,255,.18)'; g.lineWidth = 1.5; for (let i = 0; i < 9; i++) { g.beginPath(); let x = rnd() * s, y = rnd() * s; g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (rnd() - .3) * 90; y += (rnd() - .5) * 40; g.lineTo(x, y); } g.stroke(); }
    grout(g, s, 1, 2, 'rgba(90,85,75,.35)', 2); }),
  checker: canvasTex(256, (g, s) => { const c = s / 4; for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { g.fillStyle = (i + j) % 2 ? '#1f1f1d' : '#efede7'; g.fillRect(i * c, j * c, c, c); }
    mottle(g, s, null, ['#ffffff', '#8d8a82'], 160, 2, 10, .12); }),
  concrete: canvasTex(256, (g, s) => { mottle(g, s, '#a7a49c', ['#b4b1a9', '#99968e', '#8f8c84'], 500, 2, 14, .4); grout(g, s, 2, 2, 'rgba(60,58,52,.35)', 2); }),
  oxide: canvasTex(512, (g, s) => mottle(g, s, '#a9bf97', ['#b9cda8', '#98af86', '#c3d3b2'], 260, 6, 40, .35)),
  wet: canvasTex(256, (g, s) => { mottle(g, s, '#d4d4cc', ['#c9c9c0', '#dedfd8'], 60, 4, 20, .4); grout(g, s, 2, 2, 'rgba(80,85,75,.35)', 2); }),
  wetdark: canvasTex(128, (g, s) => { mottle(g, s, '#a9aaa2', ['#9c9d95', '#b6b7af'], 60, 2, 8, .5); grout(g, s, 4, 4, 'rgba(50,52,48,.4)', 1.5); }),
  terracotta: canvasTex(256, (g, s) => { mottle(g, s, '#b9643f', ['#c87652', '#a8573a', '#c06a45'], 160, 4, 26, .5); grout(g, s, 3, 3, 'rgba(240,226,206,.6)', 3); }),
  lawn: canvasTex(256, (g, s) => mottle(g, s, '#6f8f48', ['#7d9d55', '#5f7f3c', '#8aa860'], 400, 2, 7, .6)),
  pavers: canvasTex(256, (g, s) => { g.fillStyle = '#6f8c4c'; g.fillRect(0, 0, s, s); mottle(g, s, null, ['#7f9c58', '#5d7a3e'], 80, 3, 10, .6);
    g.fillStyle = '#a7a395'; const c = s / 4; for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { g.fillRect(i * c + 3, j * c + 3, c - 6, 6); g.fillRect(i * c + 3, j * c + 3, 6, c - 6); } }),
  gravel: canvasTex(256, (g, s) => mottle(g, s, '#a69f90', ['#8c8577', '#bdb6a6', '#7a7468'], 900, 1, 4, .8)),
  asphalt: canvasTex(256, (g, s) => mottle(g, s, '#55575a', ['#4a4c4f', '#64666a'], 900, 1, 3, .7)),
  stepping: canvasTex(256, (g, s) => { mottle(g, s, '#6f8f48', ['#7d9d55', '#5f7f3c'], 200, 2, 6, .6); g.fillStyle = '#c9c2b2'; for (let j = 0; j < 3; j++) g.fillRect(s * .1, j * s / 3 + 10, s * .8, s / 3 - 26); }),
  soil: canvasTex(128, (g, s) => mottle(g, s, '#5a4532', ['#4b3828', '#6a5240'], 300, 1, 4, .6)),
  rug: canvasTex(256, (g, s) => { g.fillStyle = '#d9cfbd'; g.fillRect(0, 0, s, s); mottle(g, s, null, ['#cbbfa9', '#e3dac9'], 400, 1, 3, .5); g.strokeStyle = '#b6a78d'; g.lineWidth = 6; g.strokeRect(14, 14, s - 28, s - 28); }),
  walnut: canvasTex(256, (g, s) => grain(g, s, '#6e4428', '#563319', '#86573a')),
  render: canvasTex(256, (g, s) => mottle(g, s, '#eeece6', ['#e6e3dc', '#f5f4f0'], 300, 6, 30, .35))
};
const texCache = {};
function texMat(name, w, d, tile, extra = {}) {
  const key = `${name}|${w.toFixed(2)}|${d.toFixed(2)}|${tile}|${extra.roughness || ''}`;
  if (texCache[key]) return texCache[key];
  const t = TEX[name].clone(); t.needsUpdate = true; t.repeat.set(tile ? w / tile : 1, tile ? d / tile : 1);
  return texCache[key] = new THREE.MeshStandardMaterial({ map: t, roughness: .8, ...extra });
}
const TILE = { stoneTile: 1.2, checker: 1.2, concrete: 1.2, oxide: 1.6, wet: 0.6, wetdark: 0.4, terracotta: 0.9, lawn: 1.5, rug: 0, pavers: 1.2, gravel: 1.5, asphalt: 4, stepping: 1.1, soil: .5 };
const mat = (c, o = {}) => { const m = new THREE.MeshStandardMaterial({ color: c, roughness: .85, ...o }); m.color.convertSRGBToLinear(); return m; };
const M = {
  render: new THREE.MeshStandardMaterial({ map: TEX.render, roughness: .95 }),
  wallInt: mat(0xf2efe8, { roughness: .95 }),
  slab: mat(0xe9e6df, { roughness: .95 }),
  glass: mat(0xbcd0d4, { transparent: true, opacity: .26, roughness: .08, depthWrite: false }),
  walnut: new THREE.MeshStandardMaterial({ map: TEX.walnut, roughness: .62 }),
  white: mat(0xf2f1ee, { roughness: .55 }),
  quartz: mat(0xf4f3f0, { roughness: .35 }),
  sage: mat(0x9db19a, { roughness: .75 }),
  linen: mat(0xe8e1d3, { roughness: .95 }),
  boucle: mat(0xeae4d8, { roughness: 1 }),
  cane: mat(0xc8a36a, { roughness: .9 }),
  black: mat(0x22221e, { roughness: .5, metalness: .2 }),
  steel: mat(0xb8b9b4, { roughness: .35, metalness: .5 }),
  nickel: mat(0xa9a69c, { roughness: .3, metalness: .7 }),
  ceramic: mat(0xf6f5f1, { roughness: .2 }),
  terracotta: mat(0xb4593a, { roughness: .9 }),
  stone: mat(0xc6bfb1, { roughness: .8 }),
  step: mat(0xd2ccc0, { roughness: .7 }),
  car: mat(0x6c7f8c, { roughness: .3, metalness: .35 }),
  tyre: mat(0x1d1d1b, { roughness: .9 }),
  gateback: mat(0x3c2a1c),
  leaf: [mat(0x58773f), mat(0x6c8c4a), mat(0x4a6a37), mat(0x7f9b55)],
  flower: mat(0xf6efe0), trunk: mat(0x6d5a48),
  solar: mat(0x1d2a3a, { roughness: .25, metalness: .4 }),
  neighbour: mat(0xd9d5cb, { roughness: 1 }),
  shadowLine: mat(0xc9c7c1), joint: mat(0x3a2414),
  person: mat(0x3f5d4b, { roughness: .7 }), skin: mat(0xb98563, { roughness: .8 }), accent: mat(0xb4593a)
};
M.walnut.map.repeat.set(1.5, 1.5);
const matOf = n => M[n] || M.white;

const stage = document.getElementById('stage');
let renderer;
try { renderer = new THREE.WebGLRenderer({ antialias: true }); }
catch (e) { stage.innerHTML = '<p style="padding:24px;max-width:46ch">This device could not start 3D graphics, so the walkthrough can\'t run here. The Plans and Feasibility tabs still work.</p>'; return; }
renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.localClippingEnabled = true;
stage.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const SKY_DAY = new THREE.Color(0xcfd8dc), SKY_EVE = new THREE.Color(0x2b3140);
scene.background = SKY_DAY.clone();
scene.fog = new THREE.Fog(0xcfd8dc, 35, 80);
const camera = new THREE.PerspectiveCamera(70, 1, 0.05, 200);
camera.rotation.order = 'YXZ';
const hemi = new THREE.HemisphereLight(0xf2efe6, 0x8a8370, 0.75); scene.add(hemi);
const amb = new THREE.AmbientLight(0xfff3df, 0.18); scene.add(amb);
const sun = new THREE.DirectionalLight(0xffe2b8, 1.3);   // afternoon sun from the west-south-west
sun.position.set(-10, 13, 7.5); sun.target.position.set(6, 3, 3);
sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -13, right: 13, top: 13, bottom: -13, near: 1, far: 50 });
sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target);
const clip = [new THREE.Plane(new THREE.Vector3(0, -1, 0), 100)];
const root = new THREE.Group(); scene.add(root);

function box(x1, x2, y0, y1, z1, z2, m, cast = true) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(Math.max(x2 - x1, .001), Math.max(y1 - y0, .001), Math.max(z2 - z1, .001)), m);
  mesh.position.set((x1 + x2) / 2, (y0 + y1) / 2, (z1 + z2) / 2); mesh.castShadow = cast; mesh.receiveShadow = true; root.add(mesh); return mesh;
}
function plane(x1, x2, z1, z2, y, m) {
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(x2 - x1, z2 - z1), m);
  mesh.rotation.x = -Math.PI / 2; mesh.position.set((x1 + x2) / 2, y, (z1 + z2) / 2); mesh.receiveShadow = true; root.add(mesh); return mesh;
}
function cyl(x, z, r, y0, h, m, seg = 16) { const c = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), m); c.position.set(x, y0 + h / 2, z); c.castShadow = true; c.receiveShadow = true; root.add(c); return c; }
const blobGeo = new THREE.IcosahedronGeometry(1, 1);
function blob(x, y, z, s, m) { const b = new THREE.Mesh(blobGeo, m); b.position.set(x, y, z); b.scale.set(s, s * .85, s); b.castShadow = true; root.add(b); return b; }
function foliage(x1, x2, z1, z2, y, size = .22) {
  const n = Math.min(60, Math.max(3, Math.round((x2 - x1) * (z2 - z1) / (size * size) * 1.2)));
  for (let i = 0; i < n; i++) blob(x1 + rnd() * (x2 - x1), y + rnd() * size * 1.2, z1 + rnd() * (z2 - z1), size * (.6 + rnd() * .7), M.leaf[i % 4]);
}

/* ground + context */
const G0 = P.ground;
plane(-40, 40, -40, 40, G0 - 0.02, mat(0x8e9a74, { roughness: 1 }));
const SURF = [[-9, 0, -6, 12, 'asphalt'], [0, 0.9, 0.15, 3.35, 'pavers'], [0, 0.9, 3.9, 5.0, 'stepping'], [0, 0.9, 0, 0.15, 'gravel'], [0, 0.9, 3.35, 3.9, 'gravel'], [0, 0.9, 5.0, 6.096, 'gravel'],
  [0.9, 12.192, 0, 0.7, 'gravel'], [11.49, 12.192, 0.7, 6.096, 'gravel']];
for (const [x1, x2, z1, z2, m] of SURF) plane(x1, x2, z1, z2, G0 + 0.001, texMat(m, x2 - x1, z2 - z1, TILE[m]));
for (const n of P.neighbours) box(n.x1, n.x2, G0, n.h, n.z1, n.z2, M.neighbour);

/* decks, finishes */
for (const d of P.decks) {
  if (d.kind !== 'slab') { box(d.x1, d.x2, d.y - 0.2, d.y, d.z1, d.z2, M.step); continue; }
  if (!d.hole) { box(d.x1, d.x2, d.y - d.t, d.y, d.z1, d.z2, d.y > 0 ? M.slab : M.stone); continue; }
  const sh = new THREE.Shape(); sh.moveTo(d.x1, d.z1); sh.lineTo(d.x2, d.z1); sh.lineTo(d.x2, d.z2); sh.lineTo(d.x1, d.z2); sh.lineTo(d.x1, d.z1);
  const hp = new THREE.Path(); hp.absarc(d.hole.cx, d.hole.cz, d.hole.r, 0, Math.PI * 2, true); sh.holes.push(hp);
  const mesh = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: d.t, bevelEnabled: false, curveSegments: 40 }), M.slab);
  mesh.rotation.x = Math.PI / 2; mesh.position.y = d.y; mesh.castShadow = mesh.receiveShadow = true; root.add(mesh);
}
for (const s of P.slabs) { if (s.glass) { box(s.x1, s.x2, s.y - .03, s.y, s.z1, s.z2, M.glass, false); for (let x = s.x1 + .6; x < s.x2; x += .6) box(x - .02, x + .02, s.y - .06, s.y, s.z1, s.z2, M.black, false); } else box(s.x1, s.x2, s.y - s.t, s.y, s.z1, s.z2, M.slab); }
for (const f of P.finishes) plane(f.x1, f.x2, f.z1, f.z2, f.y, texMat(f.mat, f.x2 - f.x1, f.z2 - f.z1, TILE[f.mat], { roughness: f.mat === 'stoneTile' ? .45 : f.mat === 'oxide' ? .5 : f.mat === 'rug' ? 1 : .8 }));

/* walls */
function archShape(w, lo, hi) {
  const H = w.y1 - w.y0, sh = new THREE.Shape();
  sh.moveTo(lo, 0);
  for (const o of (w.open || []).filter(o => o.type === 'arch' && o.par === 0).sort((a, b) => a.a - b.a)) {
    const r = (o.b - o.a) / 2; sh.lineTo(o.a, 0); sh.lineTo(o.a, o.spring); sh.absarc(o.a + r, o.spring, r, Math.PI, 0, true); sh.lineTo(o.b, 0);
  }
  sh.lineTo(hi, 0); sh.lineTo(hi, H); sh.lineTo(lo, H); sh.lineTo(lo, 0);
  for (const o of (w.open || []).filter(o => o.type === 'arch' && o.par > 0)) {
    const r = (o.b - o.a) / 2, hole = new THREE.Path();
    hole.moveTo(o.a, o.par); hole.lineTo(o.a, o.spring); hole.absarc(o.a + r, o.spring, r, Math.PI, 0, true); hole.lineTo(o.b, o.par); hole.lineTo(o.a, o.par);
    sh.holes.push(hole);
  }
  return sh;
}
function steelFrame(alongX, w, a, b, y0, y1, glass) {
  const mid = alongX ? (w.z1 + w.z2) / 2 : (w.x1 + w.x2) / 2, t = 0.025, f = 0.035;
  const put = (u1, u2, v0, v1) => alongX ? box(u1, u2, v0, v1, mid - t, mid + t, M.black, false) : box(mid - t, mid + t, v0, v1, u1, u2, M.black, false);
  put(a, a + f, y0, y1); put(b - f, b, y0, y1); put(a, b, y1 - f, y1); put(a, b, y0, y0 + f);
  const n = Math.max(1, Math.round((b - a) / 0.45));
  for (let i = 1; i < n; i++) { const u = a + (b - a) * i / n; put(u - 0.012, u + 0.012, y0, y1); }
  if (y1 - y0 > 1.2) put(a, b, y0 + (y1 - y0) * .62 - .012, y0 + (y1 - y0) * .62 + .012);
  if (glass) { const g = alongX ? box(a, b, y0, y1, mid - .008, mid + .008, M.glass, false) : box(mid - .008, mid + .008, y0, y1, a, b, M.glass, false); g.receiveShadow = false; }
}
function rod(a, b, r, m) {
  const len = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
  const c = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 8), m);
  c.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2); c.lookAt(b[0], b[1], b[2]); c.rotateX(Math.PI / 2); c.castShadow = true; root.add(c); return c;
}
for (const w of P.walls) {
  if (w.kind === 'screen') { steelFrame(true, w, w.x1, w.x2, w.y0, w.y1, true); continue; }
  if (w.kind === 'sguard') continue;   // collision only: the stair balusters are drawn from P.stair
  if (w.kind === 'rail') {   // open balustrade: black-steel balusters, timber handrail
    const top = w.y1, ax = w.axis === 'x', c = ax ? (w.z1 + w.z2) / 2 : (w.x1 + w.x2) / 2, lo = ax ? w.x1 : w.z1, hi = ax ? w.x2 : w.z2;
    const bb = (u1, u2, y0, y1, h) => ax ? box(u1, u2, y0, y1, c - h, c + h, y1 - y0 > .2 ? M.black : M.walnut, false) : box(c - h, c + h, y0, y1, u1, u2, y1 - y0 > .2 ? M.black : M.walnut, false);
    for (let u = lo + .05; u < hi; u += .11) bb(u - .009, u + .009, w.y0, top - .05, .009);
    ax ? box(lo, hi, w.y0, w.y0 + .04, c - .02, c + .02, M.black, false) : box(c - .02, c + .02, w.y0, w.y0 + .04, lo, hi, M.black, false);
    ax ? box(lo, hi, top - .05, top, c - .04, c + .04, M.walnut) : box(c - .04, c + .04, top - .05, top, lo, hi, M.walnut);
    continue;
  }
  const alongX = w.axis === 'x', m = w.kind === 'int' || w.kind === 'guard' ? M.wallInt : M.render, lo = alongX ? w.x1 : w.z1, hi = alongX ? w.x2 : w.z2, y0 = w.y0, y1 = w.y1;
  const hasArch = (w.open || []).some(o => o.type === 'arch');
  if (hasArch) {
    const geo = new THREE.ExtrudeGeometry(archShape(w, lo, hi), { depth: w.x2 - w.x1, bevelEnabled: false, curveSegments: 20 });
    const mesh = new THREE.Mesh(geo, m); mesh.rotation.y = -Math.PI / 2; mesh.position.set(w.x2, y0, 0);
    mesh.castShadow = mesh.receiveShadow = true; root.add(mesh);
    for (const o of (w.open || []).filter(o => o.type === 'arch' && o.glazed)) {
      const r = (o.b - o.a) / 2, c = o.a + r, sh = new THREE.Shape();
      sh.moveTo(o.a, o.par); sh.lineTo(o.b, o.par); sh.lineTo(o.b, o.spring); sh.absarc(c, o.spring, r, 0, Math.PI, false); sh.lineTo(o.a, o.par);
      const gm = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: 0.016, bevelEnabled: false, curveSegments: 20 }), M.glass);
      const mx = (w.x1 + w.x2) / 2; gm.rotation.y = -Math.PI / 2; gm.position.set(mx + 0.008, y0, 0); root.add(gm);
      const bar = (z1, z2, ya, yb) => box(mx - .02, mx + .02, y0 + ya, y0 + yb, z1, z2, M.black, false);
      bar(c - .015, c + .015, o.par, o.spring + r); bar(o.a, o.b, o.spring - .015, o.spring + .015); bar(o.a, o.b, o.par, o.par + .035);
      for (const q of [.25, .75]) bar(o.a + (o.b - o.a) * q - .01, o.a + (o.b - o.a) * q + .01, o.par, o.spring);
    }
  }
  const seg = (a, b, ya, yb) => { if (hasArch || b - a < 1e-4 || yb - ya < 1e-4) return; alongX ? box(a, b, ya, yb, w.z1, w.z2, m) : box(w.x1, w.x2, ya, yb, a, b, m); };
  let cur = lo;
  for (const o of [...(w.open || [])].sort((p, q) => p.a - q.a)) {
    seg(cur, o.a, y0, y1);
    if (o.type === 'door') {
      const head = o.head || (o.slide ? 2.6 : 2.1);
      seg(o.a, o.b, y0 + head, y1);
      if (o.slide) steelFrame(alongX, w, o.a, o.b, y0, y0 + head, false);
      else if (o.side) {
        const r = leafRect(w, o), lh = head - .05; box(r.x1, r.x2, y0, y0 + lh, r.z1, r.z2, o.main ? M.gateback : w.id.startsWith('Rc') ? M.black : M.walnut);
        if (o.main) {   // vertical timber battens on both faces, like the car gate
          const alongLeafX = r.x2 - r.x1 > r.z2 - r.z1;
          for (let u = (alongLeafX ? r.x1 : r.z1) + .03; u < (alongLeafX ? r.x2 : r.z2) - .02; u += .075)
            alongLeafX ? box(u, u + .045, y0 + .03, y0 + lh - .03, r.z1 - .02, r.z2 + .02, M.walnut) : box(r.x1 - .02, r.x2 + .02, y0 + .03, y0 + lh - .03, u, u + .045, M.walnut);
        }
      }
    }
    if (o.type === 'window') { seg(o.a, o.b, y0, y0 + o.sill); seg(o.a, o.b, y0 + o.head, y1); steelFrame(alongX, w, o.a, o.b, y0 + o.sill, y0 + o.head, true); }
    if (o.type === 'gate' && o.closed) {   // vertical timber battens, as in the reference photo
      const top = y0 + o.rel_h, xb = w.x1 - 0.005;
      box(xb - 0.03, xb, y0 + 0.05, top, o.a, o.b, M.gateback);
      for (let z = o.a + 0.03; z < o.b - 0.02; z += 0.075) box(xb - 0.075, xb - 0.03, y0 + 0.05, top, z, z + 0.045, M.walnut);
      seg(o.a, o.b, top, y1);
    }
    if (o.type === 'gate' && !o.closed) seg(o.a, o.b, y0 + o.rel_h, y1);
    cur = Math.max(cur, o.b);
  }
  seg(cur, hi, y0, y1);
}

/* furniture */
function sub(f, back, v0, v1, u0 = 0, u1 = 1) {
  const W = f.x2 - f.x1, D = f.z2 - f.z1;
  if (back === 'x1' || back === 'x2') { const z1 = f.z1 + D * u0, z2 = f.z1 + D * u1; return back === 'x1' ? [f.x1 + v0, f.x1 + v1, z1, z2] : [f.x2 - v1, f.x2 - v0, z1, z2]; }
  const x1 = f.x1 + W * u0, x2 = f.x1 + W * u1; return back === 'z1' ? [x1, x2, f.z1 + v0, f.z1 + v1] : [x1, x2, f.z2 - v1, f.z2 - v0];
}
const bx = (r, y0, y1, m, cast = true) => box(r[0], r[1], y0, y1, r[2], r[3], m, cast);
function furniture(f) {
  const y0 = f.y0, y1 = y0 + f.h, m = matOf(f.mat), cx = (f.x1 + f.x2) / 2, cz = (f.z1 + f.z2) / 2, W = f.x2 - f.x1, D = f.z2 - f.z1;
  switch (f.shape) {
    case 'car': {
      box(f.x1, f.x2, y0 + .18, y0 + .85, f.z1, f.z2, M.car);
      box(f.x1 + .9, f.x2 - .7, y0 + .85, y0 + 1.42, f.z1 + .1, f.z2 - .1, M.glass);
      box(f.x1 + .95, f.x2 - .75, y0 + 1.42, y0 + 1.5, f.z1 + .12, f.z2 - .12, M.car);
      for (const x of [f.x1 + .7, f.x2 - .7]) for (const z of [f.z1 + .05, f.z2 - .05]) { const w = cyl(x, z, .31, y0, .2, M.tyre, 18); w.rotation.x = Math.PI / 2; w.position.y = y0 + .31; }
      return; }
    case 'bike': {
      for (const x of [f.x1 + .32, f.x2 - .32]) { const w = new THREE.Mesh(new THREE.TorusGeometry(.29, .06, 8, 20), M.tyre); w.position.set(x, y0 + .32, cz); w.castShadow = true; root.add(w); }
      box(f.x1 + .45, f.x2 - .5, y0 + .45, y0 + .8, cz - .15, cz + .15, M.black);
      box(f.x1 + .6, f.x1 + 1.2, y0 + .8, y0 + .9, cz - .14, cz + .14, M.gateback);
      box(f.x2 - .55, f.x2 - .45, y0 + .8, y0 + 1.1, f.z1 + .02, f.z2 - .02, M.steel); return; }
    case 'screen': {
      box(f.x1, f.x2, y0, y0 + .45, f.z1, f.z2, M.render);
      foliage(f.x1, f.x2, f.z1, f.z2, y0 + .52, .14);
      for (let x = f.x1 + .02; x < f.x2 - .02; x += .09) box(x, x + .045, y0 + .45, y1, f.z1 + .04, f.z2 - .04, M.walnut);
      box(f.x1, f.x2, y1 - .05, y1, f.z1 + .03, f.z2 - .03, M.walnut); return; }
    case 'planter': {
      box(f.x1, f.x2, y0, y1, f.z1, f.z2, M.render);
      box(f.x1 + .04, f.x2 - .04, y1 - .02, y1 + .005, f.z1 + .04, f.z2 - .04, texMat('soil', W, D, .5), false);
      foliage(f.x1 + .05, f.x2 - .05, f.z1 + .05, f.z2 - .05, y1 + .12, Math.min(.26, Math.min(W, D) * .55));
      return; }
    case 'pot': {
      cyl(cx, cz, Math.min(W, D) * .42, y0, f.h, M.terracotta, 18);
      cyl(cx, cz, .04, y0 + f.h, 1.2, M.trunk, 8);
      for (let i = 0; i < 9; i++) blob(cx + (rnd() - .5) * .55, y0 + f.h + 1.2 + rnd() * .5, cz + (rnd() - .5) * .55, .2 + rnd() * .12, M.leaf[i % 4]);
      return; }
    case 'tree': {
      cyl(cx, cz, .07, y0, f.h * .6, M.trunk, 8);
      for (let i = 0; i < 12; i++) blob(cx + (rnd() - .5) * 1.0, y0 + f.h * .6 + rnd() * f.h * .4, cz + (rnd() - .5) * 1.0, .28 + rnd() * .15, M.leaf[(i + 1) % 4]);
      for (let i = 0; i < 10; i++) blob(cx + (rnd() - .5) * 1.1, y0 + f.h * .75 + rnd() * f.h * .3, cz + (rnd() - .5) * 1.1, .06, M.flower);
      return; }
    case 'battenleaf': {
      box(f.x1, f.x2, y0 + .02, y1, f.z1 + .012, f.z2 - .012, M.gateback);
      for (let x = f.x1 + .03; x < f.x2 - .02; x += .075) box(x, x + .045, y0 + .04, y1 - .02, f.z1, f.z2, M.walnut);
      return; }
    case 'glassleaf': {
      box(f.x1, f.x2, y0, y1, f.z1 + .01, f.z2 - .01, M.glass, false);
      for (const [a, b] of [[f.x1, f.x1 + .035], [f.x2 - .035, f.x2]]) box(a, b, y0, y1, f.z1, f.z2, M.black);
      for (const y of [y0, y0 + .9, y1 - .035]) box(f.x1, f.x2, y, y + .035, f.z1, f.z2, M.black); return; }
    case 'sofa': {
      bx(sub(f, f.back, 0, f.back[0] === 'z' ? D : W), y0 + .1, y0 + .45, M.boucle);
      bx(sub(f, f.back, 0, .22), y0 + .45, y1, M.boucle);
      if (f.back[0] === 'z') for (const [a, b] of [[f.x1, f.x1 + .18], [f.x2 - .18, f.x2]]) box(a, b, y0 + .45, y0 + .62, f.z1, f.z2, M.boucle);
      box(f.x1 + .05, f.x2 - .05, y0, y0 + .1, f.z1 + .05, f.z2 - .05, M.black); return; }
    case 'chair': {
      bx(sub(f, f.back, 0, f.back[0] === 'x' ? W : D), y0 + .36, y0 + .44, M.cane);
      bx(sub(f, f.back, 0, .06), y0 + .44, y1, M.walnut);
      for (const x of [f.x1 + .03, f.x2 - .07]) for (const z of [f.z1 + .03, f.z2 - .07]) box(x, x + .04, y0, y0 + .36, z, z + .04, M.black);
      return; }
    case 'counterE': {   // counter along the east wall, cook stands to the west facing east
      box(f.x1 + .02, f.x2, y0 + .1, y1 - .04, f.z1, f.z2, M.walnut);
      box(f.x1 + .06, f.x2, y0, y0 + .1, f.z1, f.z2, M.black);
      box(f.x1, f.x2, y1 - .04, y1, f.z1, f.z2, M.quartz);
      for (let z = f.z1 + .5; z < f.z2; z += .5) box(f.x1 + .015, f.x1 + .021, y0 + .12, y1 - .06, z - .003, z + .003, M.joint, false);
      const [h1, h2] = f.hob; box(f.x1 + .1, f.x2 - .06, y1, y1 + .008, h1, h2, M.black, false);
      if (f.sink) { const [s1, s2] = f.sink; box(f.x1 + .08, f.x2 - .1, y1, y1 + .004, s1, s2, M.steel, false); cyl(f.x2 - .07, (s1 + s2) / 2, .015, y1, .32, M.nickel, 8); box(f.x2 - .3, f.x2 - .07, y1 + .3, y1 + .32, (s1 + s2) / 2 - .01, (s1 + s2) / 2 + .01, M.nickel, false); }
      box(f.x2 - .02, f.x2, y1, y0 + 2.15, f.z1, f.z2, M.stone, false);   // splashback
      return; }
    case 'overheadE': { box(f.x1, f.x2, y0, y1, f.z1, f.z2, M.white); for (let z = f.z1 + .5; z < f.z2 - .1; z += .5) box(f.x1 - .003, f.x1, y0, y1, z - .004, z + .004, M.shadowLine, false); return; }
    case 'islandSink': {
      const over = .25;
      box(f.x1, f.x2, y1 - .04, y1, f.z1 - over, f.z2, M.quartz);
      box(f.x1, f.x1 + .04, y0, y1 - .04, f.z1 - over, f.z2, M.quartz); box(f.x2 - .04, f.x2, y0, y1 - .04, f.z1 - over, f.z2, M.quartz);
      box(f.x1 + .04, f.x2 - .04, y0, y1 - .04, f.z1, f.z2, M.white);
      box(cx - .3, cx + .3, y1, y1 + .004, cz - .05, cz + .3, M.steel, false);
      cyl(cx, cz + .35, .015, y1, .35, M.nickel, 8); box(cx - .01, cx + .01, y1 + .33, y1 + .35, cz + .12, cz + .35, M.nickel, false);
      for (const x of [cx - .45, cx + .45]) { cyl(x, cz - .1, .005, y0 + 1.95, 1.05, M.black, 4); cyl(x, cz - .1, .12, y0 + 1.8, .15, M.black, 18); }
      return; }
    case 'islandZ': {   // island running along z, optional seating overhang on the west (x1) side
      const over = f.over ?? .25;
      box(f.x1 - over, f.x2, y1 - .04, y1, f.z1, f.z2, M.quartz);
      box(f.x1 - over, f.x2, y0, y1 - .04, f.z1, f.z1 + .04, M.quartz); box(f.x1 - over, f.x2, y0, y1 - .04, f.z2 - .04, f.z2, M.quartz);
      box(f.x1, f.x2, y0, y1 - .04, f.z1 + .04, f.z2 - .04, M.white);
      if (f.sink !== false) { box(cx - .2, cx + .22, y1, y1 + .004, cz - .3, cz + .3, M.steel, false);
      cyl(f.x2 - .06, cz, .015, y1, .35, M.nickel, 8); box(f.x2 - .3, f.x2 - .06, y1 + .33, y1 + .35, cz - .01, cz + .01, M.nickel, false); }
      for (let z = f.z1 + .4; z < f.z2 - .1; z += .4) box(f.x1 - .003, f.x1, y0 + .1, y1 - .06, z - .003, z + .003, M.shadowLine, false);
      for (const z of [f.z1 + .35, f.z2 - .35]) { cyl(cx - .1, z, .005, y0 + 1.95, 1.05, M.black, 4); cyl(cx - .1, z, .12, y0 + 1.8, .15, M.black, 18); }
      return; }
    case 'crockery': { box(f.x1, f.x2, y0, y1, f.z1, f.z2, M.walnut); box(f.x1, f.x2, y1, y1 + .03, f.z1, f.z2 + .02, M.quartz); return; }
    case 'shelves': { for (let k = 0; k < 4; k++) box(f.x1, f.x2, y0 + k * f.h / 3, y0 + k * f.h / 3 + .03, f.z1, f.z2, M.walnut); return; }
    case 'tall': { box(f.x1, f.x2, y0, y1, f.z1, f.z2, M.white); for (let x = f.x1 + .45; x < f.x2 - .05; x += .45) box(x - .004, x + .004, y0, y1, f.z1 - .003, f.z1, M.shadowLine, false); return; }
    case 'pooja': {
      box(f.x1, f.x2, y0, y0 + .8, f.z1, f.z2, M.walnut); box(f.x1 + .05, f.x2, y0 + .8, y0 + .82, f.z1, f.z2, M.quartz);
      box(f.x2 - .06, f.x2, y0 + .82, y0 + 1.9, f.z1, f.z2, M.walnut);
      for (const z of [f.z1 + .25, cz, f.z2 - .25]) blob(f.x2 - .15, y0 + .9, z, .05, M.accent);
      cyl(f.x1 + .12, cz, .03, y0 + .82, .08, M.nickel, 10); blob(f.x1 + .12, y0 + .93, cz, .02, mat(0xffb347, { emissive: 0xff8c1a }));
      return; }
    case 'sofabed': {
      box(f.x1, f.x2, y0 + .1, y0 + .42, f.z1, f.z2, M.boucle);
      box(f.x2 - .2, f.x2, y0 + .42, y0 + .8, f.z1, f.z2, M.boucle);
      box(f.x1 + .05, f.x2 - .05, y0, y0 + .1, f.z1 + .05, f.z2 - .05, M.black);
      box(f.x1 + .1, f.x2 - .25, y0 + .42, y0 + .5, f.z2 - .45, f.z2 - .1, M.ceramic);
      return; }
    case 'stool': {
      cyl(cx, cz, .19, y0 + .62, .1, M.boucle, 18);
      const ring = new THREE.Mesh(new THREE.TorusGeometry(.17, .012, 6, 24), M.black); ring.rotation.x = Math.PI / 2; ring.position.set(cx, y0 + .25, cz); root.add(ring);
      for (const [dx, dz] of [[-.14, -.14], [.14, -.14], [-.14, .14], [.14, .14]]) box(cx + dx - .01, cx + dx + .01, y0, y0 + .62, cz + dz - .01, cz + dz + .01, M.black);
      if (f.back === 'z1') box(f.x1 + .03, f.x2 - .03, y0 + .72, y0 + .92, f.z1 + .02, f.z1 + .1, M.boucle); else box(f.x1 + .03, f.x2 - .03, y0 + .72, y0 + .92, f.z2 - .1, f.z2 - .02, M.boucle);
      return; }
    case 'island': {
      const over = .3;
      box(f.x1, f.x2, y1 - .04, y1, f.z1, f.z2 + over, M.quartz);
      box(f.x1, f.x1 + .04, y0, y1 - .04, f.z1, f.z2 + over, M.quartz); box(f.x2 - .04, f.x2, y0, y1 - .04, f.z1, f.z2 + over, M.quartz);
      box(f.x1 + .04, f.x2 - .04, y0, y1 - .04, f.z1, f.z2 - .02, M.white);
      for (const x of [5.95, 6.65]) { cyl(x, cz + .1, .005, y0 + 1.95, 1.05, M.black, 4); cyl(x, cz + .1, .12, y0 + 1.8, .15, M.black, 18); }
      return; }
    case 'counter': {
      box(f.x1, f.x2, y0 + .1, y1 - .04, f.z1, f.z2 - .02, M.walnut);
      box(f.x1, f.x2, y0, y0 + .1, f.z1, f.z2 - .06, M.black);
      box(f.x1, f.x2, y1 - .04, y1, f.z1, f.z2, M.quartz);
      for (let x = f.x1 + .5; x < f.x2; x += .5) box(x - .003, x + .003, y0 + .12, y1 - .06, f.z2 - .021, f.z2 - .015, M.joint, false);
      box(5.95, 6.45, y1, y1 + .004, f.z1 + .1, f.z2 - .12, M.steel, false);
      cyl(6.2, f.z1 + .08, .015, y1, .32, M.nickel, 8);
      box(6.7, 7.3, y1, y1 + .008, f.z1 + .06, f.z2 - .08, M.black, false);
      box(f.x1, f.x2, y1, y0 + 1.6, f.z1, f.z1 + .02, M.stone, false);
      return; }
    case 'overhead': {
      box(f.x1, f.x2, y0, y1, f.z1, f.z2, M.white);
      for (let x = f.x1 + .6; x < f.x2 - .1; x += .6) box(x - .004, x + .004, y0, y1, f.z2, f.z2 + .003, M.shadowLine, false);
      box(6.7, 7.3, y0 - .02, y0, f.z1 + .02, f.z2 - .03, M.steel, false);
      return; }
    case 'bed': {
      const L = f.head[0] === 'x' ? W : D;
      bx(sub(f, f.head, 0, L), y0 + .08, y0 + .32, M.walnut);
      bx(sub(f, f.head, .02, L - .02, .015, .985), y0 + .32, y1, M.linen);
      bx(sub(f, f.head, .08, .5, .06, .48), y1, y1 + .12, M.ceramic); bx(sub(f, f.head, .08, .5, .52, .94), y1, y1 + .12, M.ceramic);
      bx(sub(f, f.head, L - .6, L - .05, .01, .99), y1, y1 + .02, M.sage);
      bx(sub(f, f.head, 0, .05, 0, 1), y0, y0 + 1.15, M.walnut);
      return; }
    case 'wardrobe': {
      box(f.x1, f.x2, y0, y1, f.z1, f.z2, m);
      const along = W < D, n = Math.round((along ? D : W) / .45);
      for (let i = 1; i < n; i++) { const u = along ? f.z1 + D * i / n : f.x1 + W * i / n;
        const fz = f.face === 'z1' ? f.z1 - .004 : f.z2, fx = f.face === 'x1' ? f.x1 - .004 : f.x2;
        along ? box(fx, fx + .004, y0 + .05, y1 - .05, u - .004, u + .004, M.black, false) : box(u - .004, u + .004, y0 + .05, y1 - .05, fz, fz + .004, M.black, false); }
      return; }
    case 'frames': {
      for (const [a, b, c, d, mm] of [[0, .55, .3, .95, M.walnut], [.62, 1.0, .5, 1.0, M.black], [.62, 1.0, 0, .4, M.walnut], [1.08, 1.68, .25, .85, M.black], [1.75, 2.0, .4, .75, M.walnut]]) {
        box(f.x1 + a, f.x1 + b, y0 + c, y0 + d, f.z1, f.z2, mm); box(f.x1 + a + .04, f.x1 + b - .04, y0 + c + .04, y0 + d - .04, f.z1 - .004, f.z1, M.linen, false); }
      return; }
    case 'pergola': {
      for (const z of [f.z1, f.z2 - .12]) box(f.x1, f.x2, y0, y0 + .15, z, z + .12, M.walnut);
      for (let x = f.x1; x < f.x2; x += .22) box(x, x + .06, y0 + .15, y0 + .22, f.z1 - .1, f.z2 + .1, M.walnut);
      return; }
    case 'bench': { box(f.x1, f.x2, y0, y1, f.z1, f.z2, M.render); box(f.x1, f.x2, y1, y1 + .06, f.z1, f.z2, M.walnut); box(f.x1 + .03, f.x1 + .18, y1 + .06, y1 + .45, f.z1 + .1, f.z2 - .1, M.linen); return; }
    case 'solar': {
      const pv = new THREE.Mesh(new THREE.BoxGeometry(W, .05, D), M.solar); pv.position.set(cx, y0 + .3, cz); pv.rotation.z = -0.22; pv.castShadow = true; root.add(pv);
      for (const [x, z] of [[f.x1 + .1, f.z1 + .1], [f.x2 - .1, f.z1 + .1], [f.x1 + .1, f.z2 - .1], [f.x2 - .1, f.z2 - .1]]) box(x - .03, x + .03, P.levels[3], y0 + .3 + (x < cx ? .25 : -.25), z - .03, z + .03, M.steel);
      return; }
    case 'tank': { cyl(cx, cz, W / 2, y0, f.h, M.black, 20); return; }
    case 'lines': { for (let z = f.z1; z <= f.z2; z += .35) box(f.x1, f.x2, y0, y0 + .01, z, z + .01, M.black, false); return; }
  }
  box(f.x1, f.x2, y0, y1, f.z1, f.z2, m);
}
P.furn.forEach(furniture);

/* stair balustrades and handrails (geometry comes from the plan) */
if (P.stair) {
  for (const b of P.stair.balusters) {
    for (let x = b.x1 + .055; x < b.x2 - .005; x += .11) box(x - .009, x + .009, b.y0, b.y1, b.z - .009, b.z + .009, M.black, false);
    box(b.x1, b.x2, b.y0, b.y0 + .04, b.z - .02, b.z + .02, M.black, false);
  }
  for (const pts of P.stair.rails) for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], c = pts[i];
    if (Math.hypot(c[0] - a[0], c[1] - a[1], c[2] - a[2]) > .005) rod([a[0], a[1], a[2]], [c[0], c[1], c[2]], .022, M.walnut);
  }
}

/* spiral stair */
for (const sp of P.spirals) {
  const L = sp.levels, da = 360 / sp.n, top = L[L.length - 1];
  cyl(sp.cx, sp.cz, sp.rIn, L[0], top - L[0] + 1.0, M.black, 12);
  const pts = [];
  for (let t = 0; t < L.length; t++) for (let k = 0; k < sp.n; k++) {
    if (t === L.length - 1 && k > 0) break;
    const y = L[t] + k * sp.rise;
    const a = sp.a0 + k * da;
    if (!(t === 0 && k === 0)) {   // the first-floor slab is the bottom landing
      const g = new THREE.CylinderGeometry(sp.rOut, sp.rOut, 0.05, 6, 1, false, (90 - a - da) * Math.PI / 180, da * Math.PI / 180);
      const tread = new THREE.Mesh(g, M.walnut); tread.position.set(sp.cx, y - 0.025, sp.cz); tread.castShadow = tread.receiveShadow = true; root.add(tread);
    }
    if (sp.gap.includes(k)) { pts.push(null); continue; }   // open where you step on and off
    const am = (a + da / 2) * Math.PI / 180, bxp = sp.cx + Math.cos(am) * (sp.rOut - .04), bzp = sp.cz + Math.sin(am) * (sp.rOut - .04);
    cyl(bxp, bzp, .01, y, .9, M.black, 6); pts.push([bxp, y + .9, bzp]);
  }
  for (let i = 1; i < pts.length; i++) {
    if (!pts[i - 1] || !pts[i]) continue;
    const [x1, y1, z1] = pts[i - 1], [x2, y2, z2] = pts[i], len = Math.hypot(x2 - x1, y2 - y1, z2 - z1);
    const seg = new THREE.Mesh(new THREE.CylinderGeometry(.02, .02, len, 6), M.black);
    seg.position.set((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2); seg.lookAt(x2, y2, z2); seg.rotateX(Math.PI / 2); root.add(seg);
  }
}

/* interior lights, low by day and up in the evening */
const lamps = [];
for (const r of P.rooms) {
  if (r.lv < 1 && r.id !== 'passage' && r.id !== 'carbay') continue;
  const l = new THREE.PointLight(0xffc98a, 0, 5.5, 2); l.position.set((r.x1 + r.x2) / 2, r.y + (r.lv === 3 ? 2.4 : 2.7), (r.z1 + r.z2) / 2); scene.add(l); lamps.push(l);
}
for (const [x, y, z] of (P.stair ? P.stair.lamps : [])) { const l = new THREE.PointLight(0xffc98a, 0, 5, 2); l.position.set(x, y, z); scene.add(l); lamps.push(l); }

root.traverse(o => { if (o.isMesh) o.material.clippingPlanes = clip; });

const figure = new THREE.Group();
{ const b = new THREE.Mesh(new THREE.CylinderGeometry(.17, .2, 1.15, 16), M.person); b.position.y = .75; b.castShadow = true;
  const h = new THREE.Mesh(new THREE.SphereGeometry(.13, 16, 12), M.skin); h.position.y = 1.55;
  const n = new THREE.Mesh(new THREE.BoxGeometry(.12, .08, .08), M.accent); n.position.set(0, 1.2, -.2);
  figure.add(b, h, n); figure.visible = false; scene.add(figure); }

let evening = false;
function setTime(e) {
  evening = e;
  sun.intensity = e ? 0.12 : 1.3; sun.color.set(e ? 0xff9a5a : 0xffe2b8);
  hemi.intensity = e ? 0.16 : 0.75; amb.intensity = e ? 0.05 : 0.18;
  scene.background.copy(e ? SKY_EVE : SKY_DAY); scene.fog.color.copy(scene.background);
  lamps.forEach(l => l.intensity = e ? 1.1 : 0.18);
  const b = document.getElementById('bTime'); b.textContent = e ? 'Afternoon' : 'Evening'; b.classList.toggle('on', e);
}

/* ---------------- walker ---------------- */
const me = { x: P.start.x, z: P.start.z, feet: P.ground, vy: 0, yaw: P.start.yaw, pitch: -0.05 };
let overhead = false;
const keys = {}, joyVec = { x: 0, y: 0 };
function tryMove(dx, dz) {
  if (canStand(P, S, me.x + dx, me.z, me.feet, R)) me.x += dx;
  if (canStand(P, S, me.x, me.z + dz, me.feet, R)) me.z += dz;
}
function teleport(x, z, y, yaw) {
  const f = floorAt(P, x, z, y ?? me.feet);
  if (!canStand(P, S, x, z, f, R)) return false;
  me.x = x; me.z = z; me.feet = f; me.vy = 0; if (yaw !== undefined) me.yaw = yaw; return true;
}
function update(dt) {
  let fwd = 0, side = 0;
  if (keys.KeyW || keys.ArrowUp) fwd += 1; if (keys.KeyS || keys.ArrowDown) fwd -= 1;
  if (keys.KeyD || keys.ArrowRight) side += 1; if (keys.KeyA || keys.ArrowLeft) side -= 1;
  fwd += -joyVec.y; side += joyVec.x;
  const len = Math.hypot(fwd, side); if (len > 1) { fwd /= len; side /= len; }
  const speed = (keys.ShiftLeft || keys.ShiftRight) ? 2.6 : 1.35;
  const fx = -Math.sin(me.yaw), fz = -Math.cos(me.yaw), rx = Math.cos(me.yaw), rz = -Math.sin(me.yaw);
  const vx = (fx * fwd + rx * side) * speed * dt, vz = (fz * fwd + rz * side) * speed * dt;
  const n = Math.ceil(Math.hypot(vx, vz) / 0.04) || 1;
  for (let i = 0; i < n; i++) {
    tryMove(vx / n, vz / n);
    const fl = floorAt(P, me.x, me.z, me.feet);
    if (fl > me.feet) { me.feet = fl; me.vy = 0; }
  }
  const fl = floorAt(P, me.x, me.z, me.feet);
  if (fl < me.feet) { me.vy -= 9.8 * dt; me.feet = Math.max(fl, me.feet + me.vy * dt); if (me.feet === fl) me.vy = 0; }
}
let eyeY = null;
const tmp = new THREE.Vector3();
function placeCamera(dt) {
  eyeY = eyeY === null ? me.feet + EYE : eyeY + (me.feet + EYE - eyeY) * Math.min(1, dt * 12);
  if (!overhead) { camera.position.set(me.x, eyeY, me.z); camera.rotation.set(me.pitch, me.yaw, 0); clip[0].constant = 100; }
  else {
    const fx = -Math.sin(me.yaw), fz = -Math.cos(me.yaw);
    tmp.set(me.x - fx * 3.6, me.feet + 6.8, me.z - fz * 3.6);
    camera.position.lerp(tmp, Math.min(1, dt * 6));
    camera.lookAt(me.x + fx * .8, me.feet + .6, me.z + fz * .8);
    figure.position.set(me.x, me.feet, me.z); figure.rotation.y = me.yaw;
    clip[0].constant = me.feet + 1.45;
  }
}
function setView(o) {
  overhead = o; figure.visible = o;
  document.getElementById('cross').hidden = o;
  const b = document.getElementById('bView'); b.textContent = o ? 'Eye level' : 'Overhead'; b.classList.toggle('on', o);
  if (o && document.pointerLockElement) document.exitPointerLock();
  if (o) camera.position.set(me.x + Math.sin(me.yaw) * 3.6, me.feet + 6.8, me.z + Math.cos(me.yaw) * 3.6);
}

/* ---------------- input ---------------- */
const isTouch = matchMedia('(pointer: coarse)').matches;
if (isTouch) {
  document.body.classList.add('touch'); document.getElementById('joy').hidden = false;
  document.getElementById('helpKeys').innerHTML = '<dt>Left stick</dt><dd>Walk (stairs climb automatically)</dd><dt>Drag elsewhere</dt><dd>Look around</dd><dt>Next stop</dt><dd>Guided route through the house</dd><dt>Minimap</dt><dd>Tap a spot to jump there</dd>';
}
addEventListener('keydown', e => {
  if (active !== 'walk' || cine || /INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName || '')) return;
  keys[e.code] = true;
  if (e.code === 'KeyV') setView(!overhead);
  if (e.code === 'KeyL') setTime(!evening);
  if (e.code === 'KeyR') reset();
  if (e.code === 'KeyN') tourStep(1);
  if (e.code === 'KeyB') tourStep(-1);
  if (e.code.startsWith('Arrow') || e.code === 'Space') e.preventDefault();
});
addEventListener('keyup', e => { keys[e.code] = false; });
addEventListener('blur', () => { for (const k in keys) keys[k] = false; });
const canvas = renderer.domElement;
canvas.addEventListener('click', () => {
  hideHelp();
  if (!overhead && !isTouch && canvas.requestPointerLock) { try { const p = canvas.requestPointerLock(); if (p && p.catch) p.catch(() => {}); } catch (_) {} }
});
document.addEventListener('mousemove', e => { if (document.pointerLockElement === canvas) look(e.movementX, e.movementY); });
let drag = null;
canvas.addEventListener('pointerdown', e => { if (document.pointerLockElement === canvas) return; drag = { id: e.pointerId, x: e.clientX, y: e.clientY }; try { canvas.setPointerCapture(e.pointerId); } catch (_) {} });
canvas.addEventListener('pointermove', e => { if (!drag || drag.id !== e.pointerId) return; look((e.clientX - drag.x) * 1.4, (e.clientY - drag.y) * 1.4); drag.x = e.clientX; drag.y = e.clientY; });
const endDrag = e => { if (drag && drag.id === e.pointerId) drag = null; };
canvas.addEventListener('pointerup', endDrag); canvas.addEventListener('pointercancel', endDrag);
function look(dx, dy) { me.yaw -= dx * .0026; if (!overhead) me.pitch = Math.max(-1.35, Math.min(1.35, me.pitch - dy * .0026)); }
const joy = document.getElementById('joy'), knob = joy.querySelector('i');
let joyId = null;
joy.addEventListener('pointerdown', e => { joyId = e.pointerId; try { joy.setPointerCapture(e.pointerId); } catch (_) {} joyMove(e); hideHelp(); e.preventDefault(); });
joy.addEventListener('pointermove', e => { if (e.pointerId === joyId) joyMove(e); });
const joyEnd = e => { if (e.pointerId !== joyId) return; joyId = null; joyVec.x = joyVec.y = 0; knob.style.transform = ''; };
joy.addEventListener('pointerup', joyEnd); joy.addEventListener('pointercancel', joyEnd);
function joyMove(e) {
  const r = joy.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  let dx = (e.clientX - cx) / (r.width / 2), dy = (e.clientY - cy) / (r.height / 2);
  const l = Math.hypot(dx, dy); if (l > 1) { dx /= l; dy /= l; }
  joyVec.x = dx; joyVec.y = dy; knob.style.transform = `translate(${dx * 36}px,${dy * 36}px)`;
}

/* ---------------- HUD ---------------- */
const help = document.getElementById('help');
function hideHelp() { help.hidden = true; }
document.getElementById('bGo').addEventListener('click', () => { hideHelp(); reset(); });
document.getElementById('bHelp').addEventListener('click', () => { help.hidden = !help.hidden; });
document.getElementById('bView').addEventListener('click', () => setView(!overhead));
document.getElementById('bTime').addEventListener('click', () => setTime(!evening));
let tourIdx = 0;
function reset() { teleport(P.start.x, P.start.z, P.ground, P.start.yaw); me.pitch = -0.05; tourIdx = 0; eyeY = null; }
const toast = document.getElementById('toast'); let toastT;
function say(t) { toast.textContent = t; toast.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(() => toast.classList.remove('show'), 1800); }
function goRoom(r) {
  const [x, z, y] = r.spawn, cx = (r.x1 + r.x2) / 2, cz = (r.z1 + r.z2) / 2;
  let yaw = Math.atan2(-(cx - x), -(cz - z)); if (!isFinite(yaw) || (Math.abs(cx - x) < .05 && Math.abs(cz - z) < .05)) yaw = me.yaw;
  if (r.id === 'road') yaw = -Math.PI / 2;
  teleport(x, z, y, yaw); me.pitch = r.id === 'road' ? 0.15 : -0.08; eyeY = null; hideHelp();
}
const jump = document.getElementById('jump');
{
  const groups = [['Outside & stilt', r => r.lv <= 0], ['First floor', r => r.lv === 1], ['Second floor', r => r.lv === 2], ['Roof', r => r.lv === 3]];
  jump.innerHTML = '<option value="">Go to room…</option>' + groups.map(([g, fn]) => `<optgroup label="${g}">${P.rooms.filter(fn).map(r => `<option value="${r.id}">${r.name}</option>`).join('')}</optgroup>`).join('');
}
jump.addEventListener('change', () => { const r = P.rooms.find(q => q.id === jump.value); jump.value = ''; if (r) { goRoom(r); tourIdx = Math.max(0, P.tour.indexOf(r.id)); } });
function tourStep(d) {
  tourIdx = (tourIdx + d + P.tour.length) % P.tour.length;
  const r = P.rooms.find(q => q.id === P.tour[tourIdx]); goRoom(r); expanded = true; curRoom = undefined;
  say(`Stop ${tourIdx + 1} of ${P.tour.length} · ${r.name}`);
}
document.getElementById('bNext').addEventListener('click', () => tourStep(1));
document.getElementById('bPrev').addEventListener('click', () => tourStep(-1));

const rcName = document.getElementById('rcName'), rcDims = document.getElementById('rcDims'), rcNotes = document.getElementById('rcNotes'), rcMore = document.getElementById('rcMore'), rcLevel = document.getElementById('rcLevel');
let curRoom = null, expanded = false, lastLv = -1;
function showRoom(r) {
  const lv = levelOf(P, me.feet);
  rcLevel.textContent = r && (r.id === 'stairs' || r.id === 'spiral') ? `Stairs · ${LEVEL_NAMES[lv]}` : (me.feet < 1 ? (r && r.lv === 0 ? LEVEL_NAMES[0] : 'Outside') : LEVEL_NAMES[lv]);
  rcName.textContent = r ? r.name : 'Outside';
  const outdoor = !r || ['road', 'front', 'sidepath', 'rear', 'stairs', 'spiral'].includes(r.id);
  rcDims.textContent = r && !outdoor ? dimTxt(r.x2 - r.x1, r.z2 - r.z1) : r && r.id === 'stairs' ? 'U-turn on every floor · 1.0 m flights · 17 × 185 mm risers · 250 mm treads' : r && r.id === 'spiral' ? '1.8 m diameter · 16 × 197 mm risers per floor · 22.5° treads' : '';
  const notes = r ? r.notes : [];
  rcNotes.innerHTML = notes.slice(0, expanded ? notes.length : 1).map(n => `<p>${n}</p>`).join('');
  rcMore.hidden = notes.length <= 1;
  rcMore.textContent = expanded ? 'Show less' : `Read the design notes (${notes.length - 1} more)`;
}
rcMore.addEventListener('click', () => { expanded = !expanded; showRoom(curRoom); });
function checkRoom() {
  const r = roomAt(P, me.x, me.z, me.feet), lv = levelOf(P, me.feet);
  if (r !== curRoom || lv !== lastLv) {
    if (curRoom !== undefined && r !== curRoom && r) { expanded = false; say(r.name); }
    curRoom = r; lastLv = lv; showRoom(r); mapBase = null;
  }
}

/* ---------------- minimap ---------------- */
const mini = document.getElementById('mini'), mg = mini.getContext('2d');
const MX0 = -2.4, MX1 = 12.5, MZ0 = -0.35, MZ1 = 6.45;
const toPx = (x, z) => [(x - MX0) / (MX1 - MX0) * mini.width, (z - MZ0) / (MZ1 - MZ0) * mini.height];
const SC = mini.width / (MX1 - MX0);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
let mapBase = null;
function rectPx(g, x1, x2, z1, z2, fill) { const [a, b] = toPx(x1, z1); g[fill ? 'fillRect' : 'strokeRect'](a, b, (x2 - x1) * SC, (z2 - z1) * SC); }
const wallById = Object.fromEntries(P.walls.map(w => [w.id, w]));
function drawMapBase(lv) {
  const c = document.createElement('canvas'); c.width = mini.width; c.height = mini.height; const g = c.getContext('2d');
  g.fillStyle = css('--line'); const [rx] = toPx(0, 0); g.fillRect(0, 0, rx, c.height);
  const fp = P.footprint;
  g.fillStyle = css('--stone-soft'); rectPx(g, fp.x1, fp.x2, fp.z1, fp.z2, true);
  const FILL = { oxide: '--oxide-soft', wet: '--wet', wetdark: '--wet', terracotta: '--line', lawn: '--oxide-soft', checker: '--line' };
  for (const f of P.finishes.filter(f => f.lv === lv && f.mat !== 'rug')) { g.fillStyle = css(FILL[f.mat] || '--stone-soft'); rectPx(g, f.x1, f.x2, f.z1, f.z2, true); }
  g.strokeStyle = css('--muted'); g.lineWidth = 1;
  for (const d of P.decks.filter(d => d.kind === 'step' && d.y > P.levels[lv] - 1.6 && d.y < P.levels[lv] + 1.6)) rectPx(g, d.x1, d.x2, d.z1, d.z2, false);
  if (lv >= 1) for (const sp of P.spirals) { const [px, py] = toPx(sp.cx, sp.cz); g.beginPath(); g.arc(px, py, sp.rOut * SC, 0, 7); g.stroke();
    for (let k = 0; k < sp.n; k++) { const a = (sp.a0 + k * 360 / sp.n) * Math.PI / 180; g.beginPath(); g.moveTo(px, py); g.lineTo(px + Math.cos(a) * sp.rOut * SC, py + Math.sin(a) * sp.rOut * SC); g.stroke(); } }
  g.strokeStyle = css('--walnut'); g.lineWidth = 1.2;
  for (const f of P.furn.filter(f => f.lv === lv && f.solid !== false)) rectPx(g, f.x1, f.x2, f.z1, f.z2, false);
  for (const b of S) {
    const w = wallById[b.id] || wallById[b.id.replace(/-leaf$/, '')]; if (!w || !onLevel(lv, w)) continue;
    g.fillStyle = w.kind === 'parapet' || w.kind === 'compound' || w.kind === 'rail' || w.kind === 'sguard' || w.kind === 'screen' ? css('--muted') : css('--ink');
    const [a, c2] = toPx(b.x1, b.z1); g.fillRect(a, c2, Math.max(1.5, (b.x2 - b.x1) * SC), Math.max(1.5, (b.z2 - b.z1) * SC));
  }
  return c;
}
function drawMap() {
  const lv = levelOf(P, me.feet);
  if (!mapBase) { mapBase = drawMapBase(lv); document.getElementById('mapLevel').textContent = LEVEL_SHORT[lv]; }
  mg.clearRect(0, 0, mini.width, mini.height); mg.drawImage(mapBase, 0, 0);
  if (curRoom && curRoom.id !== 'road') { mg.strokeStyle = css('--terracotta'); mg.lineWidth = 3; rectPx(mg, curRoom.x1, curRoom.x2, curRoom.z1, curRoom.z2, false); }
  const [px, py] = toPx(me.x, me.z), ang = Math.atan2(-Math.cos(me.yaw), -Math.sin(me.yaw));
  mg.save(); mg.translate(px, py); mg.rotate(ang);
  mg.fillStyle = 'rgba(180,89,58,.3)'; mg.beginPath(); mg.moveTo(0, 0); mg.arc(0, 0, 34, -.6, .6); mg.fill();
  mg.fillStyle = css('--bad'); mg.beginPath(); mg.moveTo(11, 0); mg.lineTo(-7, -7); mg.lineTo(-3, 0); mg.lineTo(-7, 7); mg.closePath(); mg.fill();
  mg.restore();
}
matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', () => { mapBase = null; });
new MutationObserver(() => { mapBase = null; }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
mini.addEventListener('click', e => {
  const r = mini.getBoundingClientRect();
  const x = MX0 + (e.clientX - r.left) / r.width * (MX1 - MX0), z = MZ0 + (e.clientY - r.top) / r.height * (MZ1 - MZ0);
  const inside = x > 0.9 && x < 11.49 && z > 0.7 && z < 6.096;
  if (!teleport(x, z, inside ? P.levels[levelOf(P, me.feet)] : P.ground)) say('Can\'t stand there (wall or furniture)');
  hideHelp();
});

/* ---------------- cinematic tour: an automatic, smooth walk along a real route through every room ---------------- */
const CI = P.cine;
let cine = null;
const cineCap = document.getElementById('cineCap'), cineName = document.getElementById('cineName'), cineLine = document.getElementById('cineLine');
const cum = [0];
if (CI) for (let i = 1; i < CI.pts.length; i++) { const a = CI.pts[i - 1], b = CI.pts[i]; cum.push(cum[i - 1] + Math.hypot(b[0] - a[0], b[2] - a[2], (b[1] - a[1]) * .6)); }
function cineAt(d) {
  const L = cum[cum.length - 1]; d = Math.max(0, Math.min(L, d));
  let lo = 0, hi = cum.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (cum[m] <= d) lo = m; else hi = m; }
  const a = CI.pts[lo], b = CI.pts[hi], t = cum[hi] > cum[lo] ? (d - cum[lo]) / (cum[hi] - cum[lo]) : 0;
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
}
const angDiff = (a, b) => { let d = b - a; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; };
function cineCaption(r) {
  if (!r) { cineCap.classList.remove('show'); return; }
  cineName.textContent = r.name;
  const n = (r.notes && r.notes[0]) || ''; cineLine.textContent = n.length > 150 ? n.slice(0, n.lastIndexOf(' ', 147)) + '…' : n;
  cineCap.classList.remove('show'); void cineCap.offsetWidth; cineCap.classList.add('show');
}
function startCine() {
  if (!CI) return;
  if (document.pointerLockElement) document.exitPointerLock();
  setView(false); hideHelp();
  cine = { d: 0, next: 1, dwell: 2.5, pan: 0, yaw: -Math.PI / 2, pitch: 0.02, y: CI.pts[0][1] + EYE, saved: { exp: renderer.toneMappingExposure, fov: camera.fov, evening } };
  setTime(false);
  renderer.toneMappingExposure = 1.15; camera.fov = 56; camera.updateProjectionMatrix();
  sun.intensity = 1.55; hemi.intensity = .62; amb.intensity = .12; lamps.forEach(l => l.intensity = .55);
  document.body.classList.add('cine');
  cineCaption(P.rooms.find(r => r.id === CI.stops[0].id));
  document.getElementById('bCine').classList.add('on');
}
function stopCine() {
  if (!cine) return;
  const [x, y, z] = cineAt(cine.d), sv = cine.saved; cine = null;
  renderer.toneMappingExposure = sv.exp; camera.fov = sv.fov; camera.updateProjectionMatrix(); setTime(sv.evening);
  document.body.classList.remove('cine'); cineCap.classList.remove('show');
  document.getElementById('bCine').classList.remove('on');
  teleport(x, z, y, me.yaw); eyeY = null; curRoom = undefined;
}
function cineFrame(dt) {
  const c = cine, L = cum[cum.length - 1], SPEED = 0.85;
  const stopD = c.next < CI.stops.length ? cum[CI.stops[c.next].i] : L;
  let stopRoom = null;
  if (c.dwell > 0) { c.dwell -= dt; c.pan += dt; }
  else {
    c.d = Math.min(stopD, c.d + SPEED * dt);
    if (c.d >= stopD - 1e-4) {
      if (c.next >= CI.stops.length) { stopCine(); say('End of the tour'); return; }
      stopRoom = P.rooms.find(r => r.id === CI.stops[c.next].id); c.next++; c.dwell = 3.6; c.pan = 0; cineCaption(stopRoom); c.room = stopRoom;
    }
  }
  const p = cineAt(c.d), q = cineAt(c.d + 1.4);
  let ty = Math.atan2(-(q[0] - p[0]), -(q[2] - p[2]));
  let tp = Math.max(-.32, Math.min(.25, Math.atan2(q[1] - p[1], Math.hypot(q[0] - p[0], q[2] - p[2]) + .01) * .8)) - .04;
  if (c.dwell > 0 && c.room) {               // pause in each room: slow look around towards its centre
    const rx = (c.room.x1 + c.room.x2) / 2 - p[0], rz = (c.room.z1 + c.room.z2) / 2 - p[2];
    if (Math.hypot(rx, rz) > .6 && c.room.id !== 'road') ty = Math.atan2(-rx, -rz);
    ty += Math.sin(c.pan * .55) * .45; tp = -.05;
  }
  if (Math.hypot(q[0] - p[0], q[2] - p[2]) < .05 && c.dwell <= 0) ty = c.yaw;
  c.yaw += angDiff(c.yaw, ty) * Math.min(1, dt * 1.6);
  c.pitch += (tp - c.pitch) * Math.min(1, dt * 1.6);
  c.y += (p[1] + EYE - c.y) * Math.min(1, dt * 5);
  camera.position.set(p[0], c.y + Math.sin(c.d * 4.2) * .006, p[2]); camera.rotation.set(c.pitch, c.yaw, 0); clip[0].constant = 100;
  me.x = p[0]; me.z = p[2]; me.feet = p[1]; me.yaw = c.yaw;
}
document.getElementById('bCine').addEventListener('click', () => cine ? stopCine() : startCine());
addEventListener('keydown', e => { if (active !== 'walk') return; if (e.code === 'KeyC' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName || '')) cine ? stopCine() : startCine(); else if (cine && e.code === 'Escape') stopCine(); });
canvas.addEventListener('pointerdown', () => { if (cine) stopCine(); }, true);

/* ---------------- loop ---------------- */
function resize() { const w = stage.clientWidth, h = stage.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(stage); resize();
let last = performance.now();
function frame(t) {
  const dt = Math.min(.05, (t - last) / 1000); last = t;
  if (active === 'walk') { if (cine) cineFrame(dt); else { update(dt); placeCamera(dt); } checkRoom(); drawMap(); renderer.render(scene, camera); }
  requestAnimationFrame(frame);
}
setView(false); setTime(false); reset(); curRoom = undefined;
requestAnimationFrame(frame);
})();
