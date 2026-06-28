# Incident: MPLS Tunnel Degradation

## Incident ID
INC-TUN-001

## Observed issue
An overlay tunnel degraded slowly before packet loss became visible to users.

## Signals
- Packet loss increased incrementally.
- Jitter trends worsened.
- Tunnel health score declined.
- Rekey anomaly was suspected.

## Root cause hypothesis
Underlay impairment and tunnel instability reduced overlay quality.

## Impacted scope
Mission-critical application flows crossing the affected tunnel.

## Resolution
Traffic was rerouted and the underlay was inspected for impairment.

## Preventive action
Use trend-based tunnel scoring and trigger early reroute before service impact.