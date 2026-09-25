import pymongo
import time
import datetime
import re

import logging
log = logging.getLogger( __name__ )

from dateutil import tz

# convert tz module-wide to prevent having to perform lookups on every log line
tzlocal = tz.tzlocal()
tzutc = tz.tzutc()

from pycommon import util as pyutil

from base_log_query import BaseLogQuery
from log_reader_constants import SERVER_STARTUP_STRING
from mongodb_log_query_params import MongoDBLogQueryParams
from mongodb_log_query_result import MongoDBLogQueryResult
from log_reader_constants import DEFAULT_DISPLAY_COLUMNS, MAX_BUFFERED_RESULTS

import mongodb_constants as constants


class MongoDBLogSingleDBQuery( object ):
	"""
	This class provides the function to query log from a user's log database of
	given loggerID.
	"""
	def __init__( self, parentQuery, loggerID, params, resultLimit = None ):

		self.parentQuery = parentQuery
		self._loggerID = loggerID

		self.serverUser = parentQuery.serverUser
		self.logReader = parentQuery.logReader

		self._resultLimit = resultLimit
		self._zeroResults = False
		self._latestEntry = None

		self._resumeEntry = None
		self._resumeColl = None

		self._db = self.logReader.getUserDatabase( self.serverUser, loggerID )

		# Log collection list of the user of this query, in time-ascending order
		self._logCollList = None

		# Log collection name and time dict, in the same order as _logCollList
		self._logCollDict = None

		# Get the latest collection list and dict of this user from database
		self.refreshData()
		
		# get the appID in params for filter appID
		self._appID = params.get( 'appid', 0 )
		# get negate appID in params for filter appID
		self._negateAppID = params.get( 'negate_appid', False )

		self._activeCursor = None

		# This is a dict of regex objects used for translating addresses into
		# app names. Addresses are added using _addAddressTranslations().
		self.translatePatts = {}

		if 'translate' in params and params[ 'translate' ]:
			self._addAddressTranslations()
		
		self._logQueryParams = MongoDBLogQueryParams( self.logReader, self,
													params )
	# __init__


	def _addAddressTranslations( self ):
		"""
		Fetches the nub addresses since the last server startup for the given
		uid and adds them as address translations.
		"""
		for name, pid, address, type in self.getAddressesInfo():
			patt = re.compile( re.escape( address ) )
			self.translatePatts[ patt ] = "@" + name
	# _addAddressTranslations


	def _filterByRealAppID( self, dbEntry):
		"""
		Check the real appID in components collection with appID filter
		"""
		if self._appID != 0 and dbEntry.get( 'aid' ) == 0:
			if 'host' in dbEntry and 'pid' in dbEntry and 'cpt' in dbEntry:
				appID = self.findAppID( dbEntry[ 'host' ],
							dbEntry[ 'pid' ], dbEntry[ 'cpt' ] )
				if appID != 0 and (appID == self._appID) == self._negateAppID:
					return False

		return True
	# _filterByRealAppID


	def getCursor( self, resultLimit = None ):
		"""
		This function return a generator, which continuously returns query
		results until result limit is reached or result is exhausted.

		resultLimit == 0 means no limit.
		"""

		if resultLimit is None:
			resultLimit = self._resultLimit or MAX_BUFFERED_RESULTS

		resultCount = 0
		collName = self._resumeColl

		# This is to indicate whether it's the first fetch. If and only if it's
		# first fetch, we will query the last collection available. This is to
		# prevent the while loop never stopping
		firstFetch = True

		while True:
			remaining = 0

			if resultLimit > 0:
				remaining = resultLimit - resultCount
			collName, cursor = self._fetchNextResultCursor( remaining,
														collName, firstFetch )
			firstFetch = False

			# Have exhausted all of the collections, break
			if not cursor:
				return

			self._activeCursor = cursor

			for dbEntry in cursor:
				# if we have appID filter and no appID in the entry log, need to
				# compare with appID in components collection
				if not self._filterByRealAppID( dbEntry ):
					continue
				yield (dbEntry, collName)
				resultCount += 1

				# Have reached the limit, break
				if resultLimit > 0 and resultCount >= resultLimit:
					return
	# getCursor


	def resultCount( self ):
		"""
		Count the total count of logs matching the query and return the count.

		This operation could be very expensive.
		"""

		resultCount = 0

		collToQuery = None
		dateTimeParam = self._getDateTimeParam( self._logQueryParams.params,
												self.parentQuery.querySort )
		firstFetch = True

		while True:
			collToQuery = self._getNextCollToQuery( dateTimeParam,
						self.parentQuery.querySort, collToQuery, firstFetch )
			firstFetch = False

			if not collToQuery:
				return resultCount

			resultCount += self._db[ collToQuery ].find(
										self._logQueryParams.params ).count()

	# resultCount


	def closeActiveCursor( self ):
		if self._activeCursor:
			self._activeCursor.close()

		self._activeCursor = None


	def setResumePoint( self, dbEntry, collName ):
		"""
		Set the resume point of this query.

		resumePoint is a tuple of a collection name and a database entry
		"""
		self._resumeEntry = dbEntry
		self._resumeColl = collName


	def resetTimeParam( self, dateObj, counter, queryDirection, contains ):
		"""
		Reset the start time of the query.
		"""
		self._resumeEntry = None
		self._resumeColl = None

		self._logQueryParams.resetTimeParam( dateObj, counter, queryDirection,
		                                     contains )
	# resetTimeParam


	def moreResultsAvailable( self, refreshQuery = False ):
		# When refreshQuery is false, the last log entry matching the
		# params is fetched only once. This entry will then be used to
		# determine if more results are available. This means that the results
		# of each query will only be current up to when the user clicked Fetch.

		# When refreshQuery is true, a new last log entry will be fetched
		# each time this function is called. This is currently only used in
		# Live mode.

		# If we already know there are zero results, don't proceed
		if not refreshQuery and self._zeroResults:
			return False

		# If working backwards chronologically, must change to ASCENDING
		if refreshQuery or not self._latestEntry:
			self._latestEntry = self._findOne( self._logQueryParams.params,
										self.invertSortOrder(
											self.parentQuery.querySort ) )

		if self._latestEntry:
			self._zeroResults = False
			if not self._resumeEntry:
				# If a matching entry was found and we have never searched or
				# resumed, then more results are always available
				return True
		else:
			# If no single record matches then there can be no more results
			if not self._resumeEntry:
				self._zeroResults = True
			return False

		# Compare datetime and count fields of last result in most recent query
		# to that in most recent log line. If dates are equal and counter is
		# higher or date is higher, there are more results.
		if self.parentQuery.querySort == pymongo.ASCENDING:
			diffFn = lambda x, y: x > y
		else:
			diffFn = lambda x, y: x < y

		return diffFn( self._latestEntry[ 'ts' ], self._resumeEntry[ 'ts' ] ) \
			or (
				self._latestEntry[ 'ts' ] == self._resumeEntry[ 'ts' ] and
			    diffFn( self._latestEntry[ 'cnt' ], self._resumeEntry[ 'cnt' ] )
			)


	def getLogBeginningTime( self ):
		"""
		Get the timestamp of the first log of this user
		"""
		dbEntry = self._findOne( None, pymongo.ASCENDING )

		if dbEntry:
			return dbEntry[ 'ts' ]

		return None


	def findOne( self, queryDirection, anyTime = False ):
		"""
		Find just one record based on the given params and sorting direction.
		Return the found entry and its collection
		"""
		params = dict( self._logQueryParams.params )
		if anyTime and 'ts' in params:
			del params[ 'ts' ]

		return self._findOne( params, queryDirection )
	# findOne


	def refreshData( self ):
		"""
		Get the log entry collections of this server user as dict sorted by
		timestamp in the collection name in ascending order.

		Refresh the common data as well.
		"""

		collDict = {}
		collList = []
		tmpCollList = sorted( self._db.collection_names() )

		# Log collection's name format: entries_YYYYMMDDHHMMSS
		for collName in tmpCollList:
			if not collName.startswith( "entries_" ) or len( collName ) != 22:
				continue

			timeStr = collName[ 8: ]
			collTime = datetime.datetime( int( timeStr[ 0 : 4 ] ),
								int( timeStr[ 4 : 6 ] ),
								int( timeStr[ 6 : 8 ] ),
								int( timeStr[ 8 : 10 ] ),
								int( timeStr[ 10 : 12 ] ),
								int( timeStr[ 12 : ] ) ).replace( tzinfo = None)

			collDict[ collName ] = collTime
			collList.append( collName )

		self._logCollList = collList
		self._logCollDict = collDict

		# Get static data
		self.hostnames = self.logReader.getHostnames( self._loggerID )
		self.components = self.logReader.getComponentNamesAsDict(
																self._loggerID )
		self.sources = self.logReader.getSources( self._loggerID )
		self.severities = self.logReader.getSeverities( self._loggerID )
		self.categories = self.logReader.getCategories( self._loggerID )
	# refreshData

	@staticmethod
	def invertSortOrder( order ):
		"""
		Will probably always be safe to invert with maths, but abstract here
		in case it changes!
		"""
		return order * -1

	def _fetchNextResultCursor( self, maxLines, previousColl = None,
							firstFetch = False ):
		"""
		This method performs an initial query or resumes an existing one.

		MongoDB functions better if the limit is set on the cursor rather than
		querying all results and imposing the limit during post-processing.

		We also need to impose batch size to make the query more responsive.
		"""

		self._checkResume()

		dateTimeParam = self._getDateTimeParam( self._logQueryParams.params,
											self.parentQuery.querySort )

		collToQuery = self._getNextCollToQuery( dateTimeParam,
						self.parentQuery.querySort, previousColl, firstFetch )

		if not collToQuery:
			return ( None, None )

		if maxLines > 0:
			cursor = self._db[ collToQuery ].find( self._logQueryParams.params
				).sort(	[( 'ts', self.parentQuery.querySort ),
						( 'cnt', self.parentQuery.querySort )]
				).limit( maxLines ).batch_size( constants.QUERY_BATCH_SIZE )
		else:
			cursor = self._db[ collToQuery ].find( self._logQueryParams.params
				).sort( [( 'ts', self.parentQuery.querySort ),
						( 'cnt', self.parentQuery.querySort )]
				).batch_size( constants.QUERY_BATCH_SIZE )

		return ( collToQuery, cursor )
	# _fetchNextResultCursor


	def _checkResume( self ):
		"""
		Check if this is a resume query. If it is, update the query parameters
		to query from the resume point.
		"""
		if not self._resumeEntry:
			return

		previousTs = None

		# Change ts and cnt filters to values in resumeEntry
		# If DESCENDING, the time $gt filter here should be changed to $lt
		if 'ts' in self._logQueryParams.params:
			previousTs = self._logQueryParams.params[ 'ts' ]
			del self._logQueryParams.params[ 'ts' ]
		if 'cnt' in self._logQueryParams.params:
			del self._logQueryParams.params[ 'cnt' ]
		if '$or' in self._logQueryParams.params:
			del self._logQueryParams.params[ '$or' ]

		if self.parentQuery.querySort == pymongo.ASCENDING:
			direction = '$gt'

			# should keep the original 'less than' timestamp
			if previousTs:
				if '$lt' in previousTs:
					self._logQueryParams.params[ 'ts' ] = \
						{ '$lt' : previousTs[ '$lt' ] }
				elif '$lte' in previousTs:
					self._logQueryParams.params[ 'ts' ] = \
						{ '$lte' : previousTs[ '$lte' ] }
		else:
			direction = '$lt'

			# should keep the original 'larger than' timestamp
			if previousTs:
				if '$gt' in previousTs:
					self._logQueryParams.params[ 'ts' ] = \
						{ '$gt': previousTs[ '$gt' ] }
				elif '$gte' in previousTs:
					self._logQueryParams.params[ 'ts' ] = \
						{ '$gte': previousTs[ '$gte' ] }

		# TODO: Cleanup: change MongoDB parameters to constants
		self._logQueryParams.params[ '$or' ] = [
			{ 'ts': self._resumeEntry[ 'ts' ],
			'cnt': { direction: self._resumeEntry[ 'cnt' ] } },
			{ 'ts': { direction: self._resumeEntry[ 'ts' ] } } ]
	# _checkResume


	def _getNextCollToQuery( self, datetimeParam = None,
							queryDirection = pymongo.ASCENDING,
							previousColl = None, firstFetch = False ):
		"""
		Find the next collection to query over.

		We shouldn't query the last collection again if it's not first fetch.
		"""
		collList = self._logCollList
		collSize = len( collList )

		if collList and queryDirection == pymongo.DESCENDING:
			collList = list( self._logCollList )
			collList.reverse()

		previousIndex = 0
		index = 0

		if previousColl and previousColl in collList:
			previousIndex = collList.index( previousColl )

		# It's not first fetch in a query, then it means previous has been
		# exhausted, we should start from next collection then
		if not firstFetch:
			previousIndex += 1

		for collName in collList:
			if index >= previousIndex:
				# No time specified, just get by index
				if not datetimeParam:
					return collName
				# Query is in ascending order
				elif queryDirection == pymongo.ASCENDING:
					# current collection is newer
					if self._logCollDict[ collName ] >= datetimeParam:
						return collName
					# current is the last or next is newer
					elif index == collSize - 1 or \
						( self._logCollDict[ collList[ index + 1 ] ] >=
							datetimeParam ):
						return collName
				# Query is in descending order and current collection is older
				elif queryDirection == pymongo.DESCENDING and \
						self._logCollDict[ collName ] <= datetimeParam:
					return collName
			index += 1

		return None
	#_getNextCollToQuery


	def _getDateTimeParam( self, params, queryDirection ):
		"""
		Get datetime parameters from given parameters and query direction.
		This function is so.. messy...
		"""

		if not params:
			return None

		dateTimeParam = None
		tsParam = None

		# Initial query
		if 'ts' in params:
			tsParam = params[ 'ts' ]
		# Query with resume entry available
		elif '$or' in params and 'ts' in params[ '$or' ][ 1 ]:
			tsParam = params[ '$or' ][ 1 ][ 'ts' ]

		if not tsParam:
			return None

		if queryDirection == pymongo.ASCENDING:
			if '$gte' in tsParam:
				dateTimeParam = tsParam[ '$gte' ]
			elif '$gt' in tsParam:
				dateTimeParam = tsParam[ '$gt' ]
		elif queryDirection == pymongo.DESCENDING:
			if '$lte' in tsParam:
				dateTimeParam = tsParam[ '$lte' ]
			elif '$lt' in tsParam:
				dateTimeParam = tsParam[ '$lt' ]

		if dateTimeParam:
			dateTimeParam.replace( tzinfo = None )

		return dateTimeParam

	def _findOne( self, params, queryDirection ):
		"""
		Find just one record based on the given params and sorting direction.
		Return the found entry and its collection
		"""

		# Get the time stamp the query starts from
		dateTimeParam = self._getDateTimeParam( params, queryDirection )

		entry = None
		collToQuery = None
		firstFetch = True

		# Query all of the collections until find one
		while True:
			collToQuery = self._getNextCollToQuery( dateTimeParam,
									queryDirection, collToQuery, firstFetch )
			firstFetch = False

			# Have searched all the possible collections and end up with nothing
			if not collToQuery:
				break

			# if the filter contains appID we cannot use find_one, need to use
			# find to check each return entry until find one entry
			if self._appID != 0:
				for dbEntry in self._db[ collToQuery ].find(
							params,
							sort = [('ts', queryDirection),
							('cnt', queryDirection)] ):
					if not self._filterByRealAppID( dbEntry ):
						continue
					else:
						entry = dbEntry
						break
			else:
				entry = self._db[ collToQuery ].find_one(
							params,
							sort = [('ts', queryDirection),
							('cnt', queryDirection)] )

				# Find one
				if entry:
					break

		return entry
	# findOne

	def getAddressesInfo( self ):
		results = []
		componentsMap = dict( (y, x) for (y, x) in self.components.items() )

		kwargs = {}
		kwargs[ 'start' ] = SERVER_STARTUP_STRING
		kwargs[ 'severities' ] = [ 'INFO' ]
		kwargs[ 'message' ] = "address.*="
		kwargs[ 'casesens' ] = False
		kwargs[ 'categories' ] = ( 'ProcessIP', )
		params = MongoDBLogQueryParams( self.logReader,
											self, kwargs ).params

		dateTimeParam = self._getDateTimeParam( params,
									pymongo.ASCENDING )

		firstFetch = True
		collToQuery = None
		while True:
			collToQuery = self._getNextCollToQuery( dateTimeParam,
								pymongo.ASCENDING, collToQuery, firstFetch )
			firstFetch = False

			# Have searched all the possible collections
			if not collToQuery:
				break

			addressCursor = self._db[ collToQuery ].find( params
						).sort( [( 'ts', pymongo.ASCENDING ),
								( 'cnt', pymongo.ASCENDING )]
						).batch_size( constants.QUERY_BATCH_SIZE )

			for addressEntry in addressCursor:
				sub_kwargs = {}
				entryTime = addressEntry[ 'ts' ].replace( tzinfo = tzutc ) \
							.astimezone( tzlocal )
				sub_kwargs[ 'start' ] = SERVER_STARTUP_STRING
				sub_kwargs[ 'end' ] = time.mktime( entryTime.timetuple() ) + 1
				if 'cpt' in addressEntry:
					sub_kwargs[ 'procs' ] = componentsMap[ \
							addressEntry[ 'cpt' ] ]
				if 'pid' in addressEntry:
					sub_kwargs[ 'pid' ] = addressEntry[ 'pid' ]
				sub_params = MongoDBLogQueryParams( self.logReader, self, \
										sub_kwargs ).params

				messageEntry = self._findOne( sub_params, pymongo.ASCENDING )

				# find the first entry of the app
				if messageEntry:
					messageEntryTime = messageEntry[ 'ts' ].replace( \
								tzinfo = tzutc ).astimezone( tzlocal )

					# check the address entry is given as 5 seconds after
					# app startup because all known apps bind their nubs at
					# startup.
					if (time.mktime( entryTime.timetuple() ) - \
						time.mktime( messageEntryTime.timetuple() )) <= 5:

						if 'cpt' in addressEntry:
							component = self.components[ addressEntry[ 'cpt' ] ]
						else:
							component = ""
						appId = 0
						if 'aid' in addressEntry:
							appId = addressEntry[ 'aid' ]
							if appId == 0 and 'host' in addressEntry and \
								'pid' in addressEntry and 'cpt' in addressEntry:
								appId = self.findAppID(
									addressEntry[ 'host' ],
									addressEntry[ 'pid' ],
									addressEntry[ 'cpt' ] )
						if appId:
							name = "%s%02d" % (component, appId)
						else:
							name = component

						if 'msg' in addressEntry:
							messageText = addressEntry[ 'msg' ].encode(
												self.logReader.getCharset() )
						else:
							messageText = ""

						match = re.search(
									"(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d+)",
									messageText )
						if match == None:
							continue

						address = match.group( 1 )

						if re.search( "external", messageText, re.I ):
							nubtype = "external"
						else:
							nubtype = "internal"

						if 'pid' in addressEntry:
							pid = addressEntry[ 'pid' ]
						else:
							pid = 0

						results.append( (name.lower(), pid, address, nubtype) )

			addressCursor.close()

		return results

	def findAppID( self, host, pid, cpt ):
		"""
		Try to find the appID for the missing appID logs.
		"""

		collToQuery = constants.APPID_COLLECTION_NAME
		appIDParams = {}
		appIDParams[ 'host' ] = { '$in': [ host ] }
		appIDParams[ 'pid' ] = { '$in': [ pid ] }
		appIDParams[ 'cpt' ] = { '$in': [ cpt ] }

		entry = self._db[ collToQuery ].find_one( appIDParams )

		if entry:
			return entry.get( 'aid', 0 )
		else:
			return 0

	# findAppID

# MongoDBLogSingleDBQuery
