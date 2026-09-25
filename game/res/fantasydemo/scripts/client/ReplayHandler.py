import FantasyDemo
import FDGUI.Minimap
import MenuScreenSpace
import BWReplay
import GUI
import Avatar
import Keys
from Math import *
from Helpers.BWCoroutine import *
from Helpers import collide
from Helpers import Caps
import math

from Helpers import BWKeyBindings
from Helpers.BWKeyBindings import BWKeyBindingAction

class ReplayHandler( BWKeyBindings.BWActionHandler ):

	def __init__( self ):
		BWKeyBindings.BWActionHandler.__init__( self )
		self.gui = FantasyDemo.rds.fdgui.replayWindow
		self.updateHz = BWReplay.getUpdateHz()
		self.mouseEnabled = True
		self.followingEntity = None
		self.isFirstStart = True
		self.lastFollowingEntityID = None


	def onLoadStart( self ):
		if self.isFirstStart:
			FantasyDemo.freeCamera( True )
			BigWorld.camera().spaceID = BWReplay.spaceID()

			FantasyDemo.camera( FantasyDemo.rds.CURSOR_CAMERA).spaceID = \
				BWReplay.spaceID()
			FantasyDemo.camera( FantasyDemo.rds.FLEXI_CAM ).spaceID = \
				BWReplay.spaceID()
			FantasyDemo.camera( FantasyDemo.rds.FIXED_CAMERA ).spaceID = \
				BWReplay.spaceID()
			FantasyDemo.camera( FantasyDemo.rds.FREE_CAMERA ).spaceID = \
				BWReplay.spaceID()

			try:
				spaceName = FantasyDemo.rds.spaceNameMap[ BWReplay.spaceID() ]
				settings = spaceName + '/space.settings'
				BigWorld.loadResourceListBG( (settings, ), self.setupCamera )
	
				FantasyDemo.rds.keyBindings.addHandler( self )
			except KeyError:
				# Stop replay and return to the main menu if no space name in
				# spaceNameMap. Mostly this means the replay file is corrupt.
				FantasyDemo.addMsg( 'Replaying error: no space data loaded' )
				BWReplay.stopPlayback()



	def setupCamera( self, resourceRef ):
		ssect = resourceRef.values()[0]
		startPosition = ssect._startPosition.asVector3
		startDirection = ssect._startDirection.asVector3

		startMatrix = Matrix()
		startMatrix.lookAt( startPosition, startDirection, (0,1,0))
		BigWorld.camera().set( startMatrix )

		FantasyDemo.rds.cameraKeyIdx = 0
		self.setupCameraType()

		# Targetting stuff
		BigWorld.target.exclude = self.followingEntity
		self.enableMouseTargetting()
		self.targetCaps = [ Caps.CAP_CAN_HIT ]
		BigWorld.target.caps( Caps.CAP_CAN_HIT )
		self.minAimScore = 0.0
		self.maxAimScore = 0.99
		self.minimapColour = (64,64,255,255)


	def enableMouseTargetting( self ):
		if not hasattr( self, "mouseTargettingMatrix" ):
			self.mouseTargettingMatrix = BigWorld.MouseTargettingMatrix()
		BigWorld.target.source = self.mouseTargettingMatrix
		BigWorld.target.selectionFovDegrees = 5.0
		BigWorld.target.deselectionFovDegrees = 8.0


	def onLoadFinished( self ):
		if self.isFirstStart:
			BigWorld.setCursor( BigWorld.dcursor() )
			GUI.mcursor().visible = True
			GUI.mcursor().clipped = False

			FantasyDemo.rds.fdgui._root.visible = True
			FantasyDemo.rds.fdgui.offlineIndicator.visible = \
						(BigWorld.server() == "")
			FantasyDemo.rds.fdgui.minimap.m.script.component.viewpoint = \
						BigWorld.camera().invViewMatrix
			FantasyDemo.rds.fdgui.replayWindow.script.active( True )
			# TODO: Figure out why chat window still has mouse,
			# even though not visible
			FantasyDemo.rds.fdgui.chatWindow.script.active( False )

			FDGUI.Minimap.onChangeEnvironments( False )

			self.isFirstStart = False


	def onPostTick( self, currentTick, totalTicks ):
		if currentTick == 0:
			self.onLoadStart()
		elif currentTick == 1:
			self.onLoadFinished()

		if (currentTick > 1):

			self._checkFollowingEntity()

		if not self.gui.script.isDraggingSlider:
			self.gui.slider.script.maxValue = totalTicks
			self.gui.slider.script.value = currentTick
			self.gui.slider.script.onValueChanged( currentTick )


	def _checkFollowingEntity( self ):
		# We have a following entity and
		# it has been destroyed or died
		if ((self.followingEntity is not None) and
			(self.followingEntity.isDestroyed or
			self.followingEntity.inDeadState)):
			self._onFollowingEntityDead()

		# We do not have a following entity
		# But we had one before - check if it has been re-created
		if ((self.followingEntity is None) and
			(self.lastFollowingEntityID is not None)):
			self._checkFollowingEntityAlive()


	def _onFollowingEntityDead( self ):
		'''
		Check if the entity we were following has been destroyed or died.
		Then detach the camera if it has.
		@note entities are also destroyed if you rewind to before they were
			created.
		'''
		#print "entity destroyed"
		self.lastFollowingEntityID = self.followingEntity.id
		self.lastCameraKeyIdx = FantasyDemo.rds.cameraKeyIdx
		self._onEntityClicked( None )


	def _checkFollowingEntityAlive( self ):
		'''
		Check if the entity we were following has come back to life.
		Then re-attach to it if it has. Eg. you rewind.
		'''
		# Get the entity from the ID
		try:
			entity = BigWorld.entities[ self.lastFollowingEntityID ]

			# Check if it's alive
			if (entity is not None and not entity.inDeadState):
				#print "entity revived"

				self.lastFollowingEntityID = None

				# Do not snap/reset camera to follow the entity
				# eg. if you are watching from the free camera from
				# above and
				# then rewind - keep the camera in the same position
				FantasyDemo.rds.cameraKeyIdx = self.lastCameraKeyIdx
				self._onEntityClicked( entity, False )

		except KeyError:
			pass


	def onFinishedPlayback( self ):
		FantasyDemo.rds.fdgui.onPlayerAvatarLeaveWorld( self )
		if BWReplay.isPlaying:
			BWReplay.setSpeedScale( 1.0 )
			self.gui.speedScale.text = "x1"

		# Cleanup stuff on exit
		FantasyDemo.rds.keyBindings.removeHandler( self )

		self._onEntityClicked( None )
		self._restoreCameraDefaults()
		

	def onReplayMetaData( self, metaData ):
		for key, value in metaData.items():
			print "Replay metadata %s = %s\n" % (key, value)
		
		
	def onPlayerStateChange( self, playerEntity, hasBecomePlayer ):
		"""
		This callback is called when an entity transitions between being a
		player and not being a player.

		@param playerEntity 	The player entity.
		@param hasBecomePlayer  If True, the entity has become a player,
								otherwise it has become a non-player.
		"""
		if hasBecomePlayer:
			print( "(%s %d) has become a player" %
				(playerEntity.__class__.__name__, playerEntity.id))
		else:
			print( "(%s %d) has become a non-player" %
				(playerEntity.__class__.__name__, playerEntity.id))


	def onPlayerAoIChange( self, playerEntity, entity, hasEnteredAoI ):
		"""
		This callback is called when an entity enters/leaves a player entity's
		AoI.

		@param playerEntity 	The player entity.
		@param entity 			The entity that is entering/leaving the AoI.
		@param hasEnteredAoI	If True, the entity has entered the AoI,
								otherwise it has left the AoI.
		"""
		if hasEnteredAoI:
			print( "(%s %d) has entered AoI of player (%s %d)" %
				(entity.__class__.__name__, entity.id,
				playerEntity.__class__.__name__, playerEntity.id))
		else:
			print( "(%s %d) has left AoI of player (%s %d)" %
				(entity.__class__.__name__, entity.id,
				playerEntity.__class__.__name__, playerEntity.id))


	def onProgress( self, stage, status, message ):
		if ((stage == BigWorld.STAGE_LOGIN) or
				(stage == BigWorld.STAGE_DISCONNECTED)):
			self.onFinishedPlayback()

		if stage == BigWorld.STAGE_DATA:
			# Header has been loaded get our updateHz
			self.updateHz = BWReplay.getUpdateHz()

		elif stage == BigWorld.STAGE_DISCONNECTED:
			if BigWorld.server() != "":
				# We may have disconnected else where (menus), so verify
				# BigWorld.server() is set to ""
				return
		FantasyDemo._connectionCallback( stage, status, message )

	def _restoreCameraDefaults( self ):
		'''
		Reset the camera back to following the player.
		'''

		BigWorld.camera().spaceID = 0

		FantasyDemo.camera( FantasyDemo.rds.CURSOR_CAMERA ).spaceID = 0
		FantasyDemo.camera( FantasyDemo.rds.FLEXI_CAM ).spaceID = 0
		FantasyDemo.camera( FantasyDemo.rds.FIXED_CAMERA ).spaceID = 0
		FantasyDemo.camera( FantasyDemo.rds.FREE_CAMERA ).spaceID = 0

		FantasyDemo.rds.cc.source = BigWorld.dcursor().matrix
		FantasyDemo.rds.cc.target = BigWorld.PlayerMatrix()

		FantasyDemo.handleCameraKey( forceToStandardCamera = True )

	def onError( self, error ):
		'''
		Called when the replay has an error.
		'''
		FantasyDemo.addMsg( 'Replay error: %s' % error )
		FantasyDemo.promptMessage( error, BWReplay.stopPlayback )
		
	def onFinish( self ):
		'''
		Called when the recording has reached the end.
		Not if it has been stopped part way.
		'''
		BWReplay.stopPlayback()

	def followEntity( self, entityID ):
		'''
		Make the camera follow a given entity.
		@param entityID the entity to follow,
		'''
		try:
			entity = BigWorld.entities[ entityID ]

			if (entity is not None):
				self._onEntityClicked( entity )
				return True
		except KeyError:
			pass

		return False

	@BWKeyBindingAction( "CameraKey" )
	def cameraKey( self, isDown ):
		'''
		Switch between camera types.
		Following, orbit and free.
		'''
		if isDown:
			FantasyDemo.rds.cameraKeyIdx = \
				(FantasyDemo.rds.cameraKeyIdx + 1) % 3
			self.setupCameraType()

	def setupCameraType( self ):
		'''
		Setup camera in follow, orbit or free mode.
		'''

		# Cannot follow if we have no target entity or
		# the entity has died or been destroyed
		# So we have only free camera mode
		if self.followingEntity is None:
			FantasyDemo.rds.cameraKeyIdx = 2

		pivotMaxDist = 2
		if isinstance( self.followingEntity, Avatar.Avatar ):
			if self.followingEntity.vehicle is not None:
				pivotMaxDist = 3.5

		FantasyDemo.changeCameraType( pivotMaxDist, True )

	@BWKeyBindingAction( "LeftMouseButton" )
	def targetKey( self, isDown ):
		'''
		Set the camera target to follow on key release.
		@param isDown True if the key is pressed.
		'''
		if not isDown:
			type, target = self._getMouseCollidePos()
			if type == collide.COLLIDE_ENTITY:
				self._onEntityClicked( target )

	def _onEntityClicked( self, target, snapCameraToEntity=True ):
		'''
		Setup following a target.
		@param target the entity to start following. Or set to None to stop
		following.
		@param snapCameraToEntity set to true if you want to switch the camera
			mode to follow the entity (ie. switch out of free or orbit mode).
		'''

		# We only follow Avatars
		# otherwise we need to change checking Avatar.inDeadState
		# in onPostTick
		if (target is not None) and (not isinstance( target, Avatar.Avatar )):
			return

		self.followingEntity = target

		# Do not allow targetting what we are already targetting
		# (or clear this if we are stopping following)
		BigWorld.target.exclude = self.followingEntity

		# Start following
		if self.followingEntity is not None:
			FantasyDemo.rds.cc.target = self.followingEntity.matrix
			FantasyDemo.rds.fdgui.minimap.m.script.component.viewpoint = \
				BigWorld.camera().invViewMatrix

			if self.followingEntity.model is not None:
				self.cameraHeight = self.followingEntity.model.height
			else:
				self.cameraHeight = 1.0
			FantasyDemo.setCursorCameraPivot( 0.0, self.cameraHeight, 0.0 )

			if snapCameraToEntity:
				FantasyDemo.rds.cameraKeyIdx = 0

		# Set camera
		self.setupCameraType()

	def _getMouseCollidePos( self ):
		'''
		Collide the mouse's position with scene.
		@return the collision type and the target that was hit.
		'''
		mp = GUI.mcursor().position
		collisionType, target = collide.cameraCollide( mp.x, mp.y )
		return ( collisionType, target )

	@BWKeyBindingAction( "RightMouseButton" )
	def moveKey( self, isDown ):
		self.mouseEnabled = not isDown

		if self.mouseEnabled:
			BigWorld.setCursor( GUI.mcursor() )
		else:
			BigWorld.setCursor( BigWorld.dcursor() )
		GUI.mcursor().visible = self.mouseEnabled
		GUI.mcursor().clipped = not self.mouseEnabled


	def handleKeyEvent( self, event ):
		# Check key state against key bindings.
		FantasyDemo.rds.keyBindings.callActionForKeyState( event.key )
		return False

	def handleMouseEvent( self, event ):
		# Check key state against key bindings.
		if self.mouseEnabled:
			return True
		else:
			return False


@BWCoroutine
def coPlayRecording( url, publicKeyPath = "replay-sign.pubkey",
		destinationPath = "", volatileInjectionPeriod = -1 ):
	
	BigWorld.serverDiscovery.searching = 0

	if BigWorld.server() is not None:
		raise ValueError( "A connection or replay already exists" )
		
	yield BWWaitForCondition( lambda: MenuScreenSpace.g_loaded )
	BigWorld.disconnect()
	BigWorld.clearSpaces()

	def playRecording():
		FantasyDemo.addMsg( 'Playing recording: %s' % url )

		def onReadKey( resourceRefs ):
			if publicKeyPath in resourceRefs.failedIDs:
				FantasyDemo._connectionCallback( BigWorld.STAGE_LOGIN,
					"REPLAY_FAILED",
					'Could not load public key for verifying replays' )

				return

			try:
				FantasyDemo._connectionCallback( BigWorld.STAGE_LOGIN,
					"LOGGED_ON_OFFLINE",
					'Playback Mode' )
				BWReplay.startPlayback( url,
					resourceRefs[publicKeyPath].asBinary,
					ReplayHandler(), destinationPath, volatileInjectionPeriod )
			except Exception as e:
				FantasyDemo._connectionCallback( BigWorld.STAGE_LOGIN,
					"REPLAY_FAILED",
					"Replay failed to start: %s" % e )

		BigWorld.loadResourceListBG( [publicKeyPath], onReadKey )

	BigWorld.callback( 1.0, playRecording )


