# Run Instructions – Week 9: Bio-Inspired Networking

## Prerequisites

- Python 3.10+
- No external libraries required (stdlib only)
- 2–3 terminal windows

---

## Scenario 1: Basic Pheromone Reinforcement

**Goal**: Watch pheromone grow on a successful path.

1. **Terminal 1** — `BASE_PORT = 10000`, `PEER_PORTS = [10001]`
   ```bash
   python node.py
   ```
2. **Terminal 2** — `BASE_PORT = 10001`, `PEER_PORTS = [10000]`
   ```bash
   python node.py
   ```
3. **Observe**: After each successful delivery, the pheromone bar for that peer grows.
   After each cycle with no delivery, it shrinks slightly.

---

## Scenario 2: Pheromone Decay (Dead Path)

**Goal**: See a path's trail evaporate when no deliveries happen.

1. Start both nodes (Scenario 1).
2. Stop **Node 10001** (Ctrl+C).
3. Watch Node 10000's pheromone table — the trail to 10001 will decay each cycle.
4. Eventually it may drop below `FORWARD_THRESHOLD` and stop being attempted.

---

## Scenario 3: Path Competition (Three Nodes)

**Goal**: Observe two competing paths and see the better one win.

| Terminal | BASE_PORT | PEER_PORTS       |
|----------|-----------|------------------|
| 1        | 10000     | [10001, 10002]   |
| 2        | 10001     | [10000, 10002]   |
| 3        | 10002     | [10000, 10001]   |

1. Start all three nodes.
2. Stop **Node 10002** after 20 seconds.
3. Watch Node 10000 progressively prefer 10001 as 10002's trail decays.

---

## Scenario 4: Tuning — Fast Adaptation

**Goal**: See the network adapt quickly to a topology change.

In `config.py`:
```python
DECAY_FACTOR    = 0.5    # Aggressive evaporation
REINFORCEMENT   = 1.0    # Strong reinforcement
UPDATE_INTERVAL = 3      # Faster cycles
```

Repeat Scenario 3. The network should adapt to the removed peer much faster.

---

## Scenario 5: TTL Expiry

**Goal**: See a message expire when no path is ever available.

1. Set `MESSAGE_TTL = 20` in `config.py`.
2. Start Node 10000 **only** (peers offline).
3. After 20 seconds, observe:
   ```
   [NODE 10000] ⏰ Expired (age=20s, attempts=4): 'Hello from node 10000 → 10001'
   ```

---

## Key Questions to Answer (Lab Report)

1. What happens to pheromone when a peer goes offline for 3 cycles?
2. With `DECAY_FACTOR = 0.9` and `REINFORCEMENT = 0.5`, how many successful
   deliveries does it take for pheromone to exceed 2.0? (Starting from 1.0)
3. Why is the strongest-trail-first ordering important for the forwarding loop?
4. How does this differ from Week 8's fixed delivery probability approach?

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | Wait 30s or change `BASE_PORT` |
| Pheromone immediately below threshold | Lower `FORWARD_THRESHOLD` to 0.1 |
| Messages never expire | Check `MESSAGE_TTL` value in config |
| Bars not updating | Trail values are equal; one successful delivery will differentiate them |
