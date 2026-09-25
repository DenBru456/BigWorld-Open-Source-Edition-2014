import os, time

from bwtest import TestCase, config
from helpers.cluster import ClusterController


login_snippet = """
from Avatar import Avatar
def onBecomePlayer( self ):
	srvtest.finish( 0 )
Avatar.onBecomePlayer = onBecomePlayer

import BWPersonality
def onLogOnFailure( error, name ): srvtest.finish( error )
BWPersonality.onLogOnFailure = onLogOnFailure

BigWorld.addBotsWithName( [ ( "bigworldtest", "" ) ] )
"""

class TestAcceptUnknown( TestCase ):
	
	tags = []
	name = "Accept unknown"
	description = "Test shouldAcceptUnknownUsers option"
	
	RES_PATH = "simple_space/res"
	
	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		self._cc.setConfig( "bots/serverName", config.CLUSTER_MACHINES[0] )
		self._cc.setConfig( "bots/port", str(20013+config.CLUSTER_UID) )
		self._cc.setConfig( "loginApp/shouldOffsetExternalPortByUID", "true" )
		
	
	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()

	
	def testConfig( self, acceptUnknown, expected ):
		self._cc.setConfig( "billingSystem/shouldAcceptUnknownUsers", 
						acceptUnknown )
		self._cc.start()
		self._cc.startProc( "bots" )
		status = self._cc.sendAndCallOnApp( "bots", None, login_snippet) == 0

		hasLoggedIn = self._cc.bots.numBots() == 1
		self.assertTrue( hasLoggedIn == expected,
						"Bot log in status was %s when expeting %s" % \
						 ( hasLoggedIn, expected ))
		self.assertTrue( status == expected,
						 "Login callback was %s when expecting %s" % \
						 ( status, expected ) )
		self._cc.stop( timeout = 60 )
		

	def runTest( self ):
		self.testConfig( "false", False )
		self.testConfig( "true", True )
		

class TestRememberUnknown( TestCase ):
	
	tags = []
	name = "Remember unknown"
	description = "Test shouldRememberUnknownUsers option"
	
	RES_PATH = "simple_space/res"
	
	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		self._cc.setConfig( "bots/serverName", config.CLUSTER_MACHINES[0] )
		self._cc.setConfig( "bots/port", str(20013+config.CLUSTER_UID) )
		self._cc.setConfig( "loginApp/shouldOffsetExternalPortByUID", "true" )


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()
	
	
	def testConfig( self, acceptUnknown, rememberUnknown, expected ):
		self._cc.setConfig( 
				"billingSystem/shouldAcceptUnknownUsers", acceptUnknown )
		self._cc.setConfig( 
				"billingSystem/shouldRememberUnknownUsers", rememberUnknown )
		self._cc.start()
		self._cc.startProc( "bots" )
		status = self._cc.sendAndCallOnApp( "bots", None, login_snippet) == 0

		hasLoggedIn = self._cc.bots.numBots() == 1
		self.assertTrue( hasLoggedIn == expected,
						"Bot log in status was %s when expeting %s" % \
						 ( hasLoggedIn, expected ))
		self.assertTrue( status == expected,
						 "Login callback was %s when expecting %s" % \
						 ( status, expected ) )
		self._cc.stop( timeout = 60)

	
	def runTest( self ):
		self.testConfig( 
			acceptUnknown="true", rememberUnknown="true", expected=True )
		self.testConfig( 
			acceptUnknown="false", rememberUnknown="false", expected=True )
		self._cc.clearDB()
		self.testConfig( 
			acceptUnknown="true", rememberUnknown="false", expected=True )
		self.testConfig( 
			acceptUnknown="false", rememberUnknown="false", expected=False )
		
		
		
		
		
	
