# Template Index

Each template provides a starting structure, function statements, and a small library of illustrative failure chains for a specific domain. They're starting points meant to be edited with the user's real information — not authoritative data for any specific product.

| Slug | Applies to | Match on keywords like |
|---|---|---|
| `electronic-electrical` | DFMEA (primarily), PFMEA for electronics assembly | ECU, controller, sensor, wiring harness, PCB, circuit, connector |
| `mechanical-assembly` | DFMEA, PFMEA | gear, bearing, fastener, shaft, housing, assembly, press-fit |
| `surface-treatment` | PFMEA | plating, heat treatment, anodizing, quenching, case hardening |
| `painting-coating` | PFMEA | paint, coating, e-coat, powder coat, spray |
| `generic-fmea` | DFMEA, PFMEA | fallback when nothing else matches |

## Selection logic

1. If the user specified a template explicitly, use it — skip keyword matching.
2. Otherwise, scan `item_name`, `process_name`, and any product description for the keywords above (case-insensitive, partial match is fine).
3. If more than one template matches, ask the user which is the better fit rather than guessing.
4. If nothing matches, use `generic-fmea`.

## Adding a new template

Each template folder needs:
- `intro.md` — one paragraph on what the template covers and when to use it.
- `template.json` — structured starter data. See any existing `template.json` for the schema: `slug`, `name`, `applicable_types`, `keywords`, `structure_example`, `function_example`, `failure_chains_starter[]` (each with `fe`, `fm`, `fc`, `s_hint`, `o_hint`, `d_hint`, `pc`, `dc`, and for PFMEA a `category_4m`).
