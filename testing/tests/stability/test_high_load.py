import os
import sys
import bwtest
from helpers.cluster import ClusterController, CoreDumpError
import time
from random import random

from bwtest import config
from bwtest import log
from bwtest import manual


class TestHighLoadBase( object ):
	RES_PATH = config.CLUSTER_BW_ROOT + "/game/res/fantasydemo"
	# log.debug( "RES_PATH=%s" % RES_PATH )

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH, load = True )


	def tearDown( self ):
		self.stopCluster()

		self._cc.clean()


	def startCluster( self ):
		cc = self._cc

		cc.start()

		cc.startProc( "baseapp", 1, 0 )
		cc.startProc( "baseapp", 2, 1 )
		cc.startProc( "cellapp", 3, 0 )
		cc.startProc( "cellapp", 4, 1 )
		cc.startProc( "bots", 1, 0 )
		cc.startProc( "bots", 1, 1 )

		cc.waitForApp( "baseapp", 1 )
		cc.waitForApp( "baseapp", 2 )
		cc.waitForApp( "baseapp", 3 )
		cc.waitForApp( "baseapp", 4 )


	def stopCluster( self ):
		# if stopping fails, there was likely a crashed app
		cc = self._cc

		cc.stop()


class TestHighLoadWithBots( TestHighLoadBase, bwtest.TestCase ):
	name = "High load with bots"
	description = """
	Testing cluster with many apps and many walking bots.
	This test uses fantasydemo resource tree.
	"""

	tags = [ "STAGED" ]


	def runTest( self ):
		"""Create bots and check the cluster is stable"""
		cc = self._cc

		self.startCluster()

		botsToAdd = 200

		def swing():
			log.debug( "Adding %d bots...", botsToAdd )
			cc.bots.add( botsToAdd, timeout = 60 )
			log.debug( "Added %d bots.", botsToAdd )
			time.sleep( 10 )
			log.debug( "Deleting %d bots...", botsToAdd )
			cc.bots.delete( botsToAdd )
			log.debug( "Deleted %d bots.", botsToAdd )
			time.sleep( 1 )

		def doStress():
			swing()
			self.stopCluster()
			self.startCluster()

		numStresses = 10
		for i in range( 0, numStresses ):
			log.debug( "Stressing server for %d/%d time",
			  				i + 1, numStresses )
			doStress()		

#		manual.input( "Press <Enter> to resume the test" )


class TestHighLoadWithGuardsBase( TestHighLoadBase ):

	GUARDS_TO_ADD_AT_ONCE = 500

	def addGuards( self, numGuards ):
		cc = self._cc

		numBaseApps = 4

		guardsPerApp = numGuards / numBaseApps

		snippet = """
import util
util.addGuards( {num} )
srvtest.finish()
"""
		for appOrd in range( 1, numBaseApps ):
			cc.sendAndCallOnApp( "baseapp", appOrd, snippet,
					  	num = guardsPerApp )


class TestHighLoadWithGuards( TestHighLoadWithGuardsBase, bwtest.TestCase ):
	name = "High load with guards"
	description = """
	Testing cluster with many apps and many walking guards.
	This test uses fantasydemo resource tree.
	"""

	tags = ["STAGED"]


	def step1( self ):
		"""Create many guards and check the cluster is stable"""

		self.startCluster()

		numAdds = 5
		for i in range( numAdds ):
			log.debug( "adding %d guards for %d/%d time", 
			 				self.GUARDS_TO_ADD_AT_ONCE, i + 1, numAdds )
			self.addGuards( self.GUARDS_TO_ADD_AT_ONCE  )
			time.sleep( 15 )

		self.stopCluster()


	def step2( self ):
		"""Start and stop cluster multiple times with many guards"""

		numLaps = 10
		numAdds = 5
		for i in range( numLaps ):
			log.debug( "Starting cluster, lap %d/%d ", i + 1, numLaps )
			self.startCluster()

			for j in range( numAdds ):
				log.debug( "adding %d guards for %d/%d time",
			  				self.GUARDS_TO_ADD_AT_ONCE, j + 1, numAdds )
				self.addGuards( self.GUARDS_TO_ADD_AT_ONCE )
				time.sleep( 30 )

			time.sleep( 60 )
			self.stopCluster()


class TestHighLoadWithLoss( TestHighLoadBase, bwtest.TestCase ):
	name = "High load with bots and network packet loss"
	description = """
	Testing cluster with many apps and many bots.
	This test uses fantasydemo resource tree.
	"""

	tags = [ "STAGED" ]



	def stopCluster( self ):
		cc = self._cc

		try:		
			cc.stop()
		except CoreDumpError, e:
			if [app for app in e.failedAppList if app != "bots" ]:
				raise
			else:
				# we allow for failing bots processes as we kill them frequently
				# during the test
				pass


	def setClusterConfig( self, isLatency ):
		cc = self._cc
		if isLatency:
			cc.setConfig( "loginApp/externalLossRatio", "0.3" )
			cc.setConfig( "loginApp/externalLatencyMin", "2" )
			cc.setConfig( "loginApp/externalLatencyMax", "2.1" )
			cc.setConfig( "baseApp/externalLossRatio", "0.3" )
			cc.setConfig( "baseApp/externalLatencyMin", "2" )
			cc.setConfig( "baseApp/externalLatencyMax", "2.1" )
		else:
			cc.setConfig( "loginApp/externalLossRatio", "0" )
			cc.setConfig( "loginApp/externalLatencyMin", "0" )
			cc.setConfig( "loginApp/externalLatencyMax", "0" )
			cc.setConfig( "baseApp/externalLossRatio", "0" )
			cc.setConfig( "baseApp/externalLatencyMin", "0" )
			cc.setConfig( "baseApp/externalLatencyMax", "0" )


	def swingBots( self ):
		cc = self._cc

		botsToAdd = 100
		timeToSwing = 30 * 60 # in seconds

		startTime = time.time()
		accruedBots = 0
		maxAccruedBots = 300

		while True:
			if accruedBots >= maxAccruedBots:
				log.debug( "Retiring bots processes to avoid "
							"'too many open files' error"  )
				cc.killProc( "bots" ) 
				cc.killProc( "bots" ) 
				cc.startProc( "bots", 1, 0 )
				cc.startProc( "bots", 1, 1 )

				accruedBots = 0

				time.sleep( 1 )


			log.debug( "Adding %d bots...", botsToAdd )
			cc.bots.add( botsToAdd )
			log.debug( "Added %d bots.", botsToAdd )
			time.sleep( 10 )
			log.debug( "Deleting %d bots...", botsToAdd )
			cc.bots.delete( botsToAdd )
			time.sleep( 1 )

			accruedBots += botsToAdd

			if time.time() - startTime > timeToSwing:
				break 


	def testCycle( self, layoutFunc, isLatency ):

		self.setClusterConfig( isLatency )

		cc = self._cc

		cc.start()

		if layoutFunc is not None:
			layoutFunc( cc )

		cc.startProc( "bots", 1, 0 )
		cc.startProc( "bots", 1, 1 )

		self.swingBots()

		self.stopCluster()		


	def step1( self ):
		"""
		Continuously add/del 100 bots for 30 minutes 
		(1 x baseapp, 1 x loginapp, no latency)
		"""

		self.testCycle( None, isLatency = False )


	def step2( self ):
		"""
		Continuously add/del 100 bots for 30 minutes 
		(1 x baseapp, 1 x loginapp, with latency)
		"""

		self.testCycle( None, isLatency = True )


	def step3( self ):
		"""
		Continuously add/del 100 bots for 30 minutes 
		(2 x baseapp, 2 x loginapp, no latency)
		"""

		def layoutFunc( cc ):
			cc.startProc( "baseapp", 1, 1 )
			cc.startProc( "loginapp", 1, 1 )


		self.testCycle( layoutFunc, isLatency = False )


	def step4( self ):
		"""
		Continuously add/del 100 bots for 30 minutes 
		(2 x baseapp, 2 x loginapp, with latency)
		"""

		def layoutFunc( cc ):
			cc.startProc( "baseapp", 1, 1 )
			cc.startProc( "loginapp", 1, 1 )


		self.testCycle( layoutFunc, isLatency = True )

