from bwtest import TestCase
from helpers.cluster import ClusterController
from primitives import mysql


ENTITY_DEF_FILE = "scripts/entity_defs/PersistentEntity.def"

INDEX_SHOW_QUERY = """
SHOW INDEX IN tbl_PersistentEntity WHERE Column_name = 'sm_myIndex'
"""

ENTITY_DEF = """
<root>
	<Properties>
		<myIndex>
			<Type>		INT32			</Type>
			<Flags>		OTHER_CLIENTS	</Flags>
			<Default>	0				</Default>
			<Persistent> true			</Persistent>
			<Indexed> 	%s			</Indexed>
		</myIndex>
	</Properties>
</root>
"""


class CreateRemoveIndexTest( TestCase ):

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		self.cc.clean()


	def numIndexes( self ):
		return len( mysql.executeSQL( INDEX_SHOW_QUERY ) )


	def mangleEntityDef( self, isIndexed ):

		def mangleFunc( inputFile, outputFile ):
			outputFile.write( ENTITY_DEF % isIndexed )

		self.cc.mangleResTreeFile( ENTITY_DEF_FILE, mangleFunc )


	def runTest( self ):

		# Initial sync, index created when table created
		self.mangleEntityDef( True )
		self.cc.syncDB()
		self.assertEqual( self.numIndexes(), 1 )

		# Delete index
		self.mangleEntityDef( False )
		self.cc.syncDB()
		self.assertEqual( self.numIndexes(), 0 )

		# Create index
		self.mangleEntityDef( True )
		self.cc.syncDB()
		self.assertEqual( self.numIndexes(), 1 )
