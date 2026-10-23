---
name: rietx
description: >-
  Refine powder diffraction data with the rietx Python package (Rietveld, Le
  Bail, Pawley, phase quantification, indexing an unknown cell, judging a
  FitReport) — read it before the first fit() whenever a task involves a powder
  pattern, a CIF to fit against one, phase fractions, a cell to determine, an
  in-situ series, a batch of candidates or of patterns fitted as separate
  jobs, or an existing rietx result to judge. Read it too before drawing a
  crystal structure from a CIF or a refined model. rx.viz.render_structure
  draws one to a PNG with polyhedra and a view down any axis, without a
  browser.
license: MIT
compatibility: Requires the rietx Python package (pip install rietx) and Python 3.11+. Works offline — this file and its references ship in the wheel; the user manual it names is hosted at https://rietx.org.
metadata:
  version: "1.9.0"
  homepage: "https://rietx.org"
---

# Refining powder diffraction data with rietx

How to drive `rietx` on real data: the order of work, and the checks before you believe a number. Rwp ranks fits of the same data over the same channels. It certifies nothing else (rule 16).

## Routing

**A name in front of you is its own index.** A `Diagnostic` code, a field or a verb has its row in one of these files, and `grep -rn NAME references/` finds it wherever it lives. Run it from this file's directory. §5, §7, §8 and §9 are reference files, not sections of this body.

| When | Load |
|---|---|
| before any call; § Out CIF and tables | [api](references/api.md) |
| another program's file (`.EXP`, `.prm`, `.gpx`, `.pcr`, `.inp`) to read | [api-io](references/api-io.md) |
| a structure figure or a pattern plot | [api-figure](references/api-figure.md) |
| §5 quoting or comparing a number; Layer 0/1/2 | [numbers](references/numbers.md) |
| §7b-7f the phase is unknown: peaks, indexing, extinction | [diagnostics-indexing](references/diagnostics-indexing.md) |
| §7j a magnetic code, a satellite, a moment | [magnetic](references/magnetic.md), [api-magnetic](references/api-magnetic.md) |
| §4/4b the measurement behind a judging rule, before you override it | [judging](references/judging.md) |
| §6 something declined to answer | [abstention](references/abstention.md) |
| §8 a result that makes no sense | [surprises](references/surprises.md) |
| §9 the trajectory, and the history DAG | [history](references/history.md) |
| §9b a ramp, a sweep or a tray of patterns | [series](references/series.md) |
| §9c a batch: deciding; operating | [batch](references/batch.md), [batch-operating](references/batch-operating.md) |
| §9d a human watching, or a finished run on disk | [watching](references/watching.md) |

Read signatures from the package, never from memory: `rx.capabilities()`, `rx.help_for(path)`, `inspect.signature(obj)`. A failure raises. Dump an answer with `model_dump(mode="json")`.

---

## 1. Preconditions

Rietveld refinement locally fits a model you already believe. Check each row before `fit()`:

| Requirement | How |
|---|---|
| Every crystalline phase is modelled | `rx.Structure.from_cif` per phase, joined as `rx.Structure(phases=[*a.phases, *b.phases])`. A missing phase shows as `unmatched_obs` (rule 11) |
| The starting cell is within ~1 % | the CIF, or `rx.index_pattern` (§7d). Peak windows are fixed per stage, so a peak further off is out of reach; the report answers `reindex_or_recheck_cell` |
| The wavelength is right | the file header, an instrument file (api-io), or `rx.Instrument.bragg_brentano(radiation=...)`: `"CrKa"`, `"FeKa"`, `"CoKa"`, `"CuKa"`, `"MoKa"`, `"AgKa"`, suffix `1` for Kα1 only. No fit detects a wrong one. Never hand-enter a textbook value (§8.11) |
| The geometry is right | `rx.Instrument.bragg_brentano`, or `rx.Instrument.debye_scherrer(wavelength)` for a capillary. Each aberration exists only in its own geometry |
| Intensities are raw counts | `rx.read_pattern` reads the file's esd column. Wrong weights make every esd wrong |
| The starting width is within ×2 | `W` is the squared Gaussian FWHM at low angle (Γ_G² = U·tan²θ + V·tanθ + W; `rx.help_for("instrument.profile.w")`). Its default, 1e-3 deg², is a 0.03° synchrotron line. Seed `W ≈ (0.6·H)²`, `X ≈ 0.6·H`, with H the median `fwhm` of the strongest `rx.pick_peaks` peaks (§10): Gaussian and Lorentzian halves of 0.6·H combine to about H |
| The fitted range is yours | `fit(two_theta_limits=(lo, hi))`, and the same tuple to `rx.auto_background`. `PatternData.excluded_regions` drops intervals |

Never subtract a background, because that breaks the weights. Hold an estimated one additively (`rx.BackgroundFixedPlusChebyshev`), or co-refine one: `rx.auto_background(data, kind="chebyshev")`, or the default penalised P-spline. A measured blank is `BackgroundFixedPlusChebyshev.from_pattern(blank)` (§8.29).

---

## 2. The turn-on order

Free parameters in groups, cumulatively, each group converged before the next (McCusker et al. 1999, *J. Appl. Cryst.* **32**, 36). A preset plan does this; `rx.PLAN_INFO` describes each. Leave a plan's order only when `ref.suggest(data)` (held parameters ranked by predicted Δχ², with no fit) or a diagnostic names a better next group.

| Plan | When |
|---|---|
| `mccusker_default` | a known structure's first fit, and the reset when one goes wrong: scale, background, zero, cell, widths |
| `mccusker_structural` | the same, then coordinates, Biso and ADPs, PO, extinction, roughness. The worked default (§10) |
| `lab_bragg_brentano` | zero and sample displacement free together (rule 6), with Kα2 ratio and axial divergence. Only where something outside the fit pins one of the two |
| `lab_calibrate` | a standard, its certified cell held; then `rx.save_instrument_profile` |
| `lab_sample_refine` | a specimen after `rx.load_instrument_profile`, the only plan whose size and strain are the sample's |
| `profile_only` | cell and widths with no structural model (Le Bail) |
| `pawley_default` | `mode="pawley"`: intensities with esds |

1. **Free `W` before `U, V, X, Y`**, or the angular terms absorb the constant.
2. **Free intensity corrections last** (PO, extinction, roughness), after the structure settles, or they absorb structure.
3. **Free anisotropic strain inside the sample-broadening stage.** A Stephens block locks `lor_strain`, so later means fifteen coefficients turned on at once.

**Le Bail** (`mode="lebail"`, plan `profile_only`) is for a cell without a trusted structure: an indexing check, intensities for structure solution, a cell independent of any model. With a CIF, run the Rietveld plan directly (judging.md § rules 4-5). Where reflections crowd, check a Le Bail cell against a structural model before you quote it.

4. **Set `lebail_passes` (say 8) on a plan object**: `plan = rx.RefinementPlan.profile_only(); plan.lebail_passes = 8`. The run stops at the first pass that does not lower Rwp, keeps the best, and names the stop (`LEBAIL_ALTERNATION_STOPPED`).
5. **Seed the background before a Le Bail run: `rx.auto_background(data, seed=True)`.** The default starts every coefficient at 0.0, so the first partition gives the whole pedestal to the reflections; `seed=True` starts them at a low percentile of the counts.

---

## 3. The degeneracies

| Group | Signatures | Action |
|---|---|---|
| zero · displacement · cell | const · cosθ · tanθ | refine zero or displacement, not both, unless a calibration pins one |
| zero · capillary offsets · cell | const · sin2θ · cos2θ · tanθ | the Debye-Scherrer version; needs a wide range (§8.18) |
| size · strain | 1/cosθ · tanθ | one parameter over a short range |
| scale · ADPs · background · absorption · roughness · extinction | smooth in Q | each absorbs the others (rule 15) |
| capillary µR · scale · Biso | exactly | compute µR from the specimen, never refine it (§8.1) |
| flat-plate µt · scale · Biso | mostly | compute µt, never refine it (§8.12) |
| PO · occupancy | specific hkl | correct texture before you refine an occupancy |
| overlapped intensities (Le Bail, Pawley) | identical | quote the sum; the split is undetermined |
| extra peak · the reflection under it | identical | `EXTRA_PEAK_ON_REFLECTION`; declare one only for a real intruder (§8.23) |

6. **Free a group's second member only when something outside the fit pins the first.** `lab_calibrate` does this by holding the certified cell.
7. **Above a correlation of 0.98 (`HIGH_CORRELATION`), fix one member or extend the range.** Widening bounds does not help.
8. **Constrain what chemistry makes one quantity**: `ref.tie_equal([paths])`, `ref.tie(path, source, scale=, offset=)` (`occ₁ = 1 − occ₀` is `scale=-1, offset=1`), `ref.untie`. Tie only values within their combined esds in the free fit, never judged by Rwp (judging.md § rule 8).

To keep a parameter fixed through a plan, call `ref.hold(globs)`: a plan replaces `vary` flags, so `vary=False` alone does not hold (§8.25). `ref.set_vary` can refuse, so read its return.

---

## 4. Judging a fit

Judge in this order. `print(result)` shows per-stage status, the diagnostics, provenance, and the agreement indices last. Act on each `d.suggestion`, then grep its code. Evidence: [judging](references/judging.md).

9. **Status and guards first.** `result.usable` is false when the fit did not converge or carries an `"error"` diagnostic: read no value from it. Then `result.diagnostics`, then `result.statistics.max_shift_over_esd`. Above 0.1 under `converged`, a direction is still walking: bound it, or find its correlated partner (rule 7).
10. **Read the difference curve by region**: `report.regions` (local Rwp, χ² share) and `cumulative_chi2_breakpoints`.
11. **Read the unmatched peaks.** In `report.unmatched`, `unmatched_obs` is an impurity or a missing phase. `unmatched_calc` is a modelled phase that is absent, or an absence error; read it in Rietveld mode only. `result.tick_hkl` names `result.ticks` by index.
12. **Check that the values are possible**: no negative Biso, no occupancy above 1, no cell moved further than its start could have been off, no non-ellipsoid ADP. Read the bonds and angles in `result.geometry` too, which nothing scores. A `None` esd means no covariance or fixed by symmetry, never zero.
13. **Quote each esd with its trio.** Every esd already carries `statistics.esd_inflation`. Pass on `report.identifiability`'s raw χ²_red, the inflation and Durbin-Watson beside it.
14. **Settle an exchange by a swap.** An `exchangeable=True` row in `report.identifiability.exchanges` (or a `.soft_modes` entry) says a held parameter may carry the same signal as a free one. `rx.report.compare_rivals(ref, data, finding)` fits each member alone, the other at its null. If max(r, 1/r) of its `chi2_ratio` r (held over partner) is at least `rx.report.RIVAL_DECISIVE_MIN_CHI2_RATIO` (1.10), adopt the winner without caveat. Below it, declare the pair unresolved or settle it by protocol. Never free both in one fit: that rides §3's ridge to a better Rwp. `result.statistics.identifiability_clause` carries the sentence to quote.
15. **Read the background before Rwp.** In `report.background`, `worst_absorption` and `worst_absorption_path` say how much of a structural parameter the background can mimic. `off_region_chi2_reduced` and `off_region_durbin_watson` catch systematic misfit between the peaks, which rule 10 misses.
16. **Then Rwp and GoF**, beside `background.rwp_background_subtracted`, which separates two fits of the same data.
17. **Read R factors last.** `result.phase_agreement` (`r_bragg`, `r_f`) flatters any model, because I(obs) is partitioned by I(calc). Never cite R_B as evidence a correction helped, nor compare a trace phase's with the major's. Le Bail and Pawley have none.

**Adding a parameter**: its t-ratio first, then ΔBIC at N/f² with f = `esd_inflation`; at raw N any χ² gain passes. `rx.report.compare_freed(restricted, full)` returns both. **Against another code**: adopt its file's wavelengths, refined set, held parameters and excluded regions, match the channel count, then compare.

---

## 4b. Declare the deliverable

Non-ideal data moves no bar. It changes which rows decide. Declare the deliverable and read its rows with `ref.summary(deliverable=…)`, or `SeriesResult.summary(deliverable="series")` for a chain.

| Deliverable | Rows that decide it | Stop when |
|---|---|---|
| Phase ID | `report.unmatched` (`unmatched_obs`); `report.lebail_gap.ratio`, Rietveld Rwp over Le Bail Rwp: ≫ 1 means every line is indexed and the intensity model is what misfits | no strong unmatched observed peak, at any Rwp. `abstained_kind="resolution_limited"` does not block it |
| QPA | `result.qpa.phases` (`weight_fraction`, `zmv`); `report.background` absorption first, then absorption geometry, then impossible values. A large gap ratio means wrong fractions | fractions stable under a change of background flexibility, `worst_absorption` under its threshold, no unresolved scale or ZMV code, no trace-phase `ref.profile_fraction` finding. Never "Rwp stopped falling" |
| Trajectory | `SEQUENTIAL_PATH_DEPENDENT`, `SEQUENTIAL_PERSISTENT_FINDING`, `SEQUENTIAL_DISCONTINUITY`, `PHASE_UNCONSTRAINED`; 2θ anchor, precision/accuracy split, QPA check at every point (§9b) | each quoted number names the one thing that would make it wrong, and that thing is checked |
| Microstructure | `result.microstructure`: size (Å), Δd/d, `separable`, `size_agreement`, `SIZE_UNUSUALLY_SMALL`, `STRAIN_UNUSUALLY_LARGE`, `BOUND_HIT` | `separable` is true and the readings agree. Quote the size as an order of magnitude with its `scherrer_k`. `separable=False` asks for a wider 2θ range |
| Structure | all of §4, plus `report.texture`, `report.strain`, restraint tension, ADP positive-definiteness, `report.identifiability.exchanges` | the three stop conditions (§10), with every `exchangeable` row swapped (rule 14) |

`resolution_limited` ends phase-ID work; for a structure, collect better data. Before you execute one of `report.suggested_actions`, verify it with `rx.report.predict_then_verify(ref, data, action)` or on a history branch (§9). Treat a capped confidence as an open question, and never run a vetoed action.

---

## 6. Abstention

The package declines rather than return a confident wrong singleton, and the refusal is the answer. Every signal and its response: [abstention](references/abstention.md).

18. **Propagate an abstention.** With `report.abstained_reason` set, branch on `report.abstained_kind` and do not read `report.attribution`. `INDEX_ABSTAINED` lists candidates for inspection.
19. **Adopt a cell from `IndexingResult.best_or_none()`, not from a rank.** `None` is the usual first outcome: act on each candidate's refuting `confidence_caveats` first (§7c). Adopting an ungated cell is your stated decision, and a refinement checks it (§7d).
20. **A failed gate names no cause.** With `region.gates_passed` false, read `region.gate_failures`; its coefficients are display only.
21. **Report collinear answers as unresolved.** A non-separable trend, `PAWLEY_OVERLAP_UNRESOLVED`, `INDEX_GEOMETRIC_AMBIGUITY`, `EXTINCTION_GROUPS_NOT_SEPARABLE`: extend the range, report both, or carry the list forward. A group's sum is the datum.
22. **Quote no held or unquotable value as measured.** `PHASE_UNCONSTRAINED`, `STEPHENS_STRAIN_NOT_POSITIVE`, `BOUND_HIT`, `FLOOR_HIT`, `HARMONIC_HELD`: the data did not set the number, whatever its esd.

---

## 10. A worked default

A Bragg-Brentano lab pattern and a CIF. Adapt the plan, and keep the checks. To reproduce another program's fit, follow §4 instead.

```python
import numpy as np
import rietx as rx

PATTERN, CIF = "sample.xy", "phase.cif"
data = rx.read_pattern(PATTERN)
structure = rx.Structure.from_cif(CIF)
instrument = rx.Instrument.bragg_brentano(radiation="CuKa")
limits = (float(np.min(data.two_theta)), float(np.max(data.two_theta)))  # narrow to what you trust
instrument.background = rx.auto_background(data, kind="chebyshev", two_theta_limits=limits)

strong = sorted(rx.pick_peaks(data, instrument).peaks, key=lambda p: -p.intensity)[:12]
h = float(np.median([p.fwhm for p in strong]))                           # §1 width seed
instrument.profile.w.value, instrument.profile.x.value = (0.6 * h) ** 2, 0.6 * h

ref = rx.Refinement(structure, instrument)
result = ref.fit(data, plan="mccusker_structural", two_theta_limits=limits)  # zero, no displacement

print(result)                                                            # rule 9
for d in result.diagnostics:
    print(d.level, d.code, d.where, "->", d.suggestion)
report = ref.report(plan="mccusker_structural")
if report.abstained_reason:                                              # rule 18
    print("Layer 1 abstained:", report.abstained_kind, report.abstained_reason)
print([u for u in report.unmatched if u.kind == "unmatched_obs"])        # rule 11
print(ref.summary(deliverable="structure", report=report))               # §4b
```

**The three stop conditions.** Stop refining when

23. every diagnostic is understood, and resolved or reported as a caveat;
24. `report.abstained_reason` is unset and `report.attribution` attributes no remaining region above the significance gate; and
25. the next parameter group fails its t-ratio or ΔBIC at N/f² (§4), or trips a guard.

Whether Rwp is still falling decides neither way. These are the structure-grade conditions; §4b's last column gives the other deliverables' stops.

**Report** the refined values with their esds, the unresolved diagnostics as systematics, the protocol you ran (plan, held parameters, excluded ranges, channel count) and `result.provenance` (version, backend, solver). Write files with `rx.write_refinement_cif` and `rx.write_qpa_table`.

Theory and equations: <https://rietx.org/manual.html>.
