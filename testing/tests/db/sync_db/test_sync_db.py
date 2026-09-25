import os

from bwtest import TestCase, config
from helpers.cluster import ClusterController
from primitives import mysql


class TestAddRemovePersistentProperty( TestCase ):


	tags = []
	name = "Synchronising Persistent Properties"
	description = "Adding and removing persistent properties"

	RES_PATH = config.TEST_ROOT + "/res_trees/simple_space/res"

	persistent_entity_def = """
<root>
	<Properties>
		<ownerID>
			<Type>		INT32			</Type>
			<Flags>		OTHER_CLIENTS	</Flags>
			<Default>	0				</Default>
		</ownerID>
	</Properties>
</root>
"""
	def tearDown( self ):
		self._cc.clean()


	def runTest( self ):
		def editorFunction(inputFile, outputfile):
			outputfile.write( self.persistent_entity_def )
		
		self._cc = ClusterController( self.RES_PATH )
		self._cc.mangleResTreeFile( "scripts/entity_defs/PersistentEntity.def", 
									editorFunction)
		self._cc.syncDB()
		result = mysql.executeSQL( "DESCRIBE tbl_PersistentEntity" )
		columns = [ x[0] for x in result ]
		self.assertFalse( "sm_persistentProp" in columns, 
						"PersistentEntity has removed property after sync_db" )

		self._cc.clean()
		self._cc = ClusterController( self.RES_PATH )
		self._cc.syncDB()
		result = mysql.executeSQL( "DESCRIBE tbl_PersistentEntity" )
		columns = [ x[0] for x in result ]
		self.assertTrue( "sm_persistentProp" in columns, 
			"PersistentEntity doesn't have replaced property after sync_db" )
		result = mysql.executeSQL( "SHOW TABLES" )
		columns = [ x[0] for x in result ]


class TestAddRemovePersistentEntity( TestCase ):


	tags = []
	name = "Synchronising Persistent Entity"
	description = "Adding and removing persistent entities"

	RES_PATH = config.TEST_ROOT + "/res_trees/simple_space/res"


	def tearDown( self ):
		self._cc.clean()


	def runTest( self ):

		self._cc = ClusterController( 
									[self.RES_PATH] )
		def lineEditorFunction(line):
			if line.strip() == "<PersistentEntity/>":
				line = "\n"
			return line
		self._cc.lineEditResTreeFile( "scripts/entities.xml", lineEditorFunction)
		self._cc.syncDB()
		result = mysql.executeSQL( "SHOW TABLES" )
		tables = [ x[0] for x in result ]
		self.assertFalse( "tbl_PersistentEntity" in tables, 
						"PersistentEntity still exists" )

		self._cc = ClusterController( self.RES_PATH )
		self._cc.syncDB()
		result = mysql.executeSQL( "SHOW TABLES" )
		tables = [ x[0] for x in result ]
		self.assertTrue( "tbl_PersistentEntity" in tables, 
			"PersistentEntity does not exist" )
