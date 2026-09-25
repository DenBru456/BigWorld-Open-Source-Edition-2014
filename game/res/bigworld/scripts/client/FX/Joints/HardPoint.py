from FX import s_sectionProcessors
from FX import typeCheck
from FX.Joint import Joint
from bwdebug import *
import BigWorld


class HardPoint( Joint ):
	'''
	This class implements a Joint that attaches an actor to a HardPoint.
	
	The actor may be any PyAttachment, for example a model or a
	particle system.  If the actor is a model, that model must have
	the corresponding HardPoint in order to align them.  If not, you
	should use the Node Joint instead.
	'''
	def load( self, pSection, prereqs = None ):
		'''
		This method loads the HardPoint Joint from a data section.  The hard-
		point name is read from the section name.
		'''
		self.hpName = pSection.asString
		return self


	def attach( self, actor, source, target = None ):
		#typeCheck( actor, PyAttachment )
		if actor.attached:
			ERROR_MSG( "actor is already attached!", actor, self.hpName )
			return 0

		try:
			setattr( source.model, self.hpName, actor )
		except AttributeError:
			try:
				setattr( source, self.hpName, actor )
			except AttributeError:
				ERROR_MSG( "Missing hardpoint", source, "HP_" + self.hpName )
		except:
			try:
				setattr( source, self.hpName, actor )
			except:
				ERROR_MSG( "Unknown error", source, self.hpName )


	def detach( self, actor, source, target = None ):
		#typeCheck( actor, PyAttachment )
		if not actor.attached:
			# This case can happen if something else detached the actor
			# from the source (e.g. when an entity leaves the AoI and has
			# been cleaned up by the engine). Just don't do anything.
			# Ideally we would clean up effects on demand (e.g. from
			# onLeaveWorld) but this would require larger changes.
			return
		try:
			source.model.node( "HP_" + self.hpName ).detach( actor )
		except AttributeError:
			try:
				source.node( "HP_" + self.hpName ).detach( actor )
			except:
				ERROR_MSG( "Unknown error", source, self.hpName )


s_sectionProcessors[ "HardPoint" ] = HardPoint
#because typos do happen...
s_sectionProcessors[ "Hardpoint" ] = HardPoint
