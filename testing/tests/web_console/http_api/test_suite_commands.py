import sys
import time

from test_common import *

from bwtest import log

# Test suite 5: testing commands/scripts functionality

suite5 = TestSuite( 
		name = 'Test suite 5: testing commands/scripts functionality',
		description = 'Will test all commands/scripts functions',
		tags = [] )




# scenario 1: test running commands/getscripts

class Scenario1( TestCase ):
	name = 'Test running commands/getscripts'
	description = 'Will run commands/getscripts and sanity check returned values.'
	tags = []


	def step0( self ):
		"""given server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run commands/getscripts"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.commandsGetScripts( 'watcher' )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert self.context['code'] == 200, 'Status code was %r' % self.context['code']

	def step3( self ):
		"""check required items are present: 'scripts'"""
		assert 'scripts' in self.context['json']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 2: test running commands/scriptinfo

class Scenario2( TestCase ):
	name = 'Test running commands/scriptinfo'
	description = 'Will run commands/scriptinfo and sanity check returned values.'
	tags = []

	def step0( self ):
		"""given server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run commands/scriptinfo"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.commandsScriptInfo( 'watcher:cellapp:any:command/retireCellApp' )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert self.context['code'] == 200, 'Status code was %r' % self.context['code']

	def step3( self ):
		"""check required items are present: 'title', 'procType', 'args'"""
		required_sections = [
			'title', 'procType', 'args' ]

		for item in required_sections:
			if not item in self.context['json']:
				log.debug( "section %s not found in json" % item )
				assert False


	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 3: test running commands/executescript

class Scenario3( TestCase ):
	name = 'Test running commands/executescript'
	description = 'Will run commands/executescript and sanity check returned values.'
	tags = []


	def step0( self ):
		"""given server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""start another cellApp"""
		loadOk = TestCommon.startProc( "cellapp", 1 )
		assert( loadOk )
		time.sleep( 1 )

	def step2( self ):
		"""run commands/executescript"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.commandsExecuteScript( 'watcher:cellapp:any:command/retireCellApp', 
			[[ '1001', Constants.TYPE_INT ]], runType=1  ) 

	def step3( self ):
		"""check returned code is 200 (OK)"""
		assert self.context['code'] == 200, 'Status code was %r' % self.context['code']

	def step4( self ):
		"""check required items are present: 'result', 'output', 'errors'"""
		assert 'output' in self.context['json']
		output = self.context['json']['output']

		required_sections = [
			'result', 'output', 'errors' ]

		for item in required_sections:
			if not item in output:
				log.debug( "section %s not found in output" % item )
				assert False


	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()



