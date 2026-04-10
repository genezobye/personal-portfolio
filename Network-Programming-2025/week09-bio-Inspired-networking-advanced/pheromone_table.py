# pheromone_table.py – Week 9: Bio-Inspired Networking
# ─────────────────────────────────────────────────────
# Simulates an ant-colony pheromone trail table.
#
# Analogy:
#   Ants deposit pheromone on good paths → others follow.
#   Pheromone evaporates over time → stale paths fade.
#   Successful delivery  = ant reached food = reinforce.
#   Failed delivery      = path blocked    = let it decay.

from config import DECAY_FACTOR


class PheromoneTable:
    """
    Tracks pheromone level per peer.

    Pheromone rules:
      - Starts at INITIAL_PHEROMONE for known peers
      - Increases by REINFORCEMENT on each successful delivery
      - Multiplied by DECAY_FACTOR each cycle (evaporation)
      - Never goes below 0
    """

    def __init__(self):
        # {peer_port: float}
        self.table: dict[int, float] = {}

    # ── Core operations ───────────────────────────────────────────────────────

    def initialize(self, peer: int, value: float) -> None:
        """Set an initial pheromone level for a peer."""
        self.table[peer] = max(0.0, value)

    def reinforce(self, peer: int, amount: float) -> None:
        """
        Deposit pheromone after a successful delivery (positive reinforcement).
        If peer is unknown, registers it first.
        """
        prev = self.table.get(peer, 0.0)
        self.table[peer] = prev + amount
        print(
            f"[PHEROMONE] ✚ Reinforce {peer}: {prev:.3f} → {self.table[peer]:.3f}"
        )

    def decay(self) -> None:
        """
        Evaporate pheromone for all peers.
        Called every cycle so unused paths naturally fade.
        """
        for peer in self.table:
            self.table[peer] = max(0.0, self.table[peer] * DECAY_FACTOR)
        print(f"[PHEROMONE] ~ Decay applied (factor={DECAY_FACTOR})")

    # ── Query ─────────────────────────────────────────────────────────────────

    def get_level(self, peer: int) -> float:
        """Return current pheromone level for a peer (0.0 if unknown)."""
        return self.table.get(peer, 0.0)

    def get_best_candidates(self, threshold: float) -> list[int]:
        """Return peers whose pheromone meets or exceeds the threshold, sorted best-first."""
        return sorted(
            [p for p, v in self.table.items() if v >= threshold],
            key=lambda p: self.table[p],
            reverse=True,
        )

    def get_best_peer(self) -> int | None:
        """Return the single peer with the highest pheromone level (or None)."""
        if not self.table:
            return None
        return max(self.table, key=lambda p: self.table[p])

    # ── Extension C: visualization ────────────────────────────────────────────

    def display(self) -> None:
        """Print pheromone trail table to stdout with a simple bar chart."""
        print("\n[PHEROMONE TABLE]")
        if not self.table:
            print("  (empty)")
            return
        max_val = max(self.table.values()) if self.table else 1.0
        for peer, val in sorted(self.table.items()):
            bar_len = int((val / max(max_val, 0.001)) * 24)
            bar = "▓" * bar_len + "░" * (24 - bar_len)
            print(f"  Port {peer}: {val:6.3f}  [{bar}]")
        print()
