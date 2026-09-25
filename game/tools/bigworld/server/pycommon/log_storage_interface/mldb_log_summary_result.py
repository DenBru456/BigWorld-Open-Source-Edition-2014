# TODO: Document this file and its classes and methods

from base_log_query_result import BaseLogQueryResult

class MLDBLogSummaryResult( BaseLogQueryResult ):

	def __init__( self, query, pyQueryResult, count, group ):
		BaseLogQueryResult.__init__( self )

		self._query = query
		self._pyQueryResult = pyQueryResult
		self._count = count
		self._group = group


	#
	# Abstract function implementations - required by BaseLogQueryResult
	#

	def asDict( self ):
		return {
			'summaryText': self._pyQueryResult.format( self._query.filterMask ),
			'count': self._count,
			'group': self._group
		}

# MLDBLogSummaryResult
