from bwtest import TestCase
from bwtest import log
from bwtest import config
import os
#from os import path
from helpers.cluster import ClusterController
import time
import re
import string

class TestConfigurableLogs( TestCase ):

	name = "Test Configurable Logs"
	description = """
	Tests whether the core server processes plus bots can write logs to a 
	specified file. Also tests that severity levels work/appear as expected
	in these files.
	"""

	# The start time allowance to allow for the time when our Python command
	# gets the time, compared to when the server actually does start, in seconds
	START_TIME_ALLOWANCE = 60

	RES_PATH = "simple_space/res"

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )

	def tearDown( self ):
		try:
			self._f.close()
		except:
			log.info( "No file is open, so nothing to tear down" )
		self._cc.stop()
		self._cc.clean()

	def runTest( self ):
		
		# Holds the file name that the severity tests will use
		_severity_log_path = os.path.join( self._cc._tempTree,
										"SeverityOutputFile.log" )
		
		self._cc.start()
		self._cc.startProc( "bots" )

		# Test that the log files are created + header is correct for the
		# processes
		for app in ["baseapp", "dbapp", "cellapp", "serviceapp", "bots"]:
			log.progress( "Testing " + app )
			snippet = """
			import BigWorld
			import time
			BigWorld.localLogger = BigWorld.FileLogger( "%s",
			severities = ("INFO","CRITICAL","TRACE"),
			sources = ("SCRIPT","CPP"), openMode = "w")
			BigWorld.localLogger.enable = 1
			srvtest.finish( time.time() )
			""" % os.path.join( self._cc._tempTree, "%s.log" ) % app
			
			log.debug( os.path.join( self._cc._tempTree, "%s.log" ) % app )
			
			if app == "bots" or app == "dbapp":
				startTime = self._cc.sendAndCallOnApp( app, None, snippet)
			else:
				startTime = self._cc.sendAndCallOnApp( app, 1, snippet)
			
			self._readFileHeader( os.path.join( self._cc._tempTree, "%s.log" )
								% app, app, startTime )

		
		# Test modifying the severity level
		log.progress( "Testing the modification of severity levels" )
		self._cc.stop()
		self._cc.start()
		
		snippet = """
		import BigWorld
		BigWorld.localLogger = BigWorld.FileLogger( "%s",
		severities = ("INFO","CRITICAL","TRACE"), sources = ("SCRIPT","CPP"),
		openMode = "w")
		BigWorld.localLogger.enable = 1
		srvtest.finish()
		""" % _severity_log_path
		self._cc.sendAndCallOnApp( "baseapp", 1, snippet )

		snippet = """
		import BigWorld
		from bwdebug import CRITICAL_MSG
		CRITICAL_MSG( "This is a critical message" )
		BigWorld.localLogger.enable = 0
		srvtest.finish()
		"""
		
		self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		
		log.progress( "Checking if critical message exists in log file" )
		self._searchLogFile( _severity_log_path,
							"This is a critical message", True )
		
		log.progress( "Checking if modified severity levels are " \
					"what we expect" )
		# Test parameter change
		snippet = """
		import BigWorld
		BigWorld.localLogger.config( "%s", severities=("INFO",
		"ERROR","TRACE"), sources=("SCRIPT","CPP"), openMode="w")
		BigWorld.localLogger.enable = 1
		srvtest.finish( BigWorld.localLogger.severities )
		""" % _severity_log_path
		
		severityList = self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		
		log.debug( "Returned severity list is: %s", severityList )
		self.assertEqual( severityList, "TRACE;INFO;ERROR",
			"Severity list didn't match what we were expecting" )
		
		log.progress( "Checking that a log message that shouldn't appear" \
					" doesn't appear" )
		snippet = """
		from bwdebug import CRITICAL_MSG
		CRITICAL_MSG("Critical message number 2")
		srvtest.finish()
		"""
		
		self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		
		self._searchLogFile( _severity_log_path,
							"Critical message number 2", False)
		
		log.progress( "Testing setting an incorrect severity level" )
		snippet = """
		import BigWorld
		from bwdebug import ERROR_MSG
		result = False
		try:
			BigWorld.localLogger.config("%s",
			severities=("INFO"," ERROR ","TRACE"), sources=("SCRIPT","CPP"),
			openMode="w")
		except ValueError, e:
			result = True
			ERROR_MSG( "Failed to set logger config: %%s" %% ( e, ) )
		srvtest.finish(result)
		""" % _severity_log_path
		
		result = self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		self.assertTrue( result, "Traceback we were expecting did not occur" )

		self._searchLogFile( _severity_log_path ,
							"Failed to set logger config: " \
							"stringArrayToBits: ' ERROR ' is not valid, will " \
							"be ignored.", True )
		
	def _searchLogFile( self, filePath, message, expectExistance ):
		
		log.debug( "Passed in: " + filePath + " " + message )
		
		# Test that log file was created
		log.info( "Checking whether log file at " + filePath + " exists" )
		fileExists = os.path.isfile( filePath )
		self.assertTrue( fileExists, "Log file does not exist, test fails " \
						"without this file" )
		
		self._f = open( filePath, 'r' )
		
		# Potentially could be bad if the file is too big for memory
		fileData = self._f.read()
		
		searchResults = re.findall( message, fileData )
		log.debug( "searchResults: %s ", searchResults )
		# Check if the message exists in the logs
		if ( not searchResults and expectExistance == True ):
			self.fail( "Message that we were expecting was not found in " \
					"the logs" )
		elif ( searchResults and expectExistance == False ):
			self.fail( "Message that shouldn't be in the logs appears to be " \
					"in the logs" )
			
		self._f.close()

	def _readFileHeader( self, filePath, binaryName, processConsoleTime ):

		log.debug( "Passed in: filePath: %s binaryName: %s",
				filePath, binaryName )
		time.sleep( 30 )
		# Test that log file was created
		log.info( "Checking whether log file at " + filePath + " exists" )
		fileExists = os.path.isfile( filePath )
		self.assertTrue( fileExists, "Log file for " + binaryName + " does " \
						"not exist, test failed!" )

		self._f = open( filePath, 'r' )

		for i, line in enumerate( self._f ):
			if i == 2:
				splitLine = line.split()

				# Test that the binary name matches the one we're testing
				self.assertEqual( binaryName, splitLine[1],
					"Binary name in log doesn't match binary being tested" )

				# Test the version numbers match
				processVersion = self._cc.getWatcherValue( "version/string",
														binaryName, None )
				self.assertEqual( processVersion, splitLine[2], 
					"Process version in log doesn't match the binary " \
					"being tested" )

				# Test that the compile time is within a reasonable amount
				# of time

				# Ideally we would compare date modified or created to the stamp
				# on the binary file, but the builds are copied from Jenkins,
				# so we lose that data. Instead the best we can do is test
				# against the Date Built watcher. If both the watcher and logs
				# are broken in the same way, we do risk a false positive pass.

				# TODO: There might be a bug if we dont call an app ID instead
				# of None for watcher
				processBuildTimeRaw = self._cc.getWatcherValue( "dateBuilt",
															binaryName, None )
				processBuildTime = time.strptime( processBuildTimeRaw,
												"%H:%M:%S %b %d %Y" )

				processBuildLogTime = time.strptime( ":".join( splitLine[5:9] ),
													"%H:%M:%S:%b:%d:%Y)" )
				log.info("processBuildTime: %i processBuildLogTime: %i",
						time.mktime(processBuildTime),
						time.mktime(processBuildLogTime))

				timeDifference = ( time.mktime( processBuildLogTime ) -
											time.mktime( processBuildTime ) )
				
				log.info( "%i second difference", timeDifference )
				
				if( timeDifference != 0):
					self.fail( "Process build time and build time reported " \
							"by log don't match!, there is a difference of %i"
							% timeDifference )

				# Check that FileLogger start time matches the log start time
				processStartLogTime = time.strptime( ":".join( splitLine[12:] ),
													"%b:%d:%H:%M:%S:%Y" )

				log.info("processStartLogTime: %d processConsoleTime: %d. " \
						"Rounding to whole numbers", 
						time.mktime( processStartLogTime ), processConsoleTime )
				
				if ( int( time.mktime( processStartLogTime ) ) !=
					int( processConsoleTime ) ):
					self.fail( "Start time of FileLogger doesn't match time " \
							"reported in the logs" )

		self._f.close()
		log.progress( binaryName + " checked and passed" )