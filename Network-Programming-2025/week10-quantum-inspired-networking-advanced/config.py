# config.py – Week 10: Quantum-Inspired Networking
# ──────────────────────────────────────────────────
# Each node needs its own BASE_PORT.
# Edit before running each terminal instance.

HOST = "127.0.0.1"
BASE_PORT = 11000            # Change to 11001 / 11002 for other nodes
PEER_PORTS = [11001, 11002]  # All other nodes in the network

BUFFER_SIZE = 4096
TOKEN_EXPIRY = 30            # Seconds before an unread token becomes invalid
UPDATE_INTERVAL = 5          # Seconds between forwarding loop cycles
MAX_HOPS = 3                 # Extension B: maximum hops before token is consumed
