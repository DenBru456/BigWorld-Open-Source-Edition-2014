import bwtest
from helpers.cluster import ClusterController
import unittest
import time

from bwtest import log
from bwtest import config
from bwtest import manual

from test_common import LoadBalanceCommon

def approxEqual(a, b, tolerance = 0.00001):
	return abs(a - b) < tolerance


class ArtificialLoadTest( LoadBalanceCommon, bwtest.TestCase ):
	name = "Artificial load test" 
	description = """
	Testing ability to set artificial load on base and cell entity
	"""
	tags = []

	priority = 1


	RES_PATH = "simple_space/res"

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )

		self.addCleanup( self._cc.clean )

		self._cc.start()

		self.addCleanup( self._cc.stop )


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def step1( self ):
		"""
		Test whether we can set artificial load on base and cell entities
		"""

		spaces = self.getSpaces()
		
		self.assertTrue( spaces, "No spaces found in the cluster" )
		
		spaceID = spaces[ 0 ] 

		time.sleep( 2 )

		snippet = """
		entities = []
		loads = {loads}
		for ld in loads:
			e = BigWorld.createEntity( "TestEntity" )
			entities.append( e )
			e.artificialMinLoad = ld

			e.cellData[ "spaceID" ] = {spaceID}
			e.createCellEntity()

		srvtest.finish( [e.id for e in entities] )
		"""


		self._loads = [0.01, 0.02, 0.03]

		self._ids = self._cc.sendAndCallOnApp( "baseapp", 1, snippet,
				 loads = self._loads, spaceID = spaceID )

		time.sleep( 1 )

		snippet = """
		ids = {ids}
		loads = {loads}
		lid = 0
		for id in ids:
			e = BigWorld.entities[ id ]
			e.artificialMinLoad = loads[ lid ]
			lid += 1
		
		srvtest.finish()
		"""

		self._cc.sendAndCallOnApp( "cellapp", 1, snippet,
				 loads = self._loads, ids = self._ids )

		time.sleep( 1 )

		def checkLoads( appName, ids, loads ):
			lid = 0
			for id in ids:
				watcherPath = "entities/%d/profile/load" % id
				val = self._cc.getWatcherValue( watcherPath, appName, 1 )

				self.assertTrue( approxEqual( loads[lid], val ), 
					"%s: got value of %f for entity %d, expected %f" %
							(appName, val, id, loads[lid]) )
				lid += 1

		checkLoads( "baseapp", self._ids, self._loads )
		checkLoads( "cellapp", self._ids, self._loads )


	def step2( self ):
		"""
		Test whether the artificial load can be disabled
		"""

		snippet = """
		ids = {ids}
		for id in ids:
			e = BigWorld.entities[ id ]
			e.artificialMinLoad = -1
		
		srvtest.finish()
		"""

		self._cc.sendAndCallOnApp( "baseapp", 1, snippet,
							ids = self._ids )

		self._cc.sendAndCallOnApp( "cellapp", 1, snippet,
							ids = self._ids )


		time.sleep( 3 )

		def checkLoads( appName, ids, loads ):
			lid = 0
			for id in ids:
				watcherPath = "entities/%d/profile/load" % id
				val = self._cc.getWatcherValue( watcherPath, appName, 1 )

				self.assertFalse( approxEqual( loads[lid], val ), 
					"%s: got value of %f for entity %d, expected "
					 "to be non-artificial" % (appName, val, id) )
				lid += 1

		checkLoads( "baseapp", self._ids, self._loads )
		checkLoads( "cellapp", self._ids, self._loads )


		# manual.input( "Now watch for loads..." )

