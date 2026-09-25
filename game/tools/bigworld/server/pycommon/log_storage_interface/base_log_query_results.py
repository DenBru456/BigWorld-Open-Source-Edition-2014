# TODO: Document this file and its classes and methods

class BaseLogQueryResults( object ):

	def __init__( self ):
		self._results = []


	def __iter__( self ):
		return self._results.__iter__()


	def __iadd__( self, other ):
		for result in other:
			self._results.append( result )
		return self

	
	def size( self ):
		return len( self._results )


	def asDicts( self ):
		resultList = []
		for result in self._results:
			resultList.append( result.asDict() )
		return resultList


# BaseLogQueryResults

