from bwtest import TestCase, config
from helpers.cluster import ClusterController
from helpers.timer import runTimer, TimerError
from helpers.command import Command
import time, re

class PythonMethodMemoryLeaks( TestCase ):
	
	
	description = "Tests various Python API methods and ensures that calling "\
				"them does not leak memory"
	def setUp( self ):
		self.cc = ClusterController( ["simple_space_with_services/res",
									"simple_space/res" ] )
		self.cc.setConfig( "allowInteractiveDebugging", "True" )
		self.cc.setConfig( "billingSystem/shouldAcceptUnknownUsers", "True" )
		self.cc.setConfig( "billingSystem/shouldRememberUnknownUsers", "True" )
		self.cc.start()


	def tearDown( self ):
		if hasattr( self, "cc" ):
			self.cc.stop()
			self.cc.clean()


	def getProcessMemory( self, process ):
		pid = self.cc.findProc( process, None ).pid
		cmd = Command()
		cmd.call( "top -p%s -bn1" % pid )
		output = cmd.getLastOutput()[0]
		pattern = "%s\s+%s\s+\d+\s+\d+\s+\d+[a-z]\s+(\d+[a-z])\s+" % \
											(pid, config.CLUSTER_USERNAME)
		m = re.search( pattern, output )
		if m:
			ret = m.group(1)
			return ret
		self.fail( "top command had incorrect output" )
		  

	
	def checkMemoryLeak( self, command, process, calls, repeat ):
		#First call the command once, make sure it returns something.
		#also, ensures all imports are loaded and other appropriate memory usage
		snippet = """
		s = %s
		#srvtest.assertTrue( s not in [None, False, []] )
		srvtest.finish()
		""" % command
		self.cc.sendAndCallOnApp( process, None, snippet )
		global oldMem
		oldMem = self.getProcessMemory( process )
		#Wait for memory use to be stable
		def checkStable():
			global oldMem
			ret = False
			newMem = self.getProcessMemory( process )
			if newMem == oldMem:
				ret = True
			oldMem = newMem
			
			return ret
		runTimer( checkStable, timeout = 30, period = 3 )
		startMem = self.getProcessMemory( process )
		leaksFound = 0
		#Now call command specified times and ensure no memory leaks
		for i in range( 1, repeat):
			oldMem = self.getProcessMemory( process )
			snippet = """
			for i in range( %s ):
				s = %s
			srvtest.finish()
			""" % ( calls, command )
			self.cc.sendAndCallOnApp( process, None, snippet )
			try:
				runTimer( lambda: self.getProcessMemory( process ),
					checker = lambda ret: ret == oldMem, timeout = 10)
			except TimerError:
				leaksFound += 1
		finalMem = self.getProcessMemory( process )
		self.assertTrue( leaksFound < repeat/2, 
					"Found leaks on more than half of attempts when calling %s."\
					" Overall memory went from %s to %s" \
					 % ( command, startMem, finalMem ) )
		
		
	def runTest(self ):
		self.checkMemoryLeak( "BigWorld.services.items()", 
							"baseapp", 50000, 10 )
		self.checkMemoryLeak( "BigWorld.getSpaceGeometryMappings(2)", 
							"cellapp", 50000, 10 )
		self.checkMemoryLeak( "BigWorld.authenticateAccount( 'user', 'pass')", 
							"baseapp", 1500, 20 )
		
		
		#Test BigWorld.getStopPoint method
		self.cc.startProc( "bots" )
		self.cc.bots.add( 1 )
		for position in [0, 1, 5, 20, 50]:
			snippet = """
			import Math
			BigWorld.bots.values()[0].stop()
			BigWorld.bots.values()[0].snapTo( Math.Vector3( %s, %s, %s ) )
			srvtest.finish()
			""" % ( position, position, position )
			self.cc.sendAndCallOnApp( "bots", None, snippet )
		
			self.checkMemoryLeak( """BigWorld.entities["Avatar"].getStopPoint( 
								BigWorld.entities["Avatar"].position, False)""", 
							"cellapp", 25000, 10 )
		
		#Test BigWorld.lookUpBaseByDBID
		snippet = """
		e = BigWorld.createEntity( "Simple" )
		def dbCallBack(*args):
			srvtest.finish(e.databaseID)
		e.writeToDB( dbCallBack, True)
		"""
		dbID = self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		self.checkMemoryLeak( 
			"BigWorld.lookUpBaseByDBID( 'Simple', %s, lambda ret: True )" % dbID, 
			"baseapp", 500, 20 )
		
		self.checkMemoryLeak( "BigWorld.collide( 2, (0, 10, 0), (0,-10,0) )", 
							"cellapp", 50000, 10)
		self.checkMemoryLeak( "BigWorld.findChunkFromPoint( (0, 10, 0), 2 )", 
							"cellapp", 50000, 10)
		for proc in ["baseapp", "cellapp"]:
			self.checkMemoryLeak( "BigWorld.getWatcher( 'nub/address' )", 
								proc, 50000, 10 )
