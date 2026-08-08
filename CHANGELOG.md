# Changelog

All notable changes to this project are documented here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-08-08

### Added
- `scripts/fmea_project.py` — a stateful project tracker for building an FMEA incrementally: `create`/`add`/`list`/`update`/`high-priority`/`export` actions, backed by a per-project JSON file. Action Priority is computed immediately on `add`/`update`.
- `export --format report-input` bridges the tracker directly into `generate_fmea.py`'s `chains.json` schema and prints the ready-to-run report-generation command.
- `SKILL.md` workflow updated to offer incremental (tracker-based) analysis as an alternative to one-shot report generation, based on how the conversation is going.

### Notes
- This addition was prompted by comparing against a similar community skill (`duding-engicool/skill-fmea-assistant`) that uses a stateful tracker pattern — the *workflow idea* was worth adopting, but that project's actual risk math (RPN with fixed thresholds) is the pre-2019 approach the AIAG & VDA 2019 handbook replaced, so `fmea_project.py` here is an original implementation built on this skill's existing Action Priority engine, not a port of that project's code.

## [1.0.0] - 2026-08-08

### Added
- Initial release: `SKILL.md` workflow covering DFMEA and PFMEA per the AIAG & VDA (2019) seven-step approach.
- `references/seven_step_guide.md`, `references/sod_scoring_tables.md` (S/O/D tables + AP rule table), `references/failure_chain_examples.md`.
- Five industry templates: electronic-electrical, mechanical-assembly, surface-treatment, painting-coating, generic-fmea.
- `scripts/generate_fmea.py` — xlsx + docx report generator with Action Priority computed from S/O/D (no RPN), auto-fill heuristics, special-characteristic (CC/SC) flagging, and borderline-AP detection.
