import cluster
import logging
import messages
import random
import re
import operator
import socketplus
import sys
import time
import types
import util
import watcher_data_message

from exposed import Exposed
from xml.dom import minidom

from StringIO import StringIO

from cluster_constants import CELL_ENTITY_ADJ
from cluster_constants import MAX_SERVER_CPU
from cluster_constants import POLL_SLEEP
from cluster_constants import MAX_POLL_SLEEPS
from cluster_constants import MAX_STARTUP_SLEEPS
from cluster_constants import RECV_BUF_SIZE

from cluster_constants import NBOTS_AT_ONCE
from cluster_constants import MAX_BOTS_CPU
from cluster_constants import CPU_WAIT_SLEEP
from cluster_constants import BW_SUPPORTED_CONFIGS
from cluster_constants import BW_CONFIG_HYBRID

log = logging.getLogger( __name__ )


# ------------------------------------------------------------------------------
# Section: Utility classes 
# ------------------------------------------------------------------------------

class LoadStats( object ):
	def __init__( self, min, avg, max ):
		self.min = min
		self.avg = avg
		self.max = max

	def __str__( self ):
		return "%.2f %.2f %.2f" % (self.min, self.avg, self.max )


class ProcessMachineAllocation( object ):
	"""
	This class tracks and handles allocations of a process type to a set of
	machines, and is used when starting a server across a group of machines
	using a procedurally generated layout.
	"""

	def __init__( self, processClass, **startKWArgs ):
		"""
		Constructor.

		@param processClass		The class of the process to start.
		@param startKWArgs		Keyword arguments to pass to User.startProc().
		"""
		self._processClass = processClass
		self._totalCPU = 0.0
		self._machines = []
		self._startKWArgs = startKWArgs

	
	@property
	def processName( self ):
		"""
		The name of the process.
		"""
		return self._processClass.meta.name


	@property
	def totalCPU( self ):
		"""
		The total amount of CPU allocated to this process type.
		"""
		return self._totalCPU


	@property
	def machines( self ):
		"""
		The machines allocated to this process type.
		"""
		return list( self._machines )


	@property
	def hasMachine( self ):
		"""
		Whether this process has been added to a machine.
		"""
		return len( self._machines ) > 0


	@property
	def canTolerateStartupFailure( self ):
		"""
		True if the successful starting of processes of this type is optional.
		"""
		return not self._processClass.meta.isRequired


	@property
	def multiplier( self ):
		"""
		The multiplier to apply to the CPU allocated to this process type.
		"""
		if self.multiplierWeight is None:
			return None

		return Process.sumMultiplierWeights() / self.multiplierWeight


	@property
	def multiplierWeight( self ):
		"""
		The weighting to use when allocating machines to this process type.
		"""
		return self._processClass.meta.multiplierWeight


	@property
	def isExclusive( self ):
		"""
		Whether this process is prefers to be on a dedicated machine.
		"""
		return self._processClass.meta.isExclusive


	@property
	def isSingleton( self ):
		"""
		Whether this process is a singleton process.
		"""
		return self._processClass.meta.isSingleton


	def __cmp__( self, other ):
		"""Comparison operator. """

		# Processes with multiplier == None are considered to be the lowest
		# so that they will be allocated first.  

		if self.multiplierWeight is None or other.multiplierWeight is None:
			return cmp( self.multiplierWeight, other.multiplierWeight )
		
		# Among processes with multipler weights defined, sort by lowest CPU
		# allocation to highest.
		result = cmp( self.totalCPU * self.multiplier,
						other.totalCPU * other.multiplier ) 
		if result != 0:
			return result

		# In the event of CPU allocation ties, the process type with the higher
		# multiplier weight is considered to be have precedence since this will
		# cause it to be allocated to a slower CPU.
		return -cmp( self.multiplierWeight, other.multiplierWeight )

	
	def add( self, machine ):
		"""
		Add a process of this type to the given machine.
		
		@param machine 	The machine to start a process on.
		@return 		The PID if successful, otherwise None.
		"""
		self._totalCPU += max( 1 - machine.load(), 0 ) * machine.totalmhz()
		self._machines.append( machine )

		pid = machine.startProc( self.processName, **self._startKWArgs )

		if pid == 0:
			if self.canTolerateStartupFailure:
				log.debug( "Failed to start a %s (non-fatal)", 
					self.processName )
			else:
				log.error( "Couldn't even execute %s on %s",
					self.processName, machine.name )
			return None 

		log.debug( "Starting %s on %s", self.processName, machine.name )
		return pid


	def __repr__( self ):
		"""
		This method returns the string representation.
		"""
		if self.multiplierWeight is not None:
			return "<%s: (x %.03f): actual: %.03f : effective %.03f>" % \
				(self.processName, self.multiplierWeight, self.totalCPU, 
					self.multiplier * self.totalCPU)
		else:
			return "<%s: %.03f>" % (self.processName, self.totalCPU)

# end class ProcessMachineAllocation


class UserError( Exception ): 
	"""This exception is raised when a user can't be found."""
	pass


# ------------------------------------------------------------------------------
# Section: User
# ------------------------------------------------------------------------------

class User( Exposed ):
	"""
	Info about a user, and methods to query info about the server a user is
	running.

	The 'uid' param passed here can either be the username or the UID or an MGM
	that already has all the details in it.
	"""

	def __init__( self, uid, cluster, machine = None,
				  checkCoreDumps = False,
				  refreshEnv = False,
				  fetchVersion = False ):

		Exposed.__init__( self )
		self.cluster = cluster

		# Request the user info from the server if not already given
		if not isinstance( uid, messages.UserMessage ):

			mgm = messages.UserMessage()

			if type( uid ) == int:
				mgm.param = mgm.PARAM_USE_UID
				mgm.uid = uid
			elif isinstance( uid, types.StringTypes ):
				mgm.param = mgm.PARAM_USE_NAME
				mgm.username = uid.encode( "utf-8" )
			else:
				raise ValueError( "First param to User() must be an " +
							  "int, string or UserMessage, not %s" %
							  uid.__class__.__name__ )

			if checkCoreDumps:
				mgm.param |= mgm.PARAM_CHECK_COREDUMPS

			if refreshEnv:
				mgm.param |= mgm.PARAM_REFRESH_ENV

			if not machine:
				candidates = [m for m in cluster.getMachines()
					if uid not in m.unknownUsers]
			else:
				candidates = [machine]

			random.shuffle( candidates )
			# Stable sort will preserve random-ness, but group it by machined
			# version.
			candidates.sort( key = lambda m: m.machinedVersion )

			machine = None
			while candidates and machine is None:
				machine = candidates.pop( -1 )

				if fetchVersion and machine.supportsVersionString:
					# Don't set param or send version string for earlier
					# machined's that don't understand it.
					mgm.param |= mgm.PARAM_GET_VERSION
					versionRequested = True
				else:
					versionRequested = False

				replies = mgm.query( machine )

				if not replies:
					log.error( "%s:%s didn't reply to UserMessage",
						machine.name, machine.ip)
					machine = None

				elif replies[0].uid == mgm.UID_NOT_FOUND:
					log.debug( "%s:%s couldn't resolve user %s, "
							"will not ask again",
						machine.name, machine.ip, uid )
					machine.unknownUsers.add( uid )
					machine = None

				elif versionRequested and not replies[0].versionString:
					# Keep going if we couldn't get binaries on this machine -
					# probably because it's missing a filesystem mount.
					if candidates and candidates[-1].supportsVersionString:
						# If there is at least one more machined that supports
						# the version string, keep trying.
						log.debug( "Skipping machine \"%s\" due to absence of "
								"version string from machined that should "
								"support it",
							machine.name )
						machine = None
					else:
						mgm = replies[0]

				else:
					mgm = replies[0]

			if machine is None:
				raise UserError, "No machines on network able " \
					  "to resolve user %s" % uid

		else:
			mgm = uid

		self.uid = mgm.uid
		self.name = mgm.username
		self.fullname = mgm.fullname
		self.home = mgm.home
		self.mfroot = mgm.mfroot
		self.bwrespath = mgm.bwrespath
		self.coredumps = mgm.coredumps
		# Assume we are running the latest version, unless we know otherwise.
		# This is so that we can still use older bwmachined to run newer
		# processes.
		self.version = Process.types.versions[-1]
		if mgm.versionString:
			self.version = Version.fromString( mgm.versionString )
		self._queryMachineName = ""
		if machine:
			self._queryMachineName = machine.name

		# Can be a hash of the min/avg/max loads for various server components
		self.load = None

		# Some counters only used when doing bots stuff
		self.totalBots = self.numProxies = self.numEntities = None


	def __str__( self ):
		return "%s (%d)" % (self.name, self.uid)

	def __cmp__( self, other ):
		if not isinstance( other, User ):
			return -1
		return cmp( self.name, other.name )

	def __hash__( self ):
		return hash( self.uid ) ^ hash( self.name )


	def __json__( self ):
		d = self.__dict__.copy()
		del d['cluster']
		return d
	# __json__


	def checkBwConfig( self, bwConfig ):
		return bwConfig in BW_SUPPORTED_CONFIGS


	def getLoad( self, name ):
		loads = self.getLoads()
		if loads.has_key( name ):
			return loads[ name ]
		else:
			return 0

	def getLoads( self ):

		if not self.load:
			self._getLoads()
		return self.load

	def getNumEntities( self ):

		if self.numEntities != None:
			return self.numEntities

		elif self.serverIsRunning():
			self.numEntities = int( self.getProc( "cellappmgr" ).
									getWatcherValue( "numEntities", 0 ) ) + \
									CELL_ENTITY_ADJ
			return self.numEntities
		else:
			return None

	def getNumProxies( self ):

		if self.numProxies != None:
			return self.numProxies

		elif self.serverIsRunning():
			self.numProxies = int( self.getProc( "baseappmgr" ).
								   getWatcherValue( "numProxies", 0 ) )
			return self.numProxies
		else:
			return None


	def getCoresSortedByTime( self ):
		def mycmp( x, y ):
			return cmp( x[2], y[2] )

		sortedCores = list( self.coredumps )
		sortedCores.sort()
		return sortedCores


	def getTotalBots( self ):

		if self.totalBots is None:
			self.totalBots = sum( map( lambda bp: bp.nbots(),
									   self.getProcs( "bots" ) ) )

		return self.totalBots

	def _getLoads( self ):

		# Argmin/max over reported machine CPU loads
		def botsLoad( f ):
			return f( [ p.load for p in self.getProcs( "bots" ) ] )

		# Macro for querying load watcher values
		def watcherload( cb, am ):
			return max(
				float( self.getProc( "%sappmgr" % cb ).\
					   getWatcherValue( "%sAppLoad/%s" % (cb, am), 0 ) ), 0.0 )

		# Mapping from name to LoadStats object for all those processes
		self.load = {}

		# Total up all known bots and calculate bot CPU usage
		if self.getProcs( "bots" ):
			def avg( x ):
				return sum( x ) / float( len( x ) )

			self.load[ "bots" ] = LoadStats( botsLoad( min ),
											 botsLoad( avg ),
											 botsLoad( max ) )

		# Some important stats

		# TODO: Scalable DB: Add support for DBApp loads here.
		# And remove the load inner functions above, implement them on the
		# Process subclasses.

		missingProcs = set()
		self.serverIsRunning( missingProcs )
		if not "cellapp"  in missingProcs and not "baseapp" in missingProcs:
			for name in [ "cell", "base" ]:
				self.load[ name + "app" ] = LoadStats(
					watcherload( name, "min" ),
					watcherload( name, "average" ),
					watcherload( name, "max" ) )

	# ------------------------------------------------------------------------
	# Subsection: Query methods
	# ------------------------------------------------------------------------

	# Convenience functions
	def getProc( self, name ):
		return self.cluster.getProc( name, self.uid )

	def getProcs( self, name=None, ignoreProcs=[] ):
		procs = self.cluster.getProcs( name, self.uid )
		return [p for p in procs if p.name not in ignoreProcs]

	def getServerProcs( self ):
		return [p for p in self.getProcs() 
			if p.name in Process.types.serverProcs()]

	# Return a this user's process that matches the given name exactly
	def getProcExact( self, name ):
		for p in self.getProcs():
			if p.label() == name:
				return p
		return None


	def serverIsRunning( self, missingProcs = None ):
		"""
		Returns True if this user appears to be running a proper bigworld
		server. If passed a set() as the missingProcs argument, this set
		will be populated with the names of missing processes (if any).
		"""

		userProcesses = self.getProcs()
		processSetNames = set( [p.name for p in userProcesses] )

		version = Process.types.matchVersionForProcesses( processSetNames )
		if version:
			return True
		
		# Server is not running for any known version.
		if missingProcs is None:
			return False

		# Determine what version we're meant to be.
		if userProcesses:
			# If we have running processes, we can get the version from one of
			# those.
			version = userProcesses[0].version
		else:
			version = self.version

		requiredProcesses = set( Process.types.required( version ).keys() )
		missingProcs.clear()
		missingProcs.update( requiredProcesses )
		missingProcs.difference_update( processSetNames )

		log.info( "BigWorld server not complete, missing procs: %r",
			missingProcs )

		return False
	# serverIsRunning


	def serverIsOverloaded( self ):
		"""Returns true if any machine running server components for this user
		is overloaded."""

		return self.getLoad( "cellapp" ).max > MAX_SERVER_CPU or \
			   self.getLoad( "baseapp" ).max > MAX_SERVER_CPU

	def getLayout( self ):
		layout = []
		for p in self.getServerProcs():
			layout.append( (p.machine.name, p.name, p.pid) )
		return layout

	def getLayoutStatus( self, layout, _async_ = None ):
		"""
		Takes a list of (mname, pname, pid) and returns a list of
		(mname, pname, pid, status).
		"""

		status = []
		notregistered = []

		shouldExtendTime = False

		# Check for registered processes first
		for mname, pname, pid in layout:
			m = self.cluster.getMachine( mname )
			if not m:
				status.append( (mname, pname, pid, "nomachine", "") )
				continue
			p = m.getProc( pid )
			if p:
				statusMsg = ""

				if _async_:
					# Avoid doing watcher query if not async
					procStatus = p.status()
					if p.name == "dbapp":
						# Process status of 6 == consolidating
						if procStatus != None and procStatus == 6:
							statusMsg = "Consolidating"
							shouldExtendTime = True

				status.append( (mname, pname, pid, "registered", statusMsg) )
			else:
				notregistered.append( (mname, pname, pid) )

		# Check unregistered processes to see if they are actually running
		for mname, pname, pid in notregistered:

			m = self.cluster.getMachine( mname )
			pm = messages.PidMessage()
			pm.pid = pid
			replies = pm.query( m )

			if not replies:
				log.error( "No reply to PidMessage from %s", mname )
				status.append( (mname, pname, pid, "nomachine", "") )
			elif replies[0].running:
				status.append( (mname, pname, pid, "running", "") )
			else:
				status.append( (mname, pname, pid, "dead", "") )

		# Figure out return counts
		dead = running = registered = 0

		for mname, pname, pid, state, details in status:
			if state == "dead": dead += 1
			if state == "running": running += 1
			if state == "registered": registered += 1

		# Notify async handlers
		if _async_:
			# If the DBApp is consolidating the secondary DB's then extend the async
			# process life
			if shouldExtendTime:
				_async_.extendTimeout( 1 )
			_async_.update( "status", dict( layout = status ) )

		return (dead, running, registered, status)


	def getLayoutErrors( self ):
		"""Return a list of strings containing error messages (if any) for the
		User's server layout."""

		# List of machines with bots running on them
		botMachines = {}
		errors = []
		machineInfo = {}

		dbMachine = None
		for proc in self.getProcs():

			if proc.requiresOwnCPU():
				uniqueProcs = machineInfo.get( proc.machine, 0 )
				uniqueProcs = uniqueProcs + 1
				machineInfo[ proc.machine ] = uniqueProcs

			if proc.name == "dbapp":
				dbMachine = proc.machine
				# DBApp should really be on a machine by itself
				if len( dbMachine.procs ) > 1:
					errors.append( "DBApp is running on a machine with other "
						"server processes." )

			elif proc.name == "bots":
				# if bots - add to machine array
				botMachines[ proc.machine.name ] = True

		# Now check if there are too many processes for each core
		for machine, uniqueCount in machineInfo.iteritems():
			if machine.ncpus < uniqueCount:
				errors.append( "Machine %s appears to be running too many processes "
					"for the number of available CPUs/cores." % machine.name )


		# If there are any bots running, check that the processes aren't running
		# on server machines with other processes such as dbapp/cellapp/baseapp
		errorBotMachines = []
		for botMachineName in botMachines.keys():
			for uniqueMachine in machineInfo.keys():
				if uniqueMachine.name == botMachineName:
					errorBotMachines.append( botMachineName )

		if len( errorBotMachines ) > 0:
			errors.append( "bots running on the following machines should "
				"be moved to less critical server machines: %s" % \
				", ".join( errorBotMachines ) )

		return errors


	def layoutIsRunning( self, layout, status = [], _async_ = None ):

		dead, running, registered, status[:] = \
					   self.getLayoutStatus( layout, _async_ )

		if running == 0 and dead > 0:
			raise Cluster.TerminateEarlyException
		else:
			return registered == len( layout )


	def layoutIsStopped( self, layout, status = [], _async_ = None ):

		dead, running, registered, status[:] = \
					   self.getLayoutStatus( layout, _async_ )

		return dead == len( layout )


	# ------------------------------------------------------------------------
	# Subsection: Output methods
	# ------------------------------------------------------------------------

	def lsMiscProcesses( self ):
		"""
		Print out info for misc processes.  Returns a list of the processes
		displayed.
		"""

		miscps = [p for p in self.getProcs() 
			if Process.clean( p.name ) in Process.types.singletons()] 

		if not miscps:
			log.info( "no misc processes found!" )
			return []
		miscps.sort( key = lambda x : x.label() )

		log.info( "misc processes:" )
		for p in miscps:
			log.info( "\t%s", p )

		return miscps


	def ls( self ):
		"""
		Prints detailed server info for a particular user.
		"""

		# Assemble a list of already-displayed processes
		displayed = self.lsMiscProcesses()

		# Quick macro to get all machines for a given component
		def displayMachinesForProcess( name, warn = True ):
			procs = self.getProcs( name )
			procs.sort( key = lambda x : ( x.label(), x.machine.name, x.pid ) )

			if procs:
				log.info( "%s (%d):" %
						  (Process.getPlural( name ), len( procs )) )
				for p in procs:
					log.info( "\t%s", p )

			elif warn:
				log.info( "no %s found!" % Process.getPlural( name ) )

			return procs

		# Display all the multi-apps
		displayed.extend( displayMachinesForProcess( "baseapp" ) )
		displayed.extend( displayMachinesForProcess( "cellapp" ) )
		displayed.extend( displayMachinesForProcess( "serviceapp" ) )
		if Process.types["dbapp"].isInVersion( self.version ):
			displayed.extend( displayMachinesForProcess( "dbapp" ) )

		# Display any processes not already done
		remaining = set( self.getProcs() ) - set( displayed )

		for pname in Process.types.startable():
			ps = [p for p in remaining if p.name == pname]
			if ps:
				displayMachinesForProcess( pname, False )

		# Display listing of used machines
		ms = util.uniq( [p.machine for p in self.getProcs()], cmp = cmp )
		ms.sort( key = lambda x : x.name )

		if ms:
			log.info( "\nmachines (%d):", len( ms ) )
			for m in ms:
				log.info( "\t%s", m.getFormattedStr() )

	def lsSummary( self ):
		"""Prints summarised info about this user's server."""

		# Can't go any further without a complete server
		if not self.serverIsRunning():
			log.error( "Server isn't running, can't display summary" )
			return

		# Find world server
		self.lsMiscProcesses()

		# Macro that displays a summary for a type of process
		def displaySummaryForProcess( name, warn = True ):
			procs = self.getProcs( name )
			if procs:
					log.info( "%d %s at (%s)" % \
						  (len( procs ),
						   Process.getPlural( name, len( procs ) ),
						   self.getLoad( name )) )
			elif warn:
				log.info( "no %s found!" % Process.getPlural( name ) )

		displaySummaryForProcess( "baseapp" )
		displaySummaryForProcess( "cellapp" )
		displaySummaryForProcess( "serviceapp" )
		if Process.types["dbapp"].isInVersion( self.version ):
			displaySummaryForProcess( "dbapp" )
		displaySummaryForProcess( "bots", False )

	# --------------------------------------------------------------------------
	# Subsection: Cluster control methods
	# --------------------------------------------------------------------------

	def verifyEnvSync( self, machines = [], writeBack = False ):
		"""
		Checks this users BW env settings on each machines (or entire network if
		machines == []) and warns if settings are out of sync.

		If writeBack is True, the largest set of machines with in-sync config
		settings will be written back to the passed-in 'machines' list.
		"""

		um = messages.UserMessage()
		um.param = um.PARAM_USE_UID | \
			um.PARAM_REFRESH_ENV | \
			um.PARAM_GET_VERSION
		um.uid = self.uid

		variants = {}

		replies = messages.MachineGuardMessage.batchQuery( [um], 1.0, machines )

		for reply, (ip, port) in replies[um]:

			if reply.mfroot or reply.bwrespath:
				pathConfig = reply.mfroot + ";" + reply.bwrespath
			else:
				pathConfig = "<undefined>"

			variantIPs = variants.setdefault( 
				(pathConfig, reply.versionString), set() )
			variantIPs.add( ip )

		if len( variants ) <= 1:
			return True

		if not writeBack:
			log.warning( "~/.bwmachined.conf or binary version differs on "
				"network:" )

			for (pathConfig, versionString), ips in variants.items():
				if versionString:
					log.warning( "%s (%s):", pathConfig, versionString)
				else:
					log.warning( "%s (indeterminate version):" % pathConfig)

				for ip in sorted( ips, util.cmpAddr ):
					m = self.cluster.getMachine( ip )
					if m:
						log.warning( m.name )
					else:
						log.error( "Unable to resolve hostname for %s", ip )

		else:
			biggest = sorted( variants.values(), key = len )[-1]
			machines[:] = map( self.cluster.getMachine, biggest )

		return False


	def start( self, machines = None, _async_ = None,
				bots = False, revivers = False, tags = False, group = None,
				useSimpleLayout = False, bwConfig = BW_CONFIG_HYBRID ):
		"""
		Start a server for this user.  If machines is not passed, all machines
		are considered as candidates.

		If 'bots' is True, bots processes will be allocated and started.

		If 'revivers' is True, a reviver will be started on each machine that a
		process of another type is.

		If 'tags' is True, machines will be restricted to starting process types
		listed in their [Components] tag list.

		If 'group' is defined, then only machines in that machined group will be
		considered.
		"""

		# Don't start up if we already have processes running
		if self.getServerProcs():
			log.error( "Server processes already running, aborting startup" )
			self.ls()
			return False

		if not self.checkBwConfig( bwConfig ):
			log.error( "Provided bwConfig not supported" )
			return False
		# Get server candidates
		if not machines:
			machines = self.cluster.getMachines()
		machines.sort( lambda m1, m2: cmp( m1.totalmhz(), m2.totalmhz() ) )

		# Verify that env is in sync
		if not self.verifyEnvSync( machines, writeBack = True ):
			log.warning( "Candidate machines restricted due to out-of-sync env"	)
			log.warning( "Candidate set is now %s",
						 ",".join( [m.name for m in machines] ) )

		# If group is specified, restrict machine set to that group now
		if group:
			self.cluster.queryTags( "Groups" )
			machines = [m for m in machines \
						if "Groups" in m.tags and group in m.tags[ "Groups" ]]
			log.debug( "Machines in group %s: %s",
						 group, " ".join( [m.name for m in machines] ) )

		log.debug( "Candidate machines:" )
		for m in machines:
			log.debug( m.getFormattedStr() )

		# Bail now if no candidates found
		if not machines:
			log.error( "No machines found satisfying the filters" )
			return False

		# List of server processes we expect to be running
		layout = []

		# Make a list of 'cpus' sorted by speed
		cpus = reduce( operator.concat, [ [m]*m.ncpus for m in machines ] )
		cpus.sort( lambda m1, m2: cmp( m1.mhz, m2.mhz ) )

		# If we are going to need to know about machine Components tags, get
		# them now
		if tags:
			self.cluster.queryTags( "Components", machines )

		def makeAllocation( processClass ):
			return ProcessMachineAllocation( processClass,
				uid = self.uid, _async_ = _async_, config = bwConfig )

		allAllocations = [ makeAllocation( processClass )
			for processClass in
				Process.types.serverProcs( self.version ).itervalues() ]

		if bots:
			allAllocations.append( makeAllocation( Process.types["bots"] ) )

		# Make a copy of the allocation list, because we'll want to modify it
		# in the CPU allocation loop
		allocations = list( allAllocations )
		# Make a log entry to say we're starting the server
		self.log( "Starting server" )

		# Allocate all CPUs to process types
		i = 0
		while cpus and allocations:

			# Pick the most needy process 
			allocation = min( allocations )

			# Find the slowest CPU that is capable of running this process type
			cpu = None
			for m in cpus:
				if not tags or m.canRun( allocation.processName ):
					cpu = m
					break

			# If no CPU found, stop trying to assign CPU to this process 
			# (we'll fix it up later if no CPUs were allocated)
			if not cpu:
				allocations.remove( allocation )
				continue

			# Add this process to that allocation
			pid = allocation.add( cpu )
			if not pid:
				if not allocation.canTolerateStartupFailure:
					log.error(
						"Process execution failure; shutting down server" )
					self.cluster.refresh()
					self.smartStop( forceKill=True )
					return False

				allAllocations.remove( allocation )
			else:
				layout.append( (cpu.name, allocation.processName, pid) )

			# If the allocation is exclusive, remove that CPU from the list
			if allocation.isExclusive:
				cpus.remove( cpu )

			# If the allocation is singleton, remove it from the list
			if allocation.multiplier is None or useSimpleLayout:
				allocations.remove( allocation )

				# If the allocation is singleton and there are no more singleton
				# allocations to make, remove the cpu (i.e. don't spawn other
				# stuff on the world server unless you have to)
				if not [a for a in allocations if a.multiplier is None] and \
					   cpu in cpus:
					cpus.remove( cpu )

		# If any allocation didn't get allocated any CPU, allocate it to the
		# fastest machine capable of running it now
		allocateFailed = False
		for allocation in [ a for a in allAllocations if not a.hasMachine ]:

			for m in machines[::-1]:
				if not tags or m.canRun( allocation.processName ):
					pid = allocation.add( m )
					if pid:
						layout.append( (m.name, allocation.processName, pid) )
					break

			if not allocation.hasMachine:
				log.error( "Couldn't find any machines capable of running %ss",
						   allocation.processName )
				allocateFailed = True

		if allocateFailed:
			log.error( "Some processes weren't started, aborting" )
			return False

		# Start revivers on all machines used if required
		if revivers:
			reviverAllocation = makeAllocation( Process.types["reviver"] )
			allAllocations.append( reviverAllocation )
			for m in machines:
				pid = reviverAllocation.add( m )
				if pid:
					layout.append( 
						(m.name, reviverAllocation.processName, pid) )

		for allocation in allAllocations:
			log.debug( "%s (%dMHz): %s" % \
						 (allocation.processName, allocation.totalCPU,
						  " ".join( [m.name for m in allocation.machines] )) )

		if layout and self.verifyStartup( layout, _async_ = _async_ ):
			self.ls()
			return True
		else:
			return False

	@staticmethod
	def parseXMLLayout( s ):
		"""
		Reads a server layout from an XML string, and returns a list of
		processes in the format [(machine_name, process_name) ...].  Note that
		this is not the format that is expected by layoutIsRunning(), it doesn't
		include the PIDs.  It is up to startFromXML() to include this itself.
		"""

		# TODO: There is very little error checking for the expected format of
		# the XML here.  If the XML is not specified exactly as required, the
		# resulting errors will probably not make much sense.

		doc = minidom.parseString( s )
		layout = []

		for pname in Process.types.startable():

			# Find the section of the XML tree that deals with these procs.  The
			# plural case is for compatibility with old layouts.
			nodes = doc.getElementsByTagName( pname ) or \
					doc.getElementsByTagName( Process.getPlural( pname ) )

			if not nodes: continue
			root = nodes[0]

			for child in filter( lambda n: n.attributes, root.childNodes ):

				# For "machine" elements
				if child.tagName == "machine":
					mname = child.getAttribute( "name" )
					count = child.getAttribute( "count" ) or "1"
					count = int( count )
					for i in xrange( count ):
						layout.append( (mname, pname) )

				# For "range" elements
				elif child.tagName == "range":
					prefix = child.getAttribute( "prefix" )
					start = int( child.getAttribute( "start" ) )
					end = int( child.getAttribute( "end" ) )
					format = child.getAttribute( "format" ) or "%d"
					count = child.getAttribute( "count" ) or "1"
					count = int( count )

					for i in xrange( start, end+1 ):
						mname = prefix + (format % i)
						for j in xrange( count ):
							layout.append( (mname, pname) )

		# Special-case for old-style layouts with the 'world' section
		worldNodes = doc.getElementsByTagName( "world" )
		if worldNodes:
			mname = worldNodes[0].getAttribute( "name" )
			for pname in Process.types.singletons():
				layout.append( (mname, pname) )

		return layout

	def startFromXML( self, file, _async_ = None, enforceBasicLayout = False,
						bwConfig = BW_CONFIG_HYBRID ):
		"""
		Start a server using the layout in the given XML.  The argument can
		either be a filename pointing to an XML file or a file-like object to
		read the XML data from.

		If enforceBasicLayout is True and the layout given in the XML is missing
		any basic server processes, then they will automatically be started too.
		"""

		# Don't do anything if a server's already running
		if self.serverIsRunning():
			log.error( "Can't load layout from XML while server is running!" )
			return False

		if not self.checkBwConfig( bwConfig ):
			log.error( "Provided bwConfig not supported" )
			return False

		if type( file ) == str:
			try:
				xmldata = open( file ).read()
			except Exception, e:
				log.error( "Couldn't read XML data from %s: %s", file, e )
				return False
		else:
			xmldata = file.read()

		layout = self.parseXMLLayout( xmldata )

		# Verify that each machine actually exists
		missing = False
		mnames, pnames = set(), set()
		for mname, pname in layout:
			m = self.cluster.getMachine( mname )
			if m:
				mnames.add( mname )
				pnames.add( pname )
			else:
				log.error( "Layout refers to non-existent machine '%s'", mname )
				missing = True

		if missing:
			log.error( "Aborting startup due to missing machines" )
			return False

		self.log( "Starting server" )

		# Enforce basic layout if required
		if enforceBasicLayout:

			mnames = list( mnames )
			if not mnames:
				log.error( "Can't enforce basic layout with an "
						   "empty prior layout" )
				return False

			for pname in Process.types.required( self.version ):
				if pname not in pnames:
					layout.append( (random.choice( mnames ), pname) )
					log.info( "Added missing basic process %s to %s",
								layout[-1][1], layout[-1][0] )

		# Iterate through layout and add the pid to each entry for passing to
		# layoutIsRunning()
		for i in xrange( len( layout ) ):
			mname, pname = layout[i]
			machine = self.cluster.getMachine( mname )
			pid = machine.startProc( pname, self.uid,
								_async_ = _async_, config = bwConfig )
			layout[i] = (mname, pname, pid)
			log.debug( "Starting %s on %s (pid:%d)", pname, mname, pid )

		if layout and self.verifyStartup( layout, _async_ = _async_ ):
			self.ls()
			return True
		else:
			return False

	def verifyStartup( self, layout, _async_ = None ):

		# Signal async listeners with the layout
		if _async_:
			_async_.update( "layout", layout )

		status = []
		ok = self.cluster.waitFor(
			util.Functor( self.layoutIsRunning,
						  args = [layout, status],
						  kwargs = {"_async_": _async_} ),
			POLL_SLEEP, MAX_STARTUP_SLEEPS )

		if not ok:
			log.error( "The following processes failed to start:" )
			# NB: procStatus is used rather than unpacking directly
			#     in the for loop, as layoutIsRunning can return an
			#     extra 'details' element which will break unpacking
			for procStatus in status:
				mname = procStatus[ 0 ]
				pname = procStatus[ 1 ]
				pid   = procStatus[ 2 ]
				state = procStatus[ 3 ]
				if state != "registered":
					log.error( "%s on %s (pid: %d): %s",
							   pname, mname, pid, state )
		return ok

	def stop( self, signal = None, _async_ = None, timeout = MAX_POLL_SLEEPS ):
		"""
		Kills all my processes by sending the given signal, or SIGINT if none
		given.
		"""

		if signal is None:
			signal = messages.SignalMessage.SIGINT

		# Kill revivers first if there are any
		for p in self.getProcs( "reviver" ):
			p.stop()

		# Wait for reviver death
		if not self.cluster.waitFor( lambda: not self.getProcs( "reviver" ),
									 POLL_SLEEP, timeout ):
			log.error( "Some revivers haven't shut down!" )
			for p in self.getProcs( "reviver" ):
				log.error( p )
			return False

		# Kick off loginapp controlled shutdown on SIGUSR1
		if signal == messages.SignalMessage.SIGUSR1:
			loginapps = self.getProcs( "loginapp" )
			if loginapps:
				for p in loginapps:
					p.stop( messages.SignalMessage.SIGUSR1 )
			else:
				log.error( "Can't do controlled shutdown with no loginapp!" )
				return False

			# Loginapp's don't know about bots processes so kill them manually
			for bp in self.getProcs( "bots" ):
				bp.stop()

		# Otherwise send signals to all server components
		else:
			for p in self.getProcs():
				if hasattr( p, "stop" ):
					p.stop( signal )

		# Wait for server to shutdown
		if not self.cluster.waitFor(
					util.Functor( self.layoutIsStopped,
						  args = [self.getLayout()],
						  kwargs = {"_async_": _async_} ),
					POLL_SLEEP, timeout ):

			procs = self.getProcs( ignoreProcs = ["message_logger"] )
			if procs:
				log.warning( "Components still running after stop( %d ):" % signal )
				for p in procs:
						log.warning( "%s (load: %.3f)" % (p, p.machine.load()) )

				return False

		return True

	def smartStop( self, forceKill=False, _async_ = None, timeout = MAX_POLL_SLEEPS ):
		"""
		Stop the server by the most controlled means possible.
		"""

		errors = False

		# Because of the way the shutdown messages flow, you actually need all
		# the "world" processes running to do a controlled shutdown
		if self.getProc( "loginapp" ) and \
			((self.getProc( "dbappmgr" ) and self.getProc( "dbapp" )) or 
				self.getProc( "dbmgr" )) and \
			self.getProc( "cellappmgr" ) and self.getProc( "baseappmgr" ):

			self.log( "Starting controlled shutdown" )

			if self.stop( messages.SignalMessage.SIGUSR1, _async_ = _async_, timeout = timeout ):
				return True
			else:
				if not forceKill:
					# Don't force processes to quit.
					# If we are doing controlled shutdown, we'll have to wait
					# until the components have all shutdown by themselves,
					# just report on what processes are still up every
					# timeout. If the components haven't shutdown after
					# too long of a time, break out and fail smartStop
					retries = 0
					while not retries > 5:
						if self.cluster.waitFor(
								util.Functor( self.layoutIsStopped,
								args = [self.getLayout()],
								kwargs = {"_async_": _async_} ),
								POLL_SLEEP, timeout ):
							return True
						retries += 1
						log.warning( "Components still running after controlled "
							"shutdown initiated:" )
						for p in self.getProcs():
							log.warning( "%s (load: %.3f)", p, p.machine.load() )

					# if we break out, then controlled shutdown has failed
					log.error( "Controlled shutdown failed" )
					return False

				log.error( "Controlled shutdown failed" )
				errors = True


		if forceKill:
			self.log( "Starting SIGINT shutdown" )

			if self.stop( messages.SignalMessage.SIGINT, _async_ = _async_, timeout = timeout ):
				if errors:
					log.info( "Shutdown via SIGINT successful" )
				return True
			else:
				log.error( "Forced shutdown with SIGINT failed" )
				errors = True

			self.log( "Starting SIGQUIT shutdown" )

			if self.stop( messages.SignalMessage.SIGQUIT, _async_ = _async_, timeout = timeout ):
				if errors:
					log.info( "Shutdown via SIGQUIT successful" )
				return True
			else:
				log.error( "Forced shutdown with SIGQUIT failed" )
				errors = True

		else:
			# Handles the case where only some of the server processes is running
			# or no server process is running, and force kill is not allowed.
			# The server most likely is in the process of shutting down, although
			# it may be the case that one or more of the "world" processes may
			# have crashed.
			# If the user wants to kill the remaining running server processes,
			# they should use ./control_cluster.py kill command.
			if self.getProcs( ignoreProcs = [ "message_logger" ] ):
				# List processes still running.
				self.ls()

				msg = \
"\n\n" \
"The server cannot be shut down cleanly. It may already be in the process of\n" \
"shutting down.\n\n" \
"To force the server processes listed above to stop now rather than waiting for\n" \
"them to stop, use the following command:\n" \
"$ ./control_cluster.py kill\n\n" \
"WARNING: Using './control_cluster.py kill' command may cause data loss as\n" \
"BaseApps may be in the process of writing entities to the database."

				log.info( msg )

			else:
				log.info( "No server process is running." )
				return True

		return False

	def restart( self, _async_ = None ):
		"""
		Shuts down the server then restarts it with the same layout.
		"""

		if not self.serverIsRunning():
			if not self.getProcs():
				log.info( "No server process is running." )
			return False

		stream = StringIO()
		self.saveToXML( stream )
		stream.seek( 0 )
		if not self.smartStop( _async_ = _async_ ):
			return False
		return self.startFromXML( stream, _async_ = _async_,
								  enforceBasicLayout = True )

	def startProc( self, machine, pname, count = 1, bwConfig = BW_CONFIG_HYBRID ):

		if not self.checkBwConfig( bwConfig ):
			log.error( "Provided bwConfig not supported" )
			return False

		# Start new processes and collect their PIDs
		pids = [machine.startProc( pname, self.uid, config=bwConfig )
					for i in xrange( count )]

		# If there are any 0's in there something went wrong
		if 0 in pids:
			log.error( "%d processes didn't start!",
					   len( [pid for pid in pids if pid == 0] ) )
			return False
		# Function to test whether the new processes have started
		allDone = lambda: None not in [machine.getProc( pid ) for pid in pids]

		# Wait till they've started up
		if not self.cluster.waitFor( allDone, POLL_SLEEP, MAX_POLL_SLEEPS ):
			log.error( "Some processes didn't start!" )
			return False
		else:
			return True


	def verifyLayoutIsRunning( self, file ):
		try:
			layout = self.parseXMLLayout( open( file ).read() )
		except IOError:
			log.error( "No such file '%s'", file )
			return False
		except:
		 	log.exception( "Error reading '%s'", file )
		 	return False

		runningProcs = self.getProcs()

		for machine,proc in layout:

			foundProc = False
			# If we are still expecting more items in the layout
			# but no more items are running, fail.
			if len(runningProcs) == 0:
				return False

			for activeProc in runningProcs:
				if machine == activeProc.machine.name and \
				proc == activeProc.name:
					foundProc = True
					runningProcs.remove( activeProc )
					break

			if not foundProc:
				return False

		# MessageLogger shouldn't be considered part of the layout
		for remainingProc in runningProcs:
			if remainingProc.name == "message_logger":
				runningProcs.remove( remainingProc )

		if len(runningProcs) == 0:
			return True

		return False


	@Exposed.expose( args = [("file", "the filename to save the layout to")] )
	def saveToXML( self, file ):
		"""Writes this user's cluster layout to XML."""

		# Create XML document and root node
		doc = minidom.Document()
		root = doc.createElement( "cluster" )
		doc.appendChild( root )

		# Now do the non-world processes
		for pname in Process.types.startable():

			# Count up the number of procs on each machine
			pcounts = {}
			for p in self.getProcs( pname ):
				if pcounts.has_key( p.machine.name ):
					pcounts[ p.machine.name ] += 1
				else:
					pcounts[ p.machine.name ] = 1

			# Bail now if there aren't any
			if not pcounts: continue

			# Make a sorted list of the machines
			machines = filter( lambda m: pcounts.has_key( m.name ),
							   self.cluster.getMachines() )
			machines.sort( Machine.cmpByHostDigits )

			# The root node for these entries
			listNode = doc.createElement( pname )
			root.appendChild( listNode )

			# Make entries for each machine
			for m in machines:
				node = doc.createElement( "machine" )
				node.setAttribute( "name", m.name )
				if pcounts[ m.name ] > 1:
					node.setAttribute( "count", str( pcounts[ m.name ] ) )
				listNode.appendChild( node )

		# Write it to the file
		if type( file ) == str:
			file = open( file, "w" )
		file.write( doc.toprettyxml() )
		if not isinstance( file, StringIO ):
			file.close()
		return True

	#--------------------------------------------------------------------------
	# Subsection: Bot Operations
	#--------------------------------------------------------------------------

	def getBotMachines( self ):
		"""Returns a list of all the machines in the cluster that are candidates
		   for running bots."""

		return filter( lambda m: m.isBotCandidate( self.uid ),
					   self.cluster.getMachines() )

	def getBestAddCandidate( self ):
		"""
		Returns the lowest loaded bot process below the CPU thresh, or None
		if all bot processes are overloaded.
		"""

		bps = sorted( self.getProcs( "bots" ), key = lambda p: p.load )
		if not bps:
			return None

		if bps[0].load < MAX_BOTS_CPU:
			return bps[0]
		else:
			return None

	def getBestDelCandidate( self ):

		# Comparator for deletion.  Puts processes with the lowest number of
		# bots first, then orders by highest CPU load.
		def delcmp( bp1, bp2 ):
			botcmp = cmp( bp1.nbots(), bp2.nbots() )
			loadcmp = cmp( bp2.machine.load(), bp1.machine.load() )
			return botcmp or loadcmp

		# Throw away processes with no active bots
		bps = filter( lambda bp: bp.nbots() > 0, self.getProcs( "bots" ) )
		bps.sort( delcmp )

		if bps:
			return bps[0]
		else:
			return None

	def lsBots( self ):
		"""Prints out information about currently running bots processes."""

		# Get info about the cluster
		bms = sorted( self.getBotMachines(), cmp = util.cmpAddr,
					  key = lambda m: m.ip )

		usedms = util.uniq( map( lambda p: p.machine, self.getProcs( "bots" ) ),
							cmp )
		if usedms:
			log.info( "machines running bots processes:" )
			for bm in usedms:
				bps = bm.getProcs( "bots" )
				nbots = sum( [bp.nbots() for bp in bps] )
				log.info( "%-11s %d bots on %d bots processes",
						  bm.name, nbots, len( bps ) )
			log.info( "" )

		freems = self.getBotMachines()
		for m in usedms:
			freems.remove( m )
		if freems:
			log.info( "free candidate machines:" )
			for bm in freems:
				log.info( bm )
			log.info( "" )

		log.info( "%d clients\n%d proxies\n%d cell entities",
				  self.getTotalBots(), self.getNumProxies(),
				  self.getNumEntities() )

		for pname, load in self.getLoads().items():
			log.info( "min/avg/max %s load: %s",
					  re.sub( "app", "", pname ), load )


	def addBots( self, numToAdd, timeout = None ):
		"""Add the given number of bots to existing processes or create new
		   processes to handle them as necessary."""

		log.info( "Adding %d bot%s...", numToAdd, ("s","")[numToAdd==1] )
		totalToAdd = numToAdd
		starttime = time.time()

		while numToAdd > 0:

			try:
				# Refresh all cluster information
				self.cluster.refresh()

				# Find a bots process that isn't overloaded
				bp = self.getBestAddCandidate()
				if ( timeout and time.time() - starttime > timeout ):
					log.error(
					"Adding bots timed out after %s seconds" % timeout )
					break
				if not bp:
					log.info( "\tall bots processes are overloaded; "
							  "waiting for more CPU..." )
					time.sleep( CPU_WAIT_SLEEP )
					continue

				# If server components are overloaded, wait for a little bit
				if self.serverIsOverloaded():
					log.info( "\tserver overloaded; waiting for more CPU ..." )
					time.sleep( CPU_WAIT_SLEEP )
					continue
				# Add bots
				numToAddNow = min( numToAdd, NBOTS_AT_ONCE )
				bp.addBots( numToAddNow )
				numToAdd -= numToAddNow
				log.info( "\tadded %d to %s (%d done in %.1fs)",
						  numToAddNow, bp.label(),
						  totalToAdd - numToAdd,
						  time.time() - starttime )

				# Wait a little bit.  We didn't need to do this before
				# because each refresh() took so long, but now we need to do
				# this or it's easy to overload a running system.
				time.sleep( 1.0 )

			except KeyboardInterrupt:
				break

		log.info( "Added %d bots in %.1fs",
				  totalToAdd - numToAdd, time.time() - starttime )


	def delBots( self, numtoop, timeout = None ):
		"""Deletes the given number of bots from running bots processes, least
		   loaded processes first.  Does not kill empty bots processes."""

		# If no bot processes, bail out
		if not self.getProcs( "bots" ):
			log.error( "no known bot processes to delete bots from" )
			return False

		# Bail if no known bots
		if self.getTotalBots() == 0:
			log.error( "can't delete - no known bots" )
			return False

		# Cap deletion amount if more than known
		numtoop = min( numtoop, self.getTotalBots() )

		log.info( "Deleting %d of %d known bots ..." %
				  (numtoop, self.getTotalBots() ) )
		deleted = 0

		starttime = time.time()
		while numtoop > 0:

			# Refresh cluster info
			self.cluster.refresh()

			# The process we're deleting from
			bp = self.getBestDelCandidate()

			# If we couldn't find a del candidate, chances are a bot process
			# timed out when asked for its bot count, so go round again.
			if ( timeout and time.time() - starttime > timeout ):
				log.error(
					"Adding bots timed out after %s seconds" % timeout )
				break
			if bp is None:
				continue

			# The number we're actually going to delete at once
			chunksize = min( numtoop, NBOTS_AT_ONCE, bp.nbots() )

			# If the bot process has no bots, something's gone wrong
			assert bp.nbots() > 0

			# Do it
			bp.delBots( chunksize )
			bp.nbots( bp.nbots() - chunksize )
			numtoop -= chunksize
			deleted += chunksize
			log.info( "\tdeleted %d from %s:%d (%d done)",
					  chunksize, bp.machine.name, bp.port(), deleted )

		log.info( "Deleted %d bots OK." % deleted )
		return True


	def setWatchersOnAllBots( self, *values ):
		"""
		This method takes any number of tuples. Each tuple contains the path to
		the value to set and the value to set it to, eg:

		setWatchersOnAllBots( ('defaultControllerType', 'Patrol'),
		                      ('defaultControllerData', 'test.bwp') )

		It sets these watcher values on all bot processes.
		"""

		# Handle the case where you've just got two string arguments
		if values and (type(values[0]) == str):
			values=(values,)

		for value in values:
			log.info( "Setting '%s' to '%s'" % value )

		for bp in self.getProcs( "bots" ):
			bp.setWatcherValues( values )


	def callWatcherOnAllBots( self, command, *parameters ):
		"""
		This method takes a command and any number of arguments to
		that command, eg:

		callWatcherOnAllBots( 'command/addBots', int( num ) )

		It calls that command on all bot processes.
		"""

		log.info( "Calling '%s' with %s", command, parameters )
		for bp in self.getProcs( "bots" ):
			if bp.version < ( 2, 6, 0 ) and len( parameters ) == 1:
				bp.setWatcher( command, parameters[ 0 ] )
			else:
				bp.callWatcher( command, *parameters )


	def setBotMovement( self, controllerType, controllerData, botTag ):
		"""Sets the controllerType and controllerData for all bots matching the
		   given tag, e.g. ('Patrol','server/bots/test.bwp','')."""

		self.setWatchersOnAllBots( ( "defaultControllerType", controllerType ),
								   ( "defaultControllerData", controllerData ))
		self.callWatcherOnAllBots( "command/updateMovement", str( botTag ) )


	def runScriptOnBots( self, script = "" ):
		"""Runs Python script on all bot apps. With no args, command is read
		   from stdin, otherwise first arg is the command."""

		if script == "":
			log.info( "Input Python script to run (Ctrl+D to finish):" )
			self.callWatcherOnAllBots( "command/runPython", str( sys.stdin.read() ) )
		else:
			self.callWatcherOnAllBots( "command/runPython", str( script ) )


	#--------------------------------------------------------------------------
	# Subsection: Exposed stuff
	#--------------------------------------------------------------------------

	def log( self, text, severity = "INFO" ):
		"""
		Send a log message to all loggers on the network.
		"""

		for logger in cluster.cache.get().getProcs( "message_logger" ):
			try:
				logger.sendMessage( text, self, severity )
			except Exception, e:
				log.error( "Failed to send message %s to logger @ %s: %s" % ( text, logger, e ) )

from cluster import Cluster
from process import Process, Version
from machine import Machine

# user.py
