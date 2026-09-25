#!/usr/bin/env python
"""
The BigWorld lock daemon process.
"""

# import daemon module from pycommon modules
import bwsetup
bwsetup.addPath( "../server" )

from pycommon.daemon import Daemon
from common import *

# import libraries
import errno
import logging
import optparse
import os
import signal
import select
import socket
from struct import pack, unpack
import sys
from time import time
import traceback
from xml.dom import minidom

log = logging.getLogger( 'bwlockd' )


class Computer( object ):
	"""
	This class represents a workstation where a lock-aware WorldEditor is being
	run from.

	State is saved to an XML file derived from the lowercase hostname of the
	workstation suffixed by '.computer'.
	"""
	def __init__( self, name, dataDir ):
		self.name = name.lower()
		self.dataDir = dataDir
		self.spaces = {}
		self.bypasssave = 0


	def filename( self ):
		return os.path.join( self.dataDir, self.name + '.computer' )


	def load( self ):
		self.bypasssave = 1
		self.spaces = {}
		dom = minidom.parse( self.filename() )
		for element in dom.documentElement.childNodes:
			if element.nodeName == 'space':
				spaceName = ''
				for sub in element.childNodes:
					if sub.nodeName == 'name':
						spaceName = sub.childNodes[0].nodeValue.strip().\
							encode( 'utf8', 'replace' )
						break
				for sub in element.childNodes:
					if sub.nodeName == 'lock':
						rect = Rect( 0, 0, 0, 0 )
						desc = ''
						username = ''
						t = 0
						for subsub in sub.childNodes:
							if subsub.nodeName == 'rect':
								rect.__eval__(
									subsub.childNodes[0].nodeValue.strip() )
							elif subsub.nodeName == 'desc':
								desc = subsub.childNodes[0].nodeValue.strip().\
									encode( 'utf8', 'replace' )
							elif subsub.nodeName == 'username':
								username = \
									subsub.childNodes[0].nodeValue.strip().\
										encode( 'utf8', 'replace' )
							elif subsub.nodeName == 'time':
								t = float(
									subsub.childNodes[0].nodeValue.strip() )
						self.addLock( spaceName, rect, username, desc, t )
		dom.unlink()
		self.bypasssave = 0


	def save( self ):
		if self.bypasssave:
			return

		f = open( self.filename(), "w" )
		doc = minidom.getDOMImplementation().createDocument(
				None, self.name.replace( ' ', '_' ), None )

		for space in self.spaces.keys():
			spaceElt = doc.createElement( "space" )
			doc.documentElement.appendChild( spaceElt )

			nameElt = doc.createElement( "name" )
			spaceElt.appendChild( nameElt )
			nameElt.appendChild( doc.createTextNode( space ) )

			for lock in self.spaces[ space ]:
				lockElt = doc.createElement( "lock" )
				spaceElt.appendChild( lockElt )

				rectElt = doc.createElement( "rect" )
				rectElt.appendChild( doc.createTextNode( repr( lock[0] ) ) )
				lockElt.appendChild( rectElt )

				usernameElt = doc.createElement( "username" )
				usernameElt.appendChild( doc.createTextNode( lock[1] ) )
				lockElt.appendChild( usernameElt )

				descElt = doc.createElement( "desc" )
				descElt.appendChild( doc.createTextNode( lock[2] ) )
				lockElt.appendChild( descElt )

				timeElt = doc.createElement( "time" )
				timeElt.appendChild( doc.createTextNode( repr( lock[3] ) ) )
				lockElt.appendChild( timeElt )

		doc.writexml( f )
		f.close()


	def addLock( self, space, rect, username, desc, t = None ):
		if t == None:
			t = time()
		if not self.spaces.has_key( space ):
			self.spaces[ space ] = []
		for lock in self.spaces[ space ]:
			if lock[0] == rect:
				return 0
		self.spaces[ space ].append( ( rect, username, desc, t ) )
		self.save()
		return 1


	def removeLock( self, space, rect ):
		if self.spaces.has_key( space ):
			for lock in self.spaces[ space ]:
				if lock[0] == rect:
					self.spaces[ space ].remove( lock )
					self.save()
					return 1
		return 0


	def removeAllLocks( self ):
		self.spaces = {}
		self.save()


	def removeAllLocks( self, space ):
		if self.spaces.has_key( space ):
			del self.spaces[ space ]
			self.save()


	def spaceNum( self ):
		return len( self.spaces.keys() )


	def space( self, index ):
		return self.spaces.keys()[ index ]


	def lockNum( self, space ):
		if not self.spaces.has_key( space ):
			return 0
		return len( self.spaces[ space ] )


	def lock( self, space, index ): # lock is a triple ( rect, desc, time )
		return self.spaces[ space ][ index ]


	def intersect( self, space, rect ):
		if self.spaces.has_key( space ):
			for lock in self.spaces[ space ]:
				if lock[0].intersect( rect ):
					return 1
		return 0

class History( object ):

	def __init__( self, filename, maxEntry = 100 ):
		self.filename = filename
		self.maxEntry = maxEntry
		self.bypasssave = 1
		self.records = []
		try:
			dom = minidom.parse( self.filename )
			for element in dom.documentElement.childNodes:
				if element.nodeName == 'record':
					name = ''
					desc = ''
					actor = ''
					workstation = ''
					t = ''
					for sub in element.childNodes:
						if sub.nodeName == 'name':
							name = sub.childNodes[0].nodeValue.strip().\
								encode( 'utf8', 'replace' )
						elif sub.nodeName == 'desc':
							desc = sub.childNodes[0].nodeValue.strip().\
								encode( 'utf8', 'replace' )
						elif sub.nodeName == 'actor':
							actor = sub.childNodes[0].nodeValue.strip().\
								encode( 'utf8', 'replace' )
						elif sub.nodeName == 'workstation':
							workstation = sub.childNodes[0].nodeValue.strip().\
								encode( 'utf8', 'replace' )
						elif sub.nodeName == 'time':
							t = float( sub.childNodes[0].nodeValue.strip() )
					self.addRecord( name, desc, actor, workstation, t )
			dom.unlink()
			self.bypasssave = 0
		except Exception, desc:
			self.bypasssave = 0
			self.save()


	def save( self ):
		if self.bypasssave:
			return
		f = open( self.filename, "w" )

		doc = minidom.getDOMImplementation().createDocument(
				None, "history", None )
		historyElt = doc.documentElement

		for record in self.records:
			recordElt = doc.createElement( "record" )
			historyElt.appendChild( recordElt )

			nameElt = doc.createElement( "name" )
			nameElt.appendChild( doc.createTextNode( record[0] ) )
			recordElt.appendChild( nameElt )

			descElt = doc.createElement( "desc" )
			descElt.appendChild( doc.createTextNode( record[1] ) )
			recordElt.appendChild( descElt )

			actorElt = doc.createElement( "actor" )
			actorElt.appendChild( doc.createTextNode( record[2] ) )
			recordElt.appendChild( actorElt )

			workstationElt = doc.createElement( "workstation" )
			workstationElt.appendChild( doc.createTextNode( record[3] ) )
			recordElt.appendChild( workstationElt )

			timeElt = doc.createElement( "time" )
			timeElt.appendChild( doc.createTextNode( repr( record[4] ) ) )
			recordElt.appendChild( timeElt )

		doc.writexml( f )
		f.close()

	def addRecord( self, name, desc, actor, workstation, t = None ):
		if t == None:
			t = time()
		if len( name ) and len( actor ) and len( workstation ):
			self.records.append( ( name, desc, actor, workstation, t ) )
			while len( self.records ) > self.maxEntry:
				self.records.pop( 0 )
			self.save()
		else:
			raise Exception, 'invalid parameters in History.addRecord'\
				'name : %s, actor : %s, workstation : %s' % \
					( name, actor, workstation )

class Connection( object ):

	def __init__( self, address, clientSocket ):
		self.pendingMessage = ''
		self.user = None
		self.computer = None
		self.address = address
		self.space = ''
		self.socket = clientSocket


	def addMessage( self, msg ):
		self.pendingMessage += msg


	def msgAvailable( self ):
		return len( self.pendingMessage ) > 4 and \
			len( self.pendingMessage ) >= \
				unpack( 'I', self.pendingMessage[0:4] )[ 0 ]


	def nextMsg( self ):
		msgSize = unpack( 'I', self.pendingMessage[0:4] )[ 0 ]
		msg = self.pendingMessage[:msgSize]
		self.pendingMessage = self.pendingMessage[msgSize:]
		return msg


class LockDaemon( object ):

	def __init__( self, bindAddr, dataDir, historyPath=None ):
		self.computers = {}
		self.dataDir = dataDir
		self.history = None
		if historyPath:
			log.info( 'Loading history from %s', historyPath )
			self.history = History( historyPath )

		log.info( 'Loading client state from %s', self.dataDir )
		files = os.listdir( '.' )
		for file in files:
			if file.lower()[-9:] == '.computer':
				try:
					c = Computer( file[:-9], self.dataDir )
					c.load()
					log.debug( 'Loading client %s', c.name )
					self.computers[ c.name ] = c
				except Exception, e:
					log.error( 'Loading client %s failed: %s',
						file.lower()[:-4], e )
		bindName, bindPort = bindAddr
		bindIP = socket.gethostbyname( bindName )
		log.info( 'Listening on %s(%s):%d', bindIP, bindName, bindPort )
		self.serverSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.serverSocket.setsockopt(
			socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
		self.serverSocket.bind( (bindIP, bindPort) )
		self.serverSocket.listen( BACKLOG )
		self.readList = [ self.serverSocket ]
		self.writeList = []
		self.exceptionList = []

		self.connections = {}

		self.isRunning = False


	def step( self ):
		try:
			readResult, writeResult, exceptionResult = select.select(
				self.readList, self.writeList, self.exceptionList )
		except select.error, e:
			errNum, errDesc = e.args
			if errNum != errno.EINTR:
				log.error( "Error while selecting sockets: %s", errDesc )
			return

		if self.serverSocket in readResult:
			( clientSocket, clientAddress ) = self.serverSocket.accept()
			try:
				remoteAddr = clientAddress[0]
				self.onConnect( clientSocket, remoteAddr )
			except Exception, e:
				log.error( "Could not accept connection request from %s: %s",
					clientAddress, e )
		else:
			connection = self.connections[ readResult[0] ]
			msg = ''

			try:
				msg = readResult[0].recv( MAX_MESSAGE_LENGTH )
			except Exception, msg:
				msg = ''

			if msg == '':
				self.onDisconnect( connection )
			else:
				connection.addMessage( msg )
				while connection.msgAvailable():
					msg = connection.nextMsg()
					self.onMessage( msg, connection )


	def sendMessage( self, clientSocket, clientAddress, code, failed, msg,
			disconnect = 1 ):
		try:
			msg = pack( 'IcB', len( msg ) + 6, code, failed % 256 ) + msg;
			clientSocket.sendall( msg )
		except Exception, e:
			if clientSocket in self.connections:
				conn = self.connections[clientSocket]
				log.error( "Failed sending message to %s: %s",
					clientAddress, e )
				if disconnect:
					self.onDisconnect( conn )
			else:
				log.error( "Failed sending message to new client: %s", clientAddress )


	def addRecord( self, name, desc, connection, username = None ):
		if username == None:
			if connection.user != None:
				username = connection.user
			else:
				username = '(unknown)'
		if self.history:
			self.history.addRecord( name, desc, username, connection.address )


	def onConnect( self, clientSocket, clientAddress ):
		for connection in self.connections.values():
			if connection.address == clientAddress:
				# Close the old connection
				self.onDisconnect( connection )
				break

		self.readList.append( clientSocket )
		self.connections[ clientSocket ] = \
			Connection( clientAddress, clientSocket )
		self.sendMessage( clientSocket, clientAddress, 
				BWLOCKCOMMAND_CONNECT, 0,
			'hello from bwlockd at ' + socket.gethostname() )
		log.info( "Client connected: %s", clientAddress )


	def onDisconnect( self, connection ):
		log.info( "%s disconnected" % connection.address )
		self.readList.remove( connection.socket )
		del self.connections[ connection.socket ]
		connection.socket.close()


	def onMessage( self, msg, connection ):
		if len( msg ) < 6:
			log.error( 'Got invalid message from %s' % connection.address )
			self.addRecord( 'invalidmessage', repr( msg ), connection )
			return

		code = msg[4:5]

		if code == BWLOCKCOMMAND_SETUSER:
			self.onUsername( msg[6:], connection )
		elif connection.computer == None:
			log.error( "Client hasn't logged in from %s, disconnecting", 
				connection.address )
			self.sendMessage( connection.socket, connection.address, 
				BWLOCKCOMMAND_CONNECT, 1, "hasn't logged in", 0 )
			connection.socket.close()
		elif code == BWLOCKCOMMAND_SETSPACE:
			self.onSetSpace( msg[6:], connection )
		elif code == BWLOCKCOMMAND_LOCK:
			if len( msg ) < 14:
				log.error( 'Invalid message from %s' % connection.address )
				self.addRecord( 'invalidmessage', repr( msg ), connection )
				return
			( minx, miny, maxx, maxy ) = unpack( 'hhhh', msg[6:14] )
			self.onLockChunk( Rect( minx, miny, maxx, maxy ), msg[14:],
				connection )
		elif code == BWLOCKCOMMAND_UNLOCK:
			if len( msg ) < 14:
				log.error( 'Invalid message from %s' % connection.address )
				self.addRecord( 'invalidmessage', repr( msg ), connection )
				return
			( minx, miny, maxx, maxy ) = unpack( 'hhhh', msg[6:14] )
			self.onUnlockChunk( Rect( minx, miny, maxx, maxy ), msg[14:],
				connection )
		elif code == BWLOCKCOMMAND_GETSTATUS:
			self.onGetStatus( connection )


	def onUsername( self, username, connection ):
		computerName = username.split( "::" )[0]
		if not computerName:
			log.error( "Unknown computer name from %s, disconnecting", 
				connection.address )
			self.sendMessage( connection.socket, connection.address, 
				BWLOCKCOMMAND_SETUSER, 1, "unknown computer name", 0 )
			connection.socket.close()
			return
		if not computerName in self.computers.keys():
			self.computers[ computerName ] = Computer( computerName, self.dataDir )
		connection.computer = self.computers[ computerName ]
		connection.user = username.split( "::" )[1]
		self.sendMessage( connection.socket, connection.address,
			BWLOCKCOMMAND_SETUSER, 0, 'login succeeded' )
		self.addRecord( 'login', 'login succeeded', connection )
		log.debug( "SETUSER from %s: %r", connection.address, username )


	def onSetSpace( self, space, connection ):
		connection.space = space
		self.sendMessage( connection.socket, connection.address,
			BWLOCKCOMMAND_SETSPACE, 0, 'set space to ' + space )
		log.debug( "SETSPACE from %s: %r", connection.address, space )


	def onLockChunk( self, rect, desc, connection ):
		log.debug( "LOCK from %s: rect=%r, %s", connection.address, rect, desc )
		if len( connection.space ) == 0:
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_LOCK, 1, 'space not set' )
		elif len( desc ) == 0:
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_LOCK, 1, 'must have desc' )
		elif connection.user == None:
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_LOCK, 1, 'user not set' )
		elif not rect.valid():
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_LOCK, 1, 'invalid rect' + repr( rect ) )
		else:
			for computer in self.computers.values():
				if computer != connection.computer and \
						computer.intersect( connection.space, rect ):
					self.sendMessage( connection.socket, connection.address,
						BWLOCKCOMMAND_LOCK, 1, 
						'conflict with computer ' + computer.name )
					return
			if connection.computer.addLock( connection.space, rect,
					connection.user, desc ) == 0:
				self.sendMessage( connection.socket, connection.address,
					BWLOCKCOMMAND_LOCK, 1, 
					'locked rect failed : ' + repr( rect ) +
						' already existed' )
			else:
				self.sendMessage( connection.socket, connection.address,
					BWLOCKCOMMAND_LOCK, 0, 'locked rect ' + repr( rect ) )
				self.addRecord( 'lock', 'locked rect ' + repr( rect ) +
					' for ' + desc, connection )
				connections = self.connections.values()[:]
				msg = pack( 'hhhh',
					rect.left, rect.top, rect.right, rect.bottom )
				msg += pack( 'I', len( connection.computer.name ) ) + \
					connection.computer.name
				msg += pack( 'I', len( connection.user ) ) + connection.user
				msg += pack( 'I', len( desc ) ) + desc
				msg += pack( 'f', time() )
				for c in connections:
					if c.space == connection.space and c.user != None:
						self.sendMessage( c.socket, c.address, 
							BWLOCKNOTIFY_LOCK, 0, msg )


	def onUnlockChunk( self, rect, desc, connection ):
		log.debug( "UNLOCK from %s: rect=%r, %s",
			connection.address, rect, desc )
		if len( connection.space ) == 0:
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_UNLOCK, 1, 'space not set' )
		elif len( desc ) == 0:
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_UNLOCK, 1, 'must have desc' )
		elif connection.user == None:
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_UNLOCK, 1, 'user not set' )
		elif not rect.valid():
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_UNLOCK, 1, 'invalid rect : ' + repr( rect ) )
		else:
			if connection.computer.removeLock( connection.space, rect ):
				self.sendMessage( connection.socket, connection.address,
					BWLOCKCOMMAND_UNLOCK, 0, 'unlocked rect ' + repr( rect ) )
				self.addRecord( 'unlock', 'unlocked rect ' + repr( rect ) +
					' for ' + desc, connection )
				connections = self.connections.values()[:]
				msg = pack( 'hhhh',
					rect.left, rect.top, rect.right, rect.bottom )
				msg += pack( 'I', len( connection.computer.name ) ) + \
					connection.computer.name
				msg += pack( 'I', len( connection.user ) ) + connection.user
				msg += pack( 'I', len( desc ) ) + desc
				msg += pack( 'f', time() )
				for c in connections:
					if c.space == connection.space and c.user != None:
						self.sendMessage( c.socket, c.address, 
							BWLOCKNOTIFY_UNLOCK, 0, msg )
			else:
				self.sendMessage( connection.socket, connection.address,
					BWLOCKCOMMAND_UNLOCK, 1, 
					'rect not locked : ' + repr( rect ) )


	def onGetStatus( self, connection ):
		log.debug( "GETSTATUS from %s", connection.address )
		if len( connection.space ) == 0:
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_GETSTATUS, 1, 'space not set' )
		elif connection.user == None:
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_GETSTATUS, 1, 'user not set' )
		else:
			msg = ''
			for computer in self.computers.values():
				if computer.lockNum( connection.space ) != 0:
					record = pack( 'I', len( computer.name ) ) + \
						computer.name + \
						pack( 'I', computer.lockNum( connection.space ) )
					for index in range( 0,
							computer.lockNum( connection.space ) ):
						lock = computer.lock( connection.space, index )
						rect = lock[0]
						username = lock[1]
						desc = lock[2]
						time = lock[3]
						record = record + pack( 'hhhh',
							rect.left, rect.top, rect.right, rect.bottom )
						record = record + pack( 'I', len( username ) ) + \
							username
						record = record + pack( 'I', len( desc ) ) + desc
						record = record + pack( 'f', time )
					msg = msg + pack( 'I', len( record ) ) + record
			self.sendMessage( connection.socket, connection.address,
				BWLOCKCOMMAND_GETSTATUS, 0, msg )


	def run( self ):
		self.isRunning = True
		while self.isRunning:
			try:
				self.step()
			except Exception, e:
				# log the error
				log.error( "%s", traceback.format_exc() )
		return 0

	def stop( self ):
		self.isRunning = False


def main( options, args ):
	# set up logging for daemon and non-daemon modes
	if not options.daemon:
		level = logging.INFO
		if options.verbose:
			level = logging.DEBUG
		log.setLevel( level )
		logging.basicConfig( format=LOG_FORMAT )
	else:
		if options.out_file:
			print "logging to %s" % options.out_file
			handler = logging.FileHandler( options.out_file )
			handler.setFormatter( logging.Formatter( LOG_FORMAT ) )
			log.setLevel( logging.DEBUG )
			log.addHandler( handler )


	log.info( "BWLockD started" )

	bindAddr = (options.bind_ip, options.bind_port)

	try:
		lockDaemon = LockDaemon( bindAddr, options.dataDir, options.historyPath )
		def stopDaemon( sig, stackFrame ):
			log.info( "BWLockD stopping" )
			lockDaemon.stop()

		signal.signal( signal.SIGINT, stopDaemon )
		signal.signal( signal.SIGTERM, stopDaemon )

		return lockDaemon.run()
	except:
		log.error( traceback.format_exc() )
		sys.exit( 1 )


def checkDataDir( dataDir ):

	absPath = os.path.abspath( dataDir )

	if not os.path.exists( dataDir ):
		print "Data directory does not exist (%s)" % absPath
		return False

	if not os.path.isdir( dataDir ):
		print "Data directory path is not a directory (%s)" % absPath
		return False

	if not os.access( dataDir, os.W_OK ):
		print "No write access to write to data directory path %s, " \
				"please check your permissions." % absPath
		return False

	return True


# main program
if __name__ == "__main__":
	parser = optparse.OptionParser( usage="%prog [options]")
	parser.add_option( '', '--daemon',
		action='store_true',
		dest='daemon', default=False,
		help="run process in the background (daemon mode)" )

	parser.add_option( '-I', '--bind-ip',
		dest="bind_ip",
		default='0.0.0.0',
		help="IP/hostname of interface to bind to (default all interfaces)" )

	parser.add_option( '-p', '--port',
		dest="bind_port",
		default=PORT,
		type="int",
		help="port to listen on (default %default)" )

	parser.add_option( '--pid',
		dest="pid_file",
		default="bwlockd.pid",
		help="default daemon PID file (default \"%default\")" )

	parser.add_option( '-o', '--output',
		dest="out_file",
		default="bwlockd.log",
		help="default daemon output file (only applies to daemon mode, "
			"default \"%default\")" )

	parser.add_option( '-v', '--verbose',
		dest="verbose",
		default=False,
		action="store_true",
		help="verbose output (only applies to non-daemon output, "
			"daemon output is always verbose)" )

	parser.add_option( '--history',
		dest="historyPath",
		default=None,
		help="output a history file that contains recent lock server "
			"operations in XML format" )

	defaultDataDirPath = os.path.abspath( os.path.dirname( __file__ ) )

	parser.add_option( '-d', '--data-dir',
		dest="dataDir",
		default=defaultDataDirPath,
		help="path to the data directory, default %default" )

	chdirDefault = os.path.abspath( os.path.dirname(sys.argv[0]) )

	parser.add_option( '-c', '--chdir',
		type = "string", dest = "chdir",
		default = chdirDefault,
		help = "bwlockd working directory (default '%default')" )

	options, args = parser.parse_args()

	if not checkDataDir( options.dataDir ):
		sys.exit( 1 )

	if options.daemon:
		daemon = Daemon( run=main,
			args=(options, args),
			workingDir = options.chdir,
			pidFile=options.pid_file,
			umask=0137 )
		daemon.start()
		sys.exit( 0 )
	else:

		sys.exit( main( options, args ) )

# bwlockd.py

