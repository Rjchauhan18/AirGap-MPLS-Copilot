# Network Role Definitions

## CE / Edge nodes
- `edge-br`: branch customer edge
- `edge-dc`: datacenter customer edge

## PE nodes
- `pe-br`: provider edge connected to branch side
- `pe-dc`: provider edge connected to datacenter side

## Core node
- `p-core`: MPLS / provider core transit node

## Host nodes
- `host-br`: traffic generator and branch workload host
- `host-dc`: traffic generator and datacenter workload host

## Control plane behavior
- OSPF is used inside the provider core and PE layer.
- BGP is used between enterprise edges and provider edges.
- Interface health, route adjacency, and path stability are the main operational signals.