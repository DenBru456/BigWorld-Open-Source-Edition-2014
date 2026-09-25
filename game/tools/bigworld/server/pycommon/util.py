import os
import sys
import string
import re
import struct
import socket
import threading
import platform
import logging

log = logging.getLogger( __name__ )


class Functor( object ):

	def __init__( self, func, **kwargs ):
		"""Permitted kwargs are:
		   'args': unnamed argument list to be passed to __call__()
		   'kwargs': named argument list to be passed to __call__()
		   'moreargs': if True, pass unnamed args to __call__() into func()
		   'morekwargs': if True, pass named args to __call__() into func()"""

		self.func = func
		keywords = [ "args", "kwargs", "moreargs", "morekwargs" ]
		for k in keywords:
			if kwargs.has_key( k ):
				setattr( self, k, kwargs[ k ] )
			else:
				setattr( self, k, None )

	def __call__( self, *args, **kwargs ):

		# Set up local lists of unnamed and named args to pass to func()
		localargs = []; localkwargs = {}

		if self.args:
			localargs += self.args
		if self.moreargs:
			localargs = [ x for x in args ]
		if self.kwargs:
			localkwargs.update( self.kwargs )
		if self.morekwargs:
			localkwargs.update( kwargs )

		return self.func( *localargs, **localkwargs )


def anyIn( needles, haystack ):
	"""Returns true if any of the needles are in the haystack."""

	for n in needles:
		if n in haystack:
			return True
	return False

def shortCmd( cmd ):
	"""Takes a commandline and strips off all directories before the name of the
	   executable."""

	parts = string.split( cmd, " " )
	parts[0] = os.path.basename( parts[0] )
	return string.join( parts, " " ).rstrip()

def border( s, style="-" ):
	"""Make a nice ascii border around a heading."""
	title = "| %s |" % s
	border = "+" + style * (len( title ) - 2) + "+"
	return border + "\n" + title + "\n" + border

def fappend( filename, s ):
	"""Append the given string to the given file."""
	try:
		f = open( filename, "a" )
		f.write( s )
		f.close()
		return True
	except:
		return False

def daemon( cmdline, output=None ):
	"""Runs a command as a daemon and returns its PID."""

	childpid = os.fork()
	if childpid == 0:

		# If output is given, then redirect output to the given file
		if output:
			fd = os.open( output, os.O_WRONLY | os.O_CREAT )
			os.dup2( fd, 1 )
			os.dup2( fd, 2 )

		parts = cmdline.rstrip().split( " " )

		# Macro to group together args that should be a single string
		def regroup( xs ):

			ret = []
			joining = 0
			quotes = ['"',"'"]
			q = None

			for x in xs:
				if joining:
					ret[-1] += " " + x
				else:
					ret.append(x)

				if not x:
					continue

				if not joining and x[0] in quotes:
					q = x[0]

				if not joining and q and x[0] == q:
					joining = 1
					ret[-1] = ret[-1][1:]
				elif joining and q and x[-1] == q:
					joining = 0
					ret[-1] = ret[-1][:-1]
					q = None

			return ret

		parts = regroup( parts )
		os.execvp( parts[0], parts )
	else:
		log.info( "Forking '%s' [%d]", shortCmd( cmdline ), childpid )
		return childpid

def getProgDir():
	"""Return the fully qualified directory that this process is running in."""
	return os.path.dirname(	os.path.abspath( sys.argv[0] ) )

def extractTime( s ):
	"""Extract a time string from a string."""

	patt = re.compile( "\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+([A-Z]+\s+)?\d+" )
	m = patt.search( s )
	if not m:
		return None
	elif m.group(1):
		return re.sub( m.group(1), "", m.group() )
	else:
		return m.group()

def printNow( s ):
	sys.stdout.write( s ); sys.stdout.flush()

def sort( xs ):
	"""
	Why on earth doesn't the python list.sort() method return self?!?!
	"""
	xs.sort()
	return xs

def fmtSeconds( secs ):
	if secs < 60:
		return "%ds" % secs
	elif secs < 60 * 60:
		return "%dm" % (secs/60)
	elif secs < 60 * 60 * 24:
		return "%dh" % (secs/60/60)
	else:
		return "%dd" % (secs/60/60/24)


def fmtSecondsLong( secs ):
	s = ""

	if secs >= 60 * 60 * 24:
		s += "%d days " % (secs / (60 * 60 * 24))
		secs %= 60 * 60 * 24

	if secs >= 60 * 60:
		s += "%d hours " % (secs / (60 * 60))
		secs %= 60 * 60

	if secs >= 60:
		s += "%d minutes " % (secs / (60))
		secs %= 60

	s += "%d seconds" % secs
	return s


def fmtBytes( bytes, uppercase = False ):
	if bytes < 1 << 10:
		ret = "%dB" % bytes
	elif bytes < 1 << 20:
		ret = "%dKB" % (bytes/(1<<10))
	elif bytes < 1 << 30:
		ret = "%.1fMB" % (float( bytes )/(1<<20))
	else:
		ret = "%.2fGB" % (float( bytes )/(1<<30))

	if uppercase:
		return ret.upper()
	else:
		return ret

# Don't ask
class MFRectangle:
	def __init__( self, x1, y1, x2, y2 ):
		self.minX = min( x1, x2 )
		self.maxX = max( x1, x2 )

		self.minY = min( y1, y2 )
		self.maxY = max( y1, y2 )

	def __str__( self ):
		return "[%.1f,%.1f,%.1f,%.1f]" % (self.minX, self.minY,
										  self.maxX, self.maxY)

# Just like the shell command
def uniq( list, cmp = None, inplace = False ):
	ret = []

	# If a comparator is provided, sort the list prior to the uniqueness pass
	if cmp:
		slist = list[:]
		slist.sort( cmp )
	else:
		slist = list

	for i in xrange( len( slist ) ):
		if (i+1 < len( slist ) and slist[ i ] != slist[ i+1 ]) or \
		   i+1 == len( slist ):
			ret.append( slist[ i ] )

	# If inplace, overwrite the input list
	if inplace:
		for i in xrange( len( list ) ):
			list.pop()
		for e in ret:
			list.append( e )
		return list
	else:
		return ret

# Partitions a list into two sublists, based on the return value of a boolean
# predicate
def partition( func, list ):
	(yay, nay) = ([], [])
	for e in list:
		if func( e ):
			yay.append( e )
		else:
			nay.append( e )
	return (yay, nay)

# Returns a list of everything that was only in the first list, and a list of
# everything that was only in the second list
def diff( list1, list2 ):

	in1 = {}
	for x in list1:
		in1[ x ] = 1

	in2 = []
	for x in list2:
		if not in1.has_key( x ):
			in2.append( x )
		else:
			del in1[ x ]

	return (in1.keys(), in2)

def clamp( x, lo, hi ):
	if x < lo:
		return lo
	elif x > hi:
		return hi
	else:
		return x

# Returns the path to the Python interpreter being used.  On UNIX this is just
# sys.executable, but on windows, since os.spawnl() doesn't understand paths
# with spaces in them (e.g. "C:/Program Files/Python24/python.exe") we have to
# do ~1 mangling on the filename.
def interpreter():
	if os.name == "posix":
		return sys.executable
	else:
		def wintrunc( path ):
			if " " in path:
				return path[:6] + "~1"
			else:
				return path

		dirs, bin = os.path.split( sys.executable )
		dirs = os.path.sep.join( map( wintrunc, re.split( "[/\\\\]", dirs ) ) )
		return os.path.sep.join( (dirs, bin) )

# Nice way to dump packets.  Prints characters for printable characters and hex
# otherwise
def hexdump( data, printable = True ):

	def show( c ):
		if printable and \
			   c in string.letters + string.digits + string.punctuation:
			return " " + c
		else:
			return "%02x" % ord( c )

	return " ".join( [show( c ) for c in data] )


def prompt( s, default = "" ):

	# For some reason on Fedora 7, importing this can cause non-printable
	# characters to be written to stdout.  This is likely to be a bug in the GNU
	# readline library, and a bug report has been submitted to that project.
	# This plays havoc with anything that is parsing the stdout from a
	# command-line utility such as control_cluster.py.  Thankfully, console apps
	# that use prompt() or promptYesNo() are usually not too worried about
	# invisible control characters appearing on stdout.
	try:
		import readline
	except ImportError:
		pass

	if default:
		s += " [%s]" % default
	if "?" not in s:
		s += ": "
	else:
		s += " "
	return raw_input( s ) or default


def promptYesNo( question, default = True ):
	"""Prompt a user for a Yes/No response.
	   Returns: True (yes) / False (no)"""

	query = True
	if default:
		defstr = "yes"
	else:
		defstr = "no"
	ret = prompt( question, defstr )

	respre = re.compile( "^yes|no|y|n$", re.IGNORECASE )

	while query:
		m = respre.match( ret )
		if m:
			if m.group( 0 ).lower().startswith( "y" ):
				status = True
			else:
				status = False

			query = False

		# Re-ask the question if we haven't gotten a valid answer
		if query:
			ret = prompt( "Please enter either 'yes' or 'no'", defstr )

	return status



# Ordering for ascii-format IP addresses
def cmpAddr( a, b ):
	return cmp( struct.unpack( "!I", socket.inet_aton( a ) )[0],
				struct.unpack( "!I", socket.inet_aton( b ) )[0] )


# Like the Perl function.  Note that this is a generator.
def chomp( xs ):
	for x in xs:
		yield x.rstrip()
	raise StopIteration


def softMkDir( path, pwent = None, parents = False, sudo = False ):
	"""
	Ensures that the given directory exists by making it if it doesn't already.

	Pass parents as True to make any parent directories as necessary.

	Pass sudo as True to issue the mkdir command via sudo.  Necessary if you
	are making a user-owner directory in a directory owned by root (i.e. a home
	directory).
	"""

	if os.name != "posix":
		raise NotImplementedError(
			"This function is not implemented on non-POSIX systems" )

	import pwd

	# If no pwent passed, fetch one for the real user
	if not pwent:
		pwent = pwd.getpwuid( os.getuid() )

	try:
		statinfo = os.stat( path )

		# If the path exists but ownership is wrong, fail.
		if statinfo.st_uid != pwent.pw_uid:
			log.error( "%s is not owned by %s", path, pwent.pw_name )
			return False

	# Otherwise make it
	except OSError:

		if sudo:
			cmd = "sudo "
		else:
			cmd = ""

		if parents:
			cmd += "mkdir -p"
		else:
			cmd += "mkdir"

		if os.system( "%s %s" % (cmd, path) ):
			log.error( "Couldn't make directory %s", path )
			return False

		if sudo and os.system( "sudo chown -R %d:%d %s" %
							   (pwent.pw_uid, pwent.pw_gid, path) ):
			log.error( "Couldn't give ownership of %s to %s",
					   path, pwent.pw_name )
			return False

	# Hurrah!
	return True


def softSymlink( path, tgt, sudo = False ):
	"""
	Ensures that path is a symlink to tgt, making the link if it doesn't already
	exist.
	"""

	if os.path.islink( path ):
		existingtgt = os.readlink( path )
		if existingtgt != tgt:
			log.error( "%s exists but points to %s, not %s", path,
						  existingtgt, tgt )
			return False
	else:
		# Change into directory where link will reside
		oldcwd = os.getcwd()
		linkdir, linkname = os.path.split( path )
		os.chdir( linkdir )

		# Make the link
		if sudo:
			cmd = "sudo "
		else:
			cmd = ""

		cmd += "ln -s %s %s" % (tgt, linkname)

		if os.system( cmd ):
			log.error( "Couldn't symlink %s -> %s", path, tgt )
			return False

	return True


# Little class to do "percent complete" printing
class PercentComplete( object ):

	WIDTH = 80

	# Set this to true to disable all output from instances of this class (much
	# easier than putting if's around every reference to this class in your
	# program module)
	QUIET = False

	def __init__( self, text, total ):
		self.text = text
		self.curr = 0
		self.total = total
		self.currpc = 0
		self.haswritten = False
		self.started = self.finished = False
		self.update( self.curr )

	def update( self, curr = None ):

		if curr:
			self.curr = curr
		else:
			self.curr += 1

		if self.curr >= self.total - 1:
			nowpc = 100
		else:
			nowpc = int( float( (self.curr + 1) * 100 ) / self.total )

		if not self.started or nowpc > self.currpc:
			self.started = True
			self.currpc = nowpc
			self.overwrite()

		if not self.finished and self.currpc == 100 and not self.QUIET:
			self.finished = True
			print

	def overwrite( self ):

		if self.QUIET: return

		# The completeness string that appears at the end of the line
		if self.currpc < 100:
			s = "%3d%%" % self.currpc
		else:
			s = "done!"

		# How many dots we need in the middle
		middleWidth = self.WIDTH - len( s ) - len( self.text )
		nDots = int( (self.currpc / 100.0) * (middleWidth-2) )

		# Print the prefix if this is the first time, or backspace over the
		# completeness and the dots if not.
		if not self.haswritten:
			sys.stdout.write( self.text )
			self.haswritten = True
		else:
			sys.stdout.write( "\b" * (self.WIDTH - len( self.text )) )

		sys.stdout.write( " %-*s " % (middleWidth-2, "." * nDots) )
		sys.stdout.write( s )
		sys.stdout.flush()

# A size-capped ring buffer that behaves like a deque
class RingBuffer( object ):

	class error( Exception ):
		def __init__( self, reason ):
			Exception.__init__( self, reason )

	class iterator( object ):
		def __init__( self, buf ):
			self.buf = buf
			self.pos = 0

		def __iter__( self ):
			return self

		def next( self ):
			if self.pos == len( self.buf ):
				raise StopIteration
			ret = self.buf.data[ (self.buf.begin + self.pos) % self.buf.size ]
			self.pos += 1
			return ret

	def __init__( self, size ):
		self.data = [None for i in xrange( size )]
		self.size = size
		self.begin = self.end = self.len = 0

	def __len__( self ):
		return self.len

	def __str__( self ):
		return "%s (%d/%d slots)" % (self.data, self.len, self.size)

	def __iter__( self ):
		return self.iterator( self )

	def shift( self ):
		if self.len == 0:
			raise self.error, "Tried to shift an empty buffer"
		ret = self.data[ self.begin ]
		self.begin = (self.begin+1) % self.size
		self.len -= 1
		return ret

	def unshift( self, elem ):
		self.begin = (self.begin-1) % self.size
		self.data[ self.begin ] = elem
		self.len += 1
		if self.len > self.size:
			self.end = (self.end-1) % self.size

	def pop( self ):
		if self.len == 0:
			raise self.error, "Tried to pop an empty buffer"
		self.end = (self.end-1) % self.size
		self.len -= 1
		return self.data[ self.end ]

	def push( self, elem ):
		self.data[ self.end ] = elem
		self.end = (self.end+1) % self.size
		self.len += 1
		if self.len > self.size:
			self.begin = (self.begin+1) % self.size
			self.len -= 1


biglock = threading.Lock()
def synchronized( f ):
	"""
	Implements the Java 'synchronized' keyword for bound methods.
	"""

	def execute( obj, *args, **kwargs ):
		try:

			# Try to acquire the object's lock
			try:
				obj.__lock.acquire()

			# If the object doesn't have a __lock attribute, then we better
			# create one
			except AttributeError:

				# We don't want to let two threads create a __lock attribute, so
				# we synchronize this block of code with a global lock.  It's
				# very coarse grained but this shouldn't happen too often so we
				# don't mind too much
				biglock.acquire()
				if not hasattr( obj, "__lock" ):
					setattr( obj, "__lock", threading.RLock() )
				biglock.release()

				# Now that the object has a lock we acquire it
				obj.__lock.acquire()

			return f( obj, *args, **kwargs )

		finally:
			obj.__lock.release()

	return execute


def filterProcs( procs, name = None, uid = None ):
	if name != None:
		procs = [p for p in procs if p.name == name]
	if uid != None:
		procs = [p for p in procs if p.uid == uid]

	return procs


def redirectLogOutputToFiles( stdoutFile, stderrFile ):
	# If something goes wrong here, we may not be able to
	# log out anything at all to know what went wrong
	# possibly best to let an exception occur and terminate
	# execution.

	# Standard output
	fdOut = os.open( stdoutFile, os.O_CREAT | os.O_APPEND | os.O_WRONLY )

	if fdOut != 1:
		os.dup2( fdOut, 1 )
		os.close( fdOut )

	# Standard error
	if stderrFile != stdoutFile:
		fdErr = os.open( stderrFile, os.O_CREAT | os.O_APPEND | os.O_WRONLY )
		if fdErr != 2:
			os.dup2( fdErr, 2 )
			os.close( fdErr )
	else:
		os.dup2( 1, 2 )


# This will by default only output the message content for logs of INFO level
class CleanFormatter( logging.Formatter ):

	def __init__( self, stripInfoPrefix = True ):
		logging.Formatter.__init__( self )
		self.stripInfoPrefix = stripInfoPrefix

	def format( self, record ):
		if self.stripInfoPrefix and \
								record.levelno in (logging.DEBUG, logging.INFO):
			return record.getMessage()
		else:
			return "%-10s%s" % (logging.getLevelName( record.levelno ) + ":",
								record.getMessage())

# This will								
def setUpBasicCleanLogging():
	stdoutHandler = logging.StreamHandler( sys.stdout )
	stdoutHandler.setFormatter( CleanFormatter() )
	
	logging.getLogger().addHandler( stdoutHandler )
	logging.getLogger().setLevel( logging.INFO )


def MF_CONFIG():
	if platform.machine() == "x86_64":
		return "Hybrid64"
	else:
		return "Hybrid"
