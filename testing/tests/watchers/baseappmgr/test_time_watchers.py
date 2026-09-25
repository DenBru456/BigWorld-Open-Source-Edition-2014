from datetime import datetime
import time

from tests.watchers.test_common import TestCommon
from bwtest import TestCase, config
from helpers.command import Command


class TestTimeWatchers( TestCommon, TestCase):
	
	
	tags = []
	name = "Test time related watchers"
	description = "Tests the behavior of the following watchers:\
	dateBuilt, dateStarted, gameTimeInSeconds, gameTimeInTicks, gameUpdateHertz,\
	timingMethod, uptime, uptimeInSeconds"
	process = "baseappmgr"


	def runTest( self ):
		
		dateBuilt = self._cc.getWatcherValue( "dateBuilt", self.process, None )
		dateFormat = "%H:%M:%S %b %d %Y"
		dateBuilt = datetime( *( time.strptime( dateBuilt, dateFormat )[0:6] ) )
		cmd = Command()
		cmd.call( "stat -c%%Z {bwroot}/%s/%s/baseappmgr" 
				% (config.BIGWORLD_FOLDER, config.SERVER_BINARY_FOLDER) )
		exeModified = datetime.fromtimestamp( float( cmd.getLastOutput()[0] ) )
		self.assertTrue( self.compareDates( dateBuilt, exeModified ),
						"dateBuilt watcher returned inccorect date" )
		
		dateStarted = self._cc.getWatcherValue( "dateStarted", 
											self.process, None )
		dateFormat = "%a %b %d %H:%M:%S %Y"
		dateStarted = datetime( 
						*( time.strptime( dateStarted, dateFormat )[ 0:6 ] ) )
		self.assertTrue( self.compareDates(dateStarted, datetime.today()), 
						"dateStarted watcher returned incorrect date" )
		
		timingMethod = self._cc.getWatcherValue( "timingMethod", 
												self.process, None )
		self.assertTrue( timingMethod == "gettime",
						"timingMethod watcher returned incorrect method")
		
		uptime = self._cc.getWatcherValue( "uptime", self.process, None )
		uptimeInSeconds = self._cc.getWatcherValue( 
										"uptimeInSeconds", self.process, None )
		time.sleep(10)
		newUptime = self._cc.getWatcherValue( "uptime", self.process, None )
		newUptimeInSeconds = self._cc.getWatcherValue( 
										"uptimeInSeconds", self.process, None )
		res = int( newUptimeInSeconds ) - int( uptimeInSeconds )
		self.assertTrue( res >= 0 and res < 100, 
						"Watcher uptimeInSeconds did not update appropriately")
		res = self.convertToSeconds( newUptime ) - self.convertToSeconds( uptime )
		self.assertTrue( res >= 0 and res < 100,
						"Watcher uptime did not update appropriately")
		
		
		
		gameUpdateHertz = self._cc.getWatcherValue( "gameUpdateHertz", 
												self.process, None )
		self.assertTrue( int( gameUpdateHertz ) == 10,
						"gameUpdateHertz return incorrect default value")

		gameTimeInSeconds = self._cc.getWatcherValue( "gameTimeInSeconds", 
													self.process, None )
		gameTimeInTicks = self._cc.getWatcherValue( "gameTimeInTicks", 
												self.process, None )
		ticksToSeconds = float( gameTimeInTicks )/gameUpdateHertz 
		res = abs( ticksToSeconds - float( gameTimeInSeconds )) <= 2
		self.assertTrue( res, 
						"Incorrect relationship between ticks and seconds" )
		
		self._cc.stop()
		self._cc.setConfig("gameUpdateHertz", "5")
		self._cc.start()
		
		newGameUpdateHertz = self._cc.getWatcherValue( "gameUpdateHertz", 
													self.process, None )
		self.assertTrue( int( newGameUpdateHertz ) == 5,
						"gameUpdateHertz was not set")

		newGameTimeInSeconds = self._cc.getWatcherValue( "gameTimeInSeconds", 
														self.process, None )
		self.assertTrue( int( newGameTimeInSeconds ) > int( gameTimeInSeconds ), 
					"Watcher gameTimeInSeconds did not update appropriately" )
		newGameTimeInTicks = self._cc.getWatcherValue( "gameTimeInTicks", 
													self.process, None )
		ticksToSeconds = float( gameTimeInTicks )/int( gameUpdateHertz )
		newTicksToSeconds = float( newGameTimeInTicks )/int( newGameUpdateHertz )
		self.assertTrue( newTicksToSeconds > ticksToSeconds,
						"Watcher gameTimeInTicks did not update appropriately" )