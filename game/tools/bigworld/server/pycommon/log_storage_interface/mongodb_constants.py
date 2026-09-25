"""
These constants are for MongoDB only.
"""

# The prefix of a user log database
USER_DB_PREFIX = "bw_ml_user_"

# The prefix of a common data database
COMMON_DB_PREFIX = "bw_ml_common"

# The separator used in database name to separate loggerID from other part
LOGGER_ID_DELIMITER = "#"

# The loggerID to use when no loggerID is specified
LOGGER_ID_NA = ""

# How many results MondoDB is to return in one batch
QUERY_BATCH_SIZE = 100

# No result limit, fetch as many as possible
QUERY_NO_LIMIT = 0

# collection name for appid
APPID_COLLECTION_NAME = "components"