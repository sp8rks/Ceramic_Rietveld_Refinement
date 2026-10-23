# 9c. Many fits as one job: operating the run

Load it when a batch is running or about to run and the question is how to
run it well — budgeting a job's cost, timing stages, keeping the event log
honest, scoping the inventory, recovering from a per-unit failure. One
refinement is a unit of a larger job here: candidate models screened against
one pattern, or many patterns fitted independently rather than chained (§9b
is the chain, whose fits share an order and a path).
[`references/batch.md`](batch.md) is the companion file for reading what the
fits, once run, show — ranking, differencing, trusting an answer.

*A reference file of the `rietx` skill. The body it belongs to is
[`SKILL.md`](../SKILL.md); section numbers are the ones the body cites. Every
row carries its evidence: `(Measured: …)` names the run and its number,
`(Hypothesis: …)` names what would decide it. Where that run belongs to the
**archive screening campaign**, the tag names that corpus instead of a run a
reader can open — a screening campaign over a private diffraction archive of
laboratory, synchrotron and reactor-neutron patterns, refined against the
existing TOPAS, GSAS and XND answers for the same data wherever those survive.
The archive is unpublished and ships in no wheel, so those rows cannot be
reproduced from this repository; every number in them still comes from the log,
and no scientific magnitude of any specimen in it appears in any row.*

A batch is N separate `rx.Refinement` runs, or N branches of one history tree
([`references/history.md`](history.md)), each a whole §1-§10 job with its own
deliverable, stop rule and report. It is not `rx.refine_sequential` (§9b: each
fit is warm-started from its neighbour, so the set has an order and its
trajectory a path) and not `rx.refine_multi` (one joint residual over patterns
that share structural parameters). What the body settles for one fit is
settled here too and is not restated: the deliverable and its deciding rows
(§4b), the three stop conditions (§10), abstention (§6). This file holds only
what running a batch as a set costs and requires — budget, timing, logging,
inventory, fault tolerance; reading what the fits show once they exist is
[`references/batch.md`](batch.md).

## Writing a row

A row is a rule an operator of a batch needs and a single fit never does, with
the measurement that produced it. Ask first whether it is about running the
batch itself or about deciding what a batch's fits show — the latter belongs
in `batch.md` instead. From a run's logs the form is: the rule as
one imperative sentence in bold, numbered `9c.N`; what was measured — the
dataset or episode, N, the number that decides — in two to four sentences;
then the tag. `(Measured: …)` names the run. Where the run is in this
repository — a WP, an eval round, a dataset in `tests/data/README.md` — name
it so a reader can go and look. Where it is not, name the **corpus** the file
declares in its provenance line above, and name it the same way every time:
the package has to be tested on data it cannot ship, so a row measured on data
a reader cannot open is admitted, but it must be recognisable as one before
the reader acts on it. Two things the private case does not relax. Every
number still comes from the log, and anything the log does not decide is a
`Hypothesis` row: unverifiable is not a licence to be vaguer. And a scientific
magnitude derived from unpublished data stays out. The line is what the row is
about: what the *run* did may be quoted — counts, rates, wall clock, a ratio of
fit qualities, which is what the rows below are made of anyway — and what the
*specimen* is may not: a cell, a phase fraction, a domain size, a transition
temperature, and a ratio of two of those is still one of those. Quote the
shape, or a published figure, instead, which is where the lesson was anyway.
`(Hypothesis: …)` is for a
rule the logs suggest but do not decide, and names what would decide it. A
hypothesis row is not a weaker rule; it is an open question stated as one, and
§6 applies to it — do not act on it as if it were measured. Before adding a
row, ask whether it holds for one fit alone: if it does, it belongs in the
body or in §8, not here. All rows sit under *The rows*, one after another,
each closed by its tag; `tests/test_skill.py` refuses a row without one, and
`CONTRIBUTING.md` § The agent skill has the sync step.

## The rows

**9c.5 Budget a job from what a converged job costs on this batch, and read a
job past its budget as a diagnosis.** §8.13: a stage that takes minutes is
telling you it is degenerate. On a chain the rung budget is a factor times the
dearest *converged* first rung, never a fixed wall (WP-1127); a job several
times the median converged job is a flat direction or a degeneracy to read in
its trajectory, not a fit to wait for. *(Hypothesis: the mechanism is measured
on a chain, WP-1127, and on the ramp run's 27 %; the factor for independent
jobs is not.)*

**9c.6 Cost tracks solver iteration count and almost nothing else, so predict
a batch from iterations rather than from the model.** Stratified by pattern
size, cost against iteration count gave r = **+0.859 and +0.988** within
stratum on the two stratified batches with no sign flip, and **+0.983** pooled
on a third whose single frozen protocol needed no strata; peak broadening,
minimum phase fraction and reflection count **all flip sign** between pooled
and stratified, so each of them correlates with "which protocol is this"
rather than with work done. Stratify by (protocol × geometry) before
correlating anything against cost — pooling warm chain fits with cold ones,
and 180-point windows with 4787-point ones, manufactured a reflection-count
correlation of **+0.398 pooled (n = 976) against a stratified median of +0.052
(12 strata, n = 961)**. *(Measured: archive screening campaign R3 — three
batches, the (La,Sr)FeO₃ chemical-looping series, YBaCo₄O₇ and the six-phase
CuO/Cu₂O tranche; the pooled-vs-stratified reversal replicates, though its
magnitude does not on a batch with only two pattern sizes.)*

**9c.7 Do not carry a per-iteration cost model from one batch to another.**
The same fit machinery costs a different amount per iteration on different
data, so a regression fitted on one batch is not a package constant. One
batch's `s/iter = 4.4 µs × n_points + 2.9 ms` (r = **+0.972** there) predicted
**8.61 ms/iter** for a six-phase batch that measured **28.82 — 3.35× low** —
and sat at **0.34–0.49×** on a third. The missing term is model complexity:
six phases on the *smallest* patterns was the dearest per iteration of
anything measured, which is the opposite of what point count alone predicts.
*(Measured: archive screening campaign R3 — the regression is the (La,Sr)FeO₃
series', the 3.35× miss is the six-phase CuO/Cu₂O tranche and the 0.34–0.49×
is YBaCo₄O₇, i.e. two batches on opposite sides of the same line.)*

**9c.8 A stage that exhausts its iteration budget is not by itself waste —
pair `max_nfev` with the cost reduction it bought.** Across three batches,
`max_nfev`-terminated stages took **46.6 % / 42.9 % / 23.5 %** of stage time
at **72× / 53.6× / 18.0×** the median converging stage; the shape replicates
and weakens each time, so the multiplier is not quotable but the sink is real.
Splitting them by what they achieved is what separates the two populations: on
one batch twelve exhausted `warm_refit` stages returned a **17 % median cost
reduction** — real work needing more budget — while five exhausted `refit_all`
stages burned 30.8 s for **0.018 %**, and the pooled median of 12.7 % hides
the split entirely. Report it per stage name, and do not key a *guard* on the
stage name: three batches put the waste in three different stages
(`warm_refit`/`biso`, then `refit_all`, then `strain`), so a name-keyed guard
misses two of three. *(Measured: archive screening campaign R3 — three
batches; the waste signal is `max_nfev` **and** near-zero fractional cost
reduction.)*

**9c.9 Read terminations before blaming the iteration cap for a slow batch.**
The quieter sink is the larger one: of 63 stages exceeding 5× the median on
one batch — **9.9 % of stages and 52.5 % of stage time** — **43 terminated on
`ftol` and only 19 on `max_nfev`**. Long *converging* stages cost more in
aggregate than exhausted ones, so raising the cap addresses the smaller half
of the problem. *(Measured: archive screening campaign R3, the six-phase
CuO/Cu₂O tranche's full stage census — the run whose 40 minutes had been
attributed to the iteration cap.)*

**9c.11 Sum `fit_start`→`fit_end` for a fit's cost; never sum its stage
durations.** Inter-stage bookkeeping belongs to no stage, so stage-level
totals are **systematically** low: fit-level agreed with an independent wall
clock to **0.62 %** while stage-level undercounted by **19.9 %** on one batch
and **~27 %** on another. Anyone budgeting a batch from summed stage durations
is 20–27 % low before any other error. *(Measured: archive screening campaign
R3 — YBaCo₄O₇ at −19.9 % and the CuO/Cu₂O tranche at ~27 %, both audited
against an external clock, fit-level agreeing to 0.62 %.)*

**9c.12 Pair timing events in order; never bucket them by pattern index.** A
pattern index recurs — reseed retries, verification refits, restarted segments
— so `max(fit_end) − min(fit_start)` within a bucket spans everything that
happened in between, and nothing about the result looks wrong: one segmented
recovery chain reported **700.686 s of fit time against a 147.988 s wall
clock, 4.73×**. Ordered `fit_start`→`fit_end` pairing is the fix, but it can
also *overstate* where fits are silently re-executed with no retry marker
(2.7× on one audit), so cross-check against a per-part table before quoting.
Assert event-log-summed fit time against an independently measured wall clock
on every unit of the batch — it is the only check that caught any of this.
*(Measured: archive screening campaign R3, the (La,Sr)FeO₃ chemical-looping
series and its segmented-recovery audit.)*

**9c.13 Read a re-used event log per run: `rietx events <log>`.** `EventStream`
opens its file in **append mode**, so re-running a batch into the same path adds
a second run to the file. Since event schema 3 each opened stream writes a run
header first and `rietx events` (or `rietx.history.aggregate.summarize_events`)
reports every run apart. A log written before that has no header: it reads as
one run, and any duration derived from it mixes the runs. That once reported a
**10.276 s calibration as 458.995 s — 44.67×**. For such a log, or a reader of
your own, re-path per run, and note concurrent load on the machine as a
confound to state rather than to absorb. *(Measured: archive screening campaign
R3, the (La,Sr)FeO₃ series among two affected batches.)*

**9c.14 Pilot the model on a dozen patterns before multiplying it by N.** The
dominant failure at scale is not a bad fit but a *good* fit to a wrong model,
N times, and the errors that do it are invisible in the residual: a
space-group setting resolved from a bare Hermann-Mauguin symbol (**40 symbols
in gemmi's own table carry more than one setting**, and origin-2 coordinates
under an origin-1 setting converge at an ordinary Rwp with a whole reflection
class silently zeroed and **no diagnostic firing**), a unit conversion made
once in a shared calibration and therefore wrong in every pattern that uses
it, and a mis-parsed axis (**a GSAS FXYE with its `BANK` line commented out
returned `[50.0, 4399.6]°` instead of `[0.5, 43.996]°`** — same point count,
no exception, `provenance` `None`; the reader now reads such a file as GSAS and says so, `GSAS_BANK_COMMENTED`). Total cost is near-linear in length, so a
dozen patterns is a few per cent of a long run and tests all of it;
per-pattern cost is *sub*-linear in model size (**1.489 s → 4.170 s, 2.80× for
a 5.35× increase in reflections**), so the pilot's per-pattern time is an
upper bound — time it as well as reading it (9c.31). Pass `diagnostics=[]` to
every `read_pattern` and act on what comes back (it refuses an axis past 180° and
reports one at or below 0°), check a transcribed phase's cell mass against the source
file's own (**286.182 against 286.184, 7 ppm**, settled an ambiguous Cu₂O
setting whose origin-1 alternative was a 1:2 Cu:O compound — though mass
balance cannot catch the origin error above, so the two checks complement
rather than substitute), and validate any reference-file reader against check
values you did not derive. *(Measured: archive screening campaign — the Cu₂O
transcription against its own TOPAS `.inp`, the FXYE reader fallback on a
ZnCr₂O₄ pattern, and the CuO/Cu₂O tranche's five-to-six-phase cost scaling and
12-pattern timing pilot.)*

**9c.15 Re-derive the batch's inventory from the archive and de-duplicate by
file identity.** A batch scoped from a list someone wrote is scoped to that
list: one brief's own per-series counts summed to **638 rather than the 658 it
stated**, and of those 638 only **624 were diffraction patterns** — the other
14 gas-monitor markers with no diffraction angles and furnace temperature logs
— inside a directory set holding 1055 raw files in all; a whole-archive
manifest elsewhere carried **1372 rows but 1366 distinct members**, six
byte-identical duplicates that would have double-weighted four temperatures.
Assert the expected file count immediately after the selection glob, so a
wrong pattern set fails loudly instead of fitting. *(Measured: archive
screening campaign — the (La,Sr)FeO₃ tranche's 1055/638/624 count, and the
whole-archive 11-BM manifest whose 1372 entries were 1366 distinct scans, of
which the GeNi₂O₄ series contributed 215 fitted after the sentinel row.)*

**9c.16 Scope from one level above the data, and write the unrun remainder
down.** A batch scoped from the files it had already chosen looks complete
against itself, and the gap is invisible from inside the scope: one campaign
covered **3 of 10 series and left 771 patterns unrun** while reading as
finished. Two smaller instances from the same inventory — a series-looking
name that was **2 patterns with no temperature recorded**, and a folder whose
reference row count disagreed with its pattern count because it held two scan
geometries, to be filtered by filename rather than reconciled by arithmetic.
Where an arm is time-boxed out, record it as **undetermined rather than
passed** and name the exact excluded set, because an omitted arm in a summary
table reads as a clean one. *(Measured: archive screening campaign — the
inventory rebuilt one directory above the fitted set.)*

**9c.17 Give every per-unit iteration its own `try`, not just the innermost
loop.** A batch driver is judged by what one failure costs, and the guard
belongs at each level that can lose work independently: the same
reflection-enumeration guard that kills a fit fired inside a *calibration*
fit, and because that loop had no per-geometry `try`, **all of that series'
minority geometries were lost — 8 of 9 series produced them and that one
produced none**. Persist each unit's result as it lands rather than at the
end. *(Measured: archive screening campaign R3, the minority-geometry pass.)*

**9c.30 Expect model debugging, not the solve, to be the batch's cost.** In the
one batch where both halves were timed, "the batch is expensive" was a claim
about getting the model right: that pilot's summed solve time was **13.2 min**
(409.7 s + 382.0 s, confirmed against `results.json`) after **20–25 min of
setup before the first production fit**, while a fully audited job of **380
chained patterns plus 380 cold refits plus 244 minority-geometry cold fits plus
2 reference fits ran in 57 minutes single-threaded**. Speed was not the
constraint in either job measured, so budget the pilot and the inventory rather
than the cores — and pass an explicit long
timeout, since a production run will outlive a shell's default and being
auto-backgrounded mid-run is indistinguishable from finishing. *(Measured: archive screening campaign — the CuO/Cu₂O pilot's audited solve sums, whose
68.5 min session wall figure is itself unverifiable from the event logs and is
9c.29's own example, and R3's audited nine-series (La,Sr)FeO₃ job at 57
minutes.)*

**9c.31 Pin the compute environment for the whole batch and assert it per
unit, not once at the start.** Thread count and package version are covariates
of every timing and every regression claim you will make: a 12-pattern timing
pilot ran **5.92 s per pattern against the same tranche's 4.17 s in the
previous round**, a **42 % miss** traced to single-threaded BLAS and caught
only because the pilot was timed before a chunk size was committed to. Version
drift is worse because it is silent — one machine's three separately-frozen
baseline environments had all become the *same* release, which unreproduces
every version-difference claim measured against them without any of them
erroring. Set the `*_NUM_THREADS` variables inside the driver rather than in
the shell that launched it, and record `result.provenance` per unit so a later
reader can tell which build produced which number. *(Measured: archive
screening campaign — the CuO/Cu₂O timing pilot's BLAS miss, and the campaign's
collapsed version baselines.)*

**9c.32 Name every run with `label=`, after the thing that fit is about.**
Unnamed, a run takes the name of the working directory it ran in, so a batch
driven from one directory writes one name down every row of `rietx watch`'s
list, and the reader tells the runs apart by start time alone. `label=` is on
every verb that records a run (`fit`, `run_stage`, `refine`,
`refine_sequential`, `Project.fit`) and costs one keyword at the call. Pass the
candidate, the phase, the specimen: the fact that makes this fit the one you
will want to reopen. It is telemetry, so it changes no number the fit produces
and appears in no result. On a chain `label=` names the job while `labels=`
names the patterns, and the list shows the pattern. *(Hypothesis: the limit it
removes is measured, WP-1424 having made the rows tell apart by start second
and reported that the record still names no run after its science. No campaign
has yet run with labels on, so whether a named list is read faster than a
timestamped one is undecided. What would decide it: a batch operator asked to
reopen a named candidate from the watcher list, against the same task on a
timestamped one.)*
