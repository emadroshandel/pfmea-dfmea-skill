# PFMEA / DFMEA Skill

A Claude / Claude Code skill that runs Design FMEA (DFMEA) and Process FMEA (PFMEA) analyses following the **AIAG & VDA FMEA Handbook (2019)** seven-step approach, and generates `.xlsx` + `.docx` reports with Severity/Occurrence/Detection (S/O/D) scoring and Action Priority (AP) — no RPN.

> **Independent implementation, not affiliated with AIAG or VDA.** This project implements the publicly known seven-step FMEA methodology and the High/Medium/Low Action Priority concept in its own words and code. It does not reproduce the AIAG & VDA Handbook's copyrighted text, figures, or the full official scoring tables. If your organization has purchased the handbook or has customer-mandated rating tables, use those as the source of truth — treat the tables here as a solid working default, not a substitute.

## Contents

- [Features](#features)
- [Installation](#installation)
- [Directory structure](#directory-structure)
- [Usage](#usage)
- [The seven steps, briefly](#the-seven-steps-briefly)
- [Why Action Priority instead of RPN](#why-action-priority-instead-of-rpn)
- [Standards referenced](#standards-referenced)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Seven-step workflow**: Planning → Structure Analysis → Function Analysis → Failure Analysis → Risk Analysis → Optimization → Results Documentation.
- **DFMEA and PFMEA** in one skill, with explicit logic for deciding which one applies and for keeping severity ratings consistent between the two.
- **S/O/D scoring tables and an Action Priority rule table** (`references/sod_scoring_tables.md`) — 2019-handbook style AP (H/M/L), RPN intentionally not supported.
- **Five industry-starter templates** (electronic/electrical, mechanical assembly, surface treatment, painting/coating, and a generic fallback) with illustrative failure chains you edit, not treat as ground truth.
- **Stateful project tracker** (`scripts/fmea_project.py`) for building an FMEA incrementally across a conversation: `create` a project, `add` failure chains one at a time (each scored immediately), `list`/`update` as the analysis develops, pull a `high-priority` view, and `export` to CSV/JSON — or straight into the report generator's input format.
- **Report generator** (`scripts/generate_fmea.py`) that turns a JSON list of failure chains into:
  - an `.xlsx` workbook: header, structure/function summary, a color-coded risk table (S/O/D/AP), and an action list, plus a risk-count summary;
  - a `.docx` narrative report organized by the seven steps, readable on its own for a design review or audit.
- **Guardrails against common FMEA mistakes**: no RPN, no fabricated warranty/complaint/Cpk data, mandatory FE→FM→FC three-level chains, 4M/6M classification for PFMEA causes, automatic flagging of Critical/Special Characteristics (CC/SC) and of chains that warrant management review.

## Installation

### As a Claude / Claude Code skill

Drop the `pfmea-dfmea-skill/` folder into your skills directory (or point your agent's skill loader at this repo). The skill triggers automatically on requests like "make me a DFMEA for X" or "run a PFMEA on this process" — see the frontmatter in `SKILL.md` for the exact trigger description.

### As a standalone script

The report generator only needs two Python packages:

```bash
pip install openpyxl python-docx
```

```bash
git clone https://github.com/<your-username>/pfmea-dfmea-skill.git
cd pfmea-dfmea-skill
python scripts/generate_fmea.py --help
```

## Directory structure

```
pfmea-dfmea-skill/
├── README.md                          this file
├── LICENSE                            MIT
├── VERSION
├── CHANGELOG.md
├── SKILL.md                           the agent-facing workflow definition
├── scripts/
│   ├── generate_fmea.py               xlsx + docx report generator (stdlib argparse/json + openpyxl/python-docx)
│   └── fmea_project.py                stateful project tracker (create/add/list/update/high-priority/export)
├── references/
│   ├── seven_step_guide.md            what each of the 7 steps produces, common mistakes
│   ├── sod_scoring_tables.md          S/O/D 10-point tables + AP rule table
│   └── failure_chain_examples.md      worked FE→FM→FC examples across industries
└── templates/
    ├── INDEX.md                       template selection guide
    ├── electronic-electrical/
    │   ├── intro.md
    │   └── template.json
    ├── mechanical-assembly/
    │   ├── intro.md
    │   └── template.json
    ├── surface-treatment/
    │   ├── intro.md
    │   └── template.json
    ├── painting-coating/
    │   ├── intro.md
    │   └── template.json
    └── generic-fmea/
        ├── intro.md
        └── template.json
```

## Usage

### Command line

Failure chains go in a JSON file (see the schema documented at the top of `scripts/generate_fmea.py`):

```json
[
  {
    "process_step": "Injection Molding",
    "category_4m": "Machine",
    "fe": "Bumper cracks under low-speed impact, failing to protect the vehicle structure",
    "fm": "Insufficient wall thickness in the mounting boss",
    "fc": "Injection pressure below the qualified process window",
    "s": 6, "o": 4, "d": 5,
    "pc": "Process parameter SOP with tolerance band",
    "dc": "First-piece dimensional check each shift"
  }
]
```

```bash
python scripts/generate_fmea.py \
  --type PFMEA \
  --item "Front Bumper Assembly" \
  --customer "Acme Motors" \
  --process-name "Injection Molding" \
  --template mechanical-assembly \
  --chains chains.json \
  --output-dir ./output
```

This writes `Front_Bumper_Assembly_FMEA.xlsx` and `Front_Bumper_Assembly_FMEA.docx` to `./output`. Omit `s`/`o`/`d` on any chain and pass `--auto-fill` to get conservative starter scores instead of an error — useful for a first draft, not for a final report.

### Building incrementally with the tracker

If you'd rather add failure chains one at a time — during a live design review, or as an analysis develops over a longer session — use `fmea_project.py` instead of hand-writing `chains.json`:

```bash
python scripts/fmea_project.py --action create --project "Front Bumper PFMEA" \
  --type PFMEA --item "Front Bumper Assembly" --customer "Acme Motors" \
  --process-name "Injection Molding" --template mechanical-assembly

python scripts/fmea_project.py --action add --project "Front Bumper PFMEA" \
  --fe "Bumper cracks under low-speed impact" \
  --fm "Insufficient wall thickness in the mounting boss" \
  --fc "Injection pressure below the qualified process window" \
  --s 6 --o 4 --d 5 --process-step "Injection Molding" --category-4m Machine \
  --pc "Process parameter SOP with tolerance band" \
  --dc "First-piece dimensional check each shift"

python scripts/fmea_project.py --action list --project "Front Bumper PFMEA"
python scripts/fmea_project.py --action update --project "Front Bumper PFMEA" --item-id 1 --d 2 --action-status Implemented
python scripts/fmea_project.py --action high-priority --project "Front Bumper PFMEA"
```

Each `add`/`update` computes Action Priority immediately, so you get the risk level as soon as a chain is entered. The project persists as JSON under `fmea_projects/`. When you're ready for the polished report, bridge straight into the generator instead of re-typing everything:

```bash
python scripts/fmea_project.py --action export --project "Front Bumper PFMEA" \
  --format report-input --output-dir ./output
# writes chains.json and prints the exact generate_fmea.py command to run next
```

`--format csv` and `--format json` are also available for a raw export of the tracked items.

### As a Claude skill

Just ask, in an engineering context:

> "Run a DFMEA on our new headlamp LED module for Acme Motors — the driver IC has had thermal issues in testing."

The agent will ask for whatever's missing (DFMEA vs. PFMEA if ambiguous, customer, team, etc.), pick a template, build failure chains from what you've told it (or from a template starter set if you ask for an example), score them, and generate the report.

## The seven steps, briefly

1. **Planning and Preparation** — scope, team, timeline.
2. **Structure Analysis** — what the item/process is actually made of (structure tree / process flow + 4M).
3. **Function Analysis** — what each part is supposed to do, stated measurably.
4. **Failure Analysis** — the three-level chain: Failure Effect ← Failure Mode ← Failure Cause.
5. **Risk Analysis** — S/O/D scoring and the resulting Action Priority.
6. **Optimization** — actions that lower O (better prevention) or D (better detection), tracked to closure.
7. **Results Documentation** — the report itself, plus special-characteristic flags for the control plan.

Full detail, common mistakes, and the DFMEA/PFMEA-specific variations are in `references/seven_step_guide.md`.

## Why Action Priority instead of RPN

The pre-2019 approach multiplied S × O × D into a single Risk Priority Number and used an arbitrary threshold (often RPN > 100) to decide what needed action. That approach is well known to produce misleading results — a high S with low O and D can average out to the same RPN as a mediocre score across the board, even though the first case is far more urgent. The 2019 AIAG & VDA Handbook replaced this with a rule-based High/Medium/Low Action Priority derived from the *combination* of S, O, and D rather than their product, which is what this skill implements (`references/sod_scoring_tables.md` §4, `scripts/generate_fmea.py::compute_ap`).

## Standards referenced

This project is built around the publicly known structure of:

- **AIAG & VDA FMEA Handbook (2019)** — seven-step approach, Action Priority concept
- **IATF 16949:2016** — clause 8.3 (design and development) for DFMEA, clause 8.5 (production and service provision) for PFMEA
- **ISO 9001:2015** clause 6.1 (risk-based thinking)

None of these standards' copyrighted text is reproduced here — the reference documents in `references/` are original write-ups of the underlying methodology, written for this skill.

## Contributing

Issues and pull requests are welcome — particularly additional industry templates, corrections to the scoring guardrails, or improvements to the report layout. Please avoid submitting content copied from proprietary FMEA training materials or other closed-license repositories; keep contributions original or properly licensed.

## License

MIT — see [LICENSE](LICENSE). You're free to use, modify, and redistribute this skill, including commercially, provided the copyright notice is retained.
