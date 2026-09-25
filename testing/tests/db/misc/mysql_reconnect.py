import time
from helpers.cluster import ClusterController

from test_common import *

from bwtest import log

# scenario 1: stop mysql server while entity is saved ( remote db )
class MysqlReconnectScenarioR( TestCase ):
	name = 'Test surviving MySQL server disconnection/reconnection, remote DB'
	description = 'Will connect to pyconsole, create an entity, \
				   then stop mysql and update entity. Check that entity updates \
				   are not lost after mysql comes back up.'
	tags = []

	def step0( self ):
		"""Given that server is restarted"""
		assert( TestCommon.stopServer() )
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.start()

	def step1( self ):
		"""Create entity on the baseapp"""

		codeToRun = \
"""
BigWorld.e = BigWorld.createEntity( "PersistentEntity" )
BigWorld.e.writeToDB()
srvtest.finish()
"""
		log.debug( "running ==<%s>== on baseapp01" % codeToRun )
		self._cc.sendAndCallOnApp( "baseapp", 1, codeToRun )

	def step2( self ):
		"""Stop MySQL database"""
		log.debug( "Stopping MySQL server at '%s'" % config.CLUSTER_DB_HOST )
		mysql.stopMysqlServer( config.CLUSTER_DB_HOST )


	def step3( self ): 
		"""Modify persistentProp of PersistentEntity entity"""

		codeToRun = \
"""
BigWorld.e.cellData[ "persistentProp" ] = 10
BigWorld.e.destroy()
srvtest.finish( BigWorld.e.databaseID )
"""
		log.debug( "running ==<%s>== on baseapp01" % codeToRun )
		self.dbID = self._cc.sendAndCallOnApp( "baseapp", 1, codeToRun )
		self.assertTrue( self.dbID, "Snippet call did not provide a dbId" )


	def step4( self ):
		"""Start MySQL database"""
		log.debug( "Starting MySQL server at '%s'" % config.CLUSTER_DB_HOST )
		mysql.startMysqlServer( config.CLUSTER_DB_HOST )
		time.sleep( 4 )


	def step5( self ):
		"""check the DB to contain modified persistentProp"""
		results = mysql.executeSQL( 
			'SELECT sm_persistentProp FROM tbl_PersistentEntity WHERE id = ' 
			+ str(self.dbID) )
		self.assertTrue( len(results) == 1, "Unexpected amount of results,\
		 Expected 1. Found %s" % len( results ) )
		self.assertTrue( results[0][0] == 10, "Value of persistent prop not set\
		correctly. Expected 10. Found %s" % results[0][0] )


	def tearDown( self ):
		"""Shut down server"""
		mysql.startMysqlServer( config.CLUSTER_DB_HOST )
		self._cc.stop()
		self._cc.clean()

# scenario 2: stop mysql server while entity is saved ( localhost db )
class MysqlReconnectScenarioL( TestCase ):
	name = 'Test surviving MySQL server disconnection/reconnection, localhost DB'
	description = 'Will connect to pyconsole, create an entity, \
				   then stop mysql and update entity. Check that entity updates \
				   are not lost after mysql comes back up. \
				   This test uses localhost as MySQL db for DBApp.'

	additionalInfo = ' \
				   This test requires that first cluster machine as defined \
				   in user_config.xml have a running MySQL server.'

	tags = [ 'MANUAL' ]

	def step0( self ):
		"""Given that server is restarted"""
		

		self._cc = ClusterController( [ "simple_space/res" ] )
		self.MYSQL_HOST = self._cc._machines[0]

		self.oldDbHost = config.CLUSTER_DB_HOST
		config.CLUSTER_DB_HOST = self.MYSQL_HOST
		self._cc.clearDB()

		self._cc.setConfig( "db/mysql/host", "localhost" )
		self._cc.start()


	def step1( self ):
		"""Create entity on the baseapp"""
		codeToRun = \
		"""
		BigWorld.e = BigWorld.createEntity( "PersistentEntity" )
		BigWorld.e.writeToDB()
		srvtest.finish()
		"""
		log.debug( "running ==<%s>== on baseapp01" % codeToRun )
		self._cc.sendAndCallOnApp( "baseapp", 1, codeToRun )


	def step2( self ):
		"""Stop MySQL database"""
		log.debug( "Stopping MySQL server at '%s'" % self.MYSQL_HOST )
		mysql.stopMysqlServer( self.MYSQL_HOST, local = True )


	def step3( self ): 
		"""Modify PersistentProp of PersistentEntity entity"""

		codeToRun = \
		"""
		BigWorld.e.cellData[ "persistentProp" ] = 10
		BigWorld.e.destroy()
		srvtest.finish( BigWorld.e.databaseID )
		"""
		log.debug( "running ==<%s>== on baseapp01" % codeToRun )
		self.dbID = self._cc.sendAndCallOnApp( "baseapp", 1, codeToRun )
		self.assertTrue( self.dbID, "Snippet call did not provide a dbId" )


	def step4( self ):
		"""Start MySQL database"""
		log.debug( "Starting MySQL server at '%s'" % self.MYSQL_HOST )
		mysql.startMysqlServer( self.MYSQL_HOST, local = True )
		time.sleep( 2 )


	def step5( self ):
		"""check the DB to contain modified persistentProp"""
		results = mysql.executeSQL( 
			'SELECT sm_persistentProp FROM tbl_PersistentEntity WHERE id = ' 
			+ str(self.dbID), host = self.MYSQL_HOST )
		self.assertTrue( len(results) == 1, "Unexpected amount of results,\
		 Expected 1. Found %s" % len( results ) )
		self.assertTrue( results[0][0] == 10, "Value of persistent prop not set\
		correctly. Expected 10. Found %s" % results[0][0] )


	def tearDown( self ):
		"""Shut down server"""
		if self.oldDbHost:
			config.CLUSTER_DB_HOST = self.oldDbHost
		mysql.startMysqlServer( self.MYSQL_HOST, local = True )
		self._cc.stop()
		self._cc.clean()


