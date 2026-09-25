import BigWorld
import ItemLoader
from Helpers import Caps
from Helpers.CallbackHelpers import IgnoreCallbackIfDestroyed
from FDGUI import Minimap


class DroppedItem( BigWorld.Entity ):
	'''Plays the role of a collectible item dropped on the ground (client-side).
	'''

	def __init__( self ):
		BigWorld.Entity.__init__( self )

		# Common Entity State Variables
		self.targetCaps = [ Caps.CAP_CAN_USE ]

		if self.onGround:
			self.filter = BigWorld.AvatarDropFilter()
		else:		
			self.filter = BigWorld.DumbFilter()

		self.pickedUpBy = None
		self.model      = None
		self.item       = None


	def name( self ):
		'''Returns the name of the DroppedItem. It uses the name
		provided by the item currently assigned as this DroppedItem type.
		'''
		if self.item != None:
			return self.item.name()
		else:
			return "Uninstantiated DroppedItem"


	def onEnterWorld( self, prereqs ):
		'''Called when this entity is entering the client world.
		If the item is flagged as just dropped (dropperID not zero),
		it notifies the dropper entity that this item has just been
		dropped by it. Otherwise, show item immediatly.
		'''		
		if self.item != None:
			self.item.enactIdle()

		if self.dropperID != 0:
			try:
				dropper = BigWorld.entities[ self.dropperID ]
				dropper.dropNotify( self )
				self.dropperID = 0
			except KeyError:
				errorMsg = 'DroppedItem.onEnterWorld: dropper not local (%d)'
				print errorMsg % self.dropperID
		else:
			self._resetItem()
		Minimap.addEntity( self )


	def onLeaveWorld( self):
		Minimap.delEntity( self )
		if self.item != None:
			self.item.unequip( None )
		self.model = None


	def use( self ):
		'''The default use of a DroppedItem is to be picked-up by the player.
		'''
		if Caps.CAP_CAN_USE in self.targetCaps and self.pickUpTry():
			BigWorld.player().pickExecute( self )


	def pickUpTry( self ):
		'''Returns true if the item has not already been picked 
		up by another entity. There is no sense in setting pickedUpBy 
		here because its new value will not propagate to other clients.
		'''
		return self.pickedUpBy == None


	def pickUpNotify( self, picker ):
		'''An entity is picking up this item. The 
		player will no longer be allowed to pick it up.
		Params:
			picker			entity picking up this item
		'''
		self.pickedUpBy = picker


	def pickUpComplete( self ):
		'''An entity has finished picking up this item.
		It will soon be destroyed, but hide it immediatly.
		'''
		self.model = None


	def dropComplete( self ):
		'''An entity has finished dropping this item.
		Reset its internals and show it immediatly.
		'''
		self._resetItem()


	def _resetItem( self ):
		'''Reset items internal variables.
		'''
		# load the item and show it
		ItemLoader.LoadBG( self.classType, self._showModel )


	@IgnoreCallbackIfDestroyed
	def _showModel( self, itemLoader ):
		'''Show model if item is correctly set.
		'''
		self.item = ItemLoader.newItem( self.classType, itemLoader.resourceRefs )

		# show the model
		if self.item != None:
			self.model = self.item.model
			if self.inWorld:
				self.item.enactIdle()


# Preload function
def preload( list ):
	'''Load all the items
	'''
	ItemLoader.Item_preload( list )

#DroppedItem.py
