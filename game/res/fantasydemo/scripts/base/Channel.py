import BigWorld

# ------------------------------------------------------------------------------
# Section: class Channel
# ------------------------------------------------------------------------------

class Channel( BigWorld.Base ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.members = {}
		print "New group", self.id

	def register( self, registrant ):
		id = registrant.id

		# For debugging
		if self.members.has_key( id ):
			print "Trying to re-register ", id
		else:
			print "%d is joining group %d" % (id, self.id)
			self.members[ id ] = registrant

		self.broadcast( unicode( id ) + u" has joined the group." )

	def deregister( self, id ):
		self.broadcast( unicode( id ) + u" has left the group." )

		try:
			del( self.members[ id ] )
		except:
			print "Cannot deregister ", id, ". Keys = ", self.members.keys()

		# TODO: Should kill itself when there are no more members. Need to be
		# careful about synchronisation issues.
		if len( self.members ) == 0:
			self.destroy()

	def tellOthers( self, source, message ):
		print 'Telling other "%s".' % (message, )
		for key in self.members.keys():
			if key != source:
				print "Telling", key
				self.members[ key ].tellClient( 2, unicode(source), message )
				print "Done"

	def broadcast( self, message ):
		message = unicode( message )

		for value in self.members.values():
			# TODO: Could be another type.
			value.tellClient( 2, "Broadcast", message )

	def list( self, id ):
		self.members[ id ].tellClient( 2, "List", unicode( self.members.keys() ) )

# Channel.py
