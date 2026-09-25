from bwtest import config

import atexit
import os
import pwd
import subprocess

CONFIG = """
[message_logger]
storage_type = mldb

[mldb]
logdir = %s
segment_size = 104857600
default_archive = %s/message_logs.tar.gz
"""

def checkMLLogFile( filePath, expectedOutput ):
	"""
	Checks for specified text in the MessageLogger log file.

	@param filePath:		Path to the MessageLogger log file
	@param expectedOutput:	String(s) to verify in the logs
	"""
	f = open( filePath )
	mlLogs = f.readlines()
	f.close()

	for expectedLine in expectedOutput:
		resultFound = False
		for mlLogLine in mlLogs:
			if expectedLine in mlLogLine:
				resultFound = True
				break
		if not resultFound:
			return resultFound

	return True

class CustomMessageLogger:
	"""
	This class is for custom MessageLogger testing with MessageLogger logs
	"""

	def __init__( self ):

		self.MESSAGE_LOGGER = '%s/%s/%s/message_logger' % (
			config.CLUSTER_BW_ROOT,
			config.BIGWORLD_FOLDER, 
			config.TOOLS_BINARY_FOLDER )

		self.user = config.CLUSTER_USERNAME
		self.dir = '/tmp/message_logger_%s' % self.user
		self.uid = str( pwd.getpwnam( self.user ).pw_uid )
		self.mlLogs = '%s/message_logger.log' % self.dir
		self.proc = None

	def start( self, *args ):
		"""
		Starts a messge_logger process.
		"""
		os.system( "rm -rf %s" % self.dir )
		os.system( "mkdir %s" % self.dir )

		configPath = "%s/message_logger_%s.conf" % ( config.TEST_ROOT, self.user )
		configFile = open( configPath, 'w' )
		configFile.write( CONFIG % (self.dir, self.dir) )
		configFile.close()

		# Open file to contain the MessageLogger logs
		self.f = open( self.mlLogs, "w" )

		cmd = [	self.MESSAGE_LOGGER,
				'-u', self.uid,
				'-c', configPath ]

		cmd.extend( args )

		self.proc = subprocess.Popen( cmd, stdout=self.f, stderr=self.f )
	
		atexit.register( self.stop )
	
	
	def stop( self ):
		"""
		Stops started messge_logger process.
		"""
	
		if self.proc:
			self.proc.terminate()
			self.proc = None
			self.f.close()