from bwtest import TestCase
from helpers.cluster import ClusterController
from primitives import mysql


TABLE_NAME = "tbl_PersistentEntity"
PROP_NAME = "singleIndexTest"

INDEX_SHOW_QUERY = """
	SHOW INDEX IN %s WHERE Column_name = 'sm_%s'
	""" % (TABLE_NAME, PROP_NAME)

INDEX_CREATE_QUERY = """
	CREATE INDEX RedundantIndex ON %s (sm_%s)
	""" % (TABLE_NAME, PROP_NAME)

INDEX_DROP_QUERY = """
	DROP INDEX %sIndex ON %s
	""" % (PROP_NAME, TABLE_NAME)


class SingleIndexTest( TestCase ):

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		self.cc.clean()


	def numIndexes( self ):
		return len( mysql.executeSQL( INDEX_SHOW_QUERY ) )


	def runTest( self ):
		"""
		SyncDB should not index a column if already indexed
		"""

		# Start with BW schema
		self.cc.syncDB()
		self.assertEqual( self.numIndexes(), 1 )

		# Drop BW index or hand crafted on
		mysql.executeSQL( INDEX_DROP_QUERY )
		self.assertEqual( self.numIndexes(), 0 )

		mysql.executeSQL( INDEX_CREATE_QUERY )
		self.assertEqual( self.numIndexes(), 1 )

		# Re-sync should respect hand crafted index
		self.cc.syncDB()
		self.assertEqual( self.numIndexes(), 1 )
