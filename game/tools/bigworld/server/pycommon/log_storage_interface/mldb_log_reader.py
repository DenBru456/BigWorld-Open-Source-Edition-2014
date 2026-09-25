# TODO: Document this file and its classes and methods

import bwsetup
bwsetup.addPath( "../.." )

# Local modules
from base_log_reader import BaseLogReader
from mldb_log_query import MLDBLogQuery
from log_db_constants import BACKEND_MLDB, MLDB_CHARSET

# Other modules
from message_logger import message_log
from pycommon.bwlog import _bwlog as bwlog
from pycommon.exceptions import ServerStateException


class MLDBLogReader( BaseLogReader ):

	def __init__( self, config, readerLocation = None ):
		BaseLogReader.__init__( self )
		self.dbType = BACKEND_MLDB
		self.readerLocation = readerLocation
		self.config = config
		self.logDB = self.getNewLogDBConnection()

		# for the time being, piggyback on message_log.py as it performs just
		# about everything we require already
		#
		# TODO: consider migrating message_log into this class or into this
		# module (although it relies on current directory containing the conf
		# file - take that into account!!!)
	# __init__


	def getNewLogDBConnection( self ):
		try:
			if self.readerLocation:
				logDB = message_log.MessageLog( self.config, 
						self.readerLocation )
			else:
				logDB = message_log.MessageLog( self.config )

			if not logDB:
				# No valid MessageLog object but no exception raised? Raise our
				# own one then.
				raise ServerStateException( "An unknown error occurred "
					"connecting to the MLDB database. Unable to get MessageLog "
					"object." )
		except IOError:
			raise ServerStateException(
					"Message Logger has not been configured.")
		return logDB


	def refreshLogDB( self ):
		"""
		Reinitialises the message_logger to ensure table data (ie. filter
		dropdown data, list of valid users and segments, etc) is up to 
		date when querying.
		"""
		self.logDB = self.getNewLogDBConnection()


	def _getLogQueryClass( self ):
		"""
		Used to inform the BaseLogReader of the local implementation class of
		BaseLogQuery that it should create and store in its cache.
		"""
		return MLDBLogQuery


	def getUsers( self ):
		return self.logDB.getUsers()


	def getCategoryNames( self ):
		return self.logDB.getCategoryNames()


	def getComponentNames( self ):
		return self.logDB.getComponentNames()


	def getHostnames( self ):
		return self.logDB.getHostnames()


	def getStrings( self ):
		return self.logDB.getStrings()


	def getAllServerStartups( self, serverUsername, columnFilter = None ):
		"""
		Returns a list of strings representing startups, for display purposes
		only.
		"""
		uid = self.getUIDFromUsername( serverUsername )
		if not uid:
			return None

		userLog = self.logDB.getUserLog( uid )
		startupItems = userLog.getAllServerStartups()

		if columnFilter:
			showMask = MLDBLogQuery.columnFilterToMask( columnFilter )
		else:
			showMask = None

		# convert from PyQueryObjects to strings
		startupStrings = []
		for startupItem in startupItems:
			if showMask:
				startupStrings.append( startupItem[0].format( showMask ) )
			else:
				startupStrings.append( startupItem[0].format() )

		return startupStrings
	# getAllServerStartups


	def getSeverities( self ):
		severities = {}
		for (severity, level) in bwlog.SEVERITY_LEVELS.items():
			severities[ level ] = severity
		return severities


	def getSourceNames( self ):
		return bwlog.DebugMessageSource.keys()


	def isRunning( self ):
		return self.logDB.isRunning()


	# def checkDBStatus( self ):
		# TODO this option may be useful as part of the MongoDB implementation,
		# less so for MLDB but this could still possibly be a simple check (such
		# as that the message_logger directory is readable)
		# return True


	# def getDBSummary( self, serverUser = None ):
		# TODO this option will be implemented as part of the Usage page changes
		# return None


	# TODO: This would be better if it was part of a new writer class rather
	# than a reader, since it is the writer that knows what addresses it is
	# connected to.
	def getNubAddresses( self, serveruser = None ):
		uid = self.getUIDFromUsername( serveruser )
		if not uid:
			return None

		return self.logDB.getUserLog( uid ).getNubAddresses()


	def getCharset( self ):
		return MLDB_CHARSET


# MLDBLogReader
