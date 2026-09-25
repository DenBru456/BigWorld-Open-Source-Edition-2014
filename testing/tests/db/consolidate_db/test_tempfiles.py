from helpers.command import remove, exists
import test_base

from bwtest import TestCase, config


class TestCleanTempFiles( test_base.TestBase, TestCase):
	
	tags = []
	name = "Clean up temporary files"
	description = "Temporary files used by the \
	data consolidation process are deleted"


	def runTest( self ):
		remove( "/tmp/%s_*.db" % config.CLUSTER_USERNAME )
		self._cc.start()
		self.populateDB()
		self._cc.stop( timeout = 60 )
		self.assertFalse( exists( "/tmp/%s_*.db" % config.CLUSTER_USERNAME ), 
						"Temporary files were not cleaned up correctly" )
			

class TestCleanTempFilesOnFailure( test_base.TestBase, TestCase):
	
	tags = []
	name = "Clean up temporary files on failure"
	description = "Temporary files used by the \
	data consolidation process are deleted\
	when the data consolidation process fails"


	def runTest( self ):
		remove( "/tmp/%s_*.db" % config.CLUSTER_USERNAME )
		self._cc.start()
		self.populateDB()
		self.removeTransferDb()
		self._cc.stop( timeout = 60 )
		self.assertFalse( exists( "/tmp/%s_*.db" % config.CLUSTER_USERNAME ), 
						"Temporary files were not cleaned up correctly" )
