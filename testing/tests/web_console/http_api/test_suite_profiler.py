"""
The start of a test suite for the profiler API endpoints. Initially only a
limited set of negative tests that test for invalid input arguments.
"""

import sys
import time

from test_common import *

class ProfilerCommon( TestCase ):
	name = 'Common Profiler parent class'
	description = "Doesn't run any tests!"

	# def __init__( self ):
	# 	super( ProfilerCommon, self ).__init__()
	# 	self.webConsole = None

	def setUp( self ):
		assert( TestCommon.restartServer() )
		self.webConsole = StartWebConsoleAPI()

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


	def _testServerErrorResponse( self, response, exceptionType, message,
															code=500 ):
		"""Check that the response contains the expected error values.

		@param response: A response from a call that should have the known error
		@param exceptionType: String representation of the exception class
		@param message: String that the error message must start with
		@param code: Error code to check for. Defaults to 500.
		"""
		self.assertEquals( response[0],  code )
		self.assertEquals( response[1].get( 'exception' ), exceptionType )
		responseMessage = response[1].get( 'message' )
		self.assertTrue( responseMessage != None )
		self.assertTrue( message in responseMessage )

	def _testEmptyValueResponse( self, response, name ):
		"""Check the response for the common test of arguments with empty values
		@param response: A response from a call that should have the known error
		@param name: The argument name to test for
		"""
		self._testServerErrorResponse( response, 'IllegalArgumentException',
								  "No value provided for '%s'" % name )

	def _machineAndPidTest( self, endpoint, extras={} ):
		"""Test the very common set of "machine" and "pid" arguments.
		@param endpoint: The profiler endpoint to call
		@param extras: Dictionary of extra arguments to include to make the call
		valid.
		"""
		response = self.webConsole.profilerRequest( endpoint,
					dict( {'machine': '', 'pid': 1}, **extras ) )
		self._testEmptyValueResponse( response, 'machine' )
		response = self.webConsole.profilerRequest( endpoint,
					dict( {'machine': 'ZZZZ', 'pid': ''}, **extras ) )
		self._testEmptyValueResponse( response, 'pid' )
		response = self.webConsole.profilerRequest( endpoint,
					dict( {'machine': 'ZZZZ', 'pid': 1}, **extras ) )
		self._testServerErrorResponse( response, 'ServerStateException',
					'Machine ZZZZ appears to be offline', code=455 )

class ProfilerDeleteScenario( ProfilerCommon ):
	name = 'Invalid arguments to "delete"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of delete"""
		ENDPOINT = 'delete'

		response = self.webConsole.profilerRequest( ENDPOINT, {'fileName': ''} )
		self._testEmptyValueResponse( response, 'fileName' )

		response = self.webConsole.profilerRequest( ENDPOINT,
											{'fileName': 'ZZZZZZZZZZ.ZZZ'} )
		self._testServerErrorResponse( response, 'IOError', 'File not found' )

		response = self.webConsole.profilerRequest( ENDPOINT,
											{'fileName': '../../ZZZZ.ZZZ'} )
		self._testServerErrorResponse( response, 'IllegalArgumentException',
										'Dangerous and suspicious fileName' )


class ProfilerViewScenario( ProfilerCommon ):
	name = 'Invalid arguments to "view"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of view"""
		ENDPOINT = 'view'

		response = self.webConsole.profilerRequest( ENDPOINT, {'fileName': ''} )
		self._testEmptyValueResponse( response, 'fileName' )

		response = self.webConsole.profilerRequest( ENDPOINT,
												{'fileName': 'ZZZZZZZZZZ.ZZZ'} )
		self._testServerErrorResponse( response, 'IOError', 'File not found' )

		response = self.webConsole.profilerRequest( ENDPOINT,
												{'fileName': '../../ZZZZ.ZZZ'} )
		self._testServerErrorResponse( response, 'IllegalArgumentException',
										'Dangerous and suspicious fileName' )

class ProfilerLiveViewScenario( ProfilerCommon ):
	name = 'Invalid arguments to "liveview"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of liveview"""
		ENDPOINT = 'liveview'

		self._machineAndPidTest( ENDPOINT )

class ProfilerStartProfileScenario( ProfilerCommon ):
	name = 'Invalid arguments to "startProfile"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of startProfile"""
		ENDPOINT = 'startProfile'

		baseParams = {
			'machine': 'ZZZZ',
			'pid': 1,
			# Does not check valid values yet for the following
			'sortMode': 'ZZZZ',
			'exclusive': 'ZZZZ',
			'category': 'ZZZZ',
		}

		response = self.webConsole.profilerRequest( ENDPOINT, baseParams )
		self._testServerErrorResponse( response, 'ServerStateException',
								'Machine ZZZZ appears to be offline', code=455 )
		for key in baseParams.keys():
			params = baseParams.copy()
			params[key] = ''
			response = self.webConsole.profilerRequest( ENDPOINT, params )
			self._testEmptyValueResponse( response, key )

class ProfilerStopProfileScenario( ProfilerCommon ):
	name = 'Invalid arguments to "stopProfile"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of stopProfile"""
		ENDPOINT = 'stopProfile'

		self._machineAndPidTest( ENDPOINT )

class ProfilerStartRecordingScenario( ProfilerCommon ):
	name = 'Invalid arguments to "startRecording"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of startRecording"""
		ENDPOINT = 'startRecording'

		self._machineAndPidTest( ENDPOINT, {'dumpCounts': 1} )
		response = self.webConsole.profilerRequest( ENDPOINT,
			{'dumpCounts': 'ZZZZ', 'machine': 'ZZZZ', 'pid': 1} )
		self._testServerErrorResponse( response, 'IllegalArgumentException',
									   'Invalid value for \'dumpCounts\'' )
		response = self.webConsole.profilerRequest( ENDPOINT,
			{'dumpCounts': '1.0', 'machine': 'ZZZZ', 'pid': 1} )
		self._testServerErrorResponse( response, 'IllegalArgumentException',
									   'Invalid value for \'dumpCounts\'' )
		response = self.webConsole.profilerRequest( ENDPOINT,
			{'dumpCounts': 0, 'machine': 'ZZZZ', 'pid': 1} )
		self._testServerErrorResponse( response, 'IllegalArgumentException',
									   '\'dumpCounts\' must be greater than 0' )
		response = self.webConsole.profilerRequest( ENDPOINT,
			{'dumpCounts': -1, 'machine': 'ZZZZ', 'pid': 1} )
		self._testServerErrorResponse( response, 'IllegalArgumentException',
									   '\'dumpCounts\' must be greater than 0' )



class ProfilerCancelRecordingScenario( ProfilerCommon ):
	name = 'Invalid arguments to "cancelRecording"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of cancelRecording"""
		ENDPOINT = 'cancelRecording'

		self._machineAndPidTest( ENDPOINT )

class ProfilerProfileStatusScenario( ProfilerCommon ):
	name = 'Invalid arguments to "profileStatus"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of profileStatus"""
		ENDPOINT = 'profileStatus'

		self._machineAndPidTest( ENDPOINT )

class ProfilerSetWatcherScenario( ProfilerCommon ):
	name = 'Invalid arguments to "setWatcher"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of setWatcher"""
		ENDPOINT = 'setWatcher'

		baseParams = {
			'machine': 'ZZZZ',
			'pid': 1,
			'path': 'profiler/Z',
			'value': 'ZZZZ',
		}

		response = self.webConsole.profilerRequest( ENDPOINT, baseParams )
		self._testServerErrorResponse( response, 'ServerStateException',
								'Machine ZZZZ appears to be offline', code=455 )
		for key in baseParams.keys():
			params = baseParams.copy()
			params[key] = ''
			response = self.webConsole.profilerRequest( ENDPOINT, params )
			self._testEmptyValueResponse( response, key )
		params = baseParams.copy()
		params['path'] = 'ZZZ'
		response = self.webConsole.profilerRequest( ENDPOINT, params )
		self._testServerErrorResponse( response, 'IllegalArgumentException',
								 'Invalid watcher path: ZZZ' )

class ProfilerStatisticsScenario( ProfilerCommon ):
	name = 'Invalid arguments to "statistics"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of statistics"""
		ENDPOINT = 'statistics'

		self._machineAndPidTest( ENDPOINT )

class ProfilerProfileDumpScenario( ProfilerCommon ):
	name = 'Invalid arguments to "getProfileDump"'
	description = "Will call with obviously invalid arguments and test that" + \
					"they fail"
	tags = ['test_suite_profiler']

	def runTest( self ):
		"""Check the behaviour of statistics"""
		ENDPOINT = 'getProfileDump'

		response = self.webConsole.profilerRequest( ENDPOINT,
					{'machine': '', 'dumpFilePath': 'ZZZZ'} )
		self._testEmptyValueResponse( response, 'machine' )
		response = self.webConsole.profilerRequest( ENDPOINT,
					{'machine': 'ZZZZ', 'dumpFilePath': ''} )
		self._testEmptyValueResponse( response, 'dumpFilePath' )
