"""This module contains a set of wrappers for executing shell commands and 
file I/O commands.
The primary motivation of this module is that Jenkins needs to execute commands
as a different user than the currently running user.
Future plans also involve executing commands on the machine that is running the
server rather than the machine running the test case.
"""

import subprocess
import shlex
from pwd import getpwnam
import tempfile, os
import time

from bwtest import config
from bwtest import log
from error import HelperError
import xmlconf
import copy as dictcopy


def copy( src, dst ):
	"""Equivalent behavior to Shell cp -rf
	@param src: Source file or folder
	@param dst: Destination file or folder
	"""
	cmd = Command()
	cmd.call( "cp -rf %s %s" % (src, dst) )

def move( src, dst ):
	"""Equivalent behavior to Shell mv
	@param src: Source file or folder
	@param dst: Destination file or folder
	"""
	cmd = Command()
	cmd.call( "mv %s %s" % (src, dst) )

def remove( path ):
	"""Equivalent behavior to shell rm -rf
	@param path: Path to remove 
	"""
	cmd = Command()
	cmd.call( "rm -rf %s" % path)
	
	
def exists( path ):
	"""Equivalent behavior to os.path.exists
	@param path: Path to check
	"""
	cmd = Command()
	try:
		cmd.call( "ls %s" % path)
		return True
	except CommandError:
		return False

def mkdir( path ):
	"""Equivalent behavior to Shell mkdir -p
	@param path: Path of directory to create
	"""
	cmd = Command()
	cmd.call( "mkdir -p %s" % path )
	
def chmod( path, value):
	"""Equivalent behavior to Shell chmod
	@param path: Path to change permissions
	@param value: Unix style permissions eg. 755 or +x
	"""
	cmd = Command()
	cmd.call( "chmod %s %s" % (value, path) )

class CommandError( HelperError ):
	"""Error class triggered by errors in executing commands
	"""
	pass


class Command( object ):
	""" This class helps call the external Linux commands
		in auto testing environment"""

	def __init__( self, commandList = None, user = None ):
		""" Creates a command caller.
		@param commandList: list of commands or a single command
			as a string. We support the following pseudo-macros:
			{bwroot} The root of bigworld checkout
			{bwrespath} The res path used for running the cluster
			{test} The root of tests, normally {bwroot}/testing
			{cuser} cluster user in user_config.xml (or current Linux user if not given)
			{cuid} uid of cluster user in user_config.xml (or current Linux user if not given)
			{dbhost} db host in bw_<username>.xml config
			{dbuser} db user in bw_<username>.xml config
			{dbpassword} db password in bw_<username>.xml config
			{dbname} db name in bw_<username>.xml config
			You can also specify '-' before your command
			to ignore errors (like in makefiles)
		@param user: Set this if you want the commands to use a different user.
		"""

		if commandList is not None:
			list = None 
			if type( commandList ) is str:
				list = [ commandList ]
			else:
				list = commandList
			self._commands = [ self._parse( c ) for c in list ]
		else:
			self._commands = []

		self._lastOutput = None
		self._processes = []
		self._user = user


	def call( self, command = None, parallel = False, getOutput = True,
			waitForCompletion = True, input = None ):
		"""This method call all commands in the list given to constructor
			or specified command
		@param command: Command or list of commands to execute.
		See __init__ commandList for some syntax options
		@param parallel: Set to True to execute all commands simultaneously
		@param waitForCompletion: Set to False to not wait for the command to finish
		@param getOutput: Set to False to ignore output from the command.
		@param input: String of input you want to send to the command.
			getOutput must be True
		"""

		commands = None
		if command is None:
			commands = self._commands
		else:
			commands = [ self._parse( command ) ]

		res = True
		for commandTuple in commands:
			err = self._execute( commandTuple, parallel, getOutput, input )
			res = res and err
			time.sleep( 0.1 )
		if ( parallel and waitForCompletion ):
			res = self._waitForProcesses()
		return res


	def getLastOutput( self ):
		"""Returns last output of a command
		"""
		return self._lastOutput


	def _parse( self, command ):
		parsed = command.lstrip()
		ignoreErrors = False;

		if parsed.startswith( "-" ):
			ignoreErrors = True;
			parsed = parsed.lstrip( '- ' )
		if command.find( "{test}" ) >= 0:
			parsed = parsed.replace( "{test}", config.TEST_ROOT )
		if command.find( "{bwrespath}" ) >= 0:
			parsed = parsed.replace( "{bwrespath}", config.CLUSTER_BW_RES_PATH )
		if command.find( "{bwroot}" ) >= 0:
			parsed = parsed.replace( "{bwroot}", config.CLUSTER_BW_ROOT )
		if command.find( "{cuser}" ) >= 0:
			parsed = parsed.replace( "{cuser}", config.CLUSTER_USERNAME )
		if command.find( "{cuid}" ) >= 0:
			parsed = parsed.replace( "{cuid}", 
							str( getpwnam( config.CLUSTER_USERNAME ).pw_uid ) )
		if command.find( "{dbhost}" ) >= 0:
			self._setupConfig()
			parsed = parsed.replace( "{dbhost}", self.DB_HOST )
		if command.find( "{dbuser}" ) >= 0:
			self._setupConfig()
			parsed = parsed.replace( "{dbuser}", self.DB_USERNAME )
		if command.find( "{dbpassword}" ) >= 0:
			self._setupConfig()
			parsed = parsed.replace( "{dbpassword}", self.DB_PASSWORD )
		if command.find( "{dbname}" ) >= 0:
			self._setupConfig()
			parsed = parsed.replace( "{dbname}", self.DB_DATABASENAME )

		return ( parsed, ignoreErrors )		

	def _execute( self, commandTuple, parallel = False, getOutput = True,
				input = None ):
		command, ignoreErrors = commandTuple
		if self._user:
			command = "sudo -H -u %s " % self._user + command
		elif config.DO_SUDO_COMMANDS:	
			command = "sudo -H -u %s " % config.CLUSTER_USERNAME + command
		
		log.info( "Executing command '%s'..." % command ) 
		stdin = None
		if input != None:
			stdin = subprocess.PIPE

		#Delete PYTHONPATH for when we're calling system Python
		environ = dictcopy.copy( os.environ )
		if 'PYTHONPATH' in environ:
			del environ['PYTHONPATH']

		p = subprocess.Popen( command, stdout = subprocess.PIPE,
					   			stderr = subprocess.STDOUT,
					   			stdin = stdin,
					   			env = environ,
					  			shell = True )
		
		if ( parallel ):
			self._processes.append( (p, command, ignoreErrors) )
			return True
		out = None
		if not getOutput:
			out = p.wait()
		else:
			out = p.communicate( input = input )
		err = p.returncode

		self._lastOutput = out

		if ignoreErrors:
			if err != 0:
				log.warning( "Command: Failed to execute '%s': '%s'" %\
						 ( command, out ) )
				return False
			else:
				return True
		elif err != 0:
			raise CommandError( "Failed to execute '%s': '%s'. Error code=%r" 
					% ( command, out, err ) )

	
	def _waitForProcesses( self ):
		allFinished = False
		while not allFinished:
			time.sleep( 1 )
			allFinished = True
			for proc, command, ignoreErrors in self._processes:
				if proc.poll() == None:
					allFinished = True
		ret = True
		for proc, command, ignoreErrors in self._processes:
			out = proc.communicate()
			err = proc.returncode

			self._lastOutput = out

			if ignoreErrors:
				if err != 0:
					log.warning( "Command: Failed to execute '%s': '%s'" %\
						 ( command, out ) )
					ret = False
			elif err != 0:
				raise CommandError( "Failed to execute '%s': '%s'. Error code=%r" 
					% ( command, out, err ) )
		return ret
		
			
		
	def _setupConfig( self ):

		if hasattr( Command, "_isSetUp" ):
			return

		Command._isSetUp = True

		configFileName = "user_config/server/bw_%s.xml" \
			% config.CLUSTER_USERNAME 
		configName =  config.TEST_ROOT + "/" + configFileName

		try:
			success = xmlconf.readConf( configName, Command,
				{ 
					'db/mysql/host': 			 'DB_HOST',
					'db/mysql/username':		 'DB_USERNAME',
					'db/mysql/password':		 'DB_PASSWORD',
					'db/musql/databaseName':	 'DB_DATABASENAME',
				} )

		except IOError:
			raise CommandError( "%s not found!" % configFileName ) 

		if not success:
			raise CommandError( "Failed to parse %s" % configFileName ) 

		error = ""
		if not hasattr( Command, "DB_HOST" ):
			error += " db/mysql/host"
		if not hasattr( Command, "DB_USERNAME" ):
			error += " db/mysql/username"
		if not hasattr( Command, "DB_PASSWORD" ):
			error += " db/mysql/password"
		if not hasattr( Command, "DB_DATABASENAME" ):
			error += " db/mysql/databaseName"

		if error != "":			
			raise CommandError( "The following tag(s) are not found "
					"in %s: %s" % ( configFileName, error ) )


class MultiUserWriter( object ):
	"""The goal of this class is to simulate writing a file as a different user.
	Will create a temporary file that it will write to until close() is called
	at which point it will copy the contents of the temporary file to the 
	originally requested path using Command call's mechanism for prepending a sudo user
	"""
	
	def __init__( self, path ):
		"""Constructor.
		@param path: Path of file to create.
		"""
		self._path = path
		self._tempfilepath = "/tmp/test%s" % time.time()
		self._tempfile = open( self._tempfilepath, "w" )
	
	def write( self, string ):
		"""Write a string to file.
		@param string: Text to write to file
		"""
		self._tempfile.write( string )
		
	def writelines( self, lines):
		""" Write a list of lines to file.
		@param lines: List of lines to write
		"""
		self._tempfile.writelines( lines )
	
	def close( self ):
		"""Close file for writing.  Must be called or actual file will never
		be created.
		"""
		self._tempfile.flush()
		self._tempfile.close()
		copy( self._tempfilepath, self._path)
		os.remove( self._tempfilepath )	

