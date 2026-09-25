# Some constants
ID_MACHINES = -2
ID_ALLPROCESSES = -1

STAT_LOGGER_CHARSET = "utf8"

# Value in seconds to wait before we decide a program has died
# Floating point number, so can use fractional part too
timeoutLength = 10.0

# ------------------------------------------------------------------------------
# Section: Database  table names and prefices
# ------------------------------------------------------------------------------
infoDbName  = "bw_stat_log_info"		# Name of the info db
tblInfo = "bw_stat_log_databases"		# Name of the table in the info db

# Table prefixes...
statPrefix = "stat_"				# Statistic table name prefix
seenPrefix = "seen_"				# Seen table name prefix (for detecting
									# instances of machines and processes)
stdPrefix  = "std_"					# Standard table name prefix
prefPrefix = "pref_"				# Preference table name prefix

tblSeenMachines = seenPrefix + "machines"
tblSeenProcesses = seenPrefix + "processes"
tblSeenUsers = seenPrefix + "users"
tblStatMachines = statPrefix + "machines"

tblStdSessionTimes = stdPrefix + "session_times"
tblStdTickTimes    = stdPrefix + "tick_times"
tblStdInfo         = stdPrefix + "info"
tblStdTouchTime    = stdPrefix + "touch_time"
tblStdWindows      = stdPrefix + "aggregation_windows"

tblPrefCategories = prefPrefix + "categories"
tblPrefProcesses = prefPrefix + "processes"
tblPrefStatistics = prefPrefix + "statistics"

dbVersion = "0.4.3"

dbConnectTimeOut = 10


# ------------------------------------------------------------------------------
# Section: Consolidation functions
# ------------------------------------------------------------------------------

# Take the average value over the aggregation period
CONSOLIDATE_AVG = 1
# Take the maximum value over the aggregation period
CONSOLIDATE_MAX = 2
#Take the minimum value over the aggregation period
CONSOLIDATE_MIN = 3

CONSOLIDATE_NAMES = {
	CONSOLIDATE_AVG: "AVG",
	CONSOLIDATE_MAX: "MAX",
	CONSOLIDATE_MIN: "MIN"
}

# ------------------------------------------------------------------------------
# Section: Comparison constants
# ------------------------------------------------------------------------------
COMPARE_FIRST_ONLY = 1
COMPARE_SECOND_ONLY = -1
COMPARE_MATCH = 2
COMPARE_MISMATCH = 3

# ------------------------------------------------------------------------------
# Section: Preference filename
# ------------------------------------------------------------------------------
prefFilename = "preferences.xml"

# constants.py
