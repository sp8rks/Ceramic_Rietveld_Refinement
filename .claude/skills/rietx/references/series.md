# 9b. Series: refine a ramp as a chain, and check it both ways

Load it for an in-situ ramp, a parametric sweep or a tray of related specimens.

*A reference file of the `rietx` skill. The body it belongs to is [`SKILL.md`](../SKILL.md); section numbers are the ones the body cites.*

An in-situ ramp, a parametric sweep or a tray of related specimens is
`rx.SequentialRefinement` / `rx.refine_sequential`: N separate refinements,
each warm-started from its predecessor.  (One *joint* residual is
`rx.refine_multi`, below.)
What comes back is a `SeriesResult` — per-pattern summaries plus
`trajectory(path)`, `qpa_trajectory(phase)`, `to_table()`, `write_csv()`.

```python
series = rx.refine_sequential(patterns, structure, instrument,
                              x=temperatures, x_label="T (K)",
                              plan="lab_sample_refine")
a_of_T = series.trajectory("phases.0.cell.a")     # x, value, stderr
```

`to_table`/`write_csv` take the **derived** paths too, resolved the same way
the plots are: `paths=["qpa.Rutile"]` exports the weight-fraction curve and
`r_bragg.<phase>`/`r_f.<phase>` the agreement indices, beside any ordinary
dot-path. Two things to expect. A path **no pattern carries raises**, naming
it and listing what does exist: the phases carrying that kind of curve for a
derived path, the series' own parameter paths for an ordinary one. And an
agreement index gets **no `_esd` column at all**, because it is a residual and
has no esd in any series — where a column *is* present and a cell is empty,
that pattern did not estimate one, which is a different fact. (Measured:
WP-1310.)

`x` is the series coordinate, and where it comes from is the file: a reader
puts a scan's own temperature in `data.metadata["temperature_k"]`, and
`rx.io.readers.list_scans(path)` reports the same number per scan before any of
them is read.  Today only the Bruker `.raw` v3 range header has such a field,
and none is guessed from an axis named for something else.  A missing key is a
file that recorded nothing — **refuse rather than substitute an ambient value**, because
an invented coordinate makes the trajectory a fiction while every fit in it
stays perfectly good.

What an operator must know, all measured:

- **Chaining is worth ~3x in iterations, not in accuracy.**  On the eight
  round-robin sample-1 mixtures: 1826 iterations unchained, 627 chained,
  weight fractions within 0.15 wt %.  Use it to make a long series
  affordable, never to make an individual fit better.
- **What licenses a chain is physical continuity, and a *tray* has none** — so
  of the three cases above, the tray is the one to think twice about.  Chaining
  eight ex-situ YBaCo₄O₇ specimens that shared only a method *created* the
  disagreement it was then used to measure: refitting them as independent cold
  points shrank the referenced pattern's Rwp gap by **13×** and its cell-*a* gap
  by **12×**, and what had been recorded as
  that campaign's largest cell-*a* disagreement with TOPAS was the chain's own
  artefact.  Warm chaining is ~10x cheaper per pattern (**0.16 s against
  1.82 s** measured on one series), and on specimens with no physical ordering
  that is the wrong saving.  Inside a *genuine* ramp the same test is worth
  running step by step rather than once: on that series a different, larger
  jump survived having no chain, so that one was real — chaining artefacts are
  established or refuted transition by transition.
- **A law across the patterns (a(T) linear, a cell across a library) is a
  joint fit, not a line through a chain**:
  `rx.refine_multi(..., coordinates=, parametric=[rx.ParametricTie(...)])`,
  read on `result.parametric`, never the scaled `vars.` rows.  It pays only where a
  pattern cannot see the parameter alone (slope scatter 0.72× the line's for a
  minor phase the hold dropped); elsewhere it equals the line, and sharing the
  instrument cut the esd 2.6× (only while the mount stays put).  Its esd
  assumes the form (2-esd coverage 3 % under a curved truth): draw the curve
  over the trajectory first.  *(Measured: WP-1325, synthetic ramps.)*
- **The default `refit="single"` collapses the plan into one stage** for every
  pattern after the first.  The staged turn-on order exists to keep early
  stages conditioned from a *poor* starting model; a converged neighbour is not
  one.  A pattern whose Rwp jumps past the median trips the reseed fence,
  which **escalates one rung at a time** — the full staged plan from the
  warm state, then the full staged plan cold — and keeps the best attempt.
  `entry.rung` says which one produced the values and `entry.rungs_tried` says
  what else was tried; `entry.reseeded` still means only the cold rung won, so
  a `"warm_staged"` point is one whose chain is unbroken.  **A collapse every
  pattern shares is not caught**: the median rises with it.  With a plan that
  frees U, V and W (`lab_bragg_brentano`), `"single"` settled 1.04-1.29× above
  `"stages"` in Rwp on every round-robin mixture after the first with no
  reseed, from both a direct and a Le Bail first fit; what named it was
  `SEQUENTIAL_PERSISTENT_FINDING` on `RESOLUTION_UNCONSTRAINED` for U, V and W
  (6-7 of 8, none under `"stages"`), while the U/V correlation row appeared
  from one start only (Measured: WP-1469, issue #475).  Read that code, and
  refit two or three patterns cold; with a width-freeing plan `"stages"` cost
  1.2-1.6× the collapsed chain's wall clock.
- **A pattern that no rung recovers is quarantined, not merely flagged**
  (`SEQUENTIAL_UNRECOVERED`): it seeds no successor and its Rwp is left out of
  the median that decides every later trigger.  So a single failure cannot
  propagate down the chain or quietly raise the bar for the patterns after it —
  but it is still *reported*, and reading its parameters is on you.
- **A tie or a named variable reaches a chain only through `constrain=`.**  The
  chain builds its own `Refinement` per pattern, so a constraint you declare on
  one you built yourself fits one pattern and nothing after it — there is no
  `carry` glob for it either, since a tie lives in no model.  Pass
  `constrain=lambda index, ref: ...` to `fit`/`refine_sequential` and call
  `ref.add_variable(...)` / `ref.tie_equal(...)` inside it, against that
  pattern's own table.  It fires once per **fit** and not once per pattern —
  every escalation rung and the `verify_discontinuities` refit get it — so a
  hook that counts its own calls counts fits.  The variable's *value* then
  rides the `carry` globs like any other path (`vars.<name>`) and warm-starts
  from the last **accepted** pattern, a quarantined one seeding no successor
  here either.  *(Measured: WP-1441, issue #376 — before it, the tie holding
  pattern 1 together left `ref._ties` empty on pattern 2.)*
- **Chart a chained coordinate by its `x`/`y`/`z` rows, never by its `dof`.**
  `carry` moves a refined coordinate into the next pattern a whole site at a
  time, but the `phases.*.atoms.*.dof.*` value a fit reports is measured from
  where *that fit* began, which in a chain is the previous pattern's answer: its
  trajectory is a step per pattern, not a position.  The coordinate rows carry
  the same esd and are what the discontinuity and path-dependence checks judge.
  A DOF your `constrain` hook ties to a variable follows the variable, so
  leaving `vars.*` out of `carry` restarts the coordinate too.  *(Measured:
  WP-1333 — before it the chain restarted a synthetic LaB6 ramp's boron `x` at
  0.19 on every pattern, and once it carried, the DOF's steps fired both
  checks on a clean both-way run until they skipped it.)*
- **A Le Bail or Pawley chain carries its per-hkl intensities too, and
  `carry_hkl_intensities=False` turns that off.**  They live outside θ, so no
  `carry` glob reaches them; the constructor switch does, and `False` starts
  every pattern's extraction afresh, as the first pattern's is. Keep the
  default for Pawley: on a synthetic 10-pattern fluorapatite ramp the two
  chains agree to five digits of Rwp on every pattern. For Le Bail, carrying
  is the better start (Rwp 3.95 % against 4.29 % on the last pattern of the
  same ramp). A Pawley reflection centred past the end of the data is ridged
  toward zero. Where only its tail reaches the data it comes back near zero,
  with an esd of the order of the strongest reflection (2e-4 ± 3.9e3 against
  a strongest of 2.6e3). Read that as "not measured", never as an intensity.
  *(Measured: WP-1459, issue #440. Before the ridge that one reflection grew to 1.1e12 along the
  carried chain, and warm refits stopped on `xtol`, still `converged`, at up
  to 769× the re-seeded chain's Rwp.)*
- **A sequential trajectory is path-dependent by construction**, so a smooth
  curve is exactly what a poisoned chain produces.  `direction="both"` runs the
  series each way and reports `SEQUENTIAL_PATH_DEPENDENT` per parameter.  For
  any trajectory you intend to publish, run it — it is the only check that
  separates a measurement from an ordering artefact.
- **But forward/backward *agreement* is not evidence of correctness**, and the
  two failures it cannot see were both measured.  A flat degenerate band
  reproduces the same wrong answer in both directions — **|Δweight| median
  0.000, max 0.030, 0 of 35 patterns disagreeing by more than 5 pp** on a
  construction that was physically wrong — because the check compares two
  paths, not two basins.  And where findings *are* present the set is not the
  signal: `SEQUENTIAL_PATH_DEPENDENT` was non-empty on all four series of one
  tranche, and the single chain actually sitting in a wrong basin was localised
  by **σ magnitude** (98.9σ and 84.4σ on the scales the QPA is built from,
  against ≤8.8σ everywhere else).  Read what was flagged before reading physics
  into it: two of the largest flags measured anywhere — **81.5σ** for *a* and
  *b* exchanging in `Fddd` and **15.8σ** for *a* and *c* in `Pnma` — are
  degenerate axis relabellings, and the largest on
  another run (16.6σ) was a *held* cell reaching the pattern with two different
  held histories, which is bookkeeping rather than two measurements.
- **`SEQUENTIAL_RESEED` is not the net for a wrong basin.**  Its trigger is
  Rwp > `reseed_factor` × the running median of accepted patterns (default
  1.25), so it needs roughly a **25 % relative Rwp jump** — and a polymorph
  swap does not cost that.  Tested directly on 20 such patterns it fired **0
  times**; where it *can* fire it works, 6 firings elsewhere in the same run
  all keeping the chain out of the disagreement set.  A wrong basin at
  negligible Rwp cost is the case for `direction="both"` and for cold refits,
  not for the reseed ladder.
- **The `SEQUENTIAL_*` codes live on `SeriesResult.diagnostics`, one level up
  from the entries.**  Reading `entry.diagnostics` for them returns zero on
  every series, which presents as a clean run rather than as a lookup in the
  wrong place — it cost one operator a full re-run of the chain stage for nine
  series, caught only by distrusting a suspiciously flat all-zero result.
  Per-entry diagnostics are real and carry every per-pattern occurrence; the
  rollups are not among them.
- **Zero `SEQUENTIAL_PATH_DEPENDENT` is a clean bill only with no
  `SEQUENTIAL_PATH_CHECK_INCOMPLETE` beside it.**  A series whose forward pass
  completed all 125 patterns and whose **backward pass crashed** reported zero
  findings, byte-for-byte what a clean series reports; the comparison now says
  when it did not run (`warning`, naming the chain and the pattern it stopped
  on) and when it ran on less than the series (`info`: patterns one chain has
  no entry for, or paths no pattern could judge).  Report the empty set as a
  measured result only in the first case's absence, and name what an `info`
  one lists.  *(Measured: issue #224's series C before WP-1333; the codes are
  WP-1333's.)*  Both safety checks are also worth pricing up front: on one
  series the backward pass was **43.9 %** of wall clock and the
  `verify_discontinuities` refits **15.1 %**, so **59 % of the run bought
  assurance rather than answers** — the right trade for a trajectory you will
  publish, the wrong one for a screen.
- **One pattern that cannot be fitted costs that pattern, not the chain.**  A
  rung whose fit raises escalates like a diverged one, so a neighbour that
  converged into a runaway cell (every warm rung inherits it and the
  enumerator refuses it) is rescued by the cold rung and comes back
  `reseeded` with `rungs_raised` saying what the warm rungs hit.  Only a
  pattern on which every rung raised is a `SeriesFailure` — absent from
  `entries`, named by `SERIES_PATTERN_FAILED` — and the default
  `on_error="carry"` continues from the last accepted pattern.  Read a
  failed pattern as a gap, never as a datum, and check `result.n_failed`
  before quoting a trajectory as complete.  What a *restarted* chain is not:
  a new `fit` over the remaining patterns warm-starts from the **initial**
  models, since a `RefinementResult` does not carry the warm state, so a
  resumed chain has a cold seam an uninterrupted one does not.  *(Measured:
  issue #224, 20 of 24 patterns lost to one raise before WP-1333; the ladder
  rescue is WP-1333's fixture test, not a re-run of that series.)*
- **A flagged step can check itself.**  `verify_discontinuities=True` refits
  each `SEQUENTIAL_DISCONTINUITY`'s two patterns **cold and independently** and
  writes the cold step over the chain's step to the diagnostic's `value`, signed:
  near 1.0 the step is in the data, near 0 the chain made it, negative a cold
  pair that moved the other way.  Off by default because
  a cold fit is the full staged plan from the initial models; measured on a
  68-pattern ramp flagging four steps over four patterns it costs 5 % of the
  chain, and the cost scales with the patterns flagged rather than with the
  series length.  Nothing else moves: the refits are separate `Refinement` runs
  writing to their own `<label>.verify` histories.  **An abstaining
  verification is a finding, not a pass:** on a polymorph-swap exhibit the refit
  fired and then reported *"an independent cold refit of both patterns does not
  determine this parameter, so the step could not be re-measured"* — the check
  needs the parameter determined and the pathology is that it is not.  Read that
  message as `PHASE_UNCONSTRAINED` about the step, and go to a cold refit sample
  rather than concluding the step was real.

- **The check that covers both blind spots is a cold-refit sample, and it is
  affordable.**  Neither `SEQUENTIAL_RESEED` (needs a ~25 % Rwp jump) nor
  `direction="both"` (agrees in a degenerate band) sees a wrong basin at
  negligible Rwp cost, and the audited job that did see it refitted **380
  patterns cold against the chain and found 316 material disagreements, 29 of
  them at |ΔRwp| ≤ 0.5 pp** — invisible to both.  Whole job, warm chain plus 380
  cold refits plus 244 minority-geometry fits plus 2 reference fits, **57 minutes
  single-threaded**.  Sample the chain cold; it is the only check here that
  catches a cheap wrong basin.
- **Pass `events=EventStream(path)` when you need a run record**: one log for
  the chain, its `stage_end` events carrying Rwp and `termination`.
  `rietx events <path>` reads it per run, re-runs into one path included
  ([`references/batch-operating.md`](batch-operating.md) § 9c.13).
  A phase switching fully in and out along the ramp is this file's *Is the
  transition first order?* section, not a batch row.
- **A trajectory of phase fractions is a QPA question at every point of it, and
  the background is what decides it.**  Fractions ride on scales, and an
  over-flexible background biases scales silently while *improving* every
  agreement index — which is why §4b's QPA row reads
  `report.background.worst_absorption` before any statistic beside it.  Nothing
  in `SeriesResult` repeats that check for you, and no `SEQUENTIAL_*` code can:
  they compare each pattern against its neighbours, and a background too
  flexible for the *specimen* is wrong in the same direction at every point, so
  the trajectory it produces is smooth, self-consistent and false.  Measured on
  a real 68-pattern reel: a 12-term cold fit put LT-ZrMo₂O₈ at **77.9 wt %**
  when that phase is not present at all, Rwp 0.0821 against 0.0822 for the
  correct answer, with a difference curve that looks fine; over the round the
  absent phase took **40-96 wt %** at an Rwp within 0.01 of the right one.
  Neither Rwp nor the plot separates them.  So read
  `background.worst_absorption` per pattern — at least on the first, the last
  and every flagged step — before quoting a fraction trajectory at all.  The
  route is not `SeriesResult`, which carries summaries only, and not
  `rx.refine_sequential`, which discards the per-pattern results: use the class
  form, whose `results_` holds them.  `sr = rx.SequentialRefinement(structure,
  instrument)`, `series = sr.fit(patterns, ...)`, then
  `rx.build_report(sr.results_[i]).background.worst_absorption`.

Driving one: **`fit()` is all-or-nothing, so wire `on_result=` before starting
anything long.**  The per-pattern loop catches `RefinementCancelled` and nothing
else and returns its `SeriesResult` only at the very end, so one exception
discards every pattern already fitted — measured as a `LinAlgError: SVD did not
converge` at pattern 217 of 531 taking all 216 with it, and a deterministic
`LinAlgError: Eigenvalues did not converge` at index 78 destroying **103
already-fitted patterns whose values were fine, because the fit had converged
and only the error bars failed**.  Cell lengths carry no physical upper bound,
so a pattern reaching `a = −347.644 Å` raises out of the reflection enumerator
and takes the chain with it (**3 of 9 chains** on one tranche, one losing 20 of
24 patterns).  The failure mode is reassuringly narrow — across **1846
`fit_start`/`fit_end` pairs the only exceptions raised anywhere were those
reflection-enumeration guards**, no hangs, no NaNs, no silent wrong-shape
results — so a driver only has to survive that one.  `on_result=(index,
result)` fires as each pattern lands; persisting there is what saved the 103
above, and it is the single highest-value line in a series driver.

**`on_result` fires on the forward pass only, and so does `results_`.**  With
`direction="both"` the backward chain is passed `None` for the callback, so
backward-pass patterns have event-log timings and **no `RefinementResult`** — 53
of them on one run.  The backward `SeriesResult` is on `.backward_` and on
`series.backward`; any per-pattern instrumentation you plan is half-populated by
design, which matters most for exactly the check above, since
`background.worst_absorption` is unreachable for the backward pass.

**Turn history on explicitly — the two defaults disagree.**  `Refinement`'s
`history` defaults to `True` and `SequentialRefinement`'s to **`False`**, and
one harness silently lost the restorable per-pattern tree for **550 fits** by
never passing it.  Here the path becomes a *directory* of one JSONL per pattern
holding **more files than patterns**, because reseed retries write their own
(291 files for 275 patterns) — so file count is not a completion check.

When the deliverable *is* the trajectory, print its deciding rows:
`series.summary(deliverable="series")` — §4b's fourth row, and the two
statements no diagnostic can make for you.

```python
print(series.summary(deliverable="series"))
```

`carry` (dot-path globs) restricts what crosses a pattern boundary.  Reach for
it when a parameter must provably not be chained; do **not** reach for it
because a parameter jumps.  That hypothesis was tested on a series whose
composition swings 1 → 94 wt % and it is false: carrying everything is cheaper
there than excluding the scales.

`prepare=(index, data, structure, instrument)` is the other half of that, and
the case above is what forces it: excluding a parameter from `carry` only falls
back to the **first** pattern's guess, which is not the same as re-estimating
it.  `prepare` runs on the *warmed* models just before each fit, so a scale
that must be estimated from *this* pattern rather than carried or left at an
initial value has somewhere to be set.  Two smaller hooks worth passing on any
long run: `progress=` (a stream or path) emits one line per stage boundary per
pattern and is the cheap way to know a run is alive, and `labels=` names the
entries — without it every downstream table is keyed by integer. One letter
away, `label=` names the whole chain in `rietx watch`'s list, and a sequence
passed to it raises `TypeError` rather than being recorded.  A cancelled
series **returns** what completed, with `SEQUENTIAL_CANCELLED`.  Note that
`stage_reports=True` does *not* exist here; it is a `Refinement.fit()` argument
and raises `TypeError`, and per-stage Rwp lives on the `stage_end` events of the
shared `EventStream` instead (present on **637 of 637** payloads in one run,
where `StageResult` carries no `rwp` field at all).

Where `stage_reports=True` *does* apply — the single `Refinement.fit()` calls of a batch — it
is expensive.  On the bundled NAC fixture it cost **6.5×**: 1.923 s against 0.296 s, median of
three, with Rwp identical to six decimal places.  `cProfile` puts 75 % of the fit inside
`_stage_report`, whose March-Dollase texture and Stephens strain analyses re-run at *every*
stage and each cost more than the optimiser step they describe; the solve itself is 23 %.
Sample it — the first fit, the last, anything you will plot — rather than setting it on every
fit of a long run.

That cost sits **outside** the stage brackets: Σ(`stage_start`→`stage_end`) was 11 % of wall
clock with stage reports on and 50 % off, unchanged at 0.225 s against 0.223 s (the solve
alone), while `fit_start`→`fit_end` covers ~100 % either way, so take a fit's cost from that
span (§ 9c.11).

## Microstrain evolves along a chain — leave it free, or it lands in the fractions

Hold the **instrument** profile after calibrating it once, and let the **per-phase** width
terms refine per pattern.  That is not a stylistic preference: in an in-situ reaction, an
electrochemical cycle or a temperature ramp, microstrain and domain size genuinely change
along the series, and a chain that holds sample broadening fixed has nowhere to put that
change.  It goes into whatever *is* free — usually the scales, and therefore the weight
fractions, which is the one number such a run is normally for.  Measured on an 11-BM
cryostat ramp, a phase's `lor_strain` rose 0.019° → ~0.11° toward low temperature,
reproducibly and in both directions; a chain with that term pinned would have had to absorb
the same intensity redistribution somewhere else.  What separates that from a width standing
in for something missing is whether the fit keeps up: a width that grows while GoF rises with
it is `SEQUENTIAL_WIDTH_GROWTH` (the codes table below), and one that grows at a flat GoF is
this rule and fires nothing.

The mirror-image mistake is a **numeric floor carried across instruments**.  A microstrain or
size floor is a hedge against the term collapsing to zero and capturing no broadening at all,
and it has to be re-derived from the peak widths of the data in front of you.  A 0.02° floor
that behaved well on lab Cu Kα data was reused on 11-BM, where the instrumental width is one
to two orders of magnitude smaller; it pinned `lor_size` **and** `lor_strain` to the bound on
every pattern of a series and inflated Rwp 3–4× (0.546 with the floor, 0.148 without, same
pattern and seed), while `BOUND_HIT` fired on the width paths on essentially every fit.  The
package's own suggested remedy for the resulting misfit — free `instrument.profile.u` — did
not help (0.546 → 0.544).  So: measure the FWHM of two or three strong isolated peaks off the
**observed** data, keep any floor well below the narrowest of them, and say which number you
used and why.  A floor at or above the instrumental width is not a floor, it is the profile.

## A symmetry test that has not been run against a null is not yet a test

A trajectory that ends in "the symmetry changes at T\*" needs the claim checked against a
compound, or a sub-series, where the symmetry is reported **not** to change — and the check
has to be able to fail.  The reason is specific and it defeated two candidate methods on one
tranche: a lower-symmetry model carries freedom that a naive parameter count does not see —
more resolved reflections, and more atoms once sites split — so a bare ΔBIC comparison tilts
toward the lower symmetry regardless of the physics.  Applied to a cubic control it "found" a
distortion below 235 K in a compound reported cubic throughout.

What survived that control was a two-part criterion: a jump in Rwp(T) against its own
baseline scatter, **confirmed by the shape of the ΔBIC curve** — a step followed by a new
plateau, rather than a smooth decay.  Write the threshold down before running it, report the
null arm's result next to the positive one, and if the null fires too, say that the detector
measured flexibility rather than physics.  A shuffled-coordinate run on the same patterns is
the cheapest null available when no second compound is to hand: on one series it gave ~12×
the β scatter and ~3× the Rwp scatter of the true ordering.

## Is the transition first order? The order decides whether a phase fraction is an observable at all

**Establish the order before reading any phase fraction across the transition.** A first-order transition genuinely coexists, so a
parent-plus-distorted two-phase model is correct and its fraction *is* the
measurement: ZnCr₂O₄ and MgCr₂O₄ hold *both* low-temperature phases in
near-equal amounts down to base temperature, and Mn₃O₄ does the same below its
T_N — all explicit in the papers cited below, whose figures are the ones to
quote. A continuous transition never coexists, and a parent whose distortion
is undetectable never has a second phase at all — in either case the child's
metric approaches the parent's, the two become one phase, and the weight split
is unidentifiable **by construction**, which is exactly what
`HIGH_CORRELATION` on the two scales reports (ρ ≈ −0.98 on **87 of 182**
patterns, all of them above T_N). Read the symptom correctly: a candidate that
is fully in (**ΔBIC ≈ −10⁴**) at the coldest scan, out (**+9.5, weight exactly
0**) at the next, back at a third and gone at a fourth is a profile-shaping
device switched on wherever the peak shape is imperfect, so **ΔBIC across a
batch is not by itself a discriminator** even at −8 700 to −41 300 — only a
**distortion magnitude against a published value** separated them, and it
agreed with the paper to ~1 %. The observable across a continuous transition
is the order parameter, never the fraction. *(Measured: archive screening
campaign, 11-BM variable-temperature series — a compound published as showing
no detected structural transition, modelled as two phases; the first-order
coexistence figures are Kemei et al., J. Phys.: Condens. Matter 25, 326001
(2013) and Phys. Rev. B 90, 064418 (2014).)*

## A moment through an ordering transition

Each entry carries `SeriesEntry.magnetic` (`MomentEvidence` rows);
`series.magnetic_trajectory()` is |m| against the axis, **esd withheld on every
unsupported point**, onset bracketed on `MagneticOnset`.  Never build "|m| vs
T" from the raw `…moment.dof0` rows: signed, verdict-free, and smoothed through
the transition by the warm start.  A pattern with no modulus esd, or diverged,
gives no verdict (`MagneticTrajectory.measured` False), outside the bracket.

## The series codes: what each one means you must not do

These eleven arrive on a `SeriesResult` — the series' own `diagnostics`, or a
pattern's entry — and a single `fit()` never emits one, so their rows live
here rather than in §7's table, which carries what a fit is likely to say.
Branch on the code, as §7 says; the manual's *Refining many patterns* chapter explains each.
The twelfth series code, `SEQUENTIAL_PERSISTENT_FINDING`, is an abstention, so its row is in §6, [`abstention.md`](abstention.md).

| Code | What it means you must not do |
|---|---|
| `SEQUENTIAL_RESEED` | Read this point of a series as evidence that the trajectory is continuous — its starting values did not come from its neighbour. With `SEQUENTIAL_RWP_OUTLIER` on the same pattern the cold rung was only the best of the rejected rungs, not a good fit |
| `SEQUENTIAL_RWP_OUTLIER` | Read that point as a measurement before opening its fit: every rung the chain tried left it above the Rwp fence (with `reseed=False` only the first, and the message says so) (`value` = Rwp over `entry.rwp_fence`). The message quotes GoF and Rexp against the last pattern inside the fence, which says why. **GoF up** means a model the pattern outgrew (a phase it lacks, a bad frame). **GoF level, Rexp up** means fewer counts: a blank frame, fitted perfectly with its scales at their esds (#481: GoF 1.00 against 1.06, Rexp 0.159 against 0.040), or a shorter frame whose fit is sound. It is not quarantined, so a run that stops is the median catching up with a lasting change (WP-1469) |
| `SEQUENTIAL_DISCONTINUITY` | Report the jump as physics without opening that pattern's own fit; it is equally the signature of a chain failure. `fit(verify_discontinuities=True)` opens it for you — both patterns refitted cold and independently, and `value` is what that pair reproduces (1.0 in the data, 0 the chain's own); measured cost 5 % of a 68-pattern chain. The pair is `series.discontinuities` (a `SeriesStep` per flag, key `path`), not the prose. Steps into or out of an outlier or unrecovered pattern are not scanned |
| `SEQUENTIAL_PATH_DEPENDENT` | Quote that parameter's per-pattern esd as its uncertainty — the between-chain spread is larger and is the honest one |
| `SEQUENTIAL_CANCELLED` | Read the shortened `entries` list as the series — it is where the chain stopped, not where the ramp ended |
| `SEQUENTIAL_UNRECOVERED` | Read that point's values as a measurement, or its failure as evidence about its neighbours — nothing was chained through it. A pattern that *converged* above the Rwp fence on every rung is `SEQUENTIAL_RWP_OUTLIER` instead, and is chained through |
| `SEQUENTIAL_WIDTH_GROWTH` | Read that phase's width, or its scale, cell or weight fraction, as a measurement from the pattern the message names onward. At one pattern the width reached 3× the first value the series measured **and** GoF 2× its own, so the phase is standing in for something the model lacks: a second phase, a diffuse signal, background the function cannot follow. No per-pattern code says so until `STRAIN_UNUSUALLY_LARGE` at 1.5° (measured on a 0.4 %-split second phase: width 3.65×, GoF 3.1×, nothing else fired). Fit the onset pattern with the missing component. `value` is the width ratio there. A Stephens block is not screened (WP-1465) |
| `SERIES_PATTERN_FAILED` | Read a missing index in `SeriesResult.entries` as a pattern nobody asked to fit — it is one on which **every** rung of the ladder raised rather than returned (`SeriesResult.failures`/`.n_failed` name it, `SeriesFailure.exception` carries the last rung's `repr(exc)`), not a converged-but-rejected `"diverged"` entry. A rung that raises is a rung that lost and the ladder escalates past it, so the last rung tried was a cold fit unless `reseed=False` or the pattern was the first walked: what failed is the pattern, not its neighbour's state. A pattern a later rung rescued has an entry whose `rungs_raised` says what the earlier rungs raised. With `direction="both"` a failure in the backward chain says so and costs only the comparison (`SEQUENTIAL_PATH_CHECK_INCOMPLETE`); the forward entry stands. The default `on_error="carry"` warm-starts the successor from the last accepted pattern; `"skip"` starts it cold; under `"raise"` the chain ends in the exception instead — read `SequentialRefinement.results_`/`.failures_`, or the exception's own `series_results`/`series_failures` (and `series_result`, the forward `SeriesResult`, when the backward pass is what raised) for what completed. A chain that fitted **no** pattern raises under every policy, so an empty `SeriesResult` never comes back as an answer |
| `SEQUENTIAL_PATH_CHECK_INCOMPLETE` | Read zero `SEQUENTIAL_PATH_DEPENDENT` findings as a clean bill while this is present. At `warning` the forward/backward comparison **did not run** at all — the forward chain was cancelled (so the backward one never started), the backward chain was cancelled, or it raised under `on_error="raise"` — and the message names the chain and the pattern it stopped on: no trajectory on this series has been shown independent of the order it was refined in, so re-run `direction="both"` to completion before quoting any per-pattern esd as the uncertainty. At `info` it ran on less than the series, in one of two ways: `where` lists **patterns** one chain has no entry for (every rung raised there; `value` is the number compared), or **paths** some chain measured that no pattern could judge because no pattern has an esd for them in both chains (issue #269 — a path held throughout one direction). A finding that did fire still stands; silence says nothing about what these name — read `result.trajectory(path)` against `result.backward.trajectory(path)` yourself |
| `SEQUENTIAL_MOMENT_HOLD` | Read the held patterns as small moments, or plot them as zero with an error bar. A held point's `value` is its fit's modulus, judged against its *own* esd, so the trajectory withholds the esd there. The message names the successors reseeded to the floor instead of warm-started |
| `SEQUENTIAL_MOMENT_ONSET` | Quote the midpoint as a critical temperature with that ± as its uncertainty: it is a **bracket** between the last released and the first held pattern, the ± half *your pattern spacing*, and nothing fits `m ∝ (1 − T/T_N)^β`. Nor quote it when `MagneticOnset.bracket_verdicts_final` is False (the early-stopped modulus had not finished falling), nor from one pass: `direction="both"` carries both chains' brackets and says whether they overlap, and one chain's warm start can carry a moment across the transition |
