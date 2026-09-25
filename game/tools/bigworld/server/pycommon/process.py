import bisect
import itertools
import logging
import messages
import re
import signal
import socket
import socketplus
import util
import watcher_data_message

from exposed import Exposed, ExposedType
from cluster_constants import MESSAGE_LOGGER_NAME
from cluster_constants import RECV_BUF_SIZE

from pycommon.watcher_data_message import WatcherDataMessage

log = logging.getLogger( __name__ )


# ------------------------------------------------------------------------------
# Section: Version
# ------------------------------------------------------------------------------

class Version( object ):
	def __init__( self, major, minor, patch = 0 ):
		self.major = major
		self.minor = minor
		self.patch = patch

	def __str__( self ):
		if self.major == 0:
			return "Pre 2.0"
		else:
			return "%d.%d.%d" % (self.major, self.minor, self.patch)

	def __cmp__( self, other ):
		if not isinstance( other, tuple ):
			other = other.asTuple()

		return cmp( self.asTuple(), other )

	def asTuple( self ):
		return (self.major, self.minor, self.patch)


	@classmethod
	def fromString( klass, s ):
		if not s:
			return None
		return klass( *(map( int, s.split( '.' ) ) ) )


	def __repr__( self ):
		return "Version%r" % (self.asTuple(),)

	__json__ = asTuple

# end class Version

# ------------------------------------------------------------------------------
# Section: Processes 
# ------------------------------------------------------------------------------

class Processes( object ):
	"""
	This class holds a collection of Process subclasses mapped by their name
	and interface names.
	"""
	class _MappingProxy( object ):
		"""
		This class is a proxy object that dynamically exposes an existing
		mapping as a read-only mapping. Optionally, it can filter based on a
		test functor on values and transforming values via a functor.
		"""
		def __init__( self, mapping, valueFunctor = lambda x: x, 
				valueTest = None ):
			self._mapping = mapping
			self._valueFunctor = valueFunctor
			self._valueTest = valueTest

		def __len__( self ):
			return len( self._filteredMap() )

		def _filteredMap( self ):
			if self._valueTest is None:
				return self._mapping
			
			return dict( itertools.ifilter( 
				lambda (key, value): self._valueTest( value ), 
				self._mapping.iteritems() ) )

		def __contains__( self, key ):
			return key in self._filteredMap()

		def has_key( self, key ):
			return self._filteredMap().has_key( key )

		def __iter__( self ):
			return self.iterkeys()

		def get( self, key, default = None ):
			try:
				return self._valueFunctor( self._mapping[ key ] )
			except KeyError:
				return default

		def __getitem__( self, key ):
			return self.get( key )

		def iteritems( self ):
			return itertools.imap( 
				lambda (key, value): (key, self._valueFunctor( value ) ),
				self._filteredMap().iteritems() )

		def items( self ):
			return list( self.iteritems() )

		def iterkeys( self ):
			return self._filteredMap().iterkeys()

		def keys( self ):
			return self._filteredMap().keys()

		def itervalues( self ):
			return itertools.imap( self._valueFunctor, 
				self._filteredMap().itervalues() )

		def values( self ):
			return list( self.itervalues() )

		def __repr__( self ):
			return repr( dict( self.items() ) )


	class _MappingKeySetAdaptorProxy( object ):
		"""
		This class is a proxy object that dynamically exposes the set of a
		map's keys.
		"""
		def __init__( self, mapping ):
			self._mapping = mapping
		
		def __len__( self ):
			return len( self._mapping )

		def __contains__( self, key ):
			return key in self._mapping

		def __iter__( self ):
			return self._mapping.iterkeys()

		def __repr__( self ):
			return repr( self._mapping.keys() )


	def __init__( self ):
		""" Constructor."""
		self._processes = {}
		self._interfaceMap = {}
		self._versionSteps = []


	def addProcessClass( self, klass ):
		"""
		This method adds a Process subclass.
		"""
		self._processes[ klass.meta.name ] = klass 

		for interfaceName in klass.meta.interfaceNames:
			self._interfaceMap[ interfaceName ] = klass
		self._addVersions( klass.meta.sinceVersion, klass.meta.lastVersion )
			

	def _addVersions( self, *versions ):
		"""
		This method adds the given versions, keeping the version steps in
		order.
		"""
		steps = self._versionSteps
		for version in versions:
			if version is not None:
				pos = bisect.bisect_left( steps, version )
				if (pos == len( steps )) or (steps[pos] != version):
					steps.insert( pos, version )


	@property
	def names( self ):
		""" A set of the registered processes' names. """
		return self._MappingKeySetAdaptorProxy( self._processes )


	@property
	def interfaceMap( self ):
		""" A mapping of interface names to process class. """
		return self._MappingProxy( self._interfaceMap )


	@property
	def componentMap( self ):
		""" A mapping of process names to component names. """
		return self._MappingProxy( self._processes,
			lambda value: value.componentName )


	def __contains__( self, processName ):
		return processName in self._processes


	def __getitem__( self, processName ):
		return self._processes[ processName ]


	def __iter__( self ):
		return iter( self._processes )


	def getByInterfaceName( self, interfaceName ):
		"""
		Returns a process class by interface name.
		"""
		return self._interfaceMap[ interfaceName ]


	def filter( self, version = None, test = None ):
		"""
		Returns a dynamic mapping of the process names to process classes,
		optionally filtering on version and using a custom filter.

		@param version 	The specific version, or None for all versions.
		@param test 	The test to filter process classes on, or None to
						specify no test.
		"""
		return self._MappingProxy( self._processes,
			valueTest = lambda desc: 
				(version is None or desc.isInVersion( version )) and 
					(test is None or test( desc )) )


	all = property( filter,
		doc = "Map of all registered processes, from name to class." )


	def serverProcs( self, version = None ):
		"""
		Returns a mapping of the process names to process classes for all
		server components.

		@param version 	The specific version, or None for all versions.
		"""
		return self.filter( version,
			lambda klass: klass.meta.isServerProc )


	def required( self, version = None ):
		""" 
		Returns a mapping of the process names to process classes for
		components required for a running server.

		@param version 	The specific version, or None for all versions.
		"""
		return self.filter( version, lambda klass: klass.meta.isRequired and
			klass.meta.isServerProc )


	def optional( self, version = None ):
		""" 
		Returns a mapping of the process names to process classes for
		components that are optional to the running of the server.

		@param version 	The specific version, or None for all versions.
		"""
		return self.filter( version, lambda klass: not klass.meta.isRequired and
			klass.meta.isServerProc )


	def singletons( self, version = None ):
		""" 
		Returns a mapping of the process names to process classes for
		singleton process types.

		@param version 	The specific version, or None for all versions.
		"""
		return self.filter( version, lambda klass: klass.meta.isSingleton )


	def startable( self, version = None ):
		"""
		Returns a mapping of the process names to process classes for processes
		that can be started via the tools.

		@param version 	The specific version, or None for all versions.
		"""
		return self.filter( version, lambda klass: klass.meta.isStartable )


	@property 
	def versions( self ):
		"""
		A list of all version boundaries (where process sets change).
		"""
		return list( self._versionSteps )


	def matchVersionForProcesses( self, processes ):
		"""
		This method returns the version for which the required processes is
		contained within the given process iterable, or None if no such version
		exists.
		"""
		processSet = set( processes )
		for version in reversed( self._versionSteps ):
			if processSet.issuperset( set( self.required( version ) ) ):
				return version
		return None
			
# end class Processes


# ------------------------------------------------------------------------------
# Section: Process and ProcessMeta
# ------------------------------------------------------------------------------

class ProcessMeta( ExposedType ):
	"""
	Metaclass type for Processes. Each Process with an inner class named "meta"
	is registered according to the parameters set as class attributes on that
	"meta" inner class.

	The specification of some parameters are optional as per below. These will
	be filled with defaults if not specified explicitly, so each registered
	process class will have access to the complete set.
	"""

	REQUIRED_PARAMS = [
		"componentName", 	# The name of the component, e.g. CellApp
		"isRequired", 		# Whether an instance is required for the server to
							# operate
		"isServerProc" # Whether this is for a server component.
	]
	OPTIONAL_PARAMS = [
		"name", 			# The process binary name, e.g. cellapp, defaults
							# to the lowercase of the component name.
		"interfaceName", 	# The name of the interface this process serves.
							# Defaults to the component name + "Interface".
							# This is short-hand for 
							# 	interfaceNames = [interfaceName]
		"interfaceNames", 	# The names of every interface this process serves.
							# Overrides interfaceName.
		"isSingleton",		# Whether this process is a singleton process.
		"sinceVersion", 	# The first version that introduced this component.
		"lastVersion", 		# The last version that had this component.
		"isStartable", 		# Whether this process can be started by the server
							# tools.
		"requiresOwnCPU",	# Whether this process is preferred to be on its
							# own dedicated machine.
		"multiplierWeight",	# When allocating for multiple processes of this
							# type across the available machines, this is used
							# as the relative ratio for carving up the
							# available CPU for this process. So if CellApp is
							# 5 and BaseApp is 3, and total sum of all process
							# weights is N, then there should be roughly 5 / N
							# CellApps and 3 / N BaseApps.
		"isExclusive",		# When allocating machines automatically, try to
							# allocate a dedicated machine for this process, if
							# possible.
	]

	def __init__( klass, name, bases, dct ):

		ExposedType.__init__( klass, name, bases, dct )

		if not hasattr( klass, "meta" ):
			# Don't have to register this one.
			return

		# Check required metadata is set if it exists.
		for param in ProcessMeta.REQUIRED_PARAMS:
			if not hasattr( klass.meta, param ):
				raise RuntimeError( "Process class %s does not have "
					"complete meta-data" % name )

		# Fill out the rest of meta data derivable from component name if it's
		# not specified explicitly.
		optionals = [('name', klass.meta.componentName.lower()),
			('interfaceNames', getattr( klass.meta, "interfaceNames",
				[getattr( klass.meta, "interfaceName", 
					klass.meta.componentName + "Interface" )])),
			('isSingleton', False),
			('sinceVersion', None),
			('lastVersion', None),
			('isStartable', True),
			('requiresOwnCPU', False),
			('multiplierWeight', None),
			('isExclusive', False)]

		for param, default in optionals:
			if not hasattr( klass.meta, param ):
				setattr( klass.meta, param, default )

		Process.types.addProcessClass( klass )
	
# end class ProcessMeta


class Process( Exposed ):
	"""
	Represents a process in a BigWorld cluster.

	Subclasses that represent real process types should define an inner class
	named "meta", which serves as a namespace to hold various meta-attributes
	about process types. Refer to ProcessMeta.REQUIRED_PARAMS and
	ProcessMeta.OPTIONAL_PARAMS for more information.
	"""

	__metaclass__ = ProcessMeta
	types = Processes()


	def __init__( self, machine, mgm ):

		Exposed.__init__( self )
		self.hasPythonConsole = False
		self.isRetirable = False
		self.generatesLogs = True
		self.machine = machine
		self.component = mgm.name
		self.uid = mgm.uid
		self.pid = mgm.pid
		self.id = mgm.id
		self.load = mgm.load / 255.0
		self.mem = mgm.mem / 255.0
		self.mute = False
		self.mercuryPort = socket.ntohs( mgm.port )

		self.version = \
			Version( mgm.majorVersion, mgm.minorVersion, mgm.patchVersion )

		self.interfaceVersion = mgm.interfaceVersion
		self.username = mgm.username
		self.defDigest = mgm.defDigest

		if hasattr( self, "meta" ):
			self.name = self.meta.name
		elif mgm.category == mgm.WATCHER_NUB:
			self.name = re.sub( "\d+$", "", self.component )
		else:
			self.name = self.component

		# This the watcher port for this process.  This is private to force
		# everyone to go via port() and addr()
		if not hasattr( self, "_port" ):
			self._port = None

		self.supportWebConsoleProfiler = None


	def __str__( self ):
		return "%-15s on %-8s %2d%% cpu  %2d%% mem  pid:%d version:%s" % \
			   (self.label(), self.machine.name,
				self.load * 100, self.mem * 100, self.pid, str( self.version ))

	def __cmp__( self, other ):
		"""
		Sorts world processes first, alphabetically otherwise.
		"""

		# Early breakout on type error
		if not isinstance( other, Process ):
			return -1

		classCmp = Process.classComparator( self.__class__, other.__class__ )
		if classCmp != 0:
			return classCmp

		return cmp( self.name, other.name )


	def __json__( self ):
		apiAttributes = [ "load", "username", "uid", "mem", "component",
			"pid", "generatesLogs", "hasPythonConsole", "id", 
			"interfaceVersion", "isRetirable", "name", "mercuryPort",
			"machine", "version"]
		out = dict( [(attr, getattr( self, attr )) for attr in apiAttributes] )

		out['label'] = self.label()
		out['isStoppable'] = isinstance( self, StoppableProcess )
		out['isSingletonProcess'] = self.isSingleton()
		out['type'] = self.componentName()
		return out
	# __json__


	def isSingleton( self ):
		"""This method returns True if this process is a singleton process."""
		if hasattr( self, "meta" ):
			return self.meta.isSingleton
		else:
			return False


	def requiresOwnCPU( self ):
		"""This method can be used to decide whether a process should be run on
			its own CPU/core."""

		if hasattr( self, "meta" ):
			return self.meta.requiresOwnCPU
		else:
			return False


	def getExposedID( self ):
		return dict( type = "process", machine = self.machine.name,
					 pid = self.pid )


	def label( self ):
		if self.component == "bots":
			return "%s:%s:%s" % (
					self.name, self.machine.name, self.mercuryPort )
		elif self.id > 0:
			return "%s%02d" % (self.name, self.id)
		else:
			return self.name


	def status( self ):
		"""Returns a string representation of the status of the current process.
			This enables access to the DBApp's new statusDetail watcher, and
			provides the ability for similar functionality to be added to other
			server process types."""

		if self.name == "dbapp":
			return self.getWatcherValue( "status", "" )
		else:
			return ""


	def isProduction( self ):
		return self.getWatcherValue( "isProduction", False )

	def supportsTCPWatchers( self ):
		return self.version >= (2,0,0)


	# This is to test whether this process can work with Profiler of WebConsole
	def getSupportWebConsoleProfiler( self ):
		if self.supportWebConsoleProfiler != None:
			return self.supportWebConsoleProfiler

		# This is new added for the Profiler of WebConsole
		categoriesdData = self.getWatcherData( "profiler/controls/categories" )
		if categoriesdData.value != None:
			self.supportWebConsoleProfiler = True
		else:
			self.supportWebConsoleProfiler = False

		return self.supportWebConsoleProfiler


	def componentName( self ):
		if hasattr( self, "meta" ):
			return self.meta.componentName
		else:
			return self.name

	def addr( self ):
		return (self.machine.ip, self.port())

	def port( self ):
		"""
		Returns the port number of the watcher nub for this process, but if it
		is unknown as yet, discovers it first.

		Generally, this is OK to do for small query sets because it doesn't time
		out, but if you know you're going to need a lot of watcher ports ahead
		of time, query them beforehand with Cluster.getWatcherPorts() because it
		uses broadcast and is more network efficient.
		"""

		if self._port is None:
			psm = messages.ProcessStatsMessage()
			psm.param = psm.PARAM_USE_CATEGORY | psm.PARAM_USE_PID
			psm.category = psm.WATCHER_NUB
			psm.pid = self.pid

			replies = psm.query( self.machine )
			if replies:
				if replies[0].pid > 0:
					self._port = socket.ntohs( replies[0].port )
				else:
					del self.machine.procs[ self.pid ]
			else:
				log.error( "Could not get watcher port for %s on %s",
						   self.name, self.machine.name )

		return self._port

	def watcherAddr( self ):
		port = int( self.getWatcherValue( "viewer server port" ) )
		return (self.machine.ip, port)

	def user( self ):
		return self.machine.cluster.getUser( self.uid, self.machine )

	def hasWatchers( self ):
		return True

	def getWatcherData( self, path ):
		return WatcherData( self, path )

	def getWatcherValue( self, path, default=None ):
		"""Slightly quicker way to query a single Watcher value."""

		# If this process has been marked as mute, then just return the default
		# immediately
		if self.mute:
			return default

		v = self.getWatcherData( path ).value
		if v != None:
			return v
		else:
			return default

	def setWatcherValue( self, path, value ):
		"""Set the watcher value at the given path to the given value.  This is
		   defined in Process rather than WatcherData because more often than
		   not a Watcher set command does not need the whole hierarchical
		   WatcherData thing going on."""

		(status, returnValue) = self._setWatcher( path, value )

		if status:
			self._checkWatcherSetReturnValue( value, returnValue )

		return status


	def setWatcherValues( self, watcherValues ):
		"""Set a series of watchers from the watcherValues sequence of tuples.
		A tuple is a pair of ( watcherPath, valueToSet ). This is more efficient
		than repeated calls to setWatcherValue.

		Returns True if all the sets succeeded, and False otherwise"""

		log.debug( "Attempting to set watchers: %s", ",".join(
			[ watcherValue[ 0 ] for watcherValue in watcherValues ] ) )

		wdm = watcher_data_message.WatcherDataMessage()
		wdm.message = wdm.WATCHER_MSG_SET2
		wdm.count = 0

		for path, value in watcherValues:
			# Ensure path is a string
			path = str( path );
			wdm.addSetRequest( path, value )

		sock = socketplus.socket()
		sock.sendto( wdm.get(), self.addr() )
		sock.settimeout( 2 )

		# Recv replies until the right one comes through
		while True:
			try:
				data, srcaddr = sock.recvfrom( RECV_BUF_SIZE )
			except socket.timeout:
				break

			if srcaddr != self.addr():
				log.warning( "Got reply from wrong address: %s:%d", *srcaddr )
				continue

			# Re-use the same WDM as was used to send the request so we
			# can use the sequence number as validation of response.
			wdm.set( data )

			if wdm.count == 0:
				log.error( "Expected %d replies on set watcher reply packet, "
						   "got empty packet instead", len( watcherValues ) )
				continue

			if wdm.count != len( watcherValues ):
				log.warning( "Expected %d replies to " +
							 "setWatcherValue(), got:\n%s",
								 len( watcherValues ), wdm )
				continue

			badReply = False
			result = True
			for i in range( len( watcherValues ) ):
				reply = wdm.getReply( i )
				replyPath = wdm.getWatcherPathFromSeqNum( reply[ 0 ] )
				path, value = watcherValues[ i ]
				if replyPath != path:
					log.warning( "Incorrect reply to setWatcherValue(): %s" % \
								replyPath )
					badReply = true
					break
				else:
					# Watcher protocol 2 specifies the status of the set operation
					# as part of the response, so let's use it.
					result &= reply[4]

					if reply[4]:
						self._checkWatcherSetReturnValue( value, reply[3] )

			if badReply:
				continue

			return result

		return False


	def getWatcherValues( self, paths ):
		try:
			watcherResponse = WatcherDataMessage.batchQuery( paths, [ self ] )
		except Exception, e:
			 log.error( "Watcher batch query failed: %s", e )
			 return None

		responseDict = watcherResponse[ self ]
		watcherValues = {}

		for path in paths:
			watcherValues[ path ] = responseDict[ path ][0][1]

		return watcherValues


	def callWatcher( self, path, *params ):
		"""Call a watcher at the given path with the remaining parameters. A
		tuple containing a success as a bool and the watcher's return value is
		returned."""
		return self._setWatcher( path, params )


	def _setWatcher( self, path, value ):
		"""Call or set a watcher at the given path to the given value. A tuple
		containing a success as a bool and the watcher's return value is
		returned."""

		log.debug( "Attempting to set watcher '%s'", path )

		# Force string conversion
		path = str( path ); #value = str( value )

		wdm = watcher_data_message.WatcherDataMessage()
		wdm.message = wdm.WATCHER_MSG_SET2
		wdm.count = 0

		wdm.addSetRequest( path, value )

		sock = socketplus.socket()
		sock.sendto( wdm.get(), self.addr() )
		sock.settimeout( 2 )

		# Recv replies until the right one comes through
		while True:
			try:
				data, srcaddr = sock.recvfrom( RECV_BUF_SIZE )
			except socket.timeout:
				break

			if srcaddr != self.addr():
				log.warning( "Got reply from wrong address: %s:%d", *srcaddr )
				continue

			# Re-use the same WDM as was used to send the request so we
			# can use the sequence number as validation of response.
			wdm.set( data )

			if wdm.count == 0:
				log.error( "Expected single reply on set watcher reply packet, "
						   "got empty packet instead" )
				continue

			if wdm.count > 1:
				log.warning( "Expected single reply to " +
							 "setWatcherValue(), got:\n%s" % wdm )
				continue

			reply = wdm.getReply(0)
			replyPath = wdm.getWatcherPathFromSeqNum( reply[0] )
			if replyPath != path:
				log.warning( "Incorrect reply to setWatcherValue(): %s",
					replyPath )
				continue
			else:
				# Watcher protocol 2 specifies the status of the set operation
				# as part of the response, so let's use it.
				status = reply[4]
				returnValue = reply[3]

				return (status, returnValue)

		return (False, None)

	def kill( self, signal = None ):
		self.machine.killProc( self, signal )

	#--------------------------------------------------------------------------
	# Subsection: Static methods
	#--------------------------------------------------------------------------

	@staticmethod
	def cmpByLoad( p1, p2 ):
		return Machine.cmpByLoad( p2.machine, p1.machine )

	@classmethod
	def cmpByName( klass, n1, n2 ):
		processClass1, processClass2 = [klass.types.all.get( n, None )
			for n in (n1.lower(), n2.lower())]
		return klass.classComparator( processClass1, processClass2 )

	@staticmethod
	def classComparator( k1, k2 ):
		# None goes last
		if k1 is None and k2 is None:
			return 0

		if k1 is None or k2 is None:
			return [-1, 1][k1 is None]

		# Un-typed Processes before that.
		if (k1 is not Process) != (k2 is not Process):
			return [-1, 1][k1 is Process]

		# Meta-less classes before that.
		if hasattr( k1, "meta" ) != hasattr( k2, "meta" ):
			return [-1, 1][not hasattr( k1, "meta" )]

		# If neither has meta, then sort on name
		if not hasattr( k1, "meta" ): # and not hasattr( k2, "meta" )
			return cmp( k1.name, k2.name )

		# Order registered processes.
		metaAttrOrder = ["isSingleton", "isRequired", "isServerProc",
			"isStartable"]
		for metaAttr in metaAttrOrder:
			if getattr( k1.meta, metaAttr ) != \
					getattr( k2.meta, metaAttr ):
				return [-1, 1][not getattr( k1.meta, metaAttr )]

		return cmp( k1.meta.name, k2.meta.name )

	@staticmethod
	def clean( name ):
		"""Strip digits from a process name to reveal its type."""
		return re.sub( "[0-9]", "", name )

	@classmethod
	def getProcess( klass, machine, mgm ):
		processClass = Process

		if mgm.name in Process.types.interfaceMap:
			processClass = Process.types.interfaceMap[ mgm.name ]
		elif mgm.name in Process.types:
			processClass = Process.types[ mgm.name ]

		out = processClass( machine, mgm )
		return out


	@staticmethod
	def getPlural( name, count = 0 ):
		if count == 1:
			return str( name )

		if name[-1] == "s":
			return str( name )
		else:
			return str( name ) + "s"


	@staticmethod
	def _checkWatcherSetReturnValue( setValue, returnValue ):
		"""Confirm that the value returned by a watcher set message is
		the same as the value we sent.

		Returns True if the value was the same, returns False and logs an
		info-level message if it does not match
		"""
		isSame = True

		import watcher_data_type as WDT

		if isinstance( setValue, WDT.WatcherDataType ):
			if returnValue != setValue.value:
				isSame = False

		elif type(returnValue) == type(setValue):
			if returnValue != setValue:
				isSame = False

		elif str(returnValue) != str(setValue):
			# If the response isn't a bool, or the lower case
			# conversion of both setValue and returnValue doesn't
			# match up, then we know for certain that we've
			# failed.
			if (type(returnValue) != bool) or \
					(str(returnValue).lower() != str(setValue).lower()):
				isSame = False

		if not isSame:
			log.info( "Value returned = '%s'. Value set = '%s'" %
						(returnValue, setValue) )

		return isSame


	@classmethod
	def isInVersion( klass, version ):
		"""
		This class method returns whether the process type existed in the given
		version.
		"""
		if not hasattr( klass, "meta" ):
			# Not a registered process, shouldn't care, but assume they exist
			# in all versions.
			return True

		if version is None:
			return True

		if klass.meta.sinceVersion is None and klass.meta.lastVersion is None:
			# Exists for all known time.
			return True

		if (klass.meta.sinceVersion is not None) and \
				(version < klass.meta.sinceVersion):
			# Didn't exist yet in this version.
			return False

		if (klass.meta.lastVersion is not None) and \
				(version > klass.meta.lastVersion):
			# It was deleted before this version.
			return False

		return True


	@classmethod
	def sumMultiplierWeights( klass ):
		return sum( processClass.meta.multiplierWeight
			for processClass in klass.types.all.itervalues()
			if processClass.meta.multiplierWeight is not None )


#------------------------------------------------------------------------------
# Section: StoppableProcess
#------------------------------------------------------------------------------

class StoppableProcess( Process ):

	def __init__( self, machine, mgm ):
		Process.__init__( self, machine, mgm )

	#--------------------------------------------------------------------------
	# Subsection: Exposed stuff
	#--------------------------------------------------------------------------

	def stop( self, signal = None ):

		if signal is None:
			signal = messages.SignalMessage.SIGINT

		mgm = messages.SignalMessage()
		mgm.signal = signal
		mgm.pid = self.pid
		mgm.uid = self.uid
		mgm.param = mgm.PARAM_USE_UID | mgm.PARAM_USE_PID
		mgm.send( socketplus.socket(), self.machine.ip )


	def stopNicely( self ):
		self.stop()


#------------------------------------------------------------------------------
# Section: ScriptProcess
#------------------------------------------------------------------------------

class ScriptProcess( Process ):

	def __init__( self, machine, mgm ):
		Process.__init__( self, machine, mgm )


	@Exposed.expose()
	def reloadScript( self ):
		import run_script
		return run_script.runscript( [self], "BigWorld.reloadScript()", True )

#------------------------------------------------------------------------------
# Section: Specific Process implementations
#------------------------------------------------------------------------------

class CellAppMgrProcess( StoppableProcess ):
	class meta:
		componentName = "CellAppMgr"
		isRequired = True
		isSingleton = True
		isServerProc = True

	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )


	def shouldOffload( self, enable ):
		import memory_stream
		stream = memory_stream.MemoryStream()
		stream.pack( ("BBB", 0, 9, enable) )
		sock = socketplus.socket()
		sock.sendto( stream.data(), (self.machine.ip, self.mercuryPort) )


class CellAppProcess( StoppableProcess, ScriptProcess ):
	class meta:
		componentName = "CellApp"
		isRequired = True
		isServerProc = True
		isExclusive = True 
		multiplierWeight = 5.0

	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )
		self.hasPythonConsole = True
		self.isRetirable = True


	def retireApp( self ):
		self.callWatcher( "command/retireCellApp" )


class BaseAppProcess( StoppableProcess, ScriptProcess ):
	class meta:
		componentName = "BaseApp"
		isRequired = True
		isServerProc = True
		interfaceNames = ["BaseAppIntInterface", "BaseAppInterface"]
		isExclusive = True
		multiplierWeight = 3.0

	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )
		self.hasPythonConsole = True
		self.isRetirable = True

	def retireApp( self ):
		self.callWatcher( "command/retireBaseApp" )


class ServiceAppProcess( BaseAppProcess ):
	class meta:
		componentName = "ServiceApp"
		isRequired = False
		isServerProc = True
		sinceVersion = Version( 2, 1 )
		isExclusive = True 
		multiplierWeight = None # This makes it so we only start one ServiceApp.

	def retireApp( self ):
		self.callWatcher( "command/retireServiceApp" )


class BaseAppMgrProcess( StoppableProcess ):
	class meta:
		componentName = "BaseAppMgr"
		isRequired = True
		isSingleton = True 
		isServerProc = True

	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )


class LoginAppProcess( StoppableProcess ):
	class meta:
		componentName = "LoginApp"
		interfaceNames = ["LoginInterface", "LoginIntInterface"]
		isRequired = True
		isServerProc = True
		isExclusive = False 

	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )

	def statusCheck( self, verbose = True ):
		(isWatcherOkay, returnValue) = \
			self.callWatcher( "command/statusCheck" )

		try:
			(output, status) = returnValue
		except TypeError:
			return False

		if output.value.strip() and verbose:
			print output.value,

		return isWatcherOkay and status.value


class DBAppProcess( StoppableProcess ):
	class meta:
		componentName = "DBApp"
		isRequired = True
		isServerProc = True
		sinceVersion = Version( 2, 10 )
		requiresOwnCPU = True
		isExclusive = True 


	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )
		self.hasPythonConsole = True
		self.isRetirable = True


	def retireApp( self ):
		self.callWatcher( "command/retireDBApp" )


class DBAppMgrProcess( StoppableProcess ):
	class meta:
		componentName = "DBAppMgr"
		isRequired = True
		isSingleton = True
		isServerProc = True
		sinceVersion = Version( 2, 10 )

	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )
		self.hasPythonConsole = False


class DBMgrProcess( StoppableProcess ):
	class meta:
		componentName = "DBMgr"
		interfaceName = "DBInterface"
		isRequired = True 
		isSingleton = True
		isServerProc = True
		lastVersion = Version( 2, 9 )
		requiresOwnCPU = True

	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )
		self.hasPythonConsole = True


class ReviverProcess( StoppableProcess ):
	class meta:
		componentName = "Reviver"
		isRequired = False 
		isServerProc = False

	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )

	def hasWatchers( self ):
		# Revivers only support Watchers in 2.0 onwards
		return (self.version.major >= 2)


class BotProcess( StoppableProcess ):
	class meta:
		componentName = "Bots"
		isRequired = False 
		isServerProc = False
		isExclusive = True
		multiplierWeight = 2.0

	# technically, it is a script process, but it does not have a
	# BigWorld.reloadScript method
	def __init__( self, machine, mgm ):
		StoppableProcess.__init__( self, machine, mgm )
		self.hasPythonConsole = True
		self._nbots = None


	def __str__( self ):
		return StoppableProcess.__str__( self ) + " [%d bots]" % self.nbots()


	@Exposed.expose( args = [("num", "the number of bots to add", 1)] )
	def addBots( self, num ):
		"""
		Add bots to this bot process.
		"""
		if self.version < ( 2, 6, 0 ):
			self.setWatcherValue( "command/addBots", num )
		else:
			self.callWatcher( "command/addBots", int( num ) )


	@Exposed.expose( args = [("num", "the number of bots to delete", 1)] )
	def delBots( self, num ):
		"""
		Delete bots from this bot process.
		"""
		if self.version < ( 2, 6, 0 ):
			self.setWatcherValue( "command/delBots", num )
		else:
			self.callWatcher( "command/delBots", int( num ) )


	def nbots( self, n = None ):
		"""
		Setter/getter for the number of bots hosted on this bot process.
		"""

		# Get
		if n is None:
			if self._nbots is None:
				self._nbots = int( self.getWatcherValue( "numBots", 0 ) )
			return self._nbots

		# Set
		else:
			self._nbots = n


class ClientProcess( Process ):
	class meta:
		componentName = "Client"
		isRequired = False
		isServerProc = False
		isStartable = False

	def __init__( self, machine, component, id, pid, uid, load, mem ):
		Process.__init__( self, machine, component, id, pid, uid, load, mem )
		self.name = "client"


class MessageLoggerProcess( Process ):
	class meta:
		componentName = "MessageLogger"
		name = "message_logger"
		isRequired = False
		isServerProc = False
		isStartable = False

	# Log messages originating from python consoles in the the server do not have
	# fully parsed args - instead they have a format string of %s and a single arg
	# containing the pre-interpolated message text.
	PYTHON_MESSAGE_FORMAT = "%s"

	def __init__( self, machine, mgm ):
		Process.__init__( self, machine, mgm )
		self.generatesLogs = False


	@Exposed.expose( label = "Roll Logs" )
	def breakSegments( self ):
		mgm = messages.SignalMessage()
		mgm.signal = signal.SIGHUP
		mgm.pid = self.pid
		mgm.uid = self.uid
		mgm.param = mgm.PARAM_USE_UID | mgm.PARAM_USE_PID
		mgm.send( socketplus.socket(), self.machine.ip )


	@Exposed.expose( args = [("user", "the username to log as"),
							 ("message", "the log message")] )
	def sendMessage( self, message, user, severity = "INFO", category = "" ):
		"""
		Send the message to this logger, as the given user.  'user' can be
		passed as a string, in which case the User object is looked up.
		"""

		try:
			import bwlog

		except ImportError, e:
			log.warning( "Failed to import bwlog.so on this system: %s", e )
			log.warning( "Recompiling the extension in "
						 "bigworld/src/server/tools/message_logger "
						 "will probably fix this" )

		if type( user ) == str:
			user = self.machine.cluster.getUser( user )

		# Make sure socket is bound to a specific address (not INADDR_ANY) so
		# that it can deregister properly
		sock = socketplus.socket()
		uid = user.uid
		lcm = messages.LoggerComponentMessage( uid, MESSAGE_LOGGER_NAME )
		wdm = watcher_data_message.WatcherDataMessage()

		# Register this process with the logger
		stream = wdm.getExtensionStream( bwlog.MESSAGE_LOGGER_REGISTER )
		lcm.write( stream )
		sock.sendto( wdm.get(), self.addr() )

		# Send the message
		componentPriority = 0
		messagePriority = bwlog.SEVERITY_LEVELS[ severity ]
		messageSource = messages.MESSAGE_SOURCE_SCRIPT
		header = messages.LoggerMessageHeader( componentPriority,
					messagePriority, messageSource, category )

		stream = wdm.getExtensionStream( bwlog.MESSAGE_LOGGER_MSG )
		header.write( stream )
		stream.pack( MessageLoggerProcess.PYTHON_MESSAGE_FORMAT )
		stream.pack( message )
		sock.sendto( wdm.get(), self.addr() )

		# Deregister this process with the logger
		stream = wdm.getExtensionStream( bwlog.MESSAGE_LOGGER_PROCESS_DEATH )
		addr, port = sock.getsockname()
		stream.pack( ("4sHxx",
					  socket.inet_aton( "0.0.0.0" ), socket.htons( port )) )
		sock.sendto( wdm.get(), self.addr() )

from watcher_data import WatcherData
from cluster import Cluster
from machine import Machine

# process.py
