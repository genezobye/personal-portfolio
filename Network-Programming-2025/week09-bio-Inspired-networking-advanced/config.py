# config.py – Week 9: Bio-Inspired Networking
# ─────────────────────────────────────────────
# Each node needs its own BASE_PORT.
# Edit before running each terminal instance.

HOST = "127.0.0.1"
BASE_PORT = 10000           # Change to 10001 / 10002 for other nodes
PEER_PORTS = [10001, 10002] # All other nodes in the network

BUFFER_SIZE = 1024
INITIAL_PHEROMONE = 1.0     # Starting pheromone level for each peer
DECAY_FACTOR = 0.9          # Pheromone × this value each cycle (evaporation)
REINFORCEMENT = 0.5         # Added to pheromone on successful delivery
FORWARD_THRESHOLD = 0.2     # Minimum pheromone to consider forwarding
UPDATE_INTERVAL = 5         # Seconds between forwarding loop cycles
MESSAGE_TTL = 60            # Seconds before a queued message expires
