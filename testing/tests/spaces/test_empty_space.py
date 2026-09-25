import bwtest
from helpers.cluster import ClusterController
import time


class TestEmptySpace( bwtest.TestCase ):
	name = "Auto deletion Space"
	description = "Test automatic deletion of an empty space"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )

		self.cc.start()
		self.cc.loadSnippetModule( "baseapp", 1, "spaces/test_empty_space" )
		self.cc.loadSnippetModule( "cellapp", 1, "spaces/test_empty_space" )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		ret = self.cc.waitForWatcherValue( "numSpaces", "1", "cellapp")
		self.assertTrue( ret, "Original space not created")
			
		numSpaces1 = int( self.cc.getWatcherValue( "numSpaces", "cellapp" ) )

		spaceId = self.cc.callOnApp( "baseapp", 1, "createEntityInNewSpace" )
		numSpaces2 = int( self.cc.getWatcherValue( "numSpaces", "cellapp" ) )

		# Number of spaces should increase by 1
		self.assertTrue( numSpaces2 == (numSpaces1 + 1), "New space not created" )

		self.cc.callOnApp( "baseapp", 1, "destroyEntityInNewSpace", id = spaceId )

		# Give CellApp a chance to be ticked
		time.sleep( 1 )
		numSpaces3 = int( self.cc.getWatcherValue( "numSpaces", "cellapp" ) )

		# Number of spaces should decrease by 1
		self.assertTrue( numSpaces3 == (numSpaces2 - 1),
				"Empty space not destroyed" )
