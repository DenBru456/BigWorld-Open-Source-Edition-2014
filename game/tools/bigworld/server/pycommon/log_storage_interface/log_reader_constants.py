"""
Log Reader constants are used for reading and viewing logs. Generally used by
log reader implementations (eg. BaseLogReader) and its related classes, and by
modules which use the reader (such as LogViewer or mlcat.py).
"""

# Used to cleanup the cache of recent query objects to free up memory
QUERY_CACHE_TIMEOUT = 120  # mins

DEFAULT_CONTEXT = 10 # lines

# This is a safety measure to prevent very poor usage of QueryResults (a
# buffered, jsonifyable result set). It will prevent excessive result sets
# using up all the system memory when buffering results. Every function which
# fetches a result set.
MAX_BUFFERED_RESULTS = 10000


PRE_INTERPOLATE, \
POST_INTERPOLATE, \
DONT_INTERPOLATE = range(3)

# Used to pass server startup as a commonly defined string in the 'start'
# parameter to query parameter processing classes
SERVER_STARTUP_STRING = "server startup"

# Other constants that could be present in the 'start' parameter
QUERY_BEGINNING_OF_LOGS = "beginning of logs"
QUERY_NOW = "now"

# Used for the 'period' parameter
QUERY_TO_BEGINNING = "to beginning"
QUERY_TO_PRESENT = "to present"

# this is the default order of columns returned by message_logger
ORDERED_OUTPUT_COLUMNS = [
	"date",
	"time",
	"host",
	"serveruser",
	"pid",
	"process",
	"appid",
	"source",
	"severity",
	"category",
	"message",
]

# output columns that will be displayed by default
DEFAULT_DISPLAY_COLUMNS = (
	'date',
	'time',
	'host',
	'process',
	'source',
	'severity',
	'category',
	'message'
)

