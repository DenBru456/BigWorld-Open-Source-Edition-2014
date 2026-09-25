"""
This is a wrapper around the C++ BWLog object and should be used where possible
instead of trying to access the raw C++ API
"""

import os
import re
import sys
import time

import ConfigParser

import bwsetup; bwsetup.addPath( ".." )
from pycommon import util
from pycommon import cluster_constants
from pycommon import bwlog as bwlog_module
bwlog = bwlog_module._bwlog

import logging
log = logging.getLogger( __name__ )


class MessageLog( object ):

	# The default encoding type to use for all strings relating to message logger.
	CHARSET = "utf-8"

	# map of log output column name to mask
	OUTPUT_COLUMNS_TO_MASK = {
		"date"       : bwlog.SHOW_DATE,
		"time"       : bwlog.SHOW_TIME,
		"host"       : bwlog.SHOW_HOST,
		"serveruser" : bwlog.SHOW_USER,
		"pid"        : bwlog.SHOW_PID,
		"process"    : bwlog.SHOW_PROCS,
		"appid"      : bwlog.SHOW_APPID,
		"source"     : bwlog.SHOW_MESSAGE_SOURCE_TYPE,
		"severity"   : bwlog.SHOW_SEVERITY,
		"category"   : bwlog.SHOW_CATEGORY,
		"message"    : bwlog.SHOW_MESSAGE,
	}

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

	def __init__( self, config, logDirectory = None ):
		self.logDirectory = logDirectory or self.getDefaultLogdir( config )

		if not os.path.exists( self.logDirectory ):
			log.error( "Log directory '%s' doesn't exist", self.logDirectory )
			sys.exit( 1 )

		self.log = bwlog.BWLog( self.logDirectory )

		# This is a dict of regex objects used for translating addresses into
		# app names.  Addresses are added using addAddressTranslations().
		self.translatePatts = {}
		

	@classmethod
	def getDefaultLogdir( self, config ):
		mldir = config.get( "mldb", "mldir" )
		logdir = config.get( "mldb", "logdir" )

		if not logdir.startswith( "/" ):
			logdir = mldir + "/" + logdir

		return logdir

	# --------------------------------------------------------------------------
	# Section: C++ wrappers
	# --------------------------------------------------------------------------

	def getUsers( self ):
		return self.log.getUsers()


	def getCategoryNames( self ):
		return self.log.getCategoryNames()


	def getComponentNames( self ):
		return self.log.getComponentNames()


	def getHostnames( self ):
		return self.log.getHostnames()


	def getStrings( self ):
		return self.log.getFormatStrings()


	def getUserLog( self, uid ):
		return UserLog( self.log.getUserLog( uid ) )


	def fetch( self, **kw ):
		return Query( self.log.fetch( **kw ) )
		
	
	def refreshLogFiles( self ):
		self.log.refreshLogFiles()


	# --------------------------------------------------------------------------
	# Section: Additional functionality
	# --------------------------------------------------------------------------

	# Check the message_logger log directory for the pid file and then
	# check whether that process exists on the system.
	def isRunning( self ):

		try:
			# If the PID file exists, check if the process is running. The name
			# of the PID file is lock as it also serves as a lock to prevent
			# multiple Message Logger processes writing to the same log directory.
			pidfile = self.logDirectory + "/pid_lock"
			if os.path.exists( pidfile ):
				pfp = open( pidfile )
				pid = pfp.readline().strip()
				pfp.close()

				if os.path.exists( "/proc/" + pid ):
					return True
		except:
			pass

		return False

	def getUIDs( self ):
		return self.getUsers().values()


	def write( self, result, flags ):
		"""
		Writes a log entry to stdout.  If this log object has address
		translation enabled, this will be done first.
		"""

		self.writeTo( sys.stdout, result, flags )


	def writeTo( self, fileStream, result, flags ):

		if self.translatePatts:
			rawText = result.format( flags )
			for patt, repl in self.translatePatts.iteritems():
				rawText = patt.sub( repl, rawText )
			fileStream.write( rawText )
		else:
			fileStream.write( result.format( flags ) )


	def dump( self, query, flags = bwlog.SHOW_ALL ):
		"""
		Writes all results from a query to stdout.
		"""

		if query.inReverse():
			results = []
			for result in query:
				results.append( result )
			for result in results[::-1]:
				self.write( result, flags )
		else:
			for result in query:
				self.write( result, flags )


	def addAddressTranslations( self, uid, startup=None ):
		"""
		Fetches the nub addresses since the last server startup for the given
		uid and adds them as address translations.
		"""

		userlog = self.getUserLog( uid )

		for name, pid, address, type in userlog.getNubAddresses( startup ):
			patt = re.compile( re.escape( address ) )
			self.translatePatts[ patt ] = "@" + name


	def collect( self, *args, **kw ):
		query = self.fetch( *args, **kw )
		results = list( query )
		if query.inReverse(): results.reverse()
		return (query, results)

	def format( self, flags = bwlog.SHOW_ALL, *args, **kw ):
		query = self.fetch( *args, **kw )
		results = [result.format( flags ) for result in query]
		if query.inReverse(): results.reverse()
		return (query, results)


	def readFileList( self, filename, missingOK ):
		"""
		Reads in a file listing and returns the set of filenames.  If the file
		doesn't exist and missingOK is True, then an empty set is returned.  If
		missingOK is False, None is returned. This is currently used to read
		active_files and dirty_files.
		"""

		try:
			return set( [line.rstrip() for line in
						 open( "%s/%s" % (self.logDirectory, filename) ).readlines()] )

		except IOError, e:
			if missingOK:
				return set()
			else:
				return None


	def getActiveFiles( self ):
		"""
		Safely reads the list of active files (i.e. the list of files that are
		currently being written to).  The extra logic here is to take into
		account that if message logger is running but active_files is missing,
		message logger is halfway through rolling the logs and we should wait.
		In general, we should hardly ever hit this state since rolling logs is
		very fast.
		"""

		for i in xrange( 5 ):
			files = self.readFileList( "active_files", missingOK = False )
			if files is None and self.isRunning():
				log.warning( "active_files missing, waiting ... (%d)", i )
				time.sleep( 1 )
			elif files is not None and (self.isRunning()):
				return files
			else:
				break

		# If we got to here then we couldn't read the active_files list
		if self.isRunning():
			log.error( "Couldn't read active_files list, "
					   "logs seem to be taking a long time to roll" )
			return None

		# Getting to here means that message logger isn't running
		else:
			return set()


	def histogram( self, histCols, showProgress = False, *args, **kw ):
		"""
		Runs a query using the provided *args and **kw, but generates a
		histogram of the results instead of returning them in series.
		'histCols' is a list of the column names that should be used to form the
		keys in the histogram.

		Returns a list of tuples of the format (group, result, count).  The
		result in each tuple is the first one encountered from that group, and
		is only included so that it can be printed out nicely.
		"""

		query = self.fetch( *args, **kw )

		# We don't show progress for less than 10000 results
		entryCount = query.getProgress()[1]
		showProgress = showProgress and entryCount > 10000

		# A mapping of groupkey -> [result, count]
		groups = {}

		# Initialise progress
		if showProgress:
			progress = util.PercentComplete(
				"Processing %d messages" % entryCount, entryCount )

		for result in query:

			# Work out which hash bucket this result falls into.  We have to
			# convert to a tuple because lists are unhashable.
			group = tuple( [getattr( result, col ) for col in histCols] )

			# Increment count for that group
			rec = groups.setdefault( group, [result, 0] )
			rec[1] += 1

			# Update progress
			if showProgress:
				progress.update( query.getProgress()[0] )

		if showProgress:
			progress.update( entryCount )

		return sorted( groups.values(),
					   key = lambda (result, count): count,
					   reverse = True )


	def componentID( self, name ):
		"""
		Returns the component ID for the provided component name in this log.
		If the component ID is n, you need to pass (1 << n) in the 'procs' kwarg
		of fetch() to search for this component.
		"""

		names = self.getComponentNames()
		for i, n in enumerate( names ):
			if name.lower() == n.lower():
				return i
		raise KeyError, "Process %s does not exist in this log" % name


	def fetchContext( self, kwargs, max = 20, period = None,
					  contextTimeout = 3.0 ):
		"""
		Utility method useful for implementing `tail -f` like functionality,
		where you want to have some prior context for a query before returning
		the up-to-date results.  At the moment this only supports context that
		is backwards in time, i.e. you can't get context for a query that is
		going to run in the backwards direction.

		If you want to restrict the time window the context can be extracted
		from, pass 'period' as something like '-3600' (for 1 hour back in time).

		The return value is a list of results and a query positioned immediately
		after the last returned result.
		"""

		kw = kwargs.copy()
		kw[ "period" ] = period or "to beginning"

		# Cap time spent searching for context for potentially sparse queries
		def fetchContextTimeout( query ):
			log.warning( "Context lookup took longer than %.1f seconds",
						 contextTimeout )
			raise RuntimeError

		query = self.fetch( **kw )
		query.setTimeout( contextTimeout, fetchContextTimeout )
		resumePos = query.tell()
		results = query.get( max )
		if len( results ):
			results = reversed( results )

			# Start new query but jump over first position since we've already
			# searched it
			kwargs[ "startaddr" ] = resumePos
			query = self.fetch( **kwargs )
			query.step( bwlog.FORWARDS )

			return (results, query)

		# If we couldn't even get one line of context, just return original search
		else:
			return ([], self.fetch( **kwargs ))


class Query( object ):

	def __init__( self, query ):
		self.query = query

	# --------------------------------------------------------------------------
	# Section: C++ wrappers
	# --------------------------------------------------------------------------

	def get( self, *args ):
		return self.query.get( *args )

	def inReverse( self ):
		return self.query.inReverse()

	def getProgress( self ):
		return self.query.getProgress()

	def resume( self ):
		return self.query.resume()

	def tell( self, *args ):
		return self.query.tell( *args )

	def seek( self, *args ):
		return self.query.seek( *args )

	def step( self, *args ):
		return self.query.step( *args )

	def setTimeout( self, *args ):
		return self.query.setTimeout( *args )

	def __iter__( self ):
		return self.query.__iter__()

	# --------------------------------------------------------------------------
	# Section: Additional Functionality
	# --------------------------------------------------------------------------

	def hasMoreResults( self ):
		seen, total = self.getProgress()
		return seen < total

	def waitForResults( self, timeout = 0.5 ):
		while not self.hasMoreResults():
			time.sleep( timeout )
			self.resume()


class UserLog( object ):

	def __init__( self, userLog ):
		self.userLog = userLog
		self.uid = userLog.uid
		self.username = userLog.username

	def getSegments( self ):
		return [Segment( *tup ) for tup in self.userLog.getSegments()]

	def getComponents( self ):
		return [Component( self, *tup )	for tup in self.userLog.getComponents()]

	def getEntry( self, entryAddress ):
		return self.userLog.getEntry( entryAddress )


	@staticmethod
	def isServerStartup( component, entry ):
		"""
		Returns true if this component and entry are for a server startup.
		"""

		return component.name == cluster_constants.MESSAGE_LOGGER_NAME and \
			   entry.message == "Starting server"


	def getAllServerStartups( self ):
		"""
		Returns a list of (entry, addr) tuples for this user's server startups.
		"""

		startups = []

		for component in self.getComponents():

			entry = component.getFirstEntry()

			if entry and UserLog.isServerStartup( component, entry ):
				startups.append( (entry, component.firstEntry) )

		return startups


	def getLastServerStartup( self ):

		for component in self.getComponents()[::-1]:

			entry = component.getFirstEntry()

			# This can happen if the segment has been rolled away.  If it has,
			# then we don't need to keep searching through the rest of the
			# components, just start from the beginning of the log, since it
			# must be later than the last server restart
			if entry is None:
				break

			if UserLog.isServerStartup( component, entry ):
				return dict( entry = entry, addr = component.firstEntry )

		return None


	def getLastMatchingMessage( self, message = "", **kw ):
		"""
		Runs the query given by the keyword args in reverse and returns the
		address of the first match.
		"""

		kw[ "start" ] = bwlog.LOG_BEGIN
		kw[ "end" ] = bwlog.LOG_END
		kw[ "direction" ] = bwlog.BACKWARDS
		kw[ "message" ] = re.escape( message )

		query = self.userLog.fetch( **kw )
		results = query.get( 1 )

		if results:
			# BACKWARDS here is relative to the direction of the search, unlike above
			query.step( bwlog.BACKWARDS )
			return query.tell()

		else:
			return None


	def getNubAddresses( self, startup = None ):
		"""
		Returns a list of tuples of (app name, pid, nub address, nub type) for
		each nub created since the last server startup.
		"""

		if startup is None:
			lastStartup = self.getLastServerStartup()
			if lastStartup:
				startup = lastStartup[ "addr" ]
		components = []
		results = []

		for c in sorted( self.getComponents() ):
			if not startup or c.firstEntry >= startup:
				components.append( c )

		for c in components:
			# if cannot find the first entry, maybe it is rolled, just continue
			if not c.firstEntry or not c.getFirstEntry():
				continue
			# 'end' is given as 5 seconds after app startup because all known
			# apps bind their nubs at startup.
			query = self.userLog.fetch( startaddr = c.firstEntry,
									end = c.getFirstEntry().time + 5,
									pid = c.pid,
									uid = self.uid,
									severities = 1 << bwlog_module.MESSAGE_PRIORITY_INFO,
									message = "address.*=",
									casesens = False,
									interpolate = bwlog.PRE_INTERPOLATE,
									categories = ( 'ProcessIP', ) )

			for result in query:

				if result.appid:
					name = "%s%02d" % (result.component, result.appid)
				else:
					name = result.component

				match = re.search( "(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d+)",
									result.message )
				if match == None:
					continue

				address = match.group( 1 )

				if re.search( "external", result.message, re.I ):
					nubtype = "external"
				else:
					nubtype = "internal"

				results.append( (name.lower(), result.pid, address, nubtype) )

		return sorted( results )


class Segment( object ):

	FMT = "%-23s %10s %16s %8s"

	def __init__( self, suffix, start, end, nEntries, entriesSize, argsSize ):
		self.suffix = suffix
		self.start = start
		self.end = end
		self.nEntries = nEntries
		self.entriesSize = entriesSize
		self.argsSize = argsSize

	def __str__( self ):
		return self.FMT % \
			   (self.suffix, util.fmtSeconds( self.end - self.start ),
				self.nEntries,
				util.fmtBytes( self.entriesSize + self.argsSize ))


class Component( object ):

	def __init__( self, userLog, name, pid, id, firstEntry ):
		self.userLog = userLog
		self.name = name
		self.pid = pid
		self.id = id
		self.firstEntry = firstEntry

	def __str__( self ):
		return "%-12s (pid:%d) (id:%d)" % (self.name, self.pid, self.id)

	def __cmp__( self, c ):
		return cmp( self.name, c.name ) or \
			   cmp( self.id, c.id ) or \
			   cmp( self.pid, c.pid )

	def getFirstEntry( self ):
		return self.userLog.getEntry( self.firstEntry )

# message_log.py
