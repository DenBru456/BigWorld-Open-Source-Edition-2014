import BigWorld
import srvtest

@srvtest.testSnippet
def giveCellToAvatar( spaceID, position ):
	avatars = [e for e in BigWorld.entities.values() if e.__class__.__name__ == 'Avatar']
	srvtest.assertEqual( 1, len( avatars ), "Not exactly one Avatar on BaseApp" )
	entity = avatars[ 0 ]
	
	# TODO: Give Avatar a proper wait-for-cell-and-callback.
	def onGetCell():
		srvtest.finish( entity.id )
		del entity.onGetCell
	
	srvtest.assertFalse( hasattr( entity, "onGetCell" ), "Avatar has onGetCell method" )
	entity.onGetCell = onGetCell
	
	entity.cellData[ "position" ] = position
	if spaceID is None:
		entity.createInNewSpace()
	else:
		entity.cellData[ "spaceID" ] = spaceID
		entity.createCellEntity()
	srvtest.assertTrue( entity.hasCell, "Avatar does not have a Cell entity" )
	# srvtest.finish( entity.id ) will be triggered when the Base _really_ has a cell

@srvtest.testSnippet
def createEntity( spaceID, entityType, position):
	entity = BigWorld.createBaseLocally( "%s" % entityType)

	entity.cellData[ "position" ] = position
	if spaceID is None:
		entity.createInNewSpace()
	else:
		entity.cellData[ "spaceID" ] = spaceID
		entity.createCellEntity()
	srvtest.finish( entity.id )
