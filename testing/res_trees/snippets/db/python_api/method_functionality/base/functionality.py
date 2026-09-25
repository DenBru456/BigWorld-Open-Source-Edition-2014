import BigWorld
import srvtest
from random import random

@srvtest.testSnippet
def testWriteToDB():
	"""
	Create a new entity and write it to the database
	"""
	
	global e
	global entityName
	entityName = "test%f" % ( random() )
	e = BigWorld.createEntity( "Simple", name = entityName )

	srvtest.assertNotEqual( e, None )

	def callback( a, b ):
		srvtest.assertTrue( e.databaseID != 0 )
		testWriteToDB_01()

	e.writeToDB( callback, True )


@srvtest.testStep
def testWriteToDB_01():
	""" Destroy a base entity """
	
	global e
	e.destroy()
	srvtest.assertTrue( e.isDestroyed )
	srvtest.assertTrue( e.databaseID != 0 )
	testWriteToDB_02()


@srvtest.testStep
def testWriteToDB_02():
	"""
	Check the existence an entity using its entity type 
	and database ID key
	"""

	global e

	def storeArg( arg ):
		srvtest.assertTrue( arg )
		testWriteToDB_03_1()

	BigWorld.lookUpBaseByDBID( "Simple", e.databaseID, storeArg )


@srvtest.testStep
def testWriteToDB_03_1():
	"""
	Create a new base entity from an existing entry in the database,
	using the existing entity's database ID.
	Trying to create the entity twice will result in the second call
	returning a mailbox to the entity created in the first.	
	"""
	
	global e

	def onCreateBase( base, dbID, wasActive ):
		global e
		srvtest.assertFalse( wasActive )
		srvtest.assertEqual( dbID, e.databaseID )
		e = base
		srvtest.assertEqual( e.className, "Simple" )
		testWriteToDB_03_2()

	BigWorld.createBaseFromDBID( "Simple", e.databaseID, onCreateBase )


@srvtest.testStep
def testWriteToDB_03_2():
	"""
	Continued from the previous step.
	"""

	srvtest.mark( "BigWorld.Base.createBaseFromDBID_2" )
	global e

	def onCreateBase( base, dbID, wasActive ):
		srvtest.assertTrue( wasActive )
		srvtest.assertEqual( dbID, e.databaseID )
		srvtest.assertEqual( base.__class__.__name__, "BaseEntityMailBox" )
		testWriteToDB_03_3()

	BigWorld.createBaseFromDBID( "Simple", e.databaseID, onCreateBase )


@srvtest.testStep
def testWriteToDB_03_3():
	"""
	Continued from the previous step.
	"""

	global e

	def onCreateBase( base, dbID, wasActive ):
		srvtest.assertEqual( dbID, 0 )
		srvtest.assertEqual( base, None )
		testWriteToDB_04_1()

	BigWorld.createBaseFromDBID( "Simple", 123456, onCreateBase )


@srvtest.testStep
def testWriteToDB_04_1():
	"""
	Create a new base entity from an existing entry in the database,
	using the existing entity's name. Trying to create the entity twice
	will result in the second call returning a mailbox to the entity
	created in the first.
	"""

	global e
	global entityName

	e.destroy()

	def onCreateBase( base, dbID, wasActive ):
		global e
		srvtest.assertFalse( wasActive )
		srvtest.assertEqual( dbID, e.databaseID )
		e = base
		srvtest.assertEqual( e.className, "Simple" )
		testWriteToDB_04_2()

	BigWorld.createBaseFromDB( "Simple", entityName, onCreateBase )


@srvtest.testStep
def testWriteToDB_04_2():
	"""
	Continued from the previous step.
	"""

	global e
	global entityName

	def onCreateBase( base, dbID, wasActive ):
		global e
		srvtest.assertTrue( wasActive )
		srvtest.assertEqual( dbID, e.databaseID )
		srvtest.assertEqual( base.__class__.__name__, "BaseEntityMailBox" )
		testWriteToDB_04_3()

	BigWorld.createBaseFromDB( "Simple", entityName, onCreateBase )


@srvtest.testStep
def testWriteToDB_04_3():
	"""
	Continued from the previous step.
	"""

	global e

	def onCreateBase( base, dbID, wasActive ):
		srvtest.assertEqual( dbID, 0 )
		srvtest.assertEqual( base, None )
		testWriteToDB_05_1()

	BigWorld.createBaseFromDB( "Simple", "gibberish", onCreateBase )


@srvtest.testStep
def testWriteToDB_05_1():
	"""
	Find an entity using its entity type and database ID key.
	Also try to find entities that don't exist, using the same method.
	"""

	global e

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg.__class__.__name__, "BaseEntityMailBox" )
		srvtest.assertEqual( arg.id, e.id )
		testWriteToDB_05_2()

	BigWorld.lookUpBaseByDBID( "Simple", e.databaseID, storeArg )


@srvtest.testStep
def testWriteToDB_05_2():
	"""
	Continued from the previous step.
	"""

	global e

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg, True )
		testWriteToDB_05_3()

	BigWorld.lookUpBaseByDBID( "Simple", 123456, storeArg )


@srvtest.testStep
def testWriteToDB_05_3():
	"""
	Continued from the previous step.
	"""

	global e

	def storeArg( arg ):
		pass

	try:
		BigWorld.lookUpBaseByDBID( "Simple", 0, storeArg )
		srvtest.assertTrue( False )	
	except ValueError:
		testWriteToDB_06_1()


@srvtest.testStep
def testWriteToDB_06_1():
	"""
	Find an entity using its entity type and name. 
	Also try to find entities that don't exist, using the same method.
	"""

	global e
	global entityName

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg.__class__.__name__, "BaseEntityMailBox" )
		srvtest.assertEqual( arg.id, e.id )
		testWriteToDB_06_2()

	BigWorld.lookUpBaseByName( "Simple", entityName, storeArg )


@srvtest.testStep
def testWriteToDB_06_2():
	"""
	Continued from the previous step.
	"""

	global e
	global entityName

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg, False )
		testWriteToDB_07_1()

	BigWorld.lookUpBaseByName( "Simple", "gibberish", storeArg )


@srvtest.testStep
def testWriteToDB_07_1():
	"""
	Make MySQL queries directly to the database, and ensure 
	the resulting data is correct. 
	Try both single queries and multiple queries in a single call.
	"""

	global e

	def setFirstArg( arg, affectedRows, error ):
		global e
		srvtest.assertTrue( str( e.databaseID ) == arg[0][0] )
		testWriteToDB_07_2()

	query = "select id from tbl_Simple where id = %d" % e.databaseID
	BigWorld.executeRawDatabaseCommand( query, setFirstArg )


@srvtest.testStep
def testWriteToDB_07_2():
	"""
	Continued from the previous step.
	"""

	global e
	global entityName

	def setFirstArg( arg, affectedRows, error ):
		global e
		global entityName
		srvtest.assertTrue( entityName == arg[0][0] )
		testWriteToDB_07_3()

	query = "select sm_name from tbl_Simple where sm_name = '%s'" % entityName
	BigWorld.executeRawDatabaseCommand( query, setFirstArg )


@srvtest.testStep
def testWriteToDB_07_3():
	"""
	Continued from the previous step.
	"""

	global e
	global entityName

	def setFirstArg( arg ):
		global e
		global entityName
		print "[bwtest] arg = ", str( arg )
		srvtest.assertTrue( str( e.databaseID ) == arg[0][0][0][0] )
		srvtest.assertTrue( entityName == arg[1][0][0][0] )
		testWriteToDB_08_1()

	query = "select id from tbl_Simple where id = %d; " \
		 "select sm_name from tbl_Simple where sm_name = '%s'" % \
		 ( e.databaseID, entityName )
	BigWorld.executeRawDatabaseCommand( query, setFirstArg )


@srvtest.testStep
def testWriteToDB_08_1():
	"""
	Delete an entity from the database. 
	Try to do this before and after destroying it, and try to delete it twice.
	"""

	global e
	global entityName

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg.__class__.__name__, "BaseEntityMailBox" )
		e.destroy()
		testWriteToDB_08_2()

	BigWorld.deleteBaseByDBID( "Simple", e.databaseID, storeArg )


@srvtest.testStep
def testWriteToDB_08_2():
	"""
	Continued from the previous step.
	"""

	global e
	global entityName

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg, True )
		testWriteToDB_08_3()

	BigWorld.deleteBaseByDBID( "Simple", e.databaseID, storeArg )


@srvtest.testStep
def testWriteToDB_08_3():
	"""
	Continued from the previous step.
	"""

	global e
	global entityName

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg, True )
		testWriteToDB_08_4()

	BigWorld.lookUpBaseByDBID( "Simple", e.databaseID, storeArg )


@srvtest.testStep
def testWriteToDB_08_4():
	"""
	Continued from the previous step.
	"""

	global e
	global entityName

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg, False )
		testWriteToDB_08_5()

	BigWorld.lookUpBaseByName( "Simple", entityName, storeArg )


@srvtest.testStep
def testWriteToDB_08_5():
	"""
	Continued from the previous step.
	"""

	global e
	global entityName

	def storeArg( arg ):
		global e
		srvtest.assertEqual( arg, False )
		srvtest.finish()

	BigWorld.deleteBaseByDBID( "Simple", e.databaseID, storeArg )

