"""Audit manuscript review tables against saved inputs/results/manifests."""
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from statistics import median

from cfar.io import fingerprint


def samples(root, case, method):
    folder = root/case
    instance = json.loads((folder/"input.json").read_text())
    values = []
    for path in sorted(folder.glob(method+"-[0-9].json")):
        value = json.loads(path.read_text())
        meta = json.loads(path.with_suffix(".manifest.json").read_text())
        if (meta["git_dirty"] or meta["input_fingerprint"] != fingerprint(instance) or
            meta["solver_status"] != value["status"] or meta["settings"]["method"] != method):
            raise ValueError("measurement provenance mismatch: "+str(path))
        if value["status"] in {"optimal", "feasible"}:
            r = value["result"]
            if not r["reachability"]["satisfied"] or any(a["delta"] for a in r["adjacency"].values()):
                raise ValueError("strict replay failed: "+str(path))
            if method == "cp-sat" and any(s["status"] != "OPTIMAL" for s in r["statistics"]["stages"]):
                raise ValueError("unproved CP-SAT lexicographic stage")
        values.append(value)
    if not values:
        raise ValueError("missing method: "+case+"/"+method)
    return instance, values


def optimization_audit(controlled, optimizers):
    names = sorted(p.name for p in controlled.iterdir() if p.is_dir())
    counts = {m: Counter() for m in ("compressed", "uncompressed", "cp-sat", "greedy")}
    comparable, greedy_excess = 0, []
    expected_sources = None
    for name in names:
        signatures = []
        expected_input = None
        optimum = None
        for method in counts:
            method_root = optimizers if method in {"cp-sat", "greedy"} else controlled
            instance, values = samples(method_root, name, method)
            metadata = json.loads((method_root/name/(method+"-0.manifest.json")).read_text())
            if expected_sources is None:
                expected_sources = metadata["source_fingerprints"]
            if metadata["source_fingerprints"] != expected_sources:
                raise ValueError("solver/kernel sources differ across measurements")
            if expected_input is None:
                expected_input = fingerprint(instance)
            if fingerprint(instance) != expected_input:
                raise ValueError("methods used different input: "+name)
            if len(values) != (1 if method == "greedy" else 3):
                raise ValueError("repetition contract failed: "+name+"/"+method)
            first = values[0]
            if any(v["status"] != first["status"] for v in values):
                raise ValueError("unstable status: "+name)
            counts[method][first["status"]] += 1
            for value in values:
                if value["status"] in {"optimal", "infeasible"}:
                    r = value["result"]
                    signatures.append((r["status"], Decimal(r["cost"]) if r["cost"] is not None else None, r["selected"]))
                    optimum = r
        if signatures and any(s != signatures[0] for s in signatures):
            raise ValueError("exact solver disagreement: "+name)
        if signatures:
            comparable += 1
        _, greedy = samples(optimizers, name, "greedy")
        if greedy[0]["status"] == "feasible" and optimum is not None:
            if optimum["status"] == "infeasible":
                raise ValueError("greedy feasible on exactly infeasible input")
            excess = Decimal(greedy[0]["result"]["cost"]) - Decimal(optimum["cost"])
            if excess < 0:
                raise ValueError("greedy below exact optimum")
            greedy_excess.append(excess)
    return dict(cases=len(names), counts={m:dict(v) for m,v in counts.items()}, exact_cases=comparable,
                greedy_cost_matches=sum(v == 0 for v in greedy_excess), greedy_compared=len(greedy_excess))


def optimization_table(controlled, optimizers):
    audit = optimization_audit(controlled, optimizers)
    if audit["cases"] != 37 or audit["counts"]["cp-sat"] != {"optimal":25,"infeasible":10,"unsupported":2} or audit["greedy_cost_matches"] != 20:
        raise ValueError("review narrative requires updating for these outcomes")
    names = ["dense-8", "dense-32", "dense-64", "dense-128", "owners-2", "owners-4", "owners-8", "owners-16", "cyclic", "rooms"]
    rows = []
    for name in names:
        row = [name.replace("dense-","n=").replace("owners-","h=")]
        for m in ("compressed", "uncompressed", "cp-sat", "greedy"):
            _, values = samples(optimizers if m in {"cp-sat", "greedy"} else controlled, name, m)
            row.append(f"{median(v['elapsed_seconds'] for v in values):.4f}")
        rows.append(" & ".join(row)+r" \\")
    lines = [r"\subsection{Executed Optimization Comparison}",
        r"CP-SAT completes the same 35 recognized authored inputs (25 optimal, ten infeasible); two inputs remain outside recognition. Every completed exact cost/count/identifier label agrees with the DP and eligible oracle. CP-SAT also resolves the four natural cut-column-limit cases; the fifth DP limit is a deliberately forced one-state cap. Greedy finds a replay-valid repair on 25 cases and fails on ten; failure remains a heuristic status. Its cost matches the optimum on 20 of the 25 feasible cases. The other five include the repeated cyclic input used for the forced-cap control. On shared\_asset it pays eleven rather than the exact five, and on separate\_profiles it pays four rather than three. These are valid repairs under the same objective, unlike the semantic controls.",
        r"\begin{table}[t]\caption{Same-Model Function Times in Seconds: Three-Sample Medians for Exact Solvers; One Greedy Sample}\label{tab:optimization}",
        r"\centering\footnotesize\setlength{\tabcolsep}{3pt}\begin{tabular}{lrrrr}\toprule",
        r"Case & Comp. & Full & CP-SAT & Greedy \\\midrule"]
    lines += rows + [r"\bottomrule\end{tabular}\end{table}",
        "All times include recognition and complete repair replay and exclude imports/startup. These small local samples are descriptive; they establish neither general DP superiority nor general compression benefit."]
    return "\n".join(lines), audit


def public_section(audit_root, result_root):
    audit_rows = json.loads((audit_root/"summary.json").read_text())
    admitted = [r for r in audit_rows if r["status"] == "controlled-subset-admitted"]
    names = sorted(p.name for p in result_root.iterdir() if p.is_dir())
    if len(names) != sum(r["variants"] for r in admitted):
        raise ValueError("public case coverage mismatch")
    outcomes = Counter()
    for name in names:
        signatures = []
        for method in ("compressed", "uncompressed", "cp-sat", "oracle"):
            _, values = samples(result_root, name, method)
            if len(values) != (1 if method == "oracle" else 3):
                raise ValueError("public repetition contract failed")
            for value in values:
                r = value["result"]
                signatures.append((r["status"], r["cost"], r["selected"]))
        if any(v != signatures[0] for v in signatures):
            raise ValueError("public exact comparison mismatch")
        replay = json.loads((result_root/name/"oracle-replay.json").read_text())
        if not replay["valid"]:
            raise ValueError("public oracle certificate not replayed")
        outcomes[signatures[0][0]] += 1
    if len(audit_rows) != 5 or len(admitted) != 3 or outcomes != {"optimal":9,"infeasible":3}:
        raise ValueError("public narrative requires updating for these outcomes")
    rows = []
    for row in audit_rows:
        c = row["counts"]
        label = row["building"].replace("schependomlaan", "Schependomlaan").capitalize()
        rows.append(f"{label} & {c['storeys']} & {c['spaces']} & {c['eligible_spaces']} & " +
                    ("4 variants" if row in admitted else "Excluded") + r" \\")
    lines = [r"\section{Public-Source Screening and Controlled Corruptions}",
        r"Five pinned IFC sources from the buildingSMART community collection were inventoried \cite{publicifc}. Four were screened initially; Molio was a disclosed feasibility follow-up after two exclusions, not a preregistered representative sample. Table~\ref{tab:publicscreen} retains the admission denominator. Every space and stair/transport element is inventoried. Simple orthogonal, hole-free XY rings retain world coordinates and GlobalIds; unmapped physical background prevents admission.",
        r"\begin{table}[t]\caption{Public IFC Screening; Storey/Space Counts Describe Source Inventory, Not Solver Input}\label{tab:publicscreen}",
        r"\centering\footnotesize\setlength{\tabcolsep}{3pt}\begin{tabular}{lrrrl}\toprule Source & Storeys & Spaces & Eligible & Outcome \\\midrule"]
    lines += rows + [r"\bottomrule\end{tabular}\end{table}",
        "Duplex, Clinic and Molio admit deterministic two-room subsets of consecutive source storeys; no intervening source floor is skipped. Pairs are ranked by common projected area and GlobalIds, then checked against two aligned 0.7m squares on a fixed 0.8m grid. All source stair/lift XY envelopes remain conservative obstacles on both experimental floors. Esplanades has no eligible orthogonal simple space; Schependomlaan has three eligible spaces but no admitted aligned pair. Earlier candidate rejections remain in audit files.",
        "A replayed hypothetical reference enables both profile routes with action D; removing those activations defines the corrupted baseline. This is known finite-model feasibility, not evidence of original IFC portal validity. Four catalogue variants per admitted source reproduce bundle, separate, missing-profile and single-action regimes. All twelve comparisons agree across compressed DP, full DP, CP-SAT and exhaustive oracle: nine optimal and three infeasible. Twelve oracle certificates are independently replayed.",
        "These cases expand geometry provenance across three source models, but use one room per selected floor, empty within-floor adjacency, hypothetical reservations/profiles/costs and authored portals. They do not test complete multi-storey extraction, nontrivial whole-floor topology preservation or actual renovation. Source space counts must not be reported as optimized room counts. Larger multi-room building experiments remain an explicit breadth requirement."]
    return "\n".join(lines), dict(sources=len(audit_rows), admitted=len(admitted), cases=len(names), outcomes=dict(outcomes))
