import BigWorld

TIMEOUT_PERIOD = 660
CHECK_PERIOD = 20

class KeepAlive( object ):
	def __init__( self ):
		self.lastKeepAlivePing = BigWorld.time()
		self.start()

	def start( self ):
		self.keepAliveTimer = self.addTimer( 0, CHECK_PERIOD )

	def onTimer( self, timerID, userArg ):
		if timerID == self.keepAliveTimer:
			if self.lastKeepAlivePing + TIMEOUT_PERIOD < BigWorld.time():
				self.cancelKeepAlive()

				# Need to check for old-style keepalive too
				if not self.haveWebClient:
					self.webLogout()

	def hasWebClient( self ):
		return self.keepAliveTimer != 0

	def cancelKeepAlive( self ):
		self.delTimer( self.keepAliveTimer )
		self.keepAliveTimer = 0

	def webKeepAlivePing( self ):
		if not self.haveWebClient:
			self.start()

		self.lastKeepAlivePing = BigWorld.time()

	# Old version of keepalive for old WebIntegration. onKeepAliveStart and
	# onKeepAliveStop are now considered deprecated.

	# Create a property so that the old use of haveWebClient still works.
	def get_haveWebClient( self ):
		return self.__dict__.get( "haveWebClient" ) or self.hasWebClient()

	def set_haveWebClient( self, value ):
		self.__dict__[ "haveWebClient" ] = value

	haveWebClient = property( get_haveWebClient, set_haveWebClient )

	def onKeepAliveStart( self ):
		self.haveWebClient = True

	def onKeepAliveStop( self ):
		print "%s(%d).onKeepAliveStop" % (self.__class__.__name__, self.id)
		self.haveWebClient = False
		self.webLogout()


# KeepAlive.py
