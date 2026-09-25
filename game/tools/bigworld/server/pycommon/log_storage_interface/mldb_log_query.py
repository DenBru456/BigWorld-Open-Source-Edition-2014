# TODO: Document this file and its classes and methods

import bwsetup
bwsetup.addPath( "../.." )

# Standard python modules
import time

# Local modules
from base_log_query import BaseLogQuery
from mldb_log_query_params import MLDBLogQueryParams
from mldb_log_query_results import MLDBLogQueryResults
from mldb_log_query_result import MLDBLogQueryResult
from mldb_log_summary_results import MLDBLogSummaryResults
from iterable import iterable
from log_reader_constants import (DEFAULT_CONTEXT, MAX_BUFFERED_RESULTS,
ORDERED_OUTPUT_COLUMNS)

# Other modules
import pycommon.bwlog as bwlog_module
from pycommon.exceptions import QueryParamException

_bwlog = bwlog_module._bwlog

class MLDBLogQuery( BaseLogQuery ):

	# map of log output column name to mask
	OUTPUT_COLUMNS_TO_MASK = {
		"date"			: _bwlog.SHOW_DATE,
		"time"			: _bwlog.SHOW_TIME,
		"host"			: _bwlog.SHOW_HOST,
		"serveruser"	: _bwlog.SHOW_USER,
		"uid"			: _bwlog.SHOW_USER,
		"pid"			: _bwlog.SHOW_PID,
		"process"		: _bwlog.SHOW_PROCS,
		"appid"			: _bwlog.SHOW_APPID,
		"source"		: _bwlog.SHOW_MESSAGE_SOURCE_TYPE,
		"severity"		: _bwlog.SHOW_SEVERITY,
		"category"		: _bwlog.SHOW_CATEGORY,
		"message"		: _bwlog.SHOW_MESSAGE,
	}

	def __init__( self, logReader, params, resultLimit = None,
				truncate = False ):
		# Defaults
		self._resumeQuery = None
		self._lastFetchTime = time.time()
		self.filterMask = _bwlog.SHOW_ALL
		self._timeoutDetails = None
		self._nextFetchAddr = None
		self.__logDB = None

		# Arguments
		self.logReader = logReader
		self._resultLimit = resultLimit
		self._truncate = truncate

		self._logQueryParams = MLDBLogQueryParams( self, params )
	# __init__


	def getLogDB( self ):
		"""
		If a previously used logDB object still exists and has not been deleted,
		this method will return the object, otherwise it will create a new one.

		As the DB may be disconnected (and self.__logDB cleared) between queries
		to reduce file handle usage, this method is a safety wrapper and should
		always be the only access point to get and use a DB connection.
		self.__logDB should never be used directly.
		"""
		if not self.__logDB:
			self.__logDB = self.logReader.getNewLogDBConnection()

		return self.__logDB
	# getLogDBConnection


	def setTimeoutDetails( self, timeoutDetails ):
		self._timeoutDetails = timeoutDetails


	def setColumnFilter( self, columnFilter ):
		# The easiest way to validate the provided columns is by attempting a
		# conversion.
		self.filterMask = self.columnFilterToMask( columnFilter )


	def streamResults( self, outputStream, maxLines = None,
						showMetadata = False ):
		"""
		This method sends results directly to the specified output stream rather
		than returned as part of a set in memory. It is vastly more memory
		efficient than storing the results in a buffer, and is a safety measure
		mainly used by mlcat to prevent storing huge (potentially millions) sets
		of log lines in memory when a filter is not detailed enough.

		It also has the added bonus of providing instant result output in mlcat
		when performing a normal cat on a large dataset, rather than waiting
		minutes for everything to process without displaying any results.

		The return value is the number of lines written.
		"""

		pyQuery = self._getQuery()
		resultCount = self._streamMLDBResults( pyQuery, outputStream,
												maxLines, showMetadata )
		self._lastFetchTime = time.time()

		return resultCount


	def fetchNextResultSet( self, resultLimit = None, queryStatus = None ):
		"""
		This function returns the next set of results as a list. It must be used
		carefully and only with known limits, otherwise very large logs
		(millions of entries) can consume all the memory.

		Not suitable for a simple "cat" to stdout.

		Passing resultLimit will override the default result limit for the
		query - useful for resuming partially-polled results from timed-out
		fetches.
		"""
		if self._nextFetchAddr:
			self._logQueryParams.queryParams[ 'startaddr' ] = self._nextFetchAddr

		if resultLimit == None:
			resultLimit = self._resultLimit

		pyQuery = self._getQuery()
		try:
			results = self._processMLDBResults( pyQuery, maxLines = resultLimit )
		finally:
			self._nextFetchAddr = pyQuery.tell()
		self._lastFetchTime = time.time()
		
		if queryStatus:
			queryStatus.appendLogEntries( results )
		
		return results
	# fetchNextResultSet


	def endFetch( self ):
		"""
		For MLDB, if we pause or stop the query we need to release the DB
		connections otherwise we run out of file handles.

		This is an unfortunate necessity resulting from bwlog not being aware of
		log rotation and therefore not releasing files, resulting in strange
		fetch and resume behaviour (as some files may exist and others may not).
		"""
		self._resumeQuery = None
		self.__logDB = None


	def getLastFetchTime( self ):
		return self._lastFetchTime


	def fetchContext( self, contextLines = None, fetchForwardContext = True ):
		# Still no context lines? Use the default
		if not contextLines:
			contextLines = DEFAULT_CONTEXT

		# Need to increment to get expected behaviour
		backContext = contextLines + 1

		forwardContext = contextLines
		if forwardContext < 0:
			forwardContext = 0

		# Get backwards context and convert. Note the backwards context function
		# is what performs the maxLines limitation here (so as not to fetch all
		# the way back to the beginning)
		priorPyResults, nextQuery = \
			self.getLogDB().fetchContext( self._logQueryParams.queryParams,
												max = backContext )
		results = self._processMLDBResults( priorPyResults )

		self._resumeQuery = nextQuery
		self._lastFetchTime = time.time()

		if fetchForwardContext:
			# Get forwards context and convert.
			results += self._processMLDBResults( nextQuery,
												maxLines = forwardContext )
			self._lastFetchTime = time.time()

		return results
	# fetchContext


	def tail( self, outputStream, interval, contextLines = None,
				showMetadata = False ):
		# Display some context
		if contextLines:
			context, query = self.getLogDB().fetchContext(
					self._logQueryParams.queryParams, max = contextLines )
			results = self._processMLDBResults( context )
			for result in results:
				result.writeToStream( outputStream, showMetadata )

		# Now start tailing
		while True:
			query.waitForResults( interval )
			results = self._processMLDBResults( query )
			for result in results:
				result.writeToStream( outputStream, showMetadata )

		return True
	# tail


	def logSummary( self, summaryFields, group = None, showProgress = False ):
		"""
		Returns a list of strings and counts summarised by summaryFields
		"""
		# NOTE: MLDB uses 'stringOffset' instead of 'message' when calculating
		# summaries based on log message because they are just as unique and
		# much faster for calculating hash values.
		if "message" in summaryFields:
			summaryFields[ summaryFields.index( "message" ) ] = "stringOffset"

		histogramResults = self.getLogDB().histogram( summaryFields,
								showProgress, **self._logQueryParams.queryParams )

		if group:
			inReverse = (group == "severity")
			histogramResults.sort(
					key = lambda( result, count ): getattr( result, group ),
					reverse = inReverse )

		summaryResults = MLDBLogSummaryResults( self )

		# convert results to an abstractable format (from pyQueryResult)
		for pyQueryResult, count in histogramResults:
			if group:
				summaryResults.addSummaryResult( pyQueryResult, count,
											getattr( pyQueryResult, group ) )
			else:
				summaryResults.addSummaryResult( pyQueryResult, count, None )

		return summaryResults


	def moreResultsAvailable( self, refreshQuery = False ):
		if not self._resumeQuery:
			# Initial state. No fetches have been configured yet - always treat
			# it as if there are more results available to force at least one
			# fetch operation in the future.
			#
			# It is preferable to do this rather than creating a new pyQuery
			# object because this object may not be fully configured for
			# fetching yet (eg. columnFilters may not yet be configured).
			return True

		if refreshQuery:
			# resume is used for live mode queries and will attempt to
			# search for more results
			self._resumeQuery.resume()

		return self._resumeQuery.hasMoreResults()


	def getProgress( self ):
		if not self._resumeQuery:
			return None
		else:
			return self._resumeQuery.getProgress()


	def inReverse( self ):
		if not self._resumeQuery:
			return False
		else:
			return self._resumeQuery.inReverse()

	#
	# MLDB-only implementation functions (not abstracted)
	#

	def _getQuery( self ):
		if self._resumeQuery:
			# MLDB will work more efficiently if there is already a query saved
			# to continue on with.
			pyQuery = self._resumeQuery
		else:
			pyQuery = self.getLogDB().fetch( **self._logQueryParams.queryParams )
			self._resumeQuery = pyQuery

		if self._timeoutDetails:
			pyQuery.setTimeout( self._timeoutDetails[ 'timeout' ],
								self._timeoutDetails[ 'callback' ] )

		return pyQuery


	def _streamMLDBResults( self, pyQuery, outputStream, maxLines = None,
			showMetadata = False ):
		"""
		Send results directly to the output stream rather than returned as part
		of an MLDBLogQueryResults set. This is a safety measure mainly used by
		mlcat to prevent buffering huge (potentially millions) sets of log lines
		in memory. It also has the bonus of providing instant result output in
		mlcat when performing a normal cat.

		The return value is the number of lines written.
		"""
		if not pyQuery:
			return 0

		self._setAddressTranslations()

		# MLDB results are returned in PyQueryResult format. We need to format
		# them as something meaningful to the client (as well as apply any
		# address translations).

		resultCount = 0
		if not maxLines and self._resultLimit:
			maxLines = self._resultLimit

		for pyQueryResult in pyQuery:
			# Let MLDBLogQueryResult class format into an acceptable dictionary
			# that the abstract interface already knows how to handle
			logResult = MLDBLogQueryResult( self, pyQueryResult )
			logResult.writeToStream( outputStream, showMetadata )

			resultCount += 1
			if (maxLines > 0) and (resultCount > (maxLines-1) ):
				break

		return resultCount
	# _streamMLDBResults


	def _processMLDBResults( self, pyQuery, maxLines = None ):
		"""
		Return the next set of results as a jsonifyable/tuple-able object. Use
		this feature carefully and only with known limits otherwise very large
		logs (millions of entries) can consume large amounts of server memory.

		Not suitable for a simple "cat" to stdout.
		"""
		logQueryResults = MLDBLogQueryResults( self )

		if not pyQuery:
			return logQueryResults
		if not maxLines:
			if (not self._resultLimit) or \
				(self._resultLimit > MAX_BUFFERED_RESULTS):
				maxLines = MAX_BUFFERED_RESULTS
			else:
				maxLines = self._resultLimit

		self._setAddressTranslations()

		# MLDB results are returned in PyQueryResult format. We need to format
		# them as something meaningful to the client (as well as apply any
		# address translations).

		resultCount = 0

		startTime = time.time()
		for pyQueryResult in pyQuery:
			logQueryResults.addQueryResult( pyQueryResult )

			resultCount += 1
			if (maxLines > 0) and (resultCount > (maxLines-1) ):
				break

			if self._timeoutDetails and \
				((time.time() - startTime) > self._timeoutDetails[ 'timeout' ]):
				break

		return logQueryResults
	# _processMLDBResults


	def _setAddressTranslations( self ):
		translate = self._logQueryParams.getOriginalParamValue( "translate" )
		if translate:
			uid = self._logQueryParams.getParamValue( "uid" )
			translateFrom = self._logQueryParams.getParamValue( "startaddr" )
			self.getLogDB().addAddressTranslations( uid, translateFrom )
	# setAddressTranslations


	@classmethod
	def columnFilterToMask( cls, columnFilter ):
		showMask = 0
		if not columnFilter:
			return _bwlog.SHOW_ALL

		for s in iterable( columnFilter ):
			mask = cls.OUTPUT_COLUMNS_TO_MASK.get( s )
			if mask:
				showMask |= mask
			else:
				raise QueryParamException(
					"Unknown column name '%s', valid names are: %s" % 
					(s, ORDERED_OUTPUT_COLUMNS),
					paramName = 'show', paramValue = s )
		return showMask
	# columnFilterToMask


# MLDBLogQuery
