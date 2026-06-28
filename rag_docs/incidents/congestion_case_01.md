# Incident: Progressive Hub Link Congestion

## Incident ID
INC-CONG-001

## Observed issue
A hub-spoke link showed steadily increasing utilization before user-visible slowdown occurred.

## Signals
- Utilization rose from moderate to high over time.
- Latency drift increased gradually.
- Jitter increased during peak traffic periods.
- No hard failure was present initially.

## Root cause hypothesis
Traffic growth exceeded available bandwidth on the hub-facing path.

## Impacted scope
Branch to datacenter application traffic and delay-sensitive flows.

## Resolution
Non-critical traffic was moved away from the congested path and QoS policy was reviewed.

## Preventive action
Set early warning thresholds based on utilization trend and latency drift rather than waiting for breach.