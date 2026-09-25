import os, time
from xml.dom.minidom import parse

from bwtest import TestCase, config
from helpers.cluster import ClusterController
from primitives import mysql

class TestNumConectionsOption( TestCase ):


	tags = ["MANUAL"]
	name = "MySQL connections"
	description = "Test numConnections option"

	RES_PATH = config.TEST_ROOT + "/res_trees/simple_space/res"
	MAX_POLLS = 30
	SLEEP_TIME = 60

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		self._cc.setConfig( "db/mysql/numConnections", "1" )
		self._cc.setConfig( "baseApp/archivePeriod", "3" )
		self._cc.start()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def waitAndCheckStability( self ):
		polledTimes = 0
		while polledTimes < self.MAX_POLLS:
			time.sleep( self.SLEEP_TIME )

			self._cc.waitForServerSettle()
			polledTimes += 1


	def checkProcessCount( self, expectedCount ):
		result = mysql.executeSQL( "SHOW PROCESSLIST" )
		processes = [ x for x in result if x[1] == config.CLUSTER_DB_USERNAME ]
		self.assertTrue( len( processes ) == expectedCount )


	def runTest( self ):
		self._cc.startProc( "bots", 1 )
		self.checkProcessCount( 3 )# 1 for main thread + numConnection + 1 for the SQL call itself
		self._cc.bots.add( 20 )
		self.waitAndCheckStability()
		self._cc.stop()
		self._cc.setConfig( "db/mysql/numConnections", "20" )
		self._cc.start()
		self._cc.startProc( "bots", 1 )
		self.checkProcessCount( 22 )# 1 for main thread + numConnection + 1 for the SQL call itself
		self._cc.bots.add( 20 )
		self.waitAndCheckStability()
