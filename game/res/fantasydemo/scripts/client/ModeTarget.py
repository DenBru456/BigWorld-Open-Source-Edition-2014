import BigWorld
from bwdebug import *
import AvatarMode

class ModeTarget():
	"""
	This class should be inherited by entities that we want to involve 
	in multi-entity modes - modes that require the cooperation and/or 
	synchronisation of more than one entity.
	"""

	def __init__( self ):
		# Flag set to True if we're waiting for another entity to be created.
		self._waitingForModeTarget = False


	def _getModeTarget( self ):
		if BigWorld.entities.has_key( self.modeTarget ):
			return BigWorld.entities[ self.modeTarget ]
		else:
			ERROR_MSG( 'Unknown target entity (id=%d)' % self.modeTarget )
			return None
		
	
	def _isModeTargetReady( self ):
		"""
		This method should be called in onEnterWorld to check if 
		we have a mode target, and (if we do have a mode target) that 
		it has been created.
		"""
		if self.modeTarget == AvatarMode.NO_TARGET:
			return True
			
		if BigWorld.entities.has_key( self.modeTarget ):
			BigWorld.entities[ self.modeTarget ]._onModeTargetReady()
			return True
		else:
			self._waitingForModeTarget = True
			return False
			
			
	def _waitForModeTarget( self ):
		self._waitingForModeTarget = True
		
		
	def _endWaitForModeTarget( self ):
		self._waitingForModeTarget = False
			
			
	def _onModeTargetReady( self ):
		"""
		This method should be overridden by inheriting classes to initialise modes.
		Returns True if we were waiting for our modeTarget, otherwise returns False.
		"""
		if not self._waitingForModeTarget:
			WARNING_MSG( "Unexpected communication from modeTarget entity." )
			return False
		else:
			self._waitingForModeTarget = False
			return True
