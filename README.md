# Ceramic_Rietveld_Refinement

Software, data, and tools to accompany my American Ceramic Society workshop **"Tools for Visualizing and Understanding the Structure of Crystalline Ceramics."**
Learn more about the course [here](https://ceramics.org/professional-resources/career-development/short-courses/tools-for-visualizing-understanding-structure-of-crystalline-ceramics/).

## What's in this repo

- **Slides** (PDF) from the workshop
- **Example files**: powder diffraction data, CIFs, and refinement inputs (see the `examples` folder)
- **Python tools** for plotting and visualizing refinement results

## Video companion

The videos are arranged as a suggested learning path. If you are new to diffraction, start with the concepts; if you just want to run a refinement, jump to step 2 and follow along with the Co3O4 files in `examples`.

### 1. Concepts: how XRD and Rietveld work

<table>
  <tr>
    <td align="center" width="25%">
      <a href="https://youtu.be/gsalQKpI_aA"><img src="https://img.youtube.com/vi/gsalQKpI_aA/mqdefault.jpg" width="200" alt="Bragg's law explainer"></a><br>
      <b>Bragg's Law</b><br>
      Why X-rays can "see" atoms
    </td>
    <td align="center" width="25%">
      <a href="https://youtu.be/ZJVZ997b8u0"><img src="https://img.youtube.com/vi/ZJVZ997b8u0/mqdefault.jpg" width="200" alt="XRD optics explainer"></a><br>
      <b>XRD Optics</b><br>
      How the diffractometer shapes the beam and the pattern
    </td>
    <td align="center" width="25%">
      <a href="https://youtu.be/IBkl9OUuHMs"><img src="https://img.youtube.com/vi/IBkl9OUuHMs/mqdefault.jpg" width="200" alt="Peak broadening explainer"></a><br>
      <b>Peak Broadening</b><br>
      Instrument, crystallite size, and strain contributions
    </td>
    <td align="center" width="25%">
      <a href="https://youtu.be/G0eCClDcHrw"><img src="https://img.youtube.com/vi/G0eCClDcHrw/mqdefault.jpg" width="200" alt="Rietveld refinement explainer"></a><br>
      <b>Rietveld Refinement</b><br>
      What the method fits and why
    </td>
  </tr>
</table>

### 2. Hands-on: refine and visualize

<table>
  <tr>
    <td align="center" width="33%">
      <a href="https://youtu.be/E5aGgf9wHFc"><img src="https://img.youtube.com/vi/E5aGgf9wHFc/mqdefault.jpg" width="240" alt="XRD search/match tutorial"></a><br>
      <b>XRD Search/Match</b><br>
      Identify your phases first, and know when to distrust the match
    </td>
    <td align="center" width="33%">
      <a href="https://youtu.be/mcuLF0Szd4w"><img src="https://img.youtube.com/vi/mcuLF0Szd4w/mqdefault.jpg" width="240" alt="Co3O4 Rietveld tutorial"></a><br>
      <b>Click-by-Click Rietveld Tutorial</b><br>
      Follow along with the Co3O4 files in <code>examples</code>
    </td>
    <td align="center" width="33%">
      <a href="https://youtu.be/F7d1YJa7KX4"><img src="https://img.youtube.com/vi/F7d1YJa7KX4/mqdefault.jpg" width="240" alt="VESTA tutorial"></a><br>
      <b>Visualizing Structures in VESTA</b><br>
      Turn your refined CIF into a crystal structure figure
    </td>
  </tr>
</table>

### 3. Communicating results

<table>
  <tr>
    <td align="center" width="33%">
      <a href="https://youtu.be/rUV8VFbUi_U"><img src="https://img.youtube.com/vi/rUV8VFbUi_U/mqdefault.jpg" width="240" alt="Good vs bad scientific figures"></a><br>
      <b>Figures Part I: Good vs. Bad</b><br>
      Fundamentals of clear figures for papers and talks
    </td>
    <td align="center" width="33%">
      <a href="https://youtu.be/Y8JWfGjj2ok"><img src="https://img.youtube.com/vi/Y8JWfGjj2ok/mqdefault.jpg" width="240" alt="Basic figures how-to"></a><br>
      <b>Figures Part II: Basic How-To</b><br>
      Building clean, publication-ready plots
    </td>
    <td align="center" width="33%">
      <a href="https://youtu.be/fwZahTYfyxA"><img src="https://img.youtube.com/vi/fwZahTYfyxA/mqdefault.jpg" width="240" alt="Advanced figures how-to"></a><br>
      <b>Figures Part III: Advanced How-To</b><br>
      Advanced techniques for polished figures
    </td>
  </tr>
</table>

### 4. Scripted and AI-assisted refinement

A second track that refines the same data in Python with [rietx](https://rietx.org) and cross-checks the GSAS-II results. GSAS-II remains the main tool for the workshop. Each notebook opens in Google Colab with nothing to install. Local install and usage notes, including how to use it with Claude Code, are in [`scripted refinement (rietx)`](scripted%20refinement%20%28rietx%29/).

<table>
  <tr>
    <td align="center" width="33%">
      <a href="scripted%20refinement%20%28rietx%29/01_LaB6_instrument_calibration.ipynb"><b>01. LaB6 Instrument Calibration</b></a><br>
      Calibrate the instrument on a standard and track down a negative-B misfit<br>
      <a href="https://colab.research.google.com/github/sp8rks/Ceramic_Rietveld_Refinement/blob/main/scripted%20refinement%20%28rietx%29/01_LaB6_instrument_calibration.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"></a>
    </td>
    <td align="center" width="33%">
      <a href="scripted%20refinement%20%28rietx%29/02_Al2O3_Si_quantitative_phase_analysis.ipynb"><b>02. Al2O3/Si Phase Analysis</b></a><br>
      Two codes agree on 96.8/3.2 wt%, the balance says 90/10: why?<br>
      <a href="https://colab.research.google.com/github/sp8rks/Ceramic_Rietveld_Refinement/blob/main/scripted%20refinement%20%28rietx%29/02_Al2O3_Si_quantitative_phase_analysis.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"></a>
    </td>
    <td align="center" width="33%">
      <a href="scripted%20refinement%20%28rietx%29/03_Co3O4_temperature_series.ipynb"><b>03. Co3O4 Temperature Series</b></a><br>
      Refine a heating and cooling cycle in one script<br>
      <a href="https://colab.research.google.com/github/sp8rks/Ceramic_Rietveld_Refinement/blob/main/scripted%20refinement%20%28rietx%29/03_Co3O4_temperature_series.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"></a>
    </td>
  </tr>
</table>
