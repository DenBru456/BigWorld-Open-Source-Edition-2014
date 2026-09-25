import bwtest
from helpers.cluster import ClusterController


class TestLookUpBaseByDBID( bwtest.TestCase ):

	def setUp( self ):
		self.cc = ClusterController( [ "simple_space/res" ] )
		self.cc.start()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def lookUp( self, dbID ):
		snippet = """
		def onLookUp( arg ):
			srvtest.finish( (
				arg.__class__.__name__ == "BaseEntityMailBox",
				arg == True) )

		BigWorld.lookUpBaseByDBID( "Simple", %s, onLookUp )
		""" % dbID

		isMailBox, isTrue = self.cc.sendAndCallOnApp(
				"baseapp", snippet = snippet )

		return isMailBox, isTrue


	def runTest( self ):
		"""
		This test looks up:
		1) Checked out entity
		2) Checked in existing entity
		3) Non existing entity
		"""

		# Create checked out entity
		snippet = """
		def onWriteToDB( success, entity ):
			print success
			srvtest.finish( (entity.id, entity.databaseID) )

		import uuid
		entity = BigWorld.createEntity( "Simple", name = str( uuid.uuid4() ) )
		entity.writeToDB( onWriteToDB )
		"""

		id, dbID = self.cc.sendAndCallOnApp( "baseapp", snippet = snippet )
		self.assertNotEqual( dbID, 0, "Entity not allocated DBID" )

		# Look up checked out entity
		isMailBox, isTrue = self.lookUp( dbID )
		self.assertTrue( isMailBox )

		# Check in entity
		snippet = """
		BigWorld.entities[%s].destroy()
		srvtest.finish()
		""" % id
		self.cc.sendAndCallOnApp( "baseapp", snippet = snippet )

		# Look up checked in entity
		isMailBox, isTrue = self.lookUp( dbID )
		self.assertFalse( isMailBox, "Got mailbox, expecting True" )
		self.assertTrue( isTrue )

		# Look up non existing entity
		isMailBox, isTrue = self.lookUp( dbID + 1 )
		self.assertFalse( isMailBox, "Got mailbox, expecting True" )
		self.assertTrue( isTrue )
