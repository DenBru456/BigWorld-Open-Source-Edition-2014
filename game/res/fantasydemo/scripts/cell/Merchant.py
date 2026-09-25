import BigWorld
import AvatarMode
import Avatar


class Merchant( BigWorld.Entity ):
	'''
	'''
	INNER_RANGE = 5


	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.addProximity( Merchant.INNER_RANGE )


	def commerceStartRequest( self, avatarBase ):
		'''An avatar wants to trade with this Merchant.
		Params:
			avatarBase				requesting avatar's base mailbox
		'''
		if avatarBase.className != 'Avatar':
			errorMsg = 'Merchant.commerceStartRequest: entity not an Avatar: %d'
			print errorMsg % avatarBase.id
			return;

		if self.modeTarget == AvatarMode.NO_TARGET:
			self.modeTarget = avatarBase.id
			avatarBase.cell.commerceStartResponse( True, self.id )
			self.base.commerceItemsRequest( avatarBase )
		else:
			avatar.commerceStartResponse( False, 0 )


	def commerceCancelRequest( self ):
		'''The avatar wants to cease trading with this Merchant.
		'''
		self._commerceCancel()


	def onEnterTrap( self, entity, range, trap ):
		'''Some entity has entered the proximity trap. Just ignore it.
		'''
		pass


	def onLeaveTrap( self, entity, range, trap ):
		'''The avatar has move far from this Merchant.
		If it is our trading partiner, cancel trading with him.
		'''
		if entity.id == self.modeTarget:
			self._commerceCancel()


	def _commerceCancel( self ):
		'''Cancel trading with the current partner avatar.
		'''
		self.modeTarget = AvatarMode.NO_TARGET

	def onWitnessed( self, witnessed ):
		'''Callback for when this entity to receive witness events.  When this
		entity enters the AoI of a witness entity, then it is called back with
		witnessed=True. After 12 minutes of being outside of all witness
		entities' AoI, this is called back with witnessed=False.

		This is a good place for switching on/off CPU-intensive tasks that only
		matter if there is an entity witnessing us, e.g. AI processing.
		'''

		if not witnessed:
			msg = "We have not been witnessed in some time"
		else:
			msg = "We have been witnessed!"
		print "Merchant(%d): %s" % (self.id, msg,)

	def sayToAoI( self, msg ):
		self.allClients.chat( msg )

# Merchant.py
