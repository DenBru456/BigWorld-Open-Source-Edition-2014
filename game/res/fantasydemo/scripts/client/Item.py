import BigWorld
import ItemBase
from Helpers import Caps
import traceback

# ------------------------------------------------------------------------------
# Class Item:
#
# The Item class is a base class for the items in the game. Each item contains
# game mechanic information but does not actually exist on its own in the game.
# An in-game item exists when it becomes part of a DroppedItem entity. An item
# can also exist as part of an entity's inventory.
# ------------------------------------------------------------------------------

class Item( ItemBase.ItemBase ):
	"TODO: Document"

	canShoot = 0
	canSwing = 0

	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Loads all base-class data members.
	#	- Derived classes must call the base class __init__ method, supplying it
	#	  the derived class and its type.
	# --------------------------------------------------------------------------
	def __init__( self, child, itemType, prereqs = None ):
		methodName = "Item.__init__: "

		#
		# Check the itemType.
		#
		if not itemType in child.typeRange:
			raise AssertionError, methodName + "illegal item type."
		else:
			self.itemType = itemType

		#
		# Check the model name for the item.
		#
		if self.itemType in child.modelNames.keys():
			modelName = child.modelNames[ self.itemType ]
		else:
			modelName = child.modelNames[ child.UNKNOWN_TYPE ]
			print methodName + "itemType: " + \
				str( self.itemType ) + " has no corresponding model."

		#
		# Load the model for the item.
		#
		if modelName != None:
			if prereqs != None:
				try:
					self.model = prereqs.pop(modelName)
				except KeyError:
					traceback.print_stack()
					self.model = None
			else:
				self.model = BigWorld.Model(modelName)
			if self.model == None:
				print methodName + "failed to load model " + modelName
		else:
			self.model = None

		#
		# Check the display name for the item.
		#
		if not self.itemType in child.displayNames.keys():
			print methodName + "itemType: " + \
				str( self.itemType ) + " has no display name."
			self.displayName = child.displayNames[ child.UNKNOWN_TYPE ]
		else:
			self.displayName = child.displayNames[ self.itemType ]


	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#	- Uses the item.
	#	- This method is called by the local client for any entities controlled
	#	  by the client. Items know the conditions under which they can be
	#	  used. The logic for this is handled by this method.
	#	- Accepts a user (subject) and target (indirect object).
	# Note:
	#	If the item can't be used, or if it can't be used with the given target,
	#	then this function must return the value false. Otherwise, if it is
	#	used, it should return the value true. It should never return None.
	# --------------------------------------------------------------------------
	def use( self, user, target ):
		return 0


	# --------------------------------------------------------------------------
	# Method: enact
	# Description:
	#	- Acts out the use of the item.
	#	- This method is called by the local client for all entities when
	#	  wanting to know how to use the item. Items know the steps involved
	#	  in using itself and how to portray it to the game world. The logic
	#	  for this is handled by this method.
	#	- Accepts a user (subject) and target (indirect object).
	# --------------------------------------------------------------------------
	def enact( self, user, target ):
		pass


	# --------------------------------------------------------------------------
	# Method: enactIdle
	# Description:
	#	- Tells the item's model to begin its idle animation.
	#	- Any item model with an animation must have this called when it
	#	  enters the world as part of an Entity. This is because the models are
	#	  shared between Entities. If not, an instance will appear to have the
	#	  animation frame of the previous instance's action.
	# --------------------------------------------------------------------------
	def enactIdle( self, entity = None ):
		# Set up the entity's holding style if an entity was specified.
		if entity != None:
			if entity.model != None and entity.model.inWorld:
				try:
					entity.model.HoldUpright.stop()
				except:
					pass
		# Set up the Item's holding animation.
		if self.model != None and self.model.inWorld:
			try:
				self.model.Idle()
			except:
				pass


	def enactDrawn( self, entity = None ):
		self.enactIdle( entity )

	# --------------------------------------------------------------------------
	# Method: name
	# Description:
	#	- Returns a reference to the string containing the name of the Item.
	# --------------------------------------------------------------------------
	def name( self ):
		return self.displayName

	# Called by the player when it enters the 'using item' mode with this item
	def retain( self, owner ):
		pass

	# Called by the player when it exits the 'using item' mode with this item
	def release( self, owner ):
		pass

	# Called by anyone when they swap out the item
	def unequip( self, user ):
		pass

	def equipByPlayer( self, player ):
		"""Sets the target capabilities and gui icon and other stuff
		which should be set when the player equips this item"""

		if not player.inCombat():
			BigWorld.target.caps( Caps.CAP_CAN_USE )


	def glanceByPlayer( self, player ):
		"""Sets the gui icon and other stuff which should be set
		immediately after the player considers this item.
		equipByPlayer may not necessarily be called afterwards if it
		is switched through before the item is withdrawn"""

		# update gui
		player.itemGui.itemIcon.visible = 1
		player.itemGui.itemBack.visible = 1
		player.itemGui.itemIcon.textureName = \
			ItemLoader.resolveIconName( self.itemType )

#Item.py
