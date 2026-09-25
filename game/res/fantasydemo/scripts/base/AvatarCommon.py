# ------------------------------------------------------------------------------
# Section: class AvatarCommon
# ------------------------------------------------------------------------------

class AvatarCommon:
	def __init__( self ):
		pass

	def onClientDeath( self ):
		print "Help: The base just told us (id %d) we're dead!" % self.id
		self.logOff()

	def groupChat( self, msg ):
		if self.group:
			self.group.tellOthers( self.id, msg )
		else:
			print self.id, " is trying to chat with no group."

	def logOff( self ):
		print "trying to destroy cell entity (id %d)" % self.id
		if hasattr( self, "cell" ):
			self.destroyCellEntity()
		else:
			self.destroy()

	def tellClient( self, type, src, msg ):
		self.client.message( type, src, unicode( msg ) )

	def groupList( self ):
		if self.group:
			self.group.list( self.id )
		else:
			self.tellClient( 3, "", "Not currently in a group" )

	def tell( self, dstName, msg ):
		print "tell", dstName, msg
		self.internalTell( dstName, msg )

	def setRightHand ( self, item ):
		pass

	def onLoseCell( self ):
		self.destroy()
# AvatarCommon.py
