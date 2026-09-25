# This file contains global configuration settings used by FantasyDemo

# If True, the spaces are automatically populated with the entities from the
# chunks when the server is started.
LOAD_ENTITIES_FROM_CHUNKS = True

# If True, operations not supported by unscripted bots are not performed.
# (The main limitation is that client methods cannot be called from the base.)
UNSCRIPTED_BOTS_MODE = False

# If True, Avatar instance with a playerName of "bot_" are allowed to
# establish XMPP connections. Disabling this option prevents a large number
# of once off accounts being created on the XMPP server.
BOTS_CAN_USE_XMPP = False

# FDConfig.py
