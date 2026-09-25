"""
Module for daemonising(backgrounding) functions.

The class Daemon provides the interface for creating a new daemon process.
It can be instantiated with a run function, which returns a normal process
return code (integer). You can also give it files in which the standard
input, output and error streams can be redirected to (otherwise they go to
/dev/null). A PID file can also be generated.

"""

import os
import sys
import traceback
import signal
import atexit

import util

DEBUG_ENABLED = False
DEBUG_FILE = "/tmp/debug.log"


# -----------------------------------------------------------------------------
# Section: Exception declarations
# -----------------------------------------------------------------------------

class DaemonError:
	"""
	Daemon error.
	"""
	pass

class DaemonNoRunFunctionError( DaemonError ):
	"""
	Raised when a daemon is started with no run function.
	"""
	pass

# -----------------------------------------------------------------------------
# Section: Helper functions
# -----------------------------------------------------------------------------

def debug( s ):
	"""
	Debug function.
	@type s:		string
	@param s:		string to output
	"""
	if DEBUG_ENABLED:
		f = open( DEBUG_FILE, "a" )
		f.write( s )
		f.flush()
		f.close()


def writePidFile( pidFilePath ):
	"""
	Writes the PID of the current process to the file at the given path.

	@param pidFilePath:		the path of to the PID file to write to. Will be
							created if it does not exist.
	@raise IOError:			if the file pointed to by pidFilePath could not be
							opened for writing
	"""
	debug( "Writing PID file to " + pidFilePath )
	f = open( pidFilePath, "w" )
	f.write( "%d\n" % os.getpid() )
	f.flush()
	f.close()

# -----------------------------------------------------------------------------
# Section: class Daemon
# -----------------------------------------------------------------------------

class Daemon:
	"""
	The Daemon class.

	Specify the run function at construct time, or set it after by setting the
	attribute run.

	Start the daemon process by calling the start() method.

	@type run:		function
	@ivar run:		the run function. Returns an integer process return code
					which is what the daemon process exits with.
	"""
	def __init__( self,
			run 		= None,
			args 		= (),
			inFile 		= "/dev/null",
			outFile 	= "/dev/null",
			errFile 	= "/dev/null",
			workingDir 	= None,
			pidFile 	= None,
			umask		= 0077 ):
		"""
		Constructor.

		@type run:		function
		@param run:		the run function
		@type args:		tuple
		@param args:	the run function's arguments
		@type inFile:	string
		@param inFile:	path to the file to redirect to the standard input
						stream.
		@type outFile:	string
		@param outFile:	path to the file to redirect from the standard output
						stream.
		@type errFile: 	string
		@param errFile:	path to the file to redirect from the standard error
						stream.
		@type workingDir:	string
		@param workingDir:	the working directory to execute the function in
		@type pidFile:	string
		@param pidFile:	path to the file to write the process ID of the daemon
						process

		"""
		self.run 			= run
		self.args 			= args
		self._inFile 		= inFile
		self._outFile 		= outFile
		self._errFile 		= errFile
		self._workingDir 	= workingDir
		self._pidFile 		= pidFile
		self._umask			= umask


	def start( self ):
		"""
		Start the daemon.

		@raise DaemonNoRunFunctionError:	if no run function capable of
											running is found
		"""
		if not callable( self.run ):
			raise DaemonNoRunFunctionError


		if os.fork():
			# we are still the parent - return
			return

		# we are the child

		# create a new unix session
		os.setsid()

		if os.fork():
			# we are not the grandchild
			sys.exit( 0 )

		if self._workingDir:
			debug( "Changing dir to %s\n" % self._workingDir )
			os.chdir( self._workingDir )

		os.umask( self._umask )

		debug( "Closing file descriptors\n" )

		# get max fds
		import resource
		maxfd = resource.getrlimit( resource.RLIMIT_NOFILE )[1]

		if maxfd == resource.RLIM_INFINITY:
			maxfd = 1024

		# close all possible fds
		for fd in range( 0, maxfd ):
			try:
				os.close( fd )
			except OSError:
				pass

		debug( "Redirecting standard streams\n" )

		# redirect standard input, standard output and standard error streams
		try:
			# standard input (fd=0)
			os.open( self._inFile, os.O_RDONLY )
			# standard output (fd=1)
			flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
			mode = 0644
			os.open( self._outFile, flags, mode )
			# standard error (fd=2)
			if self._errFile != self._outFile:
				os.open( self._errFile, flags, mode )
			else:
				# duplicate stdout to stderr
				os.dup2( 1, 2 )

		except Exception, e:
			debug( "error while redirecting standard streams: %s\n" % (e,) )

		if self._pidFile:
			debug( "Writing PID file to %s\n" % self._pidFile )
			writePidFile( self._pidFile )

		signal.signal( signal.SIGTERM, self.exitGracefully )
		atexit.register( self.attemptRemovePidFile )

		# Signal Handler to assist in log rotation
		signal.signal( signal.SIGHUP, self.resetFileDescriptors )

		debug( "Executing run function\n" )
		try:
			res = self.run( *self.args )
		except:
			debug( "Exception occurred in run function\n" )
			exceptionType, exceptionValue, exceptionTraceBack = sys.exc_info()
			traceback.print_exception(
				exceptionType, exceptionValue, exceptionTraceBack )
			res = 1

		if res is None:
			res = 0

		debug( "Run function finished; exit code %d\n" % res )

		sys.exit( res )

	def attemptRemovePidFile( self ):
		# delete the pid file
		if self._pidFile:
			try:
				os.unlink( self._pidFile )
			except:
				pass
			self._pidFile = None

	def exitGracefully( self, signalNumber, stackFrame ):
		debug( "Exiting gracefully\n" )
		self.attemptRemovePidFile()
		sys.exit( 1 )


	def resetFileDescriptors( self, signalNumber, stackFrame ):
		util.redirectLogOutputToFiles( self._outFile, self._errFile )
		

# -----------------------------------------------------------------------------
# Section: Testing
# -----------------------------------------------------------------------------

#~ if __name__ == "__main__":
	#~ def testFunction():
		#~ print "this is a test function"
		#~ return 0

	#~ d = Daemon( run = testFunction,
		#~ outFile = "test.log",
		#~ errFile = "test.err",
		#~ pidFile = "test.pid",
		#~ workingDir = None )
	#~ d.start()

