# Reproduce the documentary admission study

The delivered paper already includes AppendixF. Its scalar evidence is in evidence/city-hall-documentary. This is a deterministic document audit, not an additional timed solver campaign. Existing timed observations remain2274.

1. Read city_hall_admission.md and city_hall_documentary_protocol.md. Retrieve the source PDF from the official URL in admission.json, saving it outside Git. Its required SHA256 is31b125ed7371564f3c7e4254237464cac7bf9fc1ff68bb8c46dec556d9fcf3a1. The extractor rejects a different revision. No source PDF or copied drawing is distributed.
2. Extract source-code.zip. Install requirements-release.lock.txt plus requirements-documentary.lock.txt in a suitable Python environment, then install the project editable with --no-deps. The tested documentary packages are recorded in admission.json. For a clean-revision manifest, use a Git checkout or initialize/commit the extracted archive before extraction.
3. Run the documentary extractor into a fresh directory:

```text
python scripts/audit_city_hall_document.py --pdf path/to/source.pdf --output runs/new-city-hall
```

4. Build the manuscript from supplied evidence and the delivered paper folder:

```text
python scripts/build_documentary_master.py --case path/to/evidence/city-hall-documentary --base path/to/paper --output runs/new-documentary-master
```

The current supplied folder includes pre-documentary-master.tex (the prior19-page master); the builder selects it automatically to avoid duplicating AppendixF. base-master.tex remains the original17-page source for the earlier follow-up builder. Figures and all source stages are retained. Compile master.tex with Tectonic0.17.0 or another XeTeX-capable compiler and visually inspect the regenerated pages.

For source-data regeneration, substitute --case runs/new-city-hall. The builder checks scalar-record roles, exact arithmetic, extraction hash, clean manifest and unadmitted status. New documents must receive new source-specific audits; do not remove the pinned hash guard to force admission.

The extraction creates private-source-rows.json for local review. Do not include it, the PDF or source raster images in a review/publication package. Only the selected scalar outputs listed in package_documentary_release.py are delivered. Source recommendations, unit/reference entries and historical estimates are not an admitted action catalogue or evidence of completed renovations.

The original extraction hash records Windows source bytes. The manuscript builder accepts only that exact source with equivalent LF or CRLF line endings, accommodating Git archive normalization; other source changes still fail the hash check.
