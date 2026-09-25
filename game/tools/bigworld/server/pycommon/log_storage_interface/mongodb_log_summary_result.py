# TODO: Document this file and its classes and methods

from base_log_query_result import BaseLogQueryResult

class MongoDBLogSummaryResult( BaseLogQueryResult ):

	SUMMARY_DISPLAY = [
		"time",
		"host",
		"username",
		"pid",
		"appid",
		"component",
		"severity",
		"message",
	]

	def __init__( self, query, dictResult, count, group ):
		BaseLogQueryResult.__init__( self )

		self._query = query
		self.dictResult = dictResult
		self._count = count
		self._group = group


	#
	# Abstract function implementations - required by BaseLogQueryResult
	#

	def asDict( self ):
		summary_text = ' '.join( [ self.dictResult[ col ] for col in \
				self.SUMMARY_DISPLAY if col in self.dictResult ] ) + '\n'
		return {
			'summaryText': summary_text,
			'count': self._count,
			'group': self._group
		}

# MongoDBLogSummaryResult
