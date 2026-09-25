from bwtest import TestCase, config
from helpers.cluster import ClusterController


class MemberWatchersTest( TestCase ):
	
	name = "MemberWatcher"
	description = "Tests the functionality of member watchers"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		components = self.cc.getWatcherData( 
									"components", "message_logger", None )
		for comp in components.getChildren():
			name = comp.getChild( "name" ).value
			self.assertTrue( name in ["BaseAppMgr", "CellAppMgr", "DBAppMgr", 
									"DBApp", "BaseApp", "CellApp", 
									"ServiceApp", "LoginApp"],
					"message_logger watcher returned strange name: %s" % name )
			uid = comp.getChild( "uid" ).value
			self.assertTrue( int( uid ) == config.CLUSTER_UID,
					"message_logger watcher returned strange uid: %s" % uid )