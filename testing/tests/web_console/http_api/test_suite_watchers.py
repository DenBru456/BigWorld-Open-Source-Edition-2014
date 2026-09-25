import sys
import time

from test_common import *

# Test suite 2: testing watcher functionality
suite2 = TestSuite( 
		name = 'Test suite 2: testing watcher functionality',
		description = 'Will test all watcher functions',
		tags = [] )


# scenario 1: test running Watchers/get_filtered_tree with existing path

class Scenario1( TestCase ):
	name = 'Test running Watchers/get_filtered_tree with existing path'
	description = "Will run get_filtered_tree command and check for OK code and " \
				  "that required components are returned"
	tags = []



	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run get_filtered_tree"""
		time.sleep( 5 )
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.watchersGetFilteredTree( 
			'cellappmgr', 'cellApps/*/*' )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check 'status', 'path' and 'processes' components exist"""
		assert 'status' in self.context['json']
		assert 'path' in self.context['json']
		assert 'processes' in self.context['json']
		assert 'tree' in self.context['json']

	def step4( self ):
		"""and check 'status' is true"""
		assert( self.context['json']['status'] == True )

	def step5( self ):
		"""and check 'path' and 'processes' components equal to passed in values"""
		assert( self.context['json']['processes'] == 'cellappmgr' )
		assert( self.context['json']['path'] == 'cellApps/*/*' )

	def step6( self ):
		"""and check 'tree' component contains 'subPaths' and 'values'"""
		assert 'subPaths' in self.context['json']['tree']
		assert 'values' in self.context['json']['tree']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# scenario 2: test running Watchers/get_filtered_tree with non-existing path

class Scenario2( TestCase ):
	name = 'Test running Watchers/get_filtered_tree with non-existing path'
	description = "Will run get_filtered_tree command and check for OK code and " \
				  "that required components are returned"
	tags = []


	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run get_filtered_tree"""
		time.sleep( 5 )
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.watchersGetFilteredTree( 
				'cellappmgr', 'cellFailApps/*/*' )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check 'status' component exists"""
		assert 'status' in self.context['json']

	def step4( self ):
		"""and check 'status' is true"""
		assert( self.context['json']['status'] == True )

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 3: test running Watchers/get_filtered_tree on multiple cellapps

class Scenario3( TestCase ):
	name = 'Test running Watchers/get_filtered_tree on multiple cellapps'
	description = 'Will run get_filtered_tree command on 2 cellapps and ' \
				  'check for OK code ' \
				  'and that required components are returned'
	tags = []



	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""start another cellapp"""
		loadOk = TestCommon.startProc( "cellapp", 1 )
		#assert( loadOk )

	def step2( self ):
		"""run get_filtered_tree"""
		time.sleep( 5 )
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.watchersGetFilteredTree( 
			'cellapps', 'config/*' )

	def step3( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step4( self ):
		"""and check "status', 'path' and 'processes' components exist"""
		assert 'status' in self.context['json']
		assert 'path' in self.context['json']
		assert 'processes' in self.context['json']
		assert 'tree' in self.context['json']

	def step5( self ):
		"""and check 'status' is true"""
		assert( self.context['json']['status'] == True )

	def step6( self ):
		"""and check 'path' and 'processes' components equal to passed in values"""
		assert( self.context['json']['processes'] == 'cellapps' )
		assert( self.context['json']['path'] == 'config/*' )

	def step7( self ):
		"""and check 'tree' component contains 'subPaths' and 'values'"""
		assert 'subPaths' in self.context['json']['tree']
		assert 'values' in self.context['json']['tree']

	def step8( self ):
		"""and check 'values' contains 2 elements"""
		assert len( self.context['json']['tree']['values'] ) == 2

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 4: test running Watchers/show

class Scenario4( TestCase ):
	name = 'Test running watchers/tree/show on cellAppMgr'
	description = "Will run watchers/tree/show command on the cellAppMgr and " \
				  "check for OK code and that required components are returned"
	tags = []



	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run watchers/tree/show on the cellappmgr"""
		env = command_util.CommandEnvironment( config.WCAPI_USER )
		pid = TestCommon.getPids( 'cellappmgr' )[0]
		assert pid

		self.context['cellappmgr_pid'] = pid;
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.watchersShow( 
				config.CLUSTER_MACHINES[0], pid, 'version/major' )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check 'machine', 'process' and 'watcherData' components exist"""
		assert 'machine' in self.context['json']
		assert 'process' in self.context['json']
		assert 'watcherData' in self.context['json']

	def step4( self ):
		"""and check 'process' is 'cellappmgr' and 'machine' is 'bw02'"""
		assert( self.context['json']['process']['pid'] == self.context['cellappmgr_pid'] )
		assert( self.context['json']['process']['label'] == 'cellappmgr' )
		assert( self.context['json']['machine']['name'] == config.CLUSTER_MACHINES[0] )

	def step5( self ):
		"""and check 'watcherData/name' = 'version/major'"""
		assert self.context['json']['watcherData']['path'] == 'version/major'

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 5: test running Watchers/edit

class Scenario5( TestCase ):
	name = 'Test running Watchers/edit'
	description = 'Will run edit command on a watcher value and ' \
				  'check that it has been changed'
	tags = []



	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run watchers/tree/edit"""
		env = command_util.CommandEnvironment( config.WCAPI_USER )
		pid = TestCommon.getPids( 'cellappmgr' )[0]
		assert pid

		self.context['cellappmgr_pid'] = pid;
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.watchersEdit( 
			config.CLUSTER_MACHINES[0], pid, 'config/cellAppLoad/lowerBound', 
			Constants.TYPE_FLOAT,
			0.0123 )

	def step2( self ):
		"""check returned code is 302 (Found)"""
		assert( self.context['code'] == 302 )

	def step3( self ):
		"""and check via control_cluster that value has been changed"""
		pid = self.context['cellappmgr_pid']
		watcherVal = TestCommon.getWatcher( pid, 'config/cellAppLoad/lowerBound' )
		assert watcherVal
		assert abs(watcherVal.value - 0.0123) < 0.01

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 6: test running Watchers/edit with a non-existent path

class Scenario6( TestCase ):
	name = 'Test running Watchers/edit on missing watcher'
	description = 'Will run edit command on a non-extant watcher value ' \
				  'and check that 302 is returned'
	tags = []



	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run watchers/tree/edit"""
		env = command_util.CommandEnvironment( config.WCAPI_USER )
		pid = TestCommon.getPids( 'cellappmgr' )[0]
		assert pid

		self.context['cellappmgr_pid'] = pid;
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.watchersEdit( 
			config.CLUSTER_MACHINES[0], pid, 'config/cellAppLoad/lowerUnBound', 
			Constants.TYPE_FLOAT,
			0.0123 )

	def step2( self ):
		"""check returned code is 302 (Found)"""
		assert( self.context['code'] == 302 )

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


