from tests.watchers.test_common import TestCommon
from bwtest import TestCase

import time

setupSnippet = """
import BackgroundTask
x = BackgroundTask.Manager("testing")
x.startThreads( {threads} )
class TestTask( BackgroundTask.BackgroundTask ):
	def doBackgroundTask( self, bgTaskMgr, threadData ):
		print 'bgtask'
		import time
		time.sleep( {sleep} )
		bgTaskMgr.addMainThreadTask( self )
	def doMainThreadTask( self, bgTaskMgr ):
		print 'doMainThread'
for i in range( {numtasks} ):
	x.addBackgroundTask( TestTask() )
srvtest.finish()
"""

class TestBgTaskManager( TestCommon, TestCase ):
	
	
	tags = []
	name = "Background Task Manager"
	description = "Test watcher functionality of"\
				"the background task manager"
	process = "baseapp"
	
	
	def step1( self ):
		"""Create background task and check watcher values before they complete
		"""
		self._cc.sendAndCallOnApp( self.process, 1, setupSnippet, 
								threads = 2, sleep = 10, numtasks = 5 )

		manager = self._cc.getWatcherData( "bgTaskManager/testing", 
										self.process)
		numThreads = int( manager.getChild( "numberOfThreads" ).value )
		self.assertTrue( numThreads == 2, 
						"Number of threads on background tasks incorrect")
		
		queueSizeBg = int( manager.getChild( "background/queueSize" ).value )
		queueSizeFg = int( manager.getChild( "foreground/queueSize" ).value )

		self.assertTrue( queueSizeBg == 3,
						"QueueSize for the background was not as expected: %s" % queueSizeBg)
		self.assertTrue( queueSizeFg == 0,
						"QueueSize for the foreground was not as expected: %s" % queueSizeFg )
		
		completedJobsBg = manager.getChild( "background/completedJobs" ).value
		completedJobsFg = manager.getChild( "foreground/completedJobs" ).value
		self.assertTrue( int( completedJobsBg ) == 0,
					"Background completed jobs should have been 0" )
		self.assertTrue( int( completedJobsFg ) == 0,
					"Foreground completed jobs should have been 0" )
		
		longJobClassBg = manager.getChild( "background/longestJobClass" ).value
		longJobClassFg = manager.getChild( "foreground/longestJobClass" ).value
		longJobTimeBg = manager.getChild( "background/longestJobTime" ).value
		longJobTimeFg = manager.getChild( "foreground/longestJobTime" ).value
		self.assertTrue( longJobClassBg == "",
						"Found longest job class with no completed jobs")
		self.assertTrue( longJobClassFg == "",
						"Found longest job class with no completed jobs")
		self.assertTrue( float( longJobTimeBg ) == 0.0,
						"Longest job time was non zero with no jobs completed")
		self.assertTrue( float( longJobTimeFg ) == 0.0,
						"Longest job time was non zero with no jobs completed")
		
	def step2( self ):
		"""Wait for background task to complete and check watcher values
		"""
		time.sleep( 40 )
		
		manager = self._cc.getWatcherData( "bgTaskManager/testing", 
										self.process)
		
		queueSizeBg = int( manager.getChild( "background/queueSize" ).value )
		queueSizeFg = int( manager.getChild( "foreground/queueSize" ).value )

		self.assertTrue( queueSizeBg == 0,
						"QueueSize for the background was not as expected" )
		self.assertTrue( queueSizeFg == 0,
						"QueueSize for the foreground was not as expected" )
		
		completedJobsBg = manager.getChild( "background/completedJobs" ).value
		completedJobsFg = manager.getChild( "foreground/completedJobs" ).value
		self.assertTrue( int( completedJobsBg ) == 5,
					"Background completed jobs should have been 5" )
		self.assertTrue( int( completedJobsFg ) == 5,
					"Foreground completed jobs should have been 5" )
		
		longJobClassBg = manager.getChild( "background/longestJobClass" ).value
		longJobClassFg = manager.getChild( "foreground/longestJobClass" ).value
		longJobTimeBg = manager.getChild( "background/longestJobTime" ).value
		longJobTimeFg = manager.getChild( "foreground/longestJobTime" ).value
		self.assertTrue( longJobClassBg == "TestTask",
						"Found incorrect longest job class")
		self.assertTrue( longJobClassFg == "TestTask",
						"Found incorrect longest job class")
		self.assertTrue( float( longJobTimeBg ) != 0.0,
						"Longest job time was zero with jobs completed")
		self.assertTrue( float( longJobTimeFg ) != 0.0,
						"Longest job time was non zero with jobs completed")

class TestPyOutputThreadSafe( TestCommon, TestCase ):
	
	
	tags = []
	name = "PyOutput ThreadSafe"
	description = "Test case to verify that PyOutput is thread safe"\
		"as per BWT-21598"
	process = "baseapp"
		
	
	def runTest( self ):
		self._cc.sendAndCallOnApp( self.process, 1, setupSnippet, 
								threads = 15, sleep = 20, numtasks = 30 )
		time.sleep( 10 )
		
