import BigWorld
import Pixie
import FX
import FDFX
from Helpers import Caps
from FDGUI import Minimap
import functools
import math
import random

import TriggeredDust

from GameData import BeastData

from Helpers.CallbackHelpers import *

# ------------------------------------------------------------------------------
# Section: class Beast
# ------------------------------------------------------------------------------

ENTITIES_IN_WORLD = set()

STOMP_SHAKE_ENERGY = 0.25

class Beast( BigWorld.Entity ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )


	def prerequisites( self ):
		result = []
		result.append( BeastData.MODEL_NAME )
		result.append( BeastData.EYE_PARTICLE_SYSTEM )
		result.append( BeastData.EYE_PARTICLE_SYSTEM )
		result.append( BeastData.SPIT_PARTICLE_SYSTEM )
		result.append( BeastData.SPIT_PARTICLE_SYSTEM )
		result.append( BeastData.SPLASH_MODEL_NAME )
		result.append( BeastData.SPLASH_MODEL_NAME )
		
		for actionName in BeastData.ACTION_EVENTS:
			( soundEvents, scriptEvents, effectEvents ) = BeastData.ACTION_EVENTS[ actionName ]
			for ( frame, effectName ) in effectEvents:
				result += FX.prerequisites( effectName )
		
		return result		
		

	def onEnterWorld( self, prereqs ):
		ENTITIES_IN_WORLD.add( self )			
				
		self.model = prereqs.pop(BeastData.MODEL_NAME)
		self.targetCaps = [ Caps.CAP_CAN_HIT, Caps.CAP_CAN_USE ]
		self.filter = BigWorld.DumbFilter()		
		self.tracker = BigWorld.Tracker()
		self.trackerNodeInfo = BigWorld.TrackerNodeInfo(self.model,
								'Base HumanHead',
								[],
								"None",
								-60.0, 60.0,
								-80.0, 80.0,
								60,
								180,
							        1.0)
		self.tracker.nodeInfo = self.trackerNodeInfo
		self.model.tracker = self.tracker
		self.tracker.directionProvider = None
		self.focalMatrix = self.model.node( "Base HumanHead" )
		self.model.visible = True
		self.model.visibleAttachments = True		
						
		for bone in ["HP_left_foot", "HP_right_foot"]:
			splashModel = prereqs.pop( BeastData.SPLASH_MODEL_NAME )
			splashModel.addMotor( BigWorld.Servo(self.model.node(bone)) )
			splashModel.visible = False
			self.addModel( splashModel )
		
		self.model.left_eye = prereqs.pop( BeastData.EYE_PARTICLE_SYSTEM )
		self.model.right_eye = prereqs.pop( BeastData.EYE_PARTICLE_SYSTEM )
		
		self.model.left_mouth = prereqs.pop( BeastData.SPIT_PARTICLE_SYSTEM )
		self.model.right_mouth = prereqs.pop( BeastData.SPIT_PARTICLE_SYSTEM )
		
		Minimap.addEntity( self )
		
		#Manage lifetime of remaining prereqs, the ACTION_EVENTS
		self.prereqs = prereqs


	def onLeaveWorld( self ):
		ENTITIES_IN_WORLD.remove( self )		
		
		Minimap.delEntity( self )
		self.model = None
		self.prereqs = None


	def use( self ):
		pass


	def name( self ):
		return 'The Beast'


	# --------------------------------------------------------------------------
	# Method: set_lookAtTarget
	# Description:
	#	- Accessor for the lookAtTarget property.
	#	- Called implicitly by the client when the server sends an update.
	#	- Should be called by the script when changing the lookAtTarget
	#	  variable.
	# --------------------------------------------------------------------------
	def set_lookAtTarget( self, oldID = None ):
		if self.model != None and self.tracker != None:
			target = BigWorld.entity( self.lookAtTarget )
			if target != None:
				hasFocalMatrices = hasattr(self, "focalMatrix") and hasattr(target, "focalMatrix")
				if hasFocalMatrices:
					self.tracker.directionProvider = BigWorld.DiffDirProvider( self.focalMatrix, target.focalMatrix )
			else:
				self.tracker.directionProvider = None


	def initiateRage( self ):
		try:
			if self.model.queue[0] != 'Rage' and self.model.queue[0] != 'Roar':
				actionName = random.choice( ['Rage', 'Roar',] )
				self.model.action( actionName )()
				self.queueActionEvents( actionName )
		except:
			pass
	
	
	def queueActionEvents( self, actionName ):
		if actionName in BeastData.ACTION_EVENTS:
			( soundEvents, scriptEvents, effectEvents ) = BeastData.ACTION_EVENTS[ actionName ]
			
			for ( frame, sound ) in soundEvents:
				BigWorld.callback( frame / 30.0, functools.partial( self.model.playSound, sound ) )

			for ( frame, functionName ) in scriptEvents:
				try:
					function = getattr( self, functionName )
					BigWorld.callback( frame / 30.0, function )
				except:
					print 'Unable to queue script action event for', functionName
			
			for ( frame, effectName ) in effectEvents:
				BigWorld.callback( frame / 30.0, functools.partial( self.playOneShotEffect, effectName ) )
		
	@IgnoreCallbackIfDestroyed
	def playOneShotEffect( self, effectName ):
		s = FX.OneShot( effectName )
		s.go( self.model )
				
	def onFootStomp( self ):
		if self.isDestroyed:
			return
		# TODO: Add cammera shake event to sfx system 
		# rather than calling it directly here
		FDFX.Events.Shockwave.shake( self.model, self.effectRadius, STOMP_SHAKE_ENERGY )
		
		for e in TriggeredDust.ENTITIES_IN_WORLD:
			if isinstance( e, TriggeredDust.TriggeredDust ):
				if (e.position - self.position).length < self.dustTriggerRadius:
					e.trigger()


# Beast.py
