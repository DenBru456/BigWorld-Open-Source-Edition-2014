import bwtest
from helpers.cluster import ClusterController
import time


#gCmd = helpers.Command( [
#	"mysql -h{dbhost} -u{dbuser} -p{dbpassword} -D{dbname} "
#		"-e'drop table if exists tbl_TestEntity, tbl_TestEntity_array, "
#		"tbl_TestEntity_cellArray, tbl_TestEntity_nestedArray, "
#		"tbl_TestEntity_nestedArraySingle_inner, "
#		"tbl_TestEntity_nestedArray_inner, tbl_TestEntity_tuple, "
#		"tbl_Simple, "
#		"bigworldLogOns;'",
#	"-BW_RES_PATH={bwrespath} {bwroot}/bigworld/%s/commands/consolidate_dbs --clear"\
#	 % bwtest.config.SERVER_BINARY_FOLDER,
#	"BW_RES_PATH={bwrespath} {bwroot}/bigworld/%s/commands/sync_db"\
#	 % bwtest.config.SERVER_BINARY_FOLDER
#	] )

class TestPersistent( bwtest.TestCase ):
	name = "Persistent cell data" 
	description = "Persistent cell data is written to the database"
	tags = []


	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.start()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def runTest( self ):
		def loadSnippets():
			self._cc.loadSnippetModule( "baseapp", 1,
				"db/python_api/behaviour/base/behaviour" )
			self._cc.loadSnippetModule( "cellapp", 1,
				"db/python_api/behaviour/cell/behaviour" )

		loadSnippets()
		spaceID = self._cc.callOnApp( "cellapp", 1, "snippetWaitForSpace" )

		entityID = self._cc.callOnApp( "baseapp", 1, "snippetPersistent_1",
							spaceID = spaceID )
		self._cc.callOnApp( "cellapp", 1, "snippetPersistent_2", 
							entityID = entityID )

		dbID = self._cc.callOnApp( "baseapp", 1, "snippetPersistent_3",
							entityID = entityID )

		self._cc.stop()
		self._cc.start()
		loadSnippets()

		spaceID = self._cc.callOnApp( "cellapp", 1, "snippetWaitForSpace" )
		entityID = self._cc.callOnApp( "baseapp", 1, "snippetPersistent_4",
							spaceID = spaceID, databaseID = dbID )		
		self._cc.callOnApp( "cellapp", 1, "snippetPersistent_5",
							entityID = entityID )



class TestBackup( bwtest.TestCase ):
	name = "Entity Backup" 
	description = "Entity backup is updated when writeToDB() is called."
	tags = []


	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )

		self._cc.start()
		self._cc.startProc( "baseapp" )


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def runTest( self ):
		self._cc.loadSnippetModule( "baseapp", 1,
				"db/python_api/behaviour/base/behaviour" )
		self._cc.loadSnippetModule( "baseapp", 2,
				"db/python_api/behaviour/base/behaviour" )

		backupPeriod = float( self._cc.getConfig( "baseApp/backupPeriod" ) )

		time.sleep( backupPeriod + 1 )

		entityID = self._cc.callOnApp( "baseapp", 2, "snippetBackup_1" )
		self._cc.killProc( "baseapp", 2 )

		time.sleep( 3 )
		self._cc.callOnApp( "baseapp", 1, 
						"snippetBackup_2", entityID = entityID )



class TestBackupFromCell( bwtest.TestCase ):
	name = "Entity Backup From Cell" 
	description = """Entity backup is updated when writeToDB() 
is called on the cell."""

	tags = []


	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.start()
		self._cc.startProc( "baseapp" )


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def runTest( self ):
		self._cc.loadSnippetModule( "baseapp", 1,
				"db/python_api/behaviour/base/behaviour" )
		self._cc.loadSnippetModule( "baseapp", 2,
				"db/python_api/behaviour/base/behaviour" )
		self._cc.loadSnippetModule( "cellapp", 1,
				"db/python_api/behaviour/cell/behaviour" )

		spaceID = self._cc.callOnApp( "cellapp", 1, "snippetWaitForSpace" )

		backupPeriod = float( self._cc.getConfig( "baseApp/backupPeriod" ) )

		time.sleep( backupPeriod + 1 )

		entityID = self._cc.callOnApp( "baseapp", 2, "snippetBackupFromCell_1",
										spaceID = spaceID )
		self._cc.callOnApp( "cellapp", 1, 
						"snippetBackupFromCell_2", entityID = entityID )
		self._cc.killProc( "baseapp", 2 )

		self._cc.callOnApp( "baseapp", 1, 
						"snippetBackupFromCell_3", entityID = entityID )


class TestBackupBaseOnly( bwtest.TestCase ):
	name = "Writing base-only entity" 
	description = "Entity backup doesn't fail on a base-only entity"

	tags = []


	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.start()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def runTest( self ):
		self._cc.loadSnippetModule( "baseapp", 1,
				"db/python_api/behaviour/base/behaviour" )

		self._cc.callOnApp( "baseapp", 1, "snippetBackupBaseOnly_1" )


class TestBackupNoCellEntity( bwtest.TestCase ):
	name = "Backing up with no cell entity" 
	description = """
Writing an entity with cell data but currently without a cell entity
	"""

	tags = []


	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.start()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def runTest( self ):
		def loadSnippets():
			self._cc.loadSnippetModule( "baseapp", 1,
				"db/python_api/behaviour/base/behaviour" )
			self._cc.loadSnippetModule( "cellapp", 1,
				"db/python_api/behaviour/cell/behaviour" )

		loadSnippets()
		spaceID = self._cc.callOnApp( "cellapp", 1, "snippetWaitForSpace" )


		entityID = self._cc.callOnApp( "baseapp", 1, 
						"snippetBackupNoCellEntity_1",
						spaceID = spaceID )
		self._cc.callOnApp( "cellapp", 1, "snippetBackupNoCellEntity_2", 
							entityID = entityID )

		backupPeriod = float( self._cc.getConfig( "baseApp/backupPeriod" ) )

		time.sleep( backupPeriod + 1 )

		snippet = """
e = BigWorld.entities[ {entityID} ]
e.destroyCellEntity()
srvtest.finish()
"""
		self._cc.sendAndCallOnApp( "baseapp", 1, snippet, entityID = entityID )
		time.sleep( 5 )
		dbID = self._cc.callOnApp( "baseapp", 1, "snippetBackupNoCellEntity_3",
							entityID = entityID )

		self._cc.stop()
		self._cc.start()
		loadSnippets()

		spaceID = self._cc.callOnApp( "cellapp", 1, "snippetWaitForSpace" )
		entityID = self._cc.callOnApp( "baseapp", 1, 
						"snippetBackupNoCellEntity_4",
						databaseID = dbID, spaceID = spaceID )		
		self._cc.callOnApp( "cellapp", 1, "snippetBackupNoCellEntity_5",
							entityID = entityID )
