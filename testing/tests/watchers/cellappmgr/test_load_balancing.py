from bwtest import TestCase
from tests.watchers.test_common import TestCommon

class TestLoadBalancingWatchers( TestCommon, TestCase ):
	
	
	name = "Load balancing watchers"
	description = "Tests the functionality of cellappmgr load balancing  watchers"
	tags = []
	
	
	def runTest( self ):
		cellAppGroups = self._cc.getWatcherValue("loadBalancing/cellAppGroups", 
												"cellappmgr", None)
		self.assertTrue( cellAppGroups == "[]",
						"cellAppGroups watcher unexpected value")
		
		cellsPerMultiCellSpaceAvg = self._cc.getWatcherValue(
									"loadBalancing/cellsPerMultiCellSpaceAvg", 
									"cellappmgr", None)
		self.assertTrue( float(cellsPerMultiCellSpaceAvg) == 0.0,
						"cellsPerMultiCellSpaceAvg watcher unexpected value")
		
		cellsPerSpaceMax = self._cc.getWatcherValue(
									"loadBalancing/cellsPerSpaceMax", 
									"cellappmgr", None)
		self.assertTrue( int(cellsPerSpaceMax) == 1,
						"cellsPerSpaceMax watcher unexpected value")
		
		machinesPerMultiCellSpaceAvg = self._cc.getWatcherValue(
									"loadBalancing/machinesPerMultiCellSpaceAvg", 
									"cellappmgr", None)
		self.assertTrue( float(machinesPerMultiCellSpaceAvg) == 0.0,
						"machinesPerMultiCellSpaceAvg watcher unexpected value")
		
		machinesPerMultiCellSpaceMax = self._cc.getWatcherValue(
									"loadBalancing/machinesPerMultiCellSpaceMax", 
									"cellappmgr", None)
		self.assertTrue( int(machinesPerMultiCellSpaceMax) == 1,
						"machinesPerMultiCellSpaceMax watcher unexpected value")
		
		numCells = self._cc.getWatcherValue("loadBalancing/numCells", 
												"cellappmgr", None)
		self.assertTrue( int(numCells) == 1,
						"numCells watcher unexpected value")
		
		numMachinePartitions = self._cc.getWatcherValue("loadBalancing/numMachinePartitions", 
												"cellappmgr", None)
		self.assertTrue( int(numMachinePartitions) == 0,
						"numMachinePartitions watcher unexpected value")
		
		numMultiCellSpaces = self._cc.getWatcherValue("loadBalancing/numMultiCellSpaces", 
												"cellappmgr", None)
		self.assertTrue( int(numMultiCellSpaces) == 0,
						"numMultiCellSpaces watcher unexpected value")
		
		numMultiMachineSpaces = self._cc.getWatcherValue("loadBalancing/numMultiMachineSpaces", 
												"cellappmgr", None)
		self.assertTrue( int(numMultiMachineSpaces) == 0,
						"numMultiMachineSpaces watcher unexpected value")
		
		numPartitions = self._cc.getWatcherValue("loadBalancing/numPartitions", 
												"cellappmgr", None)
		self.assertTrue( int(numPartitions) == 0,
						"numPartitions watcher unexpected value")
		
		numSpaces = self._cc.getWatcherValue("loadBalancing/numSpaces", 
												"cellappmgr", None)
		self.assertTrue( int(numSpaces) == 1,
						"numSpaces watcher unexpected value")