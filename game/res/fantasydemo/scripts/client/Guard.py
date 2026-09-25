import math
import BigWorld
import particles
from Math import *
from Helpers import Caps
from GameData import GuardData
from Avatar import Avatar
import AvatarMode as Mode
import AvatarModel
from bwdebug import *


def validatePackedAvatarModel( avatarModel ):
	try:
		modelIndices = avatarModel["models"]
	except AttributeError:
		return False
	
	return len(modelIndices) > 0 and modelIndices != [0]

# ------------------------------------------------------------------------------
# Section: class Guard
# ------------------------------------------------------------------------------


class Guard(Avatar):

	VISIBLE_RANGE = 30

	def __init__( self ):

		# You should pass Guard an avatarModel dictionary when you make it
		# LightGuard uses this to initialise avatarModel
		# Guard seems to only use it for some comparisons in cell.Guard
		# Guard uses guardType for selecting a model
		self.modelNumber = 0

		if (not hasattr( self, "avatarModel" ) or
			not validatePackedAvatarModel( self.avatarModel )):
			ERROR_MSG( "Guard %d created with no model" % (self.id,) )
		
		Avatar.__init__( self )

		# guard stuff
		self.am.collisionRooted = 1
		self.am.footTwistSpeed = 0
		self.canSeePlayer_ = 0
		self.targettingColour = (255,64,64,255)
		self.minimapColour = self.targettingColour


	def prerequisites( self ):
		list = []
		list.append( "scripts/data/guard.xml" )
		return list


	def onEnterWorld( self, prereqs ):
		Avatar.onEnterWorld( self, prereqs )
		if self.mode != Mode.DEAD:
			self.targetCaps = [ Caps.CAP_CAN_HIT , Caps.CAP_CAN_USE ]
		self.filter = BigWorld.AvatarDropFilter()
		self.am.entityCollision = False
		self.am.collisionRooted = False

	def onLeaveWorld( self ):
		Avatar.onLeaveWorld(self)
		self.targetCaps = [ Caps.CAP_NEVER ]


	def setDeadFilter( self ):
		Avatar.setDeadFilter( self )


	# Workaround for Bug 10961 - Send teleport message to client when teleporting
	def resetFilter( self ):
		self.filter = BigWorld.AvatarDropFilter()


	def enterDeadMode( self ):
		if self.worldTransition:
			# we are entering the world as dead, so don't animate
			Avatar.setDeadState( self, dyingAnimation = 0 )
		else:
			Avatar.setDeadState( self )
		self.targetCaps = [ Caps.CAP_NEVER ]


	def leaveDeadMode( self ):
		Avatar.unsetDeadState( self )
		self.filter = BigWorld.AvatarDropFilter()
		self.targetCaps = [ Caps.CAP_CAN_HIT , Caps.CAP_CAN_USE ]


	def fragged( self, shooterID ):
		Avatar.fragged( self, shooterID )


	def scanForTargets( self, amplitude, period, offset ):
		self.enableTracker( self.headNodeInfo )
		if amplitude == 0.0:
			self.tracker.directionProvider = None
		else:
			self.tracker.directionProvider = BigWorld.ScanDirProvider(amplitude, period, offset)


	def trackTarget( self, targetID ):
		self.tracker.directionProvider = BigWorld.DiffDirProvider(
					self.focalMatrix, BigWorld.entity( targetID ).focalMatrix )


	def use( self ):
		if self.ownerId != BigWorld.player().id:
			gesture = 18 # BeckonTaunt
			user = BigWorld.player()
			user.didGesture( gesture )
			user.cell.didGesture( gesture )
			user.actionCommence()
			self.cell.startFollow()
		else:
			gesture = 0 # Shooaway
			user = BigWorld.player()
			user.didGesture( gesture )
			user.cell.didGesture( gesture )
			user.actionCommence()
			self.cell.stopFollow()


	def set_avatarModel( self, oldValue = None ):
		def onModelChanged():
			self.set_modelScale()

		Avatar.set_avatarModel( self, oldValue, onModelChanged )


	def set_modelScale( self, oldScale = None ):
		try:
			self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )
		except:
			pass


	def setTargetCaps( self ):
		self.targetCaps = [Caps.CAP_CAN_USE, Caps.CAP_CAN_HIT]




#Guard.py



