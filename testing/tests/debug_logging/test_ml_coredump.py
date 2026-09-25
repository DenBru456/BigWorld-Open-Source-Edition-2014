from bwtest import TestCase
from bwtest import log
from bwtest import config
from bwtest import manual

from helpers.cluster import ClusterController
from helpers.command import Command, CommandError, mkdir, copy
from helpers.timer import runTimer

import time
import os

class TestMLCoredump( TestCase ):
	
	name = "Test MessageLogger Coredump"
	description = """
	Tests that MessageLogger creates core dumps when required and that the
	core dumps have a valid stacktrace
	"""
	
	tags = [ "MANUAL" ]
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )

	def tearDown( self ):
		if hasattr( self, "cc" ):
			self.cc.clean()

	# This is to catch MessageLogger core dumps. It exists here locally instead
	# of cluster.py pending a discussion about the future of the way autotests
	# use MessageLogger. If we keep the current implementation then
	# Cluster._checkForCoreDumps should include a check for MessageLogger
	def _archiveMLCoreDump( self, corePath ):
		coredumpsPath = os.path.join( config.CLUSTER_BW_ROOT,
			config.BIGWORLD_FOLDER, config.SERVER_BINARY_FOLDER )
		mlBinaryPath = os.path.join( config.CLUSTER_BW_ROOT,
			config.BIGWORLD_FOLDER, config.TOOLS_BINARY_FOLDER )
		snapshotDirName = time.strftime( "core-snapshot-%Y%m%d-%H%M%S" )
		snapshotPath = coredumpsPath + os.sep + snapshotDirName
		binName = "message_logger"
		binFrom = os.path.join( mlBinaryPath, binName)
		binTo = snapshotPath + os.sep + binName
		dumpTo = snapshotPath + os.sep

		try:
			mkdir( snapshotPath )
		except CommandError:
			pass

		try:
			if not os.path.exists( binTo ):
				copy( binFrom, binTo )
		except CommandError:
			log.error( "ClusterController: failed to copy %s "
				"binary into %s", binFrom, snapshotPath + os.sep )

		try:
			copy( corePath, dumpTo )
		except CommandError:
			log.error( "ClusterController: failed to copy %s "
				"core dump into %s", dump, snapshotPath + os.sep )

		return dumpTo

	def runTest( self ):
		killAndDumpMLCommand = "kill -11 $(pgrep -u $(id -u) message_logger)"
		logLocation = os.path.join( self.cc.messageLogger.dir )
		findCommand = "find " + logLocation + " -name core.*"
		backtraceFile = os.path.join( self.cc._tempTree, "mlBacktrace.txt" )
		mlBinaryPath = os.path.join( config.CLUSTER_BW_ROOT,
			config.BIGWORLD_FOLDER, config.TOOLS_BINARY_FOLDER, "message_logger"
			)

		# Wait for MessageLogger to create it's folder
		runTimer( lambda: os.path.isdir( logLocation ),
			checker = lambda res: res == True, timeout = 10 )

		cmd = Command()
		# Kill the MessageLogger
		cmd.call( killAndDumpMLCommand )
		# Find the core dump
		cmd.call( findCommand )
		coreDumpsFound = cmd.getLastOutput()
		
		self.assertNotEqual( coreDumpsFound, None,
			"No MessageLogger core dumps found " )

		log.debug( "gdb %s %s --ex bt --ex quit > %s.txt 2>&1" \
			% ( mlBinaryPath, coreDumpsFound[0].rstrip(), backtraceFile ) )
		cmd.call( "gdb %s %s --ex bt --ex quit > %s 2>&1"  \
			% ( mlBinaryPath, coreDumpsFound[0].rstrip(), backtraceFile ) )

		self.assertTrue( os.path.isfile( backtraceFile ),
			"No gdb backtrace file exists" )

		finalOutput = ""
		file = open( backtraceFile, "r" )
		lines = file.readlines()
		for line in lines:
			finalOutput += line
		file.close()

		userMessage = ("%s \nPlease look at the stacktrace above. Does the " \
		"stacktrace look fine to you?" % ( finalOutput ) )

		res = manual.input_passfail( userMessage )
		
		if not res:
			dumpLocation = self._archiveMLCoreDump( coreDumpsFound[0].rstrip() )
			self.fail( "User failed test. Core dump and binary have been " \
				"copied into %s for further analysis" % ( dumpLocation ) )