import time
from helpers.cluster import ClusterController

import xmlconf

from test_common import *

from bwtest import log

# time to wait if Xml DB file is not found after cluster run
XMLDB_WAIT = 20



# scenario 1: test writing of space data into MySQL database
class WriteSpaceDataToMysqlDB( TestCase ):
	name = 'Test writing of space data into MySQL database.'
	description = 'Will start server with cellAppMgr/shouldArchiveSpaceData=True ' \
				  'and cellAppMgr/archivePeriod=30, then stop the server and check ' \
				  'contents of bigworldSpaceData table.'

	tags = []

	def step1( self ):
		"""Start server with modified bw.xml to set 
cellAppMgr/archivePeriod=30 and cellAppMgr/shouldArchiveSpaceData=True"""

		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "cellAppMgr/shouldArchiveSpaceData", "True" )
		self._cc.setConfig( "cellAppMgr/archivePeriod", "5" )

		self._cc.start()


	def step2( self ):
		"""Wait for 10 seconds"""
		time.sleep( 10 )


	def step3( self ):
		"""Shut down server"""
		TestCommon._getCC().stop() 


	def step4( self ):
		"""Check there are entries in bigworldSpaceData table"""
		results = mysql.executeSQL( 'SELECT spaceEntryID FROM bigworldSpaceData' )
		assert( len(results) >= 1 )


	def tearDown( self ):
		"""Shut down server"""
		self._cc.stop()
		self._cc.clean()


# scenario 2: test disabled writing of space data into MySQL database
class DontWriteSpaceDataToMysqlDB( TestCase ):
	name = 'Test that server does not write space data into MySQL database.'
	description = 'Will start server with cellAppMgr/shouldArchiveSpaceData=False ' \
				  'and cellAppMgr/archivePeriod=30, then stop the server and check ' \
				  'bigworldSpaceData table to be empty.'

	tags = []

	def step1( self ):
		"""Drop table bigworldSpaceData"""
		try:
			mysql.executeSQL( 'DROP TABLE bigworldSpaceData' )
		except Exception, e:
			log.debug( "Caught Mysql exception: %s" % e )
			pass


	def step2( self ):
		"""Start server with modified bw.xml to set 
cellAppMgr/archivePeriod=30 and cellAppMgr/shouldArchiveSpaceData=False"""

		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "cellAppMgr/shouldArchiveSpaceData", "False" )
		self._cc.setConfig( "cellAppMgr/archivePeriod", "5" )

		self._cc.start()


	def step3( self ):
		"""Wait for 10 seconds"""
		time.sleep( 10 )


	def step4( self ):
		"""Shut down server"""
		TestCommon._getCC().stop() 


	def step5( self ):
		"""Check bigworldSpaceData table is empty"""
		results = mysql.executeSQL( 'SELECT spaceEntryID FROM bigworldSpaceData' )
		assert( len(results) < 1 )


	def tearDown( self ):
		"""Shut down server"""
		self._cc.stop()
		self._cc.clean()


# scenario 3: test writing of space data into XML database
class WriteSpaceDataToSQLite( TestCase ):
	name = 'Test writing of space data into XML database.'
	description = 'Will start server with cellAppMgr/shouldArchiveSpaceData=True ' \
				  'and cellAppMgr/archivePeriod=30, then stop the server and check ' \
				  'contents of bigworldSpaceData table.'

	tags = []

	def step1( self ):
		"""Start server with modified bw.xml to set 
cellAppMgr/archivePeriod=30 and cellAppMgr/shouldArchiveSpaceData=True"""

		self.oldtype = config.CLUSTER_DB_TYPE
		config.CLUSTER_DB_TYPE = "xml"
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "cellAppMgr/shouldArchiveSpaceData", "True" )
		self._cc.setConfig( "cellAppMgr/archivePeriod", "5" )
		self._cc.setConfig( "db/type", "xml" )

		self._cc.start()


	def step2( self ):
		"""Wait for 10 seconds"""
		time.sleep( 10 )


	def step3( self ):
		"""Shut down server"""
		TestCommon._getCC().stop() 

	def step4( self ):
		"""Check there are entries in AutoLoadedSpaceData xml node"""
		class Object:pass
		var = Object()
		dbFile = self._cc.getXmlDB()
		i = 0;
		while i < XMLDB_WAIT and not dbFile:
			log.error( "Failed to get XmlDB file for cluster" )
			dbFile = self._cc.getXmlDB()
			time.sleep(1)
			i = i + 1

		self.assertTrue( dbFile is not None, "Failed to get XmlDB file for cluster" )

		log.debug( "Checking for db.xml/_BigWorldInfo/AutoLoadedSpaceData in %s" % dbFile )

		try:
			success = xmlconf.readConf( dbFile, var, 
				{ '_BigWorldInfo/AutoLoadedSpaceData/space/dataItems/item/data' : 'spaceData' },
				rootTag = 'db.xml'
			)
		except IOError:
			log.debug( "[bwtest][warning] %s not found!" % dbFile )
			assert( False )

		assert( success )
		assert( var.spaceData )
		assert( len(var.spaceData) > 0 )
		log.debug( var.spaceData )


	def tearDown( self ):
		"""Shut down server"""
		self._cc.stop()
		self._cc.clean()
		config.CLUSTER_DB_TYPE = self.oldtype



# scenario 4: test disabled writing of space data into XML database
class DontWriteSpaceDataToSQLite( TestCase ):
	name = 'Test disabled writing of space data into XML database.'
	description = 'Will start server with cellAppMgr/shouldArchiveSpaceData=False ' \
				  'and cellAppMgr/archivePeriod=30, then stop the server and check ' \
				  'contents of bigworldSpaceData table.'

	tags = []


	def step1( self ):
		"""Start server with modified bw.xml to set 
cellAppMgr/archivePeriod=30 and cellAppMgr/shouldArchiveSpaceData=True"""

		self.oldtype = config.CLUSTER_DB_TYPE
		config.CLUSTER_DB_TYPE = "xml"
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "cellAppMgr/shouldArchiveSpaceData", "False" )
		self._cc.setConfig( "cellAppMgr/archivePeriod", "5" )
		self._cc.setConfig( "db/type", "xml" )
		self._cc.start()


	def step2( self ):
		"""Wait for 10 seconds"""
		time.sleep( 10 )


	def step3( self ):
		"""Shut down server"""
		self._cc.stop() 


	def step4( self ):
		"""Check there are NO entries in AutoLoadedSpaceData xml node"""
		class Object:pass
		var = Object()
		dbFile = self._cc.getXmlDB()
		i = 0;
		while i < XMLDB_WAIT and not dbFile:
			log.error( "Failed to get XmlDB file for cluster" )
			dbFile = self._cc.getXmlDB()
			time.sleep(1)
			i = i + 1

		self.assertTrue( dbFile is not None, "Failed to get XmlDB file for cluster" )

		log.debug( "Checking for db.xml/_BigWorldInfo/AutoLoadedSpaceData in %s"
				 % dbFile )

		try:
			success = xmlconf.readConf( dbFile, var, 
				{ '_BigWorldInfo/AutoLoadedSpaceData/space/dataItems/item/data':
						 'spaceData' },
				rootTag = 'db.xml'
			)
		except IOError:
			log.debug( "[bwtest][warning] %s not found!" % dbFile )
			assert( False )

		assert( success )
		assert( not hasattr( var, 'spaceData' ) )


	def tearDown( self ):
		"""Shut down server"""
		self._cc.stop()
		self._cc.clean()
		config.CLUSTER_DB_TYPE = self.oldtype


