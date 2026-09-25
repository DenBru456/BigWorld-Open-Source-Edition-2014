# TODO: Document this file and its classes and methods

from base_log_query_results import BaseLogQueryResults
from mongodb_log_query_result import MongoDBLogQueryResult

class MongoDBLogQueryResults( BaseLogQueryResults ):

	def __init__( self, query = None ):
		BaseLogQueryResults.__init__( self )
		self._query = query
	# __init__


	def addQueryResult( self, dbEntry ):
		logQueryResult = MongoDBLogQueryResult( self._query, dbEntry )
		self._results.append( logQueryResult )
		return logQueryResult
	# addQueryResult
	
	def appendResult( self, logQueryResult ):
		self._results.append( logQueryResult )
	
# MongoDBLogQueryResults
