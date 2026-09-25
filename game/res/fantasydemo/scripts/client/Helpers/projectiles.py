"""This module handles different projectiles."""

import BigWorld
import PSFX
import particles
import Pixie
import math
from functools import partial
from Math import Vector3
from Keys import *
from Math import MatrixProduct
from Math import Matrix
#from Helpers.shieldFX import instance as ShieldFX
import FX


def _safeDelModel( ownerID, model ):
	owner = BigWorld.entity( ownerID )
	if owner is not None:
		owner.delModel( model )

def preload( list ):
	list += [ "objects/models/fx/03_pchangs/shockwave.model" ]
	
	
def calculateTripTime( sourcePosition, targetPosition, speed ):

	# calculate the trip time based on the displacement
	disp = sourcePosition -	targetPosition		
	sx = math.sqrt(disp.x*disp.x + disp.z*disp.z)
	sy = disp.y
	ay = -9.8
	U = speed
	intercept = U*U*U*U - 2*U*U*sy*ay - ay*ay*sx*sx

	# if we can't make it, return now
	if intercept < 0:		
		return 0

	tsq = (2.0/(ay*ay)) * (sy*ay - U*U + math.sqrt(intercept))
	t = math.sqrt(abs(tsq))
	
	return t


def create( name, owner, target, projectile, colour = (1.0,1.0,1.0), location = None ):
	if fxMap.has_key( name ):
		(trail,explosion,project,tracer) = fxMap[name]
		if project:
			shootProjectile( owner, target, projectile, trail, partial(explosion,owner.id,True) )
		elif explosion:
			if target:
				explosion( owner, target.model, 0 )
			else:
				m = BigWorld.Model( "" )
				owner.addModel( m )
				m.position = location
				explosion( owner, m, 1 )

		#if tracer:
		#	BigWorld.tracerFire( ShieldFX.firingLocns( owner ), target.id, colour )
	else:
		pass
		#BigWorld.tracerFire( ShieldFX.firingLocns( owner ), target.id, colour )
		
projectileSpeed = 12.0


def destroyFireball( ownerID, fireball, fx, explosionFXName, targetHitCallback, prereqs ):
	m = Matrix( fireball.motors[0].target )
	fx.detach()
	owner = BigWorld.entity( ownerID )
	if owner is not None:
		owner.delModel( fireball )
	
	#Spawn explosion(s)
	explosion = BigWorld.Model( "" )
	if owner is not None:
		owner.addModel( explosion )
	explosion.position = m.applyToOrigin()
	fireballfx = FX.bufferedOneShotEffect( explosionFXName, explosion, explosion, lambda:_safeDelModel( ownerID, explosion ), 10.0, prereqs )
	
	#target hit
	if targetHitCallback != None:
		targetHitCallback( ownerID, m )
			
			
def fireballTripTime( source, target, srcoff = Vector3(0,1.5,0), dstoff = Vector3(0,1.2,0) ):
	global projectileSpeed
	if hasattr(target, "matrix"):
		targetMatrix = target.matrix
	else:
		targetMatrix = target
	sourcePosition = Vector3(source.position) + srcoff
	targetPosition = Vector3(Matrix(targetMatrix).applyToOrigin())+dstoff
	speed = projectileSpeed
	
	tripTime = calculateTripTime( sourcePosition, targetPosition, speed )
	if tripTime == 0:
		speed = speed * 2.0
		tripTime = calculateTripTime( sourcePosition, targetPosition, speed )
	if tripTime == 0:
		speed = speed * 2.0
		tripTime = calculateTripTime( sourcePosition, targetPosition, speed )
	if tripTime == 0:
		speed = speed * 2.0
		tripTime = calculateTripTime( sourcePosition, targetPosition, speed )
	if tripTime == 0:
		speed = speed * 2.0
		tripTime = calculateTripTime( sourcePosition, targetPosition, speed )
	if tripTime == 0:
		print "No speed solution for fireball"
		return 0
			
	return tripTime
	
		
def createFireball( projectileFXName, explosionFXName, source, target, srcOffset = None, targetHitCallback = None, prereqs = None ):
	fireball = BigWorld.Model("")	
	fx = FX.Persistent(projectileFXName,prereqs)
	fx.attach(fireball)
	callback = partial( destroyFireball, source.id, fireball, fx, explosionFXName, targetHitCallback, prereqs )
	global projectileSpeed
	
	tripTime = shootProjectile( source.id, target, fireball, None, callback, srcOffset )
	if tripTime == 0:
		projectileSpeed = projectileSpeed * 2.0
		tripTime = shootProjectile( source.id, target, fireball, None, callback, srcOffset )
	if tripTime == 0:
		projectileSpeed = projectileSpeed * 2.0
		tripTime = shootProjectile( source.id, target, fireball, None, callback, srcOffset )		
	if tripTime == 0:
		projectileSpeed = projectileSpeed * 2.0
		tripTime = shootProjectile( source.id, target, fireball, None, callback, srcOffset )
	if tripTime == 0:
		projectileSpeed = projectileSpeed * 2.0
		tripTime = shootProjectile( source.id, target, fireball, None, callback, srcOffset )
	if tripTime == 0:		
		fx.detach(fireball)
		print "No speed solution for fireball"
		
	projectileSpeed = 12.0
	return tripTime	


# Shoot the target with a projectile
def shootProjectile( ownerID,
						target,
						projectile,
						trail = None,
						boom = None,
						srcoff = Vector3(0,1.5,0),
						dstoff = Vector3(0,1.2,0),
						motor = None
					):

	owner = BigWorld.entity( ownerID )
	if hasattr(target, "matrix"):
		targetMatrix = target.matrix
	else:
		targetMatrix = target

	# general settings
	if not boom and dstoff: dstoff.y=1.8
	if not dstoff: dstoff = Vector3(0, 0, 0)

	if owner is not None:
		owner.addModel( projectile )
		projectile.position = Vector3(owner.position) + srcoff
	else:
		projectile.position = srcoff

	if not motor:
		motor = BigWorld.Homer()
		global projectileSpeed
		motor.speed = projectileSpeed
		motor.turnRate = 10
	if dstoff.lengthSquared == 0:
		motor.target = targetMatrix
	else:
		motor.target = MatrixProduct()
		motor.target.a = targetMatrix
		motor.target.b = Matrix()
		motor.target.b.setTranslate( dstoff )

	if motor.tripTime <= 0.0:
		if owner is not None:
			sourcePosition = Vector3(owner.position) + srcoff
		else:
			sourcePosition = srcoff
		targetPosition = Vector3(Matrix(targetMatrix).applyToOrigin())+dstoff
		speed = motor.speed
		
		t = calculateTripTime( sourcePosition, targetPosition, speed  )
		if t == 0:
			#We can't make it.  return now.
			if owner is not None:
				owner.delModel( projectile )
			return 0			
		motor.tripTime = t

		# rotate arrow to point in direction of initial velocity
		#ux = sx/t
		#uy = sy/t - 0.5*ay*t
		#print "ux is ", ux, " uy is ", uy
		#projectile.rotate( math.atan2(uy,ux), (1,0,0) )
		#projectile.yaw = math.atan2(disp.x,disp.z) + math.pi/2

	# and whack on the motor
	projectile.addMotor( motor )

	# and whack on any trail FX
	if trail:
		trail( projectile, None, motor.tripTime )

	# call us back when you get close enough
	motor.proximity = 1.0
	if boom:
		motor.proximityCallback = boom
	else:
		motor.proximityCallback = partial( _safeDelModel, ownerID, projectile )
		
	return motor.tripTime


# Convential trail - thin white line
def standardTrail( projectile, node, tripTime ):
	PSFX.attachFlareTrace( projectile, node, tripTime )


# Smoke trail - thin white line + smoke output
def smokeTrail( projectile, node, tripTime ):
	PSFX.attachFlareTrace( projectile, node, tripTime )
	PSFX.attachSmokeTrail( projectile, node )


# Conventional explosion for the specified projectile
def standardExplosion( ownerID, model, delModel ):
	PSFX.attachExplosion( model )
	if delModel:
		BigWorld.callback( 0.5, partial( _safeDelModel, ownerID, model ) )

	#note - PSFX attach methods perform auto-cleanup on the particle system,
	#so if clearModel is not set, it's ok to just do nothing.


# Electromagnetic explosion for the specified projectile
def empExplosion( ownerID, model, delModel ):
	#todo : differentiate this
	PSFX.attachExplosion( model )
	if delModel:
		BigWorld.callback( 0.5, partial( _safeDelModel, ownerID, model ) )


# Shakes the world based on distance to player
def shake( targetModel ):
	dist = Vector3(targetModel.position - BigWorld.player().position).length

	if dist < 100:
		BigWorld.player()
		try:
			BigWorld.rumble(100 - dist, 0)
			BigWorld.callback( 0.1, partial( BigWorld.rumble, 0, 0 ) )
		except:
			#running the pc client
			pass
		shDist = 0.25 - (dist/250)
		try:
			#need a try/except because you can't shake a free camera ( ... why not? )
			BigWorld.camera().shake( 0.1, (shDist,shDist,shDist/2) )
		except:
			pass

def plasmaImplode( duration, targetModel ):
	# Sound calls disabled because sound events are missing from soundbank.
	# targetModel.playSound( "plasma/implode" )
	warpEffect = PSFX.beginPlasmaWarp( targetModel )
	BigWorld.callback( duration, partial( PSFX.endPlasmaWarp, warpEffect ) )

def plasmaExplode( ownerID, targetModel, delTargetModel ):
	owner = BigWorld.entity( ownerID )
	if owner is None:
		return

	# Sound calls disabled because sound events are missing from soundbank.
	# targetModel.playSound( "plasma/explode" )
	m = BigWorld.Model("objects/models/fx/03_pchangs/shockwave.model")
	targetModel.root.attach(m)
	m.Go()
	BigWorld.callback( 1.0, partial( targetModel.root.detach, m ) )

	m = targetModel.root
	m2 = Matrix()
	m2.setScale((5,5,5))
	m2.postMultiply(m)

	v1 = Vector4( 1.0, 100000, 0, 0 )
	v2 = Vector4( 0.0, 0, 0, 0 )
	v = Vector4Animation()
	v.keyframes=[(0,v1),(0.5,v2)]
	v.duration=1
	v.time=0
	try:
		BigWorld.addWarp( 0.5, m2, v )
	except:
		#running the PC client
		pass
	shake( targetModel )


	#mps = Pixie.create( "particles/plasma_trail.xml" )
	#ps = mps.system( 0 )
	#node = None
	#try:
	#	node = targetModel.node("biped Spine1")
	#except:
	#	node = targetModel.root
	#node.attach(ps)
	#worldDir = Vector3(target.position - BigWorld.player().position)
	#worldDir.normalise()
	#ps.explicitPosition = target.position
	#ps.explicitDirection = worldDir
	#ps.actions[0].force(1)
	#BigWorld.callback( 1.0, partial( node.detach, ps ) )

	ps2 = Pixie.create("particles/plasma_blow.xml")
	targetModel.root.attach(ps2)
	ps2.system( 0 ).actions[0].force(1)
	BigWorld.callback( 5.0, partial( targetModel.root.detach, ps2 ) )

	if delTargetModel:
		BigWorld.callback( 5.0, partial( _safeDelModel, ownerID, targetModel ) )

	if BigWorld.player().flashBangCount == 0:
		fba = Vector4Animation()
		fba.keyframes = [(0,Vector4(0,0,0,0)), (0.1,Vector4(0.1,0.1,0.2,0.5)), (0.3,Vector4(0,0,0,0))]
		fba.duration = 0.3
		try:
			BigWorld.flashBangAnimation(fba)
		except:
			#running the PC client, maybe.
			pass
		BigWorld.callback( fba.duration, partial( BigWorld.flashBangAnimation, None ) )

# Plasma explosion for the specified projectile
def plasmaExplosion( ownerID, targetModel, delModel ):
	owner = BigWorld.entity( ownerID )
	if owner is None:
		return

	#create a model that is along the vector from source to target,
	#at the target minus 2 metres, and then use that as the target.
	plasmaImplode( 1.0, targetModel )
	BigWorld.callback( 1.5, partial( plasmaExplode, ownerID, targetModel, delModel ) )


fxMap = {
	"cannon" : (smokeTrail,standardExplosion,1,1),
	"cannon_he" : (smokeTrail,standardExplosion,1,1),
	"cannon_emp": (smokeTrail,empExplosion,1,1),
	"cannon_plasma": (standardTrail,plasmaExplosion,0,0),
	"throw": (standardTrail,None,1,1)
	}
