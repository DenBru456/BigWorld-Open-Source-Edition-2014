
from Item import Item

# ------------------------------------------------------------------------------
# Class Food:
#
# The Food class is a derived class representing all edible items in the game.
# It extends the use() and enact() methods for the Item class.
# ------------------------------------------------------------------------------

class Food( Item ):
	# --------------------------------------------------------------------------
	# The different types of food are listed below. The value of ALLOWED_TYPE
	# should always be set to the highest value that the itemType can take.
	# --------------------------------------------------------------------------
	typeRange = xrange( 10, 19 )
	STRIFF_DRUMSTICK	= 11
	SPIDER_LEG			= 12
	WINE_GOBLET			= 13


	# --------------------------------------------------------------------------
	# The dictionary of food models is listed below. A model name is the name
	# of the file containing model information for drawing and animating
	# food in the game world.
	# --------------------------------------------------------------------------
	modelNames = {
		STRIFF_DRUMSTICK:	"sets/items/item_food_drumstick.model",
		SPIDER_LEG:			"characters/npc/spider/spider_leg.model",
		WINE_GOBLET:		"sets/items/grail.model"
	}


	# --------------------------------------------------------------------------
	# The dictionary of food names is listed below. A display name is the
	# default text displayed to the client when targeting food.
	# --------------------------------------------------------------------------
	displayNames = {
		STRIFF_DRUMSTICK:	"Striff Drumstick",
		SPIDER_LEG:			"Spider Leg",
		WINE_GOBLET:		"Wine Goblet"
	}


	# --------------------------------------------------------------------------
	# The dictionary of food icons is listed below. A GUI icon name is the
	# file containing the bitmap for food when selected in the GUI.
	# --------------------------------------------------------------------------
	guiIconNames = {
		STRIFF_DRUMSTICK:	"gui/maps/icon_items/icon_food_drumstick.tga",
		SPIDER_LEG:			"gui/maps/icon_items/icon_spider_leg.tga",
		WINE_GOBLET:		"gui/maps/icon_items/icon_grail.tga"
	}


	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Overrides base-class data.
	#	- Sets all member data to sensible values.
	# --------------------------------------------------------------------------
	def __init__( self, itemType, prereqs = None ):
		# methodName = "Item.Food.__init__: "
		Item.__init__( self, Food, itemType, prereqs )

	# This dictionary maps an old item type to the new item class and class subtype
	typeDict = {
		Item.DRUMSTICK_TYPE: STRIFF_DRUMSTICK,
		Item.SPIDER_LEG_TYPE: SPIDER_LEG,
		Item.GOBLET_TYPE: WINE_GOBLET
	}

	# This method returns the basic prerequisites required for the item
	#@staticmethod
	def prerequisites( itemType ):
		return [Food.modelNames[Food.typeDict[ itemType ]]]

	prerequisites = staticmethod(prerequisites)

	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#	- Uses the food. This is an interface method defined by the Item
	#	  class.
	#	- Accepts a user (subject) and target (indirect object).
	# --------------------------------------------------------------------------
	def use( self, user, target ):
		if target != None: return 0

		if not user.inCombat():
			# TBD: For now, this is being done for backwards compatibility
			# until Avatar is cleaned up.
			user.eat( self.itemType )
			user.cell.eat( self.itemType )
			# How can the user ever be in combat mode with a food item in hand??

		return 1

	# --------------------------------------------------------------------------
	# Method: enact
	# Description:
	#	- Acts out the use of the food. This is an interface method defined by
	#	  the Item class.
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
					entity.model.Idle.stop()
					entity.model.HoldUpright()
				except:
					pass
		# Set up the Item's holding animation.
		if self.model != None and self.model.inWorld:
			try:
				self.model.Idle()
			except:
				pass

	# --------------------------------------------------------------------------
	# Method: setHoldingStyle
	# Description:
	#	- Sets the action matcher capabilities for a particular item. This
	#	  allows an Item to specify what type of idle is used when it is
	#	  equiped.
	# --------------------------------------------------------------------------
	def setHoldingStyle( self, entity ):
		entity.model.HoldUpright()

