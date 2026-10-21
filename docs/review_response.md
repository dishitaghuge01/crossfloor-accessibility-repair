# Response to the five research/reporting concerns

## 1. Practical advantage: limitation accepted,not solved by editing

The saved campaign has15 seeded connectivity inputs. Compressed DP is slower
than uncompressed DP on all15; median ratios range1.0210--2.2023. CP-SAT and
uncompressed DP both complete all repetitions of four natural shaft cases
where compressed mode reaches its cap. These findings are now stated in the
abstract,introduction,discussion and conclusion. No new timing was run and
no runtime advantage is claimed. Theoretical novelty must be judged on the
complete physical construction; the generic owner-state factor does not
supply a universal separation. Literature priority remains unconfirmed.

## 2. Building difficulty: limitation accepted,not solved by the CAD pilot

The eight IFC-derived catalogues contain only2--3actions,with marked effective
component counts1--2. They check geometry adaptation,semantics and limited
coupling,not difficult practical access-network optimization. The two-room
CAD/four-variant pilot likewise checks input handling and semantic correctness.
It is moved out of the main paper into the evidence supplement. No extra tiny
cases or invented complexity were added to suggest a practical result.

A materially stronger practical claim still requires nontrivial,evidence-backed
intervention choices and route constraints on building geometry. A stronger
theoretical publication claim still requires a checked distinctness argument
for the complete construction. Neither is produced by this reporting revision.

## 3. TableVIII: corrected from normalized and raw records

Root cause: the authored timing-table generator accepted only optimal and
infeasible statuses,omitting successful feasible heuristic returns. The
building timing table already accepted feasible returns and is unchanged.
The shared authored helper now counts feasible as a measured completion,
without implying optimality,and identifies actual failure statuses.

| Case | Improved-greedy median seconds | Observed min--max | Statuses |
| --- | --- | --- | --- |
| catalogue-128-s0 | -- | -- | 3 timeouts |
| ownership-8-s0 | 1.7319 | 1.7026--1.8784 | 5 feasible |
| profiles-4-s0 | 0.0567 | 0.0532--0.0653 | 5 feasible |
| connectivity-7-s0 | 6.7201 | 6.5887--6.7728 | 3 feasible |
| support-8-s0 | 0.1316 | 0.1287--0.1362 | 5 feasible |
| rooms-12-s0 | 0.4831 | 0.4777--0.4913 | 5 feasible |

The caption defines completion. Raw statuses/times were checked against every
displayed row; the outcome matrices remain unchanged. Three targeted regression
tests passed in0.10s. reporting-audit.json saves the statuses,cells,record
fingerprints,all15ratios and source catalogue sizes.

## 4. Final-study chronology: reconciled

SectionVI and AppendixE consistently describe implemented history/no-merging,
complete-unit reverse order and optional spatial indexing. History mode turns
off both minimum-label merging and representative compression; it is not a
one-factor dominance-only ablation. Reverse order preserves whole ownership
units and the floor schedule; it does not establish arbitrary-order behavior.
Separate pinned campaigns/budgets remain distinct experimental settings,not
unimplemented development stages. The upstream evaluation-text source is fixed.

## 5. Documentary material: separated

The19-page main manuscript has16 research figures and retains the model,proof,
optimizer comparisons,controlled results and final ablations. Historical price
extraction,source-access/admission studies and the small CAD pilot are in a
separate4-page evidence report with2figures and the review package's
supplementary-evidence/ subtree. Versioned source records stay accessible from
docs/supplementary_evidence/README.md. No new public repository or push was made.

Both PDFs compile with embedded fonts,no Type3 fonts,undefined references or
overfull diagnostics. All changed content was visually reviewed; the final
main bibliography was repaired after removal of obsolete column breaking.
The reproducibility package preserves every original measurement and moves
supporting evidence rather than deleting unfavorable outcomes. The final
source archive regenerates the corrected main/supplement from saved evidence.
