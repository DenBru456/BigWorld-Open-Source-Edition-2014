import BigWorld
import srvtest

@srvtest.testSnippet
def validateEntitySpacePosition( entityID, position ):
	srvtest.assertTrue( BigWorld.entities.has_key( entityID ), "Entity not found" )
	entity = BigWorld.entities[ entityID ]
	srvtest.assertTrue( entity.isReal(), "Entity not real on expected CellApp" )
	entityPos = ( entity.position.x, entity.position.y, entity.position.z )
	srvtest.assertEqual( position, entityPos, "Entity is out of position" + str(entityPos) )
	srvtest.finish( entity.spaceID )
	
@srvtest.testSnippet
def entityMoveToPosition( entityID, position, acceleration, maxSpeed ):
	srvtest.assertTrue( BigWorld.entities.has_key( entityID ), "Entity not found" )
	entity = BigWorld.entities[ entityID ]
	srvtest.assertTrue( entity.isReal(), "Entity is a real on expected CellApp" )
	
	srvtest.finish( entity.accelerateToPoint( position, acceleration, maxSpeed ) )
	

@srvtest.testSnippet
def entityMoveImmediately( entityID, oldPosition, position):
	srvtest.assertTrue( BigWorld.entities.has_key( entityID ), "Entity not found" )
	entity = BigWorld.entities[ entityID ]
	srvtest.assertTrue( entity.isReal(), "Entity is a real on expected CellApp" )
	
	entityPos = ( entity.position.x, entity.position.y, entity.position.z )
	srvtest.assertEqual( oldPosition, entityPos, "Entity is not at oldPosition" )
	
	entity.position = position
	
	entityPos = ( entity.position.x, entity.position.y, entity.position.z )
	srvtest.assertEqual( position, entityPos, "Entity is out of position" )
	srvtest.finish()
	

@srvtest.testSnippet
def entityDestroy( entityID, oldPosition):
	srvtest.assertTrue( BigWorld.entities.has_key( entityID ), "Entity not found" )
	entity = BigWorld.entities[ entityID ]
	srvtest.assertTrue( entity.isReal(), "Entity is a real on expected CellApp" )
	
	entityPos = ( entity.position.x, entity.position.y, entity.position.z )
	srvtest.assertEqual( oldPosition, entityPos, "Entity is out of position" )
	
	entity.destroy()
	
	srvtest.finish()