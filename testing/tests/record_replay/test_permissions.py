from bwtest import TestCase
from helpers.cluster import ClusterController
from helpers.timer import runTimer

import os


RECORDING = "recordings/permissions_test.rec"


class PermissionsTest( TestCase ):

	def setUp( self ):

		# Start cluster
		self.cc = ClusterController( "record_replay/res" )
		self.cc.start()

		# Delete existing recording
		self.recording = self.cc.findInResPath( RECORDING )
		if self.recording:
			os.remove( self.recording )
			self.recording = None

		# Create recorder
		snippet = """
		recorder = BigWorld.createEntity( "TestRecorder" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", None, snippet )

		# Start recording
		self.cc.callWatcher(
				"serviceapp", "setUpRecording", None, 2, RECORDING, True, "" )

		# Check recording has started
		def findRecording():
			self.recording = self.cc.findInResPath( RECORDING )
			return self.recording != None 
		runTimer( findRecording, timeout = 10 )
		self.assertFalse( self.isFinalised() )


	def tearDown( self ):
		if hasattr( self, "cc" ):
			self.cc.stop()
			self.cc.clean()


	def isFinalised( self ):
		"""
		Determines whether the recording has been finalised by checking
		whether the recorded reply file has been set to read-only.
		"""

		# There seems to be some delay in setting file permissions over NFS.
		# As a result, using os.access or os.stat to check the file
		# permissions immediately can lead to incorrect results.
		#
		# The solution is to try and open the file with write access instead.
		# This seems to force NFS to synchronise the file permissions and
		# yield correct results.

		try:
			if not os.path.exists( self.recording ):
				return False

			fd = os.open( self.recording, os.O_WRONLY)
			os.close( fd )
			return False

		except OSError:
			return True
		

class FinaliseOnShutDownTest( PermissionsTest ):

	def runTest( self ):
		"""
		Recording is read only after server shut down
		"""

		self.cc.stop()
		runTimer( self.isFinalised, timeout = 10 )


class FinaliseOnRetireTest( PermissionsTest ):

	def runTest( self ):
		"""
		After ServiceApp retirement, recording is writable if there is
		a back up.
		"""

		# Enable backup
		self.cc.startProc( "serviceapp" )

		# Determine primary
		snippet = """
		isPrimary = bool( BigWorld.localServices.values()[0].backups )
		srvtest.finish( isPrimary )
		"""
		isApp01Primary = self.cc.sendAndCallOnApp( "serviceapp", 1, snippet )

		# Retire primary
		if isApp01Primary:
			self.cc.retireProc( "serviceapp", 1 )
		else:
			self.cc.retireProc( "serviceapp", 2 )

		runTimer( self.isFinalised, timeout = 10, checker = lambda ret: ret == False )
