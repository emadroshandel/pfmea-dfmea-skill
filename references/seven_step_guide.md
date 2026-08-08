# The Seven-Step FMEA Approach

This is a working guide to the seven steps introduced in the 2019 AIAG & VDA FMEA Handbook, written as an implementation reference for this skill — not a reproduction of the handbook itself.

## Step 1 — Planning and Preparation

**Purpose:** define the boundaries of the analysis before any technical work starts, so the team isn't debating scope mid-analysis.

**Key activities:**
- Identify the item/process under analysis and its boundaries (what's in scope, what's explicitly out).
- Identify the analysis level (for DFMEA: vehicle/system/subsystem/component/part; for PFMEA: which line, which process segment).
- Identify the team and their roles.
- Check for a base/family FMEA to start from instead of a blank sheet.
- Set a timeline.

**Output:** a project header — item name, customer, team, scope statement, and (if used) the base FMEA reference.

**Common mistakes:** starting failure analysis before the scope is agreed; analyzing at the wrong system level (too broad = unmanageable, too narrow = misses interface risks).

## Step 2 — Structure Analysis

**Purpose:** establish what the item is actually made of (or, for PFMEA, what the process actually consists of) before talking about what could go wrong with it.

**DFMEA:** a structure tree or boundary diagram — system → subsystem → component → part.

**PFMEA:** a process flow diagram plus, for each process step, its 4M work elements (Man, Machine, Material, Method — Environment and Measurement are commonly added as a 5th/6th "M" when relevant).

**Output:** a structure tree (DFMEA) or process flow + work-element breakdown (PFMEA).

**Common mistakes:** skipping straight to failure modes without ever writing down the structure — this is the step most often shortcut, and it's also the step that keeps the failure analysis from missing whole branches of the design/process.

## Step 3 — Function Analysis

**Purpose:** state what each structural element is *supposed to do*, in measurable terms, before describing how it could fail to do that.

**DFMEA:** function statements in "active verb + measurable noun" form (e.g., "converts electrical energy to light output ≥ 800 lm"). For safety-relevant or complex interfaces, a Parameter Diagram (P-Diagram) captures: inputs (signals), intended outputs, unintended outputs, control factors (adjustable design parameters), and noise factors (grouped as: piece-to-piece variation, changes over time/mileage, customer usage, external environment, and system interactions).

**PFMEA:** a function per process step ("process step + object acted on + intended result", e.g., "injection molding: converts PC resin pellets into a bumper shell meeting print dimensions") and a function per 4M work element.

**Output:** a function tree (DFMEA) or process-step function list (PFMEA), linked back to the structure from Step 2.

**Common mistakes:** writing functions as vague adjectives ("works well") instead of measurable statements; forgetting noise factors in a P-Diagram.

## Step 4 — Failure Analysis

**Purpose:** for every function in Step 3, work out how it could fail — and build the three-level failure chain.

**Failure chain:**

```
Failure Effect (FE)  ←  Failure Mode (FM)  ←  Failure Cause (FC)
   "so what happens?"     "what fails to happen?"   "why does it happen?"
```

**The seven generic failure-mode types** (useful as a checklist so you don't miss a category):
1. Loss of function (can't operate at all, or sudden total failure)
2. Degraded function (performance decays over time)
3. Intermittent function (works, then doesn't, unpredictably)
4. Partial loss of function (reduced performance, still operating)
5. Unintended function (operates at the wrong time or in the wrong direction)
6. Function exceeds limits (operates beyond an acceptable range)
7. Delayed function (operates, but only after an unintended delay)

**DFMEA cause sources:** the five P-Diagram noise-factor categories; interface failures (mechanical/electrical/software); design-specific issues (material selection, geometry/tolerance stack-up).

**PFMEA cause sources — classify every cause by 4M/6M:**
- **Man**: operator error, inadequate training
- **Machine**: equipment malfunction, wear, calibration drift
- **Material**: incoming material variation, wrong batch/lot
- **Method**: missing or wrong SOP, wrong process parameter
- **Environment**: temperature/humidity, contamination
- **Measurement**: measurement system error/bias

**Output:** one FE→FM→FC chain per credible failure path, each tagged to the relevant structure/function elements.

**Common mistakes:** merging FM and FC into one field ("failed because of X" isn't a failure mode, it's a cause); listing effects that are really just restatements of the mode; only listing the "obvious" failure and missing systemic causes.

## Step 5 — Risk Analysis

**Purpose:** score each failure chain on Severity (S), Occurrence (O), and Detection (D), and compute the resulting Action Priority (AP).

See `sod_scoring_tables.md` for the full 10-point tables and the AP rule table. Two rules that are easy to get wrong:

- **S is about the effect, not the cause** — S doesn't change based on how the failure happens, only on how bad it is when it does.
- **DFMEA and PFMEA severity for the same effect must match.** If the DFMEA already rated a given effect S=8, the PFMEA analyzing the process that could cause that same effect uses S=8 too — it isn't re-derived from scratch.

**Output:** S/O/D scores, current Prevention Control (PC), current Detection Control (DC), and AP (H/M/L) for every chain.

## Step 6 — Optimization

**Purpose:** for chains where AP indicates action is warranted, define what will actually change.

**Three levers, roughly in order of how commonly they're used:**
1. **Improve detection control (lowers D)** — add a test step, move detection earlier, use a more sensitive method.
2. **Improve prevention control (lowers O)** — add a design rule, DOE, simulation, mistake-proofing (poka-yoke), tighter process control (SPC).
3. **Reduce severity (lowers S)** — usually requires a design change (redundancy, fail-safe behavior); rarely achievable through process controls alone.

**Track for each action:** status (suggested → decided → implemented → closed), owner, due date, and — once implemented — the *re-scored* S/O/D and resulting AP, so the improvement is demonstrated numerically, not just asserted.

**Output:** an action list linked to specific failure chains, with before/after AP.

## Step 7 — Results Documentation

**Purpose:** package the analysis into a report that stands on its own for an audit, a design review, or a PPAP submission.

**Typical structure (what `generate_fmea.py` produces):**
1. Header (item, customer, team, scope)
2. Structure analysis
3. Function analysis
4. Failure analysis (FE/FM/FC chains)
5. Risk analysis (S/O/D/AP/PC/DC)
6. Optimization actions (owner, due date, status, re-scored AP)
7. Summary: risk counts by priority, special characteristics identified, conclusions

**Output:** the FMEA workbook/report, plus (for PFMEA) special characteristics flagged for the control plan.

## How this maps to IATF 16949 / APQP

- DFMEA sits under IATF 16949 clause 8.3 (design and development of products and services) and is typically developed during APQP phases 2–3.
- PFMEA sits under clause 8.5 (production and service provision) and is typically developed during APQP phase 3, ahead of the control plan.
- Special characteristics identified in the PFMEA should flow directly into the control plan — this skill flags them but does not generate the control plan itself.
