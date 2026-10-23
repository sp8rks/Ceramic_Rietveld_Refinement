# 9. The trajectory, and the history DAG as a search structure

Load it when one fit is not the answer: reading the trajectory rather than the last state, and using the history DAG as a search structure.

*A reference file of the `rietx` skill. The body it belongs to is [`SKILL.md`](../SKILL.md); section numbers are the ones the body cites.*

## Read the run, not just its last state

**The first thing to do with a fit is read the report at every stage it passed
through, and that costs you one flag.** `fit(stage_reports=True)` fills
`ref.stage_reports_`. It is off by default, because WP-1064 measured that rungs
handed over unasked bought no better decisions at more calls:

```python
ref.fit(data, plan="mccusker_default", stage_reports=True)
for rung in ref.stage_reports_:
    print(rung.stage, rung.rwp, [(a.kind, a.confidence) for a in rung.actions])
```

Each rung is the same three-layer report, projected (`FitReport.for_stage`) to
the numbers §4 judges a fit on, the summary sentence, and the **active**
suggestions — those the plan you ran will *not* fix, since the strategy veto is
applied against the whole plan. Two properties make it safe to rely on:

- **It changes no number.** The rungs are read off states the plan already
  passes through; a fit run with the trajectory lands bit-for-bit where the
  same fit runs without it (measured: identical Rwp to full float precision on
  the synthetic fixtures, 0.140249 on 11-BM NAC). Nothing is refined to
  produce a rung.
- **It costs ≈2.5–2.8× the fit's wall clock** (1.06 s → 2.70 s on 59.5k
  channels of real 11-BM data; 0.30 s → 0.82 s on the 4200-channel synthetic
  LaB₆ fixture, re-measured 2026-08-19) and single-digit kB of payload: on
  that LaB₆ fixture, 0.6–0.8 kB a rung, 3.5 kB for the whole five-rung
  trajectory, ~3 % of the 111 kB report it ships beside. Quote that share
  with its fixture — the report's size is dominated by its geometry table
  (89 kB of the 111), which no rung carries, so beside a geometry-light
  report the same trajectory reads as ~26 % (the `StageReport` docstring's
  WP-1058-era episode-fixture measurement). The cost is flat *per stage*, not
  per iteration, so on a hard or diverging fit it disappears into the noise.
  Turn it off for a fit you are not going to read.

What to look for, in order:

1. **A rung that names a cause the final report does not.** That is the
   compensation signature of §5: the plan absorbed a real error. The named
   parameter is the hypothesis; `predict_then_verify` below is how you test
   it rather than believing it.
2. **A confidence that climbs across rungs.** On real 11-BM data with an
   unmodelled CaF₂ impurity, `add_impurity_phase` reads 0.3 → 0.6 → 0.9 as the
   host phase fits: a hypothesis getting *stronger* as the model improves is
   about the specimen, not about the starting values.
3. **`abstained_kind` changing.** `immature` early is ordinary. Ending at
   `resolution_limited` is a legitimate stopping point for a phase-ID
   deliverable (§4b) — not a licence to escalate corrections.
4. **`n_actions_vetoed`.** These are the suggestions your own plan already
   answers; a rung whose actions are *all* vetoed is telling you the plan is
   already the right one.

The rungs deliberately carry no regions, curves or per-region attribution: a
rung is a pointer to a state worth asking about, and `ref.report()` is where
you ask. There is no declared bootstrap ladder to invoke, because the states are already there —
every preset opens on a background+scale stage, which is that ladder's first
rung (WP-1058). A hand-rolled one-stage plan is the one case with nothing to
report but its end: the turn-on order is what makes a trajectory informative.

## The DAG: branch, verify, roll back

This is the part of the API that exists because the operator might be a search
process rather than a person. Every stage auto-commits an immutable, restorable
node (~10 kB — state, not curves), so branching is cheap and a rejected
experiment leaves no trace in the working state.

The canonical agent loop:

```python
ref = rx.Refinement(structure, instrument, history="session.jsonl")
ref.fit(data, plan="mccusker_default")
ref.history.tag(ref.history.head, "baseline")

# try a hypothesis on a branch — rollback is structural, not manual
rival = ref.branch("baseline")
rival.run_stage(data, rx.Stage("aniso_strain", ["phases.*.microstrain.dof.*"],
                               strain_seed=1000.0))

ref.history.compare([n.id for n in ref.history.leaves()])
ref.checkout(ref.history.best("rwp").id)
```

and the machine-checked version of "should I take this suggestion?":

```python
outcome = rx.report.predict_then_verify(ref, data, report.suggested_actions[0])
# runs the action on a branch, keeps it only if χ² actually improves by ≥1 %
print(outcome.accepted, outcome.reason, outcome.predicted_delta_chi2,
      outcome.observed_delta_chi2)
```

Note `expected_delta_chi2` on a suggested action is the *linear model's*
prediction — an optimistic upper bound, not a promise. The gap between
predicted and observed is itself information: a large predicted improvement
that does not materialise means the linearisation was invalid there, which is
usually a peak far enough off that it should have been re-detected rather than
shifted.

This loop is executable, not aspirational: `tests/test_report_loop.py` runs it
closed — report → top surviving suggestion → verify → checkout/rollback →
re-report — from eight planted-cause starts and measures planted-parameter
recovery, stopping behaviour and rollback hygiene against the
`mccusker_default` preset (WP-1052).

The same shape answers the other question the report asks and does not
settle — **which of an exchangeable pair is physical** (§4 rule 14):

```python
finding = next(e for e in report.identifiability.exchanges if e.exchangeable)
swap = rx.report.compare_rivals(ref, data, finding)   # two branch fits
for r in swap.rivals:                # [0] frees the held one, [1] the partner
    print(r.freed_path, r.chi2, r.rwp, r.freed_value, r.freed_esd, r.n_free)
print(swap.chi2_ratio)               # < 1 ⇒ the parameter the fit HELD wins
```

Three things about it, and each is deliberate. It runs each rival **alone**
with the other held at its **null** — never both together, which is the ridge
(§3), and never with the rival at its last fitted value, which is neither
rival. The free set is otherwise unchanged, so `n_free` matches across the two
and raw χ² is comparable without an information criterion. And there is **no
`decisive` field**: the package states the reading rule and never applies it,
the same fence `predict_then_verify` respects by reporting
`observed_delta_chi2` beside its own threshold. The reading rule is §4 rule
14's band, orientation-neutral because `chi2_ratio` is directional: take **the
winning rival**'s side whichever index it is — the losing χ² over the winning
χ², i.e. max(ratio, 1/ratio) — and compare that against
`RIVAL_DECISIVE_MIN_CHI2_RATIO`. At or above it, the winner's fit is the
answer, quoted without caveat (a `chi2_ratio` of 0.86 is 1/0.86 = 1.17, decisive);
below it the pair has tied and the resolution is protocol. A pair with no
null (a cell edge, a scale) is refused by name — that one is resolved by
protocol, not by measurement.

Two properties worth relying on:

- **Node metrics are as-optimised**, measured on a model frozen at the values
  each stage *started* from. `rx.replay(tree, node_id, data)` recompiles at the
  values the stage *ended* on, so the two can differ marginally. That gap is a
  staleness signal, not a bug.
- **Each node carries the API call that produced it**, so a session doubles as
  a reproducible script, and `cherry_pick` replays another node's stage *action*
  (not its values) on top of the current state.
