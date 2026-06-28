# Runbook: BGP Route Flap

## Symptoms
- BGP neighbor resets
- Route churn
- Alternate path oscillation
- Increased convergence time
- Traffic instability across branches

## Likely causes
- Interface instability
- Incorrect neighbor configuration
- Reachability loss on transport path
- Policy mismatch
- MPLS underlay disruption

## Checks
1. Verify BGP neighbor state.
2. Inspect interface errors and flaps.
3. Check route advertisements and withdrawals.
4. Confirm underlay path reachability.
5. Review recent configuration changes.

## Recommended actions
- Stabilize underlay connectivity.
- Validate BGP neighbor IPs and AS numbers.
- Reduce route churn by fixing the root transport issue.
- Recheck advertised prefixes after convergence.