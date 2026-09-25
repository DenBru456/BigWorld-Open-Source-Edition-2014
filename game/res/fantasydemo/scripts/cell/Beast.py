import BigWorld
import math
import random
import Avatar


class Beast( BigWorld.Entity ):

	THINK_TIMER = 1
	LOAD_TIMER = 2
	LOOK_AT_TIMEOUT_TIMER = 3
	RAGE_TIMER = 4


	#-------------------------------------------------------------------------
	# Constructor.
	#-------------------------------------------------------------------------
	def __init__( self ):
		BigWorld.Entity.__init__( self )

		self.thinkTimer = self.addTimer( 15, 2, Beast.THINK_TIMER )
		self.loadTimer = self.addTimer( 15, 0, Beast.LOAD_TIMER )
		self.lookAtTimeoutTimer = self.addTimer( 15, 0, Beast.LOOK_AT_TIMEOUT_TIMER )	
		self.rageTimer = self.addTimer( 20, 0, Beast.RAGE_TIMER )

		self.scanVisionHandle = self.addScanVision( Beast.VISION_SETTINGS.FOV,
							    Beast.VISION_SETTINGS.VISUAL_RANGE,
							    Beast.VISION_SETTINGS.VIEW_HEIGHT,
							    Beast.VISION_SETTINGS.SCAN_RADIUS,
							    Beast.VISION_SETTINGS.SCAN_DURATION,
							    Beast.VISION_SETTINGS.SCAN_TIMEGAP,
							    Beast.VISION_SETTINGS.VISION_UPDATE,
							    Beast.VISION_SETTINGS.CALLBACK_USERDATA, )

		self.knownAvatars = []

		self.pointsOfInterest = [ 0 ]



	#-------------------------------------------------------------------------
	# This method is called when a timer expires.
	#-------------------------------------------------------------------------
	def onTimer( self, timerID, userID ):
		if userID == Beast.THINK_TIMER:
			self.think()
		elif userID == Beast.LOAD_TIMER:
			pointOfInterestEntities = \
					 self.entitiesInRange( 30.0, 'PointOfInterest' )
			self.pointsOfInterest = []
			for i in pointOfInterestEntities:
				self.pointsOfInterest.append( i.id )
			if len( self.pointsOfInterest ) == 0:
				self.pointsOfInterest = [ 0 ]
		elif userID == Beast.LOOK_AT_TIMEOUT_TIMER:
			self.choseLookAtTarget()
		elif userID == Beast.RAGE_TIMER:
			self.initiateRage()


	#-------------------------------------------------------------------------
	# This method is called when we've finished moving to a point.
	#-------------------------------------------------------------------------
	def onMove(self, controllerId, userId):
		pass


	def think( self ):
		pass


	def choseLookAtTarget( self ):
		oldLookAtTarget = self.lookAtTarget
		if len( self.knownAvatars ) > 0:
			self.lookAtTarget = list( self.knownAvatars )[ random.randint( 0, len( self.knownAvatars ) - 1 ) ]
			while self.lookAtTarget == oldLookAtTarget and len( self.knownAvatars ) > 1:
				self.lookAtTarget = self.knownAvatars[ random.randint( 0, len( self.knownAvatars ) - 1 ) ]
		else:
			self.lookAtTarget = self.pointsOfInterest[ random.randint( 0, len( self.pointsOfInterest ) - 1 ) ]
			while self.lookAtTarget == oldLookAtTarget and len( self.pointsOfInterest ) > 1:
				self.lookAtTarget = self.pointsOfInterest[ random.randint( 0, len( self.pointsOfInterest ) - 1 ) ]

		self.lookAtTimeoutTimer = self.addTimer( random.uniform( 1.0, 4.0 ), 0, Beast.LOOK_AT_TIMEOUT_TIMER )


	def onStartSeeing( self, entityNowSeen ):
		if isinstance( entityNowSeen, Avatar.Avatar ):
			self.knownAvatars.append( entityNowSeen.id )
			self.knownAvatars = list( set( self.knownAvatars ) )
			self.lookAtTarget = entityNowSeen.id
			self.initiateRage()


	def onStopSeeing( self, entityNoLongerSeen ):
		if isinstance( entityNoLongerSeen, Avatar.Avatar ):
			knownAvatarSet = set( self.knownAvatars )
			knownAvatarSet.discard( entityNoLongerSeen.id )
			self.knownAvatars = list( knownAvatarSet )
			if self.lookAtTarget == entityNoLongerSeen.id:
				self.lookAtTarget = 0


	def addKnownEntity( self, source, entityID ):
		self.onStartSeeing( BigWorld.entities[ entityID ] )


	def removeKnownEntity( self, source, entityID ):
		self.onStopSeeing( BigWorld.entities[ entityID ] )


	def initiateRage( self, sourceID = None ):
		self.cancel( self.rageTimer )
		self.allClients.initiateRage()
		self.rageTimer = self.addTimer( random.uniform( 60.0, 90.0 ), 0, Beast.RAGE_TIMER )	


	class VISION_SETTINGS:
		# Visual Controller setup data
		FOV = math.radians( 90 )	# Field-Of-View (in radians)
		VISUAL_RANGE = 50			# Visual range in metres
		VIEW_HEIGHT = 4				# Height of vantage point in metres
		SCAN_RADIUS = math.radians( 90 )	# Radius of scan (amplitude in radians)
		SCAN_DURATION =	20			# Scan duration in ticks (game cycles)
		SCAN_TIMEGAP = 10			# Time between scans in ticks
		VISION_UPDATE =	10			# Vision updated every 10 ticks
		CALLBACK_USERDATA = 1


# Beast.py
