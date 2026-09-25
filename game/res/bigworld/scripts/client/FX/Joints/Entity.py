from FX import s_sectionProcessors
from FX import typeCheck
from FX.Joint import Joint
from bwdebug import *
import BigWorld
import traceback


class Entity( Joint ):
	'''
	This class implements a Joint that attaches an actor to an Entity.
	
	The actor may be any PyAttachment, for example a model or a
	particle system.

	If the actor is a Model, a motor is attached to it so that it
	follows the Entity's movements.

	If the actor is a Particle System, it is placed in the world at the
	current location of the Entity, but will not move around once attached.
	'''
	def attach( self, actor, source, target = None ):
		#typeCheck( source, [BigWorld.Entity] )

		if actor.attached:
			ERROR_MSG( "actor is already attached!", self, actor, source )
			return 0
		
		if source is None:
			return 0

		try:
			source.addModel( actor )
		except:
			ERROR_MSG( "error in addModel to entity", self, actor, source )

		#Move to the correct location
		moved = 0

		try:
			#actor is a model?  can add a motor
			actor.addMotor( BigWorld.Servo( source.matrix ) )
			moved = 1
		except AttributeError:
			try:
				#actor is a particle system?
				actor.explicitPosition = source.position
				moved = 1
			except AttributeError:
				try:
					#actor is a meta-particle system
					for i in xrange(0,actor.nSystems()):
						actor.system(i).explicitPosition = source.position
					moved = 1
				except:
					traceback.print_exc()
					#traceback.print_stack()

		if not moved:
			ERROR_MSG( "Unknown error trying to move actor to the correct location", actor, source )


	def detach( self, actor, source, target = None ):
		if not actor.attached:
			# This case can happen if something else detached the actor
			# from the source (e.g. when an entity leaves the AoI and has
			# been cleaned up by the engine). Just don't do anything.
			# Ideally we would clean up effects on demand (e.g. from
			# onLeaveWorld) but this would require larger changes.
			return

		try:
			source.delModel( actor )
		except:
			ERROR_MSG( "error in delModel from entity", self, actor, source )


s_sectionProcessors[ "Entity" ] = Entity
