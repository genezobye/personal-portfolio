# token.py – Week 10: Quantum-Inspired Networking
# ─────────────────────────────────────────────────────────────────────────────
# Simulates the quantum "no-cloning" and "state collapse" principles:
#
#   No-cloning:     A token's message cannot be copied or forwarded after reading.
#   State collapse: The act of reading the token changes its state — permanently.
#   Superposition:  Until read, the token exists in an "unread" state that could
#                   be observed by anyone, but collapses the moment it is.
#
# This is a *conceptual* simulation — no actual quantum hardware is used.

import json
import time
import uuid

from config import MAX_HOPS, TOKEN_EXPIRY


class TokenState:
    """Possible states of a quantum-inspired token."""
    SUPERPOSITION = "SUPERPOSITION"   # Created, not yet read
    COLLAPSED     = "COLLAPSED"       # Read once — irreversibly consumed
    EXPIRED       = "EXPIRED"         # TTL exceeded before reading


class Token:
    """
    A one-time-read message token.

    Inspired by:
      - Quantum no-cloning theorem: you cannot duplicate a quantum state
      - Wave-function collapse: measuring (reading) changes the state forever
      - BB84 / QKD: keys are consumed on use

    Fields:
      token_id   — globally unique identifier (like a quantum key)
      message    — the payload (only accessible before collapse)
      state      — SUPERPOSITION | COLLAPSED | EXPIRED
      created_at — Unix timestamp of creation
      read_at    — Unix timestamp of collapse (or None)
      hop_path   — ordered list of node ports this token has visited
    """

    def __init__(self, message: str, origin_port: int):
        self.token_id   = str(uuid.uuid4())[:12]   # Short but unique
        self.message    = message
        self.state      = TokenState.SUPERPOSITION
        self.created_at = time.time()
        self.read_at    = None
        self.origin_port = origin_port
        self.hop_path: list[int] = [origin_port]   # Extension B: multi-hop history

    # ── Core quantum-inspired behaviour ──────────────────────────────────────

    def read_token(self) -> str | None:
        """
        Attempt to read (collapse) this token.

        Returns the message if the token is still in SUPERPOSITION and
        within its TTL. Returns None and updates state otherwise.

        This is the "measurement" operation — irreversible.
        """
        # Check expiry first
        if self._is_expired():
            self.state = TokenState.EXPIRED
            print(f"[TOKEN {self.token_id}] ⚠ Expired — state collapsed to EXPIRED")
            return None

        # No-cloning: already read → cannot read again
        if self.state == TokenState.COLLAPSED:
            print(f"[TOKEN {self.token_id}] ✗ Already collapsed — no-cloning principle")
            return None

        if self.state == TokenState.EXPIRED:
            print(f"[TOKEN {self.token_id}] ✗ Expired token — access denied")
            return None

        # Valid read → collapse the state
        self.state   = TokenState.COLLAPSED
        self.read_at = time.time()
        print(
            f"[TOKEN {self.token_id}] ⚡ State collapsed: SUPERPOSITION → COLLAPSED "
            f"(lived {self.age:.1f}s)"
        )
        return self.message

    def try_forward(self, via_port: int) -> bool:
        """
        Extension B: record a hop without collapsing the token.
        Returns False if hop limit reached (token must be consumed).
        """
        if self.state != TokenState.SUPERPOSITION:
            return False
        if len(self.hop_path) >= MAX_HOPS:
            print(
                f"[TOKEN {self.token_id}] Max hops ({MAX_HOPS}) reached — "
                f"must be consumed at next node"
            )
            return False
        self.hop_path.append(via_port)
        return True

    # ── Serialisation (for network transmission) ──────────────────────────────

    def to_wire(self) -> str:
        """Serialise token to JSON string for TCP transmission."""
        return json.dumps({
            "token_id":    self.token_id,
            "message":     self.message,
            "state":       self.state,
            "created_at":  self.created_at,
            "origin_port": self.origin_port,
            "hop_path":    self.hop_path,
        })

    @classmethod
    def from_wire(cls, data: str) -> "Token":
        """Deserialise a token received from the network."""
        d = json.loads(data)
        t = cls.__new__(cls)
        t.token_id    = d["token_id"]
        t.message     = d["message"]
        t.state       = d["state"]
        t.created_at  = d["created_at"]
        t.read_at     = None
        t.origin_port = d["origin_port"]
        t.hop_path    = d["hop_path"]
        return t

    # ── Properties & utilities ────────────────────────────────────────────────

    @property
    def age(self) -> float:
        return time.time() - self.created_at

    @property
    def is_valid(self) -> bool:
        return self.state == TokenState.SUPERPOSITION and not self._is_expired()

    def _is_expired(self) -> bool:
        return time.time() - self.created_at > TOKEN_EXPIRY

    def summary(self) -> str:
        age_str = f"{self.age:.1f}s"
        path    = " → ".join(str(p) for p in self.hop_path)
        return (
            f"Token[{self.token_id}] "
            f"state={self.state:<14} "
            f"age={age_str:<7} "
            f"path={path}"
        )
