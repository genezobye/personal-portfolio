# node.py – Week 9: Bio-Inspired Networking
# ─────────────────────────────────────────────────────────────────────────────
# Simulates an ant-colony-inspired network node that:
#   1. Listens for incoming messages on BASE_PORT
#   2. Maintains a pheromone table — reinforced on success, decayed over time
#   3. Forwards queued messages along the strongest pheromone path
#   4. Supports TTL expiry and delivery statistics (Extensions B & C)
#
# Key difference from Week 8:
#   Week 8 used a fixed probability (0.0–1.0).
#   Week 9 uses an unbounded pheromone value — paths with more successful
#   deliveries accumulate more trail; unused paths evaporate toward zero.
#   This is the reinforcement learning / ACO (Ant Colony Optimization) analogy.
#
# Run one instance per terminal with a different BASE_PORT in config.py.

import socket
import threading
import time

from config import (
    BASE_PORT,
    BUFFER_SIZE,
    DECAY_FACTOR,
    FORWARD_THRESHOLD,
    HOST,
    INITIAL_PHEROMONE,
    MESSAGE_TTL,
    PEER_PORTS,
    REINFORCEMENT,
    UPDATE_INTERVAL,
)
from pheromone_table import PheromoneTable

# ── Shared state ──────────────────────────────────────────────────────────────

pheromone_table = PheromoneTable()

# Each queued message: {"text": str, "enqueued_at": float, "attempts": int}
message_queue: list[dict] = []
queue_lock = threading.Lock()

# Extension C: statistics
stats = {
    "sent": 0,
    "failed": 0,
    "expired": 0,
    "received": 0,
    "total_reinforcement": 0.0,
}


# ── Networking helpers ────────────────────────────────────────────────────────


def send_message(peer_port: int, message: str) -> bool:
    """
    Attempt TCP delivery of *message* to *peer_port*.

    On success → reinforce pheromone trail to that peer.
    On failure → let the trail decay naturally (no negative reinforcement).
    Returns True on success.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()

        # ── Reinforcement: deposit pheromone on the successful path ──
        pheromone_table.reinforce(peer_port, REINFORCEMENT)
        stats["sent"] += 1
        stats["total_reinforcement"] += REINFORCEMENT
        print(f"[NODE {BASE_PORT}] ✓ Sent to {peer_port}: {message!r}")
        return True

    except (ConnectionRefusedError, socket.timeout, OSError):
        # No negative reinforcement — decay handles path degradation passively
        stats["failed"] += 1
        print(f"[NODE {BASE_PORT}] ✗ Failed to reach {peer_port}")
        return False


# ── Background threads ────────────────────────────────────────────────────────


def forward_loop() -> None:
    """
    Each cycle:
      1. Evaporate all pheromone trails (decay)
      2. Find candidates above FORWARD_THRESHOLD
      3. For each queued message, try the strongest trail first
      4. Expire messages that have exceeded MESSAGE_TTL
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        # Step 1: Evaporation
        pheromone_table.decay()
        pheromone_table.display()

        # Step 2: Find viable paths
        candidates = pheromone_table.get_best_candidates(FORWARD_THRESHOLD)

        if not candidates:
            print(
                f"[NODE {BASE_PORT}] No paths above threshold {FORWARD_THRESHOLD:.2f} — "
                f"waiting for encounters..."
            )
        else:
            print(
                f"[NODE {BASE_PORT}] Candidate paths (pheromone ≥ {FORWARD_THRESHOLD}): "
                f"{candidates}"
            )

        # Step 3 & 4: Process queue
        with queue_lock:
            now = time.time()
            to_remove = []

            for item in message_queue:
                age = now - item["enqueued_at"]

                # TTL check (Extension B)
                if age > MESSAGE_TTL:
                    print(
                        f"[NODE {BASE_PORT}] ⏰ Expired (age={age:.0f}s, "
                        f"attempts={item['attempts']}): {item['text']!r}"
                    )
                    stats["expired"] += 1
                    to_remove.append(item)
                    continue

                # Try candidates in pheromone-strength order (strongest first)
                delivered = False
                for peer in candidates:
                    if send_message(peer, item["text"]):
                        to_remove.append(item)
                        delivered = True
                        break
                    # else: trail decays naturally, try next candidate

                if not delivered:
                    item["attempts"] += 1
                    print(
                        f"[NODE {BASE_PORT}] ⏳ Still queued (attempt #{item['attempts']}, "
                        f"age={age:.0f}s): {item['text']!r}"
                    )

            for item in to_remove:
                message_queue.remove(item)

        print_stats()


def start_server() -> None:
    """Accept TCP connections and enqueue received messages for forwarding."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, BASE_PORT))
    server.listen()
    print(f"[NODE {BASE_PORT}] Listening on {HOST}:{BASE_PORT} ...")

    while True:
        conn, addr = server.accept()
        data = conn.recv(BUFFER_SIZE).decode(errors="replace")
        conn.close()
        print(f"[NODE {BASE_PORT}] ← Received from {addr}: {data!r}")
        stats["received"] += 1
        with queue_lock:
            message_queue.append({
                "text": data,
                "enqueued_at": time.time(),
                "attempts": 0,
            })


# ── Extension C: statistics ───────────────────────────────────────────────────


def print_stats() -> None:
    print(
        f"[NODE {BASE_PORT}] Stats → "
        f"sent={stats['sent']}  failed={stats['failed']}  "
        f"expired={stats['expired']}  received={stats['received']}  "
        f"queued={len(message_queue)}  "
        f"total_reinforcement={stats['total_reinforcement']:.2f}"
    )


# ── Entry point ───────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print(f"{'─'*62}")
    print(f"  Week 9 – Bio-Inspired (Pheromone) Routing  (port {BASE_PORT})")
    print(f"  Peers            : {PEER_PORTS}")
    print(f"  Forward threshold: {FORWARD_THRESHOLD}")
    print(f"  Decay factor     : {DECAY_FACTOR}  (evaporation per cycle)")
    print(f"  Reinforcement    : +{REINFORCEMENT} per successful delivery")
    print(f"{'─'*62}\n")

    # Start background threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Initialize pheromone trails for known peers
    for peer in PEER_PORTS:
        pheromone_table.initialize(peer, INITIAL_PHEROMONE)

    pheromone_table.display()

    # Initial delivery attempts
    time.sleep(0.3)  # Let server thread bind
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT} → {peer}"
        if not send_message(peer, msg):
            print(f"[NODE {BASE_PORT}] Peer {peer} unreachable — queuing: {msg!r}")
            with queue_lock:
                message_queue.append({
                    "text": msg,
                    "enqueued_at": time.time(),
                    "attempts": 0,
                })

    print(f"\n[NODE {BASE_PORT}] Running. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n[NODE {BASE_PORT}] Shutting down.")
        pheromone_table.display()
        print_stats()
