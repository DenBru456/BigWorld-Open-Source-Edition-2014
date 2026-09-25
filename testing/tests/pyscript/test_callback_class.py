from helpers.cluster import ClusterController
import time
from bwtest import TestCase, log


class CallbackClassTest( TestCase ):
	name = "Callback Class" 
	description = "Test callback class usage"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		snippet1 = """
class Callback:
	def __init__( self ):
		self.done = False
		self.args = None
	def __call__( self, *args ):
		self.done = True
		self.args = args
		srvtest.finish( (self.done, self.args) )

cb = Callback()
BigWorld.lookUpBaseByDBID( "TestEntity", 1, cb )
"""

		(done, args) = self.cc.sendAndCallOnApp( "baseapp", 1, snippet1 )
		self.assertTrue( done )
		self.assertNotEqual( args, None )
