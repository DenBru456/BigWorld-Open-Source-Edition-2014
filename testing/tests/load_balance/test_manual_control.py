import time
from bwtest import TestCase
from helpers.cluster import ClusterController
from helpers.timer import runTimer


class TestManualControl( TestCase ):
	
	name = "Manual Control of Load Balancing"
	description = "Tests the ability to manually control load balancing "\
				"using the spaces/*/cells and spaces/*bsp watchers "\
				"on cellappmgr"
	
	NUM_ENTITIES = 50
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "balance/demo/enable", "true" )
		self.cc.setConfig( "balance/demo/numEntitiesPerCell", 
							str( self.NUM_ENTITIES * 2 ) )
	
	
	def tearDown( self ):
		if hasattr(self, "cc"):
			self.cc.stop()
			self.cc.clean()
	

	def findLeafCells( self, root ):
		cells = []
		left = root.getChild( "left")
		if left.value:
			cells.extend( self.findLeafCells( left ) )
		right = root.getChild( "right" )
		if right.value:
			cells.extend( self.findLeafCells( right ) )
		isLeaf = root.getChild( "isLeaf" )
		if isLeaf.value:
			cells.append( root )
		return cells
		

	def checkCellsHaveEntities( self, cells ):
		ret = True
		for cell in cells:
			numEntities = cell.getChild( "app" ).getChild( "numEntities" ).value
			if int( numEntities ) == 0:
				ret = False
		return ret
				
	def checkCellEntityCounts( self, cells, oldCounts ):
		ret = True
		for i, cell in enumerate( cells ):
			numEntities = cell.getChild( "app" ).getChild( "numEntities" ).value
			if int( numEntities) != oldCounts[i]:
				ret = False
		return ret


	def runTest( self ):
		#First, test that you can't split cells with no avaialble cellapps
		self.cc.start()
		self.cc.setWatcher( "spaces/2/cells/0/isLeaf", "False",  
						"cellappmgr", None )
		isLeaf = lambda: self.cc.getWatcherValue( "spaces/2/cells/0/isLeaf", 
										"cellappmgr", None)
		runTimer( isLeaf, timeout = 5 )
		
		#Create some entities
		self.cc.startProc( "cellapp", 6 )
		snippet = """
		for i in range( %s ):
			pos = (190 - 35*(i%%12), 0, 190 - 35*(i%%12))
			dir = (0,0,0)
			BigWorld.createEntity( "TestEntity", 2, pos, dir)
		srvtest.finish()
		""" % self.NUM_ENTITIES
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet)
		
		#Wait for load balancing to split the space
		bspRoot = self.cc.getWatcherData( "spaces/2/bsp", "cellappmgr", None )
		runTimer( lambda: self.findLeafCells( bspRoot ),
				checker = lambda res: len(res) == 5, timeout = 30 )
		
		cells = self.findLeafCells( bspRoot )
		runTimer( lambda: self.checkCellsHaveEntities( cells ), timeout = 10 )
		
		
		#Manually split a cell 
		cells[0].getChild( "isLeaf" ).set( "False" )
		runTimer( lambda: self.findLeafCells( bspRoot ),
				checker = lambda res: len(res) == 6, timeout = 20 )
		cells = self.findLeafCells( bspRoot )
		runTimer( lambda: self.checkCellsHaveEntities( cells ), timeout = 10 )
		
		#Manually retire a cell
		cells[0].getChild( "isRetiring" ).set( "True" )
		runTimer( lambda: self.findLeafCells( bspRoot ),
				checker = lambda res: len(res) == 5, timeout = 20 )
		cells = self.findLeafCells( bspRoot )
		runTimer( lambda: self.checkCellsHaveEntities( cells ), timeout = 10 )
		
		#Quickly start retiring and cancel, check that the cell keeps its
		#entities
		cells[0].getChild( "isRetiring" ).set( "True" )
		cells[0].getChild( "isRetiring" ).set( "False" )
		time.sleep( 5 )
		numEntities = cells[0].getChild( "app" ).getChild( "numEntities" ).value
		self.assertTrue( int( numEntities ) != 0, 
					"Entities were offloaded even when retiring was cancelled" )
		cells = self.findLeafCells( bspRoot )
		self.assertTrue( len(cells) == 5, 
						"Cell was retired even though retiring was cancelled")
		
		#Verify that setting isRetiring to False doesn't retire the cell
		cells[0].getChild( "isRetiring" ).set( "False" )
		time.sleep( 5 )
		numEntities = cells[0].getChild( "app" ).getChild( "numEntities" ).value
		self.assertTrue( int( numEntities ) != 0, 
					"Entities were offloaded when isRetiring was set to False" )
		cells = self.findLeafCells( bspRoot )
		self.assertTrue( len(cells) == 5, 
					"Cell was retired even though isRetiring was set to false")
		
		#Turn off load balancing
		self.cc.setWatcher( "debugging/shouldLoadBalance", "False", 
							"cellappmgr", None )
		self.cc.setWatcher( "debugging/shouldMetaLoadBalance", "False", 
							"cellappmgr", None )
		#Split a cell and verify that the split happens but cells 
		# don't get offloaded
		cells[0].getChild( "isLeaf" ).set( "False" )
		runTimer( lambda: self.findLeafCells( bspRoot ),
				checker = lambda res: len(res) == 6, timeout = 20 )
		cells = self.findLeafCells( bspRoot )
		time.sleep( 5 )
		self.assertFalse( self.checkCellsHaveEntities( cells ), 
						"Newly split cell received entities when it shouldn't" )

		#Move a separator and verify that entities get offloaded
		cellEntityCounts = []
		for cell in cells:
			numEntities = cell.getChild( "app" ).getChild( "numEntities" ).value
			cellEntityCounts.append( int( numEntities ) )
		oldPosition = int( bspRoot.getChild( "position" ).value )
		bspRoot.getChild( "position" ).set( str( oldPosition + 100 ) )
		runTimer( lambda: self.checkCellEntityCounts( cells, cellEntityCounts ), 
				checker = lambda res: res == False, timeout = 5 )
		
		#Turn load balancing back on, check that entities get moved again 
		#and all cells get some entities
		cellEntityCounts = []
		for cell in cells:
			numEntities = cell.getChild( "app" ).getChild( "numEntities" ).value
			cellEntityCounts.append( int( numEntities ) )
		self.cc.setWatcher( "debugging/shouldLoadBalance", "True", 
							"cellappmgr", None )
		self.cc.setWatcher( "debugging/shouldMetaLoadBalance", "True", 
							"cellappmgr", None )
		runTimer( lambda: self.checkCellEntityCounts( cells, cellEntityCounts ), 
				checker = lambda res: res == False, timeout = 5 )
		cells = self.findLeafCells( bspRoot )
		runTimer( lambda: self.checkCellsHaveEntities( cells ), timeout = 10 )