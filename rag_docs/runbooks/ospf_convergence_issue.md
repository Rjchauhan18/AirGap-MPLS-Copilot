# Runbook: OSPF Convergence Issue

## Symptoms
- Slow route convergence
- Intermittent adjacency changes
- Inconsistent reachability
- Latency spikes during reconvergence

## Likely causes
- Interface loss
- MTU mismatch
- Misconfigured hello/dead timers
- CPU pressure on routing devices
- Core path instability

## Checks
1. Check neighbor adjacency state.
2. Review OSPF database consistency.
3. Inspect interface and link health.
4. Review routing logs for repeated transitions.
5. Verify that all transit links are stable.

## Recommended actions
- Restore stable link state.
- Validate OSPF timers and area settings.
- Confirm loopback reachability.
- Rebuild adjacency if needed.