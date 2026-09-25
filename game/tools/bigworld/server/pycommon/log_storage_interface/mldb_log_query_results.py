# TODO: Document this file and its classes and methods

from base_log_query_results import BaseLogQueryResults
from mldb_log_query_result import MLDBLogQueryResult

class MLDBLogQueryResults( BaseLogQueryResults ):

	def __init__( self, query ):
		BaseLogQueryResults.__init__( self )
		self._query = query


	#
	# MLDB-only implementation functions (not required at abstraction layer).
	#

	def addQueryResult( self, pyQueryResult ):
		logQueryResult = MLDBLogQueryResult( self._query, pyQueryResult )
		self._results.append( logQueryResult )

# MLDBLogQueryResults
