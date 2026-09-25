"""
This module starts, stops and mlcats a local message_logger.
"""

from bwtest import config

import atexit
import os
import pwd
import subprocess
import copy


CONFIG = """
[message_logger]
storage_type = mldb

[mldb]
logdir = %s
segment_size = 104857600
default_archive = %s/message_logs.tar.gz
"""

MESSAGE_LOGGER = '%s/%s/%s/message_logger' % (
	config.CLUSTER_BW_ROOT,
	config.BIGWORLD_FOLDER, 
	config.TOOLS_BINARY_FOLDER )


MLCAT = '%s/%s/tools/bigworld/server/message_logger/mlcat.py' % (
	config.CLUSTER_BW_ROOT,
	config.BIGWORLD_FOLDER )


class MessageLogger:
	"""
	This class encapsulates message_logger and mlcat.py.
	"""

	def __init__( self, user ):
		"""
		Constructor

		@param user:	User to run message_logger process
		"""

		self.user = user
		self.uid = str( pwd.getpwnam( self.user ).pw_uid )
		self.dir = '/tmp/message_logger_%s' % user
		self.proc = None

		# TODO: For backwards compatibility, remove once TestCases are updated
		global g_messageLogger
		if g_messageLogger is not None:
			g_messageLogger.stop()
		g_messageLogger = self


	def start( self ):
		"""
		Starts a messge_logger process.
		"""

		os.system( "rm -rf %s" % self.dir )

		configPath = "%s/message_logger_%s.conf" % (config.TEST_ROOT, self.user)
		configFile = open( configPath, 'w' )
		configFile.write( CONFIG % (self.dir, self.dir) )
		configFile.close()

		cmd = [	MESSAGE_LOGGER,
				'-u', self.uid,
				'-c', configPath,
				'-q']

		self.proc = subprocess.Popen( cmd )

		atexit.register( self.stop )


	def stop( self ):
		"""
		Stops started messge_logger process.
		"""

		if self.proc:
			self.proc.terminate()
			self.proc = None


	def mlcat( self, message = None, procs = None, back = None ):
		"""
		Runs mlcat.py.

		@param message:	Pattern to match against in message for inclusion
		@param procs:	Processes to match
		@param back:	Amount of history to search
		"""

		cmd = [	MLCAT, '--uid', self.uid ]

		if message:
			cmd.extend( ['--message', message] )

		if procs:
			cmd.extend( ['--procs', procs] )

		if back:
			cmd.extend( ["--back", str( back )] )
		else:
			cmd.append( "--last-startup" )

		cmd.append( self.dir )
		
		#Delete PYTHONPATH since we're calling system Python
		environ = copy.copy( os.environ )
		if 'PYTHONPATH' in environ:
			del environ['PYTHONPATH']
		proc = subprocess.Popen( cmd, 
						stdout = subprocess.PIPE, env = environ )
		output = proc.communicate()
		if proc.returncode != 0:
			return ""
		return output[0].strip()



g_messageLogger = None

def grepLastServerLog( text, lastSeconds = None, process = None, 
					   user = config.CLUSTER_USERNAME ):
	"""
	See MessageLogger.mlcat.
	TODO: For backwards compatibility, remove once TestCases are updated.

	@param text:		Pattern to match against in message for inclusion
	@param lastSeconds:	Amount of history to search
	@param process:		Processes to match
	@param user:		Ignored
	"""
	global g_messageLogger
	if g_messageLogger is None:
		return ""
	return g_messageLogger.mlcat( text, process, lastSeconds )
