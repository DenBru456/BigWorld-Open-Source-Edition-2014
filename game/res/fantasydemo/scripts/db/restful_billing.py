import BackgroundTask
import BigWorld

import ResMgr

import billing_system_settings
import cgi
import json
import urllib
import urllib2

import socket
import struct

NUM_THREADS = 1

class GetTask( BackgroundTask.BackgroundTask ):
	def __init__( self, username, password, response ):
		self.username = username
		self.password = password
		self.response = response

	def doBackgroundTask( self, bgTaskMgr, connection ):
		self.result = connection.getEntityKeyForAccount(
							self.username, self.password )
		bgTaskMgr.addMainThreadTask( self )

	def doMainThreadTask( self, bgTaskMgr ):
		try:
			self.processResult()
		except:
			self.response.failureDBError()
			raise

	def entityType( self ):
		entityType = self.result[ 'entityType' ]

		return entityType if entityType else "Account"

	def processResult( self ):
		result = self.result
		responseType = result[ 'response' ]

		if responseType == "loadEntity":
			self.response.loadEntity( self.entityType(),
					result[ "entityID" ] )
		elif responseType == "createNewEntity":
			self.response.createNewEntity( self.entityType(),
					result[ "shouldRemember" ] )
		elif responseType == "failureInvalidPassword":
			self.response.failureInvalidPassword()
		elif responseType == "failureNoSuchUser":
			self.response.failureNoSuchUser()
		else:
			self.response.failureDBError()


class SetTask( BackgroundTask.BackgroundTask ):
	def __init__( self, username, entityType, entityID ):
		self.username = username
		self.entityType = entityType
		self.entityID = entityID

	def doBackgroundTask( self, bgTaskMgr, connection ):
		result = connection.setEntityKeyForAccount( self.username,
				self.entityType, self.entityID )


# This class allows us to do a PUT request.
class PutRequest( urllib2.Request ):
	def get_method( self ):
		return "PUT"


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

	def _request( self, username,
			requestType = urllib2.Request, dataStr = None, **kwargs ):

		headers = { "Authorization" : self.privateKey }
		req = requestType( self._generateUrl( username, **kwargs ), dataStr,
			   headers )

		with urllib2.urlopen( req ) as f:
			return json.load( f )

	def getEntityKeyForAccount( self, username, password ):
		return self._request( username, signin_key = password )

	def setEntityKeyForAccount( self, username, entityType, entityID ):
		return self._request( username, requestType = PutRequest,
				entityType = entityType, entityID = entityID )


# This class integrates with a RESTful billing system.
class BillingSystem( object ):
	def __init__( self ):
		print "BillingSystem.__init__:"

		ds = ResMgr.openSection( "server/remote_auth_key.xml" )

		host = ds.readString( "host" )
		publicKey = ds.readString( "publicKey" )
		privateKey = ds.readString( "privateKey" )

		connection = Connection( host = host,
				publicKey = publicKey,
				privateKey = privateKey )

		# TODO: Do a sanity-check connection of config options

		self.bgTaskMgr = BackgroundTask.Manager()
		threadDataCreator = lambda : connection
		self.bgTaskMgr.startThreads( NUM_THREADS, threadDataCreator )


	# This method validates account details and returns the entity key that this
	# account should use.
	def getEntityKeyForAccount( self, username, password,
			clientAddr, response ):
		ip = socket.inet_ntoa(
			struct.pack( '!I', socket.ntohl( clientAddr[0] ) ) )
		port = socket.ntohs( clientAddr[1] )

		print "%s is logging in from %s:%d '%s'" % (username, ip, port, password)
		self.bgTaskMgr.addBackgroundTask(
				GetTask( username, password, response ) )

	# This method is called to add new account details. This will only be called
	# if createNewEntity is called with shouldRemember as True.
	def setEntityKeyForAccount( self, username, password,
			entityType, entityID ):
		print "setEntityKeyForAccount:", username, password
		self.bgTaskMgr.addBackgroundTask(
				SetTask( username, entityType, entityID ) )

# restful_billing.py
