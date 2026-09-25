from bwtest import TestCase
from bwtest import log
from bwtest import config
from primitives import locallog

from helpers.cluster import ClusterController
from helpers.timer import runTimer

import time
import os
import re

class TestFilteringSuppression( TestCase ):


	name = "Test Log Filtering/Suppression"
	description = """
	Tests that when message patterns are specified, log spam from those messages
	are suppressed and appropriately noted in the logs.
	"""
	
	RES_PATH = "stress/res"
	
	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		self._cc.setConfig( "shouldFilterLogSpam", "true" )
		self._cc.setConfig( "logSpamPatterns/pattern", "ChunkLoader:" )
		self._cc.setConfig( "logSpamThreshold", "0" )
		self._cc.setConfig( "logSpamFiltersSummaries", "true" )

	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()

	def runTest( self ):
		self._cc.start()
		
		snippet = """
		e=BigWorld.createBaseAnywhere( "SpaceCreator",
		spaceDir = "/spaces/30x30" )
		srvtest.finish()
		"""
		log.info( "Creating the space" )
		self._cc.sendAndCallOnApp( "baseapp", None, snippet )
		
		log.progress( "Waiting for chunks to load" )
		runTimer( lambda: self._cc.getWatcherValue( "numSpacesFullyLoaded",
						"cellapp", 1 ), checker = lambda res: res == "1",
				timeout = 60 )
		log.progress( "Chunks loaded" )

		logMessage = "Suppressed [0-9]+ in last [0-9]+s: ChunkLoader:" \
					" Loaded chunk '%s'"
		
		log.progress( "Searching for the suppress message" )
		searchResults = locallog.grepLastServerLog( logMessage,
												process = "CellApp" )
		log.debug( "searchResults: %s ", searchResults )
		
		# Check if the message exists in the logs
		if not searchResults:
			self.fail( "ChunkLoader suppression messages not found in the log" )