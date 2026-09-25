import time
import bwtest
from helpers.cluster import ClusterController

from test_common import *

class FileDescriptorsPerBotTest( bwtest.TestCase ):
	name = "Bot File Descriptor Usage"
	description = "Test bots file descriptor usage"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		self.cc.startProc( "bots", 1 )

		bots = self.cc.bots
		pid = bots.procs()[0].pid

		count1 = fileDescriptorsUsed( pid )

		# Add single bot
		bots.add( 1 )
		count2 = fileDescriptorsUsed( pid )
		FDsPerBot = count2 - count1

		bots.add( 55 )
		count3 = fileDescriptorsUsed( pid )
		self.assertEqual( count3, count2 + FDsPerBot*55 )


class FileDescriptorsLimitsTest( bwtest.TestCase ):
	name = "Bot File Descriptor Limit"
	description = "Test bots file descriptor limits"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		# Get FDs used by idle bots process
		self.cc.start()
		self.cc.startProc( "bots", 1 )

		bots = self.cc.bots
		pid = bots.procs()[0].pid
		idleFDs = fileDescriptorsUsed( pid )
		
		bots.add( 1 )
		botFDs = fileDescriptorsUsed( pid ) - idleFDs

		self.cc.stop()

		# Calculate limits
		maxFDOpen = 1024
		maxBots = int( ( maxFDOpen - idleFDs) / botFDs )

		# Start server with FD limits
		self.cc.setConfig( "maxOpenFileDescriptors", str( maxFDOpen ) )
		self.cc.start()
		self.cc.startProc( "bots", 1 )
		pid = bots.procs()[0].pid
		
		# Add max bots
		for i in range(4):
			bots.add( maxBots/4, timeout = 60 )
			self.assertTrue( fileDescriptorsUsed( pid ) < maxFDOpen, bots.numBots() )
			time.sleep( 2 )
		
