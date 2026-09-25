import BigWorld

import Pixie
import Keys
import Math
import GUI
import Bloom
from bwdebug import INFO_MSG
from Helpers import Caps
from functools import partial
from FDGUI import Minimap
import FantasyDemo

MODEL_NAME = "sets/dungeon/props/honourstone.model"

teleportGui = None
wasTargetingEnabled = False
teleportParticles = None

def finiTeleportGui():	
	global teleportGui
	if teleportGui != None:
		teleportGui.script.active(0)
		teleportGui = None


def teleportFinished():
	global teleportGui
	global wasTargetingEnabled
	global teleportParticles
	BigWorld.player().actionComplete()
	INFO_MSG( "Enabling World Drawing" )	
	BigWorld.player().model.root.detach( teleportParticles )
	FantasyDemo.enableWorldDrawing()
	BigWorld.target.isEnabled = wasTargetingEnabled
	teleportGui.script.active(0)
	teleportGui = None
	teleportParticles = None


#start Progress Check for the new space to load
def onChangeSpace( spaceID = -1, spaceSettings = None ):
	FantasyDemo.rds.delCameraSpaceChangeListener(onChangeSpace)
	global teleportGui	
	teleportGui.script.start(-1.0,teleportFinished)


def doTeleport( destination ):
	INFO_MSG( "Disabling World Drawing" )
	FantasyDemo.disableWorldDrawing()
	BigWorld.player().base.teleportTo( *destination )
	FantasyDemo.rds.addCameraSpaceChangeListener(onChangeSpace)


def blurScreen( destination ):
	global teleportGui
	global wasTargetingEnabled

	wasTargetingEnabled = BigWorld.target.isEnabled
	BigWorld.target.isEnabled = False
	BigWorld.target.clear()
	teleportGui = GUI.load( "gui/teleport_screen.gui" )
	teleportGui.script.active(1)		
	teleportGui.script.preTeleport(lambda:doTeleport(destination))


def teleportStep1( destination, particles ):
	global teleportParticles
	teleportParticles = particles	
	teleportParticles.clear()
	BigWorld.player().model.root.attach( teleportParticles )
	BigWorld.player().actionCommence()
	BigWorld.callback( 2.5, lambda:blurScreen(destination) )


def teleportTo( destination ):	
	global teleportParticles

	#don't let us teleport again while in mid-flight
	if teleportGui != None or teleportParticles != None:
		print "Already teleporting. Please wait"
		return

	if not teleportParticles:
		teleportParticles = Pixie.createBG("particles/teleport.xml", partial( teleportStep1, destination ) )
	else:
		teleportStep1( destination, teleportParticles )	

# ------------------------------------------------------------------------------
# Section: A class to allow testing of the teleport blur effect
# ------------------------------------------------------------------------------

class TestTeleportBlur:
	def __init__( self ):
		self.component = GUI.Gobo( "system/maps/col_white.dds" )
		self.component.size = (2,2)
		self.shader = GUI.AlphaShader()
		self.shader.alpha = 0
		self.shader.reset()

		self.component.addShader( self.shader )
		self.component.materialFX = "BLEND"

		Bloom.selectPreset("Gobo")
		GUI.addRoot( self.component )

	def setBlurAmount( self, amount):
		self.shader.speed = 0
		self.shader.alpha = amount

	def killTeleportBlur( self ):
		GUI.delRoot( self.component )

# ------------------------------------------------------------------------------
# Section: class Button
# ------------------------------------------------------------------------------

class Button( BigWorld.Entity ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def modelName( self ):
		# TODO: Use model type.
		return MODEL_NAME

	def prerequisites( self ):
		return [self.modelName()]

	def onEnterWorld( self, prereqs ):
		self.prereqs = prereqs
		self.set_modelType()
		Minimap.addEntity( self )

	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.model = None
		self.prereqs = None

	def set_modelType( self, oldType= None ):
		self.model = self.prereqs[ self.modelName() ]
		self.model.motors[0].entityCollision = 1
		self.model.motors[0].collisionRooted = 1
		self.targetCaps = [Caps.CAP_CAN_USE]

	# The player wants to use us
	def use( self ):
		# TODO: This is old and no longer used.
		teleportTo( *self.useData.rsplit( '/', -1 ) )

	def name( self ):
		return "Teleport to " + self.useData

# Button.py
