
"""
This class provides an abstract interface to retrieve information from a
message_logger datastore.

Its main features are to create and retrieve normal log queries, along with
abstract interface methods for retrieving full database tables (such as
categories and hostnames)
"""

import time

from log_reader_constants import QUERY_CACHE_TIMEOUT


class BaseLogReader( object ):

	def __init__( self ):
		"""
		This method must be called explicitly from all derived classes.

		If it is not called explicitly the implementation class will
		immediately fail upon the first call to createQuery or getQueryByID.
		"""
		self.__registeredQueries = {}
	# __init__


	#
	# Functionality common to all implementations of BaseLogReader. Not intended
	# for overriding.
	#

	def createQuery( self, params, resultLimit = None, truncate = False ):
		"""
		Creates and returns a query object.

		The type of query object created relies on the implementation layer, which
		specifies it by implementing the _getLogQueryClass() method.

		The created query object is then stored in a cache for later use (such
		as resuming a query).
		"""
		self._cleanupOldQueries()

		query = self._getLogQueryClass()( self, params, resultLimit, truncate )
		self.__registeredQueries[ str( query.getID() ) ] = query
		return query
	# createQuery


	def getQueryByID( self, queryId ):
		"""
		Locates and returns a stored query by its ID.
		
		If the query can not be located (eg. it has timed out) then an exception
		is raised. It is up to the calling module to handle the exception in an
		appropriate manner.
		"""
		try:
			return self.__registeredQueries[ str( queryId ) ]
		except:
			# object is old/has been deleted due to timeout
			raise LookupError( "Invalid query ID. "
				"Log query may have timed out." )
	# getQueryByID


	def _cleanupOldQueries( self ):
		"""
		This method cleans up the cache of stored queries after a set
		timeout period.
		"""
		currentTime = time.time()

		for q in self.__registeredQueries.values():
			if ((currentTime - q.getLastFetchTime()) > (QUERY_CACHE_TIMEOUT * 60)):
				del self.__registeredQueries[ str( q.getID() ) ]
	# _cleanupOldQueries


	def getUIDFromUsername( self, username ):
		userList = self.getUsers()
		if username in userList:
			return userList[ username ]
		else:
			return None
	# getUIDFromUsername


	#
	# Abstract functions - must be implemented by subclasses
	#

	def refreshLogDB( self ):
		"""
		If required, this will reinitialise the log DB table data (eg. filter
		dropdown data, list of valid users and segments, etc) to ensure it is
		up to date.
		"""
		raise NotImplementedError(
			"BaseLogReader.refreshLogDB method not implemented. "
			"Unable to call abstract method." )
	# refreshLogDB


	def _getLogQueryClass( self ):
		"""
		An abstract method which when overridden should return the DB-specific
		class type which implements BaseLogQuery.
		"""
		raise NotImplementedError(
			"BaseLogReader._getLogQueryClass method not implemented. "
			"Unable to call abstract method." )
	# _getLogQueryClass


	def getUsers( self ):
		"""
		An abstract method which when overridden should return an iterable list
		of usernames that have logs in the database.
		"""
		raise NotImplementedError(
			"BaseLogReader.getUsers method not implemented. "
			"Unable to call abstract method." )
	# getUsers


	def getCategoryNames( self ):
		"""
		An abstract method which when overridden should return an iterable list
		of category names that have logs associated with them.
		"""
		raise NotImplementedError(
			"BaseLogReader.getCategoryNames method not implemented. "
			"Unable to call abstract method." )
	# getCategoryNames


	def getComponentNames( self ):
		"""
		An abstract method which when overridden should return an iterable list
		of component names that have logs associated with them.
		"""
		raise NotImplementedError(
			"BaseLogReader.getComponentNames method not implemented. "
			"Unable to call abstract method." )
	# getComponentNames


	def getHostnames( self ):
		"""
		An abstract method which when overridden should return an iterable list
		of hostnames that have logs associated with them.
		"""
		raise NotImplementedError(
			"BaseLogReader.getHostnames method not implemented. "
			"Unable to call abstract method." )
	# getHostnames


	def getStrings( self ):
		"""
		An abstract method which when overridden should return an iterable list
		of all the format strings available in the logs.
		"""
		raise NotImplementedError(
			"BaseLogReader.getStrings method not implemented. "
			"Unable to call abstract method." )
	# getStrings


	def getAllServerStartups( self, serverUsername, columnFilter = None ):
		"""
		An abstract method which when overridden should return an iterable list
		of all the server startups in the logs as strings.
		"""
		raise NotImplementedError(
			"BaseLogReader.getAllServerStartups method not implemented. "
			"Unable to call abstract method." )
	# getAllServerStartups


	def getSeverities( self ):
		"""
		An abstract method which when overridden should return an iterable list
		of all available severities as strings.
		"""
		raise NotImplementedError(
			"BaseLogReader.getSeverities method not implemented. "
			"Unable to call abstract method." )
	# getSeverities


	def getSourceNames( self ):
		"""
		An abstract method which when overridden should return an iterable list
		of all available sources as strings.
		"""
		raise NotImplementedError(
			"BaseLogReader.getSourceNames method not implemented. "
			"Unable to call abstract method." )
	# getSourceNames


	def isRunning( self ):
		"""
		An abstract method which when overidden should report if the message
		logger is running.

		The method of checking this is up to each DB implementation (eg. MLDB
		will check for a pid file, MongoDB may check for a pid table entry or
		may ask bwmachined to confirm)
		"""
		raise NotImplementedError(
			"BaseLogReader.isRunning method not implemented. "
			"Unable to call abstract method." )
	# isRunning


	def checkDBStatus( self ):
		"""
		An abstract method which when overidden should report if the data store
		can be connected to.

		The method of checking this is up to each DB implementation (eg. MLDB
		could check that the root log path exists (or may do nothing), whereas
		MongoDB may check its its discovery mechanism (if implemented) and/or
		test the port connection.
		"""
		raise NotImplementedError(
			"BaseLogReader.checkDBStatus method not implemented. "
			"Unable to call abstract method." )
	# checkDBStatus


	def getDBSummary( self, serverUser = None ):
		"""
		An abstract method which when overidden should return a JSON
		string representing a summary of the specified user's database, or all
		databases if none is provided..
		"""
		raise NotImplementedError(
			"BaseLogReader.dbSummary method not implemented. "
			"Unable to call abstract method." )
	# getDBSummary


	# TODO: This would be better if it was part of a new writer class rather
	# than a reader, since it is the writer that knows what addresses it is
	# connected to.
	def getNubAddresses( self, uid ):
		"""
		An abstract method which when overidden should return a list of 
		array objects containing the following nub data:
		(name, pid, addr, nubtype)
		"""
		raise NotImplementedError(
			"BaseLogReader.getNubAddresses method not implemented. "
			"Unable to call abstract method." )
	# getNubAddresses


	def getCharset( self ):
		"""
		An abstract method which when overidden should return the character set
		used by the database.
		"""
		raise NotImplementedError(
			"BaseLogReader.getCharset method not implemented. "
			"Unable to call abstract method." )
	# getCharset


# BaseLogReader
