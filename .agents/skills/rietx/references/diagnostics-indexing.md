# 7b-7f. Indexing: peak picking, the answer, the closed loop, the extinction screen

Load it when the phase is unknown — peak picking through indexing, space-group screening, and on to a refinement.

*A reference file of the `rietx` skill. The body it belongs to is [`SKILL.md`](../SKILL.md); section numbers are the ones the body cites.*

## 7b. Peak picking and indexing (`PeakList.diagnostics`, `DataQualityReport.diagnostics`)

These arrive from `rietx.pick_peaks` and
`rietx.indexing.assess_peak_list`, *before* any refinement exists — so they
are read on the peak list, not on a `RefinementResult`.

| Code | What it means you must not do |
|---|---|
| `PEAK_LIST_TOO_SHORT` | Read the answer as *scored*. Below 20 usable lines the classical figures (M₂₀, F_N, Smith's envelope) are not scored, so the search still runs — over the systems the line count supports — but ranks on the reduced panel, and nothing in the answer is comparable to a published threshold. (Before WP-1043 it refused the search; see §7f) |
| `INDEX_DATA_INSUFFICIENT` | Spend a search budget. The gate has already decided the data cannot support a search *in any system*, and it names which of the two reasons applies (lines per metric degree of freedom, or σ(Q)/Q) |
| `INDEX_PANEL_REDUCED` | Treat an absent figure as zero, or compute your own M on fewer lines and quote it as M₂₀. Each absent member is named with its reason on `quality.fom_undefined`; the members that remain rank every candidate alike, so the *order* means what it always does — the `fom_panel_reduced` caveat (capping) is what says the scoring does not |
| `PEAK_SIGMA_ASSUMED` | Quote a precision, or weight lines by 1/σ² as if that meant something — every σ in the list is the same assumed constant. Re-pick from the pattern if you have it. **You may still index it**: an assumed σ is not grounds for refusing, so the σ(Q)/Q abstention below does not run on such a list (it would be quoting a precision this package invented) |
| `PEAK_NOT_SEPARABLE` | Treat the flagged component as a line, or as noise. It is neither: the fit believes in it as *shape* and disbelieves it as a *line*, so it stays in `peaks` (removing it from the model displaces the real line beside it) and is excluded from `usable()`. If many fire, suspect a **mis-declared instrument profile** rather than a crowded pattern — undeclared axial divergence reproduces the whole effect |
| `PEAK_POSITION_PRECISION` | (info/warning) Ignore it when choosing a tolerance: it *is* the resolving power of the list, and it bounds every tolerance downstream |
| `INDEX_SHIFT_DETECTED` | Absorb the shift into the cell. The named template is the physical cause; correct the instrument (`zero_shift`, `sample_displacement`, `sample_transparency`) rather than the lattice |
| `INDEX_SHIFT_MODEL_AMBIGUOUS` | Pick one cause from this data. The magnitude is measured and the cell is safe to `prediction_spread_deg`; the *cause* is not identified, and extending the 2θ range is the only fix |
| `PEAK_KALPHA2_ALIAS` | Assume the dropped candidates were noise — each is at a stronger line's Bragg-predicted Kα2 position, and a genuine coincident line is indistinguishable from an alias in one pattern |
| `PEAK_AXIAL_TAIL` | (info) Read the flagged components as lattice lines — or exclude them without looking. Each sits on the axial-divergence **tail side** of a much stronger group-mate (low-2θ below 90°, high-2θ above — the one sign flip nothing else has), and they stay *usable* because the side test is evidence, not proof. Measured on SRM 660c (WP-1043): five such components carried 125 ppm of certified-cell bias, and excluding exactly the flagged ones plus measuring the shift took the gate to `high` at −2 ppm — so on a well-aligned Bragg-Brentano pattern, excluding them before indexing is usually right |
| `PEAK_KALPHA2_RESIDUAL` | (info) Treat it as a line of anything. It sits at a strong group-mate's **predicted** Kα2 maximum at a few per cent of its area — the residual of a *modelled* doublet, re-created by a re-seed pass after detection dropped the alias. Kept usable only because a genuine reflection can coincide with an alias position; exclude it before indexing unless you have a reason to believe one does |
| `PEAK_UNRESOLVED_SHOULDER` | Quote one of a pair as an independent line. Their σ already carries the correlation |
| `PEAK_CONTAMINATION_LINE` | Subtract it, or read one flag as the evidence. The finding is joint: it fires only when five of the eight strongest reflections carry a line at their Kβ (or W Lα) position at one common ratio, and `ContaminationFlag.leak_ratio` is that ratio. The peak list carries only the flag, so re-run `rx.background.diagnose(data, wavelength=...)` to read the ratio. An unfiltered tube leaks 0.14 of Kα, so a reported 0.3 is a reflection and not a ghost. Flagged lines leave `usable()` and are never stripped (Measured: WP-1442) |
| `PEAK_ASYMMETRY_UNMODELLED` | Trust the *positions* of the flagged lines. An unmodelled one-sided aberration biases a centroid in one direction, which σ cannot see — and the low-angle lines are the ones indexing depends on most |
| `PEAK_WIDTH_LAW_MISMATCH` | Leave `instrument.profile` as declared. A factor near 13 is the `ProfileTCHZ` synchrotron default (W = 1e-3 deg², FWHM ≈ 0.03°) on lab data |
| `PEAK_SHOULDER_SEEDED` | (info) Read a shoulder-seeded line as a detection. Survival was decided by ΔBIC, not by detection |
| `INDEX_SEARCH_INCOMPLETE` | Read "no cell found" as "no cell exists". Only a *completed* exhaustive search says that; this one was stopped by its per-system budget, a size cap or the run's ceiling, and `search_complete[system]` says which systems it covered. Raise `budget_seconds` only when the message says "within … s per system" (Measured: WP-1449) |
| `INDEX_DOMINANT_ZONE` | Conclude the pattern cannot be indexed. The exact-solve engine found nothing at its base-line index table but found a cell with a wider one, which means one axis is long enough (or short enough) that the lowest observed lines carry large indices. Use the dichotomy engine, which bounds the metric instead of assuming indices |
| `INDEX_SHIFT_ALLOWANCE` | (info) Quote the winning cell without fitting a shift template. The search *assumed* a systematic allowance (no shift had been measured), and a cell found inside a widened window absorbs the shift — measured, +1400 ppm on a certified pattern. Re-fit with `shift_template` and quote that cell |
| `INDEX_SHIFT_FROM_PAIRS` | (info) Read the reported amplitude as naming a *cause*. It does not: the pair method measures the shift's size from harmonic reflection pairs with no reference, and `constant` and `cos_theta` are collinear over an ordinary range, so `best` is not an attribution. Read `pairs.refuted_templates` for what the data *do* reject, and widen the 2θ range if the cause matters |

### Peaks you name (`rx.fit_peaks`)

`pick_peaks` decides what the lines are; `fit_peaks(data, instrument, positions)`
fits exactly the positions you pass and nothing else. Reach for it when the
question is about the peaks rather than about a cell: a width analysis
(Williamson-Hall) over lines you chose, d-spacings for a lookup, one reflection
checked. It needs no structure and no space group, and it runs in tens of
milliseconds on a lab pattern.

The answer is an ordinary `PeakList`, so §7b's flags and the `usable()`/`peaks`
split read exactly as they do above. Four rules are specific to naming your own
positions.

* **A position with no peak comes back flagged, not dropped.** It carries
  `no_intensity` (and usually `position_at_bound`), and it is out of `usable()`.
  Do not read its `two_theta`: a component at zero intensity has no gradient on
  its own position, so the fitter leaves it wherever the solve ended, and the
  esd says so in the only way it can — 7e+17° on the bundled fluorapatite
  pattern. Count the flag, quote nothing (WP-1101).
* **`unnamed_neighbour` means your list is incomplete, and the bias is real.**
  It fires when the window holds a component you did not name, decided by the
  same ΔBIC test `pick_peaks` uses to accept one. Measured on the bundled
  fluorapatite: naming 52.253° alone gives 52.2502(10)° with χ²_red 4.94;
  naming its weak neighbour at 52.170° too gives 52.2529(8)° with χ²_red 1.50 —
  the line you wanted moved **2.7 m°, 2.7 of its own esds**. On a deliberately
  doubled synthetic the same omission moved a position **51 m°, 26 esds**, with
  χ²_red 0.93 → 82.5. Re-fit with the neighbour named, or say the position is
  biased; do not quote it silently.
* **Widths are the pattern's, not the specimen's.** `ObservedPeak.fwhm` is what
  was measured: instrument convolved with sample. A Williamson-Hall intercept
  from raw widths is a floor set by the diffractometer (1355 Å on that
  fluorapatite, where the instrument dominates), not a crystallite size.
  Calibrate the instrument on a standard first (`lab_calibrate`,
  `save_instrument_profile`), or refine the sample-broadening terms and read
  `rietx.model.microstructure`, which reports each mechanism with an esd and
  says whether the two are separable. State K and whether β is FWHM or integral
  breadth whenever you quote a size: they differ by ~10 % on the same data.
* **Refusals are by name, not by silence.** A position off the end of the
  pattern, or in a gap or an excluded region, raises `ValueError` naming the
  position and the channel count. That is a fact about the range you asked for;
  re-read the pattern's limits rather than retrying. The same position named
  twice is refused too: two components at one 2θ are exactly singular in their
  intensities, so there is no answer to give.

Positions sharing a window are fitted together in one solve, so pass the whole
cluster at once rather than calling once per line — separate calls over
overlapping lines each bias the other.

## 7c. The answer's own diagnostics (`IndexingResult.diagnostics`, and each candidate's)

These arrive from `rietx.index_pattern`. **Statements about one candidate live
on that candidate** (`result.candidates[i].diagnostics`); statements about the
result live on the result. `INDEX_ABSTAINED` names the top candidate's caveats,
which is the pointer from one level to the other — so read both, and start at the
result.

| Code | What it means you must not do |
|---|---|
| `INDEX_PREDICTED_BUT_ABSENT` | Keep this candidate. The lattice needs reflections the pattern does not have: an oversized cell, which M₂₀ cannot see, or a glide or screw axis in a correct one. Prefer a smaller cell only if its own Le Bail fit indexes the same lines (Measured: WP-1545, aragonite in P m c n is correct with 4 of 105 absent). **Do not check this with Rwp** — measured, an oversized cell scores 0.379 against a correct 0.216, a gap smaller than the spread between specimens |
| `INDEX_IMPURITY_LINES` | Read it as one thing. A handful of unexplained lines is an impurity; most of the pattern is a wrong metric (measured, 95 of them when the metric was 1 % off). And note the fence: this package does **not** index multi-phase patterns, so a second phase means subtracting the solved one first |
| `INDEX_BRAVAIS_AMBIGUOUS` | Refine in the higher symmetry because it was reported. The stated system is the conservative one; refine there and *test* the higher one, never the reverse. A disagreement between gemmi and spglib is information, not a bug — their tolerances are different kinds of number (a Le Page obliquity in degrees against a `symprec` in Å) and disagreement is what genuine pseudosymmetry looks like |
| `INDEX_VOLUME_UNPHYSICAL` | Quote the cell. It is outside what these data can support — below a single atom's exclusion volume, or clear of Smith's (1977) envelope for the number of lines observed |
| `INDEX_SUPERCELL_REFUTED` | Quote the larger cell, or read its old rank as evidence for it. A smaller reported cell explains the same lines, and the extra lines this one needs that no extinction could remove are seen no more often than chance, so it now sits below that cell (the `supercell_refuted` caveat, refuting). The counts are on `supercell_checks`. Only a real superstructure too weak to pick escapes the test, so look at the pattern at `absent_two_theta` if the chemistry predicts one. (Measured: on the finished acceptance searches it put brucite's and 11-BM NAC's truths first, and it kept every truth tested as a child, the lowest at p = 0.0072) |
| `INDEX_Z_NOT_INTEGER` | (warning, with `formula=`) Drop the candidate for it. Its volume holds a fractional count of formula units by Hofmann's (2002) volumes, and `value` is that Z. It fires past 8 % from a whole number, twice one crystal's scatter, so a correct cell can fire and Z above 6 never does. Check the formula (solvent, a counter-ion), then suspect a sub- or supercell |
| `INDEX_NOT_VALIDATED` | Read a `medium` as a near-`high`. No pattern was supplied, so nothing tested any candidate against the whole profile, and the figure-of-merit panel is blind to lines beyond the first twenty, to impurity content and to predicted-but-absent reflections. Pass `data=` and `instrument=` |
| `INDEX_VALIDATION_FAILED` | (warning — on the candidate's `lebail.diagnostics`) Read this candidate's Le Bail numbers as a judgement, in either direction. The validation *fit* raised (the message names the exception), so `lebail.rwp` is inf and its `status` is `failed`: nothing was measured, which refutes nothing. It is evidence about the candidate, not about the search — but check the instrument before discarding the candidate, because a mis-declared profile or a wavelength on an absorption edge fails every candidate alike, and a run whose validations all fail this way is telling you about the setup, not the cells |
| `INDEX_BUDGET_EXHAUSTED` | Read the answer as covering the requested search. The ceiling (`quick`'s default, or a declared `total_budget_seconds`) bound, and the result covers what was *reached*: `systems_searched` + `search_complete` distinguish three states — searched (present, `True`), truncated (present, `False`), and not reached (absent; the diagnostic's `where` names them) — and candidates whose validation never ran read `not_validated` (capping), never `validation_failed` (refuting). Units run system-major (WP-1042), so what a binding ceiling cuts is trailing low-symmetry *systems* for every engine equally, never a whole engine — a candidate from a completed system keeps all its finders. The message also distinguishes the slice-only case: the run finished under its ceiling but one or more validation fits exhausted their equal slice of the remaining clock. A user cancellation never writes this code: a stopped run is not a budget statement |
| `INDEX_SINGLE_ENGINE` | (info) Read `low` as "refuted". One engine ran, and agreement between independent searches is what confidence measures — so every candidate of a one-engine run grades `low` *structurally* (fewer than two finders), which means "unconfirmed by construction". It is a diagnostic rather than a caveat because a capping caveat cannot explain a floor `grade()` produces before caveats are consulted. Re-run with the default engine set for a gradeable answer |
| `INDEX_CELL_SYSTEMATIC_UNQUANTIFIED` | Quote a Bragg-Brentano cell to its esd. The esd is a *precision* from the line positions; the goniometer radius alone carries **≈ ±85 ppm** that no esd reports, because the data cannot identify it (Rwp moves 0.029 points across 180–320 mm) |
| `INDEX_CANDIDATES_TRUNCATED` | (info) Read the reported list as everything the search produced. It is the top `max_candidates` of a larger merged set, and the message says how many ranked below it — the cap exists because each reported candidate is priced a Le Bail fit, not because the rest were judged. Its second clause names any (engine × system) unit that returned a **full pool** (five times the reported cap since WP-1046); that clause is a flag rather than a count, because how many distinct lattices sat behind a discarded harvest is not knowable without deduplicating one the search already dropped. Raise `max_candidates` to see further down — it raises the pool with it, and the cost is the validation fits |
| `INDEX_PRIOR_USED` | (info; a warning when a prior lay outside the axis box, naming the value to pass) Read the answer as unsteered. It *was* steered — this diagnostic names each declared prior and its fate — but steering changed only *when* things were searched and what seeded the stochastic engine, never a range, a system set, or a rank: prior-only candidates are appended **after** the ranked list and never enter the Borda ranking. A candidate whose `found_by` is `["prior"]` alone is stated-and-unconfirmed — the ordinary agreement caveat grades it down, so treat it as your own hypothesis checked against the lines, not as a finding (WP-1045) |

## 7d. The closed loop: from a pattern of an unknown phase to a refinement

This section closes the loop between `index_pattern` and `refine`.

**Before the first search, ask for the cell or infer it** (Measured: solution
case 1: the blind search never found the person's cell).
Ask for a cell range or candidate cells. When the person has given
the chemistry (formula, Z or density, solvent), infer a volume window with
`SearchSpec.from_formula(formula, z=…)`, say so, and pass `formula=` too. Declare a candidate cell in
`prior_cells` with `max_d_axis` above its longest axis.

**These names are provisional, and the answers they return are versioned.**
Indexing is under active development, so everything under `rietx.indexing` and
every answer type in `rietx.schemas.indexing` may change in any release — the
[compatibility promise](https://rietx.org/using/compatibility.html#provisional-by-declaration)
has the detail. Two things do not move with them:
`capabilities().indexing_thresholds_version`, which is what the gates below are
versioned by, and the serialized shape of an `IndexingResult`. So a tool loop
that *reads* an answer sees any observable change as a version bump; one that
imports these types should pin an exact version.

**How long will this take?** The default answers this itself:
`index_pattern` resolves the **`quick` preset** — every engine, every requested
system, and a whole-run ceiling (`SEARCH_PRESETS["quick"]`) covering search,
probe and validation, with each validation fit drawing an equal slice of the
remaining clock. A run that hits the ceiling says so
(`INDEX_BUDGET_EXHAUSTED`, §7c). Progress and a graded shortlist for every *completed* system
stream on the event ladder as the run goes (`events=`), so a useful answer
usually arrives seconds in. `preset="full"` is the
unbounded pre-1.0 behaviour — reach for it when a quick run reports truncated
or not-reached systems and the answer may live there. For the arithmetic, ask
`rietx.indexing.engines.estimate_ceiling(spec)` (CLI: `rietx index
--ceiling`): `budget_seconds` (default 30) is per **(engine × system)**, the
worst case is that arithmetic plus the probe plus per-fit validation (measured
0.6–44 s each), against measured typicals an order of magnitude lower, because
searches usually finish their systems early. Budgets are runaway guards, not
timers — this package's record has six point measurements where a longer run
never bought a better answer, and one where too little budget reported a wrong
centring, so bound generously and read the three states rather than shrinking
the search.

**State what you know.** You often hold something the search does not: an
isostructural analogue from a database hit, a homologue's cell, a family's
space group. Declare it (WP-1045) — `SearchSpec.prior_cells` /
`prior_spacegroups`, the same fields on the agent request's `search` and in
the GUI's Search controls — and the search runs the prior's crystal system
*first*, seeds the stochastic engine's starting basin with the stated metric,
and checks the cell itself against the lines. Three facts make this safe to
do liberally: a prior **steers, never gates** (no system dropped, no range
changed, prior-only candidates appended after the ranked list — a wrong
prior costs time, not truth, and that sentence is pinned by test); a *real*
prior is then found by the engines themselves, so `found_by` and the grade
keep their meaning; and `INDEX_PRIOR_USED` records what you assumed and what
it changed, so assumed knowledge can never read as measured knowledge. A
worked example — you suspect the specimen is isostructural with calcite
(R -3 c, a = 4.99 Å, c = 17.06 Å):

```python
idx = rietx.index_pattern(
    peaks, data=data, instrument=instrument,
    spec=rietx.indexing.SearchSpec(
        prior_cells=((4.99, 4.99, 17.06, 90.0, 90.0, 120.0),),
        prior_spacegroups=("R -3 c",)))   # trigonal jumps the queue; the
                                          # centring steers the prior's check
# the same controls survive a JSON round trip (a project document stores them):
# {"search": {"prior_cells": [[4.99, 4.99, 17.06, 90, 90, 120]],
#             "prior_spacegroups": ["R -3 c"]}}
```

If the analogue is right, the truth arrives in the *first* streamed
per-system shortlist instead of after the whole sweep; if it is wrong, the
final list is the one you would have had anyway, plus the record that the
prior was tried.

```python
peaks  = rietx.pick_peaks(data, instrument)           # fitted positions + σ
report = rietx.indexing.assess_peak_list(peaks)       # fit to index at all?
if not report.supports_indexing:
    ...                        # abstention. Do not spend a budget (§6)

idx  = rietx.index_pattern(peaks, data=data, instrument=instrument)
cell = idx.best_or_none()
if cell is None:
    ...                        # read confidence_caveats; do NOT take candidates[0]

phase = rietx.indexing.structure_from_candidate(cell)  # dummy atom, lattice group
result = rietx.refine(data, phase, instrument, mode="lebail",
                        plan="profile_only")

screen = rietx.determine_extinction_symbol(data, cell, instrument)
klass  = screen.best_or_none()          # an extinction *class*, never one group
if klass is not None:
    # any member fits the data equally well — that is what the class means
    phase = rietx.indexing.structure_from_candidate(
        cell, space_group=klass.space_groups[0])
```

Six things about that sequence are load-bearing:

1. **Pass the pattern, not only the peaks.** It is what turns whole-profile
   validation on, and validation is what catches the oversized cell no figure of
   merit sees. Without it every candidate caps at `medium` and the *result*
   abstains.
2. **`best_or_none()` returning `None` is the normal first outcome.** With no
   measured systematic shift it is currently unreachable to get `high` on real
   lab data at all — the engines widen their matching window by an *assumed*
   allowance and say so — and the fix is evidence (an internal standard, a
   calibrated `shift_allowance_deg`), not a bigger constant.
3. **Go through `structure_from_candidate`.** It supplies the mandatory dummy
   atom and, more importantly, defaults the space group to the **absence-free
   lattice group**. A plausible-looking space group would hide exactly the
   reflections whose absence is not yet established.
4. **The extinction screen answers the next question, and answers it as a
   class.** `determine_extinction_symbol` ranks the classes the lattice admits,
   each listing its space groups; the powder observable *is* the extinction
   symbol, so a returned class with three groups in it is a complete answer, not
   a hedge (§7e).
5. **Choosing inside the class is chemistry, not diffraction.** Any member can be
   handed to `structure_from_candidate` for the Le Bail or Rietveld step that
   follows — they predict the same reflections at the same positions. What
   separates them is what you know about the compound, or which one a structure
   solution works in.
6. **`cell` is the conventional setting** (monoclinic: b unique, β obtuse);
   the search's own is `engine_cell`. One lattice? `same_lattice` on `af`.

The reverse direction closes too. When a refinement's Layer 2 emits
`reindex_or_recheck_cell` — peak offsets beyond the linearisation radius in most
of the misfitting regions, i.e. the cell is wrong (or the calibration grossly
off) rather than slightly off — that action has something to call: pick peaks
and run `index_pattern` on the same data. Since WP-1054 it survives abstention,
which is where it matters most: the wrong-cell state abstains, and before the
fix it surfaced only a confident `add_impurity_phase` built from its own
displaced peaks. The action carries `refine_zero_shift` /
`refine_sample_displacement` in `alternatives` because the validity-radius
signature cannot choose between a wrong cell and a gross calibration error —
re-indexing is still the safe first move, because `index_pattern` searches
under its own shift allowance.

---

## 7e. The extinction screen (`ExtinctionScreen.diagnostics`, and each class's)

These arrive from `rietx.determine_extinction_symbol`, which runs *after* a cell
is in hand and answers the next question — which systematic absences the pattern
shows. Same split as §7c: a refutation lives on the class it refutes.

| Code | What it means you must not do |
|---|---|
| `EXTINCTION_GROUPS_NOT_SEPARABLE` | (info) Pick one of the listed space groups and call it the answer. They produce **identical** powder patterns by construction — a centre of symmetry, an enantiomorph or a mirror leaves no absence — so this is not weak data and not a tie to be broken by counting longer. Carry the list; `structure_from_candidate(cand, space_group=…)` accepts any member. The arbiters are chemistry (a polar or optically active compound cannot be centrosymmetric) and, eventually, which one a structure solution works in |
| `EXTINCTION_SYMBOL_AMBIGUOUS` | Read the ranked first class as the answer. It fires for three different reasons and says which: a runner-up inside the decisive ΔBIC margin, a leading class none of whose absences is **testable** here (each is outside the range, coincides with a line the class still allows, or sits where the class's own fit already puts a neighbour's tail), or classes a `max_classes` cap never fitted. Only the first is fixed by better data at the same setting |
| `EXTINCTION_FORBIDDEN_INTENSITY` | Keep this class. A position it forbids carries intensity its own Le Bail fit cannot account for (hkl and 2θ named). A held cell off by ~10⁻³ refutes the *true* class: pass `refine_cell=True` or Le Bail-refine the cell first. Two things it is not: a position under a neighbour's tail (untestable, WP-1077), and necessarily a violated absence — it can be an impurity line, so check the indexing result's `unmatched_observed`. A good ΔBIC does not excuse it: a testable position carrying intensity refutes the class however well it scores |
| `EXTINCTION_CONDITIONS_PARTIAL` | (info) Read `conditions` as the complete condition list for this class. The screen used the absence set itself, which is unaffected; only the human-readable reduction is short. Read `space_groups` |
| `EXTINCTION_SCREEN_FAILED` | (error) Read the empty ranking, or any class's absence from it, as evidence about the symmetry. The *reference* Le Bail fit of the absence-free lattice group raised (the message names the exception), so no class was screened at all — `screen.status` is `failed` and there is nothing to rank. This is about the cell, the instrument or the data, never about one class: every class would fail the same way. Validate the cell first (`index_pattern` with `data=`, §7d's sequence) and check the wavelength is not on an absorption edge |

Three things about the screen that change how you use its answer:

1. **The score is a nested comparison, not Rwp.** A class with fewer absences has
   more reflections and can only fit at least as well, so Rwp ranks the
   least-constrained class first every time. `delta_bic` is BIC(class) −
   BIC(absence-free lattice); **negative favours the class**, and the difference
   between two classes' values is itself a ΔBIC. Measured on a synthetic P 2₁/c
   specimen: the true class and its screw-free partner differ by 1e-5 in Rwp and
   by 24 in ΔBIC.
2. **`n_added` counts only *testable* absences**, so a class whose extra absences
   all hide under allowed neighbours earns nothing for them. Read `n_testable`
   beside `n_absent`: if it is zero the class is a hypothesis these data cannot
   address, whatever its Rwp; if it is `None` the class was never fitted, so the
   question was not asked. The third clause of testable — the class's own fit
   must leave the window below the detection threshold — is what stops a
   badly-modelled peak tail refuting a true class, and it is measured: on
   certified corundum, sham positions 1–3 FWHM below an allowed line, carrying no
   reflection at all, clear the same 3σ test on 40–50 % of probes.
3. **The absence-free class winning is a result, not a failure.** On NAC (I 2₁3)
   it is the *correct* answer: I-centring already extinguishes the very
   reflections the 2₁ screws would, so those screws are invisible in principle.
   It is a *wrong* answer when the shared profile fit is bad, and
   `ExtinctionScreen.profile_rwp` reports how good that fit was: on certified
   corundum 0.259 over 20–90° (`R - c -`) and 0.262 over 5–150° with declared
   widths (`R - - -` wins). It bounds trust and does not choose. Give it a range
   and a width law its profile fit can match before reading a refutation.

**`where` names the paths on every guard code, `HIGH_CORRELATION` included**
(WP-1007). Read `d.where`; never split a message like `"a ~ b (ρ=+0.994)"`.

```python
for d in result.diagnostics:
    if d.code == "HIGH_CORRELATION":
        a, b = d.where          # the degenerate pair, as dot-paths
```

And ask the package what it can do rather than assuming: `rietx.capabilities()`
returns the live registries — backends (with whether each optional dependency is
importable *on this machine*), solvers, plan presets with their `when_to_use`
text, modes, anodes, the pattern formats `read_pattern` opens, and the six
versioned contracts (`schema_version`, `report_thresholds_version`,
`event_schema_version`, `project_format_version`, `textdoc_format_version`,
`indexing_thresholds_version`). Its `features` map is derived
from the tree, so `features["indexing"]` tells you whether *this* build has an
indexer instead of leaving you to try one.

Two of those flags are about **speed rather than capability**, and they are the
ones to read before reporting that a refinement is slow.
`features["compiled_kernels"]` says whether the compiled peak kernels loaded
here (the `rietx-kernels` wheel is required, but a `--no-deps` install may
lack it), and `compiled_kernels_unavailable` says why not.
`features["compiled_kernels_active"]` says whether the next refinement will use
them — `RIETX_COMPILED=0` switches them off without a reinstall. Both false on
a slow fit is an explanation; both true is not, and the answer is somewhere in
the stage plan. Nothing else changes: numbers agree to
the last place or two, and the accumulation is bit-for-bit identical.

---

## 7f. Two consumers, one answer: the gate and the evidence (WP-1043)

The gate exists for **unattended** use: a machine that cannot weigh evidence
must never be handed one cell confidently, so `best_or_none()` stays as strict
as it is and nothing in this section loosens it. But the gate's three levels
compress the judgement's *inputs*, and a consumer that can reason — an LLM in
a tool loop, or a human at a screen — wants the inputs, not only the verdict.
The design call this section serves: give them all the information, and let
the judge, human or machine, be the judge.

**What a reasoning consumer reads**: `result.evidence()`, the companion to dump
beside the answer. Per candidate: every caveat with its
`refuting`/`capping` **kind** (the split `confidence_caveats` alone withholds);
the panel members that ranked, with values, beside `fom_undefined` — the
figures that could not be computed, each *absent with its reason*, never
silently zero; and the whole-profile numbers together — `lebail_rwp` and both
detector counts, surfaced so a reader can see when a detector has failed (as
it measurably does on magnetite's rival, whose fit buys a negative background
— §7c's row), and never a thing to score on. Result-wide: what the search
covered (`systems_searched` + `search_complete`) against what the list
supports (`systems_supported`). The visual check is part of the answer, not
documentation of it: `rietx.viz.plot_indexing(result, peaks, data=...,
instrument=...)` draws the ranked tick rows and the Le Bail panel from the
result alone.

**Worked example — fluorite, why the two reads differ.** Seventeen usable
lines on certified CaF₂ (Fm-3m, a = 5.4631 Å). The unattended read:
`best_or_none()` is `None` — correct, and exactly as strict as ever, because
the `fom_panel_reduced` caveat (capping) holds every below-twenty-line
candidate at `medium`. The reasoning read: the certified cell at rank 1 at
−18 ppm, found by every engine that ran, Le Bail-validated `converged`, four
systems searched to completion, and the *only* caveat on it is the reduced
panel — M₂₀/F_N absent for cause, the coverage and reversed members all
ranked. A consumer that can weigh that is entitled to adopt the cell with its
eyes open; before WP-1043 the same list was refused outright — the old gate
conflated scoring (twenty lines, where M₂₀ is *defined* and F_N is scored) with searching
(`MIN_LINES_PER_DOF` per system: seventeen lines are seventeen-fold
over-determined for a cubic metric), and neither consumer got anything.

**Worked example — bethanechol set F, the truth already at rank 1.** On the
one externally graded benchmark, the published P2₁/n cell comes back ranked
**first** on set F (measured 2026-08-06: `trial_error` under the paper's own
manual-mode conditions, −340/+56/+67 ppm with β out by 0.012°) — and the sets
are bare positions, so there is no profile to validate against and a
single-engine find grades `low`: the gate can never promote it. The evidence
view is where that answer *exists* for a consumer — rank 1, its figures, and
caveats that say precisely what was not checked. An unattended pipeline
correctly gets nothing; a reasoner gets the answer with its qualifications
attached.

One qualifier on everything above, and on any scoreboard number you quote:
nine of ten real-data corpus datasets sit at **≤ 2 free metric parameters**
(0 orthorhombic, 1 monoclinic, 0 triclinic), so every measured claim here is
about high-symmetry lattices until the corpus moves — post-v1 by scope call.
