import sys
import time
from datetime import datetime

from bwtest import log

from test_common import *

from pycommon.process import Process

suite1 = TestSuite( 
		name = 'Test suite 1: testing server control functionality',
		description = 'Will test all server control functions',
		tags = [] )


# scenario 1: starting server in single mode
class Scenario1( TestCase ):
	name = 'Test starting the server in single mode'
	description = 'Will run start command and check for success'
	tags = []


	def step1( self ):
		"""run doStart"""
		TestCommon._getCC()
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.startServer( 
													config.CLUSTER_MACHINES[0] )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ): 
		"""and returned layout includes all required apps"""
		TestCommon._getCC().waitForServerSettle()
		reqitems = { 'cellappmgr': 0, 
					 'baseappmgr': 0, 
					 'dbapp': 0, 
					 'loginapp': 0, 
					 'serviceapp': 0, 
					 'baseapp': 0, 
					 'cellapp': 0 }

		assert self.context['json']['layout']

		for item in self.context['json']['layout']:
			if item[3] == 'running':
				if item[1] in reqitems:
					reqitems[ item[1] ] = reqitems[ item[1] ] + 1

		for key in reqitems:
			assert( reqitems[key] >0 )

	def step4( self ):
		"""and returned action is 'start'"""
		assert( self.context['json']['action'] == 'start' )

	def tearDown( self ):
		"""Shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()



# scenario 2: stopping started server

class Scenario2( TestCase ):
	name = 'Test stopping a started server'
	description = 'Will run stop command and check for success'
	tags = []

	def step0( self ):
		"""Given that server is started"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run stop"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.stopServer()

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		time.sleep( 1 )
		"""and returned layout includes none of the required apps"""
		reqitems = { 'cellappmgr': 0, 
					 'baseappmgr': 0, 
					 'dbapp': 0, 
					 'loginapp': 0, 
					 'baseapp': 0, 
					 'cellapp': 0 }

		assert self.context['json']['layout']

		for item in self.context['json']['layout']:
			if item[3] == 'registered':
				if item[1] in reqitems:
					reqitems[ item[1] ] = reqitems[ item[1] ] + 1

		for key in reqitems:
			assert( reqitems[key] >0 )


	def step4( self ):
		"""and returned action is 'stop'"""
		assert( self.context['json']['action'] == 'stop' )


	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 3: test restarting the server in single mode

class Scenario3( TestCase ):
	name = 'Test restarting the server in single mode'
	description = 'Will run restart command and check for success'
	tags = []


	def _waitForServer( self, timeout = 60 ):

		reqitems = Process.types.required( 
								TestCommon._getCC().getUser().version ).keys()

		startTime = datetime.now()
		while( True ):
			procs = TestCommon.getProcs()
			if procs:
				log.debug( "WaitForServer: got procs: %s" % procs )

				allItemsPresent = True
				for item in reqitems:
					if not item in procs:
						allItemsPresent = False
						break

				if allItemsPresent:
					log.debug( "WaitForServer: got all server procs, "\
								"returning True" )
					return True

			curTime = datetime.now()
			if (curTime - startTime).seconds > timeout:
				log.debug( "WaitForServer: timeout reached, "\
						"server not started properly, returning False" )
				return False

			time.sleep( 1 )

	def _waitForShutdown( self, procs, timeout = 60 ):

		log.debug( "WaitForShutdown: checking procs %s" % procs )

		startTime = datetime.now()
		while( True ):
			serverRunning = False
			for procName in procs.keys():
				for procPid in procs[procName]:
					if TestCommon.getProcs( procName, procPid ):
						serverRunning = True
						break

			if not serverRunning:
				log.debug( "WaitForShutdown: check complete. Success." )
				return True

			curTime = datetime.now()
			if (curTime - startTime).seconds > timeout:
				log.debug( "WaitForShutdown: timeout reached, "\
						"server not started properly, returning False" )
				return False

			time.sleep( 1 )

		
	def step0( self ):
		"""Given that server is started"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run restart"""
		time.sleep( 4 )
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.restartServer()

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ): 
		"""and returned layout includes all required apps"""
		reqitems = { 'cellappmgr': [], 
					 'baseappmgr': [], 
					 'dbapp': [], 
					 'loginapp': [], 
					 'serviceapp': [], 
					 'baseapp': [], 
					 'cellapp': [] }

		assert self.context['json']['layout']
		log.debug( "Layout returned: %r" % self.context['json']['layout'] )

		for item in self.context['json']['layout']:
			if item[3] == 'running' or item[3] == 'registered':
				if item[1] in reqitems:
					reqitems[ item[1] ].append( item[2] )	# store pid

		for key in reqitems:
			assert( len( reqitems[key] ) >0 )

		self._waitForShutdown( reqitems )	# due to async call: first wait for 
											# server to shutdown
		self._waitForServer()				# due to async call: wait for server 
											# to finish startup

	def step4( self ):
		"""and returned action is 'restart'"""
		assert( self.context['json']['action'] == 'restart' )

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()



# scenario 4: test starting a process

class Scenario4( TestCase ):
	name = 'Test starting a process'
	description = 'Will run startproc command and check'\
				' for added process via control cluster'
	tags = []


	def _collectProcCounts( self ):
		reqitems = { 'cellappmgr': 0, 
					 'baseappmgr': 0, 
					 'dbapp': 0, 
					 'loginapp': 0, 
					 'serviceapp': 0, 
					 'baseapp': 0, 
					 'cellapp': 0 }

		procs = TestCommon.getProcs()
		assert procs
		log.debug( "got procs: %s" % procs )

		for item in procs:
			if item in reqitems:
				reqitems[ item ] = reqitems[ item ] + 1

		return reqitems

	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""count the apps"""
		time.sleep( 1 )
		reqitems = self._collectProcCounts()
		self.context['apps'] = reqitems

	def step2( self ):
		"""then run startproc with 2 cellapps"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
					w.startProcess( config.CLUSTER_MACHINES[0], "cellapp", 2 )

	def step3( self ):
		"""check returned code is 302 (Found)"""
		print self.context['json']

	def step4( self ):
		"""and count the apps to have two more cellapps"""
		time.sleep( 1 )
		reqitems = self._collectProcCounts()
		assert self.context['apps']['cellapp'] +2 == reqitems['cellapp']
		self.context['apps'] = reqitems

	def step5( self ):
		"""then run startproc with 1 base"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
					w.startProcess( config.CLUSTER_MACHINES[0], "baseapp", 1 )

	def step6( self ):
		"""check returned code is 302 (Found)"""
		#self.assertTrue( self.context['code'] == 302, "expected code 302, got %r" % self.context['code'] )

	def step7( self ):
		"""and count the apps to have one more baseapp"""
		time.sleep( 1 )
		reqitems = self._collectProcCounts()
		assert self.context['apps']['baseapp'] +1 == reqitems['baseapp']
		self.context['apps'] = reqitems

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 5: test stopping a process

class Scenario5( TestCase ):
	name = 'Test stopping a process'
	description = 'Will run stopproc command and check for'\
				' removed process via control cluster'
	tags = []


	def _collectProcCounts( self ):
		reqitems = { 'cellappmgr': 0, 
					 'baseappmgr': 0, 
					 'dbapp': 0, 
					 'loginapp': 0, 
					 'serviceapp': 0, 
					 'baseapp': 0, 
					 'cellapp': 0 }

		procs = TestCommon.getProcs()
		assert procs
		log.debug( "got procs: %s" % procs )

		for item in procs:
			if item in reqitems:
				reqitems[ item ] = reqitems[ item ] + 1

		return reqitems

	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""start 2 cellapps via control cluster"""
		loadOk = TestCommon.startProc( "cellapp", 2 )
		assert( loadOk )

	def step2( self ):
		"""count the apps"""
		reqitems = self._collectProcCounts()
		self.context['apps'] = reqitems

	def step3( self ):
		"""then run stopproc with pid of one cellapp"""
		pid = TestCommon.getPids( "cellapp", machine = TestCommon.getMachine() )[1]
		log.debug( "PID to stop: %r" % pid )
		assert pid
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
						w.stopProcess( config.CLUSTER_MACHINES[0], pid )

	def step4( self ):
		"""check returned code is 302 (Found)"""
		self.assertTrue( self.context['code'] == 302, 
						"expected code 302, got %r" % self.context['code'] )

	def step5( self ):
		"""and count the apps to have one less cellapp"""
		time.sleep( 1 )
		reqitems = self._collectProcCounts()
		log.debug( "Testing current count (%r) vs. previous count (%r)" % \
			( reqitems['cellapp'], self.context['apps']['cellapp'] ) )
		assert self.context['apps']['cellapp'] -1 == reqitems['cellapp']
		self.context['apps'] = reqitems

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 6: test retiring a process

class Scenario6( TestCase ):
	name = 'Test retiring a process'
	description = 'Will run retireApp command and check for 302 return code'
	tags = []


	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""start 2 cellapps via control cluster"""
		loadOk = TestCommon.startProc( "cellapp", 2 )
		#assert( loadOk )

	def step2( self ):
		"""then run retireApp with pid of one cellapp"""
		pid = TestCommon.getPids( "cellapp", machine = TestCommon.getMachine() )[1]
		log.debug( "PID to retire: %r" % pid )
		assert pid
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
						w.retireApp( config.CLUSTER_MACHINES[0], pid )

	def step3( self ):
		"""check returned code is 302 (Found)"""
		self.assertTrue( self.context['code'] == 302, 
						"expected code 302, got %r" % self.context['code'] )

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# scenario 7: test sending a SIG to a process

class Scenario7( TestCase ):
	name = 'Test sending a SIG to a process'
	description = 'Will run killproc command and check for return code 302'
	tags = []


	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""start 2 cellapps via control cluster"""
		loadOk = TestCommon.startProc( "cellapp", 2 )
		#assert( loadOk )

	def step2( self ):
		"""then run killproc with pid of one cellapp"""
		pid = TestCommon.getPids( "cellapp", 
								machine = TestCommon.getMachine() )[1]
		log.debug( "PID to send signal: %r" % pid )
		assert pid
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
						w.killProc( config.CLUSTER_MACHINES[0], pid, SIGINT )

	def step3( self ):
		"""check returned code is 302 (Found)"""
		self.assertTrue( self.context['code'] == 302, 
						"expected code 302, got %r" % self.context['code'] )

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# scenario 8: test running usersFlush

class Scenario8( TestCase ):
	name = 'Test running usersFlush'
	description = 'Will run usersFlush command and check for return code 302'
	tags = ["BWT-22626", "WIP"]#TODO: Re-enable this when BWT-22626 is fixed


	def step0( self ):
		""" Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run usersFlush"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.usersFlush()

	def step2( self ):
		"""check returned code is 302 (Found)"""
		self.assertTrue( self.context['code'] == 302, 
						"expected code 302, got %r" % self.context['code'] )
		
		time.sleep(5)
		startTime = time.time()
		
		while not TestCommon._getCC().machineExists( config.CLUSTER_MACHINES[0]):
			log.info("Waiting for %s to come back" % config.CLUSTER_MACHINES[0])
			time.sleep(5)
			if ( time.time() - startTime > 900 ):
				self.fail( "%s never came back after flushing mapping." 
						% config.CLUSTER_MACHINES[0] )
		

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# scenario 9: test running getProcs with a user and machine

class Scenario9( TestCase ):
	name = 'Test running getProcs with a user and machine'
	description = 'Will run getProcs command for a certain user and machine and check for required stuff'
	tags = []


	def _collectProcCountsJSON( self ):
		reqitems = { 'cellappmgr': 0, 
					 'baseappmgr': 0, 
					 'dbapp': 0, 
					 'loginapp': 0, 
					 'serviceapp': 0, 
					 'baseapp': 0, 
					 'cellapp': 0 }

		procs = self.context['json']['machine']['processes']
		assert procs
		log.debug( "Procs collected: %r" % procs )

		for item in procs:
			if item in reqitems:
				reqitems[ item ] = reqitems[ item ] + 1

		return reqitems

	def step0( self ):
		""" Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run getProcs with current user and bw02 machine"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
					w.getProcs( config.WCAPI_USER, config.CLUSTER_MACHINES[0] )
		log.debug( "getProcs returns: %s" % self.context['json'] )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check machine component exists and has required apps"""
		procCounts = self._collectProcCountsJSON()

		for item in procCounts:
			assert procCounts[item] > 0

	def step4( self ):
		"""then check layoutErrors and missingProcessTypes components do not exist"""
		assert 'layoutErrors' not in self.context['json']
		assert 'missingProcessTypes' not in self.context['json']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 10: test running getProcs with a user

class Scenario10( TestCase ):
	name = 'Test running getProcs with a user'
	description = 'Will run getProcs command for a certain user and check for OK code and that no "machine" component is returned'
	tags = []


	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run getProcs with current user and bw02 machine"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
								w.getProcs( user=config.WCAPI_USER )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check machine component does not exist"""
		assert 'machine' not in self.context['json']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# scenario 11: test running getMachines

class Scenario11( TestCase ):
	name = 'Test running getMachines with no parameters'
	description = 'Will run getMachines command with no parameters'\
				' and check for OK code and that "ms" component is present'
	tags = []


	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run getMachines with no parameters"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.getMachines()

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check 'ms' component exists"""
		assert 'ms' in self.context['json']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# scenario 12: test running getMachines with the tags argument

class Scenario12( TestCase ):
	name = 'Test running getMachines with tags=True'
	description = 'Will run getMachines command with tags=True '\
				'and check for OK code and that "ms" component is returned'
	tags = []

	

	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run getMachines with tags=True"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
						w.getMachines( includeTagInfo=True )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check 'ms' component exists"""
		assert 'ms' in self.context['json']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# scenario 13: test running getUsers with and w/o inactive parameter

class Scenario13( TestCase ):
	name = 'Test running getUsers with and w/o "inactive" parameter'
	description = 'Will run getUsers command and check for OK code'\
				' and that "users" component is returned'
	tags = []



	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run getUsers without 'inactive' parameter"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.getUsers()

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check 'users' component exists"""
		assert 'users' in self.context['json']
		self.context['lastusercount'] = len(self.context['json']['users'])

	def step4( self ):
		"""Then run getUsers with 'inactive'=True"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = \
							w.getUsers( includeInactive=True )

	def step5( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step6( self ):
		"""and check 'users' component exists"""
		assert 'users' in self.context['json']
		self.context['usercount'] = len(self.context['json']['users'])

	def step7( self ):
		"""and check 'users' count is >= prev. time reported"""
		assert self.context['usercount'] >= self.context['lastusercount']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# scenario 14: test running coredumps

class Scenario14( TestCase ):
	name = 'Test running coredumps'
	description = 'Will run coredumps command and check for OK code'\
				' and that "coredumps" component is returned'
	tags = []


	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run coredumps"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.coredumps( config.WCAPI_USER )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check 'coredumps' component exists"""
		assert 'coredumps' in self.context['json']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

# @SCENARIO scenario 15: test running layouts

class Scenario15( TestCase ):
	name = 'Test running layouts'
	description = 'Will run layouts command and check for OK code'\
				' and that required components are returned'
	tags = []


	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run coredumps"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.layouts( )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""and check 'pnames' and 'layouts' components exist"""
		assert 'pnames' in self.context['json']
		assert 'layouts' in self.context['json']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

