
import FantasyDemo
from Helpers import BWKeyBindings

from Item import Item

# ------------------------------------------------------------------------------
# Class Gadget:
#
# The Gadget class is a derived class representing a catch-all category of
# useful to semi-useful items in the game. The Gadget class extends the use()
# and enact() methods for the Item class.
# ------------------------------------------------------------------------------

class Gadget( Item ):
	"TODO: Document"

	# --------------------------------------------------------------------------
	# The different types of gadgets are listed below. The value of
	# ALLOWED_TYPE should always be set to the highest value that the itemType
	# can take.
	# --------------------------------------------------------------------------
	typeRange = xrange(20,29)
	BINOCULARS			= 23


	# --------------------------------------------------------------------------
	# The dictionary of gadget models is listed below. A model name is the name
	# of the file containing model information for drawing and animating the
	# gun in the game world.
	# --------------------------------------------------------------------------
	modelNames = {
		BINOCULARS:			"sets/items/binocver2.model"
	}


	# --------------------------------------------------------------------------
	# The dictionary of gadget names is listed below. A display name is the
	# default text displayed to the client when targeting the gadget.
	# --------------------------------------------------------------------------
	displayNames = {
		BINOCULARS:			"Binoculars"
	}


	# --------------------------------------------------------------------------
	# The dictionary of gadget icons is listed below. A GUI icon name is the
	# file containing the bitmap for the gadget when selected in the GUI.
	# --------------------------------------------------------------------------
	guiIconNames = {
		BINOCULARS:			"gui/maps/icon_items/icon_tek_binoc2.tga"
	}


	class BinocularsActionHandler( BWKeyBindings.BWActionHandler ):

		def __init__( self, owner ):
			self.owner = owner
			BWKeyBindings.BWActionHandler.__init__( self )

		@BWKeyBindings.BWKeyBindingAction( "CameraKey" )
		def cameraKey( self, isDown ):
			if isDown:
				return True
			else:
				return False

		@BWKeyBindings.BWKeyBindingAction( "EscapeKey" )
		def escapeKey( self, isDown ):
			if isDown:
				owner = self.owner
				owner.binocularsMode( 0 ) # escape out of binoculars gui mode
				owner.setUsingCurrentItem( 0 )
				return True
			else:
				return False

	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Overrides base-class data.
	#	- Sets all member data to sensible values.
	# --------------------------------------------------------------------------
	def __init__( self, itemType, prereqs = None ):
		Item.__init__( self, Gadget, itemType, prereqs )
		if self.itemType == Gadget.BINOCULARS:
			self.binocularsActionHandler = None

	# This dictionary maps an old item type to the new item class and class subtype
	typeDict = {
		Item.BINOCULARS_TYPE: BINOCULARS
	}

	# This method returns the basic prerequisites required for the item
	#@staticmethod
	def prerequisites( itemType ):
		return [Gadget.modelNames[Gadget.typeDict[itemType]]]

	prerequisites = staticmethod(prerequisites)

	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#	- Uses the gadget. This is an interface method defined by the Item
	#	  class.
	#	- Accepts a user (subject) and target (indirect object).
	# --------------------------------------------------------------------------
	def use( self, user, target ):
		handled = 0
		if not user.inCombat():
			if self.itemType == Gadget.BINOCULARS:
				# TBD: For now, this is being done for backwards compatibility
				# until Avatar is cleaned up.
				#if target == None:
				user.setUsingCurrentItem( 1 )
				handled = 1

		return handled


	# --------------------------------------------------------------------------
	# Method: enact
	# Description:
	#	- Acts out the use of the gun. This is an interface method defined by
	#	  the Item class.
	#	- Accepts a user (subject) and target (indirect object).
	# --------------------------------------------------------------------------
	def enact( self, user, target ):
		pass


	# Called by the player when it enters the 'using item' mode with this item
	def retain( self, owner ):
		if self.itemType == Gadget.BINOCULARS:
			owner.binocularsMode( 1 )
			self.binocularsActionHandler = Gadget.BinocularsActionHandler( owner )
			FantasyDemo.rds.keyBindings.addHandler( self.binocularsActionHandler )

	# Called by the player when it exits the 'using item' mode with this item
	def release( self, owner ):
		if self.itemType == Gadget.BINOCULARS:
			owner.binocularsMode( 0 )
			FantasyDemo.rds.keyBindings.removeHandler( self.binocularsActionHandler )
			self.binocularsActionHandler = None


	# --------------------------------------------------------------------------
	# Method: equipByPlayer
	# Description:
	#	- Sets the target capabilities and gui icon and other stuff
	#		which should be set when the player equips this item
	# --------------------------------------------------------------------------
	#def equipByPlayer( self, player ):
	#	print "Gadget.equipByPlayer", self, player
	#	Item.equipByPlayer( self, player )
