import sys

from bwtest import log

from test_common import *


# Test suite 6: testing remote python console functionality

suite6 = TestSuite( 
		name = 'Test suite 6: testing remote python console functionality',
		description = 'Will test all console/process_*_request functions',
		tags = [] )




# scenario 1: test running console/process_request

class Scenario1( TestCase ):
	name = 'Test running console/process_request'
	description = 'Will run console/process_request and sanity check returned values.'
	tags = []


	def _getPythonConsoleAddr( self, processname ):
		""" will find first process's python console address """
		userObj = TestCommon.getUserObj()
		processes = command_util.selectProcesses( userObj, [processname] )
		assert processes
		process = processes[0]
		assert process
		assert process.hasPythonConsole 
		return process.machine.ip, process.getWatcherValue( "pythonServerPort" )

	def step0( self ):
		"""given server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run console/process_request"""
		# get host and port of cellapp python console 
		host, port = self._getPythonConsoleAddr( 'cellapp' )
		assert host, port
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.consoleProcessRequest( '5+5', host, port )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""check required items are present: 'output'"""
		assert 'output' in self.context['json']
		output = self.context['json']['output']
		#log.debug( "Output='%s'" % output )
		assert '>> 5+5' in output

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()



# scenario 2: test running console/process_multiline_request

class Scenario2( TestCase ):
	name = 'Test running console/process_multiline_request'
	description = 'Will run console/process_multiline_request and sanity check returned values.'
	tags = []



	def _getPythonConsoleAddr( self, processname ):
		""" will find first process's python console address """
		userObj = TestCommon.getUserObj()
		processes = command_util.selectProcesses( userObj, [processname] )
		assert processes
		process = processes[0]
		assert process
		assert process.hasPythonConsole 
		return process.machine.ip, process.getWatcherValue( "pythonServerPort" )

	def step0( self ):
		"""given server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run console/process_request"""
		# get host and port of cellapp python console 
		host, port = self._getPythonConsoleAddr( 'cellapp' )
		assert host, port
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.consoleProcessMultilineRequest( '5+5\n10+10\n', host, port )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""check required items are present: 'output'"""
		assert 'output' in self.context['json']
		output = self.context['json']['output']
		log.debug( "Output='%s'" % output )
		assert '>> 5+5' in output

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()




