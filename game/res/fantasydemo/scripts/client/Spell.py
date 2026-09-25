import FX
import BigWorld
from Math import Matrix
from Math import Vector3
from Helpers import projectiles
from functools import partial
import Creature
import Avatar
import traceback
from bwdebug import *
from Helpers import collide


# Helper function to return "None" if the required string doesn't exist in the
# data section.
def readStringOrNone( ds, tagName ):
	try:
		return ds[tagName].asString
	except KeyError:
		return None


#------------------------------------------------------------------------------
#	A CharacterItemEffectPlayer handles the playback of simulataneous actions
#	and FX on both a character entity and an item model.
#
#	You must call setupActions() before each call to play().
#	If you have more than one CIEP, call setupActions() on all of them.
#	Then you should call play() on the first, queue() on the first, and play()
#	on the second.
#
#	TODO : factor in timing of FX (currently ignores it)
#
#	player :	play playerAction, playerFX on it
#	item :		play itemAction, itemFX on it
#------------------------------------------------------------------------------
class CharacterItemEffectPlayer:

	def prerequisites( ds ):
		itemFXName = ds.readString( "itemFX" )
		playerFXName = ds.readString( "playerFX" )
		p = []
		if itemFXName != None:
			p += (FX.prerequisites(itemFXName))
		if playerFXName != None:
			p += (FX.prerequisites(playerFXName))
		return p

	prerequisites = staticmethod( prerequisites )

	def __init__( self, ds, prereqs ):
		self.setup = False
		self.playerAction = None
		self.playerActionContinuation = None
		self.itemAction = None
		self.itemActionContinuation = None
		self.playerActionName = ds.readString( "playerAction", "" )
		self.continuePlayerAction = ds.readBool( "playerAction/continues", False )
		self.itemActionName = ds.readString( "itemAction", "" )
		self.continueItemAction = ds.readBool( "itemAction/continues", False )
		self.itemFXName = ds.readString( "itemFX" )
		self.playerFXName = ds.readString( "playerFX" )
		self.totalDuration = 0.0
		self.prereqs = prereqs


	def setupActions( self, playerModel, itemModel ):
		self.setup = True

		if self.playerActionName != "":
			try:
				self.playerAction = getattr( playerModel, self.playerActionName )
			except AttributeError:
				WARNING_MSG( "playerActionName %s not found." % (self.playerActionName,) )
				self.playerAction = None
		else:
			self.playerAction = None

		if self.playerAction:
			self.playerActionDur = self.playerAction.duration
		else:
			self.playerActionDur = 0

		if self.itemActionName != "":
			try:
				self.itemAction = getattr( itemModel, self.itemActionName )
			except AttributeError:
				print "itemActionName %s not found." % (self.itemActionName,)
				self.itemAction = None
		else:
			self.itemAction = None

		if self.itemAction:
			self.itemActionDur = self.itemAction.duration
		else:
			self.itemActionDur = 0

		self.totalDuration = max( self.playerActionDur, self.itemActionDur )


	def freeActions( self ):
		self.setup = False
		self.playerAction = None
		self.playerActionContinuation = None
		self.itemAction = None
		self.itemActionContinuation = None


	def play( self, playerModel, itemModel, callbackFn ):
		if not self.setup:
			print "Please call setupActions first"
			return

		if (self.playerActionDur > self.itemActionDur):
			if self.playerAction:
				self.playerActionContinuation = self.playerAction()
			if self.itemAction:
				self.itemActionContinuation = self.itemAction( self.playerActionDur - self.itemActionDur )
		else:
			if self.itemAction:
				self.itemActionContinuation = self.itemAction()
			if self.playerAction:
				self.playerActionContinuation = self.playerAction( self.itemActionDur - self.playerActionDur )

		BigWorld.callback( self.totalDuration, self.freeActions )
		BigWorld.callback( self.totalDuration, callbackFn )

		if self.itemFXName != "":
			FX.bufferedOneShotEffect( self.itemFXName, itemModel, itemModel, None, self.totalDuration, self.prereqs )

		if self.playerFXName != "":
			FX.bufferedOneShotEffect( self.playerFXName, playerModel, playerModel, None, self.totalDuration, self.prereqs )


	#This method takes another CharacterItemEffectPlayer, and queues up its
	#actions so they seamlessly play after this one has finished. (no one
	#frame gap between playing, and no blend-in/out between the two)
	def queueActions( self, otherCIEP ):
		if not self.setup:
			print "Please call setupActions first"
			return

		if self.continuePlayerAction and self.playerActionContinuation:
			try:
				action = getattr( self.playerActionContinuation, otherCIEP.playerActionName )
				if action != None:
					otherCIEP.playerActionContinuation = action()
					otherCIEP.playerAction = None
			except AttributeError:
				pass

		if self.continueItemAction and self.itemActionContinuation:
			try:
				action = getattr( self.itemActionContinuation, otherCIEP.itemActionName )
				if action != None:
					otherCIEP.itemActionContinuation = action()
					otherCIEP.itemAction = None
			except AttributeError:
				pass


	def stop( self ):
		if self.itemAction:
			self.itemAction.stop()
		if self.playerAction:
			self.playerAction.stop()


	def duration( self ):
		if not self.setup:
			print "Please call setupActions first"

		return self.totalDuration



#------------------------------------------------------------------------------
#	A Spell handles the casting and delivering of a spell.  It may use an item
#	to launch itself from.
#
#	caster :	play playerAction
#	item :		play itemPowerup FX file
#	item :		play launch spell action
#	spell :		launch projectile of the given name
#------------------------------------------------------------------------------
class Spell:

	def prerequisites( ds ):
		p = []

		idleFXName = ds.readString( "Idle", "" )
		prepSection = ds["Prepare"]
		fireSection = ds["Fire"]

		isProjectile = False
		result = None
		if "Projectile" in ds.keys():
			result = ds["Projectile"]
			projectileFX = result.asString
			isProjectile = True
		else:
			result = ds["InstantHit"]
			instantHitFX = result.asString

		baseExplosion = result.readString( "baseExplosion", "" )
		personExplosion = result.readString( "personExplosion", "" )
		groundExplosion = result.readString( "groundExplosion", "" )
		airExplosion = result.readString( "airExplosion", "" )

		if idleFXName != "":
			p += FX.prerequisites(idleFXName)
		if prepSection != None:
			p += CharacterItemEffectPlayer.prerequisites( prepSection )
		if fireSection != None:
			p += CharacterItemEffectPlayer.prerequisites( fireSection )
		if isProjectile and projectileFX != "":
			p += FX.prerequisites(projectileFX)
		elif instantHitFX != "":
			p += FX.prerequisites(instantHitFX)
		if baseExplosion != "":
			p += FX.prerequisites(baseExplosion)
		if personExplosion != "":
			p += FX.prerequisites(personExplosion)
		if groundExplosion != "":
			p += FX.prerequisites(groundExplosion)
		if airExplosion != "":
			p += FX.prerequisites(airExplosion)

		return p

	prerequisites = staticmethod( prerequisites )

	def __init__( self, prereqs ):
		self.inUse = False
		self.isProjectile = False
		self.prereqs = prereqs
		if self.prereqs == None:
			WARNING_MSG( "Creating a Spell with no prerequisites, could be costly" )
			traceback.print_stack()


	def load( self, ds ):
		#Staff attaches this sfx on its own, we just create it.
		self.idleFXName = ds.readString( "Idle", "" )
		if self.idleFXName != "":
			self.idleFX = FX.Persistent( self.idleFXName, self.prereqs )
		else:
			self.idleFX = None

		self.prepActions = CharacterItemEffectPlayer( ds["Prepare"], self.prereqs )
		self.fireActions = CharacterItemEffectPlayer( ds["Fire"], self.prereqs )

		result = None
		if "Projectile" in ds.keys():
			result = ds["Projectile"]
			self.projectileFX = result.asString
			self.isProjectile = True
		else:
			result = ds["InstantHit"]
			self.instantHitFX = result.asString

		self.baseExplosion = readStringOrNone( result, "baseExplosion" )
		self.personExplosion = readStringOrNone( result, "personExplosion" )
		self.groundExplosion = readStringOrNone( result, "groundExplosion" )
		self.airExplosion = readStringOrNone( result, "airExplosion" )

		self.range = ds.readFloat( "range", 50.0 )
		self.explodeRadius = ds.readFloat( "explodeRadius", -1 )


	#------------------------------------------------------------------------------
	#	Launch the spell.  This method may come from the client or the server,
	#	depending on who the player parameter refers to.
	#
	#	This method performs preliminary spell cast animations etc, then calls
	#	the goBang() method to launch the actual spell.
	#
	#	player :	PlayerAvatar, or another Avatar
	#	item	:	Item object
	#	targetid :	If the spell it targetted, the ID of the entity
	#	hitLocation : If the spell was not targetted, the hit location
	#	materialKind : Again, untargetted, the material kind of the hit.
	#------------------------------------------------------------------------------
	def go( self, caster, targetid, item, hitLocation = None, materialKind = None ):
		if self.inUse:
			print "Please Wait"
			return False

		self.inUse = True
		self.hitLocation = hitLocation
		self.materialKind = materialKind
		self.targetid = targetid

		self.prepActions.setupActions( caster.model, item.model )
		self.fireActions.setupActions( caster.model, item.model )

		# If we're the caster, or if we are the target and the caster is not another player,
		# then do the initial calculations and send the to the server for propagation to other clients.
		if caster == BigWorld.player() or \
			( BigWorld.player() != None and targetid == BigWorld.player().id \
				and caster.__class__.__name__ != "Avatar" ):
			if targetid == 0:
				(self.hitLocation, self.materialKind) = self.getCollisionInformation( caster )
				tripTime = 0.0	#doesn't matter at the moment, not used for non-entity shots
			else:
				targetEntity = BigWorld.entity( self.targetid )
				self.hitLocation = Vector3( targetEntity.position )
				self.hitLocation[1] += 1
				self.materialKind = 0
				position = item.getLaunchSpellLocation()
				if self.isProjectile:
					tripTime = projectiles.fireballTripTime( caster, targetEntity.matrix, position - caster.position )
				else:
					tripTime = 0.0

			castTime = self.prepActions.duration()

			BigWorld.player().cell.castSpell( self.targetid, self.hitLocation, self.materialKind, castTime + tripTime, self.explodeRadius )

		# if caster is player then need to activate move action
		if hasattr( caster, "moveActionCommence" ):
			caster.moveActionCommence()

		self.prepActions.play( caster.model, item.model, partial(self.onFire, caster.id, item) )
		self.prepActions.queueActions( self.fireActions )


	#------------------------------------------------------------------------------
	#	Show the spell launch actions.
	#------------------------------------------------------------------------------
	def onFire( self, casterID, item ):
		caster = BigWorld.entity( casterID )
		if caster is not None and caster.inWorld:
			self.goBang( caster, item )
			self.fireActions.play( caster.model, item.model, partial(self.onFinishCast, casterID) )


	#------------------------------------------------------------------------------
	#	Actually launch the spell projectile.
	#------------------------------------------------------------------------------
	def goBang( self, caster, item ):
		if not caster.inWorld:
			return

		targetEntity = BigWorld.entity( self.targetid )
		position = item.getLaunchSpellLocation()
		targetMatrix = None
		if (targetEntity != None):
			targetMatrix = targetEntity.matrix
		else:
			targetMatrix = Matrix()
			targetMatrix.setTranslate(self.hitLocation)

		if targetEntity != None:
			if isinstance( targetEntity, Creature.Creature ):
				effect = FX.getBufferedOneShotEffect(targetEntity.hitFXName, prereqs = targetEntity.prereqs)
			else:
				effect = FX.getBufferedOneShotEffect(self.personExplosion, prereqs = self.prereqs)
		else:
			#ground or air burst
			if self.materialKind == 0:
				effect = FX.getBufferedOneShotEffect(self.airExplosion, prereqs = self.prereqs)
			else:
				effect = FX.getBufferedOneShotEffect(self.groundExplosion, prereqs = self.prereqs)

		targetHitCbk = partial(self.targetHitCallback, effect, self.targetid)

		if self.isProjectile:
			tripTime = projectiles.createFireball( self.projectileFX, self.baseExplosion, caster, targetMatrix, position - caster.position, targetHitCbk, self.prereqs )
		else:
			if targetEntity != None:
				FX.bufferedOneShotEffect( self.instantHitFX, item.model, targetEntity.model, prereqs = self.prereqs )
			else:
				m = BigWorld.Model("")
				caster.addModel(m)
				m.position = self.hitLocation
				FX.bufferedOneShotEffect( self.instantHitFX, item.model, m, partial( caster.delModel, m), prereqs = self.prereqs )
			targetHitCbk(caster.id, targetMatrix)


	#------------------------------------------------------------------------------
	#	Callback from projectile - it hit the target
	#
	#	sfx - target's explosion effect
	#	target - target entity
	#	owner - owner of the projectile
	#	targetMatrix - matrix of the projectile where it hit the target
	#------------------------------------------------------------------------------
	def targetHitCallback( self, sfx, targetID, ownerID, targetMatrix ):
		target = BigWorld.entity( targetID )
		# note: sfx may not exist if all buffered slots are used
		if sfx == None:
			return

		if target != None:
			sfx.go(target, target, None)
		else:
			owner = BigWorld.entity( ownerID )
			if owner is not None:
				explosion2 = BigWorld.Model("")
				owner.addModel(explosion2)
				explosion2.position = targetMatrix.applyToOrigin()
				sfx.go(explosion2, explosion2, partial(owner.delModel, explosion2))


	#------------------------------------------------------------------------------
	#	Finish up part 1, stop all actions and get them off the queue
	#------------------------------------------------------------------------------
	def onFinishCast( self, playerID ):
		#Temporary workaround - Stop action queue going nuts
		self.prepActions.stop()
		self.fireActions.stop()

		del self.targetid
		del self.hitLocation
		del self.materialKind

		BigWorld.callback( 0.01, partial(self.releaseSpell, playerID) )


	#------------------------------------------------------------------------------
	#	Finish up part 2, allow a new spell to be cast.
	#------------------------------------------------------------------------------
	def releaseSpell( self, playerID ):
		player = BigWorld.entity( playerID )
		if player is not None:
			player.actionComplete()
		self.inUse = False


	#------------------------------------------------------------------------------
	#	Get collision information based on the camera view angle.
	#
	#	Returns (position, materialKind) pair.  For now the material kind is
	#	a 1 or a 0, based on hitting some object, or nothing.
	#------------------------------------------------------------------------------
	def getCollisionInformation( self, player ):
		if player.inWoWMode:
			collisionType, target = player.getMouseCollidePos()
			if collisionType == collide.COLLIDE_OTHER:
				WARNING_MESSAGE( "Unexpected collision type" )
				return
			elif collisionType == collide.COLLIDE_ENTITY:
				lookAtPos = Vector3( target.position )
				lookAtPos[1] += 1
			elif collisionType == collide.COLLIDE_TERRAIN \
			or collisionType == collide.COLLIDE_NONE:
				lookAtPos = target
		else:
			# Find the position that the camera is looking at.
			m = Matrix( BigWorld.camera().invViewMatrix )
			forward = Vector3( m.applyToAxis(2) )
			cameraSrc = m.applyToOrigin() + forward.scale( BigWorld.projection().nearPlane * 1.01 )
			lookAtPos = Vector3( cameraSrc + forward.scale( 10000 ) )

			colres = BigWorld.collide( player.spaceID, cameraSrc, lookAtPos )
			if colres != None:
				(hitPt, (x,y,z), materialKind) = colres
				vectToHitPt = (hitPt - cameraSrc)
				lookAtPos = cameraSrc + vectToHitPt

		# Check for collisions between the source of the spell and the position the camera is looking at.
		# The source of the spell is the player's position plus 2 metres up.
		casterSrc = Vector3( player.position )
		casterSrc[1] += 2	# TODO: Use current position of the head of the staff for more precision.

		casterToTarget = lookAtPos - casterSrc
		if casterToTarget.length > self.range:
			casterToTarget.normalise()
			lookAtPos = casterSrc + casterToTarget * self.range

		colres = BigWorld.collide( player.spaceID, casterSrc, lookAtPos )
		if colres != None:
			(hitPt, (x,y,z), materialKind) = colres
			# Scale back the hit position slightly, so it's not on the geometry we collided with.
			# This helps prevent possible unwanted collisions later.
			vectToHitPt = (hitPt - casterSrc)
			hitPt = casterSrc + vectToHitPt
			return (hitPt, 1)
		else:
			return (lookAtPos, 0)
