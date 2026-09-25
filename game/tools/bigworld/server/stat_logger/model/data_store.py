
class DataStore( object ):
	"""Parent class for the backend stores of StatLogger
		
		"""

	def __init__( self, storeConfig, prefTree ):
		if not storeConfig or not storeConfig.enabled:
			raise Exception( "Data store is not enabled." )

		self.storeConfig = storeConfig
		self.prefTree = prefTree
		

	def finalise( self, quickTerminate = True ):
		raise NotImplementedError( "This function should be implemented" )


	def isOk( self ):
		raise NotImplementedError( "This function should be implemented" )


	@classmethod
	def testConnection( cls, storeConfig ):
		raise NotImplementedError( "This function should be implemented" )
		

	def logNewMachine( self, machine ):
		raise NotImplementedError( "This function should be implemented" )


	def logNewProcess( self, process, userName ):
		raise NotImplementedError( "This function should be implemented" )


	def logNewUser(self, user):
		raise NotImplementedError( "This function should be implemented" )


	def logProcessStats( self, processStats, tick ):
		raise NotImplementedError( "This function should be implemented" )


	def logMachineStats( self, machineStats, tick ):
		raise NotImplementedError( "This function should be implemented" )

		
	def delProcess( self, process ):
		raise NotImplementedError( "This function should be implemented" )
		
		
	def consolidateStats( self, tick, shouldLimitDeletion=True ):
		raise NotImplementedError( "This function should be implemented" )
		
	
	def addTick( self, tick, tickTime ):
		raise NotImplementedError( "This function should be implemented" )

# class DataStore

