import test_base
from bwtest import TestCase, config
from helpers.cluster import ClusterControllerError
from primitives import locallog
import time


class StartUpConsolidation( test_base.TestBase, TestCase ):
	
	tags = []
	name = "Start-up consolidation"
	description = "During startup, database consolidation is run\
	 if it wasn't run during shutdown"

	
	def runTest( self ):
		self._cc.start()
		self.populateDB()
		time.sleep( self.ARCHIVE_PERIOD )
		self._cc.killProc( "dbapp" )
		self._cc.stop()
		self._cc.start()
		self.assertTrue( self.checkServerLogs(), 
						"Database consolidation was not run on second startup" )
		self._cc.stop()

		
class NoDeleteOnFailure( test_base.TestBase, TestCase ):
	
	tags = []
	name = "No delete on failure"
	description = "Secondary database files are not deleted\
	 if the data consolidation process failed"
	
	def runTest( self ):
		self._cc.start()
		self.populateDB()
		time.sleep( self.ARCHIVE_PERIOD )
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) > 0, 
						"Secondary database files are not present when running" )
		self.removeTransferDb()
		self._cc.stop()
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) > 0, 
		"Secondary database files are not present after consolidation failed" )
		

class NetworkSecondaryDb( test_base.TestBase, TestCase ):
	
	
	tags = ["MANUAL"]
	name = "Secondary DB can not run network share"
	description = "If the .DB file is to be written to a network share, \
		an error should be displayed in the server logs\
		and the BaseApp should fail to start"
		
	
	def runTest( self ):
		self._parseUserConfig()
		self._cc.setConfig( "db/secondaryDB/directory", config.WINDOWS_MOUNT )
		try:
			self._cc.start() #This should fail
		except ClusterControllerError:
			pass
		else:
			self.assertTrue( False, 
				"Server started with secondary DBs on network share" )
		output = locallog.grepLastServerLog( "database is located on a CIFS or SMB file system" )
		self.assertTrue( len( output ) > 0, "Expected log output not found" )

