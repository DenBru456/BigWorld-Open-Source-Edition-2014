import BigWorld
import GUI

import Helpers.PyGUI as PyGUI

from functools import partial

FADE_SPEED = 2.0
HEALTH_SPEED = 0.5

class CharStats( PyGUI.Window ):

	factoryString = "FDGUI.CharStats"

	def __init__( self, component ):
		PyGUI.Window.__init__( self, component )
		self.component.script = self
		self.inCombatMode = False

		
	def onBound( self ):
		PyGUI.Window.onBound( self )
	
		
	def avatarInit( self, avatar ):
		#print "CharStats.avatarInit", avatar
		avatar.addListener( "healthUpdated", self.healthUpdated )
		
		avatar.addListener( "combatStanceUpdated", self.combatModeChanged )
		avatar.addListener( "enterCloseCombatMode", partial( self.combatModeChanged, True ) )
		avatar.addListener( "leaveCloseCombatMode", partial( self.combatModeChanged, False ) )
		
		self.component.characterName.text = avatar.name()
	
	
	def avatarFini( self, avatar ):
		pass


	def healthUpdated( self, newHealthPct, oldHealthPct ):
		#print "CharStats.healthUpdated", newHealthPct, oldHealthPct
		if oldHealthPct is None:
			# First update, force to the new health without animating.
			self.component.healthBar.clipper.speed = 0
			self.component.healthBar.colourer.speed = 0
		else:
			self.component.healthBar.clipper.speed = HEALTH_SPEED
			self.component.healthBar.colourer.speed = HEALTH_SPEED
	
		self.component.healthBar.clipper.value = newHealthPct
		self.component.healthBar.colourer.value = newHealthPct
		
		self.component.fader.speed = 0
		self.component.fader.value = 1		
		BigWorld.callback( 0.001, self.fade )


	def combatModeChanged( self, inMode ):	
		#print "CharStats.combatModeChanged", inMode
		self.inCombatMode = inMode
		if inMode:
			self.component.fader.speed = 0
			self.component.fader.value = 1
		else:
			self.fade()


	def fade( self ):
		#print "CharStats.fade", self.inCombatMode
		# Only start fading if we're not in combat mode.
		if not self.inCombatMode:
			self.component.fader.speed = FADE_SPEED
			self.component.fader.value = 0
