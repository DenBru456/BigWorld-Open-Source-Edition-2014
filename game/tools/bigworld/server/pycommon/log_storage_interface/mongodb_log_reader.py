# Local modules
from base_log_reader import BaseLogReader
from mongodb_log_query import MongoDBLogQuery
from mongodb_log_query_result import MongoDBLogQueryResult
from log_db_constants import BACKEND_MONGODB, MONGODB_CHARSET
import mongodb_constants as constants

import bwsetup
bwsetup.addPath( "../.." )

from pycommon.exceptions import ServerStateException

import ConfigParser
import pymongo
from bisect import bisect_left
import datetime

from collections import defaultdict
import logging
log = logging.getLogger( __name__ )

class MongoDBLogReader( BaseLogReader ):

	def __init__( self, config ):
		super( MongoDBLogReader, self ).__init__()
		self.dbType = BACKEND_MONGODB

		self.config = config
		try:
			host = self.config.get( 'mongodb', 'host' )
			port = self.config.get( 'mongodb', 'port' )
			user = self.config.get( 'mongodb', 'user' )
			password = self.config.get( 'mongodb', 'password' )
		except ConfigParser.NoOptionError:
			raise ServerStateException(
					"Message Logger has not been configured.")

		# TODO: add error handling here
		self.client = pymongo.MongoClient( host, int(port) )
		self.client.bw_ml_common.authenticate( user, password, source='admin' )
	# __init__


	@staticmethod
	def parseDatabaseInfo( name ):
		"""
		Parse a database name to extract information about it. Supports both
		delimited and non-delimited names, although this module should only ever
		use delimited ones now.
		"""

		result = {'name': name}
		if constants.USER_DB_PREFIX in name:
			prefix = constants.USER_DB_PREFIX
			result['type'] = 'user'
		elif constants.COMMON_DB_PREFIX in name:
			prefix = constants.COMMON_DB_PREFIX
			result['type'] = 'common'
		else:
			result['type'] = 'unknown'
			return result

		name = name[ name.rfind( prefix ) + len(prefix): ]
		"""
		Possible expected remainders are:
		for bw_ml_common:
		- <nothing>
		- #
		- #logid

		for bw_ml_user:
		- uname
		- uname#
		- uname#logid
		"""
		pos = name.find( constants.LOGGER_ID_DELIMITER )
		result['multi'] = pos != -1

		# If it's a user database, there's a user name between here and the
		# delimiter or end-of-line.
		if result['type'] == 'user':
			if pos != -1:
				result['user'] = name[ :pos ]
			else:
				result['user'] = name
				name = ''

		if pos != -1:
			# Skip past the delimiter
			name = name[ pos + 1: ]
		else:
			# No delimiter means no logger id
			name = ''

		result[ 'logger' ] = name     # Which will be '' if it's the default.
		return result
	# parseDatabaseInfo


	def refreshLogDB( self ):
		"""
		This is a stub function, unused in MongoDB.
		"""
		pass
	# refreshLogDB


	def getCharset( self ):
		return MONGODB_CHARSET
	# getCharset


	def getCommonDatabaseName( self, logger = None ):
		return '%s%s%s' % (constants.COMMON_DB_PREFIX,
						constants.LOGGER_ID_DELIMITER, logger or
						constants.LOGGER_ID_NA)
	# getCommonDatabaseName


	def getCommonDatabase( self, logger ):
		return self.client[ self.getCommonDatabaseName( logger ) ]
	# getCommonDatabase

	def commonDatabaseNameIter( self ):
		match = lambda x: self.getCommonDatabaseName() in x
		for name in filter( match, self.client.database_names() ):
			yield name
	# commonDatabaseNameIter

	def getUserDatabaseName( self, user, logger = None ):
		return '%s%s%s%s' % (constants.USER_DB_PREFIX, user,
							constants.LOGGER_ID_DELIMITER, logger or
							constants.LOGGER_ID_NA)
	# getUserDatabaseName

	def getUserDatabase( self, user, logger ):
		return self.client[ self.getUserDatabaseName( user, logger ) ]
	# getUserDatabase

	def userDatabaseNameIter( self, user=None ):
		if user:
			pattern = self.getUserDatabaseName( user )
		else:
			pattern = constants.USER_DB_PREFIX
		match = lambda x: pattern in x
		for name in filter( match, self.client.database_names() ):
			yield name
	# userDatabaseNameIter


	def getUsers( self ):
		"""
		Parse the user names out of the database names, then extract their UID
		from the collection in that database (required for both mlcat and
		LogViewer).
		"""
		users = {}

		for dbName in self.userDatabaseNameIter():
			try:
				user = self.parseDatabaseInfo( dbName ).get( 'user' )
				if user:
					value = self.client[ dbName ].uid.find_one(
						{'uid': {'$exists': True}} )[ 'uid' ]
					if user not in users:
						users[ user ] = value
					elif users[ user ] != value:
						log.warning( "uid for %s in database %s is %s, ' + \
							'clashes with existing value of %s",
							user, value, dbName, users[ user ]
						)
			except TypeError:
				# Happens when find_one returns None, because the collection
				# is missing or empty.
				if 'uid' in self.client[ dbName ].collection_names():
					log.warning( "database %s: collection \"uid\" does not "
					             "contain any valid entries", dbName )
				else:
					log.warning( "database %s does not contain a \"uid\" "
			             "collection", dbName )
		return users
	# getUsers


	def getLoggerIDs( self ):
		"""
		Parse the unique logger ids out of the database common names.
		"""
		uniqueIDs = set()
		for dbName in self.commonDatabaseNameIter():
			logger = self.parseDatabaseInfo( dbName ).get( 'logger' )
			if logger is not None:
				uniqueIDs.add( logger )
		return sorted( uniqueIDs )
	# getLoggerIDs


	def getCategoryNames( self, logger = None ):
		return self._extractCommonFields( 'categories', logger=logger )
	# getCategoryNames


	def getCategories( self, logger = None ):
		return self._collateCommonFields( 'categories', 'id', 'name',
										logger=logger, renumber=True )
	# getCategories


	def getComponentNamesAsDict( self, logger = None ):
		return self._collateCommonFields( 'components', 'id', 'name',
										logger=logger, renumber=True )
	# getComponentNames


	def getComponentNames( self, logger = None ):
		return self._extractCommonFields( 'components', logger=logger )
	# getComponentNames


	def getHostnames( self, logger = None ):
		return self._collateCommonFields( 'hosts', 'ip', 'hostname',
										logger=logger )
	# getHostnames


	def getStrings( self, logger = None ):
		return self._extractCommonFields( 'format_strings',
										'fmt_str', logger=logger )
	# getStrings


	# Construct a list for source names
	def getSourceNames( self, logger = None ):
		return self._extractCommonFields( 'sources', logger=logger )
	# getSourceNames


	# Construct a dict for both param conversion and logline building
	def getSources( self, logger = None ):
		return self._collateCommonFields( 'sources', 'id', 'name',
										logger=logger, renumber=True )
	# getSources


	def getSeverities( self, logger = None ):
		return self._collateCommonFields( 'severities', 'level', 'name',
										logger=logger, renumber=True )
	# getSeverities


	# Sizes of user logs etc
	def dbSummary( self, serverUser = None, logger = None ):
		# TODO: convert data into format mlcat/logviewer is expecting
		# Probably want to make the whole thing into a JSON blob, too, rather
		# than a dictionary of JSON values.
		if logger is None:
			result = {}
			for dbName in self.userDatabaseNameIter( serverUser ):
				logger = self.parseDatabaseInfo( dbName ).get( 'logger' )
				result[ logger ] = self.client[ dbName ].command( 'collstats' )
			return result
		else:
			return self.getUserDatabase( serverUser, logger ).command( 
																'collstats' )
	# dbSummary


	def getAllServerStartups( self, serverUser, columnFilter = None,
							logger = None ):
		result = []

		for entry in self._collateStartups( serverUser, logger ):
			dateTimeString = MongoDBLogQueryResult.dateTimeToString(
					entry, columnFilter )
			result.append( dateTimeString + "\n" )
		return result
	# getAllServerStartups


	def getServerStartupDateTime( self, serverUser, startupIndex,
								logger = None ):
		try:
			return self._collateStartups( serverUser, logger )[startupIndex]
		except IndexError:
			return None
	# getServerStartupTime


	def getLastServerStartupDateTime( self, serverUser, logger = None ):
		maxTime = None
		if logger is None:
			iterator = self.userDatabaseNameIter( serverUser )
		else:
			iterator = [ self.getUserDatabaseName( serverUser, logger ) ]

		for dbName in iterator:
			item = self.client[ dbName ].server_start_ups \
					.find().sort( 'time', pymongo.DESCENDING ).limit( 1 )

			try:
				dbMax = item[0][ 'time' ]
			except IndexError:
				continue

			if maxTime:
				maxTime = max( maxTime, dbMax )
			else:
				maxTime = dbMax

		return maxTime
	# getLastServerStartupDateTime


	def getNubAddresses( self, serveruser ):
		"""
		Returns a list of tuples of (app name, pid, nub address, nub type) for
		each nub created since the last server startup.
		"""
		uid = self.getUIDFromUsername( serveruser )
		if not uid:
			return None

		query = self._getLogQueryClass()( self, {'serveruser': serveruser} )

		return query.getAddressesInfo()
	# getNubAddresses


	# message_logger status
	def isRunning( self ):
		# TODO
		return True
	# isRunning


	def _getLogQueryClass( self ):
		return MongoDBLogQuery
	# _getLogQueryClass


	def _getCommonCollections( self, collectionType, logger = None ):
		"""
		Returns a list of all collections of the given collectionType, across
		all of the bw_ml_common#* databases. Optionally restricted to the
		database for the logger id.
		"""
		result = []
		for dbName in self.commonDatabaseNameIter():
			info = self.parseDatabaseInfo( dbName )
			collection = self.client[ dbName ][ collectionType ]
			if logger is None:
				result.append( collection )
			else:
				if logger == info.get( 'logger' ):
					return [ collection ]
		return result
	# _getCommonCollections


	def _extractCommonFields( self, collectionType, fields=('name',),
							logger = None ):
		"""
		Iterate through all bw_ml_common* databases, to extract the value for
		the given fields in collections of the given collectionType. If logger
		is specified, then only queries the database for that one.

		@return: A list of values for the given fields
		"""
		values = set()

		# Can pass a single string
		if not isinstance( fields, (list, tuple) ):
			fields = [fields]

		for collection in self._getCommonCollections( collectionType, logger ):
			for record in collection.find():
				entry = []
				for f in fields:
					try:
						entry.append( record[ f ].encode( MONGODB_CHARSET ) )
					except AttributeError:
						# Unencodable type
						entry.append( record[ f ] )
				if len( entry ) == 1:
					values.add( entry[0] )
				else:
					values.add( tuple ( entry ))

		return list( values )
	# _extractCommonFields


	def _collateCommonFields( self, collectionType, keyField, valueField,
							renumber=False, logger = None ):
		"""
		Iterate through all bw_ml_common* databases, to build a combined
		dictionary for the keyField and valueField drawn from collectionType.
		In the case of key clashes, the default operation is to take the first
		value found; setting renumber=True causes it to instead add the values
		so that each has a unique integer key, assigned in the same sort order
		as their original keys.

		If logger is set, this simply collates a dictionary and ignores the
		renumber option.

		@return: A dictionary with keys taken from keyField OR new numbering,
		values taken from valueField.
		"""
		seen = set()
		combined = defaultdict( list )

		# Keep track of every unique value against the first key we find it for
		for collection in self._getCommonCollections( collectionType, logger ):
			for record in collection.find():
				key, value = record[ keyField ], record[ valueField ]
				if value not in seen:
					try:
						combined[ key ].append(
											value.encode( MONGODB_CHARSET ) )
					except AttributeError:
						# Unencodable type
						combined[ key ].append( value )
				seen.add( value )

		if renumber and logger is None:
			# Flatten out the values into a sorted list, ignore the existing
			# index values and give each a new, unique one.
			result = {}
			newKey = 0
			for key, valueList in combined.iteritems():
				for value in valueList:
					result[ newKey ] = value
					newKey += 1
		else:
			# In the case of multiple values per key, simply take the first.
			result = dict( (k, v[0]) for k, v in combined.iteritems() )
		return result
	# _collateCommonFields


	def _collateStartups( self, user, logger = None ):
		"""
		Assuming that a server can't restart more than once every X seconds,
		group startup events from different message loggers together as the
		same event.

		If logger is specified, simply returns the sorted list for that server.
		"""

		THRESHOLD = datetime.timedelta( seconds=5 )

		if logger is not None:
			return sorted( entry[ 'time' ] for entry in \
				self.getUserDatabase( user, logger ).server_start_ups.find() )

		events = []
		for dbName in self.userDatabaseNameIter( user ):
			for entry in self.client[ dbName ].server_start_ups.find():
				ts = entry[ 'time' ]

				# First event goes straight in
				if not events:
					events.append( ts )
					continue

				# Find where it sits relative to the others, and merge it if
				# they're within the threshold, keeping the smaller value.
				pos = bisect_left( events, ts )
				if pos > 0:
					if ts - events[ pos - 1 ] < THRESHOLD:
						continue
				if pos < len( events ):
					if events[ pos ] - ts < THRESHOLD:
						events[ pos ] = ts
						continue

				# If it reached this point, far enough from the others that it
				# can be inserted as a separate event.
				events.insert( pos, ts )
		return events



	# MongoDB status. Unsure how to do this?
	# def checkDBStatus( self ):
		# TODO
		# self.client.admin.command( 'serverStatus' )
		# possibly using mongostat (separate process that must be running)?
	# checkDBStatus
