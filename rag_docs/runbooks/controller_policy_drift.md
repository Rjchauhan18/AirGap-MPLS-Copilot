# Runbook: Controller Policy Drift

## Symptoms
- Policies do not match expected intent
- Inconsistent routing or tunnel steering
- Unexpected path selection
- Change after controller update
- Configuration mismatch across sites

## Likely causes
- Controller misconfiguration
- Stale policy push
- Bad automation input
- Conflicting rules
- Manual override inconsistency

## Checks
1. Compare live policy with intended policy.
2. Validate recent controller changes.
3. Inspect affected site and service scope.
4. Review configuration version history.
5. Check for correlated route or tunnel anomalies.

## Recommended actions
- Roll back the offending policy.
- Re-sync policy state.
- Freeze automation until the configuration is validated.
- Confirm affected sites have returned to normal behavior.