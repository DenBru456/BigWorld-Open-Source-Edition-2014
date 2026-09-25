import BigWorld
import srvtest


@srvtest.testSnippet
def createEntityInNewSpace():
	e = BigWorld.createBase( 'TestEntity' )
	e.createInNewSpace()
	srvtest.finish( e.id )


@srvtest.testSnippet
def destroyEntityInNewSpace( id ):
	e = BigWorld.entities[ id ]
	e.destroyCellEntity()
	srvtest.finish()