from bwtest import TestCase
from tests.watchers.test_common import TestCommon
from primitives import locallog

import time


class TestShouldShowMetaLoadBalanceDebug( TestCommon, TestCase):
	
	
	tags = []
	name = "ShouldShowMetaLoadBalanceDebug"
	description = "Tests config shouldShowMetaLoadBalanceDebug config\
	 and checks for expected log output"
		

	def runTest( self ):
		self._cc.startProc( "cellapp", 8 )
		spaces =  self._cc.getWatcherData( 
							"spaces", "cellappmgr", None ).getChildren()
		isLeaf = spaces[0].getChild( "bsp" ).getChild( "isLeaf" )
		isLeaf.set( "False" )
		time.sleep( 10 )
		output = locallog.grepLastServerLog( 
					"CellAppScorer::compareCellApps( CellCellTrafficScorer )", 
					15, "CellAppMgr" )
		self.assertTrue( len( output ) == 0, 
				"Load balancing debug output appears when watcher set to False")
		conf = self._cc.getWatcherData( 
					"config/shouldShowMetaLoadBalanceDebug", "cellappmgr", None)
		conf.set( "True" )
		
		isLeaf.set( "True" )
		time.sleep( 2 )
		isLeaf.set( "False" )
		time.sleep( 10 )
		output = locallog.grepLastServerLog( 
							"CellAppScorer::compareCellApps", 15, "CellAppMgr" )
		self.assertTrue( len( output ) > 0, 
				"Load balancing debug output doesn't appear"\
				" when watcher set to True")
		
		
		