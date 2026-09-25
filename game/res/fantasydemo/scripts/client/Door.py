import BigWorld
import Math

from Helpers import Caps
from GameData import DoorData

import DoorCommon

def _entityDir( ent ):
	d = Math.Matrix( ent.matrix ).applyToAxis( 2 )
	d.normalise()
	return d


def _getModelCentre( model ):
	return Math.Matrix( model.bounds ).applyPoint( (0.5, 0, 0.5) ) + (0, 1.8, 0)


# ------------------------------------------------------------------------------
# Section: class Door
# ------------------------------------------------------------------------------

class Door( BigWorld.Entity ):
	"""
	The Door entity allows the world builder to place openable doors that will
	block both player movement and server navigation whilst the door is closed.
	
	The door must be placed on top of the portal which will be opened and closed
	(which can be either an exit portal or an internal portal), and the door 
	script will automatically discover the portal by using Entity.setPortalState. 
	So, besides	placing the entity in the correct location, the world builder does 
	not have to do any manual linking.
	
	Note that the collision object that gets created whilst the door is closed is
	a 2D flat polygon of the shape of the portal itself. Care must be taken if the
	door model has some of depth (this script could be extended to add additional
	collision objects on the client while the door is shut via PyModelObstacle).
	
	New door types can be defined in scripts/common/GameData/DoorData.py. A door 
	type consists of a model name and a display name.
	"""

	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def __str__( self ):
		chunk = BigWorld.findChunkFromPoint( self.position, self.spaceID )
		return "Door (id=%d, position=%s, chunk=%s)" % (self.id, self.position, chunk)

	def prerequisites( self ):
		return [ DoorData.modelNames[ self.doorType ] ]

	def onEnterWorld( self, prereqs ):
		self.model = BigWorld.Model( DoorData.modelNames[ self.doorType ] )

		self.targetCaps = [ Caps.CAP_CAN_USE ]
		self.targetFullBounds = True

		self.focalMatrix = Math.Matrix()
		self.focalMatrix.setTranslate( _getModelCentre( self.model ) )

		self.retryFindPortalCount = 0
		self.set_state()


	def onLeaveWorld( self ):
		self.model = None
		self.setPortalState( True )


	def set_state( self, oldState = None ):

		#print "Door.set_state: oldState=%s, newState=%s" % (oldState, self.state)

		isOpen = (self.state != DoorData.STATE_CLOSED)

		# If the state has changed then animate.
		if oldState is not None:
			if isOpen:
				self.openAction( self.openingAction() )
			else:
				self.closedAction( self.closingAction( oldState ) )
		# Otherwise set the state animation without animating.
		else:
			if isOpen:
				self.openAction()
			else:
				self.closedAction()

		self.setPortalState( isOpen )


	def use( self ):
		if not self.isClientOnly:
			self.cell.use()
		else:
			oldState = self.state
			if oldState != DoorData.STATE_CLOSED:
				self.state = DoorData.STATE_CLOSED
			else:
				self.state = DoorCommon.getOpeningDirection(
								BigWorld.player().position, 
								self.position, _entityDir(self) )

			self.set_state( oldState )


	def name( self ):
		return DoorData.displayNames[ self.doorType ]


	def openingAction( self ):
		try:
			if self.state == DoorData.STATE_OPEN_INWARD:
				return self.model.DoorOpeningInward()
			elif self.state == DoorData.STATE_OPEN_OUTWARD:
				return self.model.DoorOpeningOutward()
		except AttributeError:
			try:
				return self.model.DoorOpening()
			except AttributeError:
				print "ERROR: Door with type '%s' does not have any valid opening actions." % self.doorType


	def openAction( self, prevActQueuer = None ):
		if prevActQueuer is None:
			prevActQueuer = self.model
		try:
			if self.state == DoorData.STATE_OPEN_INWARD:
				return prevActQueuer.DoorOpenInward()
			elif self.state == DoorData.STATE_OPEN_OUTWARD:
				return prevActQueuer.DoorOpenOutward()
		except AttributeError:
			try:
				return prevActQueuer.DoorOpen()
			except AttributeError:
				print "ERROR: Door with type '%s' does not have any valid open actions." % self.doorType


	def closingAction( self, oldOpenState ):
		try:
			if oldOpenState == DoorData.STATE_OPEN_INWARD:
				return self.model.DoorClosingInward()
			elif oldOpenState == DoorData.STATE_OPEN_OUTWARD:
				return self.model.DoorClosingOutward()
		except AttributeError:
			try:
				return self.model.DoorClosing()
			except AttributeError:
				print "ERROR: Door with type '%s' does not have any valid closing actions." % self.doorType


	def closedAction( self, prevActQueuer = None ):
		if prevActQueuer is None:
			prevActQueuer = self.model
		try:
			return prevActQueuer.DoorClosed()
		except AttributeError:
			print "ERROR: Door with type '%s' does not have a DoorClosed action." % self.doorType


# Door.py
