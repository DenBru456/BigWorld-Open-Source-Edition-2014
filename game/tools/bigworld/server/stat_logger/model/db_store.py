import operator
import collections
import itertools
import threading
import time
import Queue
import logging


import utilities
import constants
import comparepref

from data_store import DataStore
from dbmanager import DbManager, LogDbError, LogDbValidateError

# Logging module
log = logging.getLogger( __name__ )


class DbStore( DataStore ):
	""" Interface to write statistics to backend database """

	# How frequently (in seconds) tables should be optimised.
	# This is a low priority task to help reclaim disk space.
	# Defaults to: 43200 (every 12 hours)
	OPTIMISE_FREQUENCY = 43200

	def __init__( self, dbStoreConfig, sampleTickInterval, prefTree,
				allowCreate, dbName, useDbPrefs ):
		DataStore.__init__( self, dbStoreConfig, prefTree )

		self.dbManager = DbManager( dbStoreConfig )

		self.sampleTickInterval = sampleTickInterval
		self.allowCreate = allowCreate
		self.dbName = dbName
		self.useDbPrefs = useDbPrefs

		# Process database ids (Machines use ip integer as their id)
		self.dbIds = {}

		# Last time (in seconds since Epoc) that the tables were
		# optimised. Defaulting to 0 ensures that every startup
		# will see the tables optimised.
		self.lastOptimised = 0

		# Warning thresholds (go above these and we start printing warnings)
		self.warnDumpQueueSize = 500
		self.warnSQLTime = 3.0
		
		# connect to DB and grab out preference tree if necessary
		self.prefTree = self._connectToLogDb()

		# Map of Process.name -> ProcPref
		self.nameToProcPref = \
			dict( (pref.matchtext, pref) for pref in \
				self.prefTree.iterProcPrefs() )

		self.dbManager.addSessionStart()

		# start the dumper thread
		self.statDumper = StatDumper( self.dbManager.cloneWithNewConnection() )
		self.statDumper.setDaemon( True )
		self.statDumper.start()
	# __init__


	# -------------------------------------------------------------------------
	# Section: exposed methods, inherited from DataStore
	# (virtual ones in DataStore)
	# -------------------------------------------------------------------------
	def finalise( self, quickTerminate = True ):
		self.dbManager.endSession()
		self.dbManager.close()

		self.statDumper.pushFinish( quickTerminate )
		log.debug( "Waiting for StatDumper to terminate..." )
		self.statDumper.join(60.0)
	# finalise


	def isOk( self ):
		if not self.statDumper.isAlive():
			log.error( "Error: StatDumper thread died unexpectedly, "\
				"stopping Gather thread." )
			return False

		# Note: Following two lines are unthreadsafe, I'm relying on Python's
		# global interpreter lock here
		queueSize = len(self.statDumper.generalQueue)
		delQueueSize = len(self.statDumper.deleteQueue)
		if queueSize > self.warnDumpQueueSize:
			log.warning( "Queue size is larger than %d (now %d)",
				self.warnDumpQueueSize, queueSize )
		queryInfo = self.statDumper.getCurrentQueryInfo()
		if queryInfo and queryInfo[1] > self.warnSQLTime:
			log.warning( "Currently stuck on query: %s (taken %.3fs so far)",
				queryInfo[ 0 ], queryInfo[ 1 ] )

		return True
	# isOk


	@classmethod
	def testConnection( cls, dbStoreConfig ):
		return DbManager.testConnection( dbStoreConfig )
	# testConnection


	def logNewMachine( self, machine ):
		""" Adds machine info to the database if it doesn't already exist """
		ipInt = utilities.ipToInt( machine.ip )
		c = self.dbManager.getCursor()
		# Seach the database first, and grab the name stored in the database
		c.execute( "SELECT ip, hostname FROM %s WHERE ip=%%s" %
				(constants.tblSeenMachines), ipInt )
		results = c.fetchone()
		if results:
			# We found a corresponding entry, compare the name
			name = results[ 1 ]
			if machine.name and name != machine.name:
				# Name is different, update name change in the database
				log.info( "Machine name %s is different to stored name %s! "\
					"Updating...", machine.name, name )
				c.execute( "UPDATE %s SET hostname=%%s WHERE ip=%%s" % \
					(constants.tblSeenMachines), (machine.name, ipInt) )
			else:
				log.info( "Retrieved machine %s (%s) from database",
					name, machine.ip )
		else:
			log.info( "Adding machine %s (%s)", machine.name, machine.ip )
			c.execute( "INSERT INTO %s (ip, hostname) VALUES (%%s, %%s)" % \
					(constants.tblSeenMachines), (ipInt, machine.name) )
		c.close()
	# logNewMachine


	def logNewProcess( self, process, userName ):
		""" Adds process info to the database if it doesn't already exist """
		ipInt = utilities.ipToInt( process.machine.ip )
		procPref = self.nameToProcPref[process.name]
		c = self.dbManager.getCursor()
		c.execute("SELECT id FROM %s "
					"WHERE machine = %%s AND pid = %%s AND name = %%s" \
				% (constants.tblSeenProcesses),
			(ipInt, process.pid, process.label()) )
		results = c.fetchone()

		if results:
			# Great! We already found our process then
			dbId = results[0]
			log.info( "Retrieved process %s (user:%s, pid:%d, host:%s) from " \
				"database (dbid %d)", process.label(), userName,
				process.pid, process.machine.name, dbId )
		else:
			c.execute( "INSERT INTO %s "\
				"(machine, userid, name, processPref, pid) "\
				"VALUES (%%s, %%s, %%s, %%s, %%s)" \
				% (constants.tblSeenProcesses),
					(ipInt, process.uid, process.label(), procPref.dbId,
					process.pid) )
			dbId = c.connection.insert_id()
			log.info( "Added process %s (user:%s, pid:%d, host:%s)"\
					" to database. (dbid %d)",
				process.label(), userName, process.pid,
				process.machine.name, dbId )
		self.dbIds[process] = dbId
		c.close()
	# logNewProcess


	def logNewUser(self, user):
		""" Adds user info to the database if it doesn't already exist """
		if not hasattr( user, "uid" ):
			log.warning( "User object %%s has no attribute uid" % (user) )
			return

		c = self.dbManager.getCursor()
		c.execute( "SELECT name FROM %s WHERE uid = %%s" \
			% (constants.tblSeenUsers), user.uid )

		# If the user hasn't been logged to the database, do it now
		if c.rowcount == 0:
			c.execute( "INSERT INTO %s (uid, name)" "VALUES (%%s, %%s)" % \
					(constants.tblSeenUsers), (user.uid, user.name) )
		c.close()
	# logNewUser


	def logMachineStats( self, machineStats, tick ):
		""" Logs stats for all machines """
		baseWindowId = self.prefTree.windowPrefs[0].dbId
		table = "%s_lvl_%03d" % (constants.tblStatMachines, baseWindowId)
		values = []
		columns = ["tick", "machine"]
		columns.extend( pref.columnName for pref in 
				self.prefTree.iterMachineStatPrefs() )
		for m, statDict in machineStats.iteritems():
			ipInt = utilities.ipToInt( m.ip )
			row = [tick, ipInt]
			row.extend( (statDict[pref] for pref \
				in self.prefTree.iterMachineStatPrefs()) )
			values.append( row )

		self.statDumper.pushInsert( table, columns, values )
	# logMachineStats


	def logProcessStats( self, processStats, tick ):
		""" Logs stats for all processes """
		getName = operator.attrgetter( 'name' )
		baseWindowId = self.prefTree.windowPrefs[0].dbId
		assert baseWindowId >= 0
		processes = itertools.groupby(
			sorted( processStats.iterkeys(), key=getName), getName )

		# Go through each process type and construct an insert
		# command for each one
		for procName, procList in processes:
			procPref = self.nameToProcPref[ procName ]
			values = []
			columns = [ "tick", "process" ]
			columns.extend( pref.columnName for pref in \
				procPref.iterAllStatPrefs() )
			table = "%s_lvl_%03d" % ( procPref.tableName, baseWindowId )

			procList = list( procList )
			for p in procList:
				statDict = processStats[p]
				row = [ tick, self.dbIds[p] ]
				row.extend( statDict.get(pref, None) for pref \
					in procPref.iterAllStatPrefs() )
				values.append( row )

			#log.debug( "Adding stats for %s, %d rows", table, len(values) )
			self.statDumper.pushInsert( table, columns, values )
	# logProcessStats


	def delProcess( self, process ):
		del self.dbIds[ process ]
	# delProcess


	def consolidateStats( self, tick, shouldLimitDeletion=True ):
		"""
		Consolidate statistics for all machines and processes

		@param shouldLimitDeletion True if deletion should be limited to
			StatDumper.deleteSize and consolidation should be performed;
			else false.

		"""
		# Iterate through all windows
		for windowPref in self.prefTree.windowPrefs:
			windowId = windowPref.dbId
			samples = windowPref.samples
			samplePeriodTicks = windowPref.samplePeriodTicks
			tickFrom = tick - samplePeriodTicks
			tickTo = tick
			keepStatThreshold = int(tick - (samples * samplePeriodTicks))

			# Consolidate from the window below into the current one
			if tick % samplePeriodTicks != 0:
				continue

			# To avoid allowing the DB size to grow out of control, we
			# remove older statistics.
			if keepStatThreshold > 0:
				# Remove old rows from process statistics
				for procPref in self.prefTree.iterProcPrefs():
					table = "%s_lvl_%03d" % (procPref.tableName, windowId)
					self.statDumper.pushDeleteBefore( table,
							"tick", keepStatThreshold, shouldLimitDeletion )
					if self._shouldOptimise():
						self.statDumper.pushOptimiseTable( table )

				# Remove old rows from machine statistics
				table = "%s_lvl_%03d" % (constants.tblStatMachines, windowId)
				self.statDumper.pushDeleteBefore( table, "tick",
					keepStatThreshold, shouldLimitDeletion )
				if self._shouldOptimise():
					self.statDumper.pushOptimiseTable( table )

				# Remove unused ticks no longer referenced by any window
				if windowPref == self.prefTree.windowPrefs[-1]:
					table = constants.tblStdTickTimes
					self.statDumper.pushDeleteBefore( table,
						"id", keepStatThreshold, shouldLimitDeletion )
					if self._shouldOptimise():
						self.statDumper.pushOptimiseTable( table )

				# If we've performed the optimisation, reset the timer
				if self._shouldOptimise():
					self.lastOptimised = time.time()

			if ((windowId == 1) or (not shouldLimitDeletion)):
				continue

			# Consolidate machine statistics
			tableTo = "%s_lvl_%03d" % (constants.tblStatMachines, windowId)
			tableFrom = "%s_lvl_%03d" % (constants.tblStatMachines, windowId-1)
			groupColumn = "machine"
			columns= [pref.columnName for pref in \
				self.prefTree.iterMachineStatPrefs()]
			aggregators = [pref.consolidateColumn() for pref in \
				self.prefTree.iterMachineStatPrefs()]
			self.statDumper.pushConsolidate( tableFrom, tableTo, groupColumn,
				columns, aggregators, tickFrom, tickTo )

			# Consolidate process statistics
			for procPref in self.prefTree.iterProcPrefs():
				tableTo = "%s_lvl_%03d" % (procPref.tableName, windowId)
				tableFrom = "%s_lvl_%03d" % (procPref.tableName, windowId - 1)
				groupColumn = "process"
				columns = [pref.columnName for pref in \
							procPref.iterAllStatPrefs()]
				aggregators = [pref.consolidateColumn() for pref in \
							procPref.iterAllStatPrefs()]
				self.statDumper.pushConsolidate( tableFrom, tableTo,
					groupColumn, columns, aggregators, tickFrom, tickTo )
	# consolidateStats


	def addTick( self, tick, tickTime ):
		return self.dbManager.addTickToDb( tick, tickTime )
	# addTick


	# ------------------------------------------------------
	# Section: other exposed methods
	# ------------------------------------------------------
	def retrieveLatestTime( self ):
		""" Grab the last tick out of the database """
		cursor = self.dbManager.getCursor()
		cursor.execute( "SELECT id, time FROM %s "\
			"ORDER BY time DESC LIMIT 1" % constants.tblStdTickTimes )
		if cursor.rowcount > 0:
			lastTick, lastTime = cursor.fetchone()
			lastTime = float( lastTime ) / 1000
		else:
			lastTime = None
		cursor.close()
		return lastTime
	# retrieveLatestTime


	def getFirstTick( self ):
		return self.dbManager.getFirstTick()
	# getFirstTick


	def printLogList( self ):
		"""
		Prints a list of log databases.
		"""
		try:
			results = self.dbManager.getLogDbList( allowCreate=False )
		except LogDbError, e:
			if e.code == LogDbError.ERR_NOLOGDB:
				log.info( "No logs exist." )
			else:
				raise
			return

		if len( results ) == 0:
			log.info( "No logs exist." )
			return

		def boolToChar( val ):
			if val:
				return "Yes"
			else:
				return "No"

		for name, created, used, active, users in results:
			print "Name     : ", name
			print "Created  : ", utilities.formatTime( created )
			print "Last used: ", utilities.formatTime( used )
			print "Active   : ", boolToChar( active )
			print
	# printLogList


	def getPrefTree( self ):
		return self.prefTree
	# getPreTree


	# ------------------------------------------------------
	# Section: internal methods
	# ------------------------------------------------------	
	def _connectToLogDb( self ):
		"""
		Connect to a log database.
		"""
		logDbPrefTree = None
		try:
			self.dbManager.connectToLogDb( self.dbName )
			logDbPrefTree = self.dbManager.getLogDbPrefTree()
			if not self.useDbPrefs:
				comparepref.comparePrefTreesWithError( self.prefTree,
								logDbPrefTree )

			# Different tick time
			logDbInterval = self.dbManager.getLogDbInterval()
			if logDbInterval != self.sampleTickInterval:
				log.info( "Mismatch between preference file and database:" )
				log.info( "  - Interval is different (file %f, db %f)",
					self.sampleTickInterval, logDbInterval )
				logDbPrefTree = self._createLogDb()

			# Different database version
			logDbVersion = self.dbManager.getLogDbVersion()
			if logDbVersion != constants.dbVersion:
				log.info( "The database structure is incompatible with " \
					"the current structure. (Old version: %s, New version: %s)",
					logDbVersion, constants.dbVersion )
				logDbPrefTree = self._createLogDb()

		# Errors which occurred trying to connect to db
		except LogDbError, e:
			if e.code == LogDbError.ERR_NOLOGDB:
				log.warning( "WARNING: %s.", e.msg )
				logDbPrefTree = self._createLogDb( alreadyExists = False )

			elif e.code == LogDbError.ERR_NOACCESS:
				log.error( "ERROR: %s.", e.msg )
				log.error( " - Either the database permissions have not been " \
					"set, or the 'user' setting of 'database' was misspelled" \
					" in configuration file." )
				raise AbortConnect()

			elif e.code == LogDbError.ERR_BAD_NAME_PASSWORD:
				log.error( "ERROR: %s.", e.msg )
				log.error( " - Please check the 'user' and 'password'" \
					" setting of 'database' in configuration file." )
				raise AbortConnect()
			
			elif e.code == LogDbError.ERR_NOSQLSERVER:
				log.error( "ERROR: %s.", e.msg )
				log.error( " - Please check the 'host' and 'port' setting "\
					"of 'database' in configuration file." )
				raise AbortConnect()

		# Db table structure validation error
		except LogDbValidateError, e:
			log.error( "ERROR: Database did not validate:" )
			e.printErrors("  -")
			logDbPrefTree = self._createLogDb()

		# Preference matching error
		except comparepref.PrefMatchError, e:
			log.error( "ERROR: Mismatch between preference file and database:" )
			e.printErrors("  -")
			logDbPrefTree = self._createLogDb()

		return logDbPrefTree
	# _connectToLogDb


	def _createLogDb( self, alreadyExists = True ):
		"""
		Create a new log database.
		"""
		log.info( "Attempting to create new database..." )
		if not self.allowCreate:
			log.info( "Cannot create new database: \"-p\" option specified." )
			raise AbortConnect()
		elif self.dbName and alreadyExists:
			log.info( "Database \"%s\" cannot be used, aborting.",
				self.dbManager.logDbName )
			raise AbortConnect()
		else:
			self.dbManager.createLogDb( self.dbName, self.prefTree,
						self.sampleTickInterval )
			logDbPrefTree = self.dbManager.getLogDbPrefTree()
		return logDbPrefTree
	# _createLogDb


	def _shouldOptimise( self ):
		return (time.time() - self.lastOptimised) > self.OPTIMISE_FREQUENCY
	# _shouldOptimise
# DbStore

class AbortConnect( Exception ):
	""" Exception when we can't connect to the database. """
	pass

# ------------------------------------------------------------------------------
# Section: SQL statistic dumping class
# ------------------------------------------------------------------------------

class StatDumper( threading.Thread ):
	"""
	Statistics dumping thread.
	"""
	INSERT = 0
	DELETE = 1
	CONSOLIDATE = 2
	FINISH = 3
	OPTIMISE = 4

	def __init__( self, dbManager ):
		threading.Thread.__init__( self, name="StatDumper" )
		self.messageQueue = Queue.Queue()

		# Information on current database query
		self.currentQuery = None
		self.currentQueryStart = None

		# General command queues
		self.generalQueue = collections.deque()
		self.deleteQueue = collections.deque()

		# Rows to delete at a time
		self.deleteSize = 20
		self.sleepTime = 0.1
		self.warnSQLTime = 1.0

		# Database manager, interface to deal with Database
		self.dbManager = dbManager
		self.cursor = self.dbManager.getCursor()

		# Set to true here if profiling StatDumper thread
		self.profiling = False
	# __init__
	
	class FinishException( Exception ):
		pass


	# -------------------------------------------------------------
	# Exposed functions
	# -------------------------------------------------------------
	def pushDeleteBefore( self, table, col, cutoff, shouldLimitDeletion=True):
		"""
		Adds a delete command to delete rows from a table.

		@param table: Name of table to delete from
		@param col: Name of column which will be used to determine which
			values to delete
		@param cutoff: Value for which a row will be deleted if its
			column has a value below this.
		@param shouldLimitDeletion: True if the number of rows deleted should be
			limited; else False.
		"""
		self.messageQueue.put(
			(self.DELETE, (table, col, cutoff, shouldLimitDeletion)) )
	# pushDeleteBefore


	def pushOptimiseTable( self, table ):
		self.messageQueue.put( (self.OPTIMISE, (table)) )
	# pushOptimiseTable


	def pushInsert( self, table, columns, values ):
		"""
		Adds an insert command to the queue.

		@param tables: Name of table to insert values into.
		@param columns: List of columns in the table corresponding to
			the values being inserted.
		@param values: List of value tuples being inserted.
		"""
		self.messageQueue.put( (self.INSERT, (table, columns, values)) )
	# pushInsert


	def pushConsolidate( self, tableFrom, tableTo, groupColumn, columns,
			aggregators, tickFrom, tickTo ):
		"""
		Adds a consolidate command to the queue

		@params tableFrom:   Table name from which consolidation starts.
		@params tableTo:     Table to which consolidated data is placed.
		@params groupColumn: The column on which the rows are grouped
		@params columns:     List of column stat names
		@params aggregators: Database functions to aggregate the data. Should
			correpond to the columns parameter.
		@params tickFrom:    The start tick
		@params tickTo:      The end tick
		"""
		self.messageQueue.put( (self.CONSOLIDATE, (tableFrom, tableTo,
			groupColumn, columns, aggregators, tickFrom, tickTo)) )
	# pushConsolidate


	def pushFinish( self, quick=False ):
		"""
		Adds a terminate command to the queue

		@param quick: True if we should stop immediately upon
			processing this command, False if we should wait until all
			SQL command queues are empty.
		"""
		self.messageQueue.put( (self.FINISH, quick) )
	# pushFinish


	def getCurrentQueryInfo( self ):
		""" Returns information on the current SQL query. """
		currentQueryStart = self.currentQueryStart
		if currentQueryStart != None:
			return (self.currentQuery, time.time() - currentQueryStart)
		else:
			return None
	# getCurrentQueryInfo


	# -------------------------------------------------------------
	# Internal functions
	# -------------------------------------------------------------
	def _processMessage( self, msgTuple ):
		"""Handle messages passed to us from the Gather thread."""
		msg, params = msgTuple
		if msg == self.INSERT:
			self.generalQueue.appendleft( msgTuple )

		elif msg == self.CONSOLIDATE:
			self.generalQueue.appendleft( msgTuple )

		elif msg == self.OPTIMISE:
			self.generalQueue.appendleft( msgTuple )

		elif msg == self.DELETE:
			found = False
			table, column, cutoff, shouldLimitDeletion = params
			# Try to update the entry in deleteQueue if we already have
			# a delete scheduled for the same table
			for i in range(len(self.deleteQueue)):
				if table == self.deleteQueue[i][0]:
					oldTable, oldColumn, oldCutoff, shouldLimitDeletion = \
						self.deleteQueue[i]
					self.deleteQueue[i] = oldTable, oldColumn, cutoff, shouldLimitDeletion
					log.debug( "Extended existing delete command on %s "\
						"from %s to %s", table, oldCutoff, cutoff )
					found = True
					break
			if not found:
				self.deleteQueue.appendleft( params )

		elif msg == self.FINISH:
			quick = params
			if not quick:
				self._processGeneralQueue( entireQueue=True )
			raise self.FinishException()

		else:
			raise Exception("StatDumper: Got unknown message %s" % (msg))
	# _processMessage


	def _constructDeleteSQL( self, table, col, cutoff, shouldLimitDeletion ):
		"""
		Constructs the SQL statement for an insert command.
		Params correspond to those for pushDelete().
		"""
		sql = "".join( ("DELETE FROM ", table, " WHERE ",
			col, " < ", str( cutoff ) ) )

		if shouldLimitDeletion:
			sql = "".join( (sql, " LIMIT ", str( self.deleteSize)) )

		return sql
	# _constructDeleteSQL


	def _constructInsertSQL( self, table, columns, values ):
		"""
		Constructs the SQL statement for an insert command.
		Params correspond to those for pushInsert()
		We use str.join() a lot here because it's the fastest method
		of string concatenation. It's not as bad as it looks, really.
		"""
		if not values:
			return None
		conv = self.cursor._get_db().literal
		sqlValues = ",".join(
			"".join( ("(", ",".join( conv(v) for v in row ), ")") )
			for row in values )
		sqlColumns = ",".join(columns)
		sql = "".join( ("INSERT INTO ", table, "(", sqlColumns, ") VALUES ",
				sqlValues) )
		return sql
	# _constructInsertSQL


	def _constructOptimiseSQL( self, table ):
		"""
		Constructs SQL for optimising a table after deletions.
		http://dev.mysql.com/doc/refman/5.0/en/optimize-table.html
		"""

		return "".join( ("OPTIMIZE TABLE ", table) )
	# _constructOptimiseSQL


	def _constructConsolidateSQL( self, tableFrom, tableTo, groupColumn,
							columns, aggregators, tickFrom, tickTo ):
		"""
		Construct consolidation SQL query.
		We don't use str.join as much here because it'd be far too messy.
		Params correspond to those for pushConsolidate()
		"""

		assert len(columns) == len(aggregators), \
			"Expected columns to be the same length as aggregators"

		conv = self.cursor._get_db().literal
		aggregatedColumns = ",".join( "".join( (
			a, "(", c, ")") ) for a,c in zip(aggregators, columns) )
		tickFrom = int(tickFrom)
		tickTo = int(tickTo)

		sql = """INSERT INTO %s(%s) SELECT
			%s AS currentTick,
			-- Current tick
			stat.%s,
			-- Aggregated columns
			%s
			FROM %s AS stat WHERE stat.tick >= %s AND stat.tick < %s
			GROUP BY stat.%s
			""" % ( tableTo, ",".join(["tick", groupColumn] + ( columns )),
				conv( tickFrom ),
				groupColumn,
				",".join(columns),
				tableFrom, conv( tickFrom ), conv( tickTo ),
				groupColumn)

		return sql
	# _constructConsolidateSQL


	def _processGeneralQueue( self, entireQueue=False ):
		""" Handle our general database query queue """
		reportInterval = 1.0
		lastReport = time.time()
		if entireQueue:
			log.debug( "Beginning full SQL queue dump, %d batches left" % \
					(len(self.generalQueue)) )
		while self.generalQueue:
			msg, params = self.generalQueue.pop()
			if msg == self.INSERT:
				sql = self._constructInsertSQL( *params )
			elif msg == self.CONSOLIDATE:
				sql = self._constructConsolidateSQL( *params )
			elif msg == self.OPTIMISE:
				sql = self._constructOptimiseSQL( params )
			self._timedSQLQuery( sql )
			if not entireQueue:
				break
			if time.time() - lastReport > reportInterval:
				log.info( "Processing entire queue, %d batches left" % \
					(len(self.generalQueue)) )
	# _processGeneralQueue


	def _processDeleteQueue( self, entireQueue=False ):
		""" Handle our low priority delete queue """
		while self.deleteQueue:
			params = self.deleteQueue[-1]
			sql = self._constructDeleteSQL( *params )

			numDeleted = self._timedSQLQuery( sql )

			if params[-1]:
				# numDeleted is enforced to be at most self.deleteSize
				# by the SQL 'LIMIT' command. See _constructDeleteSQL()
				if numDeleted < self.deleteSize:
					self.deleteQueue.pop()
			else:
				self.deleteQueue.pop()

			if not entireQueue:
				break
	# _processDeleteQueue


	def _timedSQLQuery( self, sql, args=None ):
		"""
		Performs an SQL query. If time exceeds a certain
		threshold, print a warning message.
		"""
		if args == None:
			self.currentQuery = sql
		else:
			conv = self.cursor._get_db().literal
			self.currentQuery = sql % tuple( conv(a) for a in args )

		self.currentQueryStart = time.time()
		results = self.cursor.execute( self.currentQuery )
		timeTaken = time.time() - self.currentQueryStart
		showSQL = False
		if timeTaken > self.warnSQLTime:
			log.warning( "Query took (%.3fs, %d rows):",
				timeTaken, self.cursor.rowcount )
			showSQL = True
		numWarnings = self.cursor._warnings
		if numWarnings > 0:
			log.warning( "We got %d warnings", numWarnings )
			showSQL = True
		if showSQL:
			log.warning( self.currentQuery )

		self.currentQueryStart = None
		self.currentQuery = None
		return self.cursor.rowcount
	# _timedSQLQuery


	def run( self ):
		""" Thread entry point """
		if self.profiling:
			import cProfile
			prof = cProfile.Profile()
			prof.runcall( self._runDumper )
			prof.dump_stats( "stat_logger_dumper.prof" )
			log.debug( "Dumped profile statistics to stat_logger_dumper.prof" )
		else:
			self._runDumper()
	# run


	def _runDumper( self ):
		""" Start the main StatDumper loop """
		try:
			while True:
				if (not self.generalQueue) and (not self.deleteQueue):
					# If both queues are empty, sleep for a bit
					# (should be a really small amount)
					time.sleep( self.sleepTime )
				else:
					# Process both queues. Deleting goes first, since
					# inserting extra values might make the database
					# seach longer to find the rows to delete (just
					# being paranoid, it probably makes minimal difference)
					self._processDeleteQueue()
					self._processGeneralQueue()

				# Process message queue
				while not self.messageQueue.empty():
					self._processMessage( self.messageQueue.get(0) )

		except self.FinishException:
			pass

		self.dbManager.close()

		log.info( "StatDumper thread terminating normally" )
	# _runDumper


# StatDumper
