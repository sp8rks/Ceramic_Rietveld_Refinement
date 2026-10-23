# 4/4b. The evidence behind the judging rules

Load it when a rule in §4 (judging a fit) or §4b (declaring the deliverable)
needs its measurement: before you override one, or quote a number it governs.

*A reference file of the `rietx` skill. The body it belongs to is
[`SKILL.md`](../SKILL.md); section numbers are the ones the body cites.*

## Step 9 — what `max_shift_over_esd` separates

McCusker et al. (1999) §7 calls a refinement converged when max|Δθ|/esd ≤ 0.1.
The band is quoted from the paper and gates nothing here, but read the number
on **every** solve, `converged` included. The solver stops on the cost, and a
cost that has stopped falling says nothing about a parameter walking a flat
direction: on a 25–50° four-phase QPA scan all six stages reported `converged`
with the number at 70.1, Fe's Biso at −165 Å² (the campaign's run) along a scale·exp(−2Bs²) ridge,
and 4.02e-05 once that Biso was bounded (issue #204). So a large value on a
converged stage is the signature of an unbounded or degenerate direction: look
for a parameter without the range its field declares, or for a
`HIGH_CORRELATION` pair. After `STAGE_MAX_ITER` it says *how far* the solve was still moving, in esds: just over the band is nearly there, and one stage stopped mid-flight read ≈14.

## Step 9 — `status` is the optimiser's exit; `usable` reads both channels

`result.status` says how the solver stopped and claims nothing about the fit:
issue #243's reproduction on the bundled NAC fixture, profile unseeded, returns
`converged` beside `MODEL_FAR_FROM_DATA` (Measured: Rwp 2.15 on 1.6.0.dev0).
Quality is `result.diagnostics`. A batch driver branches on `result.usable`,
which is `status == "converged"` with no diagnostic at level `"error"`; `False`
means read nothing, and `True` still owes every warning its answer (WP-1336).

## Step 9 — the width census runs on the fit

`PEAK_WIDTH_LAW_MISMATCH` also fires on a refinement. The indexing census (the
median FWHM of the 12 most prominent lines) is compared with the *fitted*
width, instrument plus size and strain, of each phase the data can see, and
fires when none comes within 3× either way; `value` is the ratio, `where` the
closest phase. A phase below `PHASE_SUPPORT_SIGMA` is left out, so a runaway
width on a phase at its scale floor cannot silence it. Above 3 the data is broader than the model can make it: free the
phase's `lor_size`/`lor_strain`, or calibrate the instrument, before quoting
intensities. Below 1/3 a width term ran away. A phase with a Stephens
`microstrain` block is not judged (Measured: synthetic LaB6, `lor_size` 0.1°
against √W ≈ 0.016°, fired at 6.3 with no size term and silent with it freed;
silent at 1.01–1.32 on the NAC, SRM 660c and FAP examples, WP-1336; fired at
4.0 beside a 7e-6σ phase whose width came within 3×, silent when that phase
was visible at 7σ).

## Step 12 — the geometry table's esds

McCusker §11 ranks the geometry with the profile fit and above every R value, so it is read before step 16. The number of rows naming an atom is its coordination number.

`stderr` is propagated through the *whole* covariance, as McCusker §10 requires of any derived quantity. `stderr_diagonal` beside it ignores the correlations. Quote the first; use the pair when
you need to say how much the correlations mattered (measured on 11-BM NAC,
dropping them moves an esd by ×0.71 to ×1.15, in *both* directions, so a
diagonal esd is not the conservative choice).

`None` covers all four ways a number is unavailable: no covariance behind the
row (an evaluate-only pass), no free source, a quadratic form that reaches zero
by cancelling, and a straight angle where linear propagation does not hold. An
esd of 0 on a symmetry-fixed 90° angle would be a claim about precision rather
than a statement about constraint.

`write_refinement_cif` writes the whole table as `_geom_bond_*`,
`_geom_contact_*` and `_geom_angle_*` loops, with the symmetry codes resolvable
against the `_space_group_symop_operation_xyz` loop it writes beside them.

## §2 rules 4-5 — the two Le Bail measurements

**Alternate under a cap, and keep the best pass.** On PbSO4 pass 1 ends at Rwp 20.756 % with an unphysical Caglioti **V = +0.0615**; passes 2-4 reach 10.247 % with the curve sane. On Tb2BaCoO5 a later pass rose, 17.3 % → 18.7 %. `plan.lebail_passes` stops at the first pass that does not lower Rwp and keeps the best. `LEBAIL_ALTERNATION_STOPPED` names the stop; `non_monotone` or a cap hit is no fixed point. Rwp % per pass (Measured: 11-BM LaB6+cBN, `profile_only`): exact cells 16.821, 16.907, pass 1 kept; 0.3 % off, a fixed point at 16.967; 2 % off, 230, 207, 175, 195, pass 3 kept.

**A known structure is no Le Bail job.** One staged Rietveld calibration took 43.8 s against ~40 min of Le Bail (#210).

**Seed the background first.** `auto_background` chooses the knot spacing or the Chebyshev *order* but starts every coefficient at **0.0**, so the first `lebail_update` runs *before* the background is fitted. It partitions `max(y_obs − 0, 0)` (the whole pedestal) and gives it to the Bragg reflections. Measured on a synthetic pattern whose background is 5× its
strongest peak: cycle one claims **571×** the true Bragg intensity. `seed=True` starts them at a low percentile of the counts.

**The cell is the weaker half.** Peterson (2005, *Powder Diffr.* **20**, 14)
fitted triclinic tricalcium silicate at NSLS X7A. The Le Bail fit won on both
indices reported (χ² 16.46 against 22.81, R_p 2.34 against 3.52 at ambient) and
its cell parameters wandered over a heating and cooling series, while the
Rietveld cell from an admittedly imperfect model stayed consistent. The cause is
reflection density rather than low symmetry alone.

**Measured at the other end of that variable**, one range and one instrument
treatment, three modes: 11-BM LaB₆, 2-40°, 55 reflections, mean FWHM 0.0097°,
**0.014 reflections per FWHM**. Rietveld a = 4.1568414(45) Å, Le Bail
4.1568425(44), Pawley 4.1568431(44). They spread 0.4 ppm, two-fifths of one esd, and the esds agree within 3 %. Le Bail also won on Rwp there (0.0861 against 0.0879), so a better Rwp does not show the cell is wrong or right. Where reflections crowd, check the cell against a structural model; where resolved, skip it.

**Multi-phase Le Bail** works since v1.0. The shares sum to 1 across all phases at every channel (measured Σ calculated / Σ observed excess **1.79 → 1.0000** on LaB₆ + CaF₂, single-phase path bit-identical). One caveat is the method's own. The data do not split the intensity of two phases whose reflections *coincide*, so the partition splits it by the current model, a starting value. Treat a high multi-phase Le Bail Rwp as a reason to check the
seeding above.

## §3 rule 8 — what tying three oxygens actually bought

A constraint *removes* a parameter and so raises the observation-to-parameter ratio. A restraint adds a weighted observation and leaves the count alone. The two cases worth reaching for are
McCusker's: equal displacement parameters across atoms in the same
environment, and occupancies summing to a known total.

**Check the premise in the free refinement, not with Rwp.** Compare each pair of free values with their combined esd, √(σa²+σb²). If every pair differs by less than about two of them, the
data does not contradict the claim that they are one parameter. Where one pair
differs by more, the atoms are saying they are *not* in the same environment, and
tying them replaces a measurement with an assumption. The test ignores the
correlation between the two fits, so it is lenient when that is positive.

Fluorapatite's three phosphate oxygens, tied as one displacement parameter: 20 →
18 free parameters, 287.5 → 319.4 points per parameter (5 750 channels, not independent
observations; McCusker §9), and B(O) 0.3647(1513) / 0.6016(1590) / 0.5377(1078) Å²
free against 0.5150(754) Å² tied. The free values differ pairwise by 1.08, 0.93
and 0.33 combined esds, and the tied esd is tighter than the best of the three. Rwp moved by 0.05 % of itself, so it cannot say whether the constraint helped or hurt.

Every tie is recorded as a `set_tie` history node and restored by a checkout, so
a constrained protocol replays as one. Symmetry outranks a user tie: a
cell axis the space group already ties and a coordinate behind its site-symmetry
direction are refused by name rather than silently ignored. A `lebail`/`pawley`
mode-fixed path is refused too, because the mode already fixes it.

## Step 13 — why the inflation is not a measurement, and why the trio travels

Scaling variances by GoF² alone is "highly questionable" (Schwarzenbach, 1989), which is why the trio travels instead of a rescaled esd.

The Bérar-Lelann factor has an expected value of √1.269 ≈ 1.13 even for white residuals: chance same-sign neighbours give E[S″]/E[S] = 1.269 under the
paper's eqs (10)-(12) (`optimize.statistics.berar_lelann_factor`; quadrature,
checked by simulation). It is one scalar applied to every esd, so it says how
correlated the residual is, not how wrong any one parameter's esd is.

`report.identifiability` quotes raw χ²_red, the inflation (already in every quoted esd, dividable back out) and Durbin-Watson side by side, plus the δR line (`delta_r_slope` / `delta_r_intercept`: sorted Δ/σ against
normal quantiles; slope ≈ 1 and intercept ≈ 0 on honest σ, slope > 1 when σ is
underestimated).

The round robins measured why the ingredients matter: the same data refined
under different protocols spread by up to ×17–25 of the quoted esds on cell
dimensions (Hill, 1992, *J. Appl. Cryst.* **25**, 589; Hill & Cranswick, 1994, *J. Appl. Cryst.* **27**, 802),
explained by §3's first degeneracy row (the cell compensating 2θ-scale errors). Durbin-Watson is in the trio because serial correlation makes the raw esds untrustworthy, and its d stays discriminating where Rwp and
GoF do not (Hill & Flack, 1987, *J. Appl. Cryst.* **20**, 356).

## Step 14 — the exchange row, the swap, and the ridge

**The row and its verdict.** An `exchangeable=True` row says a **held**
parameter's signature is reproducible inside the fitted span (`r2` → 1) *and*
that a fitted partner stands many σ from its null. An E2-shaped answer reads
"converged, but the fitted zero_shift is exchangeable with the held
sample_displacement — **this fit** cannot tell you which is physical". Measured,
the fit carrying a planted displacement inside a compensating zero and its clean
reference differ only in this row: χ²_red 1.012 against 1.010, R² identical to six decimals, the partner at 168σ against 1.5σ.

**Why R² cannot decide it.** R² measures column overlap alone, not whether the counts separate the pair. On real SRM 660c a pair at R² 0.9977 comes apart decisively: χ² 4.0752 (zero only) against 3.4890
(displacement only) on 5332 points, with the zero-only model biasing *a* by
+100 ppm.

**The decision band, and hedging a won swap.** `RIVAL_DECISIVE_MIN_CHI2_RATIO`
is 1.10, read on the losing rival's χ² over the winning rival's. On the round-3
eval's solvable control (rivals decisive at 1.1679, the SRM 660c pair above) the
agents that ran the swap recovered the true displacement and still declined or
hedged the answer: the control went 0/7 valid. Below the band the pair is
unresolved: the two real tie states measure 1.0075 and 1.0001.

**Why the clause is on the statistics block as well as in the summary.**
Measured consumers pipe the answer to a file and grep the statistics back, and
the summary string is what those greps drop: the licence reached agent context
in 2 of 12 cells from the summary, and 4 of 4 from the statistics block once
placed there. `None` there means no report was built or nothing crossed a
comment threshold, never a verdict.

**The ridge.** Freeing the held parameter alongside its partner and refitting
lands on §3's degenerate ridge and reports the unconstrained combination at a
*better* Rwp. Measured over 30 agent runs, seven of twenty position cells took
it. The swap runs each rival **alone**; the ridge runs them **together**.

## Step 16 — what background-subtracted Rwp separates

Rwp is a relative number. Eighteen refinements of one PbSO₄ dataset returned Rwp 8.2–20.0 % (Hill 1992). It is dominated by the strongest peaks and the background level, so it ranks fits of the same data over the same channels and nothing else.

A sharp LaB₆ fit and one under 0.6° of broadening both report Rwp **0.0137**,
and background-subtracted they read 0.0490 and 0.0768. Raw Rwp is flattered by
whatever the background carries (89 % of the observed intensity in both), so
the number that separates two fits is the subtracted one. The literature says
the same twice: Toby (2006, Fig. 1) shows identical model discrepancies reading
Rwp 23 % with no background and 3.5 % with one, and Hill's 1992 round robin
recommends quoting the background-subtracted forms for exactly this comparison.
It is published on every report and deliberately never mentioned in `summary`,
because every background-dominated pattern would trigger it, converged ones
included.

## Step 17 — a trace phase's R_B

Neither index is weighted, so a reflection the fit barely constrains weighs as much as one that dominates it. The weighted R_WI of Cox & Papoular (1996, *Mater. Sci. Forum* **228–231**, 233) answers this and is not computed here. A minor phase's windows also sit under the major phase's peaks and get the counts the major phase failed to describe. Measured
on 11-BM NAC with 1.34 wt % CaF₂: 0.048 for the major phase against 0.377 for
the impurity, all of the latter in four reflections at I(obs)/I(calc) of 2.2 to 2.3,
each under a strong NAC peak. Read it beside `qpa.phases[].weight_fraction`, and
treat a trace phase's value as a question rather than a measurement.

`write_refinement_cif` writes them as `_refine_ls_R_I_factor` and
`_refine_ls_R_factor_all` on each phase's own block, beside a
`_pd_proc_ls_special_details` that states the esd method in full, as McCusker §10 requires: the base estimator √diag(χ²_red·(JᵀJ)⁻¹), then the Bérar-Lelann factor it was multiplied by.

## §4 — adding a parameter: the t-ratio before ΔBIC

Schwarz's BIC counts N independent observations. A powder residual is serially
correlated, so at tens of thousands of channels the reward N·ln(χ²_r/χ²_f)
outvotes one ln N for almost any gain. Issue #270 measured it on four ~49 500-channel
synchrotron fits, each freeing one occupancy. These are pre-1.6 measurements, made
with the run-sum esd inflation that #674 replaced with Bérar and Lelann's § IV
correction; `esd_inflation` now reads about 0.8-0.9 of the column below, and the
fits were not re-run:

| fit | t = value/esd | ΔBIC at raw N | Hamilton | `esd_inflation` | Durbin-Watson |
|---|---|---|---|---|---|
| 1 | 0.76 | +36.2 | justified | 10.16 | 0.43 |
| 2 | 1.89 | +211.0 | justified | 7.13 | 0.58 |
| 3 | 1.05 | +71.1 | justified | 7.89 | 0.57 |
| 4 | 1.01 | +80.9 | justified | 8.59 | 0.61 |

None reaches 2σ, and both statistics call all four decisive. Charged at
N/f², with f the fit's own `esd_inflation`, all four turn negative. For one
parameter that count makes ΔBIC close to t² − ln N_eff, so the verdict and the
esd agree. Over 27 last-freed parameters across the acceptance fixtures, N/f²
refused every |t| < 2.3 and admitted every |t| ≥ 2.6 (also pre-1.6, not re-measured). The rule this replaced
was measured on a 7251-channel corundum pattern, where Hamilton's test at raw N
blessed an inert Stephens block's 0.16 % χ² gain. At N/f² both tests refuse
it.

`suggest()` predicts ΔBIC at N/f² before you free anything. After the fit,
compare the two fits:

```python
trial = ref.branch()
trial.run_stage(data, rx.Stage("occupancy", ["phases.0.atoms.2.occ"]))
c = rx.report.compare_freed(ref, trial)
[(p.path, p.t_ratio) for p in c.freed], c.delta_bic, c.delta_bic_raw_n
```

Read the t-ratios first. A disagreement between the pair is information. A
block of several parameters can carry a positive joint ΔBIC while no member's
|t| reaches 2, which says the block moves the fit and no single member is
measured. A ΔBIC far from t² − ln N_eff for one parameter means f moved between
the two fits. `predict_then_verify` carries the same record on
`VerificationOutcome.comparison`, beside its 1 % χ² rule.

By hand, for a pair `compare_freed` refuses as not nested, remember that
`result.statistics.chi2` is reduced. Multiply each by its own N − P before
`rx.report.delta_bic`, and pass `n_effective=`. The reduced pair costs about
one unit of raw-N ΔBIC per added parameter.

## §4 — comparing against another code

Adopting another code's protocol means mirroring its refined-parameter set, its
held parameters and its excluded regions, then checking that the channel count
matches before believing any Rwp comparison.
Measured on the GSAS-II fluorapatite tutorial: guessing a plausible protocol
gave Rwp 16 % and a +390 ppm cell, while mirroring the converged `.EXP` gave
9.73 % against GSAS's 10.05 % on an identical 5750 channels.

## §4b — Phase ID: the unmatched list and the Le Bail-gap read

`report.unmatched`'s `kind="unmatched_obs"` entries are the strong lines your
phase set does not produce — an unmodelled phase's signature, distinct from
resolution-limited noise. `report.lebail_gap` is the structural-against-profile
triage: it re-partitions the per-hkl intensities at the frozen converged state
and reports both Rwp. A `ratio` ≫ 1 means positions and profile alone account for the pattern, so every line is indexed and phase identification is safe **at any absolute Rwp**.

`unmatched_calc` asks the same question from the other side and only answers it
in Rietveld mode. Le Bail and Pawley extraction takes each intensity from
`max(y_obs − y_bkg, 0)`, so a reflection with nothing under it is assigned
nothing and most of the residual the detector looks for goes with it. What
survives is a noise excursion near a tick. Measured on a synthetic LaB₆ pattern
(WP-1024): 19 of the certified cell's own 28 reflections
and 84 of a doubled cell's 153, 68 % against 55 %, so it does not separate them. The count that does is `LeBailValidation.predicted_but_absent`, which
integrates net intensity above the fitted background over each predicted
position. The blind direction is the one de Wolff's M₂₀ has, and it is why
Oishi-Tomiyasu (2013, *J. Appl. Cryst.* **46**, 1277) reversed the figure.

The clip at zero is rietx's, and it changes what a bad background looks like.
Unrectified, the method returns **negative** intensities wherever the background
is overestimated, which David & Sivia (2002, *Structure Determination from
Powder Diffraction Data*, ch. 8) found and Le Bail's retrospection passes on.
So a background set too high hides in intensities pinned at zero. A background driven too
*low* is the documented pathology on the other side: `absent_reflections` found
0 of 163 absences on a wrong candidate whose co-refined background had gone
negative.

## §4b — the QPA background measurement in full

Fractions ride on scales, so the rows that decide a QPA are the ones that bias
scales silently. `report.background.absorption`, keyed by parameter path, is
the detector: the block projection R² of each structural parameter's Jacobian
column onto the background column span sees §3's scale↔Biso↔background
degeneracy. A negative Biso is that same error
laundered through a scale. The Le Bail gap reads the *other* way here than for
phase ID: a large ratio means the intensity model is wrong, and wrong
intensities **are** wrong fractions.

LaB₆, broad peaks, same data both times. Fitted with a 1°-knot unpenalized
spline the refinement reports Rwp **0.08831** and GoF 1.019, against **0.08942**
and 1.022 with a correct Chebyshev-6. The wrong background wins on every agreement index, and its displacement parameters come back 0.935 and −0.184 Å²
against a truth of 0.5, one of them negative, where the correct background
gives 0.687 and 0.621. `worst_absorption` reads 0.46 against 0.08, either side
of the 0.25 at which `BACKGROUND_ABSORPTION` fires. No agreement index and no plot distinguishes the two fits (the over-flexible
residual is white noise inside ±3σ). `BACKGROUND_ABSORPTION` does, and so does
the negative B. No default bound stops B at zero since 1.7, so `BOUND_HIT` is
silent.

The **too-stiff** side has no guard of its own. On round-robin sample 2, a
1°-knot P-spline with its penalty ten thousand times too stiff moved corundum's
Biso 28 % with no background code firing, at 1.17× the Rwp and with the
fractions within 1 wt % (WP-1454). Up to 1.5.0 that was what high counts did to the
default λ, which was measured in intensity units. λ is a pure number now, and
the same λ means the same stiffness at any count level. A λ tuned by hand
against an older version, such as λ ≈ 1/σ², does not carry over.

The table lists entries below `BACKGROUND_ABSORPTION_NOTABLE` too; the diagnostic carries the verdict. A pairwise ρ reads ~0.2 per coefficient while the block absorbed 46 %.

## §4b — the two QPA rules the round robins own

Madsen et al., 2001, *J. Appl. Cryst.* **34**, 409; Scarlett et al., 2002, *J.
Appl. Cryst.* **35**, 383.

- A Rietveld σ(W) reflects only the fit's mathematical precision and is "not
  necessarily related to the accuracy". Judge a fraction against the published
  participant spread, never against its own esd.
- Microabsorption is the largest physical obstacle to X-ray QPA and "may prove to be insurmountable in some circumstances". A Brindley correction applied
  where none is needed *reduces* accuracy (their sample 1 and synthetic bauxite;
  `BRINDLEY_OUTSIDE_REGIME`).

## §4b — a short range measures a scale only together with its B

A phase's intensity is scale · exp(−2B·s²). On a range where its reflections
sit at one d-spacing, the data give one number for the pair, and a fraction
read from it is conditional on B. (Measured: WP-1534's synthetic rebuild of #204's 25–50° Cu Kα
four-phase scan. bcc Fe has one reflection there. With B free it walked to
−150 Å² and returned 0.000 ± 0.000 wt%. With B held it returned 1.284 wt%,
against 1.211 true.) The stage now holds that B and fires
`SCALE_B_INSEPARABLE`. It holds too where a phase has fewer reflections than
scale and displacement parameters, as fluorite's two sites on (111) and (200)
over 25–33°. (Measured: on IUCr CPD sample 1c, unbounded, B(Ca) +99 and
B(F) −111 Å² and fluorite 0.0 wt% against 1.36 weighed, before the hold;
1.32 after.) Quote the fraction together with that condition.
Reflections a little apart in d are not held, and their esd is honest but
huge. On the same fixture, fluorite's error passed through the normalisation
into every fraction as ± thousands of wt%. Read a QPA esd that large as a
limit of the fitted range, not of the specimen, and widen the range before you
quote.

## §4b — a trace phase's esd describes one basin

`weight_fraction_stderr` is the curvature of χ² at the converged point, so it
describes the basin the fit stopped in and no other. A weak phase's scale
trades against its width: broadened far enough, its peaks become a hump the
background shares, and its scale can then grow at almost no χ² cost. That ridge
can hold separate basins, each with ordinary curvature and a tight esd, and the
fit reports whichever it reached.

`QPA_ESD_UNAVAILABLE` (warning) is a different `None`: every
`weight_fraction_stderr` is absent because the scale `where` names has no
gradient at any value, so the data cannot measure it. Do not propagate the
scale esds by hand. Every fraction divides by Σ S·ZMV, so a propagation without
that term quotes each fraction as if the phase were known, which an agent did on
16 of 48 patterns of a real series. The fractions themselves are the fit's.
Remove the phase and refit for esds, or run `ref.profile_fraction(data, phase)`
for a range. A scale that refined to 0.0 keeps its esd, reads `at_bound=True`
and fires `FLOOR_HIT`, even when `PHASE_UNCONSTRAINED` is silent because the
scale is the phase's only free parameter. It usually means the phase is absent.

A lab Cu Kα in-situ pattern gave one phase at 1.41 ± 0.65 wt% with no
diagnostic. Pinning its `lor_strain` on a grid and refitting everything else
warm found three reproducible basins, at 0 %, ~1.5 % and 98.7 %, within 0.011 pp
of Rwp, and the lowest Rwp belonged to 98.7 %. The pattern 100 °C lower spanned
0.636 pp around one minimum, so the case is per pattern. Another program gave 25.3 ± 0.5 wt%, in no basin, so the scan is the only evidence. No local statistic flagged it. On a real six-phase fit the
offending phase's `background_absorption` read 0.183 against another phase's
0.208, it was absent from `top_correlations`, and it was absent from the one
scale-bearing soft mode.

`profile_fraction` runs a width profile. It pins each of the phase's free width terms (`lor_strain`, `lor_size`,
`gauss_strain`, `gauss_size`; `axes=` to name one) at 12 FWHMs, 0 and then
log-spaced to half the fitted range, refits the rest warm on a branch, and
reads the fraction and the data's χ² at each:

```python
profile = ref.profile_fraction(data, "CaF2")   # 12 refits per free width term
profile.range_low, profile.range_high, profile.excess, profile.fit_admissible
[(p.fwhm, p.weight_fraction, p.delta_chi2, p.admissible) for p in profile.points]
```

The cut, `profile.delta_chi2_cut`, is the 95 % Δχ² for one parameter (3.84)
scaled by the same χ²_red and Bérar-Lelann factor every esd already carries,
so on a single quadratic basin it reproduces W ± 1.96 esd. `excess` is the
farthest admissible fraction from the fit's in units of that half-width, and
`QPA_FRACTION_UNDETERMINED` fires past 2. The axis is the width, never the
scale: at a pinned scale the refit reaches the hump basin only by broadening
the phase below `PHASE_SUPPORT_SIGMA`, where WP-1301 holds its structure, so the scan stops short.
The grid stops at half the range because on the full range the frozen peak
windows no longer cover the profile and `FROZEN_COMPILE_STALE` fires.
`fit_admissible=False` means a pinned refit beat the fit by more than the cut,
so the fit is not in the lowest basin along the ridge.

A synthetic trace of CaF₂ in LaB₆ (lab Cu Kα, a 10-count amorphous hump under a
six-term Chebyshev) reproduces the shape. The fit gives 1.19 ± 0.39 wt%. The
profile admits 0.86 % to 77 % in two basins separated by a barrier the data sees
(Δχ² 15 against a cut of 5.2), `excess` 99, and fires. Without the hump and with
five times the CaF₂, one basin at 3.8-3.9 % and `excess` 0.22: silent. By hand
the same scan is `ref.branch()`, `trial.set_vary([axis], False)`, then per value
`set_values` and `run_stage(data, rx.Stage("width_pin", []))`, with χ² = `chi2 · (n_points − n_free_parameters)`.

A width profile cannot see the ZMV family. A wrong multiplicity or setting (`SITE_SNAPPED_TO_SPECIAL_POSITION`, `SPACE_GROUP_SETTING_ASSUMED`) is a fixed multiplicative offset on one phase at an unchanged Rwp.

## §4b — the worked example that stops at GoF 2.97

LaB₆ pore proxy: a guest scatterer at the 1b site in the data only, host model
refined to convergence. Rietveld Rwp 0.0405, GoF 2.97 — a "bad fit" by GoF. The report suggests no action. Intensity carries 81 % of the misfit, in per-region errors of 9–18 % with **alternating sign**: (100) low, (110) high, (111) low. That is structure-factor interference, which scale, ADP and texture cannot produce; the summary names it un-modelled scattering contents. `lebail_gap.rwp_lebail` reads 0.0140 against 0.0405, a ratio of ×2.9.

Read by deliverable: phase ID is **done** — stop, at GoF 2.97. A structure
determination is **not**, and its next move is chemistry (what occupies the pores). Finer profile corrections cannot help.

## §4b — why no bar moves for non-ideal data

The gates auto-scale to information content. Measured: a zero error named at confidence 0.997 on sharp data draws silence and GoF 1.02 under 0.6° of broadening. Pushing finer corrections into a fit whose attribution
is resolution-limited changes numbers it cannot justify.

## §4b — the trajectory deliverable, and where its rows come from

Four codes on `SeriesResult.summary(deliverable="series")` carry the chain's
own rows. `SEQUENTIAL_PATH_DEPENDENT` is an ordering artefact — only a
`direction="both"` chain can produce one, so a one-way chain has not looked.
`SEQUENTIAL_PERSISTENT_FINDING` states a persistent count no per-pattern code
can, measured at **42 of 68** patterns on this ramp (`BOUND_HIT` on one cell, original run). `SEQUENTIAL_DISCONTINUITY`
flags either the science or a chain failure, and `verify_discontinuities=True`
tells them apart (below). `PHASE_UNCONSTRAINED` says the value is held, so its trajectory is the one you handed in. Apply the QPA background check **at every point** too: an absent phase took **40–96 wt %** at equal Rwp.

The row exists because an agent needed it and wrote it itself. Given 68 patterns
of a variable-temperature ramp, `rietx`, and "tell me what the cell does, and
flag anything you would not quote", a run recorded in full built its own
stopping rules and they were the right ones: model selection by ΔBIC and the
rival χ² ratio rather than by Rwp; the step at 430 → 440 °C verified by an
**independent cold refit** of both patterns; tan θ against cos θ to tell a cell
change from a specimen-height jump; a CaF₂ impurity used as an internal standard
to bound 2θ drift to ±27 ppm over 280 K; and the explicit split — precision on
the shape of a(T) at ±0.00015 Å, no accuracy claim on the absolute beyond
~100 ppm, *because nothing pinned the 2θ scale*. About 34 of its 90 calls went
into those checks. None of them is a fit statistic, and §4b named none of them.

Two are now the package's:

- **The cold-refit check is `verify_discontinuities=True`.** Each flagged step's
  two patterns are refitted cold and independently, and the diagnostic's `value`
  becomes the cold step over the chain's (1.0 a real step, 0 the chain's).
  Measured on that ramp, reproducing the run's own protocol: the chain takes
  11.6–12.0 s and the check adds 1–5 % (12.1–12.2 s) for four flagged steps over
  four patterns, and the real transition reproduces at **1.00**. The cost scales
  with the patterns flagged, not with the series length.
- **The rows are `SeriesResult.summary(deliverable="series")`.** In the same
  re-run, `PHASE_UNCONSTRAINED` fires on the impurity's cell in **40 of 68** patterns (re-run, WP-1301), the "would not quote" list the agent built by hand.

The two the package cannot supply stay the caller's, and the row says so: nothing in a pattern file records what pinned the 2θ
scale, and no esd can tell you it is a precision on the shape rather than an
accuracy on the absolute.

## Microstructure: what a domain size is, and what it is not

`result.microstructure` reads each of a phase's four sample-broadening
coefficients as the quantity behind it (a **coherent domain size** in Å from the two 1/cosθ terms, a dimensionless Δd/d from the two tanθ terms), with an esd, or a named reason there is none (`MicrostructureTerm.unavailable`:
`at_zero`, `no_wavelength`, `not_measured`).

**A domain size is not a particle size.** `Phase.particle_radius_um` is a
different quantity for a different correction, the absorption path through a
grain; profile broadening measures the coherent domain inside it, which is
smaller and unrelated. Reporting one as the other is the commonest way to
misread this block.

**It is not a two-figure number either.** The Scherrer constant moves 10-20 %
with crystallite shape, and the codes disagree about which constant and which
measure of breadth: rietx reads the FWHM with K = 0.9, GSAS-II the FWHM with
K = 1, FullProf the integral breadth — which for a pure Lorentzian is 1.571×
rietx's answer. Quote the size as an order of magnitude with the `scherrer_k`
the block carries, and quote a Δd/d with its convention (rietx's is the FWHM of
the d-spacing distribution; GSAS-II's `mustrain` is twice it, FullProf's
apparent strain half of it before the breadth factor).

**Read `separable` before either number.** Over a short 2θ range 1/cosθ and
tanθ are one curve, so the fit trades a size against a strain at no cost in
Rwp. `PhaseMicrostructure.separable` is the width trend's own verdict and
`size_strain_collinearity` the correlation it was decided on. `False` means collect a wider range. Refining one of the
pair and holding the other is not a workaround: the answer then depends on
which was held.

**Then read `size_agreement`.** rietx registers the Gaussian and Lorentzian
halves of each mechanism as independent columns, where GSAS-II refines one
magnitude and a mixing coefficient. Nothing makes them agree, so the ratio is a
measurement: far from 1 means the two describe different specimens and neither
is quotable alone.

**In a joint fit, read the size and never the degrees.** The Lorentzian size coefficient is
proportional to λ and the Gaussian one to λ² (`SIZE_LAMBDA_POWER`), so `MultiHistogramRefinement` normalises the shared column
and reports it at histogram 0's wavelength, saying so through
`SIZE_NORMALISED_ACROSS_WAVELENGTHS`. Each histogram's own structure copy
carries the coefficient it needs; the crystallite behind them is one number.

**`SIZE_UNUSUALLY_SMALL` and `STRAIN_UNUSUALLY_LARGE` flag a coefficient
outside its usual range, and `BOUND_HIT` or `FLOOR_HIT` on the same path says why it stopped
there:** a width term pinned to a bound is a held value, not a measurement,
and reads no differently in the table until you check for it.

## §4b — Structure: why the intensity-model rows are not optional

Structure determination needs everything Phase ID, QPA, Trajectory and
Microstructure check, plus the rows that speak to the intensity model
directly: per-region intensity coefficients and their angular trends,
`report.texture` and `report.strain` with their caveats, restraint tension,
ADP positive-definiteness, and `report.identifiability.exchanges` with
`.soft_modes` (step 14, above). Here a Le Bail gap over `LEBAIL_GAP_NOTABLE` is a **blocker**: the intensity model *is* the structural claim, and the gap says that model does not carry the pattern,
whatever the profile-only fit's Rwp says.
