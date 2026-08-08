# Worked Failure-Chain Examples (FE → FM → FC)

Reference examples for auto-fill mode and for illustrating what a well-formed failure chain looks like. These are generic, illustrative chains — not measured data for any real product. Always tell the user that when auto-fill is used.

Each example shows the three-level chain, an S/O/D starting point with the reasoning, and PC/DC. Treat the scores as reasonable defaults for the scenario described, not universal constants — real O and D always depend on the specific controls in place.

---

## Electronics / Electrical (DFMEA)

**FE:** Vehicle exterior lighting fails during night driving, increasing collision risk.
**FM:** LED driver module open circuit.
**FC:** Solder joint on the LED driver IC cracks due to thermal cycling stress exceeding the joint's fatigue life.
**S=10** (safety-related, loss of function while driving at night) · **O=4** (mature LED driver technology, moderate thermal cycling exposure) · **D=6** (validated pass/fail thermal cycling test, not 100% inline).
**PC:** Thermal simulation during design + solder joint reliability design rules (IPC-9701 class).
**DC:** 1000-hour high-temperature cycling test + post-test cross-section inspection.

**FE:** Infotainment display shows corrupted/frozen image, distracting the driver.
**FM:** Display controller intermittent reset.
**FC:** Insufficient decoupling capacitance causes voltage droop under peak load.
**S=4** (annoyance, not safety-critical) · **O=5** (similar architecture used previously with occasional issues) · **D=5** (power integrity bench test, not exhaustive across all load profiles).
**PC:** Power integrity simulation at design review.
**DC:** Bench-level load-transient test on prototype boards.

---

## Mechanical Assembly (DFMEA / PFMEA)

**FE (DFMEA):** Drivetrain makes unexpected noise and eventually loses torque transfer.
**FM:** Gear tooth pitting and premature wear.
**FC:** Case-hardening depth on the gear is below the design specification.
**S=7** (degraded primary function within service life) · **O=3** (established heat-treat process, tight incoming control) · **D=4** (validated hardness-depth test with adequate lead time before shipment).
**PC:** Heat-treat process parameters locked via DOE; supplier PPAP requirement on case depth.
**DC:** Destructive case-depth sectioning on a sampling frequency per control plan.

**FE (PFMEA):** Bearing assembly fails prematurely in service.
**FM:** Bearing preload out of specification after press-fit assembly.
**FC — Machine:** Press force sensor drifted out of calibration.
**S=7** · **O=5** (mechanical wear-prone step, moderate calibration interval) · **D=6** (validated go/no-go press-force check, applied at the station).
**PC:** Calibration schedule for press-force sensors + SPC on press force.
**DC:** In-station force-displacement monitoring with automatic reject on out-of-band curves.

---

## Surface Treatment (PFMEA)

**FE:** Plated fastener corrodes prematurely in service, weakening the joint.
**FM:** Insufficient plating thickness on threaded region.
**FC — Method:** Plating bath current density set below the qualified process window.
**S=6** (loss of a secondary function — fastener still holds initially but service life is shortened) · **O=5** (established plating process, periodic parameter drift risk) · **D=6** (validated thickness gauge check, per-lot sampling rather than 100%).
**PC:** Process parameter SOP with tolerance band + operator training.
**DC:** X-ray fluorescence thickness check per lot + first-piece verification each shift.

**FE:** Heat-treated component distorts, causing an assembly fit issue downstream.
**FM:** Excessive quench distortion.
**FC — Machine:** Non-uniform quench flow due to a partially clogged quench tank nozzle.
**S=5** · **O=4** (equipment maintained on a schedule; occasional nozzle fouling) · **D=5** (dimensional check after heat treat, sampling-based).
**PC:** Preventive maintenance schedule for quench nozzles.
**DC:** CMM dimensional check on a defined sampling plan post-heat-treat.

---

## Painting / Coating (PFMEA)

**FE:** Visible paint defect on a customer-facing surface, perceived as poor quality.
**FM:** Orange peel / uneven paint texture.
**FC — Environment:** Booth humidity outside the qualified spray window.
**S=3** (cosmetic, noticed by many users) · **O=5** (seasonal humidity swings, partial environmental control) · **D=5** (visual inspection under standard lighting, subjective).
**PC:** Booth humidity control system with alarm on excursion.
**DC:** 100% visual inspection at defined lighting/angle standard + periodic gloss-meter audit.

**FE:** Coated part fails salt-spray corrosion testing, risking warranty claims.
**FM:** Insufficient coating adhesion.
**FC — Material:** Substrate surface contamination (oil residue) not fully removed before coating.
**S=6** · **O=4** (established pretreatment process with periodic bath-chemistry drift) · **D=6** (validated cross-hatch adhesion test, per-lot sampling).
**PC:** Pretreatment bath chemistry SPC + tank concentration monitoring.
**DC:** Cross-hatch adhesion test per defined sampling frequency + salt-spray audit testing.

---

## Generic / Cross-Industry (fallback template)

**FE:** Product fails to meet a customer-specified functional requirement during use.
**FM:** [replace with the specific way the function is lost/degraded]
**FC:** [replace with the specific root cause — classify by 4M/6M for PFMEA]
**S=** [score against the effect on the end user, per `sod_scoring_tables.md`]
**O=** [score against current prevention control effectiveness]
**D=** [score against current detection control effectiveness]
**PC:** [what currently prevents the cause from occurring]
**DC:** [what currently would catch the failure before it reaches the customer]

Use this generic pattern whenever the item doesn't clearly match one of the four industry templates — don't force-fit an electronics or mechanical example onto an unrelated product.
