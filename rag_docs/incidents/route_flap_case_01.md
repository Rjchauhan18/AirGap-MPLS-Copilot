# Incident: BGP Route Flap

## Incident ID
INC-BGP-001

## Observed issue
BGP adjacency instability caused route churn and intermittent path changes.

## Signals
- Neighbor transitions were repeated.
- Route advertisements changed frequently.
- Convergence time increased.
- Reachability remained unstable during the event.

## Root cause hypothesis
Underlay transport instability caused repeated BGP session resets.

## Impacted scope
Branch and datacenter service reachability.

## Resolution
The underlying transport issue was corrected and BGP stabilized afterward.

## Preventive action
Monitor adjacency changes as an early precursor rather than waiting for traffic failure.