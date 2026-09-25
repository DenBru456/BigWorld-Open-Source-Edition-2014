import bwtest
from helpers.cluster import ClusterController
from helpers.command import Command, exists, CommandError
import util
import time

from bwtest import log

class TestBasic( util.TestBase, bwtest.TestCase ):
	name = "Basic check of secondary DBs"
	description = "Basic Checks consolidate_db and sync_db"
	tags = []

	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.cleanSecondaryDBs()


	def tearDown( self ):
		self._cc.stop()
		self._cc.cleanSecondaryDBs();

		self._cc.clean()


	def runTest( self ):
		cmd = Command() 

		self._cc.start()

		time.sleep( 2 )

		self._cc.killProc( "dbapp" )
		time.sleep(1)
		self._cc.killProc( "baseapp" )

		# ls fails if db's are not found
		secDBPath = self._cc.getSecondaryDBPath()
		self.assertTrue( exists( secDBPath ), 
						"ls fails if db's are not found" )

		try:
			# This should fail
			cmd.call( 
			'BW_RES_PATH="{bwrespath}" {bwroot}/%s/%s/commands/sync_db'\
			% ( bwtest.config.BIGWORLD_FOLDER, 
				bwtest.config.SERVER_BINARY_FOLDER ) )
		except CommandError:
			pass
		else:
			log.debug( cmd.getLastOutput() )
			self.assertTrue( False, 'Expected exception on step 1.' )

		cmd.call( 
		'BW_RES_PATH="{bwrespath}" {bwroot}/%s/%s/commands/consolidate_dbs'
				 % ( bwtest.config.BIGWORLD_FOLDER, 
					 bwtest.config.SERVER_BINARY_FOLDER ))

		try:
			# second call should fail
			cmd.call( 'BW_RES_PATH="{bwrespath}" {bwroot}/%s/%s/commands/consolidate_dbs'\
					% ( bwtest.config.BIGWORLD_FOLDER, 
						bwtest.config.SERVER_BINARY_FOLDER ) )
		except CommandError:
			pass
		else:
			self.assertTrue( False, 'Expected exception on step 2.' )

		cmd.call( 'BW_RES_PATH="{bwrespath}" {bwroot}/%s/%s/commands/sync_db'\
				 % ( bwtest.config.BIGWORLD_FOLDER, 
					 bwtest.config.SERVER_BINARY_FOLDER ) )

