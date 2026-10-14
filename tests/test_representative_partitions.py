from decimal import Decimal
from itertools import product
import random

import pytest

from cfar.errors import ValidationError
from cfar.representative_partitions import cut_row, product_cut_row, representative_indices


def partitions(n):
    if n == 1:
        return [(0,)]
    return [prefix+(block,) for prefix in partitions(n-1) for block in range(max(prefix)+2)]


def connected_join(first, second):
    # Independent union-find completion oracle, no cut rows or elimination.
    parent = list(range(len(first)))

    def find(i):
        while parent[i] != i:
            i = parent[i]
        return i

    for partition in (first, second):
        for i in range(len(partition)):
            for j in range(i):
                if partition[i] == partition[j]:
                    parent[find(i)] = find(j)
    return len({find(i) for i in range(len(first))}) == 1


@pytest.mark.parametrize("n", range(1,6))
def test_cut_factorization_for_every_partition_pair(n):
    for first, second in product(partitions(n), repeat=2):
        assert ((cut_row(first) & cut_row(second)).bit_count() % 2 == 1) == connected_join(first, second)


@pytest.mark.parametrize("dimensions", [(4,), (3,3), (2,2,2), (1,3)])
@pytest.mark.parametrize("seed", range(5))
def test_basis_preserves_exact_best_label_for_every_completion(dimensions, seed):
    histories = list(product(*(partitions(n) for n in dimensions)))
    rng = random.Random(seed)
    # Tied costs deliberately exercise count and ID ordering.
    labels = []
    for i in range(len(histories)):
        count = rng.randrange(1,4)
        labels.append((Decimal(rng.randrange(3)), count,
                       tuple(f"A{i:03d}-{j}" for j in range(count))))
    kept = representative_indices(histories, labels)
    _, columns = product_cut_row(histories[0])
    assert len(kept) <= columns
    for completion in histories:
        feasible = lambda history: all(connected_join(a,b) for a,b in zip(history,completion))
        original = min((labels[i] for i,h in enumerate(histories) if feasible(h)), default=None)
        reduced = min((labels[i] for i in kept if feasible(histories[i])), default=None)
        assert original == reduced


def test_mismatched_boundaries_cannot_be_compressed_together():
    with pytest.raises(ValidationError, match="REPRESENTATIVE_BOUNDARY"):
        representative_indices([((0,),), ((0,1),)], [(0,), (1,)])


def test_duplicate_rows_keep_cheapest_original_witness():
    assert representative_indices([((0,1),), ((7,8),)], [(2,1,("A",)), (1,1,("B",))]) == [1]
