# Permission-backed CAD pilot, 21 October 2026

The user authorized thesis use of WD Revised24-02-2024.dwg and delegated
selection of the most useful group. This is not an assertion of an open
redistribution licence or approval of physical intervention candidates.

Source SHA256:
0399309c5d19218bad44329471745354098b28431548ccf9a1bff5bd8a779acc.
GNU LibreDWG0.14 decoded the local DWG to JSON with SUCCESS. The local binary
release is from https://github.com/LibreDWG/libredwg/releases/tag/0.14.
The original DWG and decoded/private extracts remain ignored and are not
included in source commits or release archives.

## Selection and geometry

Select the working drawing group in model coordinates x(-125,-86),y(47,165).
Its lower/upper-ground plans are separately drawn. Exclude the neighbouring
presentation copies, unrelated residential plans, and repeated typical-floor
labels. Source handles can repeat through INSERTs: use transformed position
and insertion path, not a handle alone, to identify an occurrence.

Start with one conservative aligned bedroom pair. Labels11250431 (lower
guest bedroom) and11249846 (upper master bedroom) both state5.700x4.800.
The selected inner wall/window endpoints reproduce5.7x4.8 exactly to1e-6.
This supports a local metre scale despite contradictory global unit metadata.
Do not apply this local scale to every drawing in the DWG.

The adapter uses exact source x/y endpoints and one rigid translation aligning
corresponding upper-window wall endpoints11222668/11222983. It reconstructs
rectangular room rings, closing door/window apertures as a declared manual
annotation. These are not automatically extracted original room polygons;
the CAD supplies no original semantic room IDs. Derived IDs retain label
handles; raw and registered rings/insertion paths are audited.

Preserve source column envelopes in the selected group. Carry a conservative
lift/stair background exclusion envelope; the drawn lift is not reintroduced
as a new purchasable intervention. Other rooms and external circulation are
outside this two-room pilot. Furniture is not a structural obstacle in this
controlled abstraction. No whole-building or construction-clearance result
follows from this subset.

## Experimental catalogue and fixed evaluation

The source does not verify intervention reservations, accessibility profiles,
permissions, present-day prices or an unambiguous signed storey rise for this
pair. Declare experimental elevations0/3.6m, two disjoint1.2m-square candidate
slots, two profiles (0.8/1.0m minimum widths/clearances), connector width1.0m,
and abstract atomic prices. These assumptions do not certify a lift design.

Four predetermined variants exercise bundled, separate, unavailable-profile
and single-purchase cases. They are variants of ONE source room pair, not
four buildings or independent physical layouts. The catalogue reuses the
previous controlled pilot semantics; it is an input-workflow validation,
not a new scaling or performance claim.

At a clean revision run compressed/uncompressed DP once and the exhaustive
oracle once per variant. Replay every returned selection and independently
re-enumerate each oracle certificate; check exact cost/count/ID labels,
unchanged room polygons/IDs/adjacency, and paid rectangles/owner constraints.
Use fresh output directories, deterministic seed0, source/adapter/decoder/input
fingerprints and environment/status manifests. Keep this12-observation pilot
separate from the frozen2274 observations. No timing speedup claim is planned.

Classification: permission-backed CAD-derived controlled experiment. Actual
building repair validation and literature priority remain unestablished.
