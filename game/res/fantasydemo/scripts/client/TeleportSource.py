import BigWorld
import Pixie
import Keys
import Math
import GUI
import Bloom
import FantasyDemo as FantasyDemo
from bwdebug import INFO_MSG
from Helpers import Caps
from functools import partial

# ------------------------------------------------------------------------------
# Section: Teleportation Methods
# ------------------------------------------------------------------------------

teleportGui = None
wasTargetingEnabled = False
teleportParticles = None

teleportXML = "particles/teleport.xml"
teleportScreen = "gui/teleport_screen.gui"


def startTeleportation( *dst ):	
	global teleportParticles

	#don't let us teleport again while in mid-flight
	if teleportGui != None or teleportParticles != None:
		FantasyDemo.addChatMsg( -1, "Already teleporting please wait" )
		return

	if not teleportParticles:
		teleportParticles = Pixie.createBG("particles/teleport.xml", partial( attachTeleportParticles, dst ) )
	else:
		attachTeleportParticles( dst, teleportParticles )	


def attachTeleportParticles( dst, particles ):
	global teleportParticles
	teleportParticles = particles
	teleportParticles.clear()
	BigWorld.player().model.root.attach( teleportParticles )
	BigWorld.player().actionCommence()
	# let teleport particles animation play a while before blurring screen
	BigWorld.callback( 2.5, lambda:blurScreen( dst ) )


def blurScreen( dst ):
	global teleportGui
	global wasTargetingEnabled

	wasTargetingEnabled = BigWorld.target.isEnabled
	BigWorld.target.isEnabled = False
	BigWorld.target.clear()

	# create teleport gui screen
	BigWorld.worldDrawEnabled(False)
	teleportGui = GUI.load( teleportScreen )
	BigWorld.worldDrawEnabled(True)
	teleportGui.script.active(1)		
	teleportGui.script.preTeleport( lambda:teleportPlayer( dst ) )


def teleportingToDifferentSpace( dstSpaceName ):
	try:
		spaceName = FantasyDemo.rds.spaceNameMap[BigWorld.player().spaceID]
		return spaceName != dstSpaceName
	except:
		pass
	return True


def teleportPlayer( dst ):
	INFO_MSG( "Disabling World Drawing" )
	#BigWorld.worldDrawEnabled(False)
	FantasyDemo.disableWorldDrawing()
	BigWorld.player().base.teleportTo( *dst )
	if teleportingToDifferentSpace( dst[0] ):
		FantasyDemo.addCameraSpaceChangeListener(onChangeSpace)
	else:
		BigWorld.callback( 2.5, partial( teleportGui.script.start, -1.0, endTeleportation ) )


#start Progress Check for the new space to load
def onChangeSpace( spaceID = -1, spaceSettings = None ):
	FantasyDemo.delCameraSpaceChangeListener(onChangeSpace)
	if teleportGui is not None:
		teleportGui.script.start( -1.0, endTeleportation)


def endTeleportation( didNotCompletelyLoadSpace = False ):
	global teleportGui
	global teleportParticles

	INFO_MSG( "Enabling World Drawing" )	
	#BigWorld.worldDrawEnabled(True)
	FantasyDemo.enableWorldDrawing()

	BigWorld.player().actionComplete()
	BigWorld.player().model.root.detach( teleportParticles )

	BigWorld.target.isEnabled = wasTargetingEnabled
	teleportGui.script.postTeleport()
	teleportGui.script.active(0)
	teleportGui = None
	teleportParticles = None


def cleanupTeleportGUI():	
	global teleportGui
	if teleportGui != None:
		teleportGui.script.active(0)
		teleportGui = None


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
# Section: class TeleportSource
# ------------------------------------------------------------------------------

MODEL_NAME = "sets/dungeon/props/honourstone.model" 

class TeleportSource( BigWorld.Entity ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def modelName( self ):
		# TODO: Use model type.
		return MODEL_NAME

	def prerequisites( self ):
		return [ self.modelName() ]

	def onEnterWorld( self, prereqs ):
		self.prereqs = prereqs
		self.set_modelType()

	def onLeaveWorld( self ):
		self.model = None
		self.prereqs = None

	def set_modelType( self, oldType= None ):
		self.model = self.prereqs[ self.modelName() ]
		self.model.motors[0].entityCollision = 1
		self.model.motors[0].collisionRooted = 1
		self.targetCaps = [ Caps.CAP_CAN_USE ]

	# Player wants to use Teleport Source
	def use( self ):
		BigWorld.player().tryToTeleport( self.spaceLabel, self.destination )

	def name( self ):
		return "Teleport to %s in %s" % (self.destination, self.spaceLabel)

# TeleportSource.py
