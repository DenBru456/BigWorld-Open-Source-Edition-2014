import BigWorld
import srvtest
from array import array

# -----------------------------------------------------------------------
# Snippets for TestPersistent

@srvtest.testSnippet
def snippetWaitForSpace():
	import BWPersonality

	spaceID = BWPersonality.getSpaceID()
	if spaceID > 0:	
		srvtest.finish( spaceID )

	def callback( spaceID ):
		srvtest.finish( spaceID )

	BWPersonality.hookOnSpaceID( callback )



@srvtest.testSnippet
def snippetPersistent_2( entityID ):
	e = BigWorld.entities[ entityID ]
	e.cellArray = [1, 2, 3, 4, 5]
	srvtest.finish()


@srvtest.testSnippet
def snippetPersistent_5( entityID ):
	e = BigWorld.entities[ entityID ]
    		
	srvtest.assertEqual( array( 'i', e.cellArray ), array( 'i', [1, 2, 3, 4, 5] ) )
	srvtest.finish() 


# -----------------------------------------------------------------------
# Snippets for TestBackupFromCell

@srvtest.testSnippet
def snippetBackupFromCell_2( entityID ):
	"""
	Trigger a backup from cell
	"""
	
	e = BigWorld.entities[ entityID ]
	e.writeToDB()

	srvtest.finish() 
		
		

# -----------------------------------------------------------------------
# Snippets for TestBackupNoCellEntity

@srvtest.testSnippet
def snippetBackupNoCellEntity_2( entityID ):
	"""
	Modify cell data
	"""
	
	e = BigWorld.entities[ entityID ]

	e.cellArray = [5, 4, 3, 4, 5]

	srvtest.finish() 

		
@srvtest.testSnippet
def snippetBackupNoCellEntity_5( entityID ):
	"""
	Check if array data is preserved on cell entity
	"""
	
	e = BigWorld.entities[ entityID ]

	print "[bwtest] cellArray = ", e.cellArray
	srvtest.assertEqual( array('i', e.cellArray), array('i', [5, 4, 3, 4, 5] ) )

	srvtest.finish() 
		