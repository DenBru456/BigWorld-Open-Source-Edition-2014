import time
from bwtest import TestCase, config, addParameterizedTestCases
from helpers.cluster import ClusterController, ClusterControllerError
from primitives import locallog


class ConfigurationParsingTest( TestCase ):
	
	
	name = "Configuration Parsing"
	description = "Tests that server handles XML errors in bw.xml"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		
		def breakConfig( inputFile, outputFile ):
			for line in inputFile.readlines():
				outputFile.write( line )
				if line.strip() == "<root>":
					outputFile.write( "<debugConfigOptions> 0 </>\n" )
		
		user = config.CLUSTER_USERNAME
		self.cc.mangleResTreeFile( "server/bw_%s.xml" % user, breakConfig )
		started = True
		try:
			self.cc.start()
		except ClusterControllerError:
			started = False
		self.assertFalse( started, "Server started even though bw.xml was broken")


class DesiredAppsTest:
	
	
	name = "Desired Apps"
	description = "Tests that desiredBaseApps and desiredCellApps option works"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "bots/serverName", config.CLUSTER_MACHINES[0] )
		self.cc.setConfig( "bots/port", str(20013+config.CLUSTER_UID) )
		self.cc.setConfig( "loginApp/shouldOffsetExternalPortByUID", "true" )
		
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.setConfig( self.desiredConfig , "5" )
		self.cc.start()
		self.cc.startProc( "bots" )
		
		self.cc.bots.addWithCredentials( "bigworldtest", "" )
		time.sleep( 10 )
		hasLoggedIn = self.cc.bots.numBots() == 1
		self.assertFalse( hasLoggedIn,
						"Bot logged in without %s" % self.desiredConfig )
		output = locallog.grepLastServerLog( "Logon failed: Server not ready" )
		self.assertTrue( len( output ) > 0,
						"Didn't find expected logon failure message")
		
		if self.desiredConfig == "desiredBaseApps":
			self.cc.startProc( "baseapp", 4 )
		else:
			self.cc.startProc( "cellapp", 4 )
		
		self.cc.bots.addWithCredentials( "bigworldtest", "" )
		time.sleep( 10 )
		hasLoggedIn = self.cc.bots.numBots() == 1
		self.assertTrue( hasLoggedIn,
						"Bot didn't log in with %s" % self.desiredConfig )
		output = locallog.grepLastServerLog( "ServerConnection::createBasePlayer" )
		self.assertTrue( len( output ) > 0,
						"Didn't find expected logon success message")
		


addParameterizedTestCases( DesiredAppsTest, 
					[{"desiredConfig": "desiredBaseApps"}, 
					 { "desiredConfig": "desiredCellApps" }])


class OutputFilterThresholdTest( TestCase ):
	
	
	name = "Output Filter Threshold"
	description = "Tests the functionality of outputFilterThreshold"
	tags = []
	
	logLevels = {0: "trace",
				1: "debug",
				2: "info",
				3: "notice",
				4: "warning",
				5: "error",
				6: "critical",
				7: "hack"}
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		
		snippet = """
		import logging
		log = logging.getLogger( "Test" )
		log.log( log.TRACE, "Logging at level trace" )
		log.debug( "Logging at level debug" )
		log.info( "Logging at level info")
		log.log( log.NOTICE, "Logging at level notice" )
		log.warning( "Logging at level warning" )
		log.error( "Logging at level error" )
		log.critical( "Logging at level critical" )
		log.log( log.HACK, "Logging at level hack" )
		srvtest.finish()
		"""
		
		for i in range( 9 ):
			self.cc.setConfig( "outputFilterThreshold", str( i ) )
			self.cc.start()
			self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
			for key, value in self.logLevels.items():
				output = locallog.grepLastServerLog( 
										"Logging at level %s" % value )
				if i > key:
					self.assertTrue( len(output ) == 0,
								"Found %s log at threshold %s" % (value, i))
				else:
					self.assertTrue( len(output ) > 0,
								"Didn't find %s log at threshold %s" % (value, i))
			self.cc.stop()

		