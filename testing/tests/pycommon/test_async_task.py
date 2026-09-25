from bwtest import TestCase
from helpers.timer import runTimer

from pycommon.async_task import AsyncTask

from time import sleep
from datetime import datetime
from threading import Thread


class TestAsyncTask( TestCase ):
	"""
	This class tests the following behaviour in the AsyncTask class:
	- Simple timeout and termination
	- Termination from a second task after timing out
	- Multiple terminations in a threaded environment (which is what happens in
	  WebConsole). The main goal is to ensure that the logs are not endlessly
	  spammed with warnings.

	TODO: Extend this test suite to include interactive AsyncTask functionality such
	as updating and polling.
	"""

	def setUp( self ):
		self.reset()
	# setUp


	def tearDown(self):
		if self.sleepTask:
			self.sleepTask.terminate()
		if self.joinTask:
			self.joinTask.terminate()
		if self.stateCheckTask:
			self.stateCheckTask.terminate()

	def reset( self ):
		self.entryStates = {}
		self.exitStates = {}
		self.sleepTask = None
		self.joinTask = None
		self.stateCheckTask = None
		self.sleepAndJoinException = None
		self.stateCheckException = None
	# reset


	def runTest( self ):
		self.testSimpleTimeoutTermination()
		self.reset()
		self.testTimeoutTerminationFromAnotherTask()
		self.reset()
		self.testTimeoutTerminationFromTwoThreads()
	# runTest


	def testSimpleTimeoutTermination( self ):
		"""
		Wait for sleepTask to go over its timeout period and then
		terminate it.
		"""
		# ensure entry and exit states are clear of other tests
		self.sleepTask = AsyncTask( 0, self.sleepFunc,
							sleepTime = (AsyncTask.DEFAULT_TIMEOUT + 5 ),
							taskName = "sleepTask" )

		# wait for AsyncTask.DEFAULT_TIMEOUT (10 sec)
		runTimer( self.sleepTask.hasTimedOut )

		# Terminate calls join() and will wait for sleepFunc to complete (5
		# seconds after timeout)
		self.sleepTask.terminate()

		# Terminate should not return until the task has completed. Ensure it
		# has.
		self.assertTrue( "sleepTask" in self.entryStates )
		self.assertTrue( "sleepTask" in self.exitStates )
		self.assertTrue( not self.sleepTask.isAlive() )
	# testSimpleTimeoutTermination


	def testTimeoutTerminationFromAnotherTask( self ):
		"""
		Wait for sleepTask to go over its timeout period and then start a second
		task. The second task should automatically terminate the first. Then
		cleanly terminate the second task.
		"""
		# ensure entry and exit states are clear of other tests
		self.sleepTask = AsyncTask( 0, self.sleepFunc, 
							sleepTime = (AsyncTask.DEFAULT_TIMEOUT + 5 ),
							taskName = "sleepTask" )

		# Ensure the func starts
		runTimer( lambda: ("sleepTask" in self.entryStates) )

		# Allow the task to timeout
		runTimer( self.sleepTask.hasTimedOut )

		# This task will not start its func until it terminates sleepTask.
		self.joinTask = AsyncTask( 0, self.stateMonitoringFunc,
									taskName = "joinTask" )

		# joinTask should not have returned until sleepTask was terminated
		self.assertTrue( "sleepTask" in self.exitStates )
		self.assertTrue( not self.sleepTask.isAlive() )

		# Ensure the second task terminates if told to terminate
		self.joinTask.terminate()
		self.assertTrue( "joinTask" in self.entryStates )
		self.assertTrue( "joinTask" in self.exitStates )
		self.assertTrue( not self.joinTask.isAlive() )
	# testTimeoutTerminationFromAnotherTask


	def testTimeoutTerminationFromTwoThreads( self ):
		"""
		In the above tests, AsyncTask.__init__ calls do not process in
		parallel (__init__ functions trigger sequentially if they are called
		from the same execution block).

		This test is to trigger new tasks from separate threads so that
		AsyncTask.__init__ functions occur in parallel (which is what happens
		in WebConsole as fetch requests come in). This is where AsyncTask
		behaviour needs to be truly tested.
		"""
		# Create the sleep task and the join task.
		sleepAndJoinThread = Thread( target = self.createSleepAndJoinTasks )
		sleepAndJoinThread.start()

		# Wait until the sleep task indicates that it has been told to terminate
		runTimer( lambda: (self.sleepTask and self.sleepTask.isTerminating) )

		# Create another task which will also attempt to terminate, fail
		# immediately and then start to check isAlive().
		stateCheckThread = Thread( target = self.createStateCheckTask )
		stateCheckThread.start()

		# Finish the threads and check their status. Give them a suitable amount
		# of time to rejoin.
		stateCheckThread.join( timeout = AsyncTask.DEFAULT_TIMEOUT + 20)
		self.assertTrue( not stateCheckThread.isAlive() )

		# Raise any assertions or exceptions from the stateCheckThread (this
		# is why we need to wait for the thread to complete/join).
		if self.stateCheckException:
			raise self.stateCheckException

		sleepAndJoinThread.join( timeout = AsyncTask.DEFAULT_TIMEOUT + 20)

		# Confirm that the sleep task died and rejoined cleanly (ie. did not get
		# into a bad state).
		self.assertTrue( not sleepAndJoinThread.isAlive() )

		# Raise any assertions or exceptions from the sleepAndJoinThread (this
		# is why we need to wait for the thread to complete/join).
		if self.sleepAndJoinException:
			raise self.sleepAndJoinException
	# testTimeoutTerminationFromTwoThreads


	def createSleepAndJoinTasks( self ):
		"""
		This method is a workaround to handle the fact that Thread exceptions
		can not be raised to the caller. If an exception occurs, store it in a
		class variable (so it can be reraised by the caller if/when the caller
		tells the thread to join and checks for the exception).
		"""
		try:
			self.doCreateSleepAndJoinTasks()
		except Exception, ex:
			self.sleepAndJoinException = ex
			raise
	# createSleepAndJoinTasks


	def doCreateSleepAndJoinTasks( self ):
		self.sleepTask = AsyncTask( 0, self.sleepFunc,
							sleepTime = (AsyncTask.DEFAULT_TIMEOUT + 10 ),
							taskName = "sleepTask" )

		runTimer( lambda: ("sleepTask" in self.entryStates) )

		# Give the task a chance to timeout
		runTimer( self.sleepTask.hasTimedOut )

		self.joinTask = AsyncTask( 0, self.stateMonitoringFunc,
							taskName = "joinTask" )

		# At this point sleepTask should have completed.
		self.assertTrue( self.exitStates[ "sleepTask" ] )

		# Wait until joinTask has completed
		runTimer( lambda: ("joinTask" in self.exitStates) )

		# Terminate joinTask
		self.joinTask.terminate()
		self.assertTrue( not self.joinTask.isAlive() )
	# doCreateSleepAndJoinTasks


	def createStateCheckTask( self ):
		try:
			self.doCreateStateCheckTask()
		except Exception, ex:
			self.stateCheckException = ex
			raise
	# createStateCheckTask


	def doCreateStateCheckTask( self ):
		self.stateCheckTask = AsyncTask( 0, self.stateMonitoringFunc,
									taskName = "stateCheckTask" )

		# This is a critical test point. The stateCheckTask should have returned
		# from __init__ well before sleepTask completed. If it hasn't then it
		# has waited on sleepTask, when it definitely shouldn't have.
		self.assertTrue( not "sleepTask" in self.exitStates )

		# Give it a moment to process its func. Should only take a short moment.
		runTimer( lambda: ("stateCheckTask" in self.exitStates) )

		# Terminate it
		self.stateCheckTask.terminate()
		self.assertTrue( not self.stateCheckTask.isAlive() )
	# doCreateStateCheckTask


	def sleepFunc( self, _async_, sleepTime, taskName ):
		self.entryStates[ taskName ] = True
		sleep( sleepTime )
		self.exitStates[ taskName ] = True
	# sleepFunc


	def stateMonitoringFunc( self, _async_, taskName ):
		self.entryStates[ taskName ] = True
		self.exitStates[ taskName ] = True
	# stateMonitoringFunc

# TestAsyncTask
