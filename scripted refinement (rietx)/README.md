# Scripted and AI-assisted Rietveld refinement with rietx

A second track for the workshop. **GSAS-II stays the primary teaching tool**; this folder refines the same
data in Python with [rietx](https://rietx.org) and uses it as a cross-check on the GSAS-II refinements in
`refinement examples/`. Every notebook reads the original files in place (relative paths into
`../refinement examples/`) and changes none of them.

## Run in Google Colab (nothing to install)

| Notebook | |
|---|---|
| 01. LaB6 instrument calibration | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sp8rks/Ceramic_Rietveld_Refinement/blob/main/scripted%20refinement%20%28rietx%29/01_LaB6_instrument_calibration.ipynb) |
| 02. Al2O3/Si quantitative phase analysis | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sp8rks/Ceramic_Rietveld_Refinement/blob/main/scripted%20refinement%20%28rietx%29/02_Al2O3_Si_quantitative_phase_analysis.ipynb) |
| 03. Co3O4 temperature series | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sp8rks/Ceramic_Rietveld_Refinement/blob/main/scripted%20refinement%20%28rietx%29/03_Co3O4_temperature_series.ipynb) |

The first code cell of each notebook installs rietx and clones this repository for the data when it detects
Colab (about a minute); run the cells top to bottom. The notebooks open with their saved outputs, so you can
also just read them. Notebook 02 uses `lab_profile.json`, which is in the repository, so it runs without
notebook 01 first. The Co3O4 series (notebook 03) takes several minutes on Colab's free CPU.

## Install locally

Python 3.11 or newer.

```bash
cd "scripted refinement (rietx)"
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # rietx[viz] 1.9.0 and JupyterLab
jupyter lab
```

Run the notebooks in order: notebook 01 writes `lab_profile.json`, which notebook 02 reads. Each notebook is
saved with its outputs, so you can read them on GitHub without running anything.

## rietx or GSAS-II?

| Use GSAS-II when | Use rietx when |
|---|---|
| you are learning Rietveld refinement: seeing each parameter, clicking it on, watching the fit move | you want the whole refinement in a script you can rerun, diff and share |
| you need its breadth: single crystal, magnetic and TOF data, rigid bodies, sequential GUI tools | you are refining a series of patterns, or many specimens, the same way |
| the workshop exercises | you want a second opinion on a GSAS-II result (the notebooks here compare the two on every dataset) |
| | you want an AI assistant to drive the refinement and you want its reasoning checked |

The feature that matters most for teaching is rietx's **diagnostics**. Every fit comes back with typed
messages (`BISO_NEGATIVE`, `FLOOR_HIT`, `HIGH_CORRELATION`, `BACKGROUND_ABSORPTION`, ...) that name what is
wrong and what not to quote, plus a report that says where in the pattern the misfit lives. The notebooks
explain each diagnostic as it fires, and do not hide any.

## Using it with Claude Code

The rietx agent skill is installed in this repository, in `.agents/skills/rietx/`, with a copy for Claude Code
in `.claude/skills/rietx/` (on macOS and Linux the installer links it instead of copying). It carries rietx's
operating protocol: the order in which to free parameters, the checks to make before believing a number, and
which numbers may be quoted. Claude Code loads it automatically when a task involves a powder pattern, so a
prompt like these works from the repository root:

- *"Refine `refinement examples/LaB6/LaB6_Jan2018.raw` against its CIF with rietx and tell me what the
  diagnostics say."*
- *"Compare the GSAS-II result in `refinement examples/90Al2O3_10Si/refinement/test.lst` with a rietx
  refinement of the same scan."*

To update the skill after upgrading rietx, run `rietx skill --install` in the repository root. To read it
yourself: `rietx skill --print`.

## The notebooks

### [01. LaB6 instrument calibration](01_LaB6_instrument_calibration.ipynb)

`plan="lab_calibrate"` on the LaB6 scan with the cell held at the CIF value (the NIST lot is unknown).
A first fit gives GoF 4.6, Durbin-Watson 0.17 and negative displacement parameters, and so does GSAS-II.
Holding Biso at 0.3 Å² makes the fit worse, and rietx's region-by-region report shows why: intensities are
too strong at low angle and too weak at high angle. Testing rival causes picks **surface roughness**
(GoF 7.8 → 2.3, ΔBIC ≈ +330), not a variable slit. The axial S/L, H/L pair and the zero/displacement pair
cannot be separated on this pattern and are handled explicitly. The "unmatched peaks" turn out to be Cu Kβ
leakage, white radiation under the strongest line, and peak tails, not an impurity. The data prefer a
certificate-like cell (4.15695 Å) over the CIF value, which moves the zero shift by 0.009°. The profile is
saved to `lab_profile.json`.

### [02. Al2O3/Si quantitative phase analysis](02_Al2O3_Si_quantitative_phase_analysis.ipynb)

`plan="lab_sample_refine"` with the LaB6 profile. rietx gives **96.8 / 3.2 wt%** Al2O3/Si, GSAS-II gives
96.76 / 3.24: the two codes agree, and both disagree with the weighed 90/10. The notebook then works out why:

- the LaB6 profile comes from a different instrument (`FLOOR_HIT` on the Si widths), but the fractions do not
  depend on it, nor on the background (both within 0.05 wt%);
- both codes refine displacement parameters far too large; holding them at physical values moves Si by
  0.5 wt%;
- **amorphous content** is ruled out by the internal-standard arithmetic (it would make Si read *higher*);
- **microabsorption** is too small, because Si and corundum absorb Cu Kα about equally;
- **particle statistics** is supported: Si reflection intensities scatter 0.6 to 2.1 times calculated (Si 311,
  the worst residual near 56.1°, is twice calculated) in an unspun specimen, while a second mount does not
  show it.

The `Al2O3_Si_SiO2` scan and its GSAS-II `test_amorphous` refinement turn out to contain an unmodelled, broad,
fluorite-type phase (a = 5.096 Å, most likely zirconia contamination) rather than measurable amorphous silica.

### [03. Co3O4 temperature series](03_Co3O4_temperature_series.ipynb)

Twelve in-situ scans, 25 → 1000 → 25 °C, refined in one `rx.SequentialRefinement` run in both directions.
The scans are Co Kα (titles, GSAS-II wavelengths, and the implied spinel cell all agree). The instrument comes
from the Co `.prm` file. The "impurity" peaks excluded in the GSAS-II refinements are **Co Kβ** lines, which are
modelled here as a third emission line instead. The trajectories show CoO oxidising to Co3O4 on heating (60 →
100 %), full reduction to CoO at 1000 °C, and incomplete re-oxidation on cooling (about 94 %). They match the
older heating/cooling figure in the data folder. The series diagnostics (discontinuity checks, an Rwp outlier
at the first cooling scan, a persistent `FLOOR_HIT`) are each explained and tested. The GSAS-II 1000 °C
refinement in the folder (99 % Co3O4) is shown to be in a wrong solution. Results are written to
`co3o4_series.csv`.

## Files

| File | What it is |
|---|---|
| `01_...ipynb`, `02_...ipynb`, `03_...ipynb` | the notebooks, executed, outputs saved |
| `gsas_lst.py` | a small reader for the numbers we compare from GSAS-II `.lst` listings |
| `lab_profile.json` | the instrument profile written by notebook 01 and read by notebook 02 |
| `co3o4_series.csv` | the Co3O4 series table written by notebook 03 |
| `requirements.txt` | rietx[viz] 1.9.0 and JupyterLab |

Running the notebooks also creates `.rietx/`, rietx's per-run logs (ignored by git; safe to delete).
