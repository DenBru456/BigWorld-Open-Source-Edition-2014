import pymongo
import time
import datetime
import copy
import calendar
import heapq

import logging
log = logging.getLogger( __name__ )

from pycommon import util as pyutil

from base_log_query import BaseLogQuery
from mongodb_log_single_db_query import MongoDBLogSingleDBQuery
from mongodb_log_query_results import MongoDBLogQueryResults
from mongodb_log_query_result import MongoDBLogQueryResult
from mongodb_log_summary_results import MongoDBLogSummaryResults
from log_reader_constants import DEFAULT_DISPLAY_COLUMNS, \
	DEFAULT_CONTEXT, MAX_BUFFERED_RESULTS

import mongodb_constants as constants

try:
	from heapq import merge as heapMerge
except ImportError:
	# Taken directly from the source code for heapq in Python 2.7.
	def heapMerge( *iterables ):
		_heappop, _heapreplace, _StopIteration = heapq.heappop, \
												heapq.heapreplace, StopIteration
		_len = len
		h = []
		h_append = h.append
		for itnum, it in enumerate(map(iter, iterables)):
			try:
				next = it.next
				h_append([next(), itnum, next])
			except _StopIteration:
				pass
		heapq.heapify(h)
		while _len(h) > 1:
			try:
				while 1:
					v, itnum, next = s = h[0]
					yield v
					s[0] = next()       # raises StopIteration when exhausted
					_heapreplace(h, s)  # restore heap condition
			except _StopIteration:
				_heappop(h)             # remove empty iterator
		if h:
			# fast case when only a single iterator remains
			v, itnum, next = h[0]
			yield v
			for v in next.__self__:
				yield v

class MongoDBLogQuery( BaseLogQuery ):
	"""
	Queries a user's log database across all loggerIDs
	"""
	
	def __init__( self, logReader, params, resultLimit = None,
				truncate = False ):
		super( BaseLogQuery, self ).__init__()

		self.logReader = logReader
		self._rawParams = params

		self.columnFilter = DEFAULT_DISPLAY_COLUMNS
		self._resultLimit = resultLimit

		# This is to identify the query is happening in which order
		self.querySort = pymongo.ASCENDING

		# serveruser will be removed from params when initing
		# MongoDBLogQueryParams, else it will muck up the query.
		# It's still needed however, so keep it in its own variable.
		self.serverUser = params.get( 'serveruser' )

		self._lastFetchTime = time.time()

		# Get the max length of hostnames, used for log query result formating
		self._refreshMaxHostName()
				
		# A dict of loggerID and its query objects		
		self._dbQueries = {}		
	# __init__
	
	
	def streamResults( self, outputStream, maxLines = None,
						showMetadata = False ):
		# Fallback to the query result limit if it is set.
		if maxLines is None:
			if self._resultLimit:
				maxLines = self._resultLimit
			else:
				# If no size limit, output all the result
				maxLines = constants.QUERY_NO_LIMIT

		resultCount = [0]

		self.fetchNextResultSet( resultLimit = maxLines,
								outputStream = outputStream,
								showMetadata = showMetadata,
								resultCount = resultCount )

		return resultCount[ 0 ]
	# streamResults


	def fetchNextResultSet( self, resultLimit = None, queryStatus = None,
				outputStream = None, showMetadata = False, resultCount = None ):
		"""
		Fetch next result set, until resultLimit is reached or databases have
		been exhausted.
		
		If resultLimit is 0, it means no limit for MongoDB.
		
		If queryStatus is not none, append the result as a dict to it. This is
		usually used by Log Viewer.
		
		If outputStream is not none, write the result to this stream. This is
		usually for mlcat.py.
		
		If resultCount is not none, set the result count to its first item.
		"""
		# Get the latest databases info of this server user
		self._refreshUserDB()

		if resultLimit is None:
			resultLimit = self._resultLimit or MAX_BUFFERED_RESULTS

		# we store the query object in a list with the same order as cursors for
		# efficient look up by avoding looking up in dict
		queries = []
		cursors = []
		for loggerID, query in self._dbQueries.iteritems():
			queries.append( query )
			cursors.append( query.getCursor( resultLimit ) )
		
		logQueryResults = MongoDBLogQueryResults()

		mergedCursor = self._mergedCursor( *cursors, sort = self.querySort,
										limit = resultLimit )

		for counter, entry in enumerate( mergedCursor ):
			dbEntry, collName = entry[ 0 ]
			cursorIndex = entry[ 1 ]
			query = queries[ cursorIndex ]
			logQueryResult = MongoDBLogQueryResult( query, dbEntry,
												self._maxHostnamesLen )
			
			queries[ cursorIndex ].setResumePoint( dbEntry, collName )

			if queryStatus:
				queryStatus.appendLogEntry( logQueryResult.asDict() )			
			elif outputStream:
				logQueryResult.writeToStream( outputStream, showMetadata )
			else:
				logQueryResults.appendResult( logQueryResult )
				
			if resultCount:
				resultCount[ 0 ] = counter

		# Explicitly close open cursors
		for query in queries:
			query.closeActiveCursor()

		self._lastFetchTime = time.time()

		return logQueryResults
	# fetchNextResultSet


	def endFetch( self ):
		"""
		This is a stub function.
		"""
		pass


	def fetchContext( self, contextLines = None, fetchForwardContext = True ):
		"""
		Fetch the context of a specific time point.

		It firstly finds one record close to the query time point, then queries
		backwards from that time point and then queries forwards from that
		point. When query back, just query exactly the number of contextLines,
		when querying forward, query contextLines + 1, the extra 1 is for the
		one closest to the query parameters.
		"""
		# Still no context lines? Use the default
		if contextLines < 0:
			contextLines = DEFAULT_CONTEXT

		results = MongoDBLogQueryResults()

		self._refreshUserDB()

		# Get the first matching result to find the closest time point
		self.querySort = pymongo.ASCENDING
		dbEntry = self._findOne( pymongo.ASCENDING )
		if not dbEntry:
			# No results returned. Try to begin at the very latest entry in
			# the DB (not matching time). This may be because the time
			# specified is higher than the latest entry in the DB.
			dbEntry = self._findOne( pymongo.DESCENDING, anyTime = True )
			if not dbEntry:
				# definitely no results matching
				return results

		startTime = dbEntry[ 'ts' ]
		startCounter = dbEntry[ 'cnt' ]

		# Now go backwards
		if contextLines > 0:
			self.querySort = pymongo.DESCENDING
			for query in self._dbQueries.values():
				query.resetTimeParam( startTime, startCounter, pymongo.DESCENDING,
				                      False )

			# backwardsResults is iteratable but not sequence, so we have to
			# transform it to list before reversing it.
			backwardsResults = self.fetchNextResultSet( contextLines )
			lst = list( backwardsResults )
			lst.reverse()

			results += lst

		# reset query time parameters
		self.querySort = pymongo.ASCENDING
		for query in self._dbQueries.values():
				query.resetTimeParam( startTime, startCounter,
				                      pymongo.ASCENDING, True )

		# Now go forward if required. Query contextLines + 1, the extra 1 is to
		# include the one closest to the query parameters as the middle point.
		if fetchForwardContext:
			results += self.fetchNextResultSet( contextLines + 1 )

		return results
	# fetchContext


	# Fetch and display contextLines before current time, then start tailing. 
	# Query every interval seconds getting latest lines since last line of 
	# previous query and streaming them.
	def tail( self, outputStream, interval, contextLines = None,
			showMetadata = False ):

		if contextLines:
			if contextLines > 0:
				# Remove one because streamResults shows it instead.
				contextLines -= 1
			results = self.fetchContext( contextLines,
											fetchForwardContext = False )
			for result in results:
				result.writeToStream( outputStream, showMetadata )

		while True:
			self.streamResults( outputStream, showMetadata = showMetadata )
			time.sleep( interval )
	# tail


	def logSummary( self, summarizedColumns, group = None, showProgress = False ):
		"""
		Returns a list of strings and counts summarised by summarizedColumns
		"""

		self._refreshUserDB()

		# Get total count first. Very time-consuming.
		# TODO - should find some more efficient way to do this or not show
		# progress at all.
		totalCount = 0

		for query in self._dbQueries.values():
			totalCount += query.resultCount()

		# We don't show progress for less than 10000 results
		showProgress = showProgress and totalCount > 10000

		# A mapping of groupkey -> [result, count]
		summaryGroups = {}

		# Initialise progress
		if showProgress:
			progress = pyutil.PercentComplete(
				"Processing %d messages" % totalCount, totalCount )

		currentCount = 0
		for query in self._dbQueries.values():
			for dbEntry, collName in query.getCursor(
													constants.QUERY_NO_LIMIT ):
				query.setResumePoint( dbEntry, collName )
				currentCount += 1
				
				logQueryResult = MongoDBLogQueryResult( query, dbEntry )
				summaryGroup, summaryLogLine = \
					logQueryResult.processSummaryDisplay( summarizedColumns )

				# Increment count for that group
				rec = summaryGroups.setdefault( summaryLogLine,
											[summaryGroup, 0] )
				rec[ 1 ] += 1

				# Update progress
				if showProgress:
					progress.update( currentCount )

		histogramResults = sorted( summaryGroups.values(),
				key = lambda (result, count): count,
				reverse = True )

		if group:
			inReverse = (group == "severity")
			histogramResults.sort(
					key = lambda( result, count ): result[ group ],
					reverse = inReverse )

		summaryResults = MongoDBLogSummaryResults( self )

		for resultDict, count in histogramResults:
			if group:
				summaryResults.addSummaryResult( resultDict, count,
											resultDict[ group ] )
			else:
				summaryResults.addSummaryResult( resultDict, count, None )

		return summaryResults


	def setColumnFilter( self, columnList ):
		# Restrict output strings.
		self.columnFilter = columnList


	def setTimeoutDetails( self, timeoutDetails ):
		"""TODO"""
		#self.timeoutDetails = timeoutDetails
	# setTimeoutDetails


	def moreResultsAvailable( self, refreshQuery = False ):
		"""
		Check if there is more result available.
		
		Return true if any of the underlying query returns true.
		"""
		self._refreshUserDB()
		for query in self._dbQueries.values():
			if query.moreResultsAvailable( refreshQuery ):
				return True

		return False

	# moreResultsAvailable


	def inReverse( self ):
		return self.querySort == pymongo.DESCENDING


	def getLastFetchTime( self ):
		return self._lastFetchTime


	def getAddressesInfo(self):
		self._refreshUserDB()

		results = set()
		for loggerID, query in self._dbQueries.iteritems():
			for result in query.getAddressesInfo():
				# check if the address info is duplicate
				if result not in results:
					results.add( result )

		self._lastFetchTime = time.time()

		return sorted( results )

	# getAddressesInfo


	def _refreshUserDB( self ):
		"""
		Read the list of databases of this user and create corresponding query
		object if it's not created, otherwise refresh the data of it. 
		"""

		for dbName in self.logReader.userDatabaseNameIter( self.serverUser ):
			loggerID = self.logReader.parseDatabaseInfo( dbName ).get( 'logger' )

			if loggerID in self._dbQueries:
				self._dbQueries[ loggerID ].refreshData()
			else:
				self._dbQueries[ loggerID ] = MongoDBLogSingleDBQuery(
					self, loggerID, copy.deepcopy( self._rawParams ),
					self._resultLimit )

	# _refreshUserDB


	def _refreshMaxHostName( self ):
		"""
		Refresh the max length of hostnames. This will be used in formating
		query result.
		"""
		self.hostnames = self.logReader.getHostnames()
		self._maxHostnamesLen = \
				max( len( str( x ) ) for x in self.hostnames.values() )

	# _refreshMaxHostName


	def _findOne( self, queryDirection, anyTime = False ):
		"""
		Find just one record based on the given params and sorting direction.

		Return the earliest one if sort is ascending, otherwise the latest one.
		"""

		entries = [ query.findOne( queryDirection, anyTime ) \
					for query in self._dbQueries.values() ]

		entry = None
		for tmpEntry in filter( None, entries ):
			if entry is None:
				entry = tmpEntry
				continue

			if queryDirection == pymongo.ASCENDING:
				diffFn = lambda x, y: x < y
			else:
				diffFn = lambda x, y: x > y

			if diffFn( tmpEntry.get( 'ts' ), entry.get( 'ts' ) ) \
				or (
					tmpEntry.get( 'ts' ) == entry.get( 'ts' ) and
				    diffFn( tmpEntry.get( 'cnt' ), entry.get( 'cnt' ) )
				):
				entry = tmpEntry

		return entry

	# _findOne


	def _heapWrapper( self, iterator, num, multiplier ):
		"""
		Wrap an iterator so that every entry is formatted in a way that allows it
		to sort correctly in the heap.
		"""
		
		# The entry is a tuple of (dbEntry, collection name)
		for entry in iterator:
			dateObject = entry[0].get( 'ts' )
			if not dateObject:
				# Something is wrong with this record, as this should never happen
				continue
			ts = calendar.timegm( dateObject.timetuple() ) + \
				dateObject.microsecond * 1e-6
	
			yield (ts * multiplier, num, entry)


	def _mergedCursor( self, *cursors, **settings ):
		"""
		Take iterators of mongoDB records and returns a merged result of entries
		in the format [  original entry, iterator number].
	
		Optional keyword arguments:
		- limit: the number of records to return. Returns all if absent or <= 0
		- sort: pymongo.ASCENDING (default) or pymongo.DESCENDING. If DESCENDING,
				the input iterator MUST be sorted in descending order, else the
				results will be incorrect.
		"""
		limit = settings.get( 'limit', constants.QUERY_NO_LIMIT )
		sortMultiplier = 1
		if settings.get( 'sort', pymongo.ASCENDING ) == pymongo.DESCENDING:
			sortMultiplier = -1
	
		data = [self._heapWrapper( it, num, sortMultiplier ) \
					for num, it in enumerate( cursors )]
		for counter, entry in enumerate( heapMerge( *data ) ):
			# The entry is a tuple of (sorting field, index of the cursor, 
			# query entry returned by the cursor)
			yield ( entry[2], entry[1] )
	
			if limit > 0 and counter + 1 == limit:
				break

# MongoDBLogQuery
