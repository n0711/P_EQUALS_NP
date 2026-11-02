# XeLaTeX paper

**Deterministic Graph Search and Matrix-Based Validation: A Reproducible Framework for SAT-Oriented Research**

Charalampos Nadiotis, PELAOS Tech, Cyprus. 30 October 2026.

Source: [graph-search.tex](graph-search.tex). Compiled paper: [graph-search.pdf](graph-search.pdf).

The source is authoritative. Rebuild the PDF after changing the source so that the published document matches it.

From this directory, compile with XeLaTeX twice:

```powershell
xelatex -interaction=nonstopmode -halt-on-error graph-search.tex
xelatex -interaction=nonstopmode -halt-on-error graph-search.tex
```

Required packages: fontspec, geometry, amsmath, amssymb, amsthm, booktabs, array, xcolor, hyperref. Fonts: Latin Modern Roman, Latin Modern Sans, Latin Modern Mono. A current TeX Live or MiKTeX installation can provide them.

The paper and its XeLaTeX source use the author's ROS3-derived **Civilian-Use Licence (No Military Use), Version 1.0**. See [the full licence](../MANUSCRIPT_LICENCE.md), also included in the PDF appendix. The licence applies to the manuscript; it does not grant a new licence for the software or rights over independent implementations.

The report documents established graph-search algorithms and the recorded experiments. It does not claim a general polynomial-time SAT algorithm or a proof of P = NP.

## Additional XeLaTeX research note: frontier proof audit (2 November 2026)

- Source: [frontier-proof-audit.tex](frontier-proof-audit.tex).
- From the `paper/` directory: `xelatex -interaction=nonstopmode -halt-on-error frontier-proof-audit.tex` (run twice if cross-references change).
- Required body fonts: Comic Neue and Liberation Mono. The document uses an A4 handwritten-style layout.

This two-page note proves a conditional SAT reduction, formalizes the exact clause-frontier invariant, and records the width-parameterized bound and a fixed-order exponential obstruction. **It is not a proof of P = NP**, and it does not alter the conclusions of [PROOF_STATUS.md](../PROOF_STATUS.md) or [FRONTIER_COMPLEXITY.md](../FRONTIER_COMPLEXITY.md). The existing manuscript licence above specifically describes `graph-search.tex`; a licence for the additional note is not inferred by this index entry.
