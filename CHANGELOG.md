# Changelog

All notable changes to this project are documented here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-08-08

### Added
- Initial release: `SKILL.md` workflow covering DFMEA and PFMEA per the AIAG & VDA (2019) seven-step approach.
- `references/seven_step_guide.md`, `references/sod_scoring_tables.md` (S/O/D tables + AP rule table), `references/failure_chain_examples.md`.
- Five industry templates: electronic-electrical, mechanical-assembly, surface-treatment, painting-coating, generic-fmea.
- `scripts/generate_fmea.py` — xlsx + docx report generator with Action Priority computed from S/O/D (no RPN), auto-fill heuristics, special-characteristic (CC/SC) flagging, and borderline-AP detection.
