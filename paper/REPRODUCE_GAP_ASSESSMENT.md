# Reproduce the final assessment integration

This stage adds no timed benchmark or admitted physical instance. Read
gap_assessment_completion.md, generic_state_comparison.md and
marble_hill_evidence_screen.md. The assessment states explicit access and
scientific limits; it does not claim priority or actual-building validation.

From the extracted source-code root, using the delivered paper directory:

```text
python scripts/build_gap_assessment_master.py --base path/to/paper --output runs/new-assessment-master
```

The builder selects pre-gap-master.tex from an already integrated release to
avoid duplication. For a complete sequential rebuild, first run the original,
follow-up and documentary stages described in the other reproduction guides,
then supply that documentary output as --base. Compile the resulting
master.tex with Tectonic0.17.0 or another XeTeX-capable compiler. Perform PDF
font/reference/page-size checks and visual review before distribution.

gap-assessment-provenance.json fingerprints the input source, builder and
assessment documents. It records unconfirmed priority, unestablished
actual-building validation, zero new timed observations and zero new admitted
physical inputs. Generated artifacts remain outside Git.
