# chikkalasandra-house-plan-draft

Draft design and walkable 3D blockout for a 20 × 40 ft west-facing home in Chikkalasandra, Bengaluru:
stilt parking, two floors and a roof garden, with Vastu and structural notes.

**Provisional – not for construction.** Setbacks, ground coverage and the structure must be confirmed by a
licensed architect and structural engineer (with a soil test) before use.

## Open it

Open `index.html` in a browser. It is a single self-contained page with three tabs:

- **Walk** – a 3D walkthrough. WASD / arrows to walk, mouse to look, `N` for the next tour stop,
  `V` overhead view, `L` evening light. On phones, use the on-screen joystick.
  **Cinematic tour** (or `C`) plays an automatic walk through every room for screen recording.
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
| `tools/cine.js` | Computes the cinematic route (a real walkable path through every tour stop) into `src/plan.json` |
| `tools/export_obj.py` | Exports the model as OBJ + MTL into `model/` |
| `model/` | `chikkalasandra_house.obj` + `.mtl` for Blender, Twinmotion, D5 Render or Lumion (metres, Y up) |

## Rebuild

```sh
python3 tools/generate_plan.py   # writes src/plan.json
node tools/cine.js               # adds the cinematic route to src/plan.json
python3 tools/build.py           # writes index.html
node tools/verify.js             # walk test
python3 tools/export_obj.py src/plan.json model/chikkalasandra_house   # OBJ + MTL
```

Coordinates: x runs west → east from the road boundary, z runs north → south from the north boundary, y is height.
