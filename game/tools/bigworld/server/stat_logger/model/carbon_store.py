import time
import struct
import socket
import logging
import errno

# Logging module
log = logging.getLogger( __name__ )

try:
	import cPickle as pickle
	log.debug( "using cPickle" )
except ImportError:
	import pickle

from data_store import DataStore


# The timeout value for socket connect, unit: second
CONNECT_TIMEOUT = 30

# The interval to retry to connect to carbon, unit: second
RETRY_INTERVAL = 10

# Max data allowed to buffer in memory when connection is closed, unit: byte 
# Default to 100MB. Data beyond this will be discarded
MAX_ALLOWED_BUFFER_SIZE = 100 * 1024 * 1024


class CarbonStore( DataStore ):
	""" Interface to write statistics to backend Carbon """

	def __init__( self, carbonStoreConfig, prefTree ):
		DataStore.__init__( self, carbonStoreConfig, prefTree )

		# Carbon namespace/prefix for StatLogger metrics
		self.prefix = carbonStoreConfig.prefix or 'stat_logger'
		
		# Use an alternate path structure when sending to Carbon. Separates
		# user and process metrics from machine statistics.
		self.decoupleUserStatistics = carbonStoreConfig.decoupleUserStatistics \
			or False

		# list of metric tuples of form:
		# (statisticName, (timestamp, statisticValue))
		self._statBuffer = []

		# TCP socket to Carbon service configured to accept pickled data
		self._socket = None
		
		self.host = socket.gethostbyname( carbonStoreConfig.host )		
		self.port = carbonStoreConfig.port
		s = socket.socket()

		log.info( "Attempting to connect to %s:%s", self.host, self.port )
		s.settimeout( CONNECT_TIMEOUT )
		s.connect( (self.host, self.port) )
		self._socket = s
		
		# Last time to retry connecting
		self._lastReconnectTime = None

		# Buffer for picked data which is ready to send 
		self._msgBuffer = MsgBuffer( MAX_ALLOWED_BUFFER_SIZE ) 

	# __init__


	# -------------------------------------------------------------------------
	# Section: exposed methods, inherited from DataStore
	# (virtual ones in DataStore)
	# -------------------------------------------------------------------------
	def finalise( self, quickTerminate = True ):
		if self._socket:
			try:
				self._socket.close()
			except Exception, ex:
				log.error( "Failed to close the socket connection with Carbon" )
				
			self._socket = None
	# finalise


	def isOk( self ):
		return True
	# isOk


	@classmethod
	def testConnection( cls, carbonStoreConfig ):
		try:		
			host = socket.gethostbyname( carbonStoreConfig.host )
			port = carbonStoreConfig.port			
			s = socket.socket()		
			s.settimeout( CONNECT_TIMEOUT )
			s.connect( (host, port) )
		except Exception, ex:
			log.error( "Couldn't connect to carbon host '%s:%s': %s",
				carbonStoreConfig.host, carbonStoreConfig.port, ex )
			return False

		s.close()

		return True
	# testConnection


	def logProcessStats( self, processStats, tick ):
		""" Logs stats for all processes. """

		if not processStats:
			log.info( "processStats is empty, return.")
			return

		numMetrics = 0
		now = self._getTimestamp()

		for process, statDict in processStats.items():			
			for pref, statValue in statDict.items():
				self._recordProcessStatistic( process, pref, statValue, now )
				numMetrics += 1

		log.debug( "Writing %d process metrics", numMetrics )
		self._flush()
	# logProcessStats


	def logMachineStats( self, machineStats, tick ):
		""" Logs stats for all machines. """

		if not machineStats:
			log.info( "machineStats is empty, return.")
			return

		numMetrics = 0
		now = self._getTimestamp()
		for m, statDict in machineStats.iteritems():
			for pref in self.prefTree.iterMachineStatPrefs():
				statValue = statDict.get( pref, None )
				self._recordMachineStatistic( m, pref, statValue, now )
				numMetrics += 1

		log.debug( "Writing %d machine metrics", numMetrics )
		self._flush()
	# logMachineStats


	# -------------------------------------------------------------------------
	# Section: exposed methods, inherited from Store (virtual ones in Store)
	#          These pseudo methods are created for interface consistency
	# -------------------------------------------------------------------------
	def logNewMachine( self, machine ):
		log.debug( "new machine: %s", machine.ip )


	def logNewProcess( self, process, userName ):
		log.debug( "new process: %s", process.label() )


	def logNewUser(self, user):
		log.debug( "new user: %s", user.name )


	def delProcess( self, process ):
		log.debug( "Delete dead process: %s", process.label() )


	def consolidateStats( self, tick, shouldLimitDeletion=True ):
		log.debug( "NOOP consolidateStats" )


	def addTick( self, tick, tickTime ):
		log.debug( "new tick: %s", tick )


	# ------------------------------------------------------
	# Section: internal methods
	# ------------------------------------------------------	
	def _getTimestamp( self ):
		""" Returns current time as (float) epoch seconds. """
		return time.time()
	# _getTimestamp


	def _flush( self ):
		"""
		Flush accumulated statistic writes to Carbon.

		@raises IOError If not connected to a Carbon service.
		"""

		if not self._statBuffer:
			return

		# Create message
		payload = pickle.dumps( self._statBuffer )
		self._statBuffer[:] = []
		header = struct.pack( "!L", len( payload ) )
		message = header + payload

		self._msgBuffer.append( message )

		# socket was closed
		if not self._socket:
			if time.time() - self._lastReconnectTime < RETRY_INTERVAL: 
				log.info( "Connection with carbon has been closed. "
						"Will try to flush later" )
				return
			else:
				# It's been longer than the interval since last retry, try again
				if not self._reconnect():
					log.info( "Failed to reconnect to carbon. Will retry later" )
					return

		try:
			bufferredMsg = self._msgBuffer.pop()
			while bufferredMsg:
				self._socket.sendall( bufferredMsg )
				log.info( "Successfully wrote %d bytes to Carbon", 
						len( bufferredMsg ) )
				bufferredMsg = self._msgBuffer.pop()
		except socket.error, ex:
			# Try to close and reconnect upon any socket error. BWT-27405
			log.error( "Got socket error:%s, "
				"Closing socket and will reconnect later.", ex )
			self._socket.close()
			self._socket = None

			# initialize reconnect time to retry later after RETRY_INTERVAL
			self._lastReconnectTime = time.time() 
		except Exception, ex:
			log.error( "Failed to write data: %s to Carbon", ex )
			raise ex
	# _flush


	def _recordProcessStatistic( self, process, pref, statValue, timestamp ):
		"""
		Records the given process metric.

		@type process 	A L{Process} object
		@type pref		A L{Pref} object
		@type statValue	Number
		@type timestamp	A timestamp in epoch seconds
		"""

		machineId = process.machine.name
		assert machineId

		processId = process.label()
		assert processId

		userId = process.username
		assert userId

		statName = pref.name.replace( ' ', '_' )

		if self.decoupleUserStatistics:
			statId = "%s.users.%s.process_%s.stat_%s" % \
				(self.prefix, userId, processId, statName)
		else:
			statId = "%s.machine_%s.user_%s.process_%s.stat_%s" % \
				(self.prefix, machineId, userId, processId, statName)

		log.debug( "PROCESS: %s --> %s", statId, statValue )
		stat = (statId, (timestamp, statValue))
		self._statBuffer.append( stat )
	# _recordProcessStatistic


	def _recordMachineStatistic( self, machine, pref, statValue, timestamp ):
		"""
		Records the given machine metric.

		@type process 	A L{Machine} object
		@type pref		A L{Pref} object
		@type statValue	Number
		@type timestamp	A timestamp in epoch seconds
		"""

		# machineId = ipToInt( machine.ip )
		machineId = machine.name
		prefName = pref.name.replace( ' ', '_' )
		prefName = prefName.replace( '(', '' )
		prefName = prefName.replace( ')', '' )

		if self.decoupleUserStatistics:
			statId = "%s.machines.%s.stat_%s" % (self.prefix, machineId, 
				prefName)
		else:
			statId = "%s.machine_%s.stat_%s" % (self.prefix, machineId,
				prefName)

		log.debug( "MACHINE: %s --> %s", statId, statValue )
		stat = (statId, (timestamp, statValue))
		self._statBuffer.append( stat )
	# _recordMachineStatistic


	def _reconnect( self ):
		self._lastReconnectTime = time.time()

		try:		
			s = socket.socket()		
			s.settimeout( CONNECT_TIMEOUT )
			s.connect( (self.host, self.port) )
			self._socket = s

			log.info( "Reconnected to carbon host '%s:%s'",
				self.host, self.port )

			return True
		except Exception, ex:
			log.info( "Couldn't connect to carbon host '%s:%s': %s",
				self.host, self.port, ex )
			return False
	# _reconnect 

# CarbonStore


class MsgBuffer( object ):

	def __init__( self, maxSize ):
		self._maxSize = maxSize
		self._size = 0
		self._msgs = []

	
	def append( self, message ):
		msgSize = len( message )

		# Free space for the new data by discarding old data
		while self._size + msgSize >= self._maxSize:
			msgToDiscard = self._msgs.pop( 0 )
			self._size -= len( msgToDiscard )
			log.info( "Discarded %d byte data to free space for new data.",
					len( msgToDiscard ) )

		# add new data to buffer
		self._msgs.append( message )
		self._size += msgSize 


	def pop( self ):
		if self._msgs:
			message = self._msgs.pop( 0 )
			self._size -= len( message )

			return message
		else:
			return None


# class BufferredMsg
