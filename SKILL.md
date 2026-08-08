---
name: pfmea-dfmea
description: Use when the user needs a Design FMEA (DFMEA) or Process FMEA (PFMEA) analysis, mentions FMEA / potential failure modes / failure effects / failure causes / severity-occurrence-detection (S/O/D) scoring / Action Priority (AP) / seven-step approach / P-Diagram / control plan / special characteristics (CC/SC), or asks for an FMEA report in an IATF 16949 / APQP context. Do not use for 8D / corrective-action reports, SPC control charts, or Cpk/Ppk capability studies — those are separate concerns.
---

# PFMEA / DFMEA Skill

Generates Design FMEA (DFMEA) and Process FMEA (PFMEA) analyses that follow the **AIAG & VDA FMEA Handbook (2019)** seven-step approach, and exports them as `.xlsx` and `.docx` reports.

This skill is an independent implementation of the public AIAG & VDA methodology — it is not affiliated with, endorsed by, or sourced from AIAG or VDA, and it does not reproduce their copyrighted handbook text or figures. See `references/` for the working tables and logic this skill actually uses.

## 1. Scope

| Use this skill for | Use something else for |
|---|---|
| DFMEA — potential failure modes in a **design** | 8D / SCAR corrective-action reports |
| PFMEA — potential failure modes in a **manufacturing process** | SPC control charts |
| FMEA risk scoring (S/O/D + Action Priority) | Process capability (Cpk/Ppk) studies |
| FMEA report generation (xlsx + docx) | Pure conceptual questions about "what is FMEA" — just answer directly, no report needed |

## 2. DFMEA vs. PFMEA — how to decide

| Signal in the user's request | Type |
|---|---|
| "product design", "component design", "DFMEA" | DFMEA |
| "manufacturing process", "production line", "PFMEA", "operation/station" | PFMEA |
| Both mentioned, or unclear | **Ask**: "Is this a Design FMEA (DFMEA) for a product/component, or a Process FMEA (PFMEA) for a manufacturing process?" |

Never guess silently on this — DFMEA and PFMEA use different structural/functional analysis models (structure tree + P-Diagram vs. process flow + 4M) and picking wrong means redoing steps 2–4.

## 3. Core constraints (do not violate)

1. Use the **2019 seven-step approach** (Planning → Structure Analysis → Function Analysis → Failure Analysis → Risk Analysis → Optimization → Results Documentation). Do not use the older "5T + 6-step" model.
2. Use **Action Priority (AP: High/Medium/Low)**, not RPN (Severity × Occurrence × Detection). The 2019 handbook explicitly retired RPN thresholds — never output or reference an RPN number.
3. S/O/D scores must come from the standard tables in `references/sod_scoring_tables.md` — never assign a score "by feel." Scores are integers 1–10 (never 0).
4. DFMEA and PFMEA severity ratings for the same failure effect **must match** (the handbook requires this — severity describes the effect on the end user/vehicle, which doesn't change based on which FMEA type you're doing).
5. Failure must be expressed as a three-level chain: **Failure Effect (FE) → Failure Mode (FM) → Failure Cause (FC)**. Never skip a level or merge two levels into one field.
6. PFMEA causes must be classified by 4M (Man/Machine/Material/Method) or 6M (+ Environment/Measurement) — don't leave a cause un-categorized.
7. Keep **Prevention Controls (PC)** and **Detection Controls (DC)** in separate fields — never combine "how we prevent it" and "how we'd catch it" into one control statement.
8. Any failure effect with **S = 9 or 10** and **AP = H or M** should be flagged for management-level review in the output.
9. Never fabricate data the user hasn't given you: warranty return rates, customer complaint counts, Cpk/Ppk, or field failure history. If auto-fill needs one of these and it wasn't provided, state the assumption explicitly rather than inventing a number.

## 4. Workflow

### Step 1 — Collect required fields

Ask only for what's missing; don't re-ask for things already stated.

**Common to both:**

| Field | Required | Notes |
|---|---|---|
| `fmea_type` | yes | DFMEA or PFMEA |
| `item_name` | yes | product, component, or process under analysis |
| `customer` | yes | can be "internal" if there's no external customer |
| `project_no` | optional | |
| `team_members` | optional | |
| `template` | optional | auto-matched from `item_name`/keywords if omitted |

**DFMEA only:** `system_level` (vehicle/system/subsystem/component/part), `design_responsibility` (in-house/supplier/joint), `interfaces` (optional — mechanical/electrical/software).

**PFMEA only:** `process_name`, `process_steps` (an ordered list — ask for at least 3), `manufacturing_site` (optional).

### Step 2 — Pick a template

Match `item_name` / process keywords against `templates/INDEX.md`:

1. If the user gave `template` explicitly, use it.
2. Otherwise match by keyword (electronics/PCB/sensor/wiring harness → `electronic-electrical`; gears/bearings/fasteners/shafts/housings → `mechanical-assembly`; plating/heat-treat/anodizing → `surface-treatment`; painting/coating/e-coat → `painting-coating`).
3. If nothing matches, fall back to `generic-fmea`.

Each template supplies a starting structure tree/process flow, a small library of realistic failure chains for that domain, and S/O/D starting points — all meant to be edited, not treated as truth for the user's actual product.

### Step 3 — Build or collect failure chains

Two modes:

- **User has real data** (they've described actual failures, complaints, or known risks in the conversation): build FE→FM→FC chains directly from what they said. Score S/O/D based on the standard tables and their description — don't lower severity just because it's inconvenient.
- **User wants a starting example / "fill it in for me"**: use `auto_fill = true`. Pull failure-chain patterns from the matched template and `references/failure_chain_examples.md`, and score them per `references/sod_scoring_tables.md`'s guidance (see §4.1 below). Make clear in your response that these are illustrative starting points that need engineering review, not measured data.

Each failure chain needs: `fe`, `fm`, `fc`, `s`, `o`, `d`, `pc` (prevention control), `dc` (detection control). PFMEA chains should also carry `process_step` and the 4M/6M category of the cause.

#### 4.1 Auto-fill scoring heuristics (only when auto_fill=true and no real data exists)

- **S**: infer from how serious the stated failure effect sounds (safety/regulatory → 9–10; loss of primary function → 7–8; loss of secondary function → 5–6; cosmetic/annoyance → 1–4), per the table in `references/sod_scoring_tables.md`.
- **O**: default to the "mature technology, similar application" band (5–6) unless the chain implies otherwise (brand-new technology → 8–10; well-proven with strong preventive control → 1–3).
- **D**: default to "validated test method, pass/fail" (6) unless a stronger or weaker detection method is implied.
- **AP**: computed, never guessed — apply the rule table in `references/sod_scoring_tables.md` §3.

### Step 4 — Build the analysis: one-shot or incremental

Two ways to assemble the chains, pick based on how the conversation is going:

**One-shot** — you already have all the chains (from a template, from auto-fill, or the user dumped everything at once). Write them straight to a `chains.json` file and skip to Step 5.

**Incremental** (preferred when the user is thinking through failure modes one at a time, revising scores as the discussion develops, or wants to track action-item status over a longer session) — use `scripts/fmea_project.py`, a stateful tracker that persists the project to a JSON file between tool calls:

```bash
python scripts/fmea_project.py --action create --project "Front Bumper PFMEA" \
  --type PFMEA --item "Front Bumper Assembly" --customer "Acme Motors" \
  --process-name "Injection Molding" --template mechanical-assembly

python scripts/fmea_project.py --action add --project "Front Bumper PFMEA" \
  --fe "..." --fm "..." --fc "..." --s 6 --o 4 --d 5 \
  --process-step "Injection Molding" --category-4m Machine --pc "..." --dc "..."

python scripts/fmea_project.py --action list --project "Front Bumper PFMEA"
python scripts/fmea_project.py --action update --project "Front Bumper PFMEA" --item-id 1 --d 2 --action-status Implemented
python scripts/fmea_project.py --action high-priority --project "Front Bumper PFMEA"
```

Each `add`/`update` computes AP immediately and reports it back, so you can tell the user the risk level of a chain as soon as they describe it, without waiting until the whole analysis is done.

### Step 5 — Generate the report

When the tracker is used, bridge it into the report generator instead of hand-building `chains.json`:

```bash
python scripts/fmea_project.py --action export --project "Front Bumper PFMEA" \
  --format report-input --output-dir ./output
```

This writes `chains.json` from the tracked items and prints the exact `generate_fmea.py` command to run next (pre-filled with the project's meta fields). Then run it:

```bash
python scripts/generate_fmea.py \
  --type PFMEA \
  --item "Front Bumper Assembly" \
  --customer "Acme Motors" \
  --template mechanical-assembly \
  --chains ./output/Front_Bumper_PFMEA_chains.json \
  --output-dir ./output
```

`chains.json` is a list of failure-chain objects (see `scripts/generate_fmea.py --help` for the exact schema). The script produces `<item>_FMEA.xlsx` (one worksheet: header, structure, function, failure analysis, risk analysis with S/O/D/AP, optimization actions, and a conditional-formatted risk view) and `<item>_FMEA.docx` (a readable narrative version organized by the seven steps).

### Step 6 — Summarize for the user

After generating, report back in prose (not just "done"):

1. A short walk-through of the seven steps as applied to this item.
2. Risk counts: how many chains are H / M / L priority.
3. Any failure effects flagged for management review (S 9–10 with AP H/M).
4. Any special characteristics identified (see §5).
5. The file paths.

## 5. Special characteristics

- S = 9–10 → flag as a **Critical Characteristic (CC)**.
- S = 8 with AP = H or M → flag as a **Special Characteristic (SC)**.
- Tell the user these should be carried into the control plan (PFMEA) or design record (DFMEA) — this skill doesn't generate a control plan itself.

## 6. What NOT to do

- Don't invent warranty/complaint/Cpk data.
- Don't output an RPN number.
- Don't let S drop below what the stated failure effect implies just to make AP look better.
- Don't skip Structure Analysis / Function Analysis and jump straight to failure analysis — even a one-line structure/function summary should exist in the output.
- Don't copy a DFMEA's failure modes directly into a PFMEA or vice versa — they analyze different things (the product itself vs. the process that makes it).

## 7. Files in this skill

```
pfmea-dfmea-skill/
├── SKILL.md                        this file
├── scripts/
│   ├── generate_fmea.py            xlsx + docx report generator (one-shot, from a chains.json)
│   └── fmea_project.py             stateful project tracker (incremental: create/add/list/update/high-priority/export)
├── references/
│   ├── seven_step_guide.md         what each of the 7 steps produces, common mistakes
│   ├── sod_scoring_tables.md       S/O/D 10-point tables + AP rule table
│   └── failure_chain_examples.md   worked FE→FM→FC examples across industries
└── templates/
    ├── INDEX.md                    template selection guide
    ├── electronic-electrical/
    ├── mechanical-assembly/
    ├── surface-treatment/
    ├── painting-coating/
    └── generic-fmea/
```
