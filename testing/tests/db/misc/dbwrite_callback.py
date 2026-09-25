import time
from helpers.cluster import ClusterController, ClusterControllerError, \
							CoreDumpError

from test_common import *

from bwtest import log

# scenario 1: run writeToDB and check that backup entity gets updated before
# the callback is invoked.
class DBWriteCallbackTest( TestCase ):
	name = 'Test the writeToDB() callback is called only'\
			' after the backup entity is updated.'
	description = 'Will start server with two base apps, connect to pyconsole, \
					create an entity, modify its properties, then call writeToDB() \
					and ensure the callback hangs the first base app. Then check \
					the backup to have updated properties.'

	_cc = None
	tags = []

	def step1( self ):
		"""Start server with two baseApps and modified bw.xml to set 
baseApp/backUpUndefinedProperties to true"""
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "baseApp/backUpUndefinedProperties", "True" )
		self._cc.setConfig( "baseApp/backupPeriod", "5" )
		self._cc.setConfig( "allowInteractiveDebugging", "false" )

		self._cc.start()
		self._cc.startProc( 'baseapp', machineIdx=1 )


	def step2( self ):
		"""Wait for backup to be ready"""
		waitTime = self._cc.getConfig( "baseApp/backupPeriod" )
		log.debug( "Waiting for backup (%s seconds)" % waitTime )
		time.sleep( float(waitTime) )

	def step3( self ):
		"""Create entity on baseapp02"""

		codeToRun = """
e = BigWorld.createEntity( "PersistentEntity" )
e.shouldAutoBackup = False
srvtest.finish( e.id )
"""
		log.debug( "running ==<%s>== on baseapp02" % codeToRun )
		self.entityID = self._cc.sendAndCallOnApp( "baseapp", 2, codeToRun )


		try:
			self.entityID = int( self.entityID )
		except:
			log.debug( "Expected entityID, got %s from baseApp02 at step3:" % \
				self.entityID )
			assert( False )

		log.debug( "Got entity id as %r" % self.entityID )
		
		codeToRun = """
import time

def onCreate( *args ):
	time.sleep( 10 )

e = BigWorld.entities[%s]
e.persistentProp = 2
e.shouldAutoBackup = False
srvtest.finish()
e.writeToDB( onCreate, True )
""" % self.entityID

		try:
			self._cc.sendAndCallOnApp( "baseapp", 2, codeToRun )
		except ClusterControllerError:
			#This call will cause the baseapp to hang
			pass

	def step4( self ):
		"""Wait for db backup write"""
		waitTime = self._cc.getConfig( "baseApp/backupPeriod" )
		log.debug( "Waiting (%s seconds)" % waitTime )
		time.sleep( float(waitTime) * 2 )

	def step5( self ):
		"""Test that entity has been updated on baseapp01"""

		codeToRun= """
if BigWorld.entities.has_key( %s ):
	e = BigWorld.entities[%s]
	srvtest.finish( e.persistentProp )
else:
	srvtest.assertTrue( False, "Entity was not backed up.")
"""	 % ( self.entityID, self.entityID )
		log.debug( "running ==<%s>== on baseapp01" % codeToRun )
	
		persistentProp = self._cc.sendAndCallOnApp( "baseapp", 1, codeToRun )
		self.assertTrue( persistentProp == 2,
			"Unexpected persistentProp from baseApp02 at step4: '%s'" % 
				persistentProp )


	def tearDown( self ):
		"""Shut down server"""
		try:
			self._cc.stop()
		except CoreDumpError, e:
			if len( e.failedAppList ) == 1 and e.failedAppList[0] == "baseapp":
				pass
			else:
				raise

		self._cc.clean()


