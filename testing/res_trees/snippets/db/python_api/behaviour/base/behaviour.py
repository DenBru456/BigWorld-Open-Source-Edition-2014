import BigWorld
import srvtest
from array import array
from random import random

# -----------------------------------------------------------------------
# Snippets for TestPersistent

@srvtest.testSnippet
def snippetPersistent_1( spaceID ):
	"""
	Create both base and cell parts of a TestEntity
	"""
	
	entityName = "test%f" % (random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
	e.cellData[ 'spaceID' ] = spaceID
	e.createCellEntity()
	srvtest.finish( e.id ) 


@srvtest.testSnippet
def snippetPersistent_3( entityID ):
	"""
	Write entity to DB
	"""

	e = BigWorld.entities[ entityID ]

	def callback( result, b ):
		srvtest.assertTrue( result )
		srvtest.finish( e.databaseID ) 

	e.writeToDB( callback, True )


@srvtest.testSnippet
def snippetPersistent_4( spaceID, databaseID ):
	"""
	Create cell entity after the base entity is read from DB
	"""
	
	e = None

	for ent in BigWorld.entities.values():
		if ent.databaseID == databaseID:
			e = ent
			break

	e.cellData[ 'spaceID' ] = spaceID
	e.createCellEntity()
	srvtest.finish( e.id ) 


# -----------------------------------------------------------------------
# Snippets for TestBackup

@srvtest.testSnippet
def snippetBackup_1():
	"""
	Change an entity's property data - can be persistent or non-persistent.
	"""
	
	entityName = "test%f" % (random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
	e.array = [5, 4, 3, 2, 1]
	e.writeToDB();
	e.shouldAutoBackup = False;
	e.array = [7, 8, 9]
	srvtest.finish( e.id ) 

	
@srvtest.testSnippet
def snippetBackup_2( entityID ):
	"""
	Check the entity is restored on the second baseapp
	"""
	
#	print "[bwtest] entityID = ", entityID
	e = BigWorld.entities[ entityID ]

#	print "[bwtest] checking..."
	
	srvtest.assertEqual( array( 'i', e.array ), array( 'i', [5, 4, 3, 2, 1] ) )
	print "[bwtest] finishing..."
	srvtest.finish() 

	
# -----------------------------------------------------------------------
# Snippets for TestBackupFromCell

@srvtest.testSnippet
def snippetBackupFromCell_1( spaceID ):
	"""
	Change an entity's property data - can be persistent or non-persistent.
	"""
	
	entityName = "test%f" % (random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
	e.array = [1, 1, 3, 2, 2]
	e.cellData[ 'spaceID' ] = spaceID
	e.createCellEntity() 

	srvtest.finish( e.id ) 

	
@srvtest.testSnippet
def snippetBackupFromCell_3( entityID ):
	"""
	Check the entity is restored on the second baseapp
	"""
	
#	print "[bwtest] entityID = ", entityID
	e = BigWorld.entities[ entityID ]

#	print "[bwtest] checking..."
	
	srvtest.assertEqual( array( 'i', e.array ), array( 'i', [1, 1, 3, 2, 2] ) )
#	print "[bwtest] finishing..."
	srvtest.finish() 

	
# -----------------------------------------------------------------------
# Snippets for TestBackupBaseOnly

@srvtest.testSnippet
def snippetBackupBaseOnly_1():
	def resCallback( result, ent ):
	    srvtest.assertTrue( result )
	    srvtest.finish()

	entityName = "test%f" % (random())
	e = BigWorld.createEntity( "Simple", name = entityName )
	e.writeToDB( resCallback )
	
	
# -----------------------------------------------------------------------
# Snippets for TestBackupNoCellEntity

@srvtest.testSnippet
def snippetBackupNoCellEntity_1( spaceID ):
	"""
	Create both base and cell parts of an entity
	"""

	entityName = "test%f" % (random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
	e.cellData[ 'spaceID' ] = spaceID
	e.createCellEntity() 

	srvtest.finish( e.id ) 

	
@srvtest.testSnippet
def snippetBackupNoCellEntity_3( entityID ):
	"""
	Destroy cell entity and write to DB
	"""

	e = BigWorld.entities[ entityID ]

#	e.destroyCellEntity()

	def callback( result, ent ):
		srvtest.assertTrue( result )
		srvtest.finish( e.databaseID ) 

	e.writeToDB( callback, True )
	
	
@srvtest.testSnippet
def snippetBackupNoCellEntity_4( databaseID, spaceID ):
	"""
	Create a cell entity again after restart
	"""
	
	e = None

	for ent in BigWorld.entities.values():
		if ent.databaseID == databaseID:
			e = ent
			break
	
	srvtest.assertNotEqual( e, None )

	e.cellData['spaceID'] = spaceID
	e.createCellEntity() 

	srvtest.finish( e.id ) 
