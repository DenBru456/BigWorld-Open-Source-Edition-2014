import os
import sys
import bwtest
from helpers.cluster import ClusterController
from helpers.command import Command, exists, move, CommandError
import util
import time
from random import random

from primitives import mysql
from bwtest import config
from bwtest import log


class TestNoSecondaryDBOnXML( util.TestBase, bwtest.TestCase  ):
	name = "No Secondary DB in XML mode"
	description = """
	Secondary databases are disabled when the primary database is the XML database
	"""
	tags = []

	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "db/type", "xml" )
		self._cc.setConfig( "db/secondaryDB/enable", "true" )
		self._cc.setConfig( "baseApp/archivePeriod", str( self.ARCHIVE_PERIOD ) )
		self._cc.setConfig( "baseApp/backupPeriod", str( self.BACKUP_PERIOD ) )

		self._cc.cleanSecondaryDBs();

		self._cc.start()


	def runTest( self ):
		cc = self._cc

		cc.waitForApp( "baseapp", 1 )

		secDBPath = cc.getSecondaryDBPath()
		self.assertFalse( exists( "%s/*.db" % secDBPath ) ,
						"Secondary databases existed on XML" )


class TestMissingDirectory( util.TestBase, bwtest.TestCase  ):
	name = "Missing directory is ok"
	description = """
	BaseApp won't fail to start if secondary databases are disabled and 
	the directory where the secondary databases are supposed to be stored
	does not exist.
	"""

	tags = []

	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "db/secondaryDB/enable", "false" )
		self._cc.setConfig( "db/secondaryDB/directory", "/ryueu/ksjkjds/jdkflsjjdsj" )
		self._cc.setConfig( "baseApp/archivePeriod", str( self.ARCHIVE_PERIOD ) )
		self._cc.setConfig( "baseApp/backupPeriod", str( self.BACKUP_PERIOD ) )

		self._cc.start()


	def runTest( self ):
		cc = self._cc

		cc.waitForApp( "baseapp", 1 )


class SqliteBase( object ):
	def createEntities( self ):
		cc = self._cc

		snippet = """
from random import random		
createdEntities = []
def callback( res, ent ):
	srvtest.assertTrue( res )
	createdEntities.append( ent.databaseID )
	if len( createdEntities ) == 10:
		srvtest.finish( createdEntities )

for i in range(10):		
	entityName = "temp%d%f" % (i, random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
	e.writeToDB( callback, {isPersistent} )
"""
		self._entities = cc.sendAndCallOnApp( "baseapp", 1, 
						snippet,
						isPersistent = True )


	def readSqliteDB( self, dbFile, table ):
		if not os.path.exists( dbFile ):
			log.error( "readSqliteDB failed: file %s not found", dbFile )
			return []

		sqlCommand = "SELECT sm_dbID, sm_time FROM %s ORDER BY sm_time DESC" % \
						table
		cmd = Command( ["sqlite3 %s '%s'" % (dbFile, sqlCommand)] )
		try:
			cmd.call()
		except CommandError, e:
			log.error( "sqlite3 command failed: %s", str( e ) )
			return [] 

		lines = cmd.getLastOutput()[0].splitlines()
		res = [ ( int( line.split( '|' )[0] ), int( line.split( '|' )[1] ) )
		 		for line in lines ]

		# log.error( "db file = %s, res = %r", dbFile, res )
		return res


	def findActiveSqliteTable( self, secFiles, dbIds ):
		def findTimeInLines( lines ):
			for line in lines:
				if line[0] in dbIds:
					return line[1]
			return -1

		maxName = ""
		maxFile = ""
		maxTime = -1
		maxLines = []
		for fileName in secFiles:
			linesFlip = self.readSqliteDB( fileName, "tbl_flip" )
			linesFlop = self.readSqliteDB( fileName, "tbl_flop" )
			timeFlip = findTimeInLines( linesFlip )
			timeFlop = findTimeInLines( linesFlop )
			if timeFlip > maxTime:
				maxTime = timeFlip
				maxLines = linesFlip
				maxName = "tbl_flip"
				maxFile = fileName
			if timeFlop > maxTime:			
				maxTime = timeFlop
				maxLines = linesFlop
				maxName = "tbl_flop"
				maxFile = fileName

		return ( maxLines, maxTime, maxName, maxFile )



class TestControlledShutdown( SqliteBase, util.TestBase, bwtest.TestCase ):
	name = "Controlled shutdown"
	description = """
	During controlled shutdown, writeToDB() is called on all persistent entities.
	"""

	tags = []


	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )

		def cleanup1():
			self._cc.stop()
			self._cc.clean()
		self.addCleanup( cleanup1 )

		self._cc.setConfig( "db/secondaryDB/enable", "true" )
		self._cc.setConfig( "baseApp/archivePeriod", str( self.ARCHIVE_PERIOD ) )
		self._cc.setConfig( "baseApp/backupPeriod", str( self.BACKUP_PERIOD ) )

		self._cc.cleanSecondaryDBs();

		self._transferPath = os.path.join( config.CLUSTER_BW_ROOT,
				config.BIGWORLD_FOLDER, config.SERVER_BINARY_FOLDER, 
				"commands/transfer_db" )
		self._consolidatePath = os.path.join( config.CLUSTER_BW_ROOT,
				config.BIGWORLD_FOLDER, config.SERVER_BINARY_FOLDER, 
				"commands/consolidate_dbs" )

		move( self._transferPath, self._transferPath + ".bak" )

		def cleanup2():
			if exists( self._transferPath  + ".bak" ):
				move( self._transferPath  + ".bak", 
								self._transferPath )
		self.addCleanup( cleanup2 )

		self.assertFalse( os.access( self._transferPath, os.F_OK ) )
		self.assertTrue( os.access( self._transferPath + ".bak", os.F_OK ) )

		move( self._consolidatePath, self._consolidatePath + ".bak" )

		def cleanup3():
			if exists( self._consolidatePath + ".bak" ):
				move( self._consolidatePath  + ".bak", 
								self._consolidatePath )
		self.addCleanup( cleanup3 )

		self.assertFalse( exists( self._consolidatePath ) )
		self.assertTrue( exists( self._consolidatePath + ".bak" ) )


	def runTest( self ):
		"""Starting a cluster and write entities"""
		cc = self._cc

		# wait until any previos consolidate_dbs process has finished
		time.sleep( 60 )

		self._cc.start()

		cc.waitForApp( "baseapp", 1 )

		time.sleep( self.BACKUP_PERIOD )

		self.createEntities()

		snippet = """
srvtest.finish( BigWorld.time() * 10 )
"""
		self._lastTime = cc.sendAndCallOnApp( "baseapp", 1, snippet ) 

		cc.stop( timeout = 60 )


#	def step2( self ):
#		"""Examining secondary databases"""

		self._secFiles = cc.getSecondaryDBFiles()

		log.debug( self._secFiles )
		self.assertTrue( len( self._secFiles ) > 0, msg = "no "
				 		"secondary dbs found after cluster shutdown" )					 

		list, maxtime, tableName, file = \
				self.findActiveSqliteTable( self._secFiles, self._entities )

		for dbID in self._entities:
			isOk = False
			for t in list:
				if dbID == t[0] and self._lastTime < t[1]:
					isOk = True
			self.assertTrue( isOk, msg = "lastServerTime = %d\n"
				  		"list = %r" % (self._lastTime, list) ) 



class TestFlippingTablesBase( SqliteBase, util.TestBase ):
	name = "Flipping tables"
	description = """
	All persistent entities has an entry in the current table before flipping.
	"""

	tags = []

	BACKUP_PERIOD = 100
	PERIOD_BASE = 15

	def setUpBase( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "db/secondaryDB/enable", "true" )
		self._cc.setConfig( "baseApp/archivePeriod", str( self.ARCHIVE_PERIOD ) )
		self._cc.setConfig( "baseApp/backupPeriod", str( self.BACKUP_PERIOD ) )
		self._cc.setConfig( "db/secondaryDB/maxCommitPeriod",
					 str( self.COMMIT_PERIOD ) )

		self._cc.cleanSecondaryDBs();

		self._cc.start()


	def tearDownBase( self ):
		self._cc.stop()

		self._cc.clean()


	def runTestBase( self ):
		cc = self._cc

		cc.waitForApp( "baseapp", 1 )

		self.createEntities()

		time.sleep( self.ARCHIVE_PERIOD * 2 + 2 )

		secFiles = cc.getSecondaryDBFiles()

		self.assertTrue( secFiles, "Could not find secondary db files" )

		dbList, maxtime, notedTable, notedFile = \
				self.findActiveSqliteTable( secFiles, self._entities )


		# table-in-use is currently empty
		if notedTable == "tbl_flip":
			notedTable = "tbl_flop"
		elif notedTable == "tbl_flop":
			notedTable = "tbl_flip"

		self.assertTrue( notedTable, "Could not find an active table in %s " %
				 notedFile )

		time.sleep( self.ARCHIVE_PERIOD + 1 )

		dbList = self.readSqliteDB( notedFile, notedTable )

		# checking that all created entities have entry in
		# the noted table
		for dbID in self._entities:
			isOk = False
			for t in dbList:
				if dbID == t[0]:
					isOk = True
			self.assertTrue( isOk, msg = "dbID %d "
							"not found in the secondary database = "
				   			"%r" % (dbID, dbList) )

		time.sleep( 1 )


class TestFlippingTables( TestFlippingTablesBase, bwtest.TestCase ):
	name = "Flipping tables"
	description = """
	All persistent entities has an entry in the current table before flipping.
	"""

	tags = []

	BACKUP_PERIOD = 100
	ARCHIVE_PERIOD = 10
	COMMIT_PERIOD = 20 

	def setUp( self ):
		pass


	def tearDown( self ):
		self.tearDownBase()


	def step1( self ):
		""" archivePeriod = maxCommitPeriod * 2 """
		self.ARCHIVE_PERIOD = self.PERIOD_BASE * 2
		self.COMMIT_PERIOD = self.PERIOD_BASE
		self.setUpBase()
		self.runTestBase()
		self.tearDownBase()


	def step2( self ):
		""" archivePeriod == maxCommitPeriod """
		self.ARCHIVE_PERIOD = self.PERIOD_BASE
		self.COMMIT_PERIOD = self.PERIOD_BASE
		self.setUpBase()
		self.runTestBase()
		self.tearDownBase()


	def step3( self ):
		""" archivePeriod * 2 = maxCommitPeriod """
		self.ARCHIVE_PERIOD = self.PERIOD_BASE
		self.COMMIT_PERIOD = self.PERIOD_BASE * 2
		self.setUpBase()
		self.runTestBase()
		self.tearDownBase()

	def step4( self ):
		""" archivePeriod != maxCommitPeriod """
		self.ARCHIVE_PERIOD = self.PERIOD_BASE
		self.COMMIT_PERIOD = self.PERIOD_BASE + 3 
		self.setUpBase()
		self.runTestBase()


class TestCommitPeriod( SqliteBase, util.TestBase, bwtest.TestCase ):
	name = "Commit period"
	description = """
	Implicit writeToDBs are committed at least once per commit period.
	"""

	tags = []

	ARCHIVE_PERIOD = 400
	MAX_COMMIT_PERIOD = 30

	RES_PATH = config.TEST_ROOT + "/res_trees/simple_space/res"
#	RES_PATH = config.CLUSTER_BW_ROOT + "/game/res/fantasydemo"

	# this is used by getSecondaryDBFiles()
	SEC_DB_PATH = RES_PATH + "/server/db/secondary/"

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		self._cc.setConfig( "db/type", "mysql" )
		self._cc.setConfig( "db/secondaryDB/enable", "true" )
		self._cc.setConfig( "db/secondaryDB/maxCommitPeriod", 
					 		str( self.MAX_COMMIT_PERIOD ) )
		self._cc.setConfig( "baseApp/archivePeriod", str( self.ARCHIVE_PERIOD ) )

		self._cc.cleanSecondaryDBs();

		self._cc.start()


	def tearDown( self ):
		self._cc.stop()

		self._cc.clean()


	def step1( self ):
		""" Create persistent entities in the mysql database """
		cc = self._cc

		cc.waitForApp( "baseapp", 1 )


		snippet = """
from random import random		

for i in range(40):		
	entityName = "temp%d%f" % (i, random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
	e.writeToDB( lambda a, b: None, True )

srvtest.finish()
"""
		cc.sendAndCallOnApp( "baseapp", 1, snippet )

		cc.stop()


	def step2( self ):		
		"""Check whether persistent entities get archived to secondary db"""

		cc = self._cc

		cc.start()

		cc.waitForApp( "baseapp", 1 )

		def getMaxTime():
			secFiles = cc.getSecondaryDBFiles()
			maxTime = -1
			for fileName in secFiles:
				listFlip = self.readSqliteDB( fileName, "tbl_flip" )
				listFlop = self.readSqliteDB( fileName, "tbl_flop" )
				log.debug( "file: %s\nflip: %s\nflop: %s", 
					str( fileName ), str( listFlip ), str( listFlop ) )
				if len( listFlip ) > 0 and listFlip[0][1] > maxTime:
					maxTime = listFlip[0][1]
				if len( listFlop ) > 0 and listFlop[0][1] > maxTime:
					maxTime = listFlop[0][1]
			return maxTime

		currentTime = time.time()
		startMaxTime = getMaxTime()
		while True:
			time.sleep( 1 )
			newMaxTime = getMaxTime()
			if newMaxTime > startMaxTime:
				#At this point a commit should have just happpened
				break

			if ( time.time() - currentTime > self.MAX_COMMIT_PERIOD + 1 ):
				self.fail( "No database commits are happening")

		time1 = getMaxTime()

		time.sleep( self.MAX_COMMIT_PERIOD + 1 )

		time2 = getMaxTime()

		time.sleep( self.MAX_COMMIT_PERIOD / 2 )

		time3 = getMaxTime()

		self.assertTrue( time2 > time1, 
						"No commits happened in MAX_COMMIT_PERIOD" )
		self.assertTrue( time2 == time3, 
						"Commits happened during MAX_COMMIT_PERIOD" )

