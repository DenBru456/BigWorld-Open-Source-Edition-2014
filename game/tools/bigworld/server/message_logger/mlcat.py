#!/usr/bin/env python

import re
import os
import sys
import time

import util

json = None

# simplejson is generally more comprehensive than the default json package,
# so try to rely on it by default.
try:
	import simplejson as json

except ImportError:
	try:
		import json
	except ImportError:
		# We only use the json module in one location, so check for the error
		# case there and don't break the rest of mlcat
		pass

import bwsetup
bwsetup.addPath( ".." )

from pycommon import util as pyutil
from pycommon.exceptions import QueryParamException, NotSupportedException
import pycommon.log_storage_interface
from pycommon.log_storage_interface import log_db_constants
from pycommon.log_storage_interface.log_reader_constants \
	import PRE_INTERPOLATE, POST_INTERPOLATE, DONT_INTERPOLATE, \
			SERVER_STARTUP_STRING

import logging
pyutil.setUpBasicCleanLogging()
log = logging.getLogger( __name__ )


DISPLAY_FLAGS_TO_COLUMNS = {
	"d"	: "date",
	"t"	: "time",
	"h"	: "host",
	"u"	: "serveruser",
	"i"	: "pid",
	"a"	: "appid",
	"p"	: "process",
	"s"	: "severity",
	"m"	: "message",
	"z"	: "source",
	"c"	: "category",
}


SEVERITY_FLAGS_TO_SEVERITIES = {
	"t": "TRACE",
	"d": "DEBUG",
	"i": "INFO",
	"n": "NOTICE",
	"w": "WARNING",
	"e": "ERROR",
	"c": "CRITICAL",
	"h": "HACK",
}


SUMMARY_FLAGS = {
	"t": "time",
	"h": "host",
	"u": "username",
	"i": "pid",
	"a": "appid",
	"p": "component",
	"s": "severity",
	"m": "message",
}

TIME_FMT = "%a %d %b %Y %H:%M:%S"

USAGE = """%prog [options] [logdir]

Dump log output to the console.

By default, output is dumped in a `cat`-like manner.  With the -f switch, output
can be continuously dumped in a `tail -f`-like manner.

To query logs other than those referred to in the message logger config file, 
enter the desired log directory at the end of the command. To specify a 
different storage type, such as MongoDB, use --storage-type and the name of 
the storage type. For MongoDB, the credentials contained in the config file 
will be used to connect to the server.

Specifying Times
================

The times for which output is dumped can be constrained using the --from, --to,
and --around switches.  The arguments to each command can either be a literal
date in the format 'Thu 09 Nov 2006 16:09:01', or a file, whose last modified
time will be used.

To search through recent log output, the --back switch can be used, which
accepts a number of seconds as an argument, and will search forwards to the
current time.  The time can also be given with an 'm', 'h', or 'd' suffix for
minutes, hours, and days respectively.

The log output for a particular server run can also be selected using the
--last-startup and --startup switches.  As expected, --last-startup will show
output from the most recent server run.  --startup expects an integer to be
passed in identifying a particular server run.  The IDs can be dumped using the
--show-startups switch.

Output Formatting
=================

The columns shown in the output can be manually configured using the -c switch,
which accepts a string of characters, each of which turns on a single column.
Note that the ordering of the output columns is fixed, and cannot be set by
passing flags to -c in a different order to the default.

The accepted flags are:

	d: SHOW_DATE
	t: SHOW_TIME
	h: SHOW_HOST
	u: SHOW_USER
	i: SHOW_PID
	a: SHOW_APPID
	p: SHOW_PROCS
	s: SHOW_SEVERITY
	m: SHOW_MESSAGE
	z: SHOW_MESSAGE_SOURCE_TYPE
	c: SHOW_CATEGORY

--narrow is an alias for '-c tpasm'.

Filters
=======

Most of the filtering capabilities of WebConsole's LogViewer page are exposed
via this commandline interface too.  Supported filters are:

--categories   Select log lines by log category
--message:     Include based on match against message text
--exclude:     Exclude based on match against message text
--pid:         Filter by PID
--appid:       Filter by AppID
--context:     Control number of context lines around matching lines
--severities:  Filter by list of severities -

                 t: TRACE
                 d: DEBUG
                 i: INFO
                 n: NOTICE
                 w: WARNING
                 e: ERROR
                 c: CRITICAL
                 h: HACK

               e.g. --severities we (just warnings and errors)
                    --severities ^td (everything but trace and debug)

--procs:       Filter by comma-separated list of processes
               e.g. --procs CellApp,BaseApp (include BaseApp & CellApp output)
               e.g. --procs ^LoginApp,DBApp (exclude LoginApp & DBApp output)

--host:        Filter by a single hostname
--key:         Filter by metadata key (only valid for mongodb)
--negate-key:  Filter by negating metadata key (only valid for mongodb)
--key-value-as-json: Filter by metadata key and value pair, it must be 
				JSON string, ie. '{"text": "abc"}' (only valid for mongodb)
--value-is-number: Search for metadata value specified in --key-value-as-json 
				as a number instead of string (only valid for mongodb)


The --message|--exclude options also accept filenames which should be a list of
strings (one per line) to include or exclude from output.

Summary Output
==============

Instead of displaying actual log output, a summary of search results can be
generated using the --summary option.  The argument to this option should be a
set of flags as follows:
	t: SHOW_TIME
	h: SHOW_HOST
	u: SHOW_USER
	i: SHOW_PID
	a: SHOW_APPID
	p: SHOW_PROCS
	s: SHOW_SEVERITY
	m: SHOW_MESSAGE
The flags specify which columns are used in calculating the histogram.

One of the flags may be specified in uppercase, which indicates that the results
should be sorted by this column before being sorted by count.  For example,
--summary Sm will calculate a summary based on severity and message, and
results will be sorted by severity, then count.

The --summarymin switch can be used to specify the minimum count for which results
will be displayed.

Etc
===

For debugging purposes, the log's format string database can be dumped by
passing --strings.

A list of the nub addresses for all apps since the last server startup can be
generated with --addresses.

A list of server startup times can be generated using --show-startups.  This is
useful when combined with the --startup switch for selecting output from a
particular server run.

Addresses in log output can be translated into their app names automatically
using the --translate switch.

Format string interpolation can be controlled with the --interpolate switch.  By
default, pre-interpolation is used, which means format strings have their
arguments substituted in before matching against message text is performed.
This is so the default behaviour is as similar to `cat`'s as possible.  If you
are searching through large amounts of log data and are looking for a particular
log message, you can realise big speed improvements by using post interpolation.
""".rstrip()


def main():
	try:
		return mlcat()
	except NotImplementedError, ex:
		log.error( "Method or feature is not implemented for the current "
			"logging database. Error details: %s.", str( ex ) )
		return 1

def mlcat():
	"""
	This is a convenience function to wrap mlcat functionality within a catch
	for a NotImplementedError exception, which could in theory occur at any
	point the log reader is accessed.
	"""
	opt = util.getBasicOptionParser( USAGE )

	opt.add_option( "-l", "--list-users", action = "store_true",
					help = "List the username / uid of all users in the log" )
	opt.add_option( "-f", "--follow", action = "store_true",
					help = "`tail -f`-like behaviour" )
	opt.add_option( "--summary", metavar = "COLS",
					help = "Generate a summary of results" )
	opt.add_option( "--summarymin", type = "int", default = 1,
					help = "The minimum count to include in a summary" )
	opt.add_option( "--no-progress-bar", action="store_false",
					dest = "showProgress", default=True,
					help = "Don't show a progress bar while summarising "
						"(default is to show)" )
	opt.add_option( "--interval", default = 1.0,
					type = "float",
					help = "Refresh interval when in follow mode" )
	opt.add_option( "--storage-type",
			help = "Specify which storage backend to use for the query. "
				"Valid backend options are: %s" %
				str( pycommon.log_storage_interface.getValidBackendsByName() ) )
	opt.add_option( "-c", "--cols",
					help = "Set columns to be shown in output" )
	opt.add_option( "-s", "--last-startup", action = "store_true",
					help = "Only show logs after last server startup" )
	opt.add_option( "-n", "--narrow", action = "store_const", dest = "cols",
					const = "tpasm",
					help = "An alias for '-c tpsm'" )
	opt.add_option( "--from", dest = "ffrom", metavar = "TIME",
					help = "Specify start time" )
	opt.add_option( "--to", metavar = "TIME",
					help = "Specify end time" )
	opt.add_option( "--around", metavar = "TIME",
					help = "Specify time of interest" )
	opt.add_option( "--back", metavar = "SECONDS",
					help = "Specify amount of history to search" )
	opt.add_option( "--startup", type = "int",
					help = "Specify server run to show output for" )
	opt.add_option( "-C", "--context", type = "int", default = -1,
					metavar = "N",
					help = "Specify number of lines of context. " \
						"For non-mldb databases this option is not valid " \
						"for normal cat mode, only for backwards and around " \
						"context modes such as --around and -f.")
	opt.add_option( "--strings", action = "store_true",
					help = "Dump the log's format string database" )
	opt.add_option( "--addresses", action = "store_true",
					help = "Dump nub addresses" )
	opt.add_option( "--show-startups", action = "store_true",
					help = "Show server start times" )
	opt.add_option( "--translate", action = "store_true",
					help = "Translate addresses in output into app names (only"\
						" valid for mldb)")
	opt.add_option( "-m", "--show-metadata", action = "store_true",
					help = "Show metadata key and value " \
					"(only valid for mongodb)" )

	# Filter options
	opt.add_option( "-M", "--message", metavar = "PATT",
					help = "Pattern to match against in message for inclusion" )
	opt.add_option( "-X", "--exclude", metavar = "PATT",
					help = "Pattern to match against in message for exclusion" )
	opt.add_option( "--categories", metavar = "LIST",
					help = "The categories to display logs for" )
	opt.add_option( "-P", "--pid", type = "int",
					help = "Filter by PID" )
	opt.add_option( "--appid", type = "int",
					help = "Filter by AppID" )
	opt.add_option( "-i", "--insensitive", action = "store_true",
					help = "Use case-insensitive pattern matching" )
	opt.add_option( "-I", "--interpolate",
					help = "Specify interpolation stage (pre|post|none)" )
	opt.add_option( "-S", "--severities", metavar = "FLAGS",
					help = "Specify severities to match" )
	opt.add_option( "--procs", metavar = "LIST",
					help = "Specify processes to match" )
	opt.add_option( "-H", "--host",
					help = "Specify hostname to match" )
	opt.add_option( "-T", "--source-type", metavar = "LIST",
					help = "The code source type of the logs (script|c++)" )
	opt.add_option( "--list-source-types", action = "store_true",
					help = "Print a list of all the valid source types" )
	opt.add_option( "-k", "--key",
					help = "Specify metadata key to match" \
						" (only valid for mongodb)" )
	opt.add_option( "-K", "--negate-key",
					help = "Specify negating metadata key to match" \
						" (only valid for mongodb)" )
	opt.add_option( "-j", "--key-value-as-json",
					help = "Specify metadata key and value pair to match, it" \
						" must be JSON string, ie. '{\"text\": \"abc\"}' " \
						"(only valid for mongodb)" )
	opt.add_option( "", "--value-is-number", action = "store_true",
					help = "Search for metadata value specified in " \
						"--key-value-as-json as a number instead of string " \
						"(only valid for mongodb)" )

	options, args = opt.parse_args()
	if options.storage_type:
		storageType = options.storage_type
	else:
		storageType = None

	try:
		reader = util.initReader( storageType, args )
	except (NotSupportedException, ValueError), e:
		print str( e )
		sys.exit( 1 )

	# We can immediately catch when metadata filters are used against an invalid
	# database.
	if (reader.dbType != log_db_constants.BACKEND_MONGODB) and \
			(options.key or options.negate_key or options.key_value_as_json):
		log.error( "Metadata filters are only implemented for MongoDB" )
		sys.exit( 1 )

	# --------------------------------------------------------------------------
	# First process options that do not require a valid user with log entries to
	# have been provided.
	# --------------------------------------------------------------------------

	# List of all valid source types
	if options.list_source_types:
		print "Valid source types: ", \
				", ".join( [ key.lower() for key in reader.getSourceNames() ] )
		return 0

	# List of all users with entries
	if options.list_users:
		users = reader.getUsers()
		if users:
			userNames = users.keys()
			userNames.sort()
			print "%15s\t%5s" % ("Username", "UID")
			print "%15s\t%5s" % ("========", "===")
			for user in userNames:
				print "%15s\t%5d" % (user, users[ user ])

		else:
			print "No users found in log"

		return 0

	# Format Strings
	if options.strings:
		ss = reader.getStrings()
		for s in ss:
			if s.endswith( '\n' ):
				print s,
			else:
				print s
		log.info( "\n* %d unique strings *", len( ss ) )
		return 0


	# --------------------------------------------------------------------------
	# Everything after this point requires a username with log entries. Ensure
	# we have one.
	# --------------------------------------------------------------------------

	serveruser = util.getServerUser( options, reader )

	if not serveruser:
		log.error( "No log entries for user %s. Unable to continue", options.uid )
		return 1

	# If we're dumping server nub addresses, do it and bail
	if options.addresses:

		results = reader.getNubAddresses( serveruser )

		if results:

			print "%-12s %6s %-20s %s" % \
				  ("App", "PID", "Address", "Type")

			for name, pid, addr, nubtype in results:
				print "%-12s %6d %-20s %s" % (name, pid, addr, nubtype)

		return 0

	# If we're dumping startup times, do it and bail
	if options.show_startups:

		results = reader.getAllServerStartups( serveruser,
											columnFilter = [ "date", "time" ] )

		for index, entry in enumerate( results ):

			sys.stdout.write( "#%-3d %s" % (index, entry) )

		return 0


	# Macro to process files of string patterns as appropriate
	def handlePatterns( opt ):
		if os.path.isfile( opt ):
			patts = [s.strip() for s in open( opt ).readlines()]
			return "(" + "|".join( patts ) + ")"
		else:
			return opt

	# Handle filter options
	kwargs = {}
	kwargs[ 'serveruser' ] = serveruser

	if options.message:
		kwargs[ "message" ] = handlePatterns( options.message )
	if options.exclude:
		kwargs[ "exclude" ] = handlePatterns( options.exclude )
	if options.pid:
		kwargs[ "pid" ] = options.pid
	if options.appid:
		kwargs[ "appid" ] = options.appid
	if options.insensitive:
		kwargs[ "casesens" ] = 0

	if options.severities:

		severities = []
		validSeverities = reader.getSeverities()

		for c in options.severities:
			if c == '^':
				kwargs[ "negate_severity" ] = True
			elif c in validSeverities.keys():
				severities.append( validSeverities[ c ] )
			elif c in SEVERITY_FLAGS_TO_SEVERITIES.keys():
				severities.append( SEVERITY_FLAGS_TO_SEVERITIES[ c ] )
			else:
				log.error( "Unsupported severity level: %s", c )

		kwargs[ "severities" ] = severities

	if options.procs:

		if options.procs[0] == '^':
			kwargs[ 'negate_procs' ] = True
			names = options.procs[1:]
		else:
			names = options.procs

		kwargs[ 'procs' ] = tuple( names.split( "," ) )

	if options.host:
		try:
			kwargs[ "host" ] = options.host
		except KeyError:
			log.error( "Host %s does not exist in this log", options.host )
			return 1

	if options.source_type:
		kwargs[ 'source' ] = tuple( options.source_type.split( "," ) )

	if options.categories:
		kwargs[ "categories" ] = tuple( options.categories.split( "," ) )

	if options.context != -1:
		backContext = options.context
	else:
		backContext = 20
		options.context = 0

	if options.interpolate == "pre":
		kwargs[ "interpolate" ] = PRE_INTERPOLATE
	elif options.interpolate == "post":
		kwargs[ "interpolate" ] = POST_INTERPOLATE
	elif options.interpolate == "none":
		kwargs[ "interpolate" ] = DONT_INTERPOLATE

	if options.cols:
		# Validate that the column letters provided are in the map
		for c in options.cols:
			if not c in DISPLAY_FLAGS_TO_COLUMNS:
				log.error( "Invalid column %s" % c )

		columnFilter = [DISPLAY_FLAGS_TO_COLUMNS[ c ] for c in options.cols]
	else:
		columnFilter = [DISPLAY_FLAGS_TO_COLUMNS[ c ] for c in \
						DISPLAY_FLAGS_TO_COLUMNS.keys()]


	# Enable address translation if required
	if options.translate:
		kwargs[ 'translate' ] = True


	# Find last server restart if required
	if options.last_startup:
		kwargs[ 'start' ] = SERVER_STARTUP_STRING

	# If looking for a particular server run, find its endpoints
	elif options.startup is not None:
		try:
			start = int( options.startup )
		except ValueError, ex:
			log.error( "Server startup '%s' not a number", options.startup )
			return 1

		kwargs[ 'start' ] = "%s %d" % (SERVER_STARTUP_STRING, options.startup)

	# For --back
	if options.back:

		groups = re.search( "(\d+)(\w?)", options.back ).groups()

		if not groups:
			log.error( "Could not parse history spec: %s", options.back )
			return 1

		num = int( groups[0] )

		if len( groups ) == 2:
			if groups[1].lower() == "m":
				num *= 60
			elif groups[1].lower() == "h":
				num *= 60 * 60
			elif groups[1].lower() == "d":
				num *= 60 * 60 * 24

		kwargs[ "start" ] = time.time() - num


	# For --around
	if options.around:

		if not parseTime( options.around, "start", kwargs ):
			return 1

		try:
			query = reader.createQuery( kwargs )
		except QueryParamException, ex:
			log.error( "An error occurred processing query parameters: %s.",
					str( ex ) )
			return 1

		query.setColumnFilter( columnFilter )

		results = query.fetchContext( contextLines = backContext )
		for result in results:
			result.writeToStream( sys.stdout, options.show_metadata )

		return 0

	else:
		if options.ffrom and not parseTime( options.ffrom, "start", kwargs ):
			return 1

		if options.to and not parseTime( options.to, "end", kwargs ):
			return 1

	if options.summary:
		if not checkSummaryFlags( options.summary ):
			return 1

		summary( reader, options.summary, options.summarymin, kwargs,
			options.showProgress )
		return 0

	if options.key:
		kwargs[ "metadata_key" ] = options.key
		kwargs[ "negate_metadata_key" ] = False

	elif options.negate_key:
		kwargs[ "metadata_key" ] = options.negate_key
		kwargs[ "negate_metadata_key" ] = True

	elif options.key_value_as_json:

		if not json:
			log.error( "No JSON module available. "
				"Unable to filter with JSON." )
			return 1

		try:
			key_value = json.loads( options.key_value_as_json )
		except ValueError:
			log.error( "Invalid metadata key & value pair: %s.",
					options.key_value_as_json )
			return 1

		if len(key_value) != 1:
			log.error( "Only one metadata key & value pair is allowed: %s.",
					options.key_value_as_json )
			return 1
		
		kwargs[ "metadata_key" ] = str(key_value.keys()[0])
		
		if not options.value_is_number:
			kwargs[ "metadata_value" ] = str(key_value.values()[0])
		else:
			try:
				mdValue = float(key_value.values()[0])
			except ValueError:
				log.error( "Metadata value is not a number." )
				return 1
			kwargs[ "metadata_value" ] = mdValue
		
		kwargs[ "negate_metadata_key" ] = False
		kwargs[ "negate_metadata_value" ] = False

	if options.follow:
		return not tail( reader, columnFilter, options.interval, kwargs, \
			backContext, options.show_metadata )
	else:
		# We check the context option here instead of at the top with the rest
		# of the filter options because it is used for different things in the
		# other modes
		#
		# The context parameter here is for multi-point, between-result context
		# (whereas context for tail() is is historical backwards context, and
		# context for --around is a single point in time).
		#
		# Note: context in this usage is only valid for MLDB implementations.
		# For previous usage (eg. -f and --around) context was valid for all
		# implementations.
		if (reader.dbType != log_db_constants.BACKEND_MLDB) and options.context:
			log.error ("Context can not be used in normal cat mode when using " \
				"a non-MLDB database." )
			sys.exit( 1 )

		if options.context:
			kwargs[ "context" ] = options.context

		return not cat( reader, columnFilter, kwargs, \
			showMetadata = options.show_metadata )
# main


def parseTime( s, name, kw ):
	"""
	Write the time represented by 's' as kw[ name ].
	"""

	if os.path.isfile( s ):
		t = os.stat( s ).st_mtime
		kw[ name ] = t
		log.info( "File timestamp is %s",
				  time.strftime( TIME_FMT, time.localtime( t ) ) )

	else:
		try:
			# If the time contains a decimal point, parse ms
			if "." in s:
				ms = int( s.split( "." )[1] )
				s = s.split( "." )[0]
			else:
				ms = 0

			kw[ name ] = time.mktime( time.strptime( s, TIME_FMT ) ) + \
						 (ms / 1000.0)

		except ValueError:
			log.error( "Time format must be like 'Thu 09 Nov 2006 16:09:01'" )
			return False

	return True


def cat( reader, columnFilter, kwargs, max = None, query = None, \
		 showMetadata = False ):
	"""
	Dump the contents of a user's log to stdout.  An already-started query can
	be passed in using the 'query' argument, otherwise a new one will be started
	using the kwargs.
	"""

	if not query:
		try:
			query = reader.createQuery( kwargs, resultLimit = max )
		except QueryParamException, ex:
			log.error( "An error occurred processing query parameters: %s.",
					str( ex ) )
			return 1

		if columnFilter:
			query.setColumnFilter( columnFilter )

	# Send results directly to stdout rather than returning them as part of a
	# set. This is a safety measure to prevent storing huge (potentially
	# millions) sets of log lines in memory. It also has the bonus of providing
	# instant result output from the file (rather than spending ages buffering
	# before printing anything).
	query.streamResults( sys.stdout, showMetadata = showMetadata )

	return True


def tail( reader, columnFilter, interval, kwargs, context, \
		showMetadata = False ):
	"""
	Display log output from a user's log in a similar fashion to `tail -f`.
	"""

	kwargs[ "start" ] = time.time()

	try:
		query = reader.createQuery( kwargs )
	except QueryParamException, ex:
		log.error( "An error occurred processing query parameters: %s.",
				str( ex ) )
		return 1

	if columnFilter:
		query.setColumnFilter( columnFilter )
	query.tail( sys.stdout, interval, context, showMetadata )

	return True


def checkSummaryFlags( summaryFlags ):
	invalidFlags = False

	# Validate that the flags provided are in the list of summary flags.
	# Ignores case, as capitalised flags indicate grouping.
	for f in summaryFlags:
		if not f.lower() in SUMMARY_FLAGS:
			log.error( "Invalid summary flag %s" % f )
			invalidFlags = True

	if invalidFlags:
		return False
	return True
# checkSummaryFlags


def summary( reader, flags, minThresh, kwargs, showProgress=True,
		stream=sys.stdout ):
	"""
	Display a summary of log results.
	"""

	# If interpolation isn't specified, then disable interpolation to avoid
	# stupid results.
	if "interpolate" not in kwargs:
		kwargs[ "interpolate" ] = DONT_INTERPOLATE

	# If one of the flags is capitalised, we group results by that before
	# sorting by count.
	match = re.search( "([A-Z])", flags )
	if match:
		group = SUMMARY_FLAGS[ match.group( 1 ).lower() ]
		flags = flags.lower()
	else:
		group = None

	# Make a list of the columns to be used in calculating the summary.
	histCols = [SUMMARY_FLAGS[ c ] for c in flags]

	# Validate that the column letters provided are in the map
	for c in flags:
		if not c in DISPLAY_FLAGS_TO_COLUMNS:
			log.error( "Invalid column %s" % c )

	columnFilter = [DISPLAY_FLAGS_TO_COLUMNS[ c ] for c in flags]

	try:
		query = reader.createQuery( kwargs )
	except QueryParamException, ex:
		log.error( "An error occurred processing query parameters: %s.",
				str( ex ) )
		return 1

	query.setColumnFilter( columnFilter )
	results = query.logSummary( histCols, group, showProgress=showProgress )

	if results:
		# Display results
		prevGroup = None
		countWidth = 0

		for result in results.asDicts():
			summaryText = result[ 'summaryText' ]
			count = result[ 'count' ]
			resultGroup = result[ 'group' ]

			if not countWidth:
				# Work out width for count column.
				countWidth = len( str( count ) )
				fmt = "%%%dd: %%s" % countWidth

			if count >= minThresh:

				# If we re-sorted and we're in a new section, insert some whitespace.
				if group and prevGroup and (resultGroup != prevGroup):
					print >> stream, "-" * countWidth

				stream.write( fmt % (count, summaryText ) )
				prevGroup = resultGroup


if __name__ == "__main__":
	try:
		sys.exit( main() )
	except IOError, e:
		if e.errno != 32: # Broken pipe
			raise
	except KeyboardInterrupt:
		pass
