# Revised evaluation protocol

Frozen before performance inspection: historical 37 recipes, one integrated
worked example, catalogue 8/32/128; ownership 2/4/8; profiles 1/2/3/4;
connectivity floors 3/4/5/6/7 with seeds 0/1/2; consecutive bundled support
2/3/5/8; irrelevant rooms 0/4/12. Other family seeds are zero because their
geometry is deterministic. Connectivity randomizes integer prices 1..5 with a
local seeded generator. This changes connectivity width and support together;
measured parameters must be reported, not a claim of independent isolation.

Five fresh workers per method/input; three for >=100 actions or >=7-floor
connectivity. Oracle once for <=8 actions excluding unsupported/forced-cap
controls. All methods use a 60-second parent wall limit; CP-SAT has a 55-second
internal budget. DP caps: 100000 states, 65536 columns, except the explicitly
forced state-limit case uses one state. No enforced RAM cap; whole-process peak
RSS includes imports. Function wall time excludes imports/startup and includes
uncached recognition and solver replay; process end-to-end is separately saved.
Cached-recognition runs exclude cache creation and are separately labelled;
cache correctness requires a recognizer-produced immutable object matching the
input fingerprint and pruning setting. This is an experimental Python API, not
an authenticated external cache file format.

Direct timing splits recognition, event schedule, optimization, label
reconstruction and materialization replay. Recognition additionally splits input
validation, geometry compilation, footprint preparation, cells and units/
components. These labels describe actual code regions: geometry compilation
includes contract checks and conflict compilation; it is not pure GEOS CPU time.
Operation counts cover cell-owner coverage and action-pair equivalence tests,
not every intersection inside the shared geometry compiler. Representative
reduction wall time is measured within optimization and must not be added twice.

Same input hashes, exact cost/count/IDs, independent small oracle certificates,
and full replay are checked. Missing fields stay null. Positive incumbent gap
is max(0,c-bound)/abs(c); zero cost with zero bound has gap zero; other zero-cost
or unavailable bounds have null gap. CP-SAT cost bounds remain cost bounds when
later cardinality/ID stages time out; they do not prove tie optimality. Bounds
from interrupted first stages are conservative integer-floor/scaled rationals.

Valid ablations: compression on/off; safe marked-component pruning; cached
recognition (excluded from primary comparison). Dominance disabling and alternate
unit ordering are deferred: neither is needed to claim a measured benefit and
would change a delicate correctness path. Semantic controls remain explicitly
invalid models, never valid algorithm ablations.

Multi-room source protocol retains a deterministic maximal nonoverlapping
eligible subset on consecutive source storeys, larger projected area then IDs.
It is not claimed maximum-cardinality. All exact source rings/IDs stay frozen;
all stair/transport conservative envelopes remain obstacles on both floors.
All horizontal doors are hypothetical experimental annotations constructed only
on exact shared-boundary segments and replayed; they are not extracted IFC door
facts. Choose the first pair of grid-admissible vertical candidates whose lower
endpoints share a hypothetical horizontal component and whose distinct upper
endpoints share another. Both-profile and profile-0-only upper horizontal
permissions produce paired inputs. Source screening/admission exclusions remain
visible. These experiments test finite-model horizontal coupling, not actual
building restoration. No price, permission, reservation or door is asserted as
an IFC fact. Multi-room admission on three or more source storeys is not asserted.
