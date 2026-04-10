# node.py – Week 10: Quantum-Inspired Networking
# ─────────────────────────────────────────────────────────────────────────────
# Simulates a network node operating under quantum-inspired constraints:
#
#   1. Listens for incoming token transmissions on BASE_PORT
#   2. On receipt — collapses the token (reads it once), logs state
#   3. Generates new tokens and forwards them to peers
#   4. Enforces no-cloning: a read token is never forwarded
#   5. Enforces expiry:     tokens older than TOKEN_EXPIRY are discarded
#   6. Tracks hop history:  tokens carry their path (Extension B)
#   7. Logs all transitions: Extension C analytics
#
# Key insight vs Week 9:
#   Week 9 – routing adapts *toward* reliable paths (pheromone reinforcement)
#   Week 10 – messages are *destroyed on delivery* (collapse); no path memory

import socket
import threading
import time

from config import (
    BASE_PORT,
    BUFFER_SIZE,
    HOST,
    PEER_PORTS,
    TOKEN_EXPIRY,
    UPDATE_INTERVAL,
)
from token import Token, TokenState

# ── Shared state ──────────────────────────────────────────────────────────────

# Tokens waiting to be forwarded (in SUPERPOSITION state)
token_queue: list[Token] = []
queue_lock = threading.Lock()

# Extension B: seen token IDs — prevent re-delivery of the same token
seen_token_ids: set[str] = set()

# Extension C: event log
event_log: list[dict] = []


# ── Logging helper ────────────────────────────────────────────────────────────


def log_event(event: str, token: Token, detail: str = "") -> None:
    """Extension C: record a state-transition event."""
    entry = {
        "time":     time.strftime("%H:%M:%S"),
        "node":     BASE_PORT,
        "event":    event,
        "token_id": token.token_id,
        "state":    token.state,
        "age":      f"{token.age:.1f}s",
        "detail":   detail,
    }
    event_log.append(entry)
    print(
        f"[LOG {entry['time']}] {event:<12} | token={token.token_id} "
        f"state={token.state:<14} age={entry['age']:<7} {detail}"
    )


# ── Networking helpers ────────────────────────────────────────────────────────


def transmit_token(peer_port: int, token: Token) -> bool:
    """
    Send a token over TCP to *peer_port*.

    The token is serialised to JSON (wire format).
    On success, the token has left this node — no-cloning means we must
    remove it from our queue and never forward it again from here.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(token.to_wire().encode())
        s.close()
        log_event("TRANSMITTED", token, f"→ port {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        log_event("TX_FAILED", token, f"→ port {peer_port} unreachable")
        return False


# ── Background threads ────────────────────────────────────────────────────────


def forward_loop() -> None:
    """
    Periodically scan the token queue:
      - Expire stale tokens (TTL exceeded)
      - Attempt to forward valid tokens to the first reachable peer
      - Remove tokens after successful transmission (no-cloning)
    """
    while True:
        time.sleep(UPDATE_INTERVAL)
        print(f"\n[NODE {BASE_PORT}] ── Forwarding cycle ──")
        print_token_queue()

        with queue_lock:
            now = time.time()
            to_remove = []

            for token in token_queue:
                # Check expiry first
                if now - token.created_at > TOKEN_EXPIRY:
                    token.state = TokenState.EXPIRED
                    log_event("EXPIRED", token, "TTL exceeded — discarding")
                    to_remove.append(token)
                    continue

                # Extension B: hop limit check
                can_hop = token.try_forward(BASE_PORT)
                if not can_hop:
                    # Must be consumed here — collapse and read
                    msg = token.read_token()
                    if msg:
                        print(f"[NODE {BASE_PORT}] 📬 Consumed at hop limit: {msg!r}")
                    to_remove.append(token)
                    continue

                # Attempt transmission to first reachable peer
                # No-cloning: stop after the first success
                forwarded = False
                for peer in PEER_PORTS:
                    if peer in seen_token_ids:
                        continue  # Avoid duplicate delivery
                    if transmit_token(peer, token):
                        seen_token_ids.add(token.token_id)
                        to_remove.append(token)
                        forwarded = True
                        break

                if not forwarded:
                    log_event("QUEUED", token, "all peers unreachable — retaining")

            for token in to_remove:
                if token in token_queue:
                    token_queue.remove(token)

        print_stats()


def start_server() -> None:
    """
    Accept incoming TCP connections.
    Each connection carries one serialised token (JSON).
    On receipt: collapse (read once) and log. Never forward a collapsed token.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, BASE_PORT))
    server.listen()
    print(f"[NODE {BASE_PORT}] Listening on {HOST}:{BASE_PORT} ...")

    while True:
        conn, addr = server.accept()
        raw = b""
        while True:
            chunk = conn.recv(BUFFER_SIZE)
            if not chunk:
                break
            raw += chunk
        conn.close()

        if not raw:
            continue

        try:
            token = Token.from_wire(raw.decode(errors="replace"))
        except Exception as e:
            print(f"[NODE {BASE_PORT}] ✗ Could not deserialise token: {e}")
            continue

        log_event("RECEIVED", token, f"from {addr[0]}:{addr[1]}")

        # Extension B: duplicate check
        if token.token_id in seen_token_ids:
            log_event("DUPLICATE", token, "already seen — discarding (no-cloning)")
            continue

        seen_token_ids.add(token.token_id)

        # State collapse — read once
        message = token.read_token()
        if message:
            print(f"\n[NODE {BASE_PORT}] ⚡ Token collapsed: {message!r}")
            print(f"              Path: {' → '.join(str(p) for p in token.hop_path)}")
        else:
            log_event("INVALID", token, "expired or already collapsed on arrival")


# ── Extension C: analytics ────────────────────────────────────────────────────


def print_token_queue() -> None:
    with queue_lock:
        if not token_queue:
            print(f"[NODE {BASE_PORT}] Token queue: (empty)")
            return
        print(f"[NODE {BASE_PORT}] Token queue ({len(token_queue)} item(s)):")
        for t in token_queue:
            print(f"  {t.summary()}")


def print_stats() -> None:
    counts = {e: 0 for e in ("TRANSMITTED", "TX_FAILED", "RECEIVED", "EXPIRED", "DUPLICATE")}
    for entry in event_log:
        if entry["event"] in counts:
            counts[entry["event"]] += 1
    print(
        f"[NODE {BASE_PORT}] Stats → "
        + "  ".join(f"{k}={v}" for k, v in counts.items())
        + f"  queued={len(token_queue)}"
    )


# ── Entry point ───────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print(f"{'─'*62}")
    print(f"  Week 10 – Quantum-Inspired Networking  (port {BASE_PORT})")
    print(f"  Peers       : {PEER_PORTS}")
    print(f"  Token expiry: {TOKEN_EXPIRY}s")
    print(f"  Max hops    : from config.MAX_HOPS")
    print(f"{'─'*62}\n")
    print("  Quantum principles simulated:")
    print("    No-cloning  : a transmitted token is removed from this node")
    print("    Collapse    : reading a token is irreversible")
    print("    Expiry      : unread tokens past TTL are discarded")
    print("    Hop path    : tokens carry their travel history\n")

    # Start background threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Generate initial tokens
    time.sleep(0.3)  # Let server bind
    for peer in PEER_PORTS:
        token = Token(
            message=f"Quantum token from node {BASE_PORT} → {peer}",
            origin_port=BASE_PORT,
        )
        log_event("CREATED", token, f"destined for {peer}")

        # Attempt immediate delivery
        if not transmit_token(peer, token):
            print(f"[NODE {BASE_PORT}] Peer {peer} offline — queuing token")
            with queue_lock:
                token_queue.append(token)

    print(f"\n[NODE {BASE_PORT}] Running. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n[NODE {BASE_PORT}] Shutting down.")
        print("\n── Final event log ──────────────────────────────────")
        for entry in event_log[-20:]:   # Last 20 events
            print(
                f"  {entry['time']}  {entry['event']:<12}  "
                f"token={entry['token_id']}  {entry['detail']}"
            )
        print_stats()
