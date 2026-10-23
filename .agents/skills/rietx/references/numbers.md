# 5. Read numbers, not pixels

Load it when a fit has converged and you are about to quote, compare or believe one of its numbers.

*A reference file of the `rietx` skill. The body it belongs to is [`SKILL.md`](../SKILL.md); section numbers are the ones the body cites.*

This is the design premise of the package and the first thing that changes when
the operator is an agent.

A human judges a fit by looking at it, especially at peak-shape misfit. A
vision model cannot do that reliably: frontier VLMs fail precise value
extraction from dense plots (the CharXiv, ChartMuseum and ExChart benchmarks),
and one PNG costs ~1000–1600 tokens — about the same as 50 regions of exact
numbers. All three prior agentic Rietveld systems (AgentBuild, Rongzai,
guillemot — the repository's `docs/DESIGN.md` § "Outputs & fit assessment"
holds the survey) fed plot images to a VLM and all three report the same
failure:
*locally bad, globally fine* fits that the image hides.

So:

```python
report = ref.report(plan="mccusker_structural")  # the plan supplies the Layer-2 veto
```

- **Layer 0** — model-free, always trustworthy: regions, per-region χ² share,
  cumulative-χ² breakpoints, unmatched peaks. Use this when the fit is bad.
- **Layer 1** — gated linear attribution: per region, how much of the misfit is
  a position error, a width error, an intensity error, a mixing error, an
  asymmetry error, with esds and each term's *share* of the explained misfit.
- **Layer 2** — typed suggested actions from a closed enum, each with a
  confidence, a rationale, `alternatives`, and `vetoed_by`.

The action vocabulary is closed (`ActionKind`, versioned by
`report_thresholds_version`), and each kind is carried out one of three ways —
`how`, quoted from the package's own recipe table (`report/apply.py`) and
stamped on every emitted action as `SuggestedAction.execution` (WP-1106), so a
JSON consumer reads it beside the numbers rather than from this table alone:
**stage** (one `run_stage` over the action's globs), **index** (a search, not a
stage), or **advice** (no verb — the note is the deliverable, and
`parameter_paths` is empty *by design*, not by omission). The table is every
member; emission conditions are the measured ones as of this writing and their
moves are logged in the schema version history:

| Kind | How | Emitted when | `parameter_paths` |
|---|---|---|---|
| `refine_zero_shift` | stage | the `constant` position template is significant (any geometry) | `instrument.zero_shift` |
| `refine_sample_displacement` | stage | the `cos_theta` position template is significant — Bragg-Brentano only (a capillary has no such aberration, WP-1073) | `instrument.geometry.sample_displacement` |
| `refine_sample_transparency` | stage | the `sin_2theta` position template is significant — Bragg-Brentano only | `instrument.geometry.sample_transparency` |
| `refine_capillary_offset_along_beam` | stage | the `sin_2theta` position template is significant — Debye-Scherrer only | `instrument.geometry.capillary_offset_along_beam` |
| `refine_capillary_offset_across_beam` | stage | the `cos_2theta` position template is significant — Debye-Scherrer only | `instrument.geometry.capillary_offset_across_beam` |
| `refine_cell` | stage | the `tan_theta` position template is significant (every geometry) | `phases.*.cell.*` |
| `refine_profile_widths` | stage | a width template is significant — always as the instrument-side peer of the sample action, at half its confidence, because a width trend alone cannot separate the two sides (the instrument's Gaussian polynomial spans the same shapes; Toby 2024 §4's U/V/W example). Try the sample terms first; reach for this when they leave the trend standing (measured: the sample proxy stalls at χ²_red 4.3 on a planted Gaussian deficit, this action takes the same state to the 1.01 noise floor — WP-1106) | `instrument.profile.u`, `…v`, `…w` — the Gaussian half only: a *Lorentzian* instrument width error is column-degenerate with `phases.*.lor_size`/`…lor_strain`, so the sample actions absorb it exactly |
| `refine_sample_size_broadening` | stage | the `inv_cos_theta` width template is significant | `phases.*.lor_size` |
| `refine_sample_strain_broadening` | stage | the `tan_theta` width template is significant | `phases.*.lor_strain` |
| `refine_axial_asymmetry` | stage | a significant asymmetry coefficient in gated regions below 2θ = 40° | `instrument.geometry.axial_sl`, `…axial_hl` |
| `refine_biso` | stage | the relative intensity error trends with sin²θ/λ² — the ADP signature | `phases.*.atoms.*.biso` |
| `refine_preferred_orientation` | stage | `TextureAnalysis.detected` with a best axis (both sides of the maturity gate); capped below a coexisting impurity call (§6's caveat row) | `phases.N.preferred_orientation.r` — named even when the phase declares no such block, on purpose: the rationale says which axis to declare first, and freeing nothing rolls back |
| `refine_scale` | stage | the `constant` intensity template is significant — an angle-independent scale error | `phases.*.scale` |
| `add_impurity_phase` | advice | strong unmatched observed peaks (> 8σ) not explained by the position-error evidence; when *every* one matches that evidence it is still emitted, capped at 0.3 with `reindex_or_recheck_cell` first among alternatives (§6) | empty **by design** — no phase is named yet, so there is nothing to free; the note says what to do instead |
| `increase_background_flexibility` | advice | between-peak misfit is systematic (high off-region χ²_red at low Durbin-Watson) — the too-stiff detector; capped at 0.6 however strong the evidence (§7's code block has why) | empty by design — the edit is to the background's *shape*, not to the free set; `instrument.background.*` would read as "free the background", which every plan already does |
| `decrease_background_flexibility` | advice | the background column span reproduces a notable share of a structural parameter (`report.background.worst_absorption`) — the too-flexible detector | empty by design, same reason |
| `reindex_or_recheck_cell` | index | validity-radius failures are widespread among the misfitting regions — and it survives abstention, where it matters most (§6) | `phases.*.cell.*`, but the verb is a search over cells, not a stage over parameters |
| `collect_better_data` | advice | the abstention classifier read the fit as `resolution_limited` (§6) — the one state whose remedy is the beamline, emitted at 0.5 so the data-quality reading outranks a phantom-impurity call. Its rationale carries the fork the evidence cannot resolve: instrumental breadth means better data exists; specimen breadth (nanocrystallites) means no re-measurement helps and the remedy is fewer free parameters and restraints. A `PATTERN_UNDERSAMPLED`-conditioned emission was measured and rejected — every bundled synthetic fixture trips that diagnostic beside converged GoF ≈ 1.01 fits (WP-1106) | empty by design — no parameter can be freed when the pattern itself is the limit |

**And read it at more than one state.** A report describes the state it was
built at, and the state a staged plan finishes in is routinely the least
informative one in the run: a compensated fit arrives somewhere that looks
converged and suggests nothing, because a real error has been absorbed into
whatever parameter the plan did free. Measured on the WP-1053 fixtures — a
−0.02 mm sample displacement, which no `mccusker_default` stage frees — the
final report reads Rwp 0.0137 with an **empty** action list, while the same
plan's *first* stage names `refine_sample_displacement` at confidence 0.997.
Nothing was hidden; only the last state was ever delivered. So take the
trajectory (§9), and treat a rung's high-confidence action as evidence about
the specimen even when the final report is silent.

**And an esd is a number about one basin.** Every esd, and every Layer-1
term's, is the curvature of χ² where the fit stopped. It cannot see a second
basin at the same χ², and a trace phase's weight fraction is where one appears:
its scale trades against its width until its peaks are background. 1.41 ± 0.65
wt% was reported on a pattern that admitted 0 %, 1.5 % and 98.7 % within
0.011 pp of Rwp. Before quoting a trace fraction, run
`ref.profile_fraction(data, phase)` and read its range
(`judging.md` § "a trace phase's esd describes one basin"). It is a scan,
because nothing read at the converged point can see this.

Images are secondary evidence. `plot_for_vlm()` exists and renders what VLMs
*can* read (annotated multi-panel montage, worst regions auto-zoomed, Δ/σ panel,
high contrast, never JPEG) — use it to sanity-check a conclusion you already
reached from numbers, not to reach one. The Δ/σ panel is the literature's own
recommendation for human plots too (Toby, 2024: the weighted difference shows
the weighting, stops intense regions dominating with statistically
insignificant deviations, and sits on an absolute scale with expectation 1).

**A polar group's origin along its axis is not measured.** In P 6₃ m c, P 4 m m,
Pna2₁ and the other polar groups the whole structure can slide along the polar
axis without changing any intensity, so every z a plan frees along it is quoted
with a small esd for a number the data does not fix (`FLAT_DIRECTION`, ρ = −1).
Set `phase.floating_origin = "hold"`, or call `ref.hold_floating_origin()` for
every phase, before the fit. The parameter table then holds, per such axis,
one atom DOF a shift along it moves, and the fit reports `ORIGIN_FIXED_ON_POLAR_AXIS`
(info; `where` names the held DOF). Quote that atom's coordinate as fixed, with
no esd, and read the other atoms' z as relative to it. `unhold` on the held DOF
sets the field back to `None`. `ORIGIN_NOT_FIXED` (warning) says every DOF the
shift moves was tied or held, so the flat direction is still there. Nothing is held
unless you ask. `"centroid"` instead restrains a data-weighted centroid
(Flack & Schwarzenbach 1988): every z keeps an esd quotable alone, and the
diagnostic lists each site's weight; a joint fit refuses it. (Measured:
synthetic zincite under `mccusker_structural`, O at 0.38231(57) held, each z
±0.00039 under the centroid, against ±0.00029 on each z unheld; WP-1912.)

**A symmetry-lowering can win ΔBIC and gain nothing where it splits.** Two fits
of one pattern, a model and its lowering (cubic, tetragonal): ΔBIC says it paid
for itself, not where. `rx.report.split_localisation(higher, lower)` shares the
Δχ² among the windows of the reflections the lowering splits, the unsplit ones
and the rest; read `split_share` against `split_point_share`. (Measured:
synthetic Cu, tetragonal against cubic. A truly tetragonal specimen gave ΔBIC
+190 at N/f² and +68 % of the Δχ² on 3.2 % of the points. A cubic specimen with
a {hhh}/{h00} peak shift gave ΔBIC +25 and −30 % on 4.9 %. Issue #219 is the
laboratory case.) Both fits must share channels, intensities and σ, or it
raises.
