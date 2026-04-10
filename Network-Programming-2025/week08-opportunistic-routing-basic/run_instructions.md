# Run Instructions – Week 8: Opportunistic Routing

## Prerequisites

- Python 3.10+
- No external libraries required (stdlib only)
- 2–3 terminal windows

---

## Scenario 1: Basic Two-Node Test

**Goal**: Verify that a message reaches its peer when it is online.

1. Open **Terminal 1**:
   ```bash
   # Ensure config.py has BASE_PORT = 9000, PEER_PORTS = [9001]
   python node.py
   ```

2. Open **Terminal 2**:
   ```bash
   # Ensure config.py has BASE_PORT = 9001, PEER_PORTS = [9000]
   python node.py
   ```

3. **Observe**: Node 9000 sends "Hello from node 9000 → 9001" and it is received immediately.

---

## Scenario 2: Opportunistic Queue Test

**Goal**: See messages queue and deliver when peer comes online.

1. Start **Node 9000 only** (Node 9001 is offline)
2. Observe that the message to 9001 gets queued
3. After 5–10 seconds, start **Node 9001**
4. Observe: the next `forward_loop` cycle delivers the queued message

---

## Scenario 3: Three Nodes

**Goal**: Simulate a small mobile network.

| Terminal | BASE_PORT | PEER_PORTS    |
|----------|-----------|---------------|
| 1        | 9000      | [9001, 9002]  |
| 2        | 9001      | [9000, 9002]  |
| 3        | 9002      | [9000, 9001]  |

Start nodes in order. Stop one node mid-run to see TTL expiry behavior.

---

## Scenario 4: TTL Expiry

**Goal**: See messages expire when a peer is never reachable.

1. Set `MESSAGE_TTL = 15` in `config.py`
2. Start Node 9000 but **do NOT** start Node 9001
3. After 15 seconds, observe the expiry log:
   ```
   [NODE 9000] ⏰ Message expired (age=15s): 'Hello from node 9000 → 9001'
   ```

---

## Adjusting Thresholds

To force opportunistic behavior:
- Lower `FORWARD_THRESHOLD` (e.g. 0.3) → more aggressive forwarding
- Raise `FORWARD_THRESHOLD` (e.g. 0.8) → only forward to very reliable peers
- Lower `DECAY_FACTOR` (e.g. 0.5) → probabilities drop faster, simulating high mobility

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | Wait 30s or change `BASE_PORT` |
| Messages never delivered | Check `FORWARD_THRESHOLD` vs initial probability (0.6) |
| No output after start | Node is waiting for `UPDATE_INTERVAL`; wait 5 seconds |
