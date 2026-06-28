# Runbook: MPLS Tunnel Degradation

## Symptoms
- Packet loss increasing
- Jitter drifting upward
- Tunnel retransmissions rising
- Application performance degradation
- Intermittent reachability through the overlay

## Likely causes
- Underlay congestion
- Transit path impairment
- Encapsulation overhead stress
- Rekey or tunnel refresh anomaly
- Physical or logical interface degradation

## Checks
1. Review tunnel statistics.
2. Inspect jitter and packet loss trends.
3. Validate underlay latency.
4. Confirm routing stability.
5. Check for correlated syslog events.

## Recommended actions
- Shift non-critical traffic away from the affected path.
- Check tunnel and underlay interface health.
- Reapply policy only after transport stabilizes.
- Escalate if loss trend continues.