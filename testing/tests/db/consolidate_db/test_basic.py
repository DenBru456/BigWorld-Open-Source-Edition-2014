import test_base
from bwtest.bwharness import TestCase

class TestBasic( test_base.TestBase, TestCase ):
	tags = []
	name = "Basic consolidation"
	description = "During shutdown, database consolidation is run\
	 and secondary databases are removed"
	
	def runTest( self ):
		self._cc.start()
		self._cc.waitForServerSettle()
		self.populateDB()
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) > 0, 
						"Secondary database files are not present when running" )
		self._cc.stop( timeout=60 )
		self.assertTrue( self.checkServerLogs(), 
						"Database consolidation was not run during shutdown" )
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) == 0, 
						"Secondary database files are still present after shutdown")


class TestConsolidateAll(test_base.TestBase, TestCase):
	tags = []
	name = "Consolidate all"
	description = "Database consolidation is done \
	with multiple base apps on multiple machines"
	
	def runTest( self ):
		self._cc.start()
		self._cc.startProc("baseapp", 4)
		self._cc.startProc("baseapp", 4, 1)
		self.populateDB()
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) > 0, 
						"Secondary database files are not present when running" )
		self._cc.stop( timeout = 60 )
		self.assertTrue( self.checkServerLogs(), 
						"Database consolidation was not run during shutdown" )
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) == 0, 
						"Secondary database files are still present after shutdown")

		
class TestConsolidateOneMachine(test_base.TestBase, TestCase):
	tags = []
	name = "Consolidate on one machine"
	description = "Database consolidation is done \
	with multiple base apps on a single machine"
	
	def runTest( self ):
		self._cc.start()
		self._cc.startProc("baseapp", 4)
		self.populateDB()
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) > 0, 
						"Secondary database files are not present when running" )
		self._cc.stop( timeout = 60 )
		self.assertTrue( self.checkServerLogs(), 
						"Database consolidation was not run during shutdown" )
		secFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secFiles ) == 0, 
						"Secondary database files are still present after shutdown")
