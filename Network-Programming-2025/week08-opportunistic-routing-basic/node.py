# node.py – Week 8: Opportunistic Routing
# ─────────────────────────────────────────────────────────────────────────────
# Simulates a mobile network node that:
#   1. Listens for incoming messages on BASE_PORT
#   2. Maintains delivery probabilities for all known peers
#   3. Forwards queued messages opportunistically when a good encounter occurs
#   4. Supports TTL expiry and delivery statistics (Extensions B & C)
#
# Run one instance per terminal with a different BASE_PORT in config.py.

import socket
import threading
import time

from config import (
    BASE_PORT,
    BUFFER_SIZE,
    FORWARD_THRESHOLD,
    HOST,
    MESSAGE_TTL,
    PEER_PORTS,
    UPDATE_INTERVAL,
)
from delivery_table import DeliveryTable

# ── Shared state ──────────────────────────────────────────────────────────────

delivery_table = DeliveryTable()

# Each queued message: {"text": str, "enqueued_at": float}
message_queue: list[dict] = []
queue_lock = threading.Lock()

# Extension C: statistics
stats = {"sent": 0, "failed": 0, "expired": 0, "received": 0}


# ── Networking helpers ────────────────────────────────────────────────────────


def send_message(peer_port: int, message: str) -> bool:
    """
    Attempt to deliver *message* to *peer_port*.
    Returns True on success, False on connection failure or timeout.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        print(f"[NODE {BASE_PORT}] ✓ Sent to {peer_port}: {message!r}")
        stats["sent"] += 1
        delivery_table.on_encounter(peer_port)   # Extension A
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        stats["failed"] += 1
        return False


# ── Background threads ────────────────────────────────────────────────────────


def forward_loop() -> None:
    """
    Periodically check the message queue and opportunistically forward
    each message to the best available peer.
    """
    while True:
        time.sleep(UPDATE_INTERVAL)
        delivery_table.decay_all()          # Extension A: decay probabilities
        delivery_table.display()

        candidates = delivery_table.get_best_candidates(FORWARD_THRESHOLD)
        if not candidates:
            print(f"[NODE {BASE_PORT}] No candidates above threshold {FORWARD_THRESHOLD}")
            continue

        with queue_lock:
            now = time.time()
            to_remove = []

            for item in message_queue:
                # Extension B: TTL expiry
                age = now - item["enqueued_at"]
                if age > MESSAGE_TTL:
                    print(f"[NODE {BASE_PORT}] ⏰ Message expired (age={age:.0f}s): {item['text']!r}")
                    stats["expired"] += 1
                    to_remove.append(item)
                    continue

                # Try each candidate (best-first)
                sorted_candidates = sorted(
                    candidates,
                    key=lambda p: delivery_table.get_probability(p),
                    reverse=True,
                )
                delivered = False
                for peer in sorted_candidates:
                    if send_message(peer, item["text"]):
                        to_remove.append(item)
                        delivered = True
                        break

                if not delivered:
                    print(
                        f"[NODE {BASE_PORT}] ⏳ No delivery yet for: {item['text']!r} "
                        f"(age={age:.0f}s)"
                    )

            for item in to_remove:
                message_queue.remove(item)

        print_stats()


def start_server() -> None:
    """Accept incoming TCP connections and queue received messages."""
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
            message_queue.append({"text": data, "enqueued_at": time.time()})


# ── Extension C: statistics ───────────────────────────────────────────────────


def print_stats() -> None:
    print(
        f"[NODE {BASE_PORT}] Stats → "
        f"sent={stats['sent']}  failed={stats['failed']}  "
        f"expired={stats['expired']}  received={stats['received']}  "
        f"queued={len(message_queue)}"
    )


# ── Entry point ───────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print(f"{'─'*60}")
    print(f"  Week 8 – Opportunistic Routing Node  (port {BASE_PORT})")
    print(f"  Peers: {PEER_PORTS}")
    print(f"  Forward threshold: {FORWARD_THRESHOLD}")
    print(f"{'─'*60}\n")

    # Start background threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Initialize delivery probabilities
    # (In a real network these would be learned from encounters.)
    for peer in PEER_PORTS:
        delivery_table.update_probability(peer, 0.6)

    delivery_table.display()

    # Send initial messages to each peer.
    # If unreachable, store them in the queue for later opportunistic delivery.
    time.sleep(0.5)  # Give server thread a moment to bind
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT} → {peer}"
        if not send_message(peer, msg):
            print(
                f"[NODE {BASE_PORT}] Peer {peer} unreachable – queuing: {msg!r}"
            )
            with queue_lock:
                message_queue.append({"text": msg, "enqueued_at": time.time()})

    print(f"\n[NODE {BASE_PORT}] Running. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n[NODE {BASE_PORT}] Shutting down.")
        print_stats()
