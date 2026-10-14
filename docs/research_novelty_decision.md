# M08 research-first novelty decision

14 October 2026. No new solver code. **No positive algorithmic novelty claim has passed the audit. G3 remains OPEN.** Urgency changes prioritization, not the evidence standard.

## Direction 1: geometry-induced conflicts

Actual collisions are a narrower class than arbitrary declared exclusions, so M07's declared-conflict hardness must not be relabelled as physical hardness. But geometric shape restrictions alone are not promising originality evidence: existing rectangle independent-set theory already supplies serious parameterized barriers. [Pilipczuk/van Leeuwen/Wiese MFCS 2017 primary record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.MFCS.2017.42). Its shrinking model changes the feasible objects; physical asset footprints cannot be shrunk merely to import its guarantee.

A possible physical reduction would copy packing alternatives into nested priority suffix actions, with all copies meeting a common endpoint floor. To finish it, one must prove conflict equivalence, prevent same-asset exemptions, preserve reservations/clearance, and reconcile closed-square contacts with the kernel's positive-area tolerance. The original Marx 2005 unit-square source was located but not fully fetched; theorem excerpts are not a completed construction audit. No geometry-only hardness theorem is declared here.

Decision: prioritize an explicit physical structure rather than generic rectangular footprints. The [exclusive physical-menu candidate](physical_menu_candidate.md) supplies one precise structure and a working cost-preserving catalogue bound. Its originality and practical relevance remain unestablished.

## Direction 2: floor interfaces

Feldmann/Lampis's [ICALP 2024 paper](https://drops.dagstuhl.de/storage/00lipics/lipics-vol297-icalp2024/LIPIcs.ICALP.2024.61/LIPIcs.ICALP.2024.61.pdf), introduction/Theorem 2 and technique overview, records exact Steiner Forest hardness at treewidth three and explains active-demand partition information. Its width approximation and stronger exact parameters are existing results. This is a graph-theory barrier, not a proof that the restricted frozen-floor geometry realizes those hard instances.

Fellows/Guo/Kanj's [February 12, 2010 author preprint](https://www.researchgate.net/profile/Jiong-Guo-2/publication/220573969_The_Parameterized_Complexity_of_Some_Minimum_Label_Problems/links/0a85e53aa97dc07ba1000000/The-Parameterized-Complexity-of-Some-Minimum-Label-Problems.pdf), section 3/Theorem 3.1, explicitly reduces Hitting Set to labelled connectivity at small pathwidth. Thus a small access frontier does not automatically control bundle decisions. These are direct prior barriers to careless floor-width claims.

The proposed restriction uses rooted accessibility obligations, explicit bounded bundle span, per-floor profile components and complete reserved slots. Its working proof reduces arbitrary local catalogue density to finitely many exact signatures, then uses known connectivity-state machinery. The candidate contribution is the physical-to-combinatorial bound and its necessity witnesses, not a new partition DP. [Candidate proof](physical_menu_candidate.md).

Lampis's [arXiv:0910.0582v2](https://arxiv.org/html/0910.0582), section 2.2/Lemmas 2-3 and section 6, establishes neighborhood types and exchange symmetry. The candidate's representative selection is closely related to this prior idea. We must not call cheapest-equivalent-action selection novel. Nor does local per-window type count imply bounded global neighborhood diversity when floors are unbounded.

Decision: keep exactly this scoped physical-menu characterization as the leading research candidate. Do not build it before a direct equivalent-model comparison and independent proof check. Ordinary floor width or generic MSO is not the claim.

## Direction 3: repair near an accessible reference

There is a useful but elementary bound. Suppose each original profile graph is connected and at most d of its edges are deleted, with no room changes. Each baseline profile graph then has at most d+1 connected components. For any feasible selected activation set, choose a spanning forest of its quotient connectivity in each profile and choose one supplying action for each forest edge. The union of these suppliers contains at most p*d actions and preserves every selected connectivity relation, hence all obligations. Removing other actions preserves pairwise geometry admissibility and nonnegative cost; an optimum with minimum action count therefore uses at most p*d actions.

This argument requires deletion-only corruption, a connected reference in every profile, monotone independent activations and downward-closed unary/pairwise admissibility. With original c_p components, replace d by d+c_p-1 in the sum. Dependencies invalidate the deletion step. The bound gives direct enumeration in K^(p*d), an XP algorithm, not an FPT algorithm. It is a spanning-forest witness argument and is not claimed original. Small damage by itself does not eliminate difficult geometric compatibility choices.

The [2025 solution-discovery preprint](https://arxiv.org/html/2510.17344v1), model definitions and Theorem 4.3, already studies bounded-change discovery with logic/width parameters. Its changes are token moves on a fixed graph, not our atomic connection additions; it is a comparator, not a theorem transferred without a reduction.

Decision: do not prioritize another generic damage-budget solver. Revisit this direction only if the physical-menu audit produces a stronger independent parameter bound.

## Architectural novelty correction

Strug/Slusarczyk's [2017 BIM/IFC accessibility paper](https://link.springer.com/article/10.1186/s40327-017-0048-z), graph-model and route-search sections, already distinguishes adjacent spaces from passable openings, represents vertical facilities, and uses entry/exit lookup tables for accessible routing. It optimizes travel effort on existing facilities; the inspected method does not select minimum-cost construction/representation repair bundles. Therefore A/D separation, IFC graphs or wheelchair-aware routing alone are not novel. A difference in repair decision space remains, but the complete method's originality needs a broader repair/retrofit comparison and evaluation.

## Concrete decision and evidence bar

The leading proposed statement is: **exact rooted accessibility repair under exclusive reserved slots admits a catalogue bound independent of alternative density, and an FPT algorithm in local interface components, slot count, profile count and action span, retaining original physical action witnesses.** It is currently a candidate with a working proof, not established novelty.

Before promoting it: inspect local finite-domain/weighted type-compression and constrained-labelled connectivity methods; seek a direct prior derivation that subsumes the physical bound; independently review the signature/exchange/state proof; and justify the complete-slot/private-bundle/rooted restriction with documented repair scenarios. If it reduces to a routine reformulation or the assumptions have no useful application, reject it. A search with no matching title cannot pass this bar.

The existing 512-test implementation remains available for later falsification. This pass adds research notes and primary-source locators only. No new performance claim, benchmark, dataset ingestion or thesis novelty declaration is made.
