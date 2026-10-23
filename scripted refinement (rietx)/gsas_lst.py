"""Read the handful of numbers we compare against from a GSAS-II .lst listing.

GSAS-II writes a plain-text report after every refinement. This helper pulls
out the final agreement indices and, per phase, the refined cell, the
isotropic displacement parameters and the weight fraction. It reads the file
only; nothing in `refinement examples/` is changed.
"""
import re
from pathlib import Path

_NUM = r"[-+]?\d+\.\d+(?:[eE][-+]?\d+)?"


def read_lst(path):
    text = Path(path).read_text(errors="replace")
    out = {"path": str(path), "phases": {}}

    # The last "wR = ..., GOF = ..." line is the final cycle.
    fits = re.findall(rf"wR =\s*({_NUM})%, chi\*\*2 =\s*([\d.eE+-]+), GOF =\s*({_NUM})", text)
    if fits:
        wr, chi2, gof = fits[-1]
        out.update(wR=float(wr) / 100, chi2=float(chi2), gof=float(gof))
    dw = re.findall(rf"Durbin-Watson statistic =\s*({_NUM})", text)
    if dw:
        out["durbin_watson"] = float(dw[-1])
    lam = re.search(rf"Lam1\s+Lam2.*\n\s*value :\s*{_NUM}\s+{_NUM}\s+({_NUM})\s+({_NUM})", text)
    if lam:
        out["lam1"], out["lam2"] = float(lam.group(1)), float(lam.group(2))
    excl = re.findall(rf"Excluded region:\s*({_NUM}) deg to\s*({_NUM}) deg", text)
    out["excluded_regions"] = [(float(a), float(b)) for a, b in excl]

    # Refined results: one "Result for phase:" block per phase.
    blocks = re.split(r"\n Result for phase: ", text)[1:]
    for block in blocks:
        name = block.splitlines()[0].strip()
        ph = {}
        cell = re.search(
            rf"New unit cell:.*?\n\s*values:\s*({_NUM})\s+({_NUM})\s+({_NUM})\s+({_NUM})\s+({_NUM})\s+({_NUM})\s+({_NUM})"
            rf"\s*\n\s*esds\s*:\s*({_NUM})?", block, re.S)
        if cell:
            ph["a"], ph["b"], ph["c"] = (float(cell.group(i)) for i in (1, 2, 3))
            ph["a_esd"] = float(cell.group(8)) if cell.group(8) else None
        uiso = {}
        for atom, u in re.findall(rf"\n\s+(\S+)\s+\S+:\n values:\s+{_NUM}\s+{_NUM}\s+{_NUM}\s+{_NUM}\s*({_NUM})", block):
            uiso[atom] = float(u)
        ph["uiso"] = uiso
        out["phases"][name] = ph

    # Weight fractions sit in the per-histogram "Phase: X in histogram" blocks.
    for chunk in re.split(r"\n Phase: ", text)[1:]:
        name = chunk.split(" in histogram:")[0].strip()
        wf = re.search(rf"Weight fraction\s*:\s*({_NUM}), sig\s*({_NUM})", chunk.split("\n Histogram:")[0])
        if wf:
            out["phases"].setdefault(name, {}).update(
                weight_fraction=float(wf.group(1)), weight_fraction_esd=float(wf.group(2)))
    return out
