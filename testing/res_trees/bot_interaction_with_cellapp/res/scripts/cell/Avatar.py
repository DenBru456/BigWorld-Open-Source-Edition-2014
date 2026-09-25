import BigWorld


class Avatar( BigWorld.Entity ):

	def __init__( self, nearbyEntity ):
		BigWorld.Entity.__init__( self )


	def talkToOthers( self, source, who ):
		print "Talking to other bots"
		target = BigWorld.entities[who]
		if target != None:
			target.talk()
	
	def talk( self ):
		if self.botTalked < 10:
			self.botTalked += 1
			print "Avatar:talk: entityID %s botTalked %s" % (self.id, self.botTalked)