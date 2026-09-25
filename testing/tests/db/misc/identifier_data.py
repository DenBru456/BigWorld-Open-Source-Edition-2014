import time
from helpers.cluster import ClusterController

from test_common import *

from bwtest import log

# scenario 1: test changing an identifier property
class ModifyIdentifierProperty( TestCase ):
	name = 'Test changing an identifier property'
	description = 'Will start server and create a new entity that has an identifier property.' \
				  'Then connect to a baseApp and try to modify that property.' \
				  'Check that the modifications fails.'

	tags = []

	def step1( self ):
		"""Start server with 2 baseapps"""
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "baseApp/backupPeriod", "5" )
		self._cc.start()
		self._cc.startProc( 'baseapp', machineIdx=1 )


	def step2( self ):
		"""Wait for backup to be ready"""
		waitTime = self._cc.getConfig( "baseApp/backupPeriod" )
		log.debug( "Waiting for backup (%s seconds)" % waitTime )
		time.sleep( float(waitTime) )


	def step3( self ):
		"""Connect to baseapp01 and create an entity, write it to DB"""

		codeToRun = \
"""
def onCreate( *args ):
	e.destroy()
	srvtest.finish( (e.databaseID, entityName) )
	
from random import random
entityName = "test%f" % (random())
e = BigWorld.createEntity( "TestEntity", name = entityName )
e.writeToDB( onCreate, True )
"""

		log.debug( "running ==<%s>== on baseapp01" % codeToRun )
		self.entityID, self.entityName = \
				self._cc.sendAndCallOnApp( "baseapp", 1, codeToRun )
		

	def step4( self ):
		"""Check entity ID and name from DB"""

		log.debug( "Got entity's db id as %r" % self.entityID )
		log.debug( "Got entity's name as %r" % self.entityName )

		time.sleep( 1 )


	def step5( self ):
		"""Try to modify entity name, and check for failure"""

		codeToRun = \
"""
def onCreateBase( base, dbID, wasActive ):
	try:
		base.name = '12345'
	except ValueError, e:
		base.destroy()
		srvtest.finish(e)
	else:
		base.destroy()
		srvtest.fail()


BigWorld.createBaseFromDBID( "TestEntity", %r, onCreateBase )
""" % self.entityID

		log.debug( "running ==<%s>== on baseapp01" % codeToRun )
		error = self._cc.sendAndCallOnApp( "baseapp", 1, codeToRun )
		log.debug( "Error is: (as expected?) %s" % error )


	def step6( self ):
		"""Wait for db to write to backup"""
		waitTime = self._cc.getConfig( "baseApp/backupPeriod" )
		log.debug( "Waiting for backup (%s seconds)" % waitTime )
		time.sleep( float(waitTime) )


	def step7( self ):
		"""Load Entity from DB into baseapp02, and check for unmodified name"""
		
		codeToRun = \
"""
def onCreateBase( base, dbID, wasActive ):
	srvtest.finish( (base.databaseID, base.name) )

BigWorld.createBaseFromDBID( "TestEntity", %r, onCreateBase )
""" % self.entityID

		log.debug( "running ==<%s>== on baseapp02" % codeToRun )

		self.loadedID, self.loadedName = \
			self._cc.sendAndCallOnApp( "baseapp", 2, codeToRun )
		log.debug( "Got loaded entity's db id as %r" % self.loadedID )
		log.debug( "Got loaded entity's name as %r" % self.loadedName )
		
		self.assertTrue( self.loadedID == self.entityID,
				"Expected entityID(%r), got %s at step 7:" % \
				( self.entityID, self.loadedID ) )

		self.assertTrue( self.loadedName == self.entityName,
				"Expected entity (%s), got %s at step 7:" % \
				( self.entityName, self.loadedName ) )


	def tearDown( self ):
		"""Shut down server"""
		self._cc.stop()
		self._cc.clean()


