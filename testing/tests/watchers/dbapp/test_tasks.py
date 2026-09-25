from bwtest import TestCase
from tests.watchers.test_common import TestCommon

import time

class TestTasksWatcher( TestCommon, TestCase ):
	
	
	tags = []
	name = "Test dbapp task watchers"
	description = "Tests dbapp task watchers by generating DB events"\
				" and verifying that it triggers updates in the relevant watchers"
				
	
	def runTest( self ):
		self.assertTrue( self._cc.getConfig( "dbApp/type", "mysql") == "mysql",
						"This test requires MySQL DB configuration" )
		snippet = """
e = BigWorld.createEntity( "TestEntity" )
e.writeToDB()
srvtest.finish( e.id )
"""
		self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		time.sleep( self.ARCHIVE_PERIOD * 2 )
		mainThreadTasks = self._cc.getWatcherData( 
									"tasks/MySqlDatabase/mainThread/All", "dbapp", None )
		backgroundTasks = self._cc.getWatcherData( 
									"tasks/MySqlDatabase/background/All", "dbapp", None )
		mainThreadTaskWatchers = {}
		for watcher in mainThreadTasks.getChildren():
			mainThreadTaskWatchers[watcher.name] = watcher.value

						
		backgroundTaskWatchers = {}
		for watcher in backgroundTasks.getChildren():
			backgroundTaskWatchers[watcher.name] = watcher.value


		self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		time.sleep( self.ARCHIVE_PERIOD * 2 )
		for watcher in mainThreadTasks.getChildren():
			self.assertTrue( watcher.value != mainThreadTaskWatchers[watcher.name],
							"Watcher value didn't update from activity. "\
							"%s: Went from %s to %s" % 
							( watcher.name, 
							  mainThreadTaskWatchers[watcher.name],
							  watcher.value) )
		
		for watcher in backgroundTasks.getChildren():
			self.assertTrue( watcher.value != backgroundTaskWatchers[watcher.name],
							"Watcher value didn't update from activity. "\
							"%s: Went from %s to %s" % 
							( watcher.name, 
							  backgroundTaskWatchers[watcher.name],
							  watcher.value) )
