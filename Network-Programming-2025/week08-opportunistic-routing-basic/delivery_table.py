# delivery_table.py – Week 8: Opportunistic Routing
# ────────────────────────────────────────────────
# Tracks delivery probability per peer.
# Higher probability = more reliable delivery partner.

import time
from config import DECAY_FACTOR


class DeliveryTable:
    """
    Stores and manages delivery probabilities for each known peer.

    Probability rules:
      - Range: 0.0 (never seen) → 1.0 (always reachable)
      - Increases on successful delivery
      - Decays over time when a peer is not encountered
    """

    def __init__(self):
        # {peer_port: {"prob": float, "last_seen": timestamp}}
        self.table = {}

    # ── Basic operations ──────────────────────────────────────────────────────

    def update_probability(self, peer: int, prob: float) -> None:
        """Directly set a peer's delivery probability (clamped to [0, 1])."""
        self.table[peer] = {
            "prob": max(0.0, min(1.0, prob)),
            "last_seen": time.time(),
        }

    def get_probability(self, peer: int) -> float:
        """Return current delivery probability for a peer (0.0 if unknown)."""
        entry = self.table.get(peer)
        return entry["prob"] if entry else 0.0

    def get_best_candidates(self, threshold: float) -> list[int]:
        """Return all peers whose probability meets or exceeds the threshold."""
        return [
            peer
            for peer, data in self.table.items()
            if data["prob"] >= threshold
        ]

    # ── Extension A: Dynamic probability updates ─────────────────────────────

    def on_encounter(self, peer: int) -> None:
        """
        Call when we successfully reach a peer.
        Uses additive increase: prob = prob + (1 - prob) × 0.5
        (same formula used in PRoPHET routing protocol)
        """
        current = self.get_probability(peer)
        new_prob = current + (1 - current) * 0.5
        self.update_probability(peer, new_prob)
        print(f"[DELIVERY TABLE] Encounter with {peer}: {current:.2f} → {new_prob:.2f}")

    def decay_all(self) -> None:
        """
        Decay probabilities for all peers not recently encountered.
        Call periodically to reflect changing network topology.
        """
        for peer in self.table:
            old = self.table[peer]["prob"]
            self.table[peer]["prob"] = old * DECAY_FACTOR
        print(f"[DELIVERY TABLE] Decayed all probabilities (factor={DECAY_FACTOR})")

    # ── Utility ───────────────────────────────────────────────────────────────

    def display(self) -> None:
        """Print current table to stdout."""
        print("\n[DELIVERY TABLE] Current probabilities:")
        if not self.table:
            print("  (empty)")
            return
        for peer, data in sorted(self.table.items()):
            bar = "█" * int(data["prob"] * 20)
            print(f"  Port {peer}: {data['prob']:.2f}  |{bar:<20}|")
        print()
