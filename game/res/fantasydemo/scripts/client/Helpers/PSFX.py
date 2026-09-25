"""This module acts as a bank for particle system effects. All effects from
this module are temporary effects that dissipate over time."""


import BigWorld
import Pixie
import particles
from Keys import *
from functools import partial


# ------------------------------------------------------------------------------
# Global Lists of Particle Systems.
# ------------------------------------------------------------------------------
sparksList = None
bloodSprayList = None
respawnMistList = None
smokeTrailList = None
explosionList = None
arrowTraceList = None
flareTraceList = None
pchangSparkList = None
worldExplosionList = None
pchangChunkSystem = None
pchangChunkModel = None
dustStorm = None
dustStormChunks = None
dustStormFog = None

# ------------------------------------------------------------------------------
# Particle System Action IDs.
# ------------------------------------------------------------------------------
SOURCE_PSA			=  1
SINK_PSA			=  2
BARRIER_PSA			=  3
FORCE_PSA			=  4
STREAM_PSA			=  5
JITTER_PSA			=  6
SCALER_PSA			=  7
TINT_SHADER_PSA		=  8
NODE_CLAMP_PSA		=  9
ORBITOR_PSA			= 10
FLARE_PSA			= 11


# ------------------------------------------------------------------------------
# Method: detachEffect
# Description:
#	- Used internally as a call-back method to free the particle system back
#	  into the list of available ones.
# ------------------------------------------------------------------------------
def detachEffect( model, system, store, nodeName = None ):

	# Remove the particle system from the model.
	if nodeName:
		model.node( nodeName ).detach( system )
	else:
		model.root.detach( system )

	# Clean the particles
	system.clear()

	# Return it to the list.
	store.append( system )


# ------------------------------------------------------------------------------
# Method: attachSparks
# Description:
#	- Used by various scripts when they wish to add a spark effect to a model.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def attachSparks( model, nodeName = None, numberOfSparks = 1 ):
	global sparksList

	# Generate the list of particle systems if not already done so.
	if sparksList == None:
		sparksList = generateSparksList( 10 )

	if len( sparksList ) >= 1:
		# Get the particle at the end of the list.
		sparks = sparksList.pop()

		# Attach it to the model.
		if nodeName != None:
			model.node(nodeName).attach( sparks )
		else:
			model.root.attach( sparks )

		# Tell the particle system to make the sparks.
		sparks.action( SOURCE_PSA ).force( numberOfSparks )

		# Set up call-back for removal of the sparks.
		BigWorld.callback( sparks.action( SINK_PSA ).maximumAge + 1.0,
			partial( detachEffect, model, sparks, sparksList, nodeName ) )


# ------------------------------------------------------------------------------
# Method: generateSparksList
# Description:
#	- Creates sparks particle systems, populating the sparksList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generateSparksList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		sparks = particles.createSparks()
		if sparks != None:
			psList.append( sparks )
		i = i + 1

	return psList


# ------------------------------------------------------------------------------
# Method: attachBloodSpray
# Description:
#	- Used by various scripts when they wish to add blood spray to a model.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def attachBloodSpray( model, direction = 0, numberOfSprays = 1 ):
	global bloodSprayList

	# Generate the list of particle systems if not already done so.
	if bloodSprayList == None:
		bloodSprayList = generateBloodSprayList( 10 )

	if len( bloodSprayList ) >= 1:
		# Get the particle at the end of the list.
		bloodSpray = bloodSprayList.pop()

		# Attach it to the model.
		model.root.attach( bloodSpray )
		src = bloodSpray.action( SOURCE_PSA )
		height = model.height * 0.8

		# Set the position and direction of the sprays.
		src.setPositionSource( [ "Point", ( 0.0, height, 0.0 ) ] )
		if direction == 0:
			src.setVelocitySource( [ "Sphere", ( 0.0, 4.0, 0.0 ), 1.5, 0.5 ] )
		elif direction == 1:
			src.setVelocitySource( [ "Sphere", ( -4.0, 0.0, 0.0 ), 1.5, 0.5 ] )
		elif direction == 2:
			src.setVelocitySource( [ "Sphere", ( 4.0, 0.0, 0.0 ), 1.5, 0.5 ] )

		# Tell the bloodSpray to make the sprays.
		src.force( numberOfSprays )

		# Set up call-back for removal of the blood.
		BigWorld.callback( bloodSpray.action( SINK_PSA ).maximumAge + 1.0,
			partial( detachEffect, model, bloodSpray, bloodSprayList ) )


# ------------------------------------------------------------------------------
# Method: generateBloodSprayList
# Description:
#	- Creates blood-spray particle systems, populating the bloodSprayList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generateBloodSprayList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		blood = particles.createBloodSpray()
		if blood != None:
			psList.append( blood )
		i = i + 1

	return psList


# ------------------------------------------------------------------------------
# Method: attachRespawnMist
# Description:
#	- Used by various scripts when they wish to add a respawn mist exploding
#	  from the model.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def attachRespawnMist( model, density = 100 ):
	global respawnMistList

	# Generate the list of particle systems if not already done so.
	if respawnMistList == None:
		respawnMistList = generateRespawnMistList( 10 )

	if len( respawnMistList ) >= 1:
		# Get the particle at the end of the list.
		mist = respawnMistList.pop()

		# Attach it to the model.
		model.root.attach( mist )
		#mist.system(0).action( ORBITOR_PSA ).point = model.position		

		# Tell the particle system to make the mist.
		BigWorld.callback( 0.01, partial( mist.system(0).action( SOURCE_PSA ).force, density ))
		#src = mist.system(0).action( SOURCE_PSA )
		#src.forcedUnitSize = density
		#src.force( 1 )

		# Set up call-back for removal of the mist.
		BigWorld.callback( mist.system(0).action( SINK_PSA ).maximumAge + 1.0,
			partial( detachEffect, model, mist, respawnMistList ) )


# ------------------------------------------------------------------------------
# Method: generateRespawnMistList
# Description:
#	- Creates energy mist particle systems, populating the respawnMistList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generateRespawnMistList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		mist = particles.createRespawnMist()
		psList.append( mist )
		i = i + 1

	return psList


# ------------------------------------------------------------------------------
# Method: attachArrowTrace
# Description:
#	- Used by various scripts when they wish to add an arrow trace to a model.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def attachArrowTrace( model, nodeName = None, flightTime = 1.0 ):
	global arrowTraceList

	# Generate the list of particle systems if not already done so.
	if arrowTraceList == None:
		arrowTraceList = generateArrowTraceList( 10 )

	if len( arrowTraceList ) >= 1:
		# Get the particle at the end of the list.
		trace = arrowTraceList.pop()

		# Attach it to the model.
		if nodeName != None:
			model.node(nodeName).attach( trace )
		else:
			model.root.attach( trace )
		trace.action( SOURCE_PSA ).motionTriggered = True

		# Set up call-back for removal of the sparks.
		BigWorld.callback( flightTime + 1.0,
			partial( detachEffect, model, trace, arrowTraceList, nodeName ) )


# ------------------------------------------------------------------------------
# Method: generateArrowTraceList
# Description:
#	- Creates arrow trace particle systems, populating the arrowTraceList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generateArrowTraceList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		trace = particles.createArrowTrace()
		psList.append( trace )
		i = i + 1

	return psList


# ------------------------------------------------------------------------------
# Method: attachFlareTrace
# Description:
#	- Used by various scripts when they wish to add an flare trace to a model.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def attachFlareTrace( model, nodeName = None, flightTime = 1.0 ):
	global flareTraceList
	global majorFlarePSA
	global minorFlarePSA

	# Generate the list of particle systems if not already done so.
	if flareTraceList == None:
		flareTraceList = generateFlareTraceList( 10 )

	if len( flareTraceList ) >= 1:
		# Get the particle at the end of the list.
		trace = flareTraceList.pop()

		# Attach it to the model.
		if nodeName != None:
			model.node(nodeName).attach( trace )
		else:
			model.root.attach( trace )
		trace.action( SOURCE_PSA ).motionTriggered = True

		# Setit up to fly
		trace.renderer.blurred=True

		# Set up call-back for removal of the tracer, and
		# creation of the major flare.
		BigWorld.callback( flightTime + 1.0,
			partial( detachEffect, model, trace, flareTraceList, nodeName ) )


# ------------------------------------------------------------------------------
# Method: generateFlareTraceList
# Description:
#	- Creates flare trace particle systems, populating the flareTraceList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generateFlareTraceList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		trace = particles.createFlareTrace()
		if trace != None:
			psList.append( trace )
		i = i + 1

	return psList


# ------------------------------------------------------------------------------
# Method: attachSmokeTrail
# Description:
#	- Used by various scripts when they wish to add a smoke trail emanating
#	  from the model.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def attachSmokeTrail( model, nodeName = None ):
	global smokeTrailList

	# Generate the list of particle systems if not already done so.
	if smokeTrailList == None:
		smokeTrailList = generateSmokeTrailList( 10 )

	if len( smokeTrailList ) >= 1:
		# Get the particle at the end of the list.
		trail = smokeTrailList.pop()

		# Attach it to the model.
		if nodeName:
			model.node( nodeName ).attach( trail )
		else:
			model.root.attach( trail )

		# Set up call-back for removal of the mist.
		BigWorld.callback( trail.action( SINK_PSA ).maximumAge + 1.0,
			partial( detachEffect, model, trail, smokeTrailList, nodeName ) )

# ------------------------------------------------------------------------------
# Method: generateSmokeTrailList
# Description:
#	- Creates smoke trail particle systems, populating the SmokeTrailList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generateSmokeTrailList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		mist = particles.createSmokeTrail()
		psList.append( mist )
		i = i + 1

	return psList

# ------------------------------------------------------------------------------
# Method: attachExplosion
# Description:
#	- Used by various scripts when they wish to add a spark explosion to a model.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def attachExplosion( model, nodeName = None, numberOfSparks = 25 ):
	global explosionList

	# Generate the list of particle systems if not already done so.
	if explosionList == None:
		explosionList = generateExplosionList( 10 )

	if len( explosionList ) >= 1:
		# Get the particle at the end of the list.
		explosion = explosionList.pop()

		# Attach it to the model.
		if nodeName != None:
			model.node(nodeName).attach( explosion )
		else:
			model.root.attach( explosion )

		# Tell the particle system to make the sparks.
		explosion.action( SOURCE_PSA ).force( numberOfSparks )

		# Set up call-back for removal of the sparks.
		BigWorld.callback( explosion.action( SINK_PSA ).maximumAge + 1.0,
			partial( detachEffect, model, explosion, explosionList, nodeName ) )


# ------------------------------------------------------------------------------
# Method: generateExplosionList
# Description:
#	- Creates explosion particle systems, populating the explosionList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generateExplosionList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		explosion = particles.createSparkExplosion()
		if explosion != None:
			psList.append( explosion )
		i = i + 1

	return psList


# ------------------------------------------------------------------------------
# Method: attachPchangSparks
# Description:
#	- Used by various scripts when they wish to add a spark explosion to a pchang.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def attachPchangSparks( model, worldDir, worldPos, triangleFlags, number ):
	global pchangSparkList

	# Generate the list of particle systems if not already done so.
	if pchangSparkList == None:
		pchangSparkList = generatePchangSparkList( 10 )

	if len( pchangSparkList ) >= 1:
		# Get the particle at the end of the list.
		explosion = pchangSparkList.pop()

		# Attach it to the model.
		model.root.attach( explosion )

		# this overrides the problem with attaching to a model
		explosion.explicitPosition = worldPos
		explosion.explicitDirection = worldDir

		# Tell the particle system to make the sparks.
		explosion.action( SOURCE_PSA ).force( number )

		# Set up call-back for removal of the sparks.
		BigWorld.callback( explosion.action( SINK_PSA ).maximumAge + 0.1,
			partial( detachEffect, model, explosion, pchangSparkList ) )


# ------------------------------------------------------------------------------
# Method: generatePchangSparkList
# Description:
#	- Creates pchangSpark particle systems, populating the pchangList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generatePchangSparkList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		pchang = particles.createPchangSparks()
		if pchang != None:
			psList.append( pchang )
		i = i + 1

	return psList


# ------------------------------------------------------------------------------
# Method: attachPchangChunks
# Description:
#	- Used by various scripts when they wish to add a chunk explosion to a pchang.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def detachPchangChunks( model ):
	global pchangChunkSystem
	global pchangChunkModel

	if model == pchangChunkModel:
		pchangChunkModel.root.detach( pchangChunkSystem )
		pchangChunkModel = None


def attachPchangChunks( model, worldDir, worldPos, triangleFlags, number ):
	global pchangChunkSystem
	global pchangChunkModel

	# Generate the particle system if not already done so.
	if pchangChunkSystem == None:
		pchangChunkSystem = particles.createDirectedChunks()
		pchangChunkModel = None

	# Delete from existing model.
	if pchangChunkModel:
		pchangChunkModel.root.detach( pchangChunkSystem )
		
	pchangChunkModel = model

	# Attach it to the model.
	if pchangChunkSystem != None:
		model.root.attach( pchangChunkSystem )	

		# this overrides the problem with attaching to a model	
		pchangChunkSystem.explicitDirection = worldDir
		pchangChunkSystem.explicitPosition = worldPos

		# Tell the particle system to make the chunks.
		pchangChunkSystem.action( SOURCE_PSA ).force( number )

		# Set up call-back for removal of the chunks.
		BigWorld.callback( pchangChunkSystem.action( SINK_PSA ).maximumAge + 0.1,
			partial( detachPchangChunks, model ) )


# ------------------------------------------------------------------------------
# Method: attachPchangSparks
# Description:
#	- Used by various scripts when they wish to add a spark explosion to a pchang.
#	- Automatically attaches and plays the PSFX. After playing, the PSFX is
#	  removed without further intervention.
# ------------------------------------------------------------------------------
def worldExplosion( model, worldDir, worldPos, triangleFlags, number ):
	global worldExplosionList

	# Generate the list of particle systems if not already done so.
	if worldExplosionList == None:
		worldExplosionList = generateWorldExplosionList(10)

	if len( worldExplosionList ) >= 1:
		# Get the particle at the end of the list.
		explosion = worldExplosionList.pop()		

		# Attach it to the model.
		model.root.attach( explosion )

		time = 0.0

		for i in xrange( 0, explosion.nSystems() ):
			system = explosion.system(i)

			# this overrides the problem with attaching to a model
			system.explicitPosition = worldPos
			system.explicitDirection = worldDir

			# what renderer shall we use?  hmmm...
			#if triangleFlags == 0:
			#	meshRenderer.visual = "clumpsOfDirt.visual"
			#	explosion.renderer = meshRenderer
			#else:
			#	explosion.renderer = spriteRenderer

			# Tell the particle system to make the explosion.
			system.action( SOURCE_PSA ).force( number )

			sink = system.action( SINK_PSA )
			time = max( time, sink.maximumAge + 0.1 )

		# Set up call-back for removal of the explosion.
		BigWorld.callback( time,partial( detachEffect, model, explosion, worldExplosionList ) )


# ------------------------------------------------------------------------------
# Method: generateWorldExplosionList
# Description:
#	- Creates worldExplosion particle systems, populating the worldExplosionList.
#	- Returns the list with size numberOfPS.
# ------------------------------------------------------------------------------
def generateWorldExplosionList( numberOfPS ):
	psList = []

	i = 0
	while i < numberOfPS:
		explosion = particles.createDirectedSparks()
		psList.append( explosion )
		i = i + 1

	return psList

# ------------------------------------------------------------------------------
# Method: beginDustStorm
# Description:
#	This method creates 2 particle systems and a fog emitter
# ------------------------------------------------------------------------------
def beginDustStorm():
	global dustStorm
	global dustStormChunks
	global dustStormFog

	if not dustStorm:
		dustStorm = particles.createDustStorm()
		dustStormChunks = particles.createDustStormChunks()

	pos = BigWorld.player().position
	BigWorld.player().model.root.attach( dustStorm )
	BigWorld.player().model.root.attach( dustStormChunks )
	dustStormFog = BigWorld.addFogEmitter( (0,0,0), 4,0,100, 0xff802020, 0 )


def endDustStorm():
	global dustStorm
	global dustStormChunks
	global dustStormFog
	BigWorld.player().model.root.detach( dustStorm )
	BigWorld.player().model.root.detach( dustStormChunks )
	BigWorld.delFogEmitter( dustStormFog )



warpEffects = []

def beginPlasmaWarp( target ):
	global warpEffects

	allFinished = 1
	for (finished,i,s,t) in warpEffects:
		if not finished:
			allFinished = 0

	if allFinished:
		warpEffects = []

	ps = Pixie.create("particles/plasma_suck.xml")
	try:
		target.node("biped Head").attach(ps)
	except:
		target.root.attach(ps)

	m = target.root
	m2 = Matrix()
	m2.setScale((1,1,1))
	m2.postMultiply(m)

	v1 = Vector4( 3.0, -100000, 0, 0 )
	v2 = Vector4( 0.0, 0, 0, 0 )
	v = Vector4Animation()
	v.keyframes=[(0,v2),(3,v1)]
	v.duration=1000000
	v.time=0
	warpEffects.append( [0,v,ps,target] )
	try:
		BigWorld.addWarp( 100000, m2, v )
	except:
		#PC client
		pass
	return len( warpEffects ) - 1

def endPlasmaWarp( idx ):
	global warpEffects

	#changing the z-value to 1.0 signals to the warp effects
	#engine that the effect should finish up.
	ps = warpEffects[idx][2]
	target = warpEffects[idx][3]
	try:
		target.node("biped Head").detach(ps)
	except:
		target.root.detach(ps)

	warpEffects[idx][1].keyframes = [(0,Vector4(0.0,0.0,1.0,0.0))]
	warpEffects[idx][0] = 1


# ParticleSystemManager.py
