import bwtest
import util
import time
from random import random

from helpers.timer import runTimer, TimerError


class TestRegistration( util.TestBase, bwtest.TestCase  ):
	name = "Secondary DB registration"
	description = """
	Secondary databases are registered in the bigworldSecondaryDatabases table.
	"""
	tags = []


	def runTest( self ):
		"""Testing registration"""

		cc = self._cc

		NUM_SERVICE_APPS = 1		

		cc.waitForApp( "baseapp", 1 )
		
		count = cc.getSecondaryDBCount()
		self.assertEqual( count, 1 + NUM_SERVICE_APPS )

		# Simultaneous registration
		cc.startProc( "baseapp", 2 )

		cc.waitForApp( "baseapp", 2 )
		cc.waitForApp( "baseapp", 3 )

		count = cc.getSecondaryDBCount()
		self.assertEqual( count, 3 + NUM_SERVICE_APPS )



class TestDeregistration( util.TestBase, bwtest.TestCase  ):
	name = "Secondary DB deregistration"
	description = """
	Secondary databases are deregistered when the associated BaseApp dies and 
	entity restore was successful.
	"""
	tags = []

				
	def runTest( self ):
		"""Testing deregistration"""

		cc = self._cc

		NUM_SERVICE_APPS = 1		

		cc.startProc( "baseapp", 2 )

		cc.waitForApp( "baseapp", 1 )
		cc.waitForApp( "baseapp", 2 )
		cc.waitForApp( "baseapp", 3 )

		time.sleep( self.BACKUP_PERIOD )
		
		def waiter( expectedCount ):
			try:		
				runTimer( cc.getSecondaryDBCount,
							lambda c: c == expectedCount )
			except TimerError:
				self.fail( "secondary db count %d != %d",
							 cc.getSecondaryDBCount(), expectedCount )
		
		waiter( 3 + NUM_SERVICE_APPS )
		
		# Deregistration on BaseApp retire
		cc.retireProc( "baseapp", 3 )
		time.sleep( self.ARCHIVE_PERIOD * 2 + 1 )

		waiter( 2 + NUM_SERVICE_APPS )

		# Deregistration on BaseApp kill
		cc.killProc( "baseapp", 2 )
		time.sleep( self.ARCHIVE_PERIOD * 2 + 1 )

		waiter( 1 + NUM_SERVICE_APPS )


class TestNoDeregistrationOnDisaster( util.TestBase, bwtest.TestCase  ):
	name = "No deregistration on disaster"
	description = """
	Secondary databases are not deregistered 
	if the system cannot fully recover all entities
	"""
	
	tags = []
	
					
	def runTest( self ):
		"""Testing deregistration on disaster"""

		cc = self._cc

		NUM_SERVICE_APPS = 1		

		cc.startProc( "baseapp", 4 )
		
		snippet = """
from random import random
for i in range(100):		
	entityName = "temp%d%f" % (i, random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
	e.writeToDB()
srvtest.finish()
"""	
		cc.sendAndCallOnApp( "baseapp", 1, snippet )
		cc.sendAndCallOnApp( "baseapp", 2, snippet )
		cc.sendAndCallOnApp( "baseapp", 3, snippet )
		cc.sendAndCallOnApp( "baseapp", 4, snippet )

		time.sleep( self.BACKUP_PERIOD * 2 )
		try:
			cc.setCoreDumpChecking( False )
			cc.killProc( "serviceapp" )
			cc.killProc( "baseapp", 5, forced = True )
			cc.killProc( "baseapp", 4, forced = True )
			cc.killProc( "baseapp", 3, forced = True )
			cc.killProc( "baseapp", 2, forced = True )
			cc.killProc( "baseapp", 1, forced = True )
		except:
			# one of kills may fail and that's ok
			# because the server will start shutting down
			# on bad state
			import traceback
			traceback.print_exc()
		

		ret = cc.waitForServerShutdown( self.ARCHIVE_PERIOD * 4 )
		self.assertTrue( ret, "Server did not shut-down cleanly on bad state" )

		count = cc.getSecondaryDBCount()
		self.assertEqual( count, 0 )
