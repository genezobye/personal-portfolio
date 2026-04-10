# Week 10 – Quantum-Inspired Networking (Basic)

> *"You cannot copy a quantum state. You cannot unread a message. The act of observing changes everything."*

## Overview

This lab simulates three core principles from quantum information theory — **without any quantum hardware**. The goal is to build *intuition* for how quantum constraints change the way we think about network communication.

| Quantum Principle | Network Simulation |
|---|---|
| **No-cloning theorem** | A token forwarded to one peer is removed from the sender — it cannot exist in two places |
| **Wave-function collapse** | Reading a token is irreversible; the message is consumed and unavailable forever |
| **Decoherence / TTL** | Tokens that are not read before expiry collapse to an invalid state |
| **Superposition** | Until read, a token exists in an "unread" state — observable but not yet collapsed |

---

## Week 8 → 9 → 10 Progression

| Week | Routing Model | Key Mechanism |
|---|---|---|
| 8 | Opportunistic | Delivery *probability* per peer |
| 9 | Bio-Inspired | *Pheromone trail* reinforced on success |
| **10** | **Quantum-Inspired** | **One-time tokens — consumed on delivery** |

The journey: from "how likely is delivery?" → "how can the path *learn*?" → "what if the message *ceases to exist* after delivery?"

---

## Files

```
week10-quantum-network-basic/
├── config.py       ← Ports, TOKEN_EXPIRY, MAX_HOPS
├── token.py        ← Token class: state machine, serialisation, hop path
├── node.py         ← Server + forwarding loop + event log + stats
├── README.md
└── docs/
    └── run_instructions.md
```

---

## Quick Start

### Terminal 1 — Node A (port 11000)
```bash
# config.py: BASE_PORT = 11000, PEER_PORTS = [11001, 11002]
python node.py
```

### Terminal 2 — Node B (port 11001)
```bash
# config.py: BASE_PORT = 11001, PEER_PORTS = [11000, 11002]
python node.py
```

### Terminal 3 — Node C (port 11002, optional)
```bash
# config.py: BASE_PORT = 11002, PEER_PORTS = [11000, 11001]
python node.py
```

---

## Token Lifecycle

```
  Created (SUPERPOSITION)
       │
       ├─── read_token() called ──────────────→ COLLAPSED (irreversible)
       │
       ├─── TTL exceeded ────────────────────→ EXPIRED
       │
       └─── transmitted to peer ─────────────→ removed from this node
                                                (no-cloning)
```

---

## Extensions Implemented

| | Feature | Where |
|---|---|---|
| **A** | Configurable TTL (`TOKEN_EXPIRY`) + cleanup | `token.py`, `node.py` |
| **B** | Multi-hop path tracking + hop limit (`MAX_HOPS`) | `token.hop_path`, `token.try_forward()` |
| **C** | Full event log with timestamps + stats summary | `node.py` → `log_event()`, `print_stats()` |

---

## Configuration Reference

```python
TOKEN_EXPIRY     = 30   # Seconds before unread token becomes EXPIRED
UPDATE_INTERVAL  = 5    # Seconds between forwarding loop cycles
MAX_HOPS         = 3    # Token consumed after this many hops (Extension B)
```

---

## Expected Output (Node 11000)

```
──────────────────────────────────────────────────────────────
  Week 10 – Quantum-Inspired Networking  (port 11000)
  Peers       : [11001, 11002]
  Token expiry: 30s

[LOG 10:01:05] CREATED       | token=a1b2c3d4e5f6 state=SUPERPOSITION   age=0.0s
[LOG 10:01:05] TRANSMITTED   | token=a1b2c3d4e5f6 state=SUPERPOSITION   → port 11001

--- On Node 11001 ---
[LOG 10:01:05] RECEIVED      | token=a1b2c3d4e5f6 from 127.0.0.1:xxxxx
[TOKEN a1b2c3d4e5f6] ⚡ State collapsed: SUPERPOSITION → COLLAPSED (lived 0.1s)

[NODE 11001] ⚡ Token collapsed: 'Quantum token from node 11000 → 11001'
              Path: 11000 → 11001
```

---

## Real-World Connections

- **QKD (Quantum Key Distribution)**: Keys are generated and consumed once; interception is detectable because measurement collapses the state
- **Signal / ephemeral messaging**: Messages deleted after reading — software approximation of collapse
- **One-time pads**: Each key bit used once and destroyed
- **Zero-knowledge proofs**: Proving knowledge without revealing it — related minimalism in information exposure
