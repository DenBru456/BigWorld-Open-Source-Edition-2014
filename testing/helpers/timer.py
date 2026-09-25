"""This module contains helper methods for waiting for arbitrary events on
a timeout.
"""

import time
from datetime import datetime

from error import HelperError


class TimerError( HelperError ):
	"""Exception class for when a timer times out. 
	"""
	pass


class Timer( object ):
	""" This class helps wait for arbitrary events
	on a timeout"""

	def __init__( self, callableObject, checker, timeout = 30, period = 1,
				**args ):
		""" Creates a timer.
		@param callableObject: a callable object to call
		@param checker: a function to check the value returned from callable
						it must return True if operation succeeded
		@param period: period to call callable object
		@param timeout: timeout to raise an exception
		"""
		
		self._callable = callableObject
		self._checker = checker
		self._timeout = timeout
		self._period = period
		self._callableargs = args


	def run( self ):
		""" 
		This method runs the timer and returns the result from
		callable if successful
		"""

		startTime = datetime.now()
		while True:
			res = self._callable( **self._callableargs )
			if self._checker( res ):
				return res
				
			time.sleep( self._period )
			
			currTime = datetime.now()
			if (currTime - startTime).seconds > self._timeout:
				raise TimerError( "Timer.run() timed out (> %.2f seconds)" %
									self._timeout )


def runTimer( callableMethod,
				checker = lambda res: res,
				timeout = 30,
				period = 1,
				**args ):
	""" Runs a timer.
	@param callableMethod: a callable method to call
	@param checker: a function to check the value returned from callable
					it must return True if operation succeeded
	@param period: period to call callable object
	@param timeout: timeout to raise an exception
	"""
	
	timer = Timer( callableMethod, checker, timeout, period, **args )
	return timer.run()
