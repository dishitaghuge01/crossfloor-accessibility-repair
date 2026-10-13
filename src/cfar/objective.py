from decimal import Decimal, localcontext
from collections.abc import Iterable

from .errors import require


def exact_sum(values: Iterable[Decimal]) -> Decimal:
    values = list(values)
    if not values:
        return Decimal(0)
    low = min(value.as_tuple().exponent for value in values)
    high = max(value.adjusted() for value in values)
    with localcontext() as context:
        context.prec = max(1,high-low+1+len(str(len(values))))
        return sum(values,Decimal(0))


def exact_product(first: Decimal, second: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = max(1,len(first.as_tuple().digits)+len(second.as_tuple().digits))
        return first*second


def validate_topology_weight(weight: Decimal) -> None:
    require(weight.is_finite() and weight >= 0, "TOPOLOGY_WEIGHT", str(weight))
    require(abs(weight.as_tuple().exponent) <= 10000, "TOPOLOGY_WEIGHT_RANGE", "exponent exceeds controlled range")


def action_cost(instance: dict, selected: list[str]) -> Decimal:
    choices = set(selected)
    return exact_sum(Decimal(str(a["cost"])) for a in instance["actions"] if a["action_id"] in choices)


def adjacency_delta(repair: dict) -> int:
    return sum(record["delta"] for record in repair["adjacency"].values())


def strict_cost(instance: dict, selected: list[str]) -> Decimal:
    return action_cost(instance, selected)


def relaxed_cost(instance: dict, selected: list[str], repair: dict, topology_weight: Decimal) -> Decimal:
    validate_topology_weight(topology_weight)
    return exact_sum([action_cost(instance, selected),exact_product(topology_weight,Decimal(adjacency_delta(repair)))])
