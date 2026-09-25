"""
An interface to various network protocols implemented by BigWorld server
components and daemons.
"""

import struct
import os
import socket
import random
import select
import logging
import errno

import socketplus
import util
import memory_stream
import watcher_data_type as WDT
import watcher
from cStringIO import StringIO

log = logging.getLogger( __name__ )


def any( iterable ):
	for element in iterable:
		if element:
			return True

	return False


class WatcherRequest( object ):
	def __init__( self, process, data ):
		self.process = process
		self.dataToSend = data
		self.socket = socket.socket()
		self.socket.bind( ('', 0) )
		self.socket.setblocking( False )
		try:
			self.socket.connect( process.addr() )
		except socket.error, e:
			# Non-blocking raises 'Operation now in progress'
			pass
		self.receivedData = ""

	def onWriteReady( self ):
		try:
			self.socket.setblocking( True )
			self.socket.send( self.dataToSend )
			del self.dataToSend
		except socket.error:
			return False

		return True

	def read( self ):
		newData = self.socket.recv( 65536 )

		if not newData:
			raise socket.error()
		self.receivedData += newData
		data = self.receivedData

		if len( data ) < 4:
			return

		msgLen = struct.unpack( 'i', data[:4] )[0]

		if len( data ) < msgLen + 4:
			return

		self.receivedData = data[4 + msgLen:]
		data = data[4 : 4 + msgLen]

		try:
			reply = WatcherDataMessage()
			reply.set( data )
		except:
			log.error( "Corrupt WDM v2 reply from %s" %
				self.socket.getpeername()[0] )
			log.error( util.hexdump( data ) )
			return

		# If it's not a TELL and not an MGM either, start worrying
		if (reply.message != reply.WATCHER_MSG_TELL2) and \
			(reply.message != reply.WATCHER_MSG_SET2_TELL2):
			log.error( "Received an unrecognised watcher message" )
			log.error( str( reply ) )
			return None

		return reply

	def fileno( self ):
		return self.socket.fileno()


	def closeSocket( self ):
		try:
			self.socket.close()
		except Exception, ex:
			log.error( "Failed to close socket. Error: %s", ex )


# ------------------------------------------------------------------------------
# Section: WatcherDataMessage
#          watcher protocol v2 message
# ------------------------------------------------------------------------------

class WatcherDataMessage( object ):
	WATCHER_MSG_GET2 = 26
	WATCHER_MSG_SET2 = 27
	WATCHER_MSG_TELL2 = 28
	WATCHER_MSG_SET2_TELL2 = 29


	WATCHER_MODE_INVALID = 0    # Indicates an error.
	WATCHER_MODE_READ_ONLY = 1  # Indicates the watched value cannot be changed.
	WATCHER_MODE_READ_WRITE = 2 # Indicates the watched value can be changed.
	WATCHER_MODE_DIR = 3        # Indicates that the watcher has children.
	WATCHER_MODE_CALLABLE = 4   # Indicates the watcher is a callable function
	# < - little endian
	# I - message type (ie: _GET2 / _SET2 )
	# I - num contained messages
	STRUCT_FORMAT = "<II"

	TELL2_FORMAT  = "<IBB"

	# The number of times we'll try to requery a Watcher value
	REQUERY_MAX = 2


	def __init__(self):
		self.message = 0
		self.count = 0
		self.replyData = []
		self.extensionStream = None
		self.requestPaths = []

		# For a _GET2 request requestStrings contains the following tuple:
		# ( sequence #, watcher string )
		self.requestStrings = []

		# Sequence number is an int prefix to the watcher values
		# that are sent with a _GET2 request.
		self.seqNum = random.randint(0,(2**32)-1)


	@staticmethod
	def modeToString( mode ):
		if mode == WatcherDataMessage.WATCHER_MODE_INVALID:
			return "invalid (error)"
		elif mode == WatcherDataMessage.WATCHER_MODE_READ_ONLY:
			return "read only"
		elif mode == WatcherDataMessage.WATCHER_MODE_READ_WRITE:
			return "read/write"
		elif mode == WatcherDataMessage.WATCHER_MODE_DIR:
			return "directory"
		elif mode == WatcherDataMessage.WATCHER_MODE_CALLABLE:
			return "callable"
		else:
			return "unknown"


	def get( self ):
		"""
		Convert the fields of this message into a stream.
		"""

		if self.extensionStream:
			packet = struct.pack( "I", self.message ) + \
					 self.extensionStream.data()

		else:

			packet = struct.pack( self.STRUCT_FORMAT, self.message, self.count )

			for request in self.requestStrings:

				# request[0] = sequence #
				# request[1] = watcher path
				# request[2] = data type (_SET2_only)
				# request[3] = data      (_SET2 only)
				packet += struct.pack( "<I%ds" % (len(request[1])+1),
									request[0], request[1] + '\0' )

				# If it's a set request go ahead and append the data
				# to set the watcher path to.
				if self.message == self.WATCHER_MSG_SET2:
					# request[2] = WatcherDataMessage() (_SET2_only)
					packet += request[2].toStream()

		return packet


	def readDirEntries( self, stream ):

		DIR_PREFIX = "<BB"
		COUNT_STR  = "<I"

		# TODO: This could potentially be changed to a BW_*PACK3. See addWatcherCount
		#     in watcher_path_request.hpp.
		(count,) = struct.unpack( COUNT_STR,
						stream.read( struct.calcsize( COUNT_STR ) ) )


		size = 0
		tmpDirs = []
		for i in xrange( count ):
			# Read the sequence #, type and mode of the current entry
			(dataType, mode) = struct.unpack( DIR_PREFIX,
								stream.read( struct.calcsize( DIR_PREFIX ) ) )

			# Read off the size of the current entry
			dataSize = WDT.BW_UNPACK3( stream )
			data = stream.read( dataSize )


			# Dispatch unpack to WatcherDataType
			wdtClass = WDT.WDTRegistry.getClass( dataType )
			wdtObj = wdtClass.unpack( data )


			# The final part of all directory listings is the name of the
			# directory entry.
			entrySize = WDT.BW_UNPACK3( stream )
			data = stream.read( entrySize )

			# Dispatch unpack to WatcherDataType
			wdtClass = WDT.WDTRegistry.getClass( watcher.Constants.TYPE_STRING )
			entryObj = wdtClass.unpack( data )

			# Push into the cumulative list of directory entries.
			tmpDirs.append( (entryObj.value, wdtObj.value, dataType, mode) )

		return tmpDirs



#	def printDebug( self, dt, mode ):
#		if dt == self.WATCHER_TYPE_BOOL:
#			print "Type is: Bool"
#		elif dt == self.WATCHER_TYPE_INT:
#			print "Type is: Int"
#		elif dt == self.WATCHER_TYPE_FLOAT:
#			print "Type is: Float"
#		elif dt == self.WATCHER_TYPE_STRING:
#			print "Type is: String"
#		elif dt == self.WATCHER_TYPE_TUPLE:
#			print "Type is: Tuple"
#		elif dt ==self. WATCHER_TYPE_FUNC_TUPLE:
#			print "Type is: Func Tuple"
#		else:
#			print "Type is: Unknown"
#
#		print "Mode is:", mode


	def set( self, str ):
		"""
		Unpack the contents of a stream into the fields of this message.
		"""

		# Wrap in a cStringIO - it should be fairly fast to do this
		stream = StringIO( str )

		(self.message, self.count) = struct.unpack( self.STRUCT_FORMAT,
				stream.read( struct.calcsize( self.STRUCT_FORMAT ) ) )

		for i in xrange( self.count ):

			# Read the sequence #, type and mode of the current entry
			(seqNum, type, mode) = struct.unpack( self.TELL2_FORMAT,
						stream.read(struct.calcsize( self.TELL2_FORMAT )) )

			# Now read off the size of the data chunk
			dataSize = WDT.BW_UNPACK3( stream )
			data = stream.read( dataSize )

			# Dispatch unpack to WatcherDataType
			wdtClass = WDT.WDTRegistry.getClass( type )
			wdtData  = wdtClass.unpack( data )

			# Responses to a SET2 request have a success / fail byte appended
			# to the end of each operation.
			retStatus = None
			if self.message == self.WATCHER_MSG_SET2_TELL2:
				retStatus = bool( ord( stream.read( 1 ) ) )


			# If a directory listing was found, then handle the contained data
			if type == watcher.Constants.TYPE_STRING and \
			   mode == self.WATCHER_MODE_DIR:
				tmpDirs = self.readDirEntries( stream )
				self.replyData.append( (seqNum, type, mode, tmpDirs) )
				tmpDirs = None
			else:
				value = wdtData.value
				if isinstance(value, list):
					value = tuple( value )

				# Add the extracted data to the list
				if retStatus != None:
					self.replyData.append( (seqNum, type, mode, value, retStatus) )
				else:
					self.replyData.append( (seqNum, type, mode, value) )


		return self


	def __str__( self ):
		s = "WatcherDataMessage (protocol v2):\n"
		s += " message = %d\n" % self.message
		s += " count = %d\n" % self.count
		for str in self.requestStrings:
			s += "  string %d: %s\n" % (i, str)
			if self.message != self.WATCHER_MSG_GET2:
				s += "  result %d: %s\n" % (i, str)
		return s


	def addGetRequest( self, watcherPath ):
		"""
		Adds a watcher value along with a sequence number to the list of
		watchers to retrieve.
		"""

		self.requestStrings.append( (self.seqNum, watcherPath) )
		self.requestPaths.append( watcherPath )

		# Wrap the sequence number around at 32 bits
		self.seqNum += 1
		self.seqNum %= 0xffffffff

		self.count += 1
		return


	def addSetRequest( self, path, val ):

		if not isinstance(val, WDT.WatcherDataType):
			wdtValue = WDT.WDTRegistry.toWDT( val )
			self.requestStrings.append( (self.seqNum, path, wdtValue) )
		else:
			self.requestStrings.append( (self.seqNum, path, val) )

		self.requestPaths.append( path )

		# Wrap the sequence number around at 32 bits
		self.seqNum += 1
		self.seqNum %= 0xffffffff

		self.count += 1



	def getExtensionStream( self, message ):
		"""
		Marks this message as a watcher extension message, using the provided
		extension message ID.  Returns a MemoryStream that the extension data
		should be packed into.
		"""

		self.message = message
		self.extensionStream = memory_stream.MemoryStream()
		return self.extensionStream


	def getReply( self, index ):
		return (self.replyData[ index ])

	def getReplyCount( self ):
		return len( self.replyData )


	def getWatcherPathFromSeqNum( self, seqNum ):
		for i in self.requestStrings:
			if i[0] == seqNum:
				return i[1]
		log.error( "Failed to lookup seqNum: %s", seqNum )
		raise KeyError( "Unknown watcher sequence number: %s" % seqNum )


	# This method is used by the batchQuery methods to separate the replies
	# into their originating path structures.
	def splitReply( self, reply, isReplyFromWDMSet = False ):
		replies = {}

		# Go through messages and sort them into the correct reply buckets
		for i in xrange( reply.getReplyCount() ):

			replyTuple = reply.getReply( i )
			replySeqNum = replyTuple[ 0 ]
			replyType = replyTuple[ 1 ]
			replyMode = replyTuple[ 2 ],
			replyValue = replyTuple[ 3 ]

			# Conditionally there based on the WATCHER_MSG_* type
			if len( replyTuple ) == 5:
				replyStatus = replyTuple[ 4 ]
			else:
				replyStatus = True

			replyPath = self.getWatcherPathFromSeqNum( replySeqNum )

			if isinstance( replyValue, list ):
				replies.setdefault( replyPath, replyValue )

			elif replyPath in self.requestPaths:
				# First look for an exact match in request paths (ie for
				# value requests)
				if isReplyFromWDMSet:
					tmpTuple = (replyPath, replyValue, replyType,
								replyMode, replyStatus)
				else:
					tmpTuple = (replyPath, replyValue, replyType, replyMode)

				replies.setdefault( replyPath, [] ).append( tmpTuple )
			else:
				# Next look for dirname match (ie for directory contents)
				dirname = os.path.dirname( replyPath )
				if dirname in self.requestPaths:
					replies.setdefault( dirname, [] ).append(
							(replyPath, replyValue, replyType, replyMode) )
				else:
					log.error( "WDM2: Incorrect reply (%s,%s) for %s" % \
						   (replyPath, replyValue, self.requestPaths) )

		return replies


	@staticmethod
	def query( path, proc, timeout = 1.0 ):
		"""
		Light overload for batchQuery(), returns list of replies
		"""

		replies = WatcherDataMessage.batchQuery( [path], [proc], timeout )

		if proc in replies:
			return replies[ proc ].get( path, [] )
		else:
			return []

	
	@staticmethod
	def createRequest( proc, dataToSend ):
		"""
		Try to create a WatcherRequest.
		Return: The create request upon success
				None upon EMFILE error (too many)
		Exeception will be reraised except for EMFILE error
		"""
		
		try:
			watcherRequest = WatcherRequest( proc, dataToSend )
			return watcherRequest
		except socket.error, ex:
			# We only handle the too many open files error here
			if ex[ 0 ] == errno.EMFILE:
				return None
			else:
				log.error( "Failed to create WatcherRequest:%s", ex)
				raise ex


	def tcpMainLoop( wdm, procs, timeout ):
		"""
		Monitor FDs using epoll if available, otherwise fall back onto select
		"""

		dataToSend = wdm.get()

		# Prefix with the size of the data
		dataToSend = struct.pack( 'i', len( dataToSend ) ) + dataToSend

		# Do not let queries be larger than 16 MB.
		if len( dataToSend ) > 2**24:
			raise ValueError(
					"Query of %d bytes is too large" % len( dataToSend ) )

		if hasattr( select, "epoll" ):
			return WatcherDataMessage.tcpMainLoopByEpoll( wdm, dataToSend, 
														procs, timeout )
		else:
			return WatcherDataMessage.tcpMainLoopBySelect( wdm, dataToSend, 
														procs, timeout )


	@staticmethod
	def tcpMainLoopBySelect( wdm, dataToSend, procs, timeout ):
		# Mapping from process -> list of {watcher path -> watcher response}
		replies = {}

		# In Python 2.4 we don't have access to epoll and have to use select.
		# select has a limit on largest file descriptor number, which is 1024.
		# so here we have to limit the number of opened file descriptor.
		# We cannot use 1024 as the limit because the process may have opened
		# other sockets. As a work around for this, we choose a relatively safe
		# number 900.
		# Apart from this, on Linux, there is also limit on the max number of
		# open files in one process, which by default is 1024. If number of open
		# files is more than this, "socket.error: (24, 'Too many open files')"
		# will be raised, so we need to handle this issue as well.

		# The F_SETSIZE for select
		FD_SETSIZE = 900

		wlist = []
		rlist = []		
		procsPending = []

		# Prepare first batch of requests, process beyond limit will be pending
		alreadyTooManyOpenFiles = False
		for proc in procs:
			if proc.addr()[1] is None:
				log.warning( "Process %s on %s does not have valid watcher",
						proc.name, proc.machine.name )
			elif alreadyTooManyOpenFiles or len( wlist ) >= FD_SETSIZE:
				procsPending.append( proc )
			else:
				request = WatcherDataMessage.createRequest( proc, dataToSend )
				if request:
					wlist.append( request )
				else:
					# Probably already too many open files
					procsPending.append( proc )
					alreadyTooManyOpenFiles = True

		# Collect all the replies and handle all the pending processes
		while rlist or wlist:
			readyRList, readyWList, readyXList = \
				select.select( rlist, wlist, [], timeout )

			# Did we time out?
			if not readyRList and not readyWList:
				for request in wlist:
					proc = request.process
					log.warning( "Failed to connect to %s on %s:%d",
							proc.name, proc.machine.name, proc.port() )

				for request in rlist:
					proc = request.process
					log.warning( "Failed to receive all data from %s on %s:%d",
							proc.name, proc.machine.name, proc.port() )

				for proc in procsPending:
					log.warning( "Failed to receive all data from %s on %s:%d",
							proc.name, proc.machine.name, proc.port() )

				return replies

			# Handle ready for read socket lists
			for request in readyRList:
				try:
					reply = request.read()
				except socket.error:
					proc = request.process
					log.warning( "Lost connection to %s on %s:%d",
								 proc.name, proc.machine.name, proc.port() )
					request.closeSocket()
					rlist.remove( request )
					reply = None

				if reply:
					replies[ request.process ] = wdm.splitReply( reply,
						(wdm.message == WatcherDataMessage.WATCHER_MSG_SET2) )
					request.closeSocket()
					rlist.remove( request )

			# Handle ready for write socket lists
			for request in readyWList:
				if request.onWriteReady():
					rlist.append( request )
				elif False: # Set to True for warnings about failed connections
					proc = request.process
					log.warning( "Failed to connect to %s on %s:%d",
							proc.name, proc.machine.name, proc.port() )
				wlist.remove( request )

			# Handle pending process if possible 
			while ( len( wlist ) + len( rlist ) ) < FD_SETSIZE and procsPending:
				proc = procsPending.pop()
				request = WatcherDataMessage.createRequest( proc, dataToSend )
				if request:
					wlist.append( request )
				else:
					# Probably already too many open files
					procsPending.append( proc )
					break
		# end while rlist or wlist

		return replies

	# def tcpMainLoopBySelect


	@staticmethod
	def tcpMainLoopByEpoll( wdm, dataToSend, procs, timeout ):
		"""
		Batch retrieval of a watcher value from one or more processes.
		This uses epoll which is only supported by Python 2.6 or newer.

		Return value is:

		{process: {request-path: [(path1,val1), (path2,val2), ...]}}
		"""

		# Mapping from process -> list of {watcher path -> watcher response}
		replies = {}

		# Mapping from WatcherRequest.fileno -> WatcherRequest
		fileNoDict = {}
		procsPending = []

		epollInst = select.epoll()

		def registerRequest( request ):
			fileNo = request.fileno()
			fileNoDict[ fileNo ] = request 
			epollInst.register( fileNo, select.EPOLLOUT )

		def unregisterRequest( request ):
			fileNo = request.fileno()
			request.closeSocket()
			del fileNoDict[ fileNo ]
			epollInst.unregister( fileNo )

		# Prepare the first batch of query
		alreadyTooManyOpenFiles = False 
		for proc in procs:
			if proc.addr()[1] is None:
				log.warning( "Process %s on %s does not have valid watcher",
						proc.name, proc.machine.name )
			elif alreadyTooManyOpenFiles:
				procsPending.append( proc )
			else:
				request = WatcherDataMessage.createRequest( proc, dataToSend )
				if request:
					registerRequest( request )
				else:
					# Probably already too many open files
					procsPending.append( proc )
					alreadyTooManyOpenFiles = True

		try:
			while fileNoDict:
				events = epollInst.poll( timeout )

				# Probably we have timed out
				if not events:
					requests = fileNoDict.values()
					for request in requests:
						proc =  request.process
						unregisterRequest( request )
						log.warning( "Failed to receive data from %s on %s:%d",
								proc.name, proc.machine.name, proc.port() )

					for proc in procsPending:
						log.warning( "Failed to receive data from %s on %s:%d",
								proc.name, prpc.machine.name, proc.port() )

					return replies

				# Handle events
				for fileNo, event in events:
					request = fileNoDict[ fileNo ]
					proc = request.process

					# Socket ready for read
					if event & select.EPOLLIN:
						try:
							reply = request.read()
						except socket.error:
							log.warning( "Lost connection to %s on %s:%d",
								proc.name, proc.machine.name, proc.port() )
							unregisterRequest( request )
							reply = None

						if reply:
							replies[ proc ] = wdm.splitReply( reply, \
										(wdm.message == \
										WatcherDataMessage.WATCHER_MSG_SET2) )
							unregisterRequest( request )

					# Socket ready for write 
					elif event & select.EPOLLOUT:
						if request.onWriteReady():
							epollInst.modify( fileNo, select.EPOLLIN )
						else:
							log.warning( "Failed to connect to %s on %s:%d",
								proc.name, proc.machine.name, proc.port() )
							unregisterRequest( request )

					# Socket error 
					elif event & select.EPOLLHUP or event & select.EPOLLERR:
						log.warning( "Failed to connect to %s on %s:%d",
								proc.name, proc.machine.name, proc.port() )
						unregisterRequest( request )

				# Handle pending process if possible 
				while procsPending:
					proc = procsPending.pop()
					request = WatcherDataMessage.createRequest( proc, 
							dataToSend )

					if request:
						registerRequest( request )
					else:
						# Probably already too many open files
						procsPending.append( proc )
						break

			# end while fileNoDict
		finally:
			epollInst.close()

		return replies

	# def batchQueryTCPByEpoll


	@staticmethod
	def batchQueryTCP( paths, procs, timeout = 5.0 ):
		"""
		Batch retrieval of a watcher value from one or more processes.
		Return value is:

		{process: {request-path: [(path1,val1), (path2,val2), ...]}}
		"""

		wdm = WatcherDataMessage()
		wdm.message = wdm.WATCHER_MSG_GET2

		for path in paths:
			wdm.addGetRequest( path )

		return WatcherDataMessage.tcpMainLoop( wdm, procs, timeout )


	@staticmethod
	def batchQueryUDP( paths, procs, timeout = 1.0 ):
		"""
		Batch retrieval of a watcher value from one or more processes.
		Return value is:

		{process: {request-path: [(path1,val1), (path2,val2), ...]}}
		"""

		sock = socketplus.socket( "m" )

		wdm = WatcherDataMessage()
		wdm.message = wdm.WATCHER_MSG_GET2

		for path in paths:
			wdm.addGetRequest( path )

		# Mapping from process -> number of times failed to reply in time
		notReplied = {}

		# Mapping from (ip, port) -> process to correlate replies
		addresses = {}

		# Mapping from process -> list of {watcher path -> watcher response}
		replies = {}

		dataToSend = wdm.get()

		if len( dataToSend ) > 2**16:
			raise ValueError(
					"Query of %d bytes is too large" % len( dataToSend ) )

		# Send out all the requests and initialise dictionaries
		for p in procs:
			try:
				sock.sendto( dataToSend, p.addr() )

			# These errors are caught on the sendto() call
			except socket.error:
				continue
			except TypeError:
				continue

			notReplied[ p ] = 0
			replies[ p ] = {}
			addresses[ p.addr() ] = p

		# Collect all the replies
		while notReplied:

			# This inner loop iterates until all replies received or timeout
			while notReplied and select.select( [sock], [], [], timeout )[0]:

				data, (srcip, srcport) = sock.recvfrom( 65536 )
				try:
					reply = WatcherDataMessage()
					reply.set( data )
				except:
					log.error( "Corrupt WDM v2 reply from %s" % srcip )
					log.error( util.hexdump( data ) )
					continue

				# If it's not a TELL and not an MGM either, start worrying
				if reply.message != reply.WATCHER_MSG_TELL2:
					log.error( "Received an unrecognised watcher message" )
					log.error( str( reply ) )
					continue

				# Lookup process and get its reply map
				try:
					p = addresses[ (srcip, srcport) ]
				except KeyError:
					log.warning( "Ignoring unexpected watcher response from " \
						"process at %s:%d" % (srcip, srcport) )
					continue

				pmap = replies[ p ]

				# Go through messages and sort them into the correct reply buckets
				for i in xrange( reply.getReplyCount() ):
					(replySeqNum, replyType, replyMode, replyValue) = reply.getReply( i )

					replyPath = wdm.getWatcherPathFromSeqNum( replySeqNum )

					if isinstance( replyValue, list):
						pmap.setdefault( replyPath, replyValue )
						continue

					else:
						# First look for an exact match in request paths (ie for
						# value requests)
						if replyPath in paths:
							pmap.setdefault( replyPath, [] ).\
								append( (replyPath, replyValue, replyType, replyMode) )
							continue

						# Next look for dirname match (ie for directory contents)
						dirname = os.path.dirname( replyPath )
						if dirname in paths:
							pmap.setdefault( dirname, [] ).\
								append( (replyPath, replyValue, replyType, replyMode) )
							continue

					log.error( "WDM2: Incorrect reply (%s,%s) for %s" % \
							   (replyPath, replyValue, paths) )

				# Mark this process as having replied
				try:
					del notReplied[ p ]
				except KeyError:
					# In rare situations we get two responses from one process,
					# where one response is probably a delayed response
					# from an earlier query - so we can't delete from
					# this dictionary twice.
					log.warning( "Possibly delayed packet from process %s", p )

			# If we're not done yet, chances are a reply was lost, send out the
			# request again, hopefully we'll get lucky this time
			for p, n in notReplied.items():
				log.warning( "%s on %s:%d didn't reply to WDM (%d/%d)",
							 p.name, p.machine.name, p.port(), n + 1,
							 WatcherDataMessage.REQUERY_MAX )
				sock.sendto( wdm.get(), p.addr() )
				notReplied[ p ] += 1

				# If a process has failed too many times, just put in an empty
				# list for its replies
				if notReplied[ p ] >= WatcherDataMessage.REQUERY_MAX:
					del notReplied[ p ]
					replies[ p ] = {}

		return replies

	@staticmethod
	def batchQuery( paths, procs, timeout = 5.0 ):
		paths = set( paths )
		procs = set( procs )

		useUDPWatchers = any( not proc.supportsTCPWatchers() for proc in procs )

		if useUDPWatchers:
			return WatcherDataMessage.batchQueryUDP( paths, procs, timeout )
		else:
			return WatcherDataMessage.batchQueryTCP( paths, procs, timeout )

# watcher_data_message.py
