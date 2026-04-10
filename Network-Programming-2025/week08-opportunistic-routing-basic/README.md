# Week 8 – Opportunistic Routing (Basic)

> *"Don't wait for a perfect path. Deliver when the moment is right."*

## Overview

This lab simulates mobile network nodes that forward messages **probabilistically** — not by fixed routes, but by asking: *"Is this the best messenger I've encountered so far?"*

Each node maintains a **Delivery Probability Table**: a score (0.0–1.0) for every peer representing how reliably it can reach that peer. Messages are only forwarded when a good-enough encounter occurs.

---

## Core Concepts

| Concept | Description |
|---|---|
| Delivery Probability | Per-peer score updated on encounter, decayed over time |
| Opportunistic Forwarding | Send only when `prob >= FORWARD_THRESHOLD` |
| Message Queue | Hold messages until a suitable carrier is found |
| TTL Expiry | Drop messages that are too old to be useful |
| Encounter-based Update | Success → probability increases; time → probability decays |

---

## Files

```
week08-opportunistic-routing-basic/
├── config.py           ← Ports, thresholds, intervals
├── delivery_table.py   ← Probability tracking (with decay & encounter update)
├── node.py             ← Full node: server + forwarding loop + stats
└── docs/
    └── run_instructions.md
```

---

## Quick Start

### Terminal 1 — Node A (port 9000)
```bash
# config.py: BASE_PORT = 9000, PEER_PORTS = [9001, 9002]
python node.py
```

### Terminal 2 — Node B (port 9001)
```bash
# config.py: BASE_PORT = 9001, PEER_PORTS = [9000, 9002]
python node.py
```

### Terminal 3 — Node C (port 9002, optional)
```bash
# config.py: BASE_PORT = 9002, PEER_PORTS = [9000, 9001]
python node.py
```

> **Tip**: Start Node B/C *after* Node A to see messages queue and then deliver opportunistically.

---

## What to Observe

1. **Immediate delivery** – if peer is online and `prob >= 0.5`, message is sent right away
2. **Queuing** – if peer is offline, message waits in queue
3. **Opportunistic retry** – every `UPDATE_INTERVAL` seconds, the forwarding loop retries
4. **Probability decay** – probabilities drop over time if encounters don't happen
5. **TTL expiry** – messages older than `MESSAGE_TTL` seconds are dropped

---

## Configuration Reference

```python
FORWARD_THRESHOLD = 0.5   # Minimum probability to forward
UPDATE_INTERVAL   = 5     # Seconds between forwarding attempts
DECAY_FACTOR      = 0.9   # Probability × this value each cycle
MESSAGE_TTL       = 30    # Seconds before a queued message expires
```

---

## Extensions Implemented

| Extension | Feature | Where |
|---|---|---|
| A | Dynamic probability (encounter increase + decay) | `delivery_table.py` |
| B | Message TTL (auto-expire stale messages) | `node.py` → `forward_loop()` |
| C | Delivery statistics (sent/failed/expired/received) | `node.py` → `stats` dict |

---

## Expected Output (Node 9000)

```
────────────────────────────────────────────────────────────
  Week 8 – Opportunistic Routing Node  (port 9000)
  Peers: [9001, 9002]
  Forward threshold: 0.5
────────────────────────────────────────────────────────────

[DELIVERY TABLE] Current probabilities:
  Port 9001: 0.60  |████████████        |
  Port 9002: 0.60  |████████████        |

[NODE 9000] ✓ Sent to 9001: 'Hello from node 9000 → 9001'
[NODE 9000] Peer 9002 unreachable – queuing: 'Hello from node 9000 → 9002'

[NODE 9000] Running. Press Ctrl+C to stop.
```

---

## Connection to Week 9

The probability update rule used here (`prob + (1 - prob) × 0.5`) is a fixed formula. In **Week 9 – Bio-Inspired Networking**, this becomes a *learned* value updated via reinforcement — analogous to ant pheromone trails.
