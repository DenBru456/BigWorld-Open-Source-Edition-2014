import bwunittest
import time


# --------------------------------------------------------------------------
# Section: Functions run server side
# --------------------------------------------------------------------------

def serverSideHelper():
	import BackgroundTask
	import time

	global SleepTask
	global bgTaskMgr

	class SleepTask( BackgroundTask.BackgroundTask ):

		def __init__( self, time ):
			self.time = time

		def doBackgroundTask( self, bgTaskMgr ):
			time.sleep( self.time )
			bgTaskMgr.addMainThreadTask( self )

		def doMainThreadTask( self, bgTaskMgr ):
			global taskCount
			taskCount -= 1

			if not taskCount:
				returnToPyUnit( None )

	bgTaskMgr = BackgroundTask.Manager()
	returnToPyUnit( None )


# TODO: Allow server side functions to accept args
def oneBgThreadOneMultiTickTask():
	global taskCount
	taskCount = 1

	bgTaskMgr.startThreads( 1 )

	for i in range( 0, taskCount ):
		task = SleepTask( 5 )
		bgTaskMgr.addBackgroundTask( task )

	bgTaskMgr.stopAll()


def oneBgThreadThreeMultiTickTasks():
	global taskCount
	taskCount = 3

	bgTaskMgr.startThreads( 1 )

	for i in range( 0, taskCount ):
		task = SleepTask( 5 )
		bgTaskMgr.addBackgroundTask( task )

	bgTaskMgr.stopAll()


def fiveBgThreadFiveMultiTickTasks():
	global taskCount
	taskCount = 5

	bgTaskMgr.startThreads( 5 )

	for i in range( 0, taskCount ):
		task = SleepTask( 5 )
		bgTaskMgr.addBackgroundTask( task )

	bgTaskMgr.stopAll()


def oneBgThreadTenThousandSubTickTasks():
	global taskCount
	taskCount = 10000

	bgTaskMgr.startThreads( 1 )

	for i in range( 0, taskCount ):
		task = SleepTask( 0.001 )
		bgTaskMgr.addBackgroundTask( task )

	bgTaskMgr.stopAll()


def fiveBgThreadRecursiveTasks():
	import BackgroundTask
	import time

	# On completion, add two more
	class RecursiveSleepTask( BackgroundTask.BackgroundTask ):

		def __init__( self, time ):
			self.time = time

		def doBackgroundTask( self, bgTaskMgr ):
			time.sleep( self.time )
			bgTaskMgr.addMainThreadTask( self )

		def doMainThreadTask( self, bgTaskMgr ):
			bgTaskMgr.addBackgroundTask( RecursiveSleepTask( 0.1 ) )
			bgTaskMgr.addBackgroundTask( RecursiveSleepTask( 0.1 ) )
			print "BgTask Queue = %s" % bgTaskMgr._Manager__bgTasks.qsize()

	bgTaskMgr = BackgroundTask.Manager()
	bgTaskMgr.startThreads( 5 )
	bgTaskMgr.addBackgroundTask( RecursiveSleepTask( 0.1 ) )

# --------------------------------------------------------------------------
# Section: Test cases run bwunittest side
# --------------------------------------------------------------------------

class BackgroundTaskTestSuite( bwunittest.TestCase ):

	def setUp( self ):
		bwunittest.startServer( None, None, None, "layout.xml" )


	def tearDown( self ):
		bwunittest.stopServer()


	def testOneBgThreadOneMultiTickTask( self ):
		bwunittest.runOnServer( [serverSideHelper], "baseapp01" )

		startTime = time.time()
		bwunittest.runOnServer( [oneBgThreadOneMultiTickTask], "baseapp01" )
		totalTime = time.time() - startTime

		# ~5 secs
		self.assert_( int( totalTime/5 ) == 1 )


	def testOneBgThreadThreeMultiTickTasks( self ):
		bwunittest.runOnServer( [serverSideHelper], "baseapp01" )

		startTime = time.time()
		bwunittest.runOnServer( [oneBgThreadThreeMultiTickTasks], "baseapp01" )
		totalTime = time.time() - startTime

		# ~15 secs
		self.assert_( int( totalTime/5 ) == 3 )


	def testFiveBgThreadFiveMultiTickTasks( self ):
		bwunittest.runOnServer( [serverSideHelper], "baseapp01" )

		startTime = time.time()
		bwunittest.runOnServer( [fiveBgThreadFiveMultiTickTasks], "baseapp01" )
		totalTime = time.time() - startTime

		# ~5 secs
		self.assert_( int( totalTime/5 ) == 1 )


	def testOneBgThreadTenThousandSubTickTasks( self ):
		bwunittest.runOnServer( [serverSideHelper], "baseapp01" )

		startTime = time.time()
		bwunittest.runOnServer( [oneBgThreadTenThousandSubTickTasks], "baseapp01" )
		totalTime = time.time() - startTime

		# ~10 secs
		self.assert_( int( totalTime/10 ) == 1 )


	# Do not include in auto test suite because this runs forever and 
	# should eventually fail, uncomment and run individually
	#def testFiveBgThreadRecursiveTasks( self ):
	#	bwunittest.runOnServer( [fiveBgThreadRecursiveTasks], "baseapp01" )

