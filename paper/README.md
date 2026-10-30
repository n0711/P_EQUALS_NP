# XeLaTeX paper

**Deterministic Graph Search and Matrix-Based Validation: A Reproducible Framework for SAT-Oriented Research**

Charalampos Nadiotis, PELAOS Tech, Cyprus. 30 October 2026.

Source: [graph-search.tex](graph-search.tex). Compiled paper: [graph-search.pdf](graph-search.pdf).

From this directory, compile with XeLaTeX twice:

```powershell
xelatex -interaction=nonstopmode -halt-on-error graph-search.tex
xelatex -interaction=nonstopmode -halt-on-error graph-search.tex
```

Required packages: fontspec, geometry, amsmath, amssymb, amsthm, booktabs, array, xcolor, hyperref. Fonts: Latin Modern Roman, Latin Modern Sans, Latin Modern Mono. A current TeX Live or MiKTeX installation can provide them.

The paper and its XeLaTeX source use the author's ROS3-derived **Civilian-Use Licence (No Military Use), Version 1.0**. See [the full licence](../MANUSCRIPT_LICENCE.md), also included in the PDF appendix. The licence applies to the manuscript; it does not grant a new licence for the software or rights over independent implementations.

The report documents established graph-search algorithms and the recorded experiments. It does not claim a general polynomial-time SAT algorithm or a proof of P = NP.
