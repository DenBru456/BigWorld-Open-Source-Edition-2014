from tests.watchers.test_common import TestCommon
from bwtest import TestCase
from primitives.WebConsoleAPI import WebConsoleAPI

class TestCommand( TestCommon, TestCase ):
	
	
	tags = []
	name = "Test command watchers"
	description = "Check that the listed command watchers match whats available\
		through the web console api"
	process = "baseapp"

	def runTest( self ):
		commands = self._cc.getWatcherData( "command", self.process )
		wapi = WebConsoleAPI()
		ret, output = wapi.commandsGetScripts( "watcher" )
		self.assertTrue( ret == 200, "Web console API didn't return scripts")
		webConsoleCommands = []
		for command in output[ 'scripts' ]:
			if self.process in command[ 'id' ]:
				webConsoleCommands.append( command[ 'title' ] )
		for command in commands.getChildren():
			self.assertTrue( command.name in webConsoleCommands, 
							"Following command not found in watchers: %s"
							% command.name )