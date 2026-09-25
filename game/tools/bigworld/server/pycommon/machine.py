import logging
import re
import socket

from exposed import Exposed
import messages
from cluster_constants import POLL_SLEEP
from cluster_constants import MAX_POLL_SLEEPS
from cluster_constants import BOTS_EXCLUSIVE
from cluster_constants import BW_CONFIG_HYBRID

log = logging.getLogger( __name__ )

# Whether or not we want spew for debugging
VERBOSE = False

# ------------------------------------------------------------------------------
# Section: Machine
# ------------------------------------------------------------------------------

class Machine( Exposed ):

	def __init__( self, cluster, mgm, ip, clearProcs = True ):

		Exposed.__init__( self )

		self.cluster = cluster
		self.name = mgm.hostname
		self.ip = ip

		# TODO: assuming that mgm here is a WholeMachineMessage.. should verify
		#       and assert if not or a HPM too

		# List containing the loads for each CPU on the machine
		self.loads = [ l/255.0 for l in mgm.cpuLoads ]

		self.mhz = mgm.cpuSpeed
		self.ncpus = mgm.nCpus
		self.machinedVersion = mgm.version

		# Dictionary of { interface name -> messages.IfStats object }
		self.ifStats = mgm.ifStats

		# Number of discarded packets
		self.inDiscards = mgm.inDiscards
		self.outDiscards = mgm.outDiscards

		# Ratio of memory available on this machine (available/max)
		self.mem = mgm.mem/255.0

		# a map of machined tags for this machine, tag -> [ values ]
		self.tags = {}

		# a mapping of pid -> Process for each process running on this machine.
		# it is optional to clear this because when we are updating existing
		# machine objects we don't want to lose the process mapping
		if clearProcs:
			self.procs = {}
			self.unknownUsers = set()

		self.platformInfo = None 

	def __hash__( self ):
		import struct
		return struct.unpack( "!I", socket.inet_aton( self.ip ) )[0] % 0x7fffffff

	def __cmp__( self, other ): return cmp( self.name, other.name )

	def __json__( self ):
		procs = self.getProcs()
		procsByUser = {}
		for p in procs:
			if not p.user().name in procsByUser:
				procsByUser[p.user().name] = []
			procsByUser[p.user().name].append(p.name)
		
		# processesByUser is not currently used by WebConsole, but will be
		# as part of BWT-25854
		return {
			'name': self.name,
			'tags': self.tags,
			'ip': self.ip,
			'loads': self.loads,
			'mem': self.mem,
			'interfaces': self.ifStats,
			'processor': self.mhz,
			'machinedVersion': self.machinedVersion,
			'processes': [ p.name for p in procs ],
			'processesByUser': procsByUser,
			'platformInfo': self.platformInfo
		}
	# __json__

	
	def getCpuLoadsStr( self ):
		cpuloads = ",".join( ["%2d%%" % int( l*100 ) for l in self.loads] )
		cpuloads += " of %4dMHz" % self.mhz

		return cpuloads

	
	def getProcNumStr( self ):
		nprocs = len( self.getProcs() )

		numStr = "%2d " % nprocs
		if nprocs <= 1:
			suffix = "process  "
		else:
			suffix = "processes"

		return numStr + suffix 
	

	def getMachinedStr( self ):
		# Append machined version if different to the current known version
		if self.machinedVersion != \
			   messages.MachineGuardMessage.MACHINED_VERSION:
			return " (v%d)" % self.machinedVersion

		return ""


	def getFormattedStr( self, displayPlatformInfo = False ):
		"""Returns a formatted string representing the current machine."""
		
		machineStr = ""

		# name, ip
		if VERBOSE:
			machineStr += "%s (%s)" % ( self.name, self.ip )
		else:
			machineStr += "%-15s %-15s" % ( self.name, self.ip )

		# platform info
		if displayPlatformInfo:
			if self.platformInfo:
				machineStr += " %-10s" % self.platformInfo
			else:
				machineStr += " %-10s" % "(unknown)" 

		# process, cpu, memory, bwmachined version(optional)
		machineStr += "%s  %s (%d%% mem) %s" % ( self.getProcNumStr(),
				self.getCpuLoadsStr(), self.mem * 100, self.getMachinedStr() )

		if VERBOSE:

			# Sort server procs by uid
			cmpByUid = lambda p1, p2: cmp( p1.uid, p2.uid )
			procs = self.getProcs()
			procs.sort( cmpByUid )

			# Append a list of regular server components being run if there are
			# any
			for p in procs:
				machineStr += \
				  "\n\t%-16s running as %-10s using %2d%% cpu %2d%% mem" % \
				  ( p.name, p.user().name,
				   int( p.load * 100 ), int( p.mem * 100 ) )

		return machineStr 
	# getFormattedStr


	def supportsHighPrecision( self ):
		"""Returns True if the machine we refer to supports communicating
			High Precision machine statistics."""

		return (self.machinedVersion >= 41)


	def totalmhz( self ): return self.ncpus * self.mhz

	def load( self ): return max( self.loads )

	def getServerProcs( self ):
		from process import Process
		return [p for p in self.getProcs() 
			if p.name in Process.types.serverProcs()]

	def getProcs( self, name = None, uid = None ):
		"""Returns all processes with the given name, or all if no name
		   given, filtering by uid."""

		import util
		return util.filterProcs( self.procs.values(), name, uid )


	def getProc( self, pid ):
		if self.procs.has_key( pid ):
			return self.procs[ pid ]
		else:
			return None


	def isPidRunning( self, pid ):
		pm = messages.PidMessage()
		pm.pid = pid
		replies = pm.query( self )
		if not replies:
			return False
		else:
			return replies[0].running

	def getProcForPort( self, port ):
		ps = [ p for p in self.procs.values() if p.port() == port ]
		if ps:
			return ps[0]
		else:
			return None

	def setMachinedVersion( self, version ):
		self.machinedVersion = version

	def outOfDate( self ):
		return self.machinedVersion != \
			   messages.MachineGuardMessage.MACHINED_VERSION

	def startProc( self, name, uid,
		config = BW_CONFIG_HYBRID, _async_ = None ):
		"""
		Start a process on this machine.  Returns the PID of the started
		process.  If this is run as an AsyncTask, any errors reported by
		machined are sent into the update queue.
		"""

		mgm = messages.CreateMessage()
		mgm.uid = uid
		mgm.name = name
		mgm.config = config

		# We don't want extra attempts here because that results in multiple
		# processes being spawned most of the time, because the first one
		# actually worked but just took a while to reply to us
		replies = mgm.query( self, attempts = 1, timeout = 3.0 )
		pid = 0

		if not replies:
			log.error( "%s didn't reply to CreateMessage with PID for %s",
					   self.name, name )

		elif not replies[0].running:
			log.error( "newly created process %s (%d) on %s is not running!",
					   name, replies[0].pid, self.name )

		else:
			pid = replies[0].pid

		# Everything on the packet other than first message is an error message
		if _async_:
			for mgm in replies[1:]:
				if isinstance( mgm, messages.ErrorMessage ):
					_async_.updateFinal( "__warning__", mgm.msg )

		return pid


	def startProcWithArgs( self, name, args, uid,
		config = BW_CONFIG_HYBRID ):
		"""
		Start a process on this machine.  Returns the PID of the started
		process.
		"""

		mgm = messages.CreateWithArgsMessage()
		mgm.uid = uid
		mgm.name = name
		mgm.config = config
		mgm.args = args

		# We don't want extra attempts here because that results in multiple
		# processes being spawned most of the time, because the first one
		# actually worked but just took a while to reply to us
		replies = mgm.query( self, attempts = 1, timeout = 3.0 )
		pid = 0

		if not replies:
			log.error( "%s didn't reply to CreateWithArgsMessage with PID " \
					"for %s", self.name, name )

		elif not replies[0].running:
			log.error( "newly created process %s (%d) on %s is not running!",
					name, replies[0].pid, self.name )

		else:
			pid = replies[0].pid

		return pid


	def killProc( self, proc, signal = None ):
		"""
		Kill a process on this machine.
		"""

		proc.stop( signal )
		pid = proc.pid
		uid = proc.uid
		name = proc.label()

		procIsDead = lambda: not self.getProc( pid )

		if not self.cluster.waitFor( procIsDead, POLL_SLEEP, MAX_POLL_SLEEPS ):
			proc.stop( messages.SignalMessage.SIGQUIT )
			if not self.cluster.waitFor(
				procIsDead, POLL_SLEEP, MAX_POLL_SLEEPS ):
				log.error( "Couldn't kill %s (pid:%d) on %s" %
						   (name, pid, self.name) )
				self.cluster.getUser( uid, fetchVersion = True ).ls()
				return False

		return True

	def flushMappings( self ):
		rm = messages.ResetMessage()
		if not rm.query( self ):
			log.error( "%s refused to flush its mappings", self.name )
			return False
		else:
			return True


	def setPlatformInfo( self, platformInfo ):
		if self.platformInfo and (self.platformInfo != platformInfo):
			log.warning( "Operating system type appears to have changed for %s",
				self.name )
		self.platformInfo = platformInfo

	
	@property
	def supportsVersionString( self ):
		return self.machinedVersion >= \
			messages.UserMessage.MACHINED_VERSION_FIRST_SUPPORTED_VERSION_STRING


	@staticmethod
	def cmpByHostDigits( m1, m2 ):
		"""Sorts machines with the same alpha prefixed hostnames by the digits
		   at the end of their hostnames."""
		m1nums = re.sub( "\D+", "", m1.name )
		m2nums = re.sub( "\D+", "", m2.name )
		m1alpha = re.sub( "\d+", "", m1.name )
		m2alpha = re.sub( "\d+", "", m2.name )

		if len( m1nums ) == 0 and len( m2nums ) == 0 or m1alpha != m2alpha:
			return cmp( m1alpha, m2alpha )
		elif len( m1nums ) == 0 or len( m2nums ) == 0:
			return cmp( len( m1nums ), len( m2nums ) )
		else:
			return cmp( int( m1nums ), int( m2nums ) )

	@staticmethod
	def cmpByLoad( m1, m2 ):
		return cmp( m2.load(), m1.load() )

	def isBotCandidate( self, uid ):
		"""Returns true if this machine is a candidate for running bots
		   processes."""

		bpsForUser = filter( lambda p: p.uid == uid, self.getProcs( "bots" ) )
		return bpsForUser or not BOTS_EXCLUSIVE

	def canRun( self, pname ):
		"""
		Returns true if this Machine can run the specified process name.
		"""

		if not self.tags.has_key( "Components" ):
			return True

		for tag in self.tags[ "Components" ]:
			if tag.lower() == pname:
				return True

		return False


	@staticmethod
	def localMachine():
		"""
		Returns a reference to the local machine, or None if this machine isn't
		running bwmachined.
		"""

		mgm = messages.WholeMachineMessage()
		replies = mgm.query( "127.0.0.1" )

		if not replies:
			return None
		else:
			import cluster
			return cluster.cache.get().getMachine( replies[0].hostname )

# machine.py
