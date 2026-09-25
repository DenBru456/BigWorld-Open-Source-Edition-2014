import bwtest
from helpers.cluster import ClusterController
from helpers.timer import runTimer
import time

from bwtest import config
from bwtest import log

from test_common import *

		
class FileHandlesLeakTest( bwtest.TestCase ):
	name = "File Handles Leak Test"
	description = """
	Continuously add and remove bots to make sure
	there's no dangling file handles in bots apps
	"""

	RES_PATH = "simple_space/res"

	tags = []


	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		self.addCleanup( self._cc.clean )


	def tearDown( self ):
		self._cc.stop()

		self._cc.clean()


	def swingBots( self ):
		cc = self._cc

		botsToAdd = 50

		pid = cc.bots.procs()[0].pid
		
		FDsUsed = fileDescriptorsUsed( pid )
		log.debug( "Adding %d bots...", botsToAdd )
		cc.bots.add( botsToAdd, timeout = 30 )
		log.debug( "Added %d bots.", botsToAdd )
		
		time.sleep( 10 )
		
		numBots = cc.bots.numBots()
		self.assertEqual( numBots, botsToAdd, 
			"Failed to add %d bots" % botsToAdd)
		
		log.debug( "Deleting %d bots...", botsToAdd )
		cc.bots.delete( botsToAdd )
		time.sleep( 1 )
		
		numBots = cc.bots.numBots()
		self.assertEqual( numBots, 0, 
			"Failed to delete %d bots" % botsToAdd)

		runTimer( lambda: fileDescriptorsUsed( pid ), timeout = 15,
				checker = lambda ret: ret == FDsUsed)


	def runTest( self ):
		"""
		Add/delete bots and check that file descriptor use hasn't changed
		"""

		cc = self._cc

		cc.start()

		cc.startProc( "bots", 1, 0 )

		self.swingBots()

		cc.stop()		
