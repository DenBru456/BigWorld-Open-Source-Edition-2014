"""This module provides utility functions for particle systems."""


import BigWorld
import random
import Pixie


# ------------------------------------------------------------------------------
# Method: createGlow
# Description:
#	- Creates a particle system that makes a single lens flare.
# ------------------------------------------------------------------------------
def createGlow():
	return Pixie.create( "particles/glow.xml" )

# ------------------------------------------------------------------------------
# Method: ripperDust
# Description:
#	- Creates a particle system that generates two lines of trailing dust.
# ------------------------------------------------------------------------------
def createRipperDust():
	return Pixie.create( "particles/ripper_dust.xml" )

# ------------------------------------------------------------------------------
# Method: createJetStream
# Description:
#	- Creates a periodic stream.
# ------------------------------------------------------------------------------
def createJetStream():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/jet_stream.xml" )

# ------------------------------------------------------------------------------
# Method: createRipperBreath
# Description:
#	- Creates a periodic burst of green gas.
# ------------------------------------------------------------------------------
def createRipperBreath():
	breath = Pixie.create("particles/ripper_breath.xml")
	breath.system(0).action(1).sleepPeriod = random.randint( 40, 80 ) / 10.0
	return breath

# ------------------------------------------------------------------------------
# Method: createDustSource
# Description:
#	- Creates a particle system that generates dust clouds at will.
#	- Returns a reference to the sourcePSA so that the script may force
#	  creation of particles at will.
# ------------------------------------------------------------------------------
def createDustSource():
	return Pixie.create( "particles/dust_source.xml" )

# ------------------------------------------------------------------------------
# This creates an explosion particle system for the seeker
# ------------------------------------------------------------------------------
def createFragGrenadeExplosion():
	return Pixie.create( "particles/fx_frag_grenade_explosion_outside.xml" )

# ------------------------------------------------------------------------------
# This method creates a ground mist particle system.
# ------------------------------------------------------------------------------
def createGroundMist():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/ground_mist.xml" )

# ------------------------------------------------------------------------------
# This method creates an energy sphere particle system.
# ------------------------------------------------------------------------------
def createEnergySphere( position ):
	energySphere = Pixie.create("particles/energy_sphere.xml")

	( x, y, z ) = position
	orbitor = energySphere.system(0).action(10)
	source = energySphere.system(0).action(1)
	sourceRadius = source.getPositionSourceMaxRadius()

	orbitor.point = ( x, y + sourceRadius, z )

	return energySphere

# ------------------------------------------------------------------------------
# This method creates a chimney smoke particle system.
# ------------------------------------------------------------------------------
def createChimneySmoke():
	return Pixie.create( "particles/chimney_smoke.xml" )

# ------------------------------------------------------------------------------
# This method creates an bonfire particle system.
# ------------------------------------------------------------------------------
def createBonfire():
	return Pixie.create( "particles/bonfire.xml" )

# ------------------------------------------------------------------------------
# This method creates an bonfire particle system for use with non animated fire.
# ------------------------------------------------------------------------------
def createBonfireTwo():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/bonfire_two.xml" )

# ------------------------------------------------------------------------------
# This method creates a rising steam particle system.
# ------------------------------------------------------------------------------
def createRisingSteam():
	return Pixie.create( "particles/rising_steam.xml" )

	# AKR_TODO: note, have lost the randomness on the action
	# loop though actions and perform following line
	# action.minumumAge = random.random() * 2.0


# ------------------------------------------------------------------------------
# This method creates a dust storm particle system.
# ------------------------------------------------------------------------------
def createDustStorm():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/dust_storm.xml" )

# ------------------------------------------------------------------------------
# This method creates a dust storm particle system.
# ------------------------------------------------------------------------------
def createDustStormChunks():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/dust_storm_chunks.xml" )

# ------------------------------------------------------------------------------
# This method creates a spark explosion particle system.
# ------------------------------------------------------------------------------
def createSparkExplosion():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/spark_explosion.xml" )

# ------------------------------------------------------------------------------
# This method creates a pchang spark explosion particle system. ( bullet ricochet)
# ------------------------------------------------------------------------------
def createPchangSparks():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/pchang_sparks.xml" )

# ------------------------------------------------------------------------------
# This method creates a smoke trail particle system
# ------------------------------------------------------------------------------
def createSmokeTrail():
	return Pixie.create( "particles/smoke_trail.xml" )

# ------------------------------------------------------------------------------
# This method creates a flare trace particle system
# ------------------------------------------------------------------------------
def createFlareTrace():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/flare_trace.xml" )


# ------------------------------------------------------------------------------
# This method creates a respawn mist particle system
# ------------------------------------------------------------------------------
def createRespawnMist():
	return Pixie.create( "particles/respawn_mist.xml" )

# ------------------------------------------------------------------------------
# This method creates a blood spray particle system
# ------------------------------------------------------------------------------
def createBloodSpray():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/blood_spray.xml" )

# ------------------------------------------------------------------------------
# This method creates a sparks particle system
# ------------------------------------------------------------------------------
def createSparks():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/sword_sparks.xml" )

# ------------------------------------------------------------------------------
# This method creates a directed sparks particle system
# ------------------------------------------------------------------------------
def createDirectedSparks():
	return Pixie.create( "particles/directed_sparks.xml" )

# ------------------------------------------------------------------------------
# This method creates a directed chunks particle system
# ------------------------------------------------------------------------------
def createDirectedChunks():
	return None
	#TODO : add back in when we have a particle systems for it
	#return Pixie.create( "particles/directed_chunks.xml" )



# ------------------------------------------------------------------------------
#	Section - attachment methods
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Method: attachRipperDust
# Description:
#	- Creates a particle system that generates two lines of trailing dust.
#	- This particle system is owned by the entity.
#	- Returns the particle system.
# ------------------------------------------------------------------------------
def attachRipperDust( model ):
	trails = createRipperDust()
	if trails != None:
		model.root.attach( trails )
	return trails

# ------------------------------------------------------------------------------
# Method: attachRipperBreath
# Description:
#	- Creates a particle system that generates periodic green gas.
#	- This particle system is owned by the model.
#	- Returns the particle system.
# ------------------------------------------------------------------------------
def attachRipperBreath( model ):
	breath = createRipperBreath()
	if breath != None:
		model.root.attach( breath )
	return breath

# ------------------------------------------------------------------------------
# Method: attachDustSource
# Description:
#	- Creates a particle system that generates dust clouds at will.
#	- This particle system is owned by the model.
#	- Returns a reference to the sourcePSA so that the script may force
#	  creation of particles at will.
# ------------------------------------------------------------------------------
def attachDustSource( model ):
	ps = createDustSource()
	if ps != None:
		model.root.attach( ps )
	return ps


# ------------------------------------------------------------------------------
# Method: attachBoosted
# Description:
#	- attaches a boosted effect to the model
# ------------------------------------------------------------------------------
def attachBoosted( model ):
	boosted = createBoosted()
	if boosted != None:
		model.root.attach( boosted )
	return boosted

# ------------------------------------------------------------------------------
# Method: attachGroundMist
# Description:
#	- attaches a ground mist effect to the model
# ------------------------------------------------------------------------------
def attachGroundMist( model ):
	mist = createGroundMist()
	if mist != None:
		model.root.attach( mist )
	return mist

# ------------------------------------------------------------------------------
# Method: attachEnergySphere
# Description:
#	- attaches an energy sphere effect to the model
# ------------------------------------------------------------------------------
def attachEnergySphere( model, position ):
	sphere = createEnergySphere( position )
	if sphere != None:
		model.root.attach( sphere )
	return sphere

# ------------------------------------------------------------------------------
# Method: attachJetStream
# Description:
#	- attaches a jet stream effect to the model
# ------------------------------------------------------------------------------
def attachJetStream( model ):
	js = createJetStream()
	if js != None:
		model.root.attach( js )
	return js

#------------------------------------------------------------------------------
# Method: attachChimneySmoke
# Description:
#	- attaches a chimney smoke effect to the model
# ------------------------------------------------------------------------------
def attachChimneySmoke( model ):
	cs = createChimneySmoke()
	if cs != None:
		model.root.attach( cs )
	return cs

#------------------------------------------------------------------------------
# Method: attachBonfire
# Description:
#	- attaches an bonfire effect to the model
# ------------------------------------------------------------------------------
def attachBonfire( model, animated = True ):
	fire = 0

	if animated:
		fire = createBonfire()
	else:
		fire = createBonfireTwo()

	if fire != None:
		model.root.attach( fire )
	return fire


#------------------------------------------------------------------------------
# Method: attachRisingSteam
# Description:
#	- attaches a rising steam effect to the model
# ------------------------------------------------------------------------------
def attachRisingSteam( model ):
	steam = createRisingSteam()
	if steam != None:
		model.root.attach( steam )
	return steam



def flickeringLight():
	import Math
	flame_r = 250
	flame_g = 250
	flame_b = 250
	timescale = 0.5
	pulseShader = Math.Vector4Animation()
	pulseShader.duration = 6.6 * timescale
	pulseShader.keyframes = [
	  (0.0*timescale, (0.35 * flame_r, 0.35 * flame_g, 0.35 * flame_b,  0) ),	# 1
	  (0.6*timescale, (0.65 * flame_r, 0.65 * flame_g, 0.65 * flame_b,  0) ),
	  (0.7*timescale, (0.33 * flame_r, 0.33 * flame_g, 0.33 * flame_b,  0) ),
	  (0.9*timescale, (0.65 * flame_r, 0.65 * flame_g, 0.65 * flame_b,  0) ),
	  (1.2*timescale, (0.41 * flame_r, 0.41 * flame_g, 0.41 * flame_b,  0) ),	# 5
	  (1.5*timescale, (0.65 * flame_r, 0.65 * flame_g, 0.65 * flame_b,  0) ),
	  (1.7*timescale, (0.41 * flame_r, 0.41 * flame_g, 0.41 * flame_b,  0) ),
	  (1.9*timescale, (0.80 * flame_r, 0.80 * flame_g, 0.80 * flame_b,  0) ),
	  (2.1*timescale, (0.20 * flame_r, 0.20 * flame_g, 0.20 * flame_b,  0) ),
	  (2.4*timescale, (0.92 * flame_r, 0.92 * flame_g, 0.92 * flame_b,  0) ),	# 10
	  (2.7*timescale, (0.44 * flame_r, 0.44 * flame_g, 0.44 * flame_b,  0) ),
	  (3.2*timescale, (0.72 * flame_r, 0.72 * flame_g, 0.72 * flame_b,  0) ),
	  (3.7*timescale, (0.32 * flame_r, 0.32 * flame_g, 0.32 * flame_b,  0) ),
	  (3.9*timescale, (0.78 * flame_r, 0.78 * flame_g, 0.78 * flame_b,  0) ),
	  (4.2*timescale, (0.18 * flame_r, 0.18 * flame_g, 0.18 * flame_b,  0) ),	# 15
	  (4.4*timescale, (0.86 * flame_r, 0.86 * flame_g, 0.86 * flame_b,  0) ),
	  (4.8*timescale, (0.46 * flame_r, 0.46 * flame_g, 0.46 * flame_b,  0) ),
	  (5.5*timescale, (0.76 * flame_r, 0.76 * flame_g, 0.76 * flame_b,  0) ),
	  (5.8*timescale, (0.22 * flame_r, 0.22 * flame_g, 0.22 * flame_b,  0) ),
	  (6.3*timescale, (0.80 * flame_r, 0.80 * flame_g, 0.80 * flame_b,  0) ),	# 20
	  (6.5*timescale, (0.36 * flame_r, 0.36 * flame_g, 0.36 * flame_b,  0) ),
	  (6.5*timescale, (0.54 * flame_r, 0.54 * flame_g, 0.54 * flame_b,  0) ) ]	# 22
	pulse = BigWorld.PyChunkLight()
	pulse.innerRadius = 1
	pulse.outerRadius = 10
	pulse.position = (0, 0, 0)
	pulse.shader = pulseShader
	pulse.specular = 1
	pulse.diffuse = 1
	pulse.visible = True
	return pulse

#particles.py
