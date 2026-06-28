# IP Plan

## Underlay links
- `edge-dc` eth1: `10.2.1.1/30`
- `pe-dc` eth2: `10.2.1.2/30`
- `pe-dc` eth1: `10.1.1.1/30`
- `p-core` eth1: `10.1.1.2/30`
- `p-core` eth2: `10.1.2.2/30`
- `pe-br` eth1: `10.1.2.1/30`
- `edge-br` eth1: `10.2.2.1/30`
- `pe-br` eth2: `10.2.2.2/30`

## Host networks
- Branch LAN: `192.168.2.0/24`
- Datacenter LAN: `192.168.1.0/24`

## Hosts
- `host-br`: `192.168.2.10/24`
- `host-dc`: `192.168.1.10/24`

## Loopbacks
- `p-core`: `1.1.1.1/32`
- `pe-dc`: `2.2.2.2/32`
- `pe-br`: `3.3.3.3/32`
- `edge-dc`: `4.4.4.4/32`
- `edge-br`: `5.5.5.5/32`