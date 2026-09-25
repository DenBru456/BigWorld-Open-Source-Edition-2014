
from bwdebug import *
from functools import partial

import BigWorld
import Math

class PathSeeker:
	'''
	The PathSeeker class handles moving the player along client side navigation
	paths or automatically following a straight line path if it could not
	navigate.
	Note that client side navigation must be enabled in space.settings to be
	able to find a navigation path.
	'''

	DEBUG_NAVIGATION_PATHS = False
	DEBUG_MODEL_NAME = "helpers/models/unit_sphere.model"
	DEBUG_WATCH = "Client Settings/Physics/draw debug path points"
	DEBUG_WATCH_ADDED = False


	def __init__( self ):
		'''Load up models for debugging'''

		if PathSeeker.DEBUG_NAVIGATION_PATHS:
			self._loadDebugModels()

		if not PathSeeker.DEBUG_WATCH_ADDED:
			BigWorld.addWatcher(
				PathSeeker.DEBUG_WATCH, self.getDebugOn, self.setDebugOn )
			PathSeeker.DEBUG_WATCH_ADDED = True

	def getDebugOn( self ):
		'''
		Check if debugging is on/off.
		@return true if debugging.
		'''
		return PathSeeker.DEBUG_NAVIGATION_PATHS

	def setDebugOn( self, value ):
		'''
		Turn debugging on/off.
		@param value on/off.
		'''
		try:
			if value.lower() in ("true", "1"):
				PathSeeker.DEBUG_NAVIGATION_PATHS = True

				# Not loaded or loading
				if not hasattr( self, "_debugModel" ):
					self._loadDebugModels()
			else:
				PathSeeker.DEBUG_NAVIGATION_PATHS = False
		except:
			pass

	def getPosAndYawToTarget( self, endPos, targetPos ):
		'''
		Calculate the yaw to turn to a given target at the end of a path.
		@param endPos the position at the end of the path
		'''
		targetYaw = (targetPos - endPos).yaw
		targetPosAndYaw = (targetPos[0], targetPos[1], targetPos[2], targetYaw)
		return targetPosAndYaw

	def seekPath( self,
		player,
		targetPositionAndYaw,
		speed,
		timeout=-1.0,
		heightDiff=-1.0,
		callback=None ):
	
		'''
		Calculate a path for the player to follow towards a target position and
		then automatically move towards it.
		@param player the player to move
		@param the target position and target yaw at the end of the path in a
			4 tuple.
		@param speed the speed to seek at.
		@param timeout the timeout for failure. Set to -1 to calculate a
			timeout based on the path length. If the timeout is too short for
			the path length then the seek will automatically cancel.
		@param heightDiff the height tolerance for reaching the end point.
		@param callback a callback to use on success or failure.
		'''
		self._cleanup( player )

		targetPosition = (targetPositionAndYaw[0],
			targetPositionAndYaw[1],
			targetPositionAndYaw[2])
		path = self._calculatePath( player, targetPosition )
		self._seekPathInternal( path, targetPositionAndYaw[3],
			player, speed, timeout, heightDiff, callback )

	def updateVelocity( self, player ):
		'''
		Update the player's velocity for seeking.
		Use this when a player's default forward velocity changes. eg. when he
		gets in/out of water.
		@param player the player.
		'''
		player.physics.velocity = ( 0, 0, player.runFwdSpeed )

	def cancel( self, player ):
		'''
		Cancel automatic path seeking on a player.
		@param player the player to stop seeking.
		'''
		# Will call _onSeekPathFinished callback which does cleanup
		player.physics.cancelSeek()

	def onLeaveWorld( self, player ):
		'''
		Remove any debug models attached to the player.
		@param player the player to clean up.
		'''
		self._cleanupNavPathModels( player )

	def _cleanup( self, player ):
		'''
		Cleanup after cancelling/finishing a seek.
		@param the player that was seeking.
		'''
		player.isMovingToDest = False
		self._cleanupNavPathModels( player )
		self._moveNavPath = []

	def _seekPathInternal( self,
		path,
		yaw,
		player,
		speed,
		timeout=-1.0,
		heightDiff=0.0,
		callback=None ):

		'''
		Get the player to automatically follow a given set of points.
		@param path the list of point positions to follow.
		@param yaw the yaw to turn to at the end of the path.
		@param player the player that is following.
		@param speed speed to move along path.
		@param timeout timeout, if -1 then calculate timeout.
		@param heightDiff vertical range, -1 to ignore.
		@param targetPosition the last point/goal.
		'''

		# If timeout is < 0 then use calculated timeout
		if timeout < 0.0:
			# Add x2 to try to estimate slowing from going up hills etc.
			timeout = self._calculateTimeout( path, speed ) * 2.0
		# Otherwise work out if we can
		else:
			calculatedTimeout = self._calculateTimeout( path, speed )
			if calculatedTimeout > timeout:
				# Fail early
				if PathSeeker.DEBUG_NAVIGATION_PATHS:
					DEBUG_MSG( "Could not make it along given path in ",
					timeout, "s, estimated time ", calculatedTimeout, "s" )
				self._onSeekPathFinished( player, callback, False )
				return

		# Set our path
		self._moveNavPath = path

		# Add models at path points
		self._attachDebugModels( player )

		# Seek along path
		player.physics.seekPath( self._moveNavPath,
				yaw,
				speed,
				timeout,
				heightDiff,
				partial( self._onSeekPathFinished, player, callback ) )
		player.isMovingToDest = True

	def _attachDebugModels( self, player ):
		'''
		Attach a for each path point to the player.
		@param player the player to attach the models to.
		'''
		if PathSeeker.DEBUG_NAVIGATION_PATHS:
			# Not loaded or loading
			if hasattr( self, "_debugModel" ) and self._debugModel is not None:
				for pathPoint in self._moveNavPath:
					m = BigWorld.Model( PathSeeker.DEBUG_MODEL_NAME )
					m.scale = (0.1, 0.1, 0.1)
					player.addModel( m )
					m.position = pathPoint
					self._debugNavPathModels.append( m )

	def _calculateTimeout( self, path, speed ):
		'''
		Add up timeout - linear length of path at given speed.
		@param path the path.
		@param speed speed to move along the path.
		@return timeout calculated timeout for moving along that path.
		'''
		timeout = 0
		lastPoint = path[-1] # End of list

		# Time from first point on path to next
		for pathPoint in path:
			segmentLength = Math.Vector3( pathPoint ).distTo( lastPoint )
			timeout += (segmentLength / speed)
			lastPoint = pathPoint

		return timeout

	def _calculatePath( self, player, targetPosition ):
		'''
		Calculate path from myself to position.
		@param player the player at the start of the path.
		@param targetPosition the goal/end of path.
		@return a list of points along the path to take.
		'''
		path = []

		try:
			# Calculate path path
			path = BigWorld.navigatePathPoints(
				player.position, targetPosition )

			if PathSeeker.DEBUG_NAVIGATION_PATHS:
				DEBUG_MSG( "player", player.position )
				DEBUG_MSG( "target", targetPosition )
				DEBUG_MSG( "path", path )

		except ValueError, e:

			# Could not find path, either because:
			# 1. client side navigation is not enabled in space.settings
			# 2. can't find a way to navigate there
			if PathSeeker.DEBUG_NAVIGATION_PATHS:
				DEBUG_MSG( e )
				DEBUG_MSG( "start", player.position, "end", targetPosition )

			# Could not calculate path, move in straight line towards goal
			path = [ player.position, targetPosition ]

		# Return the calculated path
		return path

	def _onSeekPathFinished( self, player, callback, prevSuccess=True ):
		'''
		Callback for when the seeking along a path has finished.
		@param player the player which was seeking.
		@param callback callback to call, ignored if None.
		@param prevSuccess reached end.
		'''
		self._cleanup( player )

		if callback is not None:
			callback( prevSuccess )

		if PathSeeker.DEBUG_NAVIGATION_PATHS:
			if not prevSuccess:
				DEBUG_MSG( "Failed to reach destination waypoint." )
			else:
				DEBUG_MSG( "Path finished" )

	def _isClose( self, p1, p2, threshold ):
		'''
		Check if two positions are close.
		@param p1 point 1.
		@param p2 point 2.
		@param threshold the threshold distance.
		'''
		diff = p1 - p2
		distSq = diff.x * diff.x + diff.z * diff.z

		return (distSq < (threshold * threshold))

	def _cleanupNavPathModels( self, player ):
		'''
		Remove any debug models attached to the player.
		@param player the player to clean up
		'''
		if (hasattr( self, "_debugNavPathModels" ) and
			(self._debugNavPathModels is not None)):
			for m in self._debugNavPathModels:
				player.delModel( m )
		self._debugNavPathModels = []

	def _loadDebugModels( self ):
		'''
		Start background loading of models used for debugging.
		'''
		if PathSeeker.DEBUG_NAVIGATION_PATHS:
			self._debugModel = None
			resourceList = ( PathSeeker.DEBUG_MODEL_NAME, )
			BigWorld.loadResourceListBG( resourceList,
				self._onDebugModelsLoaded )

	def _onDebugModelsLoaded( self, resourceRefs ):
		'''
		Callback for when debug resources have loaded.
		@param resourceRefs resources.
		'''
		if resourceRefs.failedIDs:
			ERROR_MSG( "Failed to load %s" % ( resourceRefs.failedIDs, ) )
		else:
			self._debugModel = resourceRefs[ PathSeeker.DEBUG_MODEL_NAME ]
