# config.py – Week 8: Opportunistic Routing
# ─────────────────────────────────────────
# Each node needs its own BASE_PORT.
# Edit before running each terminal instance.

HOST = "127.0.0.1"
BASE_PORT = 9000          # Change to 9001 / 9002 for other nodes
PEER_PORTS = [9001, 9002] # All other nodes in the network

BUFFER_SIZE = 1024
FORWARD_THRESHOLD = 0.5   # Forward only if delivery probability >= this value
UPDATE_INTERVAL = 5       # Seconds between forwarding loop cycles
DECAY_FACTOR = 0.9        # Probability decay per missed encounter (Extension A)
MESSAGE_TTL = 30          # Seconds before a queued message expires (Extension B)
