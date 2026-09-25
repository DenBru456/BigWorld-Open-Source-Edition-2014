import os, time
from xml.dom.minidom import parse

from helpers.cluster import ClusterController
from helpers.command import move
from bwtest import config, log
from primitives import mysql, locallog


class TestBase ( object):

	MAX_COMMIT_PERIOD = 5
	ARCHIVE_PERIOD = 5
	
	def setUp(self):
		self.moved = False
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "db/secondaryDB/enable", "true" )
		self._cc.setConfig( "db/secondaryDB/maxCommitPeriod",
						 str( self.MAX_COMMIT_PERIOD ) )
		self._cc.setConfig( "baseApp/archivePeriod", str( self.ARCHIVE_PERIOD ) )
		
		self._cc.cleanSecondaryDBs()
		
	def tearDown( self ):
		self.restoreTransferDb()
		if hasattr( self, "_cc" ):
			self._cc.stop()
			self._cc.clean()


	def checkServerLogs( self ):
		ret = True
		output = locallog.grepLastServerLog( "Starting data consolidation" )
		ret = ret and len( output ) > 0
		output = locallog.grepLastServerLog( "Consolidating '/tmp/%s" % \
											config.CLUSTER_USERNAME)
		ret = ret and len( output ) > 0
		output = locallog.grepLastServerLog( "Finished data consolidation" )
		ret = ret and len( output ) > 0
		return ret

	COMMANDS_DIR = "%s/%s/commands" % (config.BIGWORLD_FOLDER, 
									   config.SERVER_BINARY_FOLDER )
	
	def removeTransferDb( self ):
		move( "{bwroot}/%s/transfer_db" % self.COMMANDS_DIR, 
						"{bwroot}/%s/transfer_db_bck" % self.COMMANDS_DIR )
		self.moved = True
		time.sleep( 2 ) #Sleep to ensure the file is moved on network shares
	

	def restoreTransferDb( self ):
		if self.moved:
			move( "{bwroot}/%s/transfer_db_bck" % self.COMMANDS_DIR, 
						"{bwroot}/%s/transfer_db" % self.COMMANDS_DIR )

	def populateDB( self ):
		snippet = """
for i in range( 20 ):
	e = BigWorld.createEntity( "PersistentEntity" )
	e.writeToDB()
srvtest.finish()
"""
		self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		
		
	def _parseUserConfig( self ):
		userConfigFile = config.TEST_ROOT + "/user_config/user_config.xml"
		doc = parse( userConfigFile )
		try:
			doc = parse( userConfigFile )
		except IOError:
			log.error( "user_config/user_config.xml not found!" )
			return

		if doc is None:
			log.error( "failed to parse user_config/user_config.xml!" )
			return
		
		config.WINDOWS_MOUNT = \
			doc.getElementsByTagName( "windowsMount" ).item( 0 )\
			.firstChild.nodeValue.strip()
		
