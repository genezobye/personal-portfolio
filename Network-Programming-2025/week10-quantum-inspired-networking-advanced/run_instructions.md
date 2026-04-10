# Run Instructions – Week 10: Quantum-Inspired Networking

## Prerequisites

- Python 3.10+
- No external libraries required (stdlib only)
- 2–3 terminal windows

---

## Scenario 1: Basic Token Collapse

**Goal**: Observe a token being transmitted and collapsed exactly once.

1. **Terminal 1** — `BASE_PORT = 11000`, `PEER_PORTS = [11001]`
   ```bash
   python node.py
   ```
2. **Terminal 2** — `BASE_PORT = 11001`, `PEER_PORTS = [11000]`
   ```bash
   python node.py
   ```
3. **Observe on Node 11001**:
   - `RECEIVED` log event
   - `⚡ State collapsed: SUPERPOSITION → COLLAPSED`
   - The message is printed once and never again

---

## Scenario 2: No-Cloning Verification

**Goal**: Confirm a token cannot exist on two nodes simultaneously.

1. Start all three nodes (11000, 11001, 11002).
2. Watch Node 11000's logs — after transmission to 11001, the token is **removed** from its queue.
3. Node 11002 should **never** receive the same token that was sent to 11001.
4. Look for `DUPLICATE` events if a token somehow arrives twice.

---

## Scenario 3: Token Expiry

**Goal**: See a queued token expire before delivery.

1. Set `TOKEN_EXPIRY = 15` in `config.py`.
2. Start **Node 11000 only** (peers offline).
3. After 15 seconds, observe:
   ```
   [LOG xx:xx:xx] EXPIRED      | token=xxxx state=EXPIRED  TTL exceeded — discarding
   ```
4. Now start **Node 11001** — no tokens arrive because they expired.

---

## Scenario 4: Multi-Hop Path Tracking (Extension B)

**Goal**: Watch a token accumulate a hop path before being consumed.

1. Set `MAX_HOPS = 2` in `config.py`.
2. Start three nodes in sequence: 11002 → 11001 → 11000.
3. A token originating at 11000, forwarded via 11001, will be **consumed at 11002**
   when it reaches the hop limit.
4. Check the path log:
   ```
   Path: 11000 → 11001 → 11002
   ```

---

## Scenario 5: Full Event Log Replay

**Goal**: Review complete token lifecycle on exit.

1. Run any scenario.
2. Press **Ctrl+C** to stop Node 11000.
3. The last 20 events are printed with timestamps — trace each token's journey.

---

## Key Questions to Answer (Lab Report)

1. What happens if you send the same token object to two peers simultaneously?
   (Hint: look at `seen_token_ids` and the no-cloning removal logic)
2. How does `TOKEN_EXPIRY` relate to the quantum concept of decoherence?
3. In what way does the hop path (Extension B) differ from the pheromone path in Week 9?
4. What real-world secure messaging system most closely resembles this token model?

---

## Comparison Table: Weeks 8–10

| Feature | Week 8 (Opportunistic) | Week 9 (Bio-Inspired) | Week 10 (Quantum) |
|---|---|---|---|
| Message persistence | Until delivered or TTL | Until delivered or TTL | Consumed on delivery |
| Path selection | Probability threshold | Pheromone strength | Any reachable peer |
| Retry on failure | Yes, from queue | Yes, from queue | Yes, but token ages |
| Path memory | No | Yes (pheromone) | Yes (hop_path, read-only) |
| Duplicate delivery | Possible if not careful | Possible if not careful | Prevented by seen_ids |
| Message after delivery | Still exists in queue | Still exists in queue | **Destroyed** |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | Wait 30s or change `BASE_PORT` |
| Token never arrives | Check peer is running before `UPDATE_INTERVAL` elapses |
| `Could not deserialise token` | Ensure both nodes use the same `token.py` version |
| Tokens expire too fast | Increase `TOKEN_EXPIRY` in config |
