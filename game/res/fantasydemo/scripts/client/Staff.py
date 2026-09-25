from Item import Item
import Math
import BigWorld
import Spell
import ResMgr
import FantasyDemo
import traceback

# ------------------------------------------------------------------------------
# Class Staff:
#
# The Staff class is a derived class representing staffs in the game. The Staff
# class extends the use() and enact() methods for the Item class.
# ------------------------------------------------------------------------------

class Staff(Item):

	# --------------------------------------------------------------------------
	# The different types of staffs are listed below. The value of ALLOWED_TYPE
	# should always be set to the highest value that the itemType can take.
	# --------------------------------------------------------------------------
	typeRange = xrange(0,9)
	SNAKE				= 2
	LIGHTNING			= 3

	# staff can shoot
	canShoot = 1


	# --------------------------------------------------------------------------
	# The dictionary of staff models is listed below. A model name is the name of
	# the file containing model information for drawing and animating the staff
	# in the game world.
	# --------------------------------------------------------------------------
	modelNames = {
		SNAKE:			"sets/items/staff.model",
		LIGHTNING:		"sets/items/staff.model",
	}


	# --------------------------------------------------------------------------
	# Staffs have an associated Spell.
	# --------------------------------------------------------------------------
	spell = {
		SNAKE:			"scripts/data/spells.xml/Fireball",
		LIGHTNING:		"scripts/data/spells.xml/Lightning",
	}


	# --------------------------------------------------------------------------
	# Some staffs eject stuff when they launch spells.  Here is where they eject
	# them from.
	# --------------------------------------------------------------------------
	launchSpellNode = {
		SNAKE:			"HP_Snake_Mouth",
		LIGHTNING:		"HP_Snake_Mouth",
	}


	# --------------------------------------------------------------------------
	# The dictionary of staff names is listed below. A display name is the
	# default text displayed to the client when targeting the staff.
	# --------------------------------------------------------------------------
	displayNames = {
		SNAKE:			"Serpent Staff",
		LIGHTNING:		"Lightning Staff",
	}


	# --------------------------------------------------------------------------
	# The dictionary of staff icons is listed below. A GUI icon name is the file
	# containing the bitmap for the staff when selected in the GUI.
	# --------------------------------------------------------------------------
	guiIconNames = {
		SNAKE:			"gui/maps/icon_items/icon_staff.tga",
		LIGHTNING:		"gui/maps/icon_items/icon_staff_lightning.tga",
	}


	# --------------------------------------------------------------------------
	# Staffs have a set of properties which are fairly static. That is, they are
	# invariable across the type of staff. These are stored in the dictionary
	# below. The value of the dictionary is the tuple: (Range, Damage).
	# --------------------------------------------------------------------------
	staticProperties = {
		SNAKE:			( 35,  50 ),
		LIGHTNING:		( 35,  50 ),
	}


	# This method returns the basic prerequisites required for the item
	def prerequisites( itemType ):
		ds = ResMgr.openSection(Staff.spell[itemType])
		prereq = [Staff.modelNames[itemType],Staff.spell[itemType]]
		prereq += Spell.Spell.prerequisites( ds )
		return prereq

	prerequisites = staticmethod(prerequisites)


	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Overrides base-class data.
	#	- Sets all member data to sensible values.
	# --------------------------------------------------------------------------
	def __init__( self, itemType, prereqs ):
		Item.__init__( self, Staff, itemType, prereqs )

		#Resource name of Spell file to load
		self.spell = Spell.Spell( prereqs )

		try:
			ds = prereqs[Staff.spell[self.itemType]]
		except KeyError:
			ds = ResMgr.openSection(Staff.spell[self.itemType])
			print "Staff data failed to load from prerquisites : ", Staff.spell[self.itemType]
		except TypeError:
			ds = ResMgr.openSection(Staff.spell[self.itemType])
			print "Warning - creating staff from no prerequisites could be costly"
			traceback.print_stack()

		self.spell.load( ds )

		#The node from which any projectiles or flares are produced
		self.launchSpellNode = None

		if Staff.launchSpellNode[ self.itemType ] != None:
			self.launchSpellNode = self.model.node( Staff.launchSpellNode[ self.itemType ] )

		( rng, dmg ) = Staff.staticProperties[ self.itemType ]

		self.staffRange = rng
		self.staffDamage = dmg


	def getLaunchSpellLocation( self ):
		if self.launchSpellNode != None:
			m = Math.Matrix( self.launchSpellNode )
			#print m.applyToOrigin()
			return m.applyToOrigin()
		else:
			#print "root " + self.model.position
			return self.model.position



	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#	- Uses the staff. This is an interface method defined by the Item class.
	#	- Accepts a user (subject) and target (indirect object).
	#	- User should only be the PlayerAvatar.
	# --------------------------------------------------------------------------
	def use( self, player, target ):
		handled = 0

		if not player.inCombat():
			print "Error: player should already be in combat mode while holding a staff"
		else:
			handled = 1

			if target:
				tid = target.id
				vectorTo = Math.Vector3(target.position) - Math.Vector3(player.position)
				if vectorTo.length >= self.staffRange:
					tid = 0
			else:
				tid = 0

			player.castSpell( tid, None, None )

		return handled


	# --------------------------------------------------------------------------
	# Method: enactDrawn
	# Description:
	#	- Start the idle FX going.
	# --------------------------------------------------------------------------
	def enactIdle( self, entity = None ):
		Item.enactIdle( self, entity )
		if self.spell.idleFX != None:
			self.spell.idleFX.attach( self.model )
			self.spell.idleFX.go( target = entity )
		if entity != None:
			caps = entity.am.matchCaps
			if 0 not in caps:
				caps.append( 0 )
			entity.am.matchCaps = caps


	# --------------------------------------------------------------------------
	# Method: equipByPlayer
	# Description:
	#	- Move camera slightly to the right
	# --------------------------------------------------------------------------
	def equipByPlayer( self, player ):
		Item.equipByPlayer( self, player )
		FantasyDemo.setCursorCameraPivot( 0.15, 1.8, 0.0 )


	# --------------------------------------------------------------------------
	# Method: unequip
	# Description:
	#	- Stop the Idle FX
	#	- Reset the camera (player only)
	# --------------------------------------------------------------------------
	def unequip( self, entity ):
		Item.unequip( self, entity )
		if entity != None:
			caps = entity.am.matchCaps
			if 0 in caps:
				caps.remove( 0 )
			entity.am.matchCaps = caps
		if self.spell.idleFX != None and self.spell.idleFX.source != None:
			self.spell.idleFX.detach()
		if entity == BigWorld.player():
			FantasyDemo.setCursorCameraPivot( 0.0, 1.8, 0.0 )


	# --------------------------------------------------------------------------
	# Method: setHoldingStyle
	# Description:
	#	- Sets the action matcher capabilities for a particular item. This
	#	  allows an Item to specify what type of idle is used when it is
	#	  equiped.
	# --------------------------------------------------------------------------
	def setHoldingStyle( self, entity ):
		entity.model.HoldUpright()
