import time
from bwtest import TestCase
from helpers.cluster import ClusterController


class ApplicationTimerCallBacksTest( TestCase ):
	
	
	name = "ApplicationTimerCallBacks"
	description = "Tests the callback from addTimer method"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		snippet = """
		from bwdebug import DEBUG_MSG
		global count
		count = 5
		def timerCB( timerID, userArg ):
			global count
			DEBUG_MSG( "addTimer: %d (ID %d, arg %d)" % ( count, timerID, userArg ) )
			count -= 1
			if count == 0:
				BigWorld.delTimer( timerID )
				srvtest.finish( count )

		BigWorld.addTimer( timerCB, 0, 1, 5 )
		"""
		
		ret = self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		self.assertTrue( ret == 0,
						"addTimer callback wasn't called often enough" )