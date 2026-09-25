import BigWorld
import FantasyDemo
import Math
import random

# This implements the moving platform on the cell.
# The platform follows a path of PlatformNodes that is set in
# the editor, starting at the node named in startPatrolNode
# property.
class MovingPlatform( BigWorld.Entity ):

	WAIT_AT_NODE_TIMER = 1

	def __init__( self ):
		BigWorld.Entity.__init__( self )

		if FantasyDemo.hasLoadedAllGeometry( self.spaceID ):
			self.onTimer( 0, MovingPlatform.WAIT_AT_NODE_TIMER );


	def onTimer( self, ctrlID, timerID ):
		if timerID == MovingPlatform.WAIT_AT_NODE_TIMER:
			try:
				self.moveNext()
			except BigWorld.UnresolvedUDORefException:
				self.addTimer(	random.uniform( 5, 6 ), 0,
								MovingPlatform.WAIT_AT_NODE_TIMER )


	def moveNext( self ):
		if len( self.startNode.links ) == 0:
			return

		self.startNode = random.choice( self.startNode.links )

		stopAtDest = (self.startNode.waitTime > 0)

		self.accelerateToPoint( self.startNode.position,
								self.startNode.approachAcceleration,
								self.startNode.approachSpeed,
								0,		# facing: FACING_NONE
								stopAtDest )


	def onMove( self, ctrlID, userArg ):
		try:
			if self.startNode.waitTime > 0:
				self.addTimer(	self.startNode.waitTime, 0,
								MovingPlatform.WAIT_AT_NODE_TIMER )
			else:
				self.moveNext()

		except BigWorld.UnresolvedUDORefException:
			self.addTimer(	random.uniform( 5, 6 ), 0,
							MovingPlatform.WAIT_AT_NODE_TIMER )


	def onPassengerAlightAttempt( self, alightEntity ):
		print "entity", alightEntity.id, "departing"
		return True


	def onPassengerBoardAttempt( self, boardEntity ):
		print "entity", boardEntity.id, "boarding"
		return True


	# Called from cell/FantasyDemo.py when onAllSpaceGeometryLoaded() event is
	# received by the cellapp personality script.
	def onAllSpaceGeometryLoaded( self, spaceID, isBootstrap, mapping ):
		self.onTimer( 0, MovingPlatform.WAIT_AT_NODE_TIMER );


# MovingPlatform.py
