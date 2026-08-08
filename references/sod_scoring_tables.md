# S / O / D Scoring Tables and Action Priority (AP) Rules

These are the working scoring tables this skill uses. They follow the general 10-point S/O/D structure and the High/Medium/Low Action Priority concept used industry-wide since the 2019 AIAG & VDA FMEA Handbook, written independently for this skill — always defer to your organization's own approved rating tables where those exist, since some OEMs publish customer-specific variants.

All scores are integers from 1 to 10. Never use 0.

## 1. Severity (S) — how bad is the effect?

Severity rates the **effect** of the failure, not how it happens or how likely it is. The same failure effect should get the same S score whether you're rating it in a DFMEA or the PFMEA for the process that produces the part.

| S | Severity level | Typical effect |
|---|---|---|
| 10 | Very high, safety-related | Failure affects safe vehicle operation and/or involves noncompliance with safety regulation, without warning |
| 9 | Very high, safety-related | Same class of effect as 10, but with some warning, or noncompliance with a non-safety regulation |
| 8 | High | Loss of a primary function needed for normal operation, within the intended service life |
| 7 | High | Degradation of a primary function, within the intended service life |
| 6 | Moderate | Loss of a secondary function or convenience feature |
| 5 | Moderate | Degradation of a secondary function or convenience feature |
| 4 | Low | Very objectionable appearance, noise, vibration, or feel — noticed by most users |
| 3 | Low | Objectionable appearance, noise, vibration, or feel — noticed by many users |
| 2 | Low | Slightly objectionable — noticed by discriminating users |
| 1 | Very low | No discernible effect |

**Guardrails:**
- Reserve 9–10 strictly for safety/regulatory effects. Don't use them for "this would be really bad for the business" — that's a severity-adjacent business risk, not FMEA severity.
- Reserve 1–3 for genuinely cosmetic issues. Don't compress everything into the middle of the scale to avoid an uncomfortable conversation.

## 2. Occurrence (O) — how likely is the cause, given current prevention controls?

Occurrence rates the likelihood that the **cause** will occur and produce the failure mode, taking into account how effective the *current prevention controls* are — it is not a raw probability estimate pulled from nowhere.

| O | Occurrence level | Typical basis |
|---|---|---|
| 10 | Extremely high | Brand-new technology/process with no field history; prevention controls cannot predict real-world performance |
| 9 | Very high | Significant change to an existing design/process, first application; prevention controls not specific to this failure cause |
| 8 | High | New application of an existing technology; prevention controls unlikely to reliably reflect real-world performance |
| 7 | High | Significant change with some field history; prevention controls give limited insight |
| 6 | Moderate | Existing technology in a similar application; prevention controls provide partial coverage |
| 5 | Moderate | Mature technology, minor detail changes; prevention controls can detect some design/process gaps |
| 4 | Moderate-low | Nearly identical to a short-term field-proven design/process; prevention controls reflect design/process conformance |
| 3 | Low | Minor, well-understood changes to a proven design/process; prevention controls can predict consistency |
| 2 | Very low | Long-term field-proven design/process, virtually unchanged; strong confidence from prevention controls |
| 1 | Extremely low | Cause is eliminated entirely through prevention control (e.g., a physical impossibility) |

**Guardrails:**
- O should almost never be 9–10 for a product/process with years of stable field or production history — that combination is internally contradictory and should be double-checked, not just accepted.
- O should almost never be 1–2 without field or process-capability data to back it up.

## 3. Detection (D) — how likely is the current detection control to catch it before it reaches the customer?

Detection rates the effectiveness of the **current detection controls** at catching the failure mode or cause before the item leaves the relevant stage — lower D is better (more likely to be caught).

| D | Detection level | Typical basis |
|---|---|---|
| 10 | Almost none | No detection method exists or planned |
| 9 | Very low | No test/inspection method has been developed for this mode/cause |
| 8 | Low | A test method exists but is unvalidated |
| 7 | Low | Validated test method, but timing is late enough that a failure would delay production/shipment |
| 6 | Moderate | Validated pass/fail test method, applied at an appropriate point |
| 5 | Moderate | Failure (destructive/degradation) testing at an appropriate point |
| 4 | Moderate-high | Validated test method with enough lead time to correct tooling/process before it affects production |
| 3 | High | Failure testing performed early enough to catch issues well before release |
| 2 | Very high | Robust, validated screening (e.g., burn-in/aging) with strong historical correlation to field performance |
| 1 | Almost certain | Detection is virtually guaranteed — failure mode is prevented from occurring, or 100% automated detection with proven reliability |

**Guardrails:**
- D=1 or D=10 should be rare and deliberate — most real controls fall somewhere in between. If you find yourself defaulting to 1 or 10 out of convenience, that's a sign the control hasn't actually been characterized.
- "100% inspection" is not automatically D=1 or D=2 — manual 100% inspection is notoriously unreliable and typically rates D=5–7 depending on the failure mode's detectability.

## 4. Action Priority (AP)

The 2019 handbook replaced the older Risk Priority Number (S×O×D threshold) approach with a three-level Action Priority derived from the *combination* of S, O, and D — not their product. AP is always computed from the rule table below, never assigned directly.

**Rule table** (apply top to bottom, first match wins):

| Severity band | Occurrence band | Detection band | AP |
|---|---|---|---|
| S = 9–10 | any O | D = 1, and O = 1 | **M** |
| S = 9–10 | any O (except the row above) | any D | **H** |
| S = 6–8 | O = 6–10 | any D | **H** |
| S = 6–8 | O = 4–5 | D = 5–10 | **H** |
| S = 6–8 | O = 4–5 | D = 1–4 | **M** |
| S = 6–8 | O = 2–3 | D = 5–10 | **M** |
| S = 6–8 | O = 2–3 | D = 1–4 | **L** |
| S = 6–8 | O = 1 | any D | **L** |
| S = 4–5 | O = 6–10 | D = 5–10 | **H** |
| S = 4–5 | O = 6–10 | D = 1–4 | **M** |
| S = 4–5 | O = 2–5 | D = 5–10 | **M** |
| S = 4–5 | O = 2–5 | D = 1–4 | **L** |
| S = 4–5 | O = 1 | any D | **L** |
| S = 2–3 | O = 4–10 | D = 5–10 | **M** |
| S = 2–3 | any other O/D combination | | **L** |
| S = 1 | any O | any D | **L** |

This is a compact rule-based approximation of the full combinatorial AP table the handbook describes. It is deliberately conservative — when a chain sits near a boundary between two bands, `generate_fmea.py` rounds up to the higher priority rather than down, and flags the chain as "borderline — recommend manual review."

**Disposition by AP:**
- **H (High):** the team must take action, or explicitly justify and document why the current PC/DC are already adequate.
- **M (Medium):** the team should take action, or the organization may decide and document that current controls are adequate.
- **L (Low):** action is optional — use engineering judgment to decide whether it's worth improving prevention or detection anyway.

**Extra scrutiny:** any chain with S = 9–10 and AP = H or M should be flagged for management review, regardless of what the rest of the table says.

## 5. What not to do

- Don't compute or report RPN (S×O×D). It's not part of this methodology.
- Don't skip straight to AP without recording S, O, and D individually — the report needs to show the reasoning, not just the conclusion.
- Don't reuse an O or D score across unrelated causes just because they're in the same FMEA — score each cause on its own controls.
