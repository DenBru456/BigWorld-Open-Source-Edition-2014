# TODO: Document this file and its classes and methods

from base_log_query_results import BaseLogQueryResults
from mldb_log_summary_result import MLDBLogSummaryResult

class MLDBLogSummaryResults( BaseLogQueryResults ):

	def __init__( self, query ):
		BaseLogQueryResults.__init__( self )
		self._query = query


	#
	# MLDB-only implementation functions (not required at abstraction layer).
	#

	def addSummaryResult( self, pyQueryResult, count, group ):
		logSummaryResult = MLDBLogSummaryResult( self._query,
			pyQueryResult, count, group )
		self._results.append( logSummaryResult )

# MLDBLogSummaryResults
