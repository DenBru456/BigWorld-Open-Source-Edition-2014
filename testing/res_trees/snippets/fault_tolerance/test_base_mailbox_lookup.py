import BigWorld
import srvtest
from twisted.internet import defer

ids = []
numBasesToWrite = 0
numBasesToLookUp = 0

def simpleEntities():
	return [e for e in BigWorld.entities.values() if e.className == "Simple"]


def onWriteToDB( success, entity ):
	global ids
	global numBasesToWrite

	if success:
		numBasesToWrite -= 1
		ids.append( (entity.id, entity.databaseID) )

	if not numBasesToWrite:
		srvtest.finish( ids )


@srvtest.testSnippet
def createBases( numBases ):
	global numBasesToWrite
	numBasesToWrite = numBases

	for i in range( numBases ):
		entity = BigWorld.createEntity( "Simple", name = "Simple%s" % i )
		entity.writeToDB( onWriteToDB )


@srvtest.testSnippet
def numSimpleEntities():
	srvtest.finish( len( simpleEntities() ) )


@srvtest.testStep
def onLookUpBase( mailbox ):
	nubAddr = BigWorld.getWatcher( "nub/address" )
	mailboxAddr = "%s:%s" % mailbox.address
	srvtest.assertTrue( mailboxAddr == nubAddr, msg='Expected %s, got %s' % (mailboxAddr, nubAddr) )

	global numBasesToLookUp
	numBasesToLookUp -= 1
	if not numBasesToLookUp:
		srvtest.finish()


@srvtest.testSnippet
def checkMailboxes():
	global numBasesToLookUp

	entities = simpleEntities()
	numBasesToLookUp = len( entities )
	
	if not numBasesToLookUp:
		srvtest.finish()

	for e in entities:
		print "Testing entity %r:%s" % ( e.databaseID, e.name )
		BigWorld.lookUpBaseByDBID( e.className, e.databaseID, onLookUpBase )
