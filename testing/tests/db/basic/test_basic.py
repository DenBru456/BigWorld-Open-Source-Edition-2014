import os
import sys
import bwtest
from helpers.cluster import ClusterController
import time
from random import random

from bwtest import config
from bwtest import log
from bwtest import manual


class TestBasicDBFunctionality( bwtest.TestCase ):
	name = "Basic DB functionality"
	description = """
	Simple DB operations on FantasyDemo server 
	"""

	tags = [ "MANUAL" ]


	RES_PATH = config.CLUSTER_BW_ROOT + "/game/res/fantasydemo"

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		
		def cleanup1():
			self._cc.clean()
		self.addCleanup( cleanup1 )
		self._cc.start()

		def cleanup2():
			self._cc.stop()
		self.addCleanup( cleanup2 )


	def tearDown( self ):
		self._cc.stop()

		self._cc.clean()


	def step1( self ):
		"""Login a FantasyDemo client"""

		msg = """
FantasyDemo server is running now.
Login a FantasyDemo client to the server and exit.
Remember the avatar name		
		"""
		res = manual.input_passfail( msg )
			
		self.assertTrue( res )
	
		
	def step2( self ):
		"""Login a FantasyDemo client with different username"""

		msg = """
Login a FantasyDemo client with a different username.
Use client console to add first avatar as a friend:
/addFriend 		
		"""
		res = manual.input_passfail( msg )
			
		self.assertTrue( res )
		
		res = manual.input_passfail( "Exit FantasyDemo client" ) 

		self.assertTrue( res )

		self._cc.stop()
		self._cc.start()


	def step3( self ):
		"""Check if the friend persists"""
		
		msg = """
Login a FantasyDemo client with the second username.
Use client console to list fiends
/listFriends
It should have the same friend as before.		
		"""
		res = manual.input_passfail( msg )

		self.assertTrue( res )
		