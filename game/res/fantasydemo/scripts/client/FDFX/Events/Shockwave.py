from FX.Event import Event
from FX import s_sectionProcessors
import Pixie
import BigWorld
import PostProcessing
from Math import Vector3
from Math import Vector4
from Math import Vector4Animation
from bwdebug import *
from FX.Event import TRANSFORM_DEPENDENT_EVENT


def shake( targetModel, maxDist = 100, energy = 0.1 ):
	'''
	This method shakes the camera (and rumbles the joypad) based on distance
	to the player
	'''
	position = BigWorld.camera().position
	if BigWorld.player():
		position = BigWorld.player().position
	dist = Vector3(targetModel.position - position).length

	if dist < maxDist:
		normDist = dist / maxDist
		try:
			BigWorld.rumble((maxDist - dist) / maxDist, 0.0)
			BigWorld.callback( 0.1, lambda: BigWorld.rumble(0, 0 ) )
		except:
			#running the pc client
			pass
		shDist = energy - (normDist*energy)
		try:
			#need a try/except because you can't shake a free camera ( ... why not? )
			BigWorld.camera().shake( 1.0-normDist, (shDist,shDist,shDist/2) )
		except:
			pass


#-------------------------------------------------------------------------
# The ShockWaveEvent is an event that you can play on a shockwave model.
#-------------------------------------------------------------------------
class ShockWaveEvent( Event ):
	def __init__( self ):
		self.victimList = {}
		self.fader = Vector4Animation()
		pass


	def load( self, pSection, prereqs = None ):
		self.colour = pSection.readVector4( "colour", (0.0364,0.0632,0.094,1.0) )
		self.actionName = pSection.readString( "actionName" )
		self.shimmerStyle = pSection.readInt( "shimmerStyle", 1 )
		self.soundTag = pSection.readString( "hitCameraSound", "" )
		return self


	def go( self, effect, actor, source, target, **kargs ):
		if kargs.has_key( "victims" ):
			self.processVictims(actor,kargs["victims"])
		self.model = actor
		go = actor.action( self.actionName )
		try:
			go()
		except EnvironmentError:
			pass
		BigWorld.callback( go.duration, self.finishUp )
		self.effect = effect

		actor.Material = "Fader"
		self.fader.keyframes=[(0,self.colour), (go.duration,Vector4(0,0,0,0)), (go.duration+1.0,Vector4(0,0,0,0))]
		self.fader.duration = go.duration + 1.0
		self.fader.time = 0.0
		actor.Material.colour = self.fader

		#TODO : need to handle the case when multiple things try to set the shimmer style.
		try:	BigWorld.setShimmerStyle(self.shimmerStyle)
		except:	pass

		self.matID = BigWorld.addMat(actor.node("plasmaexplosion"),self.shockHitCamera)
		return go.duration


	def duration( self, actor, source, target ):
		go = actor.action( self.actionName )
		return go.duration


	def finishUp( self ):
		try:	BigWorld.setShimmerStyle(0)
		except:	pass
		if hasattr( self, "matID" ):
			BigWorld.delMat( self.matID )
			del self.matID
		for (matID,entry) in self.victimList.items():
			BigWorld.delMat( matID )
			entID = entry[0]
			wasHit = entry[1]
			if not wasHit:
				ent = BigWorld.entity(entID)
				if ent:
					try:	imfn = ent.shockImpact
					except:	pass
					else:	imfn( 0, self.model.position )
		self.model = None
		self.effect = None
		PostProcessing.setShimmerAlpha( None )

	def processVictims( self, actor, victims ):
		for id in victims:
			ent = BigWorld.entity(id)
			if ent and ent.model:
				matID = BigWorld.addMat(actor.node("plasmaexplosion"),self.shockHitEntity,ent.model.matrix)
				self.victimList[matID] = [id,0]
				try:	warnfn = ent.shockWarning
				except:	pass
				else:	warnfn( 0 )


	def shockHitEntity( self, enter, matID ):
		#DEBUG_MSG(enter, matID )
		if self.victimList[matID][1] == 0:
			id = self.victimList[matID][0]
			ent = BigWorld.entity(id)
			if ent:
					try:	imfn = ent.shockImpact
					except:	pass
					else:	imfn( 0, self.model.position )
			self.victimList[matID] = [id,1]


	def shockHitCamera( self, enter, matID ):
		if enter:
			shake( self.model )

			# Sound-related calls disabled because soundbank is missing required
			# sound events.  Also note that the new sound API provides a much
			# easier way to have sounds continue playing after the model is
			# destroyed.  See PyModel.stopSoundsOnDestroy for more info.

# 			if self.soundTag != "":
# 				s = self.model.playSound( self.soundTag )
# 				self.effect.extendTime( self, s.duration )

			PostProcessing.setShimmerAlpha( self.fader )
		else:
			PostProcessing.setShimmerAlpha( None )


	def dependsOnCorrectTransform( self ):
		return TRANSFORM_DEPENDENT_EVENT


s_sectionProcessors[ "ShockWave" ] = ShockWaveEvent
