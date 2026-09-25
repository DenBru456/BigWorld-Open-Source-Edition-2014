import time

import test_base
from helpers.command import Command, CommandError

from bwtest import TestCase
from primitives import mysql

class TestManualConsolidation( test_base.TestBase, TestCase ):


	tags = []
	name = "Manual consolidation"
	description = "Data consolidation can be run manually."


	def runTest( self ):
		self._cc.start()
		self.populateDB()
		time.sleep( self.ARCHIVE_PERIOD )
		self._cc.killProc( "dbapp" )
		self._cc.stop()
		
		cmd = Command()
		cmd.call( 'BW_RES_PATH="{bwrespath}" {bwroot}/%s/consolidate_dbs'
				 % self.COMMANDS_DIR )
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) == 0, 
			"Secondary database files are present after manual consolidation" )
		

class TestSkipConsolidation( test_base.TestBase, TestCase):
	
	
	tags = []
	name = "Skipping data consolidation"
	description = "Clears secondary database registration entries\
	 when --clear is specified"

	
	def runTest( self ):
		self._cc.start()
		self.populateDB()
		time.sleep( self.ARCHIVE_PERIOD )
		self._cc.killProc( "dbapp" )
		self._cc.stop()
		
		cmd = Command()
		cmd.call( 'BW_RES_PATH="{bwrespath}" {bwroot}/%s/consolidate_dbs --clear' 
				% self.COMMANDS_DIR )
		
		self.assertTrue( self._cc.getSecondaryDBCount() == 0, 
						"Secondary DB count not zero after clearing" )
		
		self._cc.start()
		self.assertFalse( self.checkServerLogs(), 
						"Data consolidation was not skipped" )


class TestClearWhileRunning( test_base.TestBase, TestCase ):
	

	tags = []
	name = "Cannot --clear running system"
	description = "consolidate_dbs returns an error \
	if the database is still in use by a running system"


	def runTest( self ):
		self._cc.start()
		self.populateDB()
		
		cmd = Command()
		try:
			cmd.call( 'BW_RES_PATH="{bwrespath}" {bwroot}/%s/consolidate_dbs --clear' 
					% self.COMMANDS_DIR )
		except CommandError:
			pass #This should fail
		else:
			self.assertTrue( False, 
						"consolidate_dbs --clear worked on a running system" )
		
		self._cc.stop() 