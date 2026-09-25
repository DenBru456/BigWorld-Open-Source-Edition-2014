from bwtest import TestCase
from bwtest import log
from bwtest import config

from helpers.cluster import ClusterController
from helpers.command import Command

import fixtures
import os
import time

class TestSeverityCommandFiltering( TestCase ):

	description = """
	Tests that MessageLogger is able to disable/enable logging of specific
	message types set on MessageLogger startup
	"""

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )

	def tearDown( self ):
		if hasattr( self, "customML" ):
			self.customML.stop()
		if hasattr( self, "cc" ):
			self.cc.stop()
			self.cc.clean()

	def runTest( self ):
		mlcatPath = os.path.join( config.CLUSTER_BW_ROOT,
			config.BIGWORLD_FOLDER,
			"tools/bigworld/server/message_logger/mlcat.py" )
		log.progress( "Stopping generic MessageLogger" )
		self.cc.messageLogger.stop()

		log.progress( "Starting MessageLogger with 'TRACE' and 'NOTICE'" \
		" messages ignored" )

		# We have to start MessageLogger through a custom cmd call due to
		# -NOTICE and -TRACE messages logging to console before -o and -e
		# take effect. It's messy but at the moment there's no alternative.

		self.customML = fixtures.CustomMessageLogger()
		self.customML.start( "-TRACE", "-NOTICE" )
		# Give MessageLogger time to startup
		time.sleep(3)

		log.progress( "Checking MessageLogger logs for appropriate output" )
		expectedOutput = [ "INFO: Ignoring logs with message priority 'TRACE'.",
			"INFO: Ignoring logs with message priority 'NOTICE'." ]

		if not fixtures.checkMLLogFile( self.customML.mlLogs, expectedOutput ):
			self.fail( "'Ignore logs' messages missing in logs: %s" %
					logLine )

		log.progress( "Checking that ML ignore severities works" )
		self.cc.start()

		# Trigger various message severities since they arn't guaranteed
		snippet = """
		import logging
		log = logging.getLogger( "AutoTest" )
		log.notice( "Test Notice" )
		log.trace( "Test Trace" )
		log.info( "Test Info" )
		log.error( "Test Error" )
		srvtest.finish()
		"""

		self.cc.sendAndCallOnApp( "baseapp", None, snippet )

		cmd = Command()
		cmd.call( "%s -s --severities=tn %s" %  ( mlcatPath,
			self.customML.dir) )
		result = cmd.getLastOutput()[0]

		if result:
			self.fail( "Results were found for TRACE/NOTICE severity" )

		cmd.call( "%s -s --severities=^tn %s" %  ( mlcatPath,
			self.customML.dir) )
		result = cmd.getLastOutput()[0]

		if not result:
			self.fail( "No logs with non TRACE/NOTICE severities were found" )

		self.cc.stop()
		self.customML.stop()

		log.progress( "Starting MessageLogger restricting logging to 'ERROR'" \
		" severity" )
		self.customML.start( "+ERROR" )
		# Give MessageLogger time to startup
		time.sleep(3)

		log.progress( "Checking MessageLogger logs for appropriate output" )
		expectedOutput = \
			"INFO: Restricting logging to message priority 'ERROR'."

		if not fixtures.checkMLLogFile( self.customML.mlLogs, expectedOutput ):
			self.fail( "'Restrict logs' messages missing in logs" )

		log.progress( "Checking that ML restrict severities works" )
		self.cc.start()

		self.cc.sendAndCallOnApp( "baseapp", None, snippet )

		cmd.call( "%s -s --severities=e %s" %  ( mlcatPath,
			self.customML.dir) )
		result = cmd.getLastOutput()[0]

		if not result:
			self.fail( "Results were not found for ERROR severity" )

		cmd.call( "%s -s --severities=^e %s" %  ( mlcatPath,
			self.customML.dir) )
		result = cmd.getLastOutput()[0]
		print result
		# We don't care about this message for this test step
		ignoreMessage = \
			"WARNING:  No server startup in log, starting from beginning"

		if result.replace( ignoreMessage, "" ).strip():
			self.fail( "Logs were found for non ERROR severities" )