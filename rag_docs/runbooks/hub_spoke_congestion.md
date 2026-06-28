# Runbook: Hub-Spoke Congestion

## Symptoms
- Interface utilization rising steadily
- Latency drift
- Queue saturation
- Packet loss under load
- User-visible slowdown during busy periods

## Likely causes
- Traffic growth exceeding capacity
- QoS misclassification
- Burst traffic from application flows
- Insufficient path engineering
- Hotspot on hub aggregation link

## Checks
1. Measure interface utilization trend.
2. Inspect queue drops and errors.
3. Correlate with application traffic patterns.
4. Confirm whether backup path exists.
5. Determine whether congestion is localized or systemic.

## Recommended actions
- Re-route lower priority traffic.
- Adjust QoS policy.
- Validate tunnel steering and path preference.
- Consider capacity expansion if trend persists.