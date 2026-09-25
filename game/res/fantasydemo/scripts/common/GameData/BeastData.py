

import ResMgr



MODEL_NAME = ResMgr.openSection( "scripts/data/beast.xml" ).readString( "modelName" )

SPLASH_MODEL_NAME = ResMgr.openSection( "scripts/data/beast.xml" ).readString( "splashModelName" )

EYE_PARTICLE_SYSTEM = ResMgr.openSection( "scripts/data/beast.xml" ).readString( "eyeParticleSystem" )

SPIT_PARTICLE_SYSTEM = ResMgr.openSection( "scripts/data/beast.xml" ).readString( "spitParticleSystem" )


ACTION_EVENTS = {}




def init_ACTION_EVENTS():
	for ( actionName, actionSection ) in ResMgr.openSection( "scripts/data/beast.xml/actionEvents" ).items():
		actionSounds = []
		actionScriptCalls = []
		actionEffects = []
		
		for ( eventType, eventSection ) in actionSection.items():
			frameNumber = eventSection.readInt( 'frame', -1 )
			assert frameNumber != -1, 'Event must have <frame> section'
			
			if eventType == 'runScript':
				functionName = eventSection.readString( 'function', '' )
				assert len( functionName ) > 0
				actionScriptCalls.append( ( frameNumber, functionName ) )
				
			elif eventType == 'playSound':
				soundName = eventSection.readString( 'sound', '' )
				assert len( soundName ) > 0
				actionSounds.append( ( frameNumber, soundName ) )
				
			elif eventType == 'playEffect':
				effectName = eventSection.readString( 'effect', '' )
				assert len( effectName ) > 0
				actionEffects.append( ( frameNumber, effectName ) )
				
			else:
				assert False, 'Unknown event type'
				
		ACTION_EVENTS[ actionName ] = ( actionSounds, actionScriptCalls, actionEffects )
				
					
		
		
init_ACTION_EVENTS()
				
				
				

