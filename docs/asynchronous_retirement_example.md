# Same physical owner, different profile lifetimes

Consider two profiles with permanent roots r0 and r1 and required upper-room
component vertices x0 and x1. Two original actions use the same fixed connector
owner O and collision cell c: a activates its connection for profile0, cost2;
b activates the same connection for profile1, cost3. Physical capacity admits
both profiles; these experimental action permissions differ. Purchasing both
is compatible reuse, charged 5 in two purchases. Their action–owner unit is
U={a,b}. A later unit V offers a competing owner Q at c; Q connects the root room to a different third-floor room, so it has no later incidence at x0 or x1; it is incompatible
with either paid use of O. This is a semantic state trace, not a new timed
building experiment or a claim of verified intervention permissions.

| Event | Root-connected row before projection | Occupancy | Label | Required operation |
|---|---|---|---|---|
| introduce | p0:{r0},{x0}; p1:{r1},{x1} | empty | (0,0,[]) | Both targets exist before their incident events |
| buy a | p0:{r0,x0}; p1:{r1},{x1} | c=O | (2,1,[a]) | x0 reaches final incident event |
| project x0 | p0:{r0}; p1:{r1},{x1} | c=O | (2,1,[a]) | Preserve owner; only connectivity expires |
| buy b | p0:{r0}; p1:{r1,x1} | c=O | (5,2,[a,b]) | Same-owner reuse accepted |
| project x1 | p0:{r0}; p1:{r1} | c=O | (5,2,[a,b]) | Both demands discharged through roots |
| close U | same | c=external | (5,2,[a,b]) | Owner identity may retire; occupancy must remain for V |
| consider Q in V | same | c=external | unchanged | Reject purchase Q because its full footprint overlaps |
| close V | same | empty | (5,2,[a,b]) | Last physical event at c; now erase cell |

Skipping a makes the singleton {x0} vanish at its projection, so that row is
rejected. Replacing O by external immediately after a incorrectly rejects b.
Erasing c immediately after a incorrectly allows a later competing-owner
purchase. Neither operation is justified by x0's expiry. Keeping x0 until the
floor leaves the window retains an unnecessary partition coordinate; the trace
shows this avoidable retention but does not claim an exponential improvement
from this two-action example alone. Complete paid effects and IDs remain in the
final replay after every projection.

The common connector occupies an additional upper-floor cell d: it retains O through b and is erased at close U, since V does not touch d. Cell c is the root-floor overlap and remains through V. The competing connector's other cell stays empty in the accepting row. The figure isolates c, while all original footprints remain in the paid-action label and replay.
