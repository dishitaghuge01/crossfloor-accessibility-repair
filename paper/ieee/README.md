# IEEE master manuscript: reproduction and venue adaptation

This is a detailed conference-format master with full appendices, not a claimed acceptance guarantee or a venue-specific camera-ready submission. It uses the unchanged IEEEtran V1.8b class from the supplied June 2024 ZIP. The class retains its LPPL 1.3 notice. Guidance/example authors, funding, references and figures from the template are not included. No page limit has been imposed because no conference is selected. Author metadata are intentionally empty; actual author information and review anonymity rules must be supplied before submission.

## Reproduce from saved evidence

Use the source checkout and the saved final evidence in the review archive. Install the optional figure requirements in the same Python 3.12 environment after requirements-dev.lock.txt/requirements-ifc.lock.txt. Figure source is deterministic Matplotlib vector plotting; the large original solver suite need not be remeasured to rebuild the paper.

```powershell
New-Item -ItemType Directory -Force runs/tmp | Out-Null
$env:TEMP = (Resolve-Path runs/tmp).Path
$env:TMP = $env:TEMP
$env:MPLCONFIGDIR = (Resolve-Path runs/tmp).Path
.\.venv\Scripts\python.exe -m pip install -r requirements-figures.lock.txt
.\.venv\Scripts\python.exe scripts/run_semantic_controls.py --evidence runs/final-controlled --output runs/rebuild-semantic
.\.venv\Scripts\python.exe scripts/make_ieee_figures.py --controlled runs/final-controlled --building runs/final-building --demo runs/final-demo --controls runs/rebuild-semantic --output runs/rebuild-ieee-figures
.\.venv\Scripts\python.exe scripts/build_ieee_master.py --controlled runs/final-controlled --building runs/final-building --demo runs/final-demo --controls runs/rebuild-semantic --figures runs/rebuild-ieee-figures --output runs/rebuild-ieee-master
tectonic -X compile --untrusted --keep-logs --outdir runs/rebuild-ieee-master runs/rebuild-ieee-master/master.tex
```

Use fresh empty paths. For new clean-revision semantic evidence, commit source before running controls. The original timing experiments remain at 9735c0f, and the semantic controls at 4e9f8e3. Their timestamps/environment/hashes/statuses are preserved rather than relabeled. To regenerate solver experiments from scratch, follow paper/REPRODUCE.md. The target build needs master.tex, IEEEtran.cls and figures/ beside it. Tectonic 0.17.0 with a writable TECTONIC_CACHE_DIR compiled the delivery. Standard pdflatex with the listed packages is also supported by the source; this alternative was not run here. XeLaTeX/Tectonic use TeX Gyre Termes (Times metrics) to preserve the class's intended text typography, rather than defaulting to Latin Modern. Figure labels use Times New Roman on this Windows workstation, with a serif fallback for other environments. All PDF fonts are embedded.

## What to preserve when shortening

Keep the exact problem/scope, original objective and physical effects, parameter definitions, the state/completeness argument, reused-method attribution, meaningful baselines, operational statuses and limitations. Move the full proof, formula/scalarization details and complete status matrix to an allowed supplement first. Do not drop limitations to make an apparent stronger contribution, claim that hypothetical IFC annotations are source facts, turn limits into infeasibility, or call semantic controls valid competing solvers.

Figure roles: motivating before/after access graph; coupling-unit/full-action witness schematic; pipeline; candidate/owner scaling; compression-overhead plot; semantic-control costs; IFC subset/reservation plan; complete outcome matrix. The schematics are labeled. Timing plots retain all three observations and medians without confidence claims or recognition-time subtraction. Controls are deliberately invalid semantics, not a speed comparison. Building variants remain grouped as one licensed source.

## Conference-specific completion

Once a venue is chosen, verify its scope, page limit (including references/appendices), paper size, review anonymity and authorship fields, supplemental/artifact policies, ethics/disclosure requirements and PDF validation instructions. Remove or revise identifying metadata only as that venue requires; no universal double-anonymous rule is assumed. Add actual authors, affiliations and contact/ORCID information; do not invent funding or IRB approvals. IEEE's published AI-content policy requires the disclosure included here. Human authors must review and take responsibility for the proof, sources and code. No independent human proof approval is claimed.

Run the venue's required PDF validation (such as PDF eXpress when the conference offers it) only after its details are known. No external checker upload, public release, submission or automatic push has occurred. IEEE-looking formatting does not resolve the remaining literature-priority question or ensure acceptance. See docs/ieee_master_requirements.md for official-source review criteria and the evidence assessment.
