"""Integrate the bounded priority comparison and building admission assessment."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(base, output):
    source = base / 'pre-gap-master.tex'
    if not source.exists():
        source = base / 'master.tex'
    original = source.read_text(encoding='utf-8')
    assert 'Finite-Domain Resource Comparison' not in original
    old = ('A narrower encoding or domain-valued resource/connectivity method might match our dependence. '
           'Thus \\eqref{eq:generic} compares constructed upper bounds, not a universal separation or priority proof.')
    assert original.count(old) == 1
    clarification = r'''A finite-domain resource treatment supplied the same complete-unit schedule can use the same owner factor: each live cell has empty, completed-unit occupied, or a current-owner value, at most $h+2$ values. Combining this domain with the same attributed connectivity compression reproduces our state dependence. Thus \eqref{eq:generic} compares two explicit constructions; it supplies no separation from all generic resource/connectivity methods and no priority proof. Appendix~\ref{app:assessment} states the remaining claim boundary.'''
    final = original.replace(old, clarification)
    marker = r'\clearpage' + '\n' + r'\IEEEtriggeratref{12}'
    assert final.count(marker) == 1
    addition = r'''
\section{Completed Comparison and Evidence Assessment}\label{app:assessment}
\subsection{Finite-Domain Resource Comparison}
This project derivation addresses an unresolved interpretation of the bound; it is not a newly located prior theorem. Let $b\leq prL$ be the live profile boundary and $c\leq zL$ the live collision-cell count. During a complete action--owner unit, store for each cell an empty value, a completed-unit occupancy value, or one of at most $h$ current owners. Every selected action updates all paid effect cells, allowing equal-owner reuse and rejecting different-owner occupancy. Upon completing the unit, replace its owner values by occupied. No future action can use those owners, because complete action--owner incidence components define the units. Consequently there are at most $(h+2)^c$ resource assignments. Plain connectivity partitions can still require $2^{O(b\log(b+2))}$ possibilities; the same established weighted representative reduction used here supplies the single-exponential connectivity factor.

This is a reformulation of our existing argument in finite-domain state language, not a second independently executed optimizer or a published CSP metatheorem. A generic connectivity/resource treatment supplied this valid schedule and reduction can reproduce the resource dependence. Accordingly, logarithmic dependence on owner multiplicity is not by itself a novelty or universal-superiority argument. The surviving claim is the explicit recognized physical-to-interface construction, preservation of complete actions and original objective, scoped correctness argument, and reproducible implementation/evaluation. No matching prior complete construction was identified in the bounded inspection, but its absence is not established. The 2022 conference predecessor of the choice-network paper~\cite{choice2022} was also located; publisher access exposed its abstract and references, not full proofs. The 2023 full text remained inaccessible. Literature priority and independent human proof review remain open.

\subsection{Installed-Intervention Evidence: Marble Hill}
An additional documentary screen examines Marble Hill House. The architect report~\cite{marbleaccess} identifies a ground-to-first-floor lift location and structural alterations. The planning drawing schedule~\cite{marbleplanning} lists existing/proposed lift-area sheets 300~A/301~E. The owner's project journal~\cite{marblejournal} reports approval in December 2018 and installation by February 2022. This strengthens intervention/completion evidence, but does not establish our model's metric reservations, full profile routes or atomic price. Actual drawing sheets and matching approval conditions were not obtained. The public planning page loaded; its document API blocked retrieval. Access failure is not a finding that the design violates the model.

No additional solver input is admitted. Structural floor work alone establishes neither preservation nor violation of frozen 2D room polygons; the existing/proposed geometry must settle that question. Owner-reported completion is not our site verification, and a project-level grant is not an intervention cost. Both this screen and the City Hall study remain documentary evidence, separate from the eight controlled building-derived inputs and 2274 timed observations. Hypothetical annotations cannot close actual-building validation. The delivery therefore contains completed executable studies and an explicit unresolved scientific boundary, rather than a claim of established priority or validated construction repairs.
'''
    final = final.replace(marker, addition + '\n' + marker)
    bibliography = r'''
\bibitem{choice2022} P. Wojciechowski, K. Subramani, and A. Velasquez, ``Analyzing the Reachability Problem in Choice Networks,'' in \emph{CPAIOR}, LNCS 13292, 2022, pp.408--423, doi:10.1007/978-3-031-08011-1\_27.
\bibitem{marbleaccess} Acanthus Clews Architects, ``Marble Hill House: Repairs and Alterations, Design and Access Report,'' rev.C, Aug.24, 2018. [Online]. Available: \url{https://www.english-heritage.org.uk/link/722a3f30b0374c3eb903129da002158b.aspx}.
\bibitem{marbleplanning} Lichfields, ``Marble Hill Parks for People: Planning Statement,'' Sep.2018, drawing schedule, PDF p.37. [Online]. Available: \url{https://www.english-heritage.org.uk/link/5c94c36216184066b9685eb276b9d1e1.aspx}.
\bibitem{marblejournal} English Heritage, ``Marble Hill Revived,'' project journal, Dec.2018 and Feb.2022 entries. Accessed Oct.16, 2026. [Online]. Available: \url{https://www.english-heritage.org.uk/visit/places/marble-hill/marble-hill-revived/}.
'''
    final = final.replace(r'\end{thebibliography}', bibliography + '\n' + r'\end{thebibliography}')
    shutil.copytree(base, output, ignore=shutil.ignore_patterns(
        'preview', 'master.pdf', 'master.log', 'compile-console.txt',
        'pdf-qa.json', 'extracted-text.txt'))
    (output / 'pre-gap-master.tex').write_text(original, encoding='utf-8')
    (output / 'master.tex').write_text(final, encoding='utf-8')
    evidence = [Path('docs/generic_state_comparison.md'),
                Path('docs/marble_hill_evidence_screen.md'),
                Path('docs/gap_assessment_completion.md')]
    provenance = dict(new_timed_observations=0, new_admitted_physical_instances=0,
                      priority='unconfirmed', actual_building_validation='not_established',
                      files={str(p): sha(p) for p in [Path(__file__), source, *evidence]},
                      manuscript_sha256=sha(output / 'master.tex'))
    (output / 'gap-assessment-provenance.json').write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(output / 'master.tex')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ['base', 'output']:
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    build(args.base, args.output)
