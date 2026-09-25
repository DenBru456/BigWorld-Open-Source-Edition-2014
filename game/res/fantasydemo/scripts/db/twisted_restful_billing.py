import BWTwistedReactor
BWTwistedReactor.install()

from twisted.internet import reactor

# This allows support for twisted.web.client
if not reactor.running:
	reactor.startRunning()

import BigWorld

import ResMgr

from twisted.web import client
import functools

import billing_system_settings
import cgi
import json
import urllib

import socket
import struct

class GetEntityResponseHandler( object ):
	def __init__( self, response ):
		self.response = response

	def onSuccess( self, page ):
		result = json.loads( page )
		responseType = result[ 'response' ]

		entityType = result.get( 'entityType' )

		if not entityType:
			entityType = "Account"

		if responseType == "loadEntity":
			self.response.loadEntity( entityType, result[ "entityID" ] )

		elif responseType == "createNewEntity":
			self.response.createNewEntity( entityType, result[ "shouldRemember" ] )

		elif responseType == "failureInvalidPassword":
			self.response.failureInvalidPassword()

		elif responseType == "failureNoSuchUser":
			self.response.failureNoSuchUser()

		else:
			self.response.failureDBError()


	def onFailure( self, error ):
		print "twisted_restful_billing failure:", error
		self.response.failureDBError()


def printError( error ):
	print "Error is:", error


# This class handles the "connection" to the remote server.
class Connection( object ):
	def __init__( self, host, publicKey, privateKey ):
		self.host = host
		self.publicKey = publicKey
		self.privateKey = privateKey
		self.urlPrefix = "%s/api/games/%s/signins/" % (host, publicKey)

	def _generateUrl( self, username, **kwargs ):
		return ''.join( (self.urlPrefix, cgi.escape( username ), "?",
				urllib.urlencode( kwargs )) )

	def _request( self, username, method = "GET", **kwargs ):

		headers = { "Authorization" : self.privateKey }

		url = self._generateUrl( username, **kwargs )
		deferred = client.getPage( url, method = method, headers = headers )

		return deferred

	def getEntityKeyForAccount( self, username, password ):
		return self._request( username, signin_key = password )

	def setEntityKeyForAccount( self, username, entityType, entityID ):
		return self._request( username, method = "PUT",
				entityType = entityType, entityID = entityID )


# This class integrates with a RESTful billing system.
class BillingSystem( object ):
	def __init__( self ):
		print "BillingSystem.__init__:"

		ds = ResMgr.openSection( "server/remote_auth_key.xml" )

		host = ds.readString( "host" )
		publicKey = ds.readString( "publicKey" )
		privateKey = ds.readString( "privateKey" )

		self.connection = Connection( host = host,
				publicKey = publicKey,
				privateKey = privateKey )

		# TODO: Do a sanity-check connection of config options


	# This method validates account details and returns the entity key that this
	# account should use.
	def getEntityKeyForAccount( self, username, password,
			clientAddr, response ):
		ip = socket.inet_ntoa(
			struct.pack( '!I', socket.ntohl( clientAddr[0] ) ) )
		port = socket.ntohs( clientAddr[1] )

		deferred = self.connection.getEntityKeyForAccount( username, password )
		task = GetEntityResponseHandler( response )
		deferred.addCallbacks( task.onSuccess, task.onFailure )

		deferred.addErrback( printError )

	# This method is called to add new account details. This will only be called
	# if createNewEntity is called with shouldRemember as True.
	def setEntityKeyForAccount( self, username, password,
			entityType, entityID ):
		print "setEntityKeyForAccount:", username, password
		self.connection.setEntityKeyForAccount( username, entityType, entityID )

# twisted_restful_billing.py
