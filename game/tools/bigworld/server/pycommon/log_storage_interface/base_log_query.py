"""
This class provides an abstract querying interface for log entries.

Its main features are to provide the ability to specify a set of parameters,
fetch the next batch of query results matching the specified params, determine
whether there are more results to retrieve and perform/provide a log summary
based on its creation parameters.
"""

class BaseLogQuery( object ):
	"""The abstract log query class."""

	#
	# Abstract methods - must be implemented by subclasses
	#

	def getID( self ):
		"""
		This method returns a unique identifier for this object.

		Although it is not necessary to override, it may be overridden as long
		as the overriding method returns a unique identifier for the object
		which remains consistent throughout its life.
		"""
		return id( self )
	# getID


	def setTimeoutDetails( self, timeoutDetails ):
		"""
		TODO: document this
		"""
		raise NotImplementedError(
			"BaseLogQuery.setTimeoutDetails method not implemented. "
			"Unable to call abstract method." )
	# setTimeoutDetails


	def setColumnFilter( self, columnFilter ):
		"""
		An abstract method which when overridden should apply a filter on the
		resulting columns to be returned.
		
		The filter may only be set once, before the first call to the fetch
		method. Subsequent calls to set the filter should be ignored by deriving
		classes.

		This method will be deprecated in future releases as the client tools
		are modified to perform their own filtering.
		"""
		raise NotImplementedError(
			"BaseLogQuery.setColumnFilter method not implemented. "
			"Unable to call abstract method." )
	# setColumnFilter


	def streamResults( self, outputStream, maxLines = None,
		showMetadata = False ):
		"""
		An abstract method which sends results directly to the specified output
		stream rather than returned as part of a set in memory. It is vastly
		more memory efficient than storing the results in a buffer, and is a
		safety measure mainly used by mlcat to prevent storing huge (potentially
		millions) sets of log lines in memory when a filter is not detailed
		enough.

		It also has the added bonus of providing instant result output in mlcat
		when performing a normal cat on a large dataset, rather than waiting
		for everything to process without displaying any results.

		The return value is the number of lines written.
		"""
		raise NotImplementedError(
			"BaseLogQuery.streamResults method not implemented. "
			"Unable to call abstract method." )
	# streamResults


	def fetchNextResultSet( self ):
		"""
		An abstract method which when overridden should fetch a results set
		(matching the params and size limit passed in to the constructor) as an
		object that implements BaseLogQueryResults.

		This method must be used carefully and only with known limits,
		otherwise very large logs (millions of entries) can consume all the
		memory.

		Subsequent calls to this method will return more results continuing on
		from the previous set.
		"""
		raise NotImplementedError(
			"BaseLogQuery.fetchNextResultSet method not implemented. "
			"Unable to call abstract method." )
	# fetchNextResults


	def endFetch( self ):
		"""
		This method is used to trigger actions required at an end of fetch
		(such as closing file handles if necessary).
		"""
		raise NotImplementedError(
			"BaseLogQuery.endFetch method not implemented. "
			"Unable to call abstract method." )
	# endFetch


	def moreResultsAvailable( self, refreshQuery = False ):
		"""
		An abstract method which when overridden should return a boolean value
		indicating whether there are more results to fetch matching the query
		parameters.

		If the refreshQuery parameter is true then the object will attempt to
		refresh the existing query if there is one. Utilised by live mode
		polling.
		"""
		raise NotImplementedError(
			"BaseLogQuery.moreResultsAvailable method not implemented. "
			"Unable to call abstract method." )
	# moreResultsAvailable


	def getProgress( self ):
		"""
		An abstract method which if supported by the DB implementation
		should return a tuple containing the number of results returned, as well
		as the total number of results matching the fetch query.
		"""
		raise NotImplementedError(
			"BaseLogQuery.getProgress method not implemented. "
			"Unable to call abstract method." )
	# getProgress


	def inReverse( self ):
		"""
		An abstract method which should return whether the query results are
		being reported in reverse.
		"""
		raise NotImplementedError(
			"BaseLogQuery.inReverse method not implemented. "
			"Unable to call abstract method." )
	# inReverse


	def getLastFetchTime( self ):
		"""
		An abstract method which when overridden should return a timestamp
		indicating the last fetch time for this query.
		"""
		raise NotImplementedError(
			"BaseLogQuery.getLastFetchTime method not implemented. "
			"Unable to call abstract method." )
	# getLastFetchTime


	#
	# Functionality required to keep command-line tools backwards compatible.
	#

	def fetchContext( self, contextLines = None, fetchForwardContext = True ):
		"""
		An abstract method which when overridden should fetch the first result
		matching the query parameters and provide lines of context both before
		and after the matching line. The results will be sent to the output
		location, which can either be a buffer (ie. a list object) or a
		filestream.

		If the DB implementation cannot perform this function it should raise
		an exception. It is up to the client to handle the exception correctly
		(or to avoid calling this function in the first place).
		"""
		raise NotImplementedError(
			"BaseLogQuery.fetchContext method not implemented. "
			"Unable to call abstract method." )
	# fetchContext


	def tail( self, outputStream, interval, contextLines = None, \
			showMetadata = False ):
		"""
		An abstract method which when overridden should begin reporting logs to
		the output stream provided in the manner of "tail -f". The database
		should only be queried at intervals specified by 'interval'.

		If the database supports context functionality then it should initially
		report 'contextLines' lines of context before the end of the log.
		"""
		raise NotImplementedError(
			"BaseLogQuery.tail method not implemented. "
			"Unable to call abstract method." )
	# tail


	def logSummary( self, summaryFields, group = None, showProgress = False ):
		"""
		An abstract method which when overridden should return a list of tuples
		of the format (group, result, count).

		The result in each tuple is the first one encountered from that group,
		and is only included so that it can be printed out nicely.
		"""
		raise NotImplementedError(
			"BaseLogReader.logSummary method not implemented. "
			"Unable to call abstract method." )
	# logSummary

# BaseLogQuery
