import bwtest
from helpers.cluster import ClusterController
import time


BACKUP_PERIOD = 1
NUM_BASES = 50
NUM_BASEAPPS = 5

class BaseMailboxLookUpTest( bwtest.TestCase ):
	name = "Base mailbox look up test" 
	description = "Test mailbox look up of restored bases" 
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "baseApp/backupPeriod", str( BACKUP_PERIOD ) )

		self.cc.start()
		self.cc.startProc( "baseapp", NUM_BASEAPPS - 1 )

		for i in range( 1, NUM_BASEAPPS + 1 ):
			self.cc.loadSnippetModule(
					"baseapp", i, "fault_tolerance/test_base_mailbox_lookup" )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def step0( self ):
		"""Create bases"""
		self.cc.callOnApp( "baseapp", 1, "createBases", numBases = NUM_BASES )


	def step1( self ):
		"""Ensure backup period has elapsed"""
		time.sleep( BACKUP_PERIOD * 2 )

		# Kill first baseapp
		self.cc.killProc( "baseapp", 1 )

	def step2( self ):
		"""Check bases have been restored"""
		numBases = 0
		for i in range( 2, NUM_BASEAPPS + 1 ):
			numBases += self.cc.callOnApp( "baseapp", i, "numSimpleEntities" )
		self.assertEqual( numBases, NUM_BASES )


	def step3( self ):
		"""Check mailboxes of lookup results"""
		for i in range( 2, NUM_BASEAPPS + 1 ):
			self.cc.callOnApp( "baseapp", i, "checkMailboxes" )
