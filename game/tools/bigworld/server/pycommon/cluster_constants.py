# ------------------------------------------------------------------------------
# Section: Globals
# ------------------------------------------------------------------------------

# How long we'll wait for machined and watcher replies
TIMEOUT = 10

# How many bots we add at once
NBOTS_AT_ONCE = 10

# CPU threshold for machines running bots
MAX_BOTS_CPU = 0.65

# CPU threshold for machines running server components
MAX_SERVER_CPU = 0.75

# Time to sleep while waiting for CPU load to drop
CPU_WAIT_SLEEP = 2

# Time between checks to see if the server is/isn't running
POLL_SLEEP = 1

# Maximum number of times we'll wait for the server to stop
MAX_POLL_SLEEPS = 20

# Maximum seconds we'll wait for the server to start up
MAX_STARTUP_SLEEPS = 60

# If enabled, only spawn bots processes on machines that already have bots
# processes on them
BOTS_EXCLUSIVE = True

# Buffer size for each recv() call
RECV_BUF_SIZE = 65536

# Adjustment to cell entities for static entities
CELL_ENTITY_ADJ = 0

# This is the default name that server tools use when sending once-off messages
# to message_logger
MESSAGE_LOGGER_NAME = "Tools"

#Definitions of supported build configurations
BW_CONFIG_HYBRID = "hybrid"
BW_CONFIG_DEBUG = "debug"
BW_SUPPORTED_CONFIGS = [ BW_CONFIG_HYBRID, BW_CONFIG_DEBUG ]
# cluster_constants.py
