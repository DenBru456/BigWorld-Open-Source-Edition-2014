from bwtest import TestCase
from bwtest import log
from bwtest import config

from helpers.cluster import ClusterController
from helpers.command import Command

import fixtures
import time
import os
import copy

class TestMLFlushHostNames( TestCase ):

	description = """
	This tests that IP/HostName pairings are updated when a flush command is
	sent to MessageLogger
	"""

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )

	def tearDown( self ):
		if hasattr( self, "customML" ):
			self.customML.stop()
		if hasattr( self, "cc" ):
			self.cc.stop()
			self.cc.clean()
		

	def _modifyHostFile( self, filePath ):

		f = open( filePath )
		storedLines = [ line.split(' ') for line in f.readlines() ]
		f.close()
		
		self.originalStoredLines = copy.deepcopy( storedLines )
		
		# Modify first hostname entry to be the actual ip
		storedLines[0][1] = self.originalStoredLines[0][0] + "\n"

		# Modify second hostname to be a non-existant hostname
		storedLines[1][1] = "FakeHost123\n"

		f = open ( filePath, 'w' )
		for line in storedLines:
			f.write( "%s %s" )
		f.close()

	def _compareHostFiles( self, filePath ):

		f = open( filePath )
		storedLines = [ line.split(' ') for line in f.readlines() ]
		f.close()

		results = [x for x in self.originalStoredLines if x not in storedLines]

		if results:
			self.fail( "New and original hostfiles don't match after flush" )

	def runTest( self ):

		self.customML = fixtures.CustomMessageLogger()
		self.cc.start()

		# Start a proc on a second machine to ensure that we have at least
		# two hosts in the hostnames file
		self.cc.startProc( "baseapp", machineIdx = 1 )
		hostnameFilePath = os.path.join( self.cc.messageLogger.dir,
			"hostnames" )

		# Stop the generic MessageLogger
		self.cc.messageLogger.stop()

		log.progress( "Modifying the hostnames file" )
		self._modifyHostFile( hostnameFilePath )

		cmd = Command()
		# Copy hostnames somewhere safe as ML will blow away folder on startup
		cmd.call( "cp %s/hostnames /tmp/hostnames" % self.cc.messageLogger.dir )

		self.customML.start()
		# Need to give MessageLogger enough time to create required files
		time.sleep(3)
		cmd.call( "mv /tmp/hostnames %s/hostnames" % self.cc.messageLogger.dir )

		log.progress( "Triggering MessageLogger flush" )
		cmd.call( "kill -USR1 $(pgrep message_logger)" )

		log.progress( "Comparing hostname files to ensure matching" )
		self._compareHostFiles( hostnameFilePath )

		log.progress( "Checking ML log for successful flush log output" )

		expectedOutput = [
			"validating %s with hostname %s" % ( self.originalStoredLines[0][0],
			self.originalStoredLines[0][1] ), "validating %s with hostname %s" %
			( self.originalStoredLines[1][0], self.originalStoredLines[1][1] ) ]

		if not fixtures.checkMLLogFile( self.customML.mlLogs, expectedOutput ):
			self.fail( "Flush logs success message missing in logs: %s" %
					logLine )