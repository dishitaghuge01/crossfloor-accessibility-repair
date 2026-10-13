"""Small-instance exhaustive oracle, with a complete selection ledger."""
from __future__ import annotations

from decimal import Decimal
from collections.abc import Iterator

from .actions import apply_actions
from .errors import ValidationError, require
from .io import fingerprint
from .objective import action_cost, adjacency_delta, relaxed_cost, validate_topology_weight
from .obligations import verify_obligations
from .validation import validate_instance


def enumerate_action_subsets(ids: list[str]) -> Iterator[list[str]]:
    ids = sorted(ids)
    for mask in range(1 << len(ids)):
        yield [aid for i, aid in enumerate(ids) if mask & (1 << i)]


def exact_oracle(instance: dict, variant: str = "SCFAR", topology_weight: str = "1", max_actions: int = 20) -> dict:
    validate_instance(instance)
    require(variant in {"SCFAR", "RCFAR"}, "VARIANT", variant)
    weight = Decimal(str(topology_weight))
    validate_topology_weight(weight)
    ids = sorted(a["action_id"] for a in instance["actions"])
    require(len(ids) <= max_actions, "ACTION_LIMIT", f"{len(ids)} > {max_actions}")
    ledger = []
    best: tuple | None = None
    best_repair = None
    best_verification = None
    for selected in enumerate_action_subsets(ids):
        record = {"selected": selected}
        try:
            repair = apply_actions(instance, selected, variant, validated=True)
            verification = verify_obligations(repair["instance"], repair["active"])
            cost = action_cost(instance, selected) if variant == "SCFAR" else relaxed_cost(instance, selected, repair, weight)
            record.update(status="feasible" if verification["satisfied"] else "unsatisfied", cost=str(cost))
            key = (cost, len(selected), tuple(selected))
            if verification["satisfied"] and (best is None or key < best):
                best, best_repair, best_verification = key, repair, verification
        except ValidationError as error:
            record.update(status="invalid", error_code=error.code)
        ledger.append(record)
    status = "optimal" if best is not None else "infeasible"
    output = {"status": status, "variant": variant, "topology_weight": str(weight),
              "selected": list(best[2]) if best else None, "cost": str(best[0]) if best else None,
              "ledger": ledger, "input_fingerprint": fingerprint(instance),
              "optimality": {"method": "complete_action_subset_enumeration", "status": status,
                             "subsets": len(ledger), "ledger_fingerprint": fingerprint(ledger),
                             "lower_bound": str(best[0]) if best else None, "gap": "0" if best else None}}
    if best_repair is not None:
        output.update(reachability=best_verification, geometry=best_repair["geometry"],
                      adjacency=best_repair["adjacency"], delta_A=adjacency_delta(best_repair))
    return output
