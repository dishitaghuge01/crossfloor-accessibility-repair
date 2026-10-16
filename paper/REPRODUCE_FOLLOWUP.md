# Follow-up reproduction

The original campaign stays unchanged. The follow-up was measured at a clean corrected commit, with no concurrent repository validation campaign. Two interrupted preliminary runs (`followup-ablations` and `followup-ablations-final`) are excluded. Reported timing uses only `followup-ablations-isolated`.

The research archive supplies original evidence under evidence/controlled and evidence/building, and supplemental evidence under evidence/followup-ablations and evidence/index-equivalence. Extract source-code.zip to a fresh repository-shaped folder. Restore the two original corpora at runs/revised-controlled-portable and runs/revised-building-portable (copy the corresponding supplied evidence folders); no IFC download is needed for these checks.

```text
python -m pip install -r requirements-release.lock.txt
python -m pip install -e . --no-deps
python scripts/run_followup_ablations.py --output runs/new-followup
python scripts/check_index_equivalence.py --evidence runs/revised-controlled-portable runs/revised-building-portable --output runs/new-index-comparison
python scripts/build_followup_master.py --evidence runs/new-followup --index runs/new-index-comparison --base path/to/supplied/paper --output runs/new-master
```

Run experiments from a clean Git checkout; a Git archive needs git init/add/commit before fresh timing because the runner intentionally requires a pinned clean revision. Do not rerun the index comparison concurrently with timing. The delivered current paper includes base-master.tex, the original 17-page source. The builder automatically uses that file when present, so regeneration adds the appendix exactly once. Alternatively compile the delivered current master directly with Tectonic 0.17.0 or another XeTeX-capable compiler; it already has all figures and inputs needed for typesetting.

For a manuscript-only audit from supplied follow-up evidence, use build_followup_master.py with --evidence path/to/evidence/followup-ablations and --index path/to/evidence/index-equivalence. It checks raw/normalized correspondence, clean pinned manifests, input fingerprints, original exact-label agreement and replays all returned selections. All data-derived outputs carry hashes. The no-dominance control retains duplicate histories and must use --no-compression. Indexed mode is opt-in; the default solver contract and frozen original timings remain unchanged.
