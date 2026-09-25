from test_common import *
from bwtest import manual
from helpers.cluster import ClusterController

# scenario 1: Test restoring server state.
class ControlledStartup( TestCase ):
	name = 'Test restoring server state.'
	description = """Check that merchant remembers previous visit. 
This test requires manual steps."""

	tags = [ 'MANUAL' ]
	_cc = None
	RES_PATH = config.CLUSTER_BW_ROOT + "/game/res/fantasydemo"

	def step0( self ):
		"""Given that server is restarted"""
		self._cc = ClusterController( self.RES_PATH )
		self._cc.start()

	def step1( self ):
		"""[Manual Step] Connect client and buy from Merchant"""
		msg = """
FantasyDemo server is running now.
Login a FantasyDemo client to the server and buy something from Merchant.
Then Logout.
		"""
		res = manual.input_passfail( msg )
		self.assertTrue( res )

	def step2( self ):
		"""Restart server"""
		self._cc.stop()
		self._cc.start()

	def step3( self ): 
		"""[Manual Step] Connect client and buy from Merchant. Check that you 
are not the first customer of the Merchant (you should be one 
more than previous trade)"""

		msg = """
Connect client and buy from Merchant. Check that you 
are not the first customer of the Merchant (you should be one 
more than previous trade)"
"""
		res = manual.input_passfail( msg )
		self.assertTrue( res )

	def tearDown( self ):
		"""Shut down server"""
		self._cc.stop()
		self._cc.clean()


