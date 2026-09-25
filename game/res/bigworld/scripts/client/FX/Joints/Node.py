from FX import s_sectionProcessors
from FX import typeCheck
from FX.Joint import Joint
from bwdebug import *
import BigWorld


class Node( Joint ):
	'''
	This class implements a Joint that attaches an actor to a node.
	
	The actor may be any PyAttachment, for example a model or a
	particle system.
	'''
	def load( self, pSection, prereqs = None ):
		'''
		This method loads the Joint from a data section.  The node
		name is read from the section name.
		'''
		self.nodeName = pSection.asString
		return self


	def attach( self, actor, source, target = None ):
		#typeCheck( actor, [BigWorld.Model,BigWorld.Entity] )
		if source is None:
			return 0

		if actor.attached:
			ERROR_MSG( "actor is already attached!", actor, self.nodeName )
			return 0

		#First try entity ( or something with a model attribute )
		try:
			source.model.node( self.nodeName ).attach( actor )
		except AttributeError:
			#Attribute error - try as a model being passed in
			try:
				source.node( self.nodeName ).attach( actor )
			except ValueError:
				#Value error - probably an incorrect node name
				ERROR_MSG( "No such node", self.nodeName )
		except ValueError:
			#Value error - probably an incorrect node name
			ERROR_MSG( "No such node", self.nodeName )


	def detach( self, actor, source, target = None ):
		#typeCheck( actor, [BigWorld.Model,BigWorld.Entity] )		
		if source is None:
			return
			
		if not actor.attached:
			# This case can happen if something else detached the actor
			# from the source (e.g. when an entity leaves the AoI and has
			# been cleaned up by the engine). Just don't do anything.
			# Ideally we would clean up effects on demand (e.g. from
			# onLeaveWorld) but this would require larger changes.
			return
			
		#First try entity ( or something with a model attribute )
		try:
			source.model.node( self.nodeName ).detach( actor )
		except AttributeError:
			#Attribute error - try as a model being passed in
			try:
				source.node( self.nodeName ).detach( actor )
			except ValueError:
				#Value error - probably an incorrect node name
				ERROR_MSG( "No such node", self.nodeName )
		except ValueError:
			#Value error - probably an incorrect node name
			ERROR_MSG( "No such node", self.nodeName )


s_sectionProcessors[ "Node" ] = Node
