"""Maximum-cardinality nonoverlapping subset of already eligible source rooms.

This is extraction bookkeeping, not a new repair optimizer or IFC validation.
Exact independent-set search is separated over source overlap components.
"""
from functools import lru_cache
from itertools import combinations
from shapely.geometry import Polygon


def maximum_nonoverlap(eligible):
    by={r['global_id']:r for r in eligible}
    graph={rid:set() for rid in by}
    shapes={rid:Polygon(row['polygon']) for rid,row in by.items()}
    for a,b in combinations(sorted(by),2):
        if shapes[a].intersection(shapes[b]).area>1e-8:
            graph[a].add(b);graph[b].add(a)
    remaining=set(by);retained=set();component_sizes=[];search_states=0
    while remaining:
        first=min(remaining);component={first};stack=[first]
        while stack:
            node=stack.pop()
            for other in graph[node]-component:
                component.add(other);stack.append(other)
        remaining-=component;component_sizes.append(len(component))
        @lru_cache(None)
        def best(nodes):
            if not nodes:return ()
            available=set(nodes)
            node=min(nodes,key=lambda v:(-len(graph[v]&available),v))
            take=tuple(sorted((node,)+best(tuple(sorted(available-{node}-graph[node])))))
            skip=best(tuple(sorted(available-{node})))
            return min([take,skip],key=lambda ids:(-len(ids),ids))
        retained.update(best(tuple(sorted(component))))
        search_states+=best.cache_info().currsize
    exclusions=[dict(room=rid,reason='excluded by exact maximum-cardinality source-overlap subset; lexicographic ID tie-break') for rid in sorted(by) if rid not in retained]
    return [by[rid] for rid in sorted(retained)],exclusions,dict(eligible=len(by),retained=len(retained),
        largest_overlap_component=max(component_sizes,default=0),memoized_search_states=search_states)
