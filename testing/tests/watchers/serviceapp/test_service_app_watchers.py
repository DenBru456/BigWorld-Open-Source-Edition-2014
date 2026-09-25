import time

from bwtest import TestCase
from tests.watchers.test_common import TestCommon

class TestServiceAppWatchers( TestCommon, TestCase ):
	
	
	tags = []
	name = "serviceAppsWatchers"
	description = "Test functionality of the serviceapp watchers"
	
	services = {"ExampleService": ["option1", "option2"],
				"HTTPGameService": ["configPath", "ports"],
				"HTTPReplayService": ["configPath", "ports", "tickRate"],
				"HTTPResTreeService": ["configPath"],
				"NoteStore": [],
				"SpaceRecorder": ["configPath", "numTicksToSign", "shouldOverwrite"]
				}
	
	def setUp( self ):
		self.RES_TREE = ["simple_space_with_services/res", "simple_space/res"]
		TestCommon.setUp( self )
		
	def runTest( self ):
		for service, configs in self.services.items():
			isrunning = self._cc.getWatcherValue( 
								"servicesStaticConfig/%s/isRunning" % service, 
								"serviceapp", 1 )
			self.assertTrue( isrunning, "Service %s was not running" % service)
			for c in configs:
				config = self._cc.getWatcherValue( 
								"servicesStaticConfig/%s/%s" % (service, c),
								"serviceapp", 1 )
				self.assertTrue( config != None, 
								"Config %s did not exist for service %s " 
								% ( c, service ) )
	