import MySQLdb
import MySQLdb.converters
import _mysql_exceptions
import time
import logging

import constants
import validatedb
import createdb
import readdbpref
import utilities


log = logging.getLogger( __name__ )

# ------------------------------------------------------------------------------
# Section: DbManager
# ------------------------------------------------------------------------------

class DbManager( object ):
	"""
	The main database logic class which
	performs the following:

	- 	Validation of database table structure
	- 	Listing of log databases
	- 	Creation of log databases, including auto generation
	 	of the tables and the database name
	"""

	def __init__( self, dbStoreConfig ):
		"""Constructor."""
		self.dbStoreConfig = dbStoreConfig
		self.enabled = dbStoreConfig.enabled
		self.dbUser = dbStoreConfig.user
		self.dbHost = dbStoreConfig.host
		self.dbPort = dbStoreConfig.port
		self.dbPass = dbStoreConfig.password
		self.dbPrefix = dbStoreConfig.prefix
		self.infoTblChecked = False
		self.logDbName = ""

		self._sessionDbId = None
		self._dbConn = None
		self._currentDbName = ""

		self.prefFilePath = None

	
	def setPrefFilePath( self, prefFilePath ):
		self.prefFilePath = prefFilePath


	def getCursor( self ):
		cursor = self._useDb( self.logDbName )
		return cursor

	getLogDbCursor = getCursor


	def getLogDbList( self, allowCreate = True ):
		cursor = self._useInfoDb( allowCreate )
		cursor.execute( "SELECT name FROM %s" % (constants.tblInfo) )
		names = cursor.fetchall()

		cursor.execute( "SHOW DATABASES" )
		existResults = cursor.fetchall()
		cursor.close()

		existSet = set()
		for exist in [e[0] for e in existResults]:
			existSet.add( exist )

		results = []
		for name in [n[0] for n in names]:
			if name not in existSet or not name.startswith( self.dbPrefix ):
				continue
			created, used, active, users = self._getInfoAboutLogDb( name )
			results.append( (name, created, used, active, users) )
		return results

	def getLogDbInterval( self, name = None ):
		if not name:
			name = self.logDbName

		cursor = self._useDb( name )
		cursor.execute( "SELECT sampleTickInterval FROM %s LIMIT 1" % \
			constants.tblStdInfo )
		sampleTickInterval = cursor.fetchone()[0]
		cursor.close()
		return sampleTickInterval

	# Get the database version
	def getLogDbVersion( self, name = None ):
		if not name:
			name = self.logDbName
		cursor = self._useDb( name )
		cursor.execute( "SELECT version FROM %s LIMIT 1"\
				% (constants.tblStdInfo))
		result = cursor.fetchone()
		cursor.close()
		return result[0]

	def getLastTick( self, name = None ):
		"""
		Returns the tick and timestamp of the last
		entry in the tick table.
		"""
		if not name:
			name = self.logDbName
		cursor = self._useDb( name )

		# If we get the very last tick in the table, the stats may not have
		# finished gathering for that interval...so we gather the second last,
		# which is guaranteed
		cursor.execute( "SELECT id, time FROM %s "\
			"ORDER BY id DESC LIMIT 1 OFFSET 1" \
				% constants.tblStdTickTimes )
		results = cursor.fetchone()
		cursor.close()
		if results != None:
			results = (results[0], utilities.convertLongTime( results[1] ))
		return results

	def getFirstTick( self, name = None ):
		if not name:
			name = self.logDbName

		cursor = self._useDb( name )
		cursor.execute( "SELECT id, time FROM %s "\
			"WHERE id = 1" \
				% constants.tblStdTickTimes )
		results = cursor.fetchone()
		cursor.close()
		if results != None:
			results = (results[0], utilities.convertLongTime( results[1] ))
		#log.debug("getFirstTick: %s", results)
		return results

	def addTickToDb( self, tick, time ):
		"""
		Inserts a tick into the constants.tblStdTickTimes table.
		Time must be a floating point number representing the timestamp.
		"""
		time = utilities.convertFloatTime( time )
		cursor = self._useDb( self.logDbName )
		cursor.execute( "INSERT INTO %s(id, time) "\
				"VALUES(%%s, %%s)" \
			% (constants.tblStdTickTimes), (tick, time) )
		self.updateTouchedTime()

	def updateTouchedTime( self ):
		cursor = self._useDb( self.logDbName )
		cursor.execute( "SELECT COUNT(*) FROM %s" % (constants.tblStdTouchTime) )
		numRows = cursor.fetchone()[0]
		if numRows > 0:
			cursor.execute( "UPDATE %s SET touchTime = UNIX_TIMESTAMP()" % \
				(constants.tblStdTouchTime) )
		else:
			cursor.execute( "INSERT INTO %s(touchTime) "\
					"VALUES(UNIX_TIMESTAMP())" % \
				(constants.tblStdTouchTime) )

	# Search the info db for the last database used
	def getLatestLogDbName( self ):
		logDbList = self.getLogDbList()
		if logDbList == None:
			return None
		max = 0
		maxName = None
		for name, created, used, active, users in logDbList:
			if used > max:
				max = used
				maxName = name
		return maxName

	def switchToLogDb( self, name ):
		# WARNING: Only use this if you're absolutely sure the
		# db exists, and that the db will validate
		self.logDbName = name
		cursor = self._useDb( name )
		return cursor

	def connectToLogDb( self, name = None ):
		# Connect to the server
		self._connectToServer()

		# Find a name if none provided
		if name == None:
			name = self.getLatestLogDbName( )
			if name == None:
				raise LogDbError( "No log databases found.",
						LogDbError.ERR_NOLOGDB )

		# Next, make sure the database actually exists in
		# the db server
		if not self._checkDbExists( name ):
			raise LogDbError( "Log database \"%s\" does not exist in the "\
					"server." % name, LogDbError.ERR_NOLOGDB )

		info = self._getInfoAboutLogDb( name )
		if info:
			(created, used, active, users) = info
		else:
			raise LogDbError( "Unable to retrieve database info for %s"\
					% name, LogDbError.ERR_NOLOGDB )

		# Then, check that it exists in the "name" metadatabase
		exists = self._checkNameInInfoDb( name )
		if not exists:
			log.info( "Database does not exist in the info table, adding..." )
			cursor = self._useInfoDb()
			createdb.updateInfoDb( cursor, name )
			cursor.close()


		# Connect, validate
		cursor = self._useDb( name )
		try:
			errors = validatedb.validateLogDb( cursor )
			if len(errors) > 0:
				raise LogDbValidateError( errors )
		finally:
			cursor.close()

		self.logDbName = name

	def cloneWithNewConnection( self ):
		newManager = DbManager( self.dbStoreConfig )
		newManager.infoTblChecked = True
		newManager.switchToLogDb( self.logDbName )
		return newManager

	# Must be called right after connecting to log db
	def getLogDbPrefTree( self ):
		# Load preference tree
		cursor = self._useDb( self.logDbName )
		dbPrefTree = readdbpref.generatePrefTreeFromLogDb( cursor )
		cursor.close()
		return dbPrefTree


	def createLogDb( self, name, prefTree, sampleTickInterval ):
		# Hacky thing to autogenerate info db if it doesn't exist
		cursor = self._useInfoDb()
		cursor.close()

		# Now start creating the log database
		cursor = self._getCursor()
		if name == None:
			name = createdb.generateLogDbName( cursor, self.dbPrefix )

		log.info( "Creating log database \"%s\"" % (name,) )
		createdb.generateLogDb( cursor, name, prefTree, sampleTickInterval )
		self._useDb( name )

		try:
			errors = validatedb.validateLogDb( cursor )
			if len(errors) > 0:
				raise LogDbValidateError( errors )
		finally:
			cursor.close()

		self.logDbName = name

	def addSessionStart( self ):
		if self._sessionDbId == None:
			now = int( time.time() )
			cursor = self._useDb( self.logDbName )
			cursor.execute( "INSERT INTO %s(startTime) VALUES(%%s)" % \
					(constants.tblStdSessionTimes), now )
			self._sessionDbId = cursor.connection.insert_id()
		else:
			log.error( "Trying to start session when one already in progress?" )
			log.error( "(This state should not be reached)" )

	def endSession( self ):
		if self._sessionDbId != None:
			now = int( time.time() )
			cursor = self._useDb( self.logDbName )
			cursor.execute( "UPDATE %s SET endTime=%%s WHERE id=%%s" % \
					(constants.tblStdSessionTimes), (now, self._sessionDbId) )
			self._sessionDbId = None
		else:
			log.error( "Trying to end session when none in progress?" )
			log.error( "(This state should not be reached)" )

	def getUserID( self, name ):
		cursor = self._useDb( name )
		cursor.execute( "SELECT userid FROM %s LIMIT 1"\
				% (constants.tblStdInfo))
		result = cursor.fetchone()
		cursor.close()
		return result[0]
		
	@classmethod
	def testConnection( cls, dbStoreConfig ):
		try:
			conv = DbManager.createConversionDict()
			connection = MySQLdb.connect( host=dbStoreConfig.host,
				user=dbStoreConfig.user,
				passwd=dbStoreConfig.password, port=dbStoreConfig.port,
				conv = conv,
				charset = constants.STAT_LOGGER_CHARSET,
				connect_timeout = constants.dbConnectTimeOut )
		except Exception, e:
			log.error( "Failed to connect to DB %s:%s, error: %s",
				dbStoreConfig.host, dbStoreConfig.port, e )
			return False
			
		connection.close()
		
		return True

	# Close the db connection
	def close( self ):
		if self._dbConn:
			self._dbConn.close()

	# Connect to MySQL server (without attaching to database)
	def _connectToServer( self ):
		if not self.enabled: 
			raise LogDbError( "Database data store is not enabled in StatLogger" \
					" configuration file: '%s'." % self.prefFilePath ,
					LogDbError.ERR_NOT_ENABLED,  )

		if self._dbConn != None:
			# Send a test ping which will reconnect if the connection's timed
			# out
			try:
				self._dbConn.ping( True )
			except TypeError:
				# The ping method in older versions of MySQL Python library don't
				# take a parameter.
				self._dbConn.ping()

			return self._dbConn
		try:
			conv = self.createConversionDict()
			connection = MySQLdb.connect( host=self.dbHost,
				user=self.dbUser,
				passwd=self.dbPass, port=self.dbPort,
				conv = conv,
				charset = constants.STAT_LOGGER_CHARSET,
				connect_timeout = constants.dbConnectTimeOut )
			connection.autocommit( 1 )
		except _mysql_exceptions.OperationalError, e:
			if e[0] == 1045:
				raise LogDbError( "Invalid database credentials.",
						LogDbError.ERR_BAD_NAME_PASSWORD )
			else:
				raise LogDbError( "%d: %s" % (e[0], e[1]), \
					LogDbError.ERR_NOSQLSERVER )
		self._dbConn = connection
		return self._dbConn

	# Compatibility fix with MySQL5, which tends to return
	# floating point arithmetic results as type "decimal.Decimal".
	# Make it return floats instead.
	@classmethod
	def createConversionDict( cls ):
		conv = MySQLdb.converters.conversions.copy()
		conv[ MySQLdb.FIELD_TYPE.NEWDECIMAL ] = float
		return conv

	# Switch to database specified, returns a cursor to that database
	# WARNING: make sure to call cursor.close when you're done with it!
	def _useDb( self, dbName ):
		# Connect to database if not connected
		conn = self._connectToServer()
		cursor = conn.cursor()
		# IF statement commented out because when the SQL connection times out,
		# no database is selected # and there's no way to ensure that there is
		# a database selected except by running this every time
		#if self._currentDbName != dbName:
		try:
			cursor.execute( 'USE %s' % (dbName) )
			#print "Using database %s" % dbName
		except _mysql_exceptions.OperationalError, e:
			cursor.close()
			if e[0] == 1044:
				raise LogDbError( "Database user '%s' does not have the "\
						"appropriate access to the database '%s'" % \
					(self.dbUser, dbName), LogDbError.ERR_NOACCESS )
			else:
				raise
			self._currentDbName = dbName
		return cursor

	# Use the info database, return a cursor to it
	def _useInfoDb( self, allowCreate = True ):
		try:
			cursor = self._useDb( constants.infoDbName )
		except _mysql_exceptions.OperationalError, e:
			if e[0] == 1049:
				if allowCreate:
					cursor = self._getCursor()
					createdb.generateInfoDb( cursor )
					cursor = self._useDb( constants.infoDbName )
					self.infoTblChecked = True
					return cursor
				else:
					raise LogDbError("No log info database exists.",
						LogDbError.ERR_NOLOGDB)
			else:
				raise e

		if not self.infoTblChecked:
			cursor.execute( "SHOW TABLES LIKE '%s'" % (constants.tblInfo) )
			if cursor.rowcount == 0:
				createdb.generateInfoTable( cursor )
			self.infoTblChecked = True
		return cursor

	def _checkNameInInfoDb( self, name ):
		cursor = self._useInfoDb()
		cursor.execute( "SELECT name FROM %s WHERE name = %%s" % \
				(constants.tblInfo), name )
		exists = cursor.rowcount != 0
		cursor.close()
		return exists

	# Scan the information database for a record
	# containing a log db name
	def _getInfoAboutLogDb( self, name ):
		try:
			cursor = self._useDb( name )
		except _mysql_exceptions.OperationalError, e:
			# Database doesn't exist
			if e[0] == 1049:
				return None
			else:
				raise

		# Get the time created
		cursor.execute( "SELECT MIN(t.time) AS created, MAX(t.time) AS used "\
				"FROM %s t" \
			% (constants.tblStdTickTimes) )
		created, used = cursor.fetchone()

		if created != None:
			created /= 1000

		if used != None:
			used /= 1000

		# Get the time last updated
		try:
			cursor.execute( "SELECT (UNIX_TIMESTAMP() - touchTime) < 6 "\
					"FROM %s LIMIT 1" % \
				(constants.tblStdTouchTime) )
			if cursor.rowcount > 0:
				active = bool(cursor.fetchone()[0])
			else:
				active = False
		except _mysql_exceptions.ProgrammingError:
			active = False

		# Get the users being logged in this db
		try:
			cursor.execute( "SELECT uid, name FROM %s" \
					% (constants.tblSeenUsers))
			results = cursor.fetchall()
			users = [(int(u[0]), u[1]) for u in results]
		except _mysql_exceptions.OperationalError:
			users = []
		except _mysql_exceptions.ProgrammingError:
			users = []

		return created, used, active, users


	# Check that a log database exists
	def _checkDbExists( self, dbName ):
		cursor = self._getCursor()
		cursor.execute( "SHOW DATABASES LIKE '%s'" % (dbName))
		results = cursor.rowcount
		cursor.close()
		return results > 0

	# Used to get a cursor to the current MySQL server
	# Uses current database, but this function can
	# only be used for non-database specific operations
	# i.e. listing databases, creating databases
	def _getCursor( self ):
		return self._dbConn.cursor()

# end class DbManager


# ------------------------------------------------------------------------------
# Section: Error classes
# ------------------------------------------------------------------------------

class LogDbError( Exception ):
	ERR_GENERAL  = 1
	ERR_NOSQLSERVER = 2
	ERR_NOINFODB = 3
	ERR_MISMATCH = 4
	ERR_INVALID_CATEGORY = 6
	ERR_INVALID_PROCESS = 7
	ERR_MISSING_TABLE = 8
	ERR_NOLOGDB = 9
	ERR_NOACCESS = 10
	ERR_BAD_NAME_PASSWORD = 11
	ERR_NOT_ENABLED = 12

	def __init__( self, msg, code = None ):
		Exception.__init__( self )
		self.msg = msg
		if code == None:
			self.code = self.ERR_GENERAL
		else:
			self.code = code

	def __str__( self ):
		return self.msg

class LogDbValidateError( Exception ):
	def __init__( self, errors ):
		Exception.__init__( self )
		self.errors = errors

	def __str__( self ):
		return "\n".join( self.errors )

	def printErrors( self, prefix ):
		for e in self.errors:
			print "%s%s" % (prefix, e)

# dbmanager.py
