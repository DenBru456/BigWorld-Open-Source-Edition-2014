import os, time
from bwtest import TestCase, config
from helpers.cluster import ClusterController
from helpers.timer import runTimer
from helpers.command import Command

class RestartBwmachined( TestCase ):
	
	
	name = "RestartBwmachined"
	tags = ["PRIORITY0"]
	description = "This test isn't really a test, but restarts bwmachined on"\
				  " all machines defined to ensure that the other tests "\
				  "are run against a correct version of bwmachined"
	
	
	def setUp( self ):
		self.bwmachined_path = os.path.join( config.CLUSTER_BW_ROOT, 
											  config.BIGWORLD_FOLDER,
											  config.TOOLS_BINARY_FOLDER,
											  "bwmachined2" )
		self.config = os.path.join( os.path.dirname( os.path.abspath( __file__ )),
									"bwmachined.conf" )
		self.cc = ClusterController( "simple_space/res" )

	
	def tearDown( self ):
		pass
	
	
	def runTest( self ):
		machines = config.CLUSTER_MACHINES
		if config.CLUSTER_MACHINES_LOAD:
			machines += config.CLUSTER_MACHINES_LOAD
		for machine in machines:
			#First kill any previously running bwmachined processes
			cmd = Command()
			cmd.call( 'ssh root@%s "ps ax|grep bwmachined2"' % machine )
			output = cmd.getLastOutput()[0]
			for line in output.split( "\n" ):
				if "grep" in line:
					continue
				pid = line.split()
				if pid == []:
					continue
				pid = int(pid[0])
				cmd.call( 'ssh root@%s "kill %s"' % ( machine, pid) )
		
			#Now start a new one
			cmd.call( 'ssh root@%s "echo core.%%e.%%h.%%p > /proc/sys/kernel/core_pattern"'
						% machine )
			cmd.call( 'ssh root@%s "cp %s /etc/"' % ( machine, self.config ) )
			cmd.call( 'ssh root@%s "/bin/bash -c %s"' % (machine, self.bwmachined_path),
						waitForCompletion  = False, parallel = True )
			time.sleep( 5 )
		for machine in machines:
			#Then wait for it to be registered in the cluster
			runTimer( lambda: self.cc.machineExists(machine),
							timeout = 3600, period = 20 )