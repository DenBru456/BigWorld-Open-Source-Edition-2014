from bwtest import TestCase
from tests.watchers.test_common import TestCommon

import time

class TestSpacesWatchers( TestCommon, TestCase ):
	
	
	name = "Spaces watchers"
	description = "Tests the functionality of cellappmgr spaces watcher"
	tags = []
	
	
	def runTest( self ):
		time.sleep( 10 )
		shouldLb = self._cc.getWatcherData( "debugging/shouldLoadBalance", 
										"cellappmgr", None)
		shouldMetaLb = self._cc.getWatcherData( "debugging/shouldMetaLoadBalance", 
										"cellappmgr", None)
		shouldLb.set( False )
		shouldMetaLb.set( False )
		
		bsp = self._cc.getWatcherData( "spaces/2/bsp", "cellappmgr", None)
		areaNotLoaded = int( bsp.getChild( "areaNotLoaded" ).value )
		self.assertTrue( areaNotLoaded == 0,
						"Unexpected areaNotLoaded value")
		chunkBounds = bsp.getChild( "chunkBounds" ).value
		rangeVal = bsp.getChild( "range" ).value
		self.assertTrue( chunkBounds == rangeVal,
						"chunkBounds or range watcher had unexpected value" )
		isRetiring = bsp.getChild( "isRetiring" )
		self.assertTrue( isRetiring.value == False,
						"bsp was retiring on startup" )
		isLeaf = bsp.getChild( "isLeaf" )
		self.assertTrue( isLeaf.value == True,
						"bsp was split on new startup" )
		left = bsp.getChild( "left" )
		right = bsp.getChild( "right" )
		self.assertTrue( left.value is None, "leaf has a left" )
		self.assertTrue( right.value is None, "leaf has a right" )
		isLeaf.set( False )
		left = bsp.getChild( "left" )
		right = bsp.getChild( "right" )
		self.assertTrue( left.isDir(), 
						"not leaf doesn't have a left" )
		self.assertTrue( right.isDir(), 
						"not leaf doesn't have a right" )
		isRetiring = left.getChild( "isRetiring" )
		isRetiring.set( True )
		numRetiring = int( left.getChild( "numRetiring").value )
		
		self.assertTrue( numRetiring == 1,
						"numRetiring not updated correctly")
