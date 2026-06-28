# SD-WAN over MPLS Topology Overview

This lab simulates an enterprise SD-WAN deployment over an MPLS underlay.

## Sites
- Branch site: `branch` with edge router `edge-br`
- Datacenter site: `datacenter` with edge router `edge-dc`
- Provider edge: `pe-br`, `pe-dc`
- Provider core: `p-core`

## Traffic path
- Branch host traffic enters `host-br`
- `host-br` connects to `edge-br`
- `edge-br` connects to `pe-br`
- `pe-br` connects to `p-core`
- `p-core` connects to `pe-dc`
- `pe-dc` connects to `edge-dc`
- `edge-dc` connects to `host-dc`

## Purpose
The topology is used to simulate:
- MPLS underlay forwarding
- Dynamic routing with OSPF
- BGP edge connectivity
- Tunnel degradation
- Congestion buildup
- Policy drift scenarios

## Operational notes
- Branch and datacenter traffic should remain reachable under normal conditions.
- Route convergence time and tunnel health are key metrics.
- Fault injection may affect latency, jitter, packet loss, and adjacency stability.