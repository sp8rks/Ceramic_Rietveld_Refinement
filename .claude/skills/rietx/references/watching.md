# 9d. A human is watching: run directories, and the window onto a long fit

Load it when a person may be looking over your shoulder at a fit that takes a
while, when you want to hand one a live view rather than a promise to report
back, or when you need to read a finished run off disk. §9b is a chain of fits
and §9c a batch of them; this file is about the record every single fit leaves
behind. A batch inherits one directory per fit. A series does not: one
`refine_sequential` call is one job and records one directory for the whole
chain, however many patterns it walks.

*A reference file of the `rietx` skill. The body it belongs to is
[`SKILL.md`](../SKILL.md); section numbers are the ones the body cites. Every
row carries its evidence: `(Measured: …)` names the run and its number,
`(Hypothesis: …)` names what would decide it.*

**9d.1 You did not have to arrange any of this, and you cannot forget to.**
Every `fit`, `run_stage`, `refine` and `refine_sequential` writes a run
directory to disk whether or not you passed `events=`. There is no flag to set
first and nothing to remember, so the correct action when a human asks to watch
is to point them at a command, never to restart the fit with telemetry on.

*(Measured: WP-1403's acceptance — a plain `fit()` in an empty directory leaves
one run the watcher lists, 204 kB over six files on the synthetic five-stage
LaB6 case: `snapshot.json` 171 kB, `events.jsonl` 30.8 kB over 87 events,
`summary.txt` 1425 B, `meta.json` 203 B, `status.json` 235 B, `run.lock` empty.
`[dev]` venv, macOS arm64.)*

**9d.2 Hand a human `rietx watch`, run from the directory you are working in.**
It serves a run list on `127.0.0.1:8899`, with `--port` to move it and `--open`
to open a browser. They pick a run and get the obs/calc/difference plot plus the
event console, both updating as you fit. A region they have zoomed into stays
zoomed while the stages go past, which is what makes it worth their attention
rather than a picture they have to re-find their place in after every stage.

Give them the command and the port, and say which run is yours if the directory
holds several. Name the run as you start it, with `label=` on the fit verb
(9c.32). Unnamed, its label is the working directory's name, so in a shared tree
say the run id instead. The window has a stop button in it, and
9d.9 is what that does to you.

*(Measured: WP-1402 checked the zoom in chromium — the axis range is identical
before and after a forced redraw. The watcher's own effect on your fit is
nothing: it reads, and it constructs no project and no refinement.)*

**9d.3 What the run holds is the parameter trajectory, and it is not yours to
leak.** `events.jsonl` carries every free parameter's value at every recorded
evaluation, with the stage boundaries and their statistics. `snapshot.json`
carries the stage's curves decimated for drawing. No pattern bytes are ever
copied into a run.

On a shared filesystem that trajectory is a disclosure nobody opted into. If the
work is confidential, set `RIETX_TELEMETRY=0` before the first fit rather than
deleting directories afterwards.

*(Measured: WP-1406, `[dev]` venv, macOS arm64 — an `eval` event carries
`stage`, `n_eval`, `cost`, `accepted` and `values`, the last being the free
vector itself; a `stage_end` carries `rwp`, `status`, `termination`,
`n_iterations`, `held` and `released`. The snapshot's decimation budget is 4000
points, so a 4200-point pattern kept 4143 and a 22 003-point one is a picture of
itself.)*

**9d.4 Read a finished run back with the reader, and never by opening the
project.** `runs.discover(root)` lists what is under a directory,
`runs.read_run(path)` reads one, `runs.tail_events(path / "events.jsonl",
offset)` returns events from a byte offset with the next offset, and
`runs.liveness_of(run)` says whether it is still being written. `summary.txt`
in the run is the termination view as `print(result)` gives it, which is the
cheapest way to see how a fit ended without recomputing anything.

The reader constructs nothing on purpose. `Project.open` appends an annotation
to a project's history before you have done anything, so opening a project to
look at a run would change the thing you came to look at.

*(Measured: WP-1406, against rietx 1.4.0 — `discover` returned the
run, `read_run` its id, `tail_events` 87 events at offset 30782 with 0 bad
lines, `liveness_of` `done` with the evidence "the run recorded itself done".)*

**9d.5 `abandoned` is a real answer and the one you act on.** A run's liveness
is `running` when a process holds its lock, `done` / `failed` / `cancelled` when
the writer recorded its own last word, `abandoned` when the status still says
running and the lock is free, and `unknown` when the question cannot be answered
here. `abandoned` is what a killed process leaves behind. Read it as "that fit
is over and nobody wrote an ending", and do not wait for it to finish.

`unknown` is not evidence that nothing is happening. It covers a run written on
another host, a run with no state recorded, and every run written before the
recorder existed.

*(Measured: WP-1401 built the ladder and `tests/test_runs.py` drives every rung
of it — a released lock under a `running` status reads `abandoned`, a foreign
host reads `unknown`, a status with no state reads `unknown` rather than
`running`, and a legacy run reads `unknown` and says so.)*

**9d.6 Switching recording off is one line, and the environment outranks you.**
`RIETX_TELEMETRY=0` covers a process and everything it starts, `telemetry=False`
covers one call, `telemetry=<path>` moves the root, and `runs.set_enabled(False)`
switches it inside a process. No value of `telemetry=` argues back against the
environment variable, so on a machine where an operator has set it you record
nothing and should not try to.

Do not switch it off to save time. The cost is small and measured, and a run you
did not record is a run nobody can look at afterwards.

*(Measured: WP-1403 — `RIETX_TELEMETRY=0` and `telemetry=False` each left
nothing at all, asserted as an empty `rglob`. WP-1322 measured three of three
subagents switching telemetry off when it was opt-in, which is why it is on by
default now.)*

**9d.7 Recording costs a few per cent and changes no answer.** The event log
alone runs 1.01 to 1.03 times a bare fit's wall clock. Adding the per-stage
picture takes it to 1.03 to 1.23 times over three patterns of 22 003, 7251 and
4165 points. The charge is per stage and nearly constant, so a short fit pays
the largest multiple and a long one barely notices. Disk is bounded by
retention, which deletes by age and size rather than by count: nothing younger
than a week goes, and above a 1 GiB ceiling the oldest finished runs go first. A
root over the ceiling with nothing old enough warns and keeps everything, so a
long batch never eats its own early runs.

*(Measured: WP-1401, WP-1402, WP-1404 and WP-1413 on `nac` (22 003 points),
`cpd-2` (7251) and `trigger` (4165), seven interleaved repeats, `[dev]` venv,
macOS arm64. Every configuration returned a bit-identical Rwp. The retention
scan runs once per process and cost 0.2 ms at 10 runs, 2.2 ms at 100 and 27.6 ms
at 1000.)*

**9d.8 A failure to record is not a failure to fit.** If the recorder cannot
write, it stops, warns once for the process, and puts the reason in the run's
`status.json` where it can still write one. Your fit carries on and its result is
unaffected. A `RuntimeWarning` about telemetry is therefore never a reason to
re-run anything.

A callback you passed through `events=` is the opposite case. It is yours, it
runs outside the recorder's protection, and if it raises it takes the fit down.
That is deliberate: a monitoring hook that crashes the refinement is a bug you
want to see.

*(Measured: WP-1403 — a read-only directory latches the recorder off with a
warning and the fit completes; a caller's callback exception still propagates,
asserted in both directions in `tests/test_telemetry.py`.)*

**9d.9 The human watching can stop you, and it arrives as an exception.** The
window you handed them has a stop button. Pressing it raises
`RefinementCancelled` in your process at the next residual evaluation, whether
or not you passed a `cancel=` of your own. Catch it. A `RefinementCancelled` you
did not ask for is not a bug in your call. Re-running the fit is the wrong
response to one.

What survives is stated on the exception. `.completed_stages` are the stages
that finished, `.node_id` is the history node the working state stands at, and
that id is a checkout target. The stage in flight is abandoned: no node, no
committed parameters, and the structure and instrument go back to where that
stage found them. A cancelled run has no `summary.txt`, because there is no
result to write one from.

You cannot tell a human's stop from your own `token.cancel()` by looking at the
exception, and you are not meant to. The *record* can: `status.json` carries
`cancelled_by` when a request caused it, and nothing when your own code did.

In a series a stop ends the whole chain. The call returns what completed, with
`SEQUENTIAL_CANCELLED` among the diagnostics.

Report where you got to and hand back the node id. If a fit genuinely must be
uninterruptible, the honest answer is `telemetry=False`, which removes the run
directory and the window with it. `rietx watch --read-only` is a flag the human
sets on their own watcher.

*(Measured: WP-1405 — a second process writes the request and the fit exits
0.117-0.126 s later, at stage 1 of 150, with empty stderr, while the control
that is never asked runs all 150. A 4-pattern series stopped at 0 completed
entries with `SEQUENTIAL_CANCELLED`, against 4 of 4 unasked. `[dev]` venv,
macOS arm64.)*

**9d.10 A joint fit is one run, with no picture and a row per histogram.**
`MultiHistogramRefinement.fit` and `refine_multi` take `events=`, `cancel=`,
`telemetry=`, `label=` and `progress=` as `fit` does, and record one directory
for the whole job. `rietx watch` lists it and follows its status, but draws no
curves, because the live view draws one pattern. Read a histogram off the
events instead: `stage_end` carries a `histograms` list, one row per
histogram with its `histogram_index` and its Rwp. A cancel raises as in 9d.9,
with `node_id` `None`, since a joint fit keeps no history.

*(Measured: WP-1341, `[dev]` venv, macOS arm64. The two-wavelength LaB6 pair
logged one `fit_start`, five `stage_start` and `stage_end`, 38 `eval` and one
`fit_end`, and the last `stage_end` rows equal each histogram's Rwp in the
result, 0.0411 and 0.0613.)*
