import BigWorld
import Math
import DoorCommon

from GameData import DoorData

def _entityDir( ent ):
	m = Math.Matrix()
	m.setRotateYPR( (ent.yaw, ent.pitch, ent.roll) )
	d = m.applyToAxis(2)
	d.normalise()
	return d



# ------------------------------------------------------------------------------
# Section: class Door
# ------------------------------------------------------------------------------

TIMER_AUTO_CLOSE = 1


class Door( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self._setPortalStates()


	def use( self, sourceID ):
		try:
			user = BigWorld.entities[ sourceID ]
		except KeyError:
			print "%s.use: sourceID=%d does not exist in our known entities."
			return

		# Make sure we don't let people thrash the door state.
		if BigWorld.time() < self.lastUseTime + self.reuseDelay:
			return

		oldState = self.state
		if self._isOpen():
			self.state = DoorData.STATE_CLOSED
		else:
			self.state = DoorCommon.getOpeningDirection( 
							user.position, 
							self.position, _entityDir(self) )

		self.lastUseTime = BigWorld.time()

		# Cancel any close timer
		if self.autoCloseTimerID != 0:
			self.cancel( self.autoCloseTimerID )
			self.autoCloseTimerID = 0

		# Setup the auto close timer if we need to
		if self._isOpen() and self.autoCloseDelay > 0:
			self.autoCloseTimerID = self.addTimer( self.autoCloseDelay, 0, TIMER_AUTO_CLOSE )

		self._setPortalStates()
		#print "%s.use: Door state toggled (new state = %d)" % (self, self.state)


	def __str__( self ):
		chunk = BigWorld.findChunkFromPoint( self.position, self.spaceID )
		return "Door (id=%d, position=%s, chunk=%s)" % (self.id, self.position, chunk)


	def onTimer( self, controllerID, userData ):
		if userData == TIMER_AUTO_CLOSE:
			self.state = DoorData.STATE_CLOSED
			self._setPortalStates()
			self.autoCloseTimerID = 0
			#print "%s: Auto closed." % self


	def _isOpen( self ):
		return self.state != DoorData.STATE_CLOSED

	def _setPortalStates( self ):
		self.setPortalState( self._isOpen() )

# Door.py
