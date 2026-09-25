"""
Functions can support running asynchronously by understanding a keyword
argument '_async_' being passed (which is a reference to one of these
objects).  They can signal this object with state changes, so that a listener
somewhere else (typically in the Web Console, at the moment) can extract
information from the method before it terminates.  This is useful because it
allows us to write asynchronous methods in a blocking fashion without having
to worry about splitting the methods up according to the parts we wish to
execute asynchronously.

Note that this is designed to work as a single producer/consumer mechanism.  Any
attempt to have multiple threads calling update() or calling poll() will have
strange and undesirable results.
"""

import threading
import collections
import time

import logging

log = logging.getLogger( __name__ )

class AsyncTask( threading.Thread ):

	DEFAULT_TIMEOUT = 10.0
	MAX_TERMINATED_TASK_POLL_ATTEMPTS = 10

	s_idTicker = 0
	s_idLock = threading.RLock()
	s_runningTasks = {}

	class TerminateException( Exception ):
		pass

	# I know it's ugly to have queuesize right up the front here even though
	# it's kinda optional ... when Python 2.5 introduces partial() I'll port
	# this to use that cleaner syntax instead
	def __init__( self, queuesize, func, *args, **kw ):
		"""
		Execute func with *args and **kw in a new thread, passing this AsyncTask
		object as the '_async_' kwarg to the function.  Specify queuesize > 0 to
		cause update() to block after 'queuesize' unpolled updates.
		"""

		threading.Thread.__init__( self )

		self.func = func
		self.args = args
		self.kw = kw
		self.kw[ "_async_" ] = self

		# call back function to notify worker that data has been polled
		self.pollCallback = None
		if "pollCallback" in self.kw:
			self.pollCallback = self.kw[ "pollCallback" ]
			del self.kw[ "pollCallback" ]

		self.finished = threading.Semaphore( 0 )
		self.isTerminating = False
		self.isFinished = False
		self.polledFinished = False

		self.updates = collections.deque()
		self.queueLock = threading.Condition()
		self.terminateLock = threading.Condition()

		# finalstates is a list of updates that are released to the client just
		# prior to sending the "finished" update.  At the moment this is used to
		# aggregate non-repeating errors together so they can be collected in a
		# single chunk.
		self.finalstates = []

		if queuesize:
			self.queueSem = threading.Semaphore( queuesize )
		else:
			self.queueSem = None

		# Generate unique id for this task
		self.s_idLock.acquire()
		self.id = AsyncTask.s_idTicker
		AsyncTask.s_idTicker += 1
		self.s_idLock.release()

		# Check on unjoined threads
		undyingTasks = 0
		for task in self.s_runningTasks.values():
			if task.hasTimedOut():
				log.warning( "Terminating orphaned task: %s", task )
				task.terminate()
				pollWaitAttempt = 0
				while task.isAlive():
					log.warning( "Terminated task still running ..." )
					try:
						task.poll()
					except task.TerminateException:
						log.warning( "Terminated task still running "
									 "after 'finished' state reached" )

					# An unresponsive task (eg. one that is busy outside the
					# interpreter) could spam the log here and slow the server
					# (and therefore task) down even further, creating a
					# self-perpetuating problem. It would also prevent future
					# tasks from functioning. Do not spam the log indefinitely.
					if pollWaitAttempt > self.MAX_TERMINATED_TASK_POLL_ATTEMPTS:
						log.warning(
								"Stopped waiting for terminated task to die." )
						break
					pollWaitAttempt = pollWaitAttempt + 1

				if task.isAlive():
					undyingTasks = undyingTasks + 1
				else:
					log.warning( "Terminated task is dead" )

		if undyingTasks > 0:
			log.warning( "%d terminated tasks are still running.",
						undyingTasks )

		self.timeout = self.DEFAULT_TIMEOUT
		self.lastPolled = time.time()
		self.s_runningTasks[ self.id ] = self

		self.start()

	def __str__( self ):
		return "%s() (id: %d)" % (self.func.__name__, self.id)

	def run( self ):

		try:
			result = None
			try:
				result = self.func( *self.args, **self.kw )
			except self.TerminateException:
				raise
			except Exception, ex:
				# Note that any possible exception may have been raised here!
				# Consequently, other than TerminationExceptions (which have
				# their own special handling), all other exception types must be
				# caught, logged and handled gracefully, otherwise the client
				# (and user) will never be informed of the situation.
				log.exception( ex )

				# display the error on the client
				self.update( "__error__", str( ex ) )

			# Clear finalstates
			for state, data in self.finalstates:
				self.update( state, data )

			# Signal task termination to the client
			self.update( "finished", result )

		except self.TerminateException:
			pass

		self.isFinished = True
		self.finished.acquire()

		# Explicitly throw away references to passed in parameters to avoid
		# cyclic reference problems
		self.func = None
		self.args = None
		self.kw = None

	def extendTimeout( self, extendBy ):
		"""Extend the timeout of the async task by 'extendBy' seconds"""

		self.timeout = self.timeout + extendBy
		return

	def update( self, state = None, data = None ):
		"""
		Add a new state and data change to the queue.  If no state or arguments
		are passed, then no change will be made to this object's update queue
		but we will still check if this task has been externally terminated.
		"""

		# If it's been too long since this task was polled, terminate it
		if self.hasTimedOut():
			log.warning( "Terminating task %d during update() due to "
						 "poll timeout (%.1fs)", self.id, self.timeout )
			raise self.TerminateException

		if self.queueSem and state is not None:
			self.queueSem.acquire()

		# This allows us to make 'func' terminate early without having to write
		# handlers into each function supporting _async_
		if self.isTerminating:
			raise self.TerminateException

		# Don't modify state queue when no change passed
		if state is None:
			return

		self.queueLock.acquire()
		self.updates.append( (state, data) )
		self.queueLock.notify()
		self.queueLock.release()


	def updateFinal( self, state, data = None ):
		"""
		Add a new state and data tuple to the finalstates collection.  You
		aren't allowed to pass null states to this method.
		"""

		# Still check for task termination
		if self.isTerminating:
			raise self.TerminateException

		self.finalstates.append( (state, data) )


	def poll( self, blocking = False, max = None ):
		"""
		In non-blocking mode, returns lists of all the state and data updates
		since the last poll().  In blocking mode, waits for at least a single
		update and then returns all updates in the queue.

		If max is non-zero, it defines the maximum number of updates that will
		be returned.

		If you have already polled() the 'finished' state, an exception will be
		raised here.
		"""

		if self.polledFinished:
			raise self.TerminateException

		updates = []
		self.lastPolled = time.time()

		try:
			self.queueLock.acquire()

			if blocking:
				while not self.updates:
					self.queueLock.wait()

			while self.updates and (not max or len( updates ) < max):
				updates.append( self.updates.popleft() )
				if updates[-1][0] == "finished":
					self.polledFinished = True
				if self.queueSem:
					self.queueSem.release()

		finally:
			self.queueLock.release()

		if self.pollCallback:
			self.pollCallback()

		return updates


	def terminate( self ):

		# Don't let two threads come in here at once
		try:
			self.terminateLock.acquire()

			if self.isTerminating:
				return
			else:
				self.isTerminating = True

		finally:
			self.terminateLock.release()

		self.finished.release()
		if self.queueSem:
			self.queueSem.release()
		self.join()
		del self.s_runningTasks[ self.id ]

	def queueSize( self ):
		try:
			self.queueLock.acquire()
			return len( self.updates )
		finally:
			self.queueLock.release()

	def setTimeout( self, secs ):
		self.timeout = secs

	def hasTimedOut( self ):
		return time.time() - self.lastPolled > self.timeout

	def waitForState( self, state ):
		"""
		This method is called from outside the task's thread (i.e. by the
		consumer) to wait for a particular state update from the worker thread.

		Any updates that are consumed before the target state comes along are
		preserved.
		"""

		preceding = collections.deque()

		while True:
			updates = self.poll( True, 1 )
			for s, d in updates:
				if s == state:

					# Re-insert preceding states
					self.queueLock.acquire()
					self.updates.extendleft( preceding )
					self.queueLock.release()

					return (s, d)

				# We deliberatly assemble the preceding list in reverse order
				# because when we re-insert it with extendleft() it will be
				# reversed again.
				else:
					preceding.appendleft( (s, d) )

	@classmethod
	def get( self, id ):
		return self.s_runningTasks[ id ]
