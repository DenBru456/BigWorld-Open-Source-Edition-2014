# TODO: Document this file and its classes and methods

from base_log_query_results import BaseLogQueryResults
from mongodb_log_summary_result import MongoDBLogSummaryResult

class MongoDBLogSummaryResults( BaseLogQueryResults ):

	def __init__( self, query ):
		BaseLogQueryResults.__init__( self )
		self._query = query


	def addSummaryResult( self, dictResult, count, group ):
		logSummaryResult = MongoDBLogSummaryResult( self._query,
			dictResult, count, group )
		self._results.append( logSummaryResult )

# MongoDBLogSummaryResults
