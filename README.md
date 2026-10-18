# chikkalasandra-house-plan-draft

Draft design and walkable 3D blockout for a 20 × 40 ft west-facing home in Chikkalasandra, Bengaluru:
stilt parking, two floors and a roof garden, with Vastu and structural notes.

**Provisional – not for construction.** Setbacks, ground coverage and the structure must be confirmed by a
licensed architect and structural engineer (with a soil test) before use.

## Open it

Open `index.html` in a browser. It is a single self-contained page with three tabs:

- **Walk** – a 3D walkthrough. WASD / arrows to walk, mouse to look, `N` for the next tour stop,
  `V` overhead view, `L` evening light. On phones, use the on-screen joystick.
- **Plans** – dimensioned plans for all four levels, the street elevation, and room and door schedules.
- **Feasibility** – regulations, Vastu check, structure notes, compromises and the walk-test results.

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | Built page (open this) |
| `src/plan.json` | Single source of truth: walls, openings, stairs, furniture, rooms, all in metres |
| `src/src.html`, `src/main.js` | Page shell and 3D / drawing code (Three.js r128 from cdnjs) |
| `src/shared.js` | Walking, collision and room lookup, shared by the page and the test |
| `tools/generate_plan.py` | Generates `src/plan.json` |
| `tools/build.py` | Inlines everything into `index.html` |
| `tools/verify.js` | 3D walk test: reachability (0.44 m and 0.60 m walkers), overlaps, stair headroom |

## Rebuild

```sh
python3 tools/generate_plan.py   # writes src/plan.json
python3 tools/build.py           # writes index.html
node tools/verify.js             # walk test
```

Coordinates: x runs west → east from the road boundary, z runs north → south from the north boundary, y is height.
