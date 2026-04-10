# Week 9 – Bio-Inspired Networking (Basic)

> *"Ants don't have maps. They have memory, reinforcement, and evaporation."*

## Overview

This lab simulates **Ant Colony Optimization (ACO)**-inspired routing. Instead of fixed delivery probabilities (Week 8), each node maintains a **pheromone trail** per peer that:

- **Grows** every time a message is successfully delivered (reinforcement)
- **Shrinks** every cycle even if nothing happens (evaporation/decay)
- **Guides** forwarding decisions — the strongest trail = the best current path

The result is **emergent, adaptive routing**: paths that work get reinforced; paths that fail fade away on their own.

---

## Week 8 vs Week 9 — Key Difference

| | Week 8 (Opportunistic) | Week 9 (Bio-Inspired) |
|---|---|---|
| **Metric** | Delivery probability (0.0–1.0, clamped) | Pheromone level (0.0–∞, unbounded) |
| **Update rule** | Fixed formula: `prob + (1-prob) × 0.5` | Additive reinforcement: `+REINFORCEMENT` per success |
| **Decay** | Optional, proportional | Always on, multiplicative |
| **Path selection** | Any peer above threshold | Strongest pheromone trail first |
| **Analogy** | Probability estimate | Ant trail deposit & evaporation |

---

## Files

```
week09-bio-routing-basic/
├── config.py           ← Ports, pheromone parameters
├── pheromone_table.py  ← Trail tracking (reinforce, decay, display)
├── node.py             ← Full node: server + bio-forwarding loop + stats
├── README.md
└── docs/
    └── run_instructions.md
```

---

## Quick Start

### Terminal 1 — Node A (port 10000)
```bash
# config.py: BASE_PORT = 10000, PEER_PORTS = [10001, 10002]
python node.py
```

### Terminal 2 — Node B (port 10001)
```bash
# config.py: BASE_PORT = 10001, PEER_PORTS = [10000, 10002]
python node.py
```

### Terminal 3 — Node C (port 10002, optional)
```bash
# config.py: BASE_PORT = 10002, PEER_PORTS = [10000, 10001]
python node.py
```

---

## What to Observe

1. **Pheromone grows** on successful paths — check the bar chart each cycle
2. **Pheromone decays** every cycle — unused paths fade away
3. **Strongest path chosen first** when multiple candidates exist
4. **Queue retries** on unreachable peers until TTL expires
5. **Emergent preference**: send many messages to one peer and watch its trail dominate

---

## Configuration Reference

```python
INITIAL_PHEROMONE  = 1.0   # Starting trail level for all known peers
DECAY_FACTOR       = 0.9   # Trail × this every cycle (evaporation)
REINFORCEMENT      = 0.5   # Added to trail on each successful delivery
FORWARD_THRESHOLD  = 0.2   # Minimum pheromone to attempt forwarding
UPDATE_INTERVAL    = 5     # Seconds between cycles
MESSAGE_TTL        = 60    # Seconds before queued message expires
```

**Tuning tips:**
- Lower `DECAY_FACTOR` (e.g. 0.5) → trails evaporate fast, network adapts quickly
- Higher `REINFORCEMENT` (e.g. 1.0) → successful paths dominate faster
- Lower `FORWARD_THRESHOLD` → more aggressive forwarding, even weak trails used

---

## Extensions Implemented

| | Feature | Where |
|---|---|---|
| **A** | Reinforcement on successful delivery | `pheromone_table.reinforce()` in `node.py` |
| **B** | Message TTL with attempt counter | `node.py` → `forward_loop()` |
| **C** | Stats + pheromone bar chart per cycle | `pheromone_table.display()` + `print_stats()` |

---

## Expected Output (Node 10000)

```
──────────────────────────────────────────────────────────────
  Week 9 – Bio-Inspired (Pheromone) Routing  (port 10000)
  Peers            : [10001, 10002]
  Forward threshold: 0.2
  Decay factor     : 0.9  (evaporation per cycle)
  Reinforcement    : +0.5 per successful delivery
──────────────────────────────────────────────────────────────

[PHEROMONE TABLE]
  Port 10001: 1.000  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]
  Port 10002: 1.000  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]

[PHEROMONE] ✚ Reinforce 10001: 1.000 → 1.500
[NODE 10000] ✓ Sent to 10001: 'Hello from node 10000 → 10001'
```

---

## Connection to Week 8 & Week 10

- **From Week 8**: Replaces fixed delivery probabilities with learned pheromone trails
- **Toward Week 10**: The reinforcement loop here is conceptually analogous to quantum amplitude amplification — good paths get "measured" more often
