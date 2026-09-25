import os
from xml.dom.minidom import parse
from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class SaveTest( TestCase ):
	
	name = "Control Cluster Save"
	description = "Tests control_cluster.py save command"
	tags = []
	
	basicProcesses = ["cellappmgr", "baseappmgr", "dbapp", 
					"baseapp", "loginapp", "cellapp", "serviceapp"]
	advancedProcesses = [("cellappmgr",[(0, 1)]), 
						("baseappmgr",[(0, 1)]), 
						("dbapp",[(0, 1)]), 
						("baseapp",[(0, 2)]), 
						("loginapp" ,[(0, 1)]), 
						("cellapp", [(0, 2), (1, 1)]), 
						("serviceapp", [(0, 1)]),
						("bots", [(1, 2)]),]
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		path = self.cc._tempTree + "/layout1"
		run_cc_command( "save", [path] )
		self.assertTrue( os.path.exists( path ))
		dom = parse( path )
		for process in self.basicProcesses:
			procElements = dom.getElementsByTagName( process )
			self.assertTrue( len( procElements ) == 1,
							"Too many elements of %s" % process)
			machineElements = procElements[0].getElementsByTagName( "machine" )
			self.assertTrue( len( machineElements ) == 1,
							"Wrong amount of machine elements for %s" % process)
			machineName = machineElements[0].getAttribute( "name" )
			self.assertTrue( machineName == config.CLUSTER_MACHINES[0],
							"Machine for %s is on wrong host" % process )
		
		self.cc.startProc( "baseapp", 1 )
		self.cc.startProc( "cellapp", 1 )
		self.cc.startProc( "cellapp", 1, machineIdx=1 )
		self.cc.startProc( "bots", 2, machineIdx=1 )
		path = self.cc._tempTree + "/layout2"
		run_cc_command( "save", [path] )
		self.assertTrue( os.path.exists( path ))
		dom = parse( path )
		for process, machines in self.advancedProcesses:
			procElements = dom.getElementsByTagName( process )
			self.assertTrue( len( procElements ) == 1,
							"Too many elements of %s" % process)
			machineElements = procElements[0].getElementsByTagName( "machine" )
			self.assertTrue( len( machineElements ) == len( machines ),
							"Wrong amount of machine elements for %s" % process)
			for machineID, machineCount in machines:
				machine = config.CLUSTER_MACHINES[machineID]
				foundMachines = False
				for element in machineElements:
					if element.getAttribute( "name" ) == machine:
						if machineCount == 1 and not element.hasAttribute( "count" ):
							foundMachines = True
						elif element.hasAttribute( "count" ) and \
							int( element.getAttribute( "count" ) ) == machineCount:
							foundMachines = True
				self.assertTrue( foundMachines,
								"Layout had incorrect count for %s on %s" \
								% (process, machine ))