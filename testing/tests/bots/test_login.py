from bwtest import TestCase
from helpers.cluster import ClusterController
from helpers.timer import runTimer
import time


class LoginFailureTest( TestCase ):
	
	
	name = "LoginFailure"
	tags = []
	description = "Tests bots behavior when failing to log in for various reasons"
	
	OVERLOAD_PERIOD = 1.0

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	

	def login( self ):
		snippet = """
		from Avatar import Avatar
		def onBecomePlayer( self ):
			srvtest.finish( 0 )
		Avatar.onBecomePlayer = onBecomePlayer

		import BWPersonality
		def onLogOnFailure( error, name ): srvtest.finish( error )
		BWPersonality.onLogOnFailure = onLogOnFailure

		BigWorld.addBots( 1 )
		"""

		return self.cc.sendAndCallOnApp( "bots", snippet = snippet )


	def runTest( self ):
		#Test for bots logging in with no loginapp
		self.cc.start()
		self.cc.startProc( "bots", 1 )
		self.cc.killProc( "loginapp", 1 )
		result = self.login()
		expected = 'LOGIN_REJECTED_NO_LOGINAPP_RESPONSE'
		self.assertEquals( result, expected, 
						"Incorrect logon status. Expected %s got %s" % \
						(  expected, result ))
		self.cc.stop()
	
		#Test for bots logging with an overloaded cellapp
		self.cc.setConfig( "balance/demo/enable", "true" )
		self.cc.setConfig( "balance/demo/numEntitiesPerCell", 
							"1" )
		self.cc.setConfig( "loginConditions/overloadTolerancePeriod",
						str( self.OVERLOAD_PERIOD ) )
		self.cc.start()
		
		#Need to sleep long enough that cellapp gets flagged as overloaded
		time.sleep( self.OVERLOAD_PERIOD * 5 )

		self.cc.startProc( "bots" )		
		result = self.login()
		expected = 'LOGIN_REJECTED_CELLAPP_OVERLOAD'
		self.assertEquals( result, expected, 
						"Incorrect logon status. Expected %s got %s" % \
						(  expected, result ))
		self.cc.stop()
		

class LoginControlTest( TestCase ):
	
	
	name = "LoginControl"
	tags = []
	description = "Tests logOnRetryPeriod option for bots"
	
	RETRY_PERIOD = 1.0
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "bots/logOnRetryPeriod", str(self.RETRY_PERIOD) )
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	def checkLoginResults( self, shouldSucceed = True ):
		snippet = """
		from Avatar import Avatar
		def onBecomePlayer( self ):
			srvtest.finish( %s )
		Avatar.onBecomePlayer = onBecomePlayer

		import BWPersonality
		def onLogOnFailure( error, name ):
			srvtest.assertTrue( error == \
								'LOGIN_REJECTED_LOGINS_NOT_ALLOWED')
			BWPersonality.count += 1
			if BWPersonality.count > 5:
				srvtest.finish( %s )
		BWPersonality.onLogOnFailure = onLogOnFailure
		BWPersonality.count = 0

		BigWorld.addBots( 1 )
		""" % (shouldSucceed, not shouldSucceed )
		
		return self.cc.sendAndCallOnApp( "bots", snippet = snippet )
	

	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		allowLogin = self.cc.getWatcherData( "config/allowLogin", "loginapp" )
		
		allowLogin.set( False )
		self.assertTrue( self.checkLoginResults( shouldSucceed = False ),
						"Login retries didn't happen" )
		self.assertTrue( self.cc.bots.numBots() == 0, 
						"Bot logged in when allowLogin set to False" )
		
		allowLogin.set( True )
		#Sleep to make sure that login has had at least one retry
		time.sleep( self.RETRY_PERIOD*2 )
		
		self.assertTrue( self.cc.bots.numBots() == 1,
						"Bot didn't login when allowLogin set to True" )
		self.assertTrue( self.checkLoginResults( shouldSucceed = True ),
						 "Incorrect loginstatus happened")
		self.assertTrue( self.cc.bots.numBots() == 2,
						"Bot didn't login when allowLogin set to True")
		
		
		
		