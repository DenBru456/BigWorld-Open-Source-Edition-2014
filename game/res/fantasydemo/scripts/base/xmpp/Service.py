import BigWorld
import ResMgr

import errno
import logging
import os
import socket

import BWTwistedReactor
BWTwistedReactor.install()

from twisted.internet import defer
from twisted.names import client as namesClient

log = logging.getLogger( "XMPP" )

class ServiceStatus( object ):
	def __init__( self ):
		self.host = None
		self.port = None
		self.resolvedHost = None
		self.resourceName = None
		self.isActive = False

		self.isInitialised = False

		self.deferredIsEnableds = []
		self.deferredDetails = []

		self.deferredStartup = None


	def isEnabled( self ):
		"""
		This method returns a Deferred which will be called back with either
		True or False once ServiceStatus completes its startup
		"""
		deferred = defer.Deferred()

		if self.isInitialised:
			deferred.callback( self.isActive )
		else:
			self.deferredIsEnableds.append( deferred )

		return deferred


	def details( self ):
		"""
		This method returns a Deferred which will be called back with a tuple of
		( host, resolvedHost, port ) of the XMPP Server this Service refers to,
		once ServiceStatus completes its startup successfully, or
		( None, None, None) if ServerStatus fails to complete its startup
		"""
		deferred = defer.Deferred()

		if self.isInitialised and self.isActive:
			deferred.callback( ( self.host, self.resolvedHost, self.port ) )
		elif self.isInitialised:
			deferred.callback( ( None, None, None ) )
		else:
			self.deferredDetails.append( deferred )

		return deferred


	def startup( self, configFile ):
		"""
		This method attempts to start the ServiceStatus. Returns a Deferred
		which will be called back with ( True, None ) if startup succeeds, or
		( False, failureReason ) if startup fails.

		Will raise an exception if it is called again
		"""
		if self.isInitialised or self.deferredStartup is not None:
			raise ValueError( "xmpp.Service is already initialised" )

		result = defer.Deferred()

		self.deferredStartup = result

		sec = ResMgr.openSection( configFile )
		if not sec:
			self.__onStartupFailed( "Invalid config file '%s'" % configFile )
			return result

		self.host = sec.readString( "xmppServer/host" )
		self.port = sec.readString( "xmppServer/port" )
		self.resourceName = sec.readString( "xmppServer/resourceName" )

		isEnabledInConfig = sec.readBool( "enabled", False )
		if not isEnabledInConfig:
			self.__onStartupFailed( "Disabled in '%s'" % configFile )
			return result

		log.info( "Service::init: Validating XMPP server '%s:%s'",
			self.host, self.port )

		deferredGetHostByName = namesClient.getHostByName( self.host )

		deferredGetHostByName.addCallbacks( self.__onGetHostByNameCallback, \
			self.__onGetHostByNameErrback )

		return result


	def __onGetHostByNameCallback( self, address ):
		"""
		Callback from Twisted's DNS client if we got a DNS lookup result
		"""
		self.resolvedHost = address

		sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		sock.setblocking( False )
		connectionStatus = sock.connect_ex( \
			(self.resolvedHost, int( self.port )) )

		# Immediate failure? EINPROGRESS means it's running async,
		# and the Python documentation states that 0 is a success
		if connectionStatus != 0 and connectionStatus != errno.EINPROGRESS:
			self.__onStartupFailed( "Failed to connect to XMPP server: %s"
				% ( os.strerror( connectionStatus ), ) )
			return

		BigWorld.registerFileDescriptor( sock, self.__onSocketReadyToRead )
		BigWorld.registerWriteFileDescriptor( sock, self.__onSocketReadyToWrite )


	def __onGetHostByNameErrback( self, failure ):
		"""
		Callback from Twisted's DNS client if we failed the DNS lookup
		"""
		self.__onStartupFailed( "Failed to resolve XMPP server: %s" %
			( failure.type, ) )


	def __onSocketReadyToRead( self, sock ):
		"""
		Callback from BigWorld when the connection to the server is
		readable or closed
		"""
		BigWorld.deregisterFileDescriptor( sock )
		BigWorld.deregisterWriteFileDescriptor( sock )
		sockError = sock.getsockopt( socket.SOL_SOCKET, socket.SO_ERROR )
		if sockError == 0:
			data = sock.recv( 16 )
			sock.shutdown( socket.SHUT_RDWR )
			sock.close()

		if sockError == 0 and data:
			# If we received data, it worked
			self.__onStartupSucceeded()
		else:
			# Otherwise, the socket was shutdown or failed to connect
			self.__onStartupFailed( "Failed to connect to XMPP server: %s" \
				% ( os.strerror( sockError ), ) )
		

	def __onSocketReadyToWrite( self, sock ):
		"""
		Callback from BigWorld when the connection to the server is writable
		"""
		BigWorld.deregisterFileDescriptor( sock )
		BigWorld.deregisterWriteFileDescriptor( sock )
		sockError = sock.getsockopt( socket.SOL_SOCKET, socket.SO_ERROR )
		sock.shutdown( socket.SHUT_RDWR )
		sock.close()

		if sockError == 0:
			# If we're writable and have no error codes, it worked
			self.__onStartupSucceeded()
		else:
			# Otherwise, we got an error of some kind, so report it
			self.__onStartupFailed( "Failed to connect to XMPP server: %s" \
				% ( os.strerror( sockError ), ) )


	def __onStartupSucceeded( self ):
		"""
		This method triggers all the pending Deferreds for init success
		"""
		log.info( "Service::init: XMPP server '%s:%s' (%s) is alive",
			self.host, self.port, self.resolvedHost )

		self.isInitialised = True
		self.isActive = True

		for deferred in self.deferredDetails:
			deferred.callback( ( self.host, self.resolvedHost, self.port ) )
		self.deferredDetails = []

		for deferred in self.deferredIsEnableds:
			deferred.callback( True )
		self.deferredIsEnableds = []

		self.deferredStartup.callback( ( True, None ) )
		self.deferredStartup = None


	def __onStartupFailed( self, reason ):
		"""
		This method triggers all the pending Deferreds for init failure
		"""
		log.error( "Service::init: XMPP server '%s:%s' (%s) is not usable: %s",
			self.host, self.port, self.resolvedHost, reason )

		self.isInitialised = True
		self.isActive = False

		for deferred in self.deferredDetails:
			deferred.callback( ( None, None, None ) )
		self.deferredDetails = []

		for deferred in self.deferredIsEnableds:
			deferred.callback( False )
		self.deferredIsEnableds = []

		self.deferredStartup.callback( ( False, reason ) )
		self.deferredStartup = None


__serviceStatus = ServiceStatus()


def isEnabled():
	"""
	This function returns a Deferred which will be called back with either
	True or False once Service is initialised
	"""
	return __serviceStatus.isEnabled()


def details():
	"""
	This function returns a Deferred which will be called back with a tuple of
	( host, resolvedHost, port ) of the XMPP Server this Service refers to, once
	the Service is initialised, or ( None, None, None) if the Service fails to
	initialise
	"""
	return __serviceStatus.details()


def init( configFile ):
	"""
	Attempt to initialise the Service. Returns a Deferred which will be
	called back with ( True, None ) if initialisation succeeds, or
	( False, failureReason ) if it fails.

	Will raise an exception if it is called again
	"""
	return __serviceStatus.startup( configFile )

	
__all__ = [ "isEnabled", "init", "details" ]

# Service.py
