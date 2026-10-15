# IEEE master manuscript: reproduction and venue adaptation

This is a detailed conference-format master with full appendices, not a claimed acceptance guarantee or a venue-specific camera-ready submission. It uses the unchanged IEEEtran V1.8b class from the supplied June 2024 ZIP. The class retains its LPPL 1.3 notice. Guidance/example authors, funding, references and figures from the template are not included. No page limit has been imposed because no conference is selected. Author metadata are intentionally empty; actual author information and review anonymity rules must be supplied before submission.

## Reproduce the review revision

The current thirteen-page master has twenty references and nine vector figures.
Install the tested direct packages from requirements-review.lock.txt in a fresh
Python 3.12 environment, then install the package editable. The unchanged IEEE
class supports pdfLaTeX; the review PDF was compiled with TeX Live 2023 and all
fonts were verified embedded. No Type 3 fonts, undefined citations/references or
overfull boxes remain in its final compilation. LuaLaTeX in the review environment
lacked font-loader dependencies; it is not the tested reproduction engine.

The review archive keeps generated evidence outside Git. Paths below refer to
its selected core, corrected optimizers and consecutive-storey public runs.

```bash
python scripts/make_ieee_figures.py --controlled EVIDENCE/core --building EVIDENCE/duplex --demo EVIDENCE/demo --controls EVIDENCE/controls --optimizers EVIDENCE/optimizers --output runs/review-figures
python scripts/build_ieee_master.py --controlled EVIDENCE/core --building EVIDENCE/duplex --demo EVIDENCE/demo --controls EVIDENCE/controls --optimizers EVIDENCE/optimizers --public-audit EVIDENCE/public-audit --public-results EVIDENCE/public-results --figures runs/review-figures --output runs/review-master
cd runs/review-master
pdflatex -interaction=nonstopmode -halt-on-error master.tex
pdflatex -interaction=nonstopmode -halt-on-error master.tex
pdflatex -interaction=nonstopmode -halt-on-error master.tex
```

Use fresh empty output paths. The builder checks source fingerprints, strict
replay, exact labels, repetition counts, public screening coverage and independent
public oracle replays before inserting results. It orders bibliography entries
by first appearance. It rejects missing/changed evidence rather than filling
placeholder results. The corrected optimizer and DP runs have identical core
solver/kernel fingerprints; their revisions are recorded separately. The initial
CP-SAT import-timing pilot is excluded. See docs/review_action_matrix.md for the
executed comparison and scientific limits, and docs/public_building_review_protocol.md
for source download, inventory and regeneration.

## What to preserve when shortening

Keep the exact problem/scope, original objective and physical effects, parameter definitions, the state/completeness argument, reused-method attribution, meaningful baselines, operational statuses and limitations. Move the full proof, formula/scalarization details and complete status matrix to an allowed supplement first. Do not drop limitations to make an apparent stronger contribution, claim that hypothetical IFC annotations are source facts, turn limits into infeasibility, or call semantic controls valid competing solvers.

Figure roles: motivating before/after access graph; coupling-unit/full-action witness schematic; pipeline; candidate/owner scaling; compression-overhead plot; semantic-control costs; IFC subset/reservation plan; complete outcome matrix. The schematics are labeled. Timing plots retain all three observations and medians without confidence claims or recognition-time subtraction. Controls are deliberately invalid semantics, not a speed comparison. Historical Duplex variants remain grouped as one licensed source; twelve additional variants belong to three admitted sources. Their solver inputs still contain only two rooms each. The valid greedy-cost plot shows all non-forced authored cases with an observed positive cost gap.

## Conference-specific completion

Once a venue is chosen, verify its scope, page limit (including references/appendices), paper size, review anonymity and authorship fields, supplemental/artifact policies, ethics/disclosure requirements and PDF validation instructions. Remove or revise identifying metadata only as that venue requires; no universal double-anonymous rule is assumed. Add actual authors, affiliations and contact/ORCID information; do not invent funding or IRB approvals. The master includes an explicit AI-assistance disclosure; verify the selected venue's actual requirements. Human authors must review and take responsibility for the proof, sources and code. No independent human proof approval is claimed.

Run the venue's required PDF validation (such as PDF eXpress when the conference offers it) only after its details are known. No external PDF checker upload or conference submission has occurred. Fork and PR publication are explicitly user-authorized for this revision; publication status is recorded separately. IEEE-looking formatting does not resolve the remaining literature-priority question or ensure acceptance. See docs/ieee_master_requirements.md for official-source review criteria and the evidence assessment.
