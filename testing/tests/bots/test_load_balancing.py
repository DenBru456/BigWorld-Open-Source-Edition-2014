import bwtest
from helpers.cluster import ClusterController
from helpers.timer import runTimer, TimerError
import time
from bwtest import log

NUM_BOT_PROCS = 5
NUM_BOT_PER_PROC = 50
NUM_BOTS = NUM_BOT_PROCS * NUM_BOT_PER_PROC
MAX_LOAD_RANGE = 0.1


class BotsLoadBalancingTest( bwtest.TestCase ):
	name = "Bots Load Balancing"
	description = "Test bots load balancing"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		

		# Start bot procs and add bots
		self.cc.startProc( "bots", NUM_BOT_PROCS )
		self.cc.bots.add( NUM_BOTS, timeout = 60 )

		# Check bot count
		numBots = self.cc.bots.numBots()
		self.assertEqual( numBots, NUM_BOTS,
				"Not all %s bots were added" % NUM_BOTS )
		
		#Check load
		try:
			runTimer(self.cc.bots.load, 
				lambda result: (max(result) - min(result)) < MAX_LOAD_RANGE )
		except TimerError:
			self.fail( "Load range is greater than MAX_LOAD_RANGE (%s)" \
					% MAX_LOAD_RANGE )


		# Remove bots
		self.cc.bots.delete( NUM_BOTS, timeout = 60 )

		# Check bot count
		numBots = self.cc.bots.numBots()
		self.assertEqual( numBots, 0,
				"Not all %s bots were removed" % NUM_BOTS )

		# Check load
		try:
			runTimer(self.cc.bots.load, 
				lambda result: (max(result) - min(result)) < MAX_LOAD_RANGE )
		except TimerError:
			self.fail( "Load range is greater than MAX_LOAD_RANGE (%s)" \
					% MAX_LOAD_RANGE )
		
