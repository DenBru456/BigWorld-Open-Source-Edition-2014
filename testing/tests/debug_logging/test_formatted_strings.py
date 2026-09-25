from bwtest import TestCase
from bwtest import log
from bwtest import config
from primitives import locallog

from helpers.cluster import ClusterController
from helpers.command import Command

import os
import time
import re

class TestFormattedStrings( TestCase ):

	description = """
	The test detects that a specific log message does not appear in mlcat.py
	--strings. Additionally there was a fail case where the log viewer
	tried to interpret the specially formatted strings with characters such as 
	%s resulting in "<null>" as opposed to "%s".
	"""
	LOG_MESSAGE = "ThisShouldNotAppearUsingMLCat"

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )

	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

	def runTest( self ):

		self.cc.start()

		snippet = """
		import bwdebug as bw
		bw.INFO_MSG( "%s" )
		srvtest.finish()
		""" % self.LOG_MESSAGE

		self.cc.sendAndCallOnApp( "baseapp", None, snippet )
		time.sleep( 3 )
		
		searchResults = locallog.grepLastServerLog( self.LOG_MESSAGE,
			process = "BaseApp" )

		self.assertTrue( searchResults != None,
			"%s is not found in the logs" % self.LOG_MESSAGE )

		mlcatPath = os.path.join( config.CLUSTER_BW_ROOT,
			config.BIGWORLD_FOLDER,
			"tools/bigworld/server/message_logger/mlcat.py" )

		mlcatCommand = " --strings %s " % ( self.cc.messageLogger.dir )
		
		cmd = Command();
		cmd.call( mlcatPath + mlcatCommand )
		rawResult = cmd.getLastOutput()

		finalResult = re.findall( self.LOG_MESSAGE, rawResult[0] )

		self.assertFalse( finalResult, "mlcat.py --strings found a match" )

		snippet = """
		import bwdebug as bw
		bw.INFO_MSG( "%s\\n" )
		srvtest.finish()
		"""

		self.cc.sendAndCallOnApp( "baseapp", None, snippet )

		searchResults = locallog.grepLastServerLog( "%s", process = "BaseApp" )

		self.assertTrue( searchResults != None, "'%s' not found in the logs" )