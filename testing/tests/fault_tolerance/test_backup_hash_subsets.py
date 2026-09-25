import bwtest
from helpers.cluster import ClusterController

class BackupHashSubsets( bwtest.TestCase ):
	name = "backupHashSubsets"
	description = "Test backup hash sets for ServiceApps and BaseApps"
	tags = []

	BACKUP_PERIOD = 5
	NUM_BASEAPPS = 7
	NUM_SERVICEAPPS = 5

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "baseApp/backupPeriod", str( self.BACKUP_PERIOD ) )

		self.cc.start()
		self.cc.startProc( "baseapp", self.NUM_BASEAPPS - 1 )
		self.cc.startProc( "serviceapp", self.NUM_SERVICEAPPS - 1 )
		self.serviceApps = []
		self.baseApps = []

		for procOrd in range( 1, self.NUM_BASEAPPS + 1 ):
			self.baseApps.append(
				self.cc.getWatcherValue( "nub/address", "baseapp", procOrd ) )

		for procOrd in range( 1, self.NUM_SERVICEAPPS + 1 ):
			self.serviceApps.append(
				self.cc.getWatcherValue( "nub/address", "serviceapp", procOrd ) )

	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

	def runTest( self ):
		for procOrd in range( 1, self.NUM_BASEAPPS + 1 ):
			apps = self.cc.getWatcherData( "backedUpBaseApps/apps",
										"baseapp", procOrd ).getChildren()
			for app in apps:
				self.assertIn( app.name, self.baseApps,
							"Backups for a BaseApp should also be a BaseApp" )

		for procOrd in range( 1, self.NUM_SERVICEAPPS + 1 ):
			apps = self.cc.getWatcherData( "backedUpBaseApps/apps",
										"serviceapp", procOrd ).getChildren()
			for app in apps:
				self.assertIn( app.name, self.serviceApps,
							"Backups for a ServiceApp should also be a ServiceApp" )
