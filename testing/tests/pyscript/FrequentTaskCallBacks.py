import time
from bwtest import TestCase
from helpers.cluster import ClusterController


class FrequentTaskCallBacksTest( TestCase ):
	
	
	name = "FrequentTaskCallBacks"
	description = "Tests the callback from addFrequentTask method"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		snippet = """
		global count
		count = 5
		def frequent():
			global count
			count -= 1
			if count == 0:
				srvtest.finish( count )
			return count == 0

		BigWorld.addFrequentTask( frequent, 0 )
		"""
		
		ret = self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		self.assertTrue( ret == 0, 
						"addFrequentTask callback was not called often enough" )