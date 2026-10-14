"""Weighted product cut-row bases using established rank-based machinery.

Caller must group by event, occupancy and selected boundary sets first.
This is not a complete solver or an originality claim.
"""
from .errors import require


def cut_row(partition: tuple[int, ...]) -> int:
    """Bit vector for cuts compatible with a partition; vertex zero is anchored."""
    require(bool(partition) and all(type(x) is int and x >= 0 for x in partition),
            "REPRESENTATIVE_PARTITION", "nonempty nonnegative block labels required")
    row = 0
    for cut in range(1 << (len(partition)-1)):
        sides = {}
        compatible = True
        for vertex, block in enumerate(partition):
            side = 0 if vertex == 0 else (cut >> (vertex-1)) & 1
            if block in sides and sides[block] != side:
                compatible = False
                break
            sides[block] = side
        if compatible:
            row |= 1 << cut
    return row


def product_cut_row(partitions: tuple[tuple[int, ...], ...]) -> tuple[int, int]:
    require(bool(partitions), "REPRESENTATIVE_PARTITION", "at least one profile required")
    row, columns = 1, 1
    for partition in partitions:
        factor = cut_row(partition)
        combined = 0
        for column in range(1 << (len(partition)-1)):
            if (factor >> column) & 1:
                combined |= row << (column*columns)
        row, columns = combined, columns*(1 << (len(partition)-1))
    return row, columns


def representative_indices(partitions: list[tuple[tuple[int, ...], ...]], labels: list[tuple]) -> list[int]:
    """Keep original indices of a minimum-label GF(2) product-row basis.

    Vertex positions must denote the same selected vertices in every history,
    separately in each profile; position zero denotes the permanent anchor.
    Labels must have a continuation-stable total order, e.g. cost/count/IDs.
    """
    require(len(partitions) == len(labels), "REPRESENTATIVE_LABELS", "one label per history")
    if not partitions:
        return []
    dimensions = tuple(len(p) for p in partitions[0])
    require(all(tuple(len(p) for p in history) == dimensions for history in partitions),
            "REPRESENTATIVE_BOUNDARY", "fixed selected boundary sets required")
    basis, kept = {}, []
    for index in sorted(range(len(labels)), key=lambda i: (labels[i], i)):
        row, _ = product_cut_row(partitions[index])
        while row:
            pivot = row.bit_length()-1
            if pivot not in basis:
                basis[pivot] = row
                kept.append(index)
                break
            row ^= basis[pivot]
    return kept
