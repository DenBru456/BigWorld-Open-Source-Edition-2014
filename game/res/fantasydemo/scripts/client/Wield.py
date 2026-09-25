
import random
import BigWorld
from Helpers import PSFX

from Item import Item


# ------------------------------------------------------------------------------
# Class Wield:
#
# The Wield class is a derived class representing all weildable items in the
# game. It extends the use() and enact() methods for the Item class.
# ------------------------------------------------------------------------------

class Wield( Item ):
	typeRange = xrange( 30, 39 )
	SWORD_BASTARD			= 31
	SWORD_BASTARD_MITHRIL	= 32
	BATTLE_AXE				= 33

	maximumSparks = 10
	minimumSparks =  5

	# swords (wield) can swing
	canSwing = 1

	modelNames = {
		SWORD_BASTARD:			"sets/items/sword_bastard.model",
		SWORD_BASTARD_MITHRIL:	"sets/items/sword_bastard.model",
		BATTLE_AXE:				"sets/items/battleaxe.model",
	}

	dyeNames = {
		SWORD_BASTARD:			[("Blade","Default"), ("Flat","Default")],
		SWORD_BASTARD_MITHRIL:	[("Blade","Mithril"), ("Flat","Mithril")],
		BATTLE_AXE:				[("Blade","Mithril"), ("Flat","Mithril")],
	}


	displayNames = {
		SWORD_BASTARD:			"Fine Bastard Sword",
		SWORD_BASTARD_MITHRIL:	"Mithril Bastard Sword",
		BATTLE_AXE:				"Battle Axe"
	}


	guiIconNames = {
		SWORD_BASTARD:			"gui/maps/icon_items/icon_sword_bastard.dds",
		SWORD_BASTARD_MITHRIL:	"gui/maps/icon_items/icon_sword_bastard_mithril.dds",
		BATTLE_AXE:				"gui/maps/icon_items/icon_battleaxe.dds",
	}


	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Overrides base-class data.
	#	- Sets all member data to sensible values.
	# --------------------------------------------------------------------------
	def __init__( self, itemType, prereqs = None ):
		# methodName = "Item.Wield.__init__: "
		Item.__init__( self, Wield, itemType, prereqs )

		try:
			for dye in Wield.dyeNames[ itemType ]:
				setattr( self.model, dye[0], dye[1] )
		except:
			pass

	# This dictionary maps an old item type to the new item class and class subtype
	typeDict = {
		Item.SWORD_TYPE: SWORD_BASTARD,
		Item.SWORD_TYPE_2: SWORD_BASTARD_MITHRIL,
		Item.AXE_TYPE: BATTLE_AXE
	}


	# This method returns the basic prerequisites required for the item
	#@staticmethod
	def prerequisites( itemType ):
		return [Wield.modelNames[Wield.typeDict[itemType]]]

	prerequisites = staticmethod(prerequisites)

	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#	- Wields this item. This is an interface method defined by the Item
	#	  class.
	#	- Accepts a user (subject) and target (indirect object).
	# --------------------------------------------------------------------------
	def use( self, user, target ):
		#user.closeCombatCommence( self, target )

		if BigWorld.player() is user:
			try:
				user.playGesture( 46 )
			except AttributeError:
				pass

		return 1

	# --------------------------------------------------------------------------
	# Method: enact
	# Description:
	#	- Acts out the use of the wield. This is an interface method defined
	#	  by the Item class.
	#	- Accepts a user (subject) and target (indirect object).
	# --------------------------------------------------------------------------
	def enact( self, user, target ):
		target

		# delay swing noise till the 2nd half of animation
		# BigWorld.playFxDelayed("sword/med/swish", 0.334, user.position)
		user.model.SwingSword();


	# --------------------------------------------------------------------------
	# Method: createSparks
	# Description:
	#	- Helper method to create sparks from the sword.
	# --------------------------------------------------------------------------
	def createSparks( self ):
		numSparks = random.random() * ( Wield.maximumSparks -
			Wield.minimumSparks ) + Wield.minimumSparks
		PSFX.attachSparks( self.model, None, numSparks )

#Item.py
