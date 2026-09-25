# --------------------------------------------------------------------------
# This is an Application Personality Script.  It contains classes to control
# and maintain various user interface components, such as the Direction
# Cursor settings and the console, followed by a small number of
# miscellaneous helper functions.  Finally a series of BigWorld Client
# callback functions are implemented that allow the game's 'personality' to
# be configured, executed and terminated.  These are the main methods to
# interact with the BigWorld Client engine.
# --------------------------------------------------------------------------

import time
import BigWorld
from Math import *
import math
from functools import partial
from Keys import *
import GUI
import types
import ResMgr
import Avatar
import Account
from GraphicsPresets import GraphicsPresets
from Helpers import PyGUI
__import__('__main__').PyGUI = PyGUI
import FDGUI
__import__('__main__').FDGUI = FDGUI
import weakref
import MenuScreenSpace
import AvatarModel
import PlayerModel
from Helpers.BWCoroutine import *
from Helpers import BWKeyBindings
from Helpers import Region
from bwdebug import *
import Listener
import CameraNode
import Weather
from GameData import FantasyDemoData
import PostProcessing
from WebScreen import WebScreen
import OpenAutomate
import Ripper

import BWReplay

import FDStrings.Login as LoginStrings

#Load-time XML file storage
underWaterDS = ResMgr.openSection( "system/post_processing/chains/underwater.ppchain" )

FIRST_PERSON_NEAR_CLIP_PLANE = 0.15
SHOW_ENTITY_IDS_BY_DEFAULT = False


# --------------------------------------------------------------------------
# Class:  DCSettings
# Description:
#	- Reads and stores direction cursor settings.
# --------------------------------------------------------------------------
class DCSettings:

	# --------------------------------------------------------------------------
	# Method:  __init__
	# Description:
	#	- Initialises all required attributes.
	# --------------------------------------------------------------------------
	def __init__(self):
		self.invertVerticalMovement = 0
		self.mouseSensitivity = 0
		self.mouseHVBias = 0
		self.maxPitch = 0
		self.minPitch = 0

	# -------------------------------------------------------------------------
	# Method:  load
	# Description:
	#	- Reads data taken from the BigWorld Client Configuration Script.
	# -------------------------------------------------------------------------
	def load(self, sect):
		self.invertVerticalMovement = sect.readBool('invertVerticalMovement',
													self.invertVerticalMovement)
		self.mouseSensitivity = sect.readFloat('mouseSensitivity',
											   self.mouseSensitivity)
		self.mouseHVBias = sect.readFloat('mouseHVBias', self.mouseHVBias)
		self.maxPitch = sect.readFloat('maxPitch', self.maxPitch)
		self.minPitch = sect.readFloat('minPitch', self.minPitch)

	# -------------------------------------------------------------------------
	# Method:  copy
	# Description:
	#	- Copies data from this class into another class.
	# -------------------------------------------------------------------------
	def copy(self, oth):
		self.__dict__.update(oth.__dict__)

###########################
# End of class DCSettings #
###########################



# -----------------------------------------------------------------------------
# Class: RDShare
# Description:
#	- Maintains all shared personality data.
# -----------------------------------------------------------------------------
class RDShare(Listener.Listenable):

	# -------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Initialises shared personality data.
	# -------------------------------------------------------------------------
	def __init__(self):
		Listener.Listenable.__init__( self )
		self.outsidePivotMaxDist = 0
		self.insidePivotMaxDist = 0
		self.reversePivotMaxDist = 0
		self.overridePivotMaxDist = 0

		self.useWoWMode = True
		self.mouseMoveThreshold = 5

		self.automaticAspectRatio = True

		self.currFov = 0
		self.fovs = [60,20]

		self.fixedMatrix = Matrix()

		self.cc = None
		self.flc = None
		self.fic = None
		self.frc = None

		# Indexes by which the above 4 cameras are referred to from the outside
		self.CURSOR_CAMERA = 0
		self.FLEXI_CAM = 1
		self.FIXED_CAMERA = 2
		self.FREE_CAMERA = 3

		self.gameCamIdx = 0		# for free camera mode
		self.cameraKeyIdx = 0

		self.firstPersonDCSettings = DCSettings()
		self.thirdPersonDCSettings = DCSettings()

		self.inside = 0

		self.console = None

		self.maxBandwidth = 20000 # default of FantasyDemo
		self.showIDs = SHOW_ENTITY_IDS_BY_DEFAULT

		self.spaceNameMap = {}
		self.deviceListeners = {}
		self.environmentChangeListeners = {}
		self.cameraSpaceChangeListeners = {}
		self.cameraChangeListeners = {}
		self.lastWeatherSpaceID = None
		self.cameraSpaceID = 0
		self.flyThroughMode = False

		self.selfDisconnect = False
		self.__flyThroughStartNodeName = 'camera node0'
		self.inGameFocusedComponent = None

		self.underWaterChain = None
		self.mainMenu = None

		# Skip menu
		self.skipMenu = False
		self.skipMode = "offline"
		self.skipMenuSpace = ""

		# window mode change limiting
		self.pendingUserWindowModeChange = False

	def init( self ):
		BigWorld.addWatcher( 'Debug/Max bandwidth per second',
			self.getMaxBps, self.setMaxBps )
		BigWorld.addWatcher( 'Debug/Show entity IDs',
			self.getShowIDs, self.setShowIDs )
		self.region = Region.Region()


	def fini( self ):
		BigWorld.delWatcher('Debug/Max bandwidth per second')
		self.region.fini()
		if hasattr( self, "waterListenerID" ):
			BigWorld.delWaterVolumeListener( self.waterListenerID )
		# unfortunately, we cannot have a weakref to a
		# [un]bound method. This is why we need to explicitly
		# break the cyclic references before exiting
		self.console.script.fini()
		del self.console
		self.selfDisconnect = False
		self.underWaterChain = None
		self.cc.source = None
		self.cc.target = None
		self.cc = None

	def initUnderwaterPP( self ):
		listener = self.onPostProcessingGraphicsSettingChanged
		PostProcessing.registerGraphicsSettingListener( listener )
		self.onPostProcessingGraphicsSettingChanged( BigWorld.getGraphicsSetting( "POST_PROCESSING_QUALITY" ) )


	def onPostProcessingGraphicsSettingChanged( self, optionIdx ):
		#print "onPostProcessingGraphicsSettingChanged", optionIdx
		if optionIdx == 0: #VERY HIGH
			self.underWaterChain = PostProcessing.load( underWaterDS )
		else:
			self.underWaterChain = None		


	def cameraWaterCallback(self, entering, volume):
		if entering == True:
			self.underwaterFogEmitter = BigWorld.addFogEmitter( (0,0,0), 10, -10, 100, 0x6060c0, False )
			if self.underWaterChain is not None:
				self.outOfWaterChain = PostProcessing.chain()
				PostProcessing.chain( self.underWaterChain )
		else:
			BigWorld.delFogEmitter( self.underwaterFogEmitter )
			if hasattr(self, "outOfWaterChain"):
				PostProcessing.chain( self.outOfWaterChain )
				del self.outOfWaterChain

	def initConsole(self):
		if self.console is None:
			# create fantasy demo console
			self.console = GUI.load("gui/fd_console.gui")
			self.console.script.active(True)
			self.console.script.showNow()

	def getMaxBps(self):
		return str(self.maxBandwidth)

	def setMaxBps(self, bps):
		self.maxBandwidth = int(bps)
		BigWorld.player().base.setBandwidthPerSecond(int(bps))

	def getShowIDs( self ):
		return self.showIDs

	def setShowIDs( self, value ):
		self.showIDs = self.watcherValueToBoolean( value )

	def watcherValueToBoolean( self, value ):
		result = value
		try:
			if value.lower() in ("true", "1"):
				result = True
			else:
				result = False
		except:
			pass
		return result

	def camera(self, idx):
		return (self.cc, self.flc, self.fic, self.frc)[ idx % 4 ]


	def baseFOV(self):
		return self.fovs[ self.currFov % len(self.fovs) ]


	def changeBaseFOV(self):
		self.currFov = self.currFov + 1
		self.currFov = self.currFov % len(self.fovs)
		self.fovs = [60,20]


	def updatePivotDist(self):
		self.cc.maxDistHalfLife = 1.5
		if self.overridePivotMaxDist > 0:
			self.cc.pivotMaxDist = self.overridePivotMaxDist
			self.cc.maxDistHalfLife = 0.15
		elif self.cc.reverseView:
			self.cc.pivotMaxDist = self.reversePivotMaxDist
		else: # m6rad changes
#		elif self.inside:
			self.cc.pivotMaxDist = self.insidePivotMaxDist
#		else:
#			self.cc.pivotMaxDist = self.outsidePivotMaxDist

	def toggleFlyThroughMode( self ):
		self.setFlyThroughMode( not self.flyThroughMode )
		return self.flyThroughMode

	def _runFlyThrough( self, cameraNode, loop = False ):
		"""
		Wrapper around BigWorld.FlyThroughCamera in case this code is being run against
		a client build that predates BigWorld.FlyThroughCamera
		"""
		if not hasattr( BigWorld, "FlyThroughCamera" ):
			BigWorld.runFlyThrough( cameraNode.name, loop )
			return
		camera = BigWorld.FlyThroughCamera( cameraNode )
		camera.loop = True
		BigWorld.camera( camera )

	def cancelFlyThrough( self ):
		"""
		Wrapper around BigWorld.cancelFlyThrough in case this code is being run against
		a client build that predates BigWorld.FlyThroughCamera, in which case
		BigWorld.cancelFlyThrough would not trigger the Personality.onFlyThroughFinished callback
		"""
		BigWorld.cancelFlyThrough()
		if not hasattr( BigWorld, "FlyThroughCamera" ):
			onFlyThroughFinished( None )

	def setFlyThroughMode( self, enabled ):
		if self.flyThroughMode == enabled:
			return

		if enabled:
			startNode = self.getFlightPathStartNode()
			if startNode is None:
				return
			self._runFlyThrough( startNode, True )
			self.flyThroughMode = enabled
			self.listeners.flyThroughModeActivated( enabled, None )
		else:
			self.cancelFlyThrough()


	def getFlightPathStartNode( self ):
		"""
		Returns the CameraNode UDO to start a FlyThroughCamera from, or None if no such UDO is loaded
		"""
		cameraNodes = [udo for udo in BigWorld.userDataObjects.values() if isinstance( udo, CameraNode.CameraNode )]
		startCamera = [cn for cn in cameraNodes if cn.name == self.__flyThroughStartNodeName]
		if len( startCamera ) != 1:
			if len( startCamera ) > 1:
				ERROR_MSG( "There are %d fly-through camera	start nodes.  Please make sure there is only 1" % (len(startCamera),))
			return None
		else:
			return startCamera[ 0 ]

	def flyThroughFinished( self, resultList ):
		if self.flyThroughMode:
			self.flyThroughMode = False
			self.listeners.flyThroughModeActivated( False, resultList )

########################
# End of class RDShare #
########################


# -----------------------------------------------------------------------------
# Class: LoginInfo
# Description:
#	- Stores login information.
# -----------------------------------------------------------------------------
class LoginInfo:
	def __init__(self):
		self.username = ''
		self.password = 'a'
		self.inactivityTimeout = 60
		self.transport = 'udp'

		try:
			self.username          = rds.userPreferences.readWideString('lastUsedAccountName')
			self.inactivityTimeout = rds.scriptsConfig._login._inactivityTimeout.asInt
			self.transport         = rds.scriptsConfig._login._transport.asString
			self.password          = rds.scriptsConfig._login._password.asString
		except:
			pass

##########################
# End of class LoginInfo #
##########################


############################################################################
# The following are miscellaneous functions/commands for internal use or   #
# use by other scripts.                                                    #
############################################################################

# BigWorld client personality script does not have "onInit"
def onInit( isReload ):
	INFO_MSG( "Personality init" )

DO_FULL_GC_DUMP = False

def onFini():
	'''
	Perform any final script tasks.

	At the moment this just dumps a log of memory leaks for debugging.
	'''
	INFO_MSG( "Personality fini" )

	if not BigWorld.consumerBuild():

		doFullDump = False
		import sys
		if ( DO_FULL_GC_DUMP ) or ( "enable-gc-dump" in sys.argv ):
			doFullDump = True

		import GarbageCollectionDebug
		numLeaks = GarbageCollectionDebug.gcDump( doFullDump )

		if numLeaks > 0:
			DEBUG_MSG( "Potential circular references" )
			DEBUG_MSG( "Number of leaks:", numLeaks )


# -----------------------------------------------------------------------------
# Method: v4col
# Description:
#		- Helper function to turn a vector3 into a full-on vector4 colour
# -----------------------------------------------------------------------------
def v4col(v3col, alpha = 255):
	return (v3col[0], v3col[1], v3col[2], alpha)


# These commands will be executed when the script is run by BigWorld.


# Stores whether or not the use key is down
isUseKeyDown = 0


# Set the camera type. Used to be in script_bigworld.cpp
def cameraType(idx):
	if rds.flyThroughMode:
		rds.cancelFlyThrough()

	newcam = rds.camera(idx)
	newcam.set(BigWorld.camera().matrix)
	BigWorld.camera(newcam)
	BigWorld.clearTextureStreamingViewpoints()
	BigWorld.registerTextureStreamingViewpoint( BigWorld.camera(), BigWorld.projection() )
	if idx < 3: rds.gameCamIdx = idx


# Change to the fixed camera, and set it to the given points
def setFixedCamera(camPos, lookPos):
	if not hasattr(camPos, 'x'):  camPos = Vector3(*camPos)
	if not hasattr(lookPos, 'x'): lookPos = Vector3(*lookPos)
	lookDir = lookPos - camPos
	lookDir.normalise()

	# could move out -1 * lookDir if we wanted no movement at all
	# in the fixed camera (-1 because of preferredPos setting)
	# like this is probably better for collision scene issues

	rds.fixedMatrix.lookAt(camPos, lookDir, (0,1,0))
	rds.fic.set(rds.fixedMatrix)

	rds.fixedMatrix.invert()

	if rds.flyThroughMode:
		rds.cancelFlyThrough()

	BigWorld.camera(rds.fic)
	BigWorld.clearTextureStreamingViewpoints()
	BigWorld.registerTextureStreamingViewpoint( BigWorld.camera(), BigWorld.projection() )
	rds.gameCamIdx = 2


def camera(idx):
	return rds.camera(idx)


# Change to the next camera
def nextCamera():
	curcam = BigWorld.camera()
	if curcam == rds.cc:
		newcam = 1
	elif curcam == rds.flc:
		newcam = 2
	else:
		newcam = 0
	cameraType(newcam)


# Set free camera mode
def freeCamera(ison):
	resetCameraOffset()
	if ison:
		cameraType(3)
	else:
		cameraType(rds.gameCamIdx)


# Set first person mode
def firstPerson(ison):
	rds.cc.firstPerson = ison

	if ison:
		dcSet = rds.firstPersonDCSettings
	else:
		dcSet = rds.thirdPersonDCSettings

	dc = BigWorld.dcursor()
	#dc.invertVerticalMovement = dcSet.invertVerticalMovement
	dc.mouseSensitivity       = dcSet.mouseSensitivity
	dc.mouseHVBias            = dcSet.mouseHVBias
	dc.maxPitch               = dcSet.maxPitch * math.pi / 180.0
	dc.minPitch               = dcSet.minPitch * math.pi / 180.0

	# stop any fov ramp in progress
	# (don't ask... app.cpp did this)
	p = BigWorld.projection()
	p.fov = p.fov


def setCursorCameraPivot(px, py, pz):
	rds.cc.pivotPosition = (px, py, pz)


def cameraDistanceOverride(val):
	rds.overridePivotMaxDist = val
	rds.updatePivotDist()


def cameraDistance(val):
	rds.insidePivotMaxDist = val
	rds.updatePivotDist()


def cameraTarget(entity):
	# Wow this function is so much easier than in C++!

	if entity == BigWorld.player():
		matrix = BigWorld.PlayerMatrix()
	else:
		matrix = entity.matrix

	rds.cc.target = matrix
	rds.flc.target = matrix


def fov(degs):
	BigWorld.projection().fov = degs * math.pi / 180.0


def changeFOV(degs, t):
	BigWorld.projection().rampFov(degs * math.pi / 180.0, t)


def initConsole():
	rds.initConsole()

def htmlChatWindow():
	# add to chat console
	return weakref.proxy(rds.fdgui.htmlChatWindow.script)

def chatConsole():
	# add to chat console
	if hasattr(rds, "fdgui") and rds.fdgui is not None:
		return weakref.proxy(rds.fdgui.chatWindow)

	assert rds.console is not None
	return weakref.proxy(rds.console)


def addChatMsg( id, msg, colour = FDGUI.TEXT_COLOUR_SYSTEM ):

	if BigWorld.player() and id == BigWorld.player().id:
		msg = 'you say: ' + msg
		colour = FDGUI.TEXT_COLOUR_YOU_SAY
	elif id != -1:
		msg = getEntityName(id) + ': ' + msg
		colour = FDGUI.TEXT_COLOUR_OTHER_WISHPER

	INFO_MSG( msg )

	cc = chatConsole()
	if cc:
		cc.script.addMsg( msg, colour )
		window = htmlChatWindow()
		window.addChatMsg( msg )

def appendChatMsg( id, msg, colour = FDGUI.TEXT_COLOUR_SYSTEM ):
	cc = chatConsole()

	if cc:
		if BigWorld.player() and id == BigWorld.player().id:
			msg = 'you say: ' + msg
			colour = FDGUI.TEXT_COLOUR_YOU_SAY
		elif id != -1:
			msg = getEntityName(id) + ': ' + msg
			colour = FDGUI.TEXT_COLOUR_OTHER_WISHPER

		cc.script.appendMsg( msg, colour )

def addMsg( msg, colour = FDGUI.TEXT_COLOUR_SYSTEM ):
	addChatMsg( -1, msg, colour )


def appendMsg( msg, colour = FDGUI.TEXT_COLOUR_SYSTEM ):
	appendChatMsg( -1, msg, colour )

def promptMessage( message, callbackFunc ):
	'''Prompt the message to the console
	'''
	def onEscape():
		rds.mainMenu.script.clearStatus()
		rds.mainMenu.script.pop()
		callbackFunc()

	rds.mainMenu.script.showPromptStatus( message, onEscape )

def getEntityName( id, forceShowID=False ):
	'''
	Get an identifying string for a given entity.
	@param id the entity id for which we want a name.
	@param includeID include the entity's ID in the name.
	@return name for the entity.
	'''
	# Get entity from id
	entity = BigWorld.entity( id )

	# Get name
	name = ""

	# No such entity
	if not entity:
		name = 'Nonexistent Entity'

	# No name attr
	elif not hasattr( entity, 'name' ):
		name = entity.__class__.__name__

	# It's a string attr
	elif type( entity.name ) == types.StringType:
		name = entity.name

	# Try as a callable attr
	elif callable( entity.name ):
		name = entity.name()

	# Append id in dev versions
	if forceShowID or rds.showIDs:
		name = name + " #" + repr( id )

	return name

# A couple of helper functions to add and remove key bindings.
def addBindingForAction( actionName, binding ):
	rds.keyBindings.addBindingForAction( actionName, binding )
	rds.keyBindings.buildBindList()
	rds.keyBindings.writePreferenceKeyBindings( rds.userPreferences )
	BigWorld.savePreferences()


def removeBindingForAction( actionName, binding ):
	rds.keyBindings.removeBindingForAction( actionName, binding )
	rds.keyBindings.buildBindList()
	rds.keyBindings.writePreferenceKeyBindings( rds.userPreferences )
	BigWorld.savePreferences()


def enableAutomaticAspectRatio( enable ):
	rds.automaticAspectRatio = enable
	rds.userPreferences.writeBool( "automaticAspectRatio", enable )
	_updateAutomaticAspectRatio()

def automaticAspectRatioEnabled():
	return rds.automaticAspectRatio

def _updateAutomaticAspectRatio():
	if rds.automaticAspectRatio and not BigWorld.isVideoWindowed():
		ratio = BigWorld.screenWidth() / BigWorld.screenHeight()
		BigWorld.changeFullScreenAspectRatio( ratio )


############################################################################
# The following functions implement the callbacks that BigWorld uses to    #
# initiate and maintain an application's 'personality'.                    #
############################################################################

# -----------------------------------------------------------------------------
# Method: init
# Description:
#	- The init function is called as part of the BigWorld Client
#	initialisation process.
#	- It receives the configuration script in a parsable format.
#	- This is the best place to configure all the application-specific
#		components, like initial Camera view, etc...
#	- init() creates a BigWorld Space and adds the parsed universe to it.
#	- It then creates a camera, configuring it using the values from the
#		appropriate xml data section.
#	- It also creates the Console class, again using the xml data.
# -----------------------------------------------------------------------------
def init(scriptsConfig, engineConfig, userPreferences, loadingScreenGUI = None):
	rds.userPreferences = userPreferences

	rds.middleMouseButtonDown = False
	rds.cameraCloseUpTrigger = 0.65

	rds.scriptsConfig = scriptsConfig

	rds.loadingScreen = loadingScreenGUI

	rds.keyBindings = BWKeyBindings.BWKeyBindings()

	# TODO: should be read by a module in scripts/common/GameData
	keyBindingData = ResMgr.openSection( "scripts/data/default_key_bindings.xml" )
	rds.keyBindings.readInDefaultKeyBindings( keyBindingData )

	if rds.userPreferences.has_key( "keyBindings" ):
		keyBindingData = rds.userPreferences._keyBindings
		rds.keyBindings.readInPreferenceKeyBindings( keyBindingData )

	rds.keyBindings.buildBindList()
	#rds.keyBindings.printBindList()

	# An action handler for FantasyDemo module level actions
	rds.fantasyDemoActionHandler = FantasyDemoActionHandler()
	rds.keyBindings.addHandler( rds.fantasyDemoActionHandler )

	# One for the DSLR module
	import DSLR
	rds.dslrActionHandler = DSLR.DSLRActionHandler()
	rds.keyBindings.addHandler( rds.dslrActionHandler )

	enableAutomaticAspectRatio( userPreferences.readBool( "automaticAspectRatio", True ) )

	actionToolTipsSection = ResMgr.openSection( "scripts/data/action_tooltips.xml" )
	rds.fdgui = FDGUI.FDGUI()
	rds.fdgui.setupGUI( actionToolTipsSection, rds.keyBindings )

	#setLanguage(scriptsConfig.readString('ui/language', 'english'))

	# read collision settings, default to old collision system
	rds.oldStyleCollision = scriptsConfig.readBool("physics/oldStyleCollision", True)

	cc = BigWorld.CursorCamera()
	cc.source = BigWorld.dcursor().matrix
	cc.target = BigWorld.PlayerMatrix()
	BigWorld.dcursor().yawReference = cc.invViewMatrix
	BigWorld.dcursor().minYaw = -2
	BigWorld.dcursor().maxYaw =  2

	cc.pivotPosition = scriptsConfig.readVector3(
		'camera/defTargetOffset', (0.0, 1.8, 0.0))

	rds.outsidePivotMaxDist = scriptsConfig.readFloat(
		'camera/maxDistanceFromPivot', cc.pivotMaxDist)
	rds.insidePivotMaxDist = scriptsConfig.readFloat(
		'camera/indoorDistanceFromPivot', rds.outsidePivotMaxDist)
	rds.reversePivotMaxDist = scriptsConfig.readFloat(
		'camera/faceDistanceFromPivot', rds.outsidePivotMaxDist)

	rds.useWoWMode = userPreferences.readBool('useWoWMode', rds.useWoWMode)
	rds.mouseMoveThreshold = scriptsConfig.readInt(
		'camera/mouseMoveThreshold', rds.mouseMoveThreshold)

	cc.pivotMaxDist = rds.outsidePivotMaxDist
	cc.pivotMinDist = scriptsConfig.readFloat(
		'camera/minDistanceFromPivot', cc.pivotMinDist)
	cc.terrainMinDist = scriptsConfig.readFloat(
		'camera/minDistanceFromTerrain', cc.terrainMinDist)
	cc.maxVelocity = scriptsConfig.readFloat(
		'camera/maxVelocity', cc.maxVelocity)
	cc.movementHalfLife = scriptsConfig.readFloat(
		'camera/movementHalfLife', cc.movementHalfLife)
	cc.turningHalfLife = scriptsConfig.readFloat(
		'camera/turningHalfLife', cc.turningHalfLife)

	rds.cc = cc
	rds.defaultPivotMaxDist = rds.outsidePivotMaxDist
	rds.defaultNearPlane = BigWorld.projection().nearPlane

	# flexi cam
	flc = BigWorld.FlexiCam()
	flc.target = cc.target
	flc.preferredPos = (0.0, 3.2, -2.5)
	flc.viewOffset = (0.0, 1.8, 0.0)
	flc.timeMultiplier = 8

	rds.flc = flc

	# fixed cam
	fic = BigWorld.FlexiCam()
	fic.target = rds.fixedMatrix
	fic.preferredPos = (0,0,-1)
	fic.viewOffset = (0,0,0)
	fic.timeMultiplier = 8

	rds.fic = fic

	# free cam
	rds.frc = BigWorld.FreeCamera()


	# compute matrix to translate camera position to near plane
	m = MatrixProduct()
	m.a = Matrix()
	m.a.setTranslate( (0, 0, BigWorld.projection().nearPlane) )
	m.b = rds.cc.invViewMatrix

	# hook up the cameras to water
	rds.waterListenerID = BigWorld.addWaterVolumeListener( m, rds.cameraWaterCallback )

	# start off with
	# cursor camera
	BigWorld.camera(cc)
	BigWorld.clearTextureStreamingViewpoints()
	BigWorld.registerTextureStreamingViewpoint( BigWorld.camera(), BigWorld.projection() )

	# now load direction
	# cursor details
	try:
		rds.thirdPersonDCSettings.load(engineConfig._directionCursor)
	except:
		pass

	try:
		rds.firstPersonDCSettings.copy(rds.thirdPersonDCSettings)
		rds.firstPersonDCSettings.load(scriptsConfig._dcFirstPersonOverrides)
	except:
		pass

	# make the console
	initConsole()

	# time of day when offline
	rds.offlineTimeOfDay = scriptsConfig.readString('offline/timeOfDay', '14:00')
	rds.offlineSpaces = None

	rds.lastWeatherSync = {}
	Weather.weather()

	# load the logo gui
	rds.logoGui = None

	#__import__('Helpers').alertsGui.instance.init()
	#__import__('Helpers').Inventory.instance.init()

	# for GDC 2010 - preload the spell effect
	#import FX
	#BigWorld.loadResourceListBG(FX.prerequisites("sfx/staff_spell.xml" ), partial( FX.getBufferedOneShotEffect, "sfx/staff_spell.xml", 10 ) )
	#BigWorld.loadResourceListBG(FX.prerequisites("sfx/staff_explosion.xml" ), partial( FX.getBufferedOneShotEffect, "sfx/staff_explosion.xml", 10 ) )
	#BigWorld.loadResourceListBG(FX.prerequisites("sfx/person_explosion.xml" ), partial( FX.getBufferedOneShotEffect, "sfx/person_explosion.xml", 10 ) )
	#BigWorld.loadResourceListBG(FX.prerequisites("sfx/air_explosion.xml" ), partial( FX.getBufferedOneShotEffect, "sfx/air_explosion.xml", 10 ) )
	#BigWorld.loadResourceListBG(FX.prerequisites("sfx/ground_explosion.xml" ), partial( FX.getBufferedOneShotEffect, "sfx/ground_explosion.xml", 10 ) )
	#BigWorld.loadResourceListBG(FX.prerequisites("sfx/staff_lightning.xml" ), partial( FX.getBufferedOneShotEffect, "sfx/staff_lightning.xml", 10 ) )

	# and we're done
	print 'fantasydemo personality selected.'

# -----------------------------------------------------------------------------
# Method: start
# Description:
#	- The start function is called after the BigWorld Client has initialised
#	and is used	to begin the game.
#	- Although it receives no data, it uses the shared personality data to
#	initiate the login process.
#	- Other instances may display an introduction or initiate some other game
#	flow process...
# -----------------------------------------------------------------------------
def start():
	import sys
	if len(sys.argv) >= 4 and sys.argv[1] == 'profile':
		# fantasydemo.exe -sa profile -sa spaces/highlands -sa gf8800
		runProfiler( sys.argv[2], sys.argv[3], True )
		return
	elif len(sys.argv) >= 5 and sys.argv[1] == 'soakTest':
		# fantasydemo.exe -sa soakTest -sa spaces/highlands -sa 30 -sa soakFile.csv
		runSoakTest( sys.argv[2], sys.argv[3], sys.argv[4], True )
		return
	elif len(sys.argv) >= 3 and sys.argv[1] == 'loadtimer':
		# fantasydemo.exe -sa loadtimer -sa spaces/highlands
		print "Starting load timer run ..."
		loadTimerStart( sys.argv[2] )
		return
	elif (len(sys.argv) == 3 or len(sys.argv) == 4) and sys.argv[1] == '-openautomate':
		OpenAutomate.startOpenAutomate()

	elif (len(sys.argv) >= 4) and (sys.argv[1] == 'skipmenu'):
		# Valid modes are "offline" and "online"
		rds.skipMode = sys.argv[2]

		# "offline" mode
		if ( rds.skipMode == "offline" ):
			# Get space name
			rds.skipMenuSpace = sys.argv[3]

			# Check if it's valid
			# enumOfflineSpaces returns a tuple (printName, name}
			# -> match "name"
			spaces = enumOfflineSpaces()
			found = False
			for space in spaces:
				if space[1] == rds.skipMenuSpace:
					INFO_MSG( "Skipping menu to open " + rds.skipMenuSpace )
					rds.skipMenu = True
					found = True
					break

			# Could not find
			if not found:
				ERROR_MSG( "Could not open " + rds.skipMenuSpace )

		# "online" mode
		elif ( rds.skipMode == "online" ):
			ERROR_MSG( "Skip mode for \"online\" is not yet implemented." )
			#ERROR_MSG( "Usage: fantasydemo.exe -sa skipmenu -sa online -sa host -sa username -sa password -sa realmName -sa characterName" )
			rds.skipMenu = False

		else:
			ERROR_MSG( "Skip mode must be \"offline\" or \"online\"." )
			ERROR_MSG( "Usage: fantasydemo.exe -sa skipmenu -sa offline -sa spaces/highlands" )
			rds.skipMenu = False

	# Done with arguments - start
	internalStart()


# -----------------------------------------------------------------------------
# Method: internalStart
# Description:
#	- The internalStart function is called after start has finished to begin 
#   the game.
#	- Although it receives no data, it uses the shared personality data to
#	initiate the login process.
#	- Other instances may display an introduction or initiate some other game
#	flow process...
# -----------------------------------------------------------------------------
def internalStart():
	BigWorld.worldDrawEnabled( False )
	rds.mainMenu = GUI.load( 'gui/main_menu.gui' )

	rds.advertisingScreen = None

	rds.li = LoginInfo()

	_showLogoScreen(False)
	_showLoadingBar(False)

	# Start up main menu if not in automate or skip mode
	if ( not OpenAutomate.openAutomateMode ) and ( not rds.skipMenu ):
		coSetMainMenuActive( True ).run()

	onRecreateDevice()
	BigWorld.callback(0.1, _testEngineFeatures)

	PostProcessing.init()
	rds.initUnderwaterPP()

	# Skip to a space
	if rds.skipMenu:
		if rds.skipMode == "offline":
			INFO_MSG( "Skipping.." )
			BigWorld.worldDrawEnabled( True )
			BigWorld.serverDiscovery.searching = False

			BigWorld.clearSpaces()
			BigWorld.callback(1.0, lambda: _exploreOffline( rds.skipMenuSpace ))
			_activateChatWindow()

		elif rds.skipMode == "online":
			ERROR_MSG( "Online skip not yet implemented" )
			MenuScreenSpace.init().run()
			coSetMainMenuActive( True ).run()

			# Partially implemented
			# Gets stuck on character selection?
			# TODO get from arguments
			'''skipHost=""
			skipLabel=""
			skipUsername=""
			skipPassword=""
			skipRealmName=""

			connectToServer( skipHost, skipLabel, skipUsername, skipPassword )

			BigWorld.player().selectedRealm = ""
			BigWorld.player().base.selectRealm( skipRealmName )

			try:
				yield BWWaitForCondition( lambda: BigWorld.player().selectedRealm == skipRealmName, timeout = 120 )
			except BWCoroutineTimeoutException, e:
				FantasyDemo.disconnectFromServer()
				return

			import FDGUI.CharacterSelectionPage
			rds.mainMenu.script.push( FDGUI.CharacterSelectionPage( rds.mainMenu.script ) )'''
		else:
			ERROR_MSG( "Invalid skip mode " + rds.skipMode )
			MenuScreenSpace.init().run()
			coSetMainMenuActive( True ).run()

		# Reset - user could log out and want to use menu
		#rds.skipMenu = False

_mainMenuActiveCount = 0
_mainMenuChanging = False

@BWCoroutine
def coSetMainMenuActive( active ):
	global _mainMenuActiveCount
	global _mainMenuChanging

	yield BWWaitForCondition( lambda: _mainMenuChanging == False )

	if active:
		_mainMenuActiveCount += 1
		if _mainMenuActiveCount == 1:
			_mainMenuChanging = True
			yield BWWaitForCoroutine( coStartMainMenu() )
			_mainMenuChanging = False
	else:
		_mainMenuActiveCount -= 1
		if _mainMenuActiveCount == 0:
			_mainMenuChanging = True
			yield BWWaitForCoroutine( coFinishMainMenu() )
			_mainMenuChanging = False



############################################################################
# Main menu, server discovery and login related functions.
############################################################################

@BWCoroutine
def coStartMainMenu():
	rds.mainMenu.script.active( True )
	rds.mainMenu.fader.alpha = 1.0
	rds.mainMenu.fader.reset()

	yield BWWaitForCoroutine( rds.mainMenu.script.coShowCharacterScreen( False, 0 ) )

	rds.mainMenu.script.restartMenu()

	logoFadeTime = _showLogoScreen( False )
	disableWorldDrawing()

	if not MenuScreenSpace.g_loaded:
		yield BWWaitForCoroutine( MenuScreenSpace.init() )

def quitGame():
	# When someone choose to exit when running from OpenAutomate they should just get back to the game
	if OpenAutomate.runFromOpenAutomate:
		OpenAutomate.setupOpenAutomateMainLoop(10, False, True).run()
		return
	_showLoadingBar(False)
	showAdvertisingScreen( 30.0, BigWorld.quit )

def _testEngineFeatures():
	allOkay = True
	for featureKey, active, options, desc, advanced, needsRestart, delayed in BigWorld.graphicsSettings():
		if options and not options[0][1]:
			allOkay = False
			feature = desc
			if options[0][0] == 'On' and options[1][0] == 'Off':
				addMsg('%s not supported (turning it off)' % feature)
			else:
				addMsg('%s not fully supported (using %s)' % (feature, options[active][0]))
	if allOkay:
		addMsg('Engine features fully supported on this system')


@BWCoroutine
def coFinishMainMenu():
	'''Clears the menu stack.
	'''
	gui = rds.mainMenu
	gui.fader.alpha = 0
	yield BWWaitForCoroutine( gui.script.coShowCharacterScreen( False, 0 ) )
	gui.script.active(False)

	try:
		yield BWWaitForCoroutine( MenuScreenSpace.fini(), timeout = 120 )
	except BWCoroutineTimeoutException:
		disconnectFromServer()
		return


def connectToServer( host, label, username, password = 'pass' ):
	message1 = 'Server: %s ' % label
	message2 = 'Account name: %s' % username

	rds.mainMenu.script.reset()
	rds.mainMenu.script.showProgressStatus( 'Connecting to %s...' % host )
	addMsg( message1 + message2 )

	if BigWorld.server() is not None:
		disconnectFromServer()

	rds.li.username = username
	rds.li.password = password 	
	BigWorld.serverDiscovery.searching = False

	def doConnect():
		BigWorld.clearSpaces()
		BigWorld.connect( host, rds.li, _connectionCallback )

	BigWorld.callback( 1.5, doConnect )


def enumOfflineSpaces():
	'''Enumerates all spaces listed in the space root
	directory (res/spaces). Returns a list of 2-tuples 
	containing (printName, name).
	'''
	# list spaces
	if rds.offlineSpaces is None:
		spacesRoot = 'spaces'
		rds.offlineSpaces = []
		for direct in ResMgr.openSection(spacesRoot).values():
			if direct.has_key('space.settings'):
				# since resmgr does not support
				name = '%s/%s' % (spacesRoot, direct.name)
				printName = name

				# if the printName can not be converted to unicode, we give it the value Invalid Characters
				# the space will still work, we just don't know how to display its name
				try:
					unicode(printName)
				except UnicodeDecodeError:
					printName = '%s/%s' % (spacesRoot,'<Invalid Characters>')

				if name not in FantasyDemoData.OFFLINE_MODE_IGNORED_SPACES:
					rds.offlineSpaces.append( (printName, name) )

	return rds.offlineSpaces


@BWCoroutine
def coExploreOfflineSpace( spaceDescriptor ):
	BigWorld.serverDiscovery.searching = False

	yield BWWaitForCondition( lambda: MenuScreenSpace.g_loaded )
	if BigWorld.server() is not None:
		disconnectFromServer()
	BigWorld.clearSpaces()
	BigWorld.callback(1.0, lambda: _exploreOffline( spaceDescriptor ))


def _exploreOffline(spaceName, doConnectionCallback = True):
	'''Callback triggered when the user choses a space from
	the offline spaces menu. Loads the space and run offline.
	'''
	message = 'Exploring offline space: %s' % spaceName
	addMsg( message )

	BigWorld.connect( '', '', _connectionCallback )
			
	startPosition = rds.scriptsConfig._player._startPosition.asVector3
	startDirection = rds.scriptsConfig._player._startDirection.asVector3
	try:
		ssect = ResMgr.openSection(spaceName + '/space.settings')
		startPosition = ssect._startPosition.asVector3
		startDirection = ssect._startDirection.asVector3
	except:
		pass

	playerModel = PlayerModel.defaultPlayerModel()

	etype = rds.scriptsConfig._player._class.asString
	BigWorld.createPlayerEntity( etype,
		startPosition, startDirection, 
		{'avatarModel':AvatarModel.pack( playerModel )})

	assert BigWorld.player() != None
	clientSpaceID = BigWorld.player().spaceID

	BigWorld.timeOfDay(rds.offlineTimeOfDay)

	try:
		BigWorld.addSpaceGeometryMapping( clientSpaceID, None, spaceName )
	except ValueError, e:
		errorMsg = 'Could not load space %s' % ( spaceName, )
		detailMsg = str( e )

		BigWorld.disconnect()
		BigWorld.clearLocalSpace( clientSpaceID )

		def onEscape():
			rds.mainMenu.script.clearStatus()
			rds.mainMenu.script.pop()
		rds.mainMenu.script.showPromptStatus( errorMsg, onEscape, detailMsg )
		return

	BigWorld.player().onChangeEnvironments( False )

@BWCoroutine
def coProceedToLevel( showLoadingScreen = True ):
	'''Put up the loading screen and wait for the level to load.
	'''
	if BigWorld.server() is None:
		disconnectFromServer()
		return

	if showLoadingScreen:
		_showLogoScreen( True, False )
		yield BWWaitForPeriod( 2.0 )

		yield BWWaitForCoroutine( coSetMainMenuActive( False ) )

	try:
		yield BWWaitForCondition( lambda: BWReplay.isLoaded() or
			(BigWorld.player() and BigWorld.player().inWorld), timeout = 120 )
	except BWCoroutineTimeoutException:
		disconnectFromServer()
		return

	def loadFinished():
		# connection may have been
		# cancelled half way through
		if BigWorld.server() is None:
			coSetMainMenuActive( True ).run()
		elif BigWorld.isEval() and not hasattr(rds, "notFirstTime"):
			rds.notFirstTime = True
			rds.fdgui.toggleHelp()

		_showLoadingBar( False )
		_showLogoScreen( False )

	if showLoadingScreen:
		_startChunkLoadingBar( loadFinished )
		_showLoadingBar( True )

	rds.selfDisconnect = False


def _connectionCallback( stage, status, serverMsg ):
	'''Callback triggered by BigWorld to report on the status of the connection.
	Logs the status in the console and update the GUI accordingly.
	'''
	if stage == BigWorld.STAGE_LOGIN:
		errorStatus = status not in [ 'LOGGED_ON', 'LOGGED_ON_OFFLINE' ]
		defaultMsg = serverMsg if serverMsg else 'Unknown server error'
		msgDict = dict( serverMsg = serverMsg, **rds.li.__dict__ )
		errorMsg = LoginStrings.LOGIN_ERROR_STRINGS.get( status, defaultMsg )
		errorMsg = errorMsg % msgDict

		detailMsg = LoginStrings.DETAIL_ERROR_STRINGS.get( status )

		if detailMsg:
			detailMsg = detailMsg % msgDict

		if errorStatus:
			rds.mainMenu.script.showPromptStatus( errorMsg, coHandleDisconnectionFromServer( serverMsg ).run, detailMsg )
		else:
			rds.mainMenu.script.showProgressStatus( errorMsg )
		addMsg( errorMsg )

	elif stage == BigWorld.STAGE_DATA:
		if status == 'LOGGED_ON_OFFLINE' or status == 'REPLAY':
			coProceedToLevel( (not OpenAutomate.openAutomateMode) and (not rds.skipMenu) ).run()
		else:
			postConnectedToServer()

	elif stage == BigWorld.STAGE_DISCONNECTED:
		coHandleDisconnectionFromServer( serverMsg ).run()

def postConnectedToServer():
	assert BigWorld.player() is not None

	# If we're already an avatar, then go straight into the game
	if isinstance( BigWorld.player(), Avatar.PlayerAvatar ):
		coProceedToLevel().run()
		return

	assert isinstance( BigWorld.player(), Account.Account )

	rds.mainMenu.script.connectedToServer()

@BWCoroutine
def coHandleDisconnectionFromServer( message = None ):
	if message is None:
		message = "Disconnected from Server"

	rds.fdgui.handleDisconnectionFromServer()
	rds.setFlyThroughMode( False )
	_showLoadingBar(False)
	_showLogoScreen( True, False )

	_deactivateChatWindow()

	rds.mainMenu.fader.alpha = 1.0
	yield BWWaitForCoroutine( rds.mainMenu.script.coShowCharacterScreen( False, 2.0 ) )

	if not OpenAutomate.openAutomateMode:
		rds.mainMenu.script.showPromptStatus( message )

		yield BWWaitForPeriod( 2.0 )

		while _mainMenuActiveCount > 0:
			yield BWWaitForCoroutine( coSetMainMenuActive( False ) )

		if rds.selfDisconnect:
			addMsg('Client disconnected itself from server')
		else:
			addMsg('Client lost connection to server')
	else:
		yield BWWaitForPeriod( 2.0 )
		#called from coSetMainMenuActive
		BigWorld.worldDrawEnabled( True )

	BigWorld.clearSpaces()
	MenuScreenSpace.clear()

	yield BWWaitForPeriod( 0.5 )

	if not OpenAutomate.openAutomateMode:
		yield BWWaitForCoroutine( coSetMainMenuActive( True ) )

	_showLogoScreen( False, False )
	disableWorldDrawing()


def disconnectFromServer():
	'''Disconnect client from server.
	'''

	if BWReplay.isLoaded():
		BWReplay.pausePlayback()

	if BigWorld.server() is not None:
		rds.selfDisconnect = True

		# Temporary solution until there is an official function that
		# gets rid of the proxy on the base.
		if BigWorld.player() is not None:
			try:
				BigWorld.player().base.logOff()
			except:
				pass

		_showLogoScreen( True, False )

		BigWorld.disconnect()

	if BWReplay.isLoaded():
		BWReplay.stopPlayback()
		BigWorld.clearSpaces()

	Weather.weather().toggleRandomWeather( False )



############################################################################
# The following functions implement a loading screen overlay to hide the
# initial chunk loading phase.
############################################################################

def disableWorldDrawing():
	BigWorld.worldDrawEnabled(False)
	if BigWorld.player() and hasattr(BigWorld.player(), 'hud') and BigWorld.player().hud:
		GUI.delRoot(BigWorld.player().hud)

def enableWorldDrawing():
	BigWorld.worldDrawEnabled(True)
	if BigWorld.player() and hasattr(BigWorld.player(), 'hud') and BigWorld.player().hud:
		GUI.addRoot(BigWorld.player().hud)

def _exitAdvertisingScreen( callback ):
	if rds.advertisingScreen != None:
		GUI.delRoot(rds.advertisingScreen)
		rds.advertisingScreen = None
		callback()

def showAdvertisingScreen( time, callback ):
	if BigWorld.isEval():
		if rds.advertisingScreen == None:
			rds.advertisingScreen = GUI.load("gui/advertising_graphic.gui")
			disableWorldDrawing()
			rds.advertisingScreen.script.isActive = True
			rds.advertisingScreen.script.active(True)
			rds.advertisingScreen.script.onEscape = partial(_exitAdvertisingScreen, callback)
			GUI.addRoot(rds.advertisingScreen)
			BigWorld.callback( time-0.001, rds.advertisingScreen.script.onEscape )
	else:
		callback()


def _showLogoScreen( active, fadeIn = True ):
	'''Shows/hide the BigWorld logo screen.
	'''
	if fadeIn:
		fadeTime = rds.loadingScreen.fader.speed
	else:
		fadeTime = 0.0

	if active:
		rds.loadingScreen.fader.value = 1.0
		BigWorld.callback( fadeTime, disableWorldDrawing )
	else:
		rds.loadingScreen.fader.value = 0.0
		enableWorldDrawing()

	# If we're fading out, allow mouse clicks into the menu etc immediately.
	# Otherwise capture input.
	rds.loadingScreen.focus = active
	rds.loadingScreen.moveFocus = active

	BigWorld.callback( fadeTime, partial( rds.loadingScreen.script.active, active ) )
	if not fadeIn:
		rds.loadingScreen.fader.reset()

	return fadeTime



def _showLoadingBar(active):
	'''Shows/hide the loading bar.
	'''
	rds.loadingScreen.bar.visible  = active
	rds.loadingScreen.back.visible = active
	if not active:
		rds.loadingScreen.script.cancel()


def _recommendSettings():
	# if timed out and a lower graphics setting exists then print out a message
	# to indicate this, unless the user cancelled the loading screen.

	if rds.loadingScreen.fader.value == 0.0:
		return

	presets	= GraphicsPresets()
	doNotify = False

	if presets.selectedOption == -1:
		doNotify = True
	else:
		for i in range(0, len(presets.entryNames)):
			presetMsg = presets.entryNames[i]
			if presetMsg != "Low" and presets.selectedOption == i:
				doNotify = True
				break

	if doNotify == True:
		addMsg("FantasyDemo loading timeout please try a lower graphics setting")


def _startChunkLoadingBar(finishedCallback):
	'''Starts the chunk loaing progress bar.
	'''
	if rds.loadingScreen == None:
		rds.loadingScreen = GUI.load('gui/loading_screen.gui')

	rds.loadingScreen.script.setProgress(0)
	rds.loadingScreen.script.reset(0)

	def _finishedLoading( timedOut = False ):
		if timedOut:
			_recommendSettings()
		BigWorld.worldDrawEnabled(True)

		_activateChatWindow()

		rds.loadingScreen.script.reset(0)
		finishedCallback()

	# Loading progress bar measures first 500 metres
	rds.loadingScreen.script.start(500.0, _finishedLoading)
	addMsg('Loading World Data')

############################################################################
# The following functions implement a feature that times the loading of a
# space.
############################################################################

def loadTimerStart( spaceName ):
	# Start loading requested space without loading screen
	startTime = time.time()
	_exploreOffline( spaceName, False )
	_showLogoScreen( False )

	# Start the callback chain to do the timing
	print "Load timer: Processing space '", spaceName, "'"
	BigWorld.callback( 1.0, partial( _loadTimerTick, spaceName, startTime ) )

def _loadTimerTick( spaceName, startTime ):
	s = BigWorld.spaceLoadStatus()
	print "Load timer: Space load status =", s
	if s < 1.0:
		# Tick
		BigWorld.callback( 0.1, partial( _loadTimerTick, spaceName, startTime ) )
	else:
		# End
		timeNow = time.time()
		elapsed = timeNow - startTime
		_loadTimerFinish( spaceName, elapsed )

def _loadTimerFinish( spaceName, elapsedTime ):
	filepath = "../../res/fantasydemo/load_timer.txt"
	print "Load timer: Space loaded in", elapsedTime, "seconds. Writing results to", filepath
	try:
		result = "benchmark:%s:result name:elapsedTime:value:%f:\n" % (spaceName, elapsedTime)
		with open( filepath, 'a' ) as f:
			f.writelines( result )
	except IOError:
		print "ERROR: failed to write load timer results to ", filepath
	BigWorld.quit()

############################################################################
# The following functions implement the automatic profiling
############################################################################

def runProfiler( spaceName, csvPrefix, exitOnComplete):
	# Start loading requested space without loading screen
	_exploreOffline( spaceName, False )
	_showLogoScreen( False )

	def _loadTick( spaceName, csvPrefix):
		if _isSpaceLoading() == True or _isFlightPathLoaded() == False:
			BigWorld.callback(1.0,partial(_loadTick,spaceName, csvPrefix))
		else:
			BigWorld.callback(1.0,partial(_runProfilerStart, spaceName, csvPrefix, exitOnComplete ) )

	# Puting 30 second wait before testing for loading.
	# The above loading test is not accurate enough for all situations
	# and FPS automated tests are routinely starting before the level is
	# loaded causing it to abort.
	BigWorld.callback(30.0,partial(_loadTick, spaceName, csvPrefix))

def _runProfilerStart ( spaceName, csvPrefix, exitOnComplete ):
	rds.flyThroughMode = True
	#self.listeners.flyThroughModeActivated( True, None )
	BigWorld.runProfiler('camera node0', 1 , csvPrefix, exitOnComplete)

def runSoakTest( spaceName, soakMinutes, soakStatsFile = None, fixedFrameStep = False ):
	# Start loading requested space without loading screen
	_exploreOffline( spaceName, False )
	_showLogoScreen( False )

	def _loadTick():
		if _isSpaceLoading() == True or _isFlightPathLoaded() == False:
			BigWorld.callback(1.0, _loadTick )
		else:
			BigWorld.callback(1.0, partial(_runSoakTest, spaceName, float(soakMinutes), soakStatsFile, fixedFrameStep ) )

	# Puting 30 second wait before testing for loading.
	# The above loading test is not accurate enough for all situations
	# and FPS automated tests are routinely starting before the level is
	# loaded causing it to abort.
	BigWorld.callback(30.0,_loadTick)

def _runSoakTest( spaceName, soakMinutes, soakStatsFile = None, fixedFrameStep = False ):
	rds.flyThroughMode = True
	#self.listeners.flyThroughModeActivated( True, None )
	BigWorld.runSoakTest('camera node0', soakMinutes, soakStatsFile, fixedFrameStep )

def _isFlightPathLoaded( ):
	"""
	Returns True if the CameraNode UDO to start a Profile or SoakTest from is loaded.
	"""
	cameraNodes = [udo for udo in BigWorld.userDataObjects.values() if isinstance( udo, CameraNode.CameraNode )]
	startCamera = [cn for cn in cameraNodes if cn.name == 'camera node0']
	if len( startCamera ) != 1:
		if len( startCamera ) > 1:
			ERROR_MSG( "There are %d fly-through camera start nodes.  Please make sure there is only 1" % (len(startCamera),))
		return False
	else:
		return True

def _isSpaceLoading( ):
	return (BigWorld.isLoadingChunks() == True or 
		BigWorld.spaceLoadStatus() < 1)

# -----------------------------------------------------------------------------
# Method: onChangeEnvironments
# Description:
#	- This is called automatically when player moves from inside to outside
#	environment, or vice versa.
#	- It should be used to adapt any personality related data (eg, camera
#	position/nature, etc).
# -----------------------------------------------------------------------------
def onChangeEnvironments(inside):
	rds.inside = inside
	rds.updatePivotDist()
	for listener in rds.environmentChangeListeners.keys():
		listener(inside)


def addChangeEnvironmentsListener(listener):
	rds.environmentChangeListeners[listener] = ''


def delChangeEnvironmentsListener(listener):
	try:
		if 'rds' in globals():
			del rds.environmentChangeListeners[listener]
	except:
		pass


def onGeometryMapped(spaceID, spacePath):
	rds.spaceNameMap[spaceID] = spacePath
	onChangeEnvironments(False)
	online = BigWorld.server() if BigWorld.server() else 'offline'
	print 'Entering space: %s (server: %s)' % (spacePath, online)


def spaceName(spaceID):
	try:
		return rds.spaceNameMap[spaceID]
	except KeyError:
		return ""


# -----------------------------------------------------------------------------
# Method: onCameraSpaceChange
# Description:
#	- This is called automatically when the camera moves from one space to
#	another.
#	- The space ID and space.settings datasection is passed in to this function
# -----------------------------------------------------------------------------
def onCameraSpaceChange(spaceID, spaceSettings):
	rds.cameraSpaceID = spaceID
	for listener in rds.cameraSpaceChangeListeners.keys():
		listener(spaceID,spaceSettings)


def addCameraSpaceChangeListener(listener):
	rds.cameraSpaceChangeListeners[listener] = ''


def delCameraSpaceChangeListener(listener):
	try:
		if 'rds' in globals():
			del rds.cameraSpaceChangeListeners[listener]
	except:
		pass


# -----------------------------------------------------------------------------
# Method: onCameraChange
# Description:
#	- This is called automatically when the camera is remove d
#	- The space ID and space.settings datasection is passed in to this function
# -----------------------------------------------------------------------------
def onCameraChange(oldCamera):
	for listener in rds.cameraChangeListeners.keys():
		listener(oldCamera)


def addCameraChangeListener(listener):
	rds.cameraChangeListeners[listener] = ''


def delCameraChangeListener(listener):
	try:
		if 'rds' in globals():
			del rds.cameraChangeListeners[listener]
	except:
		pass

# -----------------------------------------------------------------------------
# Method: onRecreateDevice
# Description:
#	- This is called automatically when the D3D device is reset.
# -----------------------------------------------------------------------------
def onRecreateDevice():
	'''Called by BigWorld whenever the graphics device is reset
	(usually, after a screen resise or switching full screen mode).
	'''
	_updateAutomaticAspectRatio()

	for listener in rds.deviceListeners.keys():
		listener.onRecreateDevice()

	PyGUI.onRecreateDevice()

	rds.loadingScreen.script.doLayout( None )
	rds.mainMenu.script.doLayout( None )

	if rds.advertisingScreen is not None:
		rds.advertisingScreen.script.doLayout( None )



def addDeviceListener(listener):
	rds.deviceListeners[listener] = ''


def delDeviceListener(listener):
	try:
		if 'rds' in globals():
			del rds.deviceListeners[listener]
	except:
		pass

# -----------------------------------------------------------------------------
# Method: onFlyThroughFinished
# Description:
#	- This is called when the camera fly-through has completed
# -----------------------------------------------------------------------------
def onFlyThroughFinished(resultList):
	rds.flyThroughFinished(resultList)


# -----------------------------------------------------------------------------
# Method: enableEnvironmentSync
# Description:
#	- This method is a demo-only and enables environment synchronisation.
#	Server time of day and weather updates will be displayed on the client.
# -----------------------------------------------------------------------------
def enableEnvironmentSync():
	if hasattr( BigWorld, 'setEnvironmentSync' ):
		BigWorld.setEnvironmentSync( True )
		addMsg("Environment sync enabled")
		spaceID = BigWorld.player().spaceID
		BigWorld.player().cell.resyncServTime( spaceID )
		import Weather
		Weather.weather().summon( rds.lastWeatherSync[spaceID], \
											immediate = True, serverSync = True )


# -----------------------------------------------------------------------------
# Method: disableEnvironmentSync
# Description:
#	- This method is a demo-only and disables environment synchronisation.
#	Server time of day and weather updates will be ignored.
# -----------------------------------------------------------------------------
def disableEnvironmentSync():
	if hasattr( BigWorld, 'setEnvironmentSync' ):
		BigWorld.setEnvironmentSync( False )
		addMsg("Environment sync disabled")


# -----------------------------------------------------------------------------
# Method: onWeatherChange
# Description:
#	- This method is called when the weather space data is updated from the
#	server.  This feature is demo-only and is not compiled into the consumer
#	client release build.
# -----------------------------------------------------------------------------
def onWeatherChange( spaceID, weather ):
	import Helpers.ConsoleCommands

	rds.lastWeatherSync[spaceID] = weather

	#If this is a weather change for the current space, then update the
	#weather gracefully (i.e. not immediate)
	if rds.cameraSpaceID == spaceID:
		try:
			apply = BigWorld.getEnvironmentSync()
		except KeyError:
			apply = True

		if apply:
			import Weather
			Weather.weather().summon( weather, immediate = False, serverSync = True )


# -----------------------------------------------------------------------------
# Method: fini
# Description:
#	- The fini function is called when the client is about to shutdown.  It
#		should be used to clean up the game.
# -----------------------------------------------------------------------------
def fini():
	global rds

	if BigWorld.server() is not None:
		if not BWReplay.isPlaying:
			try:
				BigWorld.player().base.logOff()
			except:	pass

	BigWorld.clearSpaces()
	MenuScreenSpace.clear()
	
	BigWorld.savePreferences()

	if rds.fdgui is not None:
		rds.fdgui.fini()
	if rds.mainMenu is not None:
		rds.mainMenu.script.fini()
		rds.mainMenu = None

	PyGUI.fini()

	import Weather
	Weather.fini()

	PostProcessing.fini()

	rds.fini()

	del rds


# -----------------------------------------------------------------------------
# Method: onTimeOfDayLocalChange
# Description:
#	- This is called automatically when Time of Day changes on the client
#	- It should only be used to sync game time from client to server
# -----------------------------------------------------------------------------
def onTimeOfDayLocalChange( gameTimeInHrs, secondsPerGameHour ):
	if not hasattr( BigWorld, 'getEnvironmentSync' ) or \
		not BigWorld.getEnvironmentSync():
		return

	if secondsPerGameHour > 0.0:
		gameSecondsPerSecond = 3600.0/secondsPerGameHour
	else:
		gameSecondsPerSecond = 0.0
	gameTimeInSeconds = gameTimeInHrs * 3600.0

	try:
		if BigWorld.server() is not None and \
				BigWorld.server() != "":
			BigWorld.player().cell.syncServTime(
				BigWorld.player().spaceID,
				gameTimeInSeconds, gameSecondsPerSecond )
	except:
		pass


# -----------------------------------------------------------------------------
# Method: handleKeyEvent
# Description:
#	- This is called automatically when a key is pressed.
# -----------------------------------------------------------------------------
def handleKeyEvent( event ):
	down = event.isKeyDown()
	#check for system event
	if down and event.key == KEY_F4 and event.isAltDown():
		if BigWorld.player() != None:
			try:
				BigWorld.player().base.logOff()
			except:	pass

		_quitGame()
		return True
	elif down and event.key == KEY_RETURN and event.isAltDown():
		def finishWindowModeChange():
			rds.pendingUserWindowModeChange = False

		# user-triggered window mode change (Alt+Enter).
		# prevent accidental repetition of this expensive operation if held down.
		if not rds.pendingUserWindowModeChange:
			rds.pendingUserWindowModeChange = True
			BigWorld.changeVideoMode( BigWorld.videoModeIndex(), not BigWorld.isVideoWindowed() )
			BigWorld.callback(0.1, finishWindowModeChange)

		return True

	PyGUI.handleKeyEvent( event )
	handled = GUI.handleKeyEvent( event )

	if handled:
		#remove focus from the inGameFocusedComponent so that if it grabs keyboard (mozilla) it will release the grab
		if rds.inGameFocusedComponent:
			rds.inGameFocusedComponent.setKeyFocus(False)
		return True
	#in this case, the GUI didn't grab the focus, therefore we cancel the GUI key focus status
	focusedComponent = PyGUI.getFocusedComponent()
	if down and event.isMouseButton() and focusedComponent is not None:
		if not hasattr( focusedComponent.script, "allowAutoDefocus" ) or focusedComponent.script.allowAutoDefocus():
			PyGUI.setFocusedComponent( None )

	#focused component is after GUI as a GUI element might be closer to the camera than the
	#inGameFocusedComponent
	if rds.inGameFocusedComponent:
		handled = rds.inGameFocusedComponent.handleKeyEvent( event )
		if handled:
			return True

	# try the camera
	cam = BigWorld.camera()
	if cam is not None:
		handled = cam.handleKeyEvent( event )

	if handleChatKeyEvent( event ):
		return True
		
	if not handled and BWReplay.isLoaded():
		BWReplay.handleKeyEvent( event )
	return handled

def handleChatKeyEvent( event ):
	# scroll player chat console if we can
	down = event.isKeyDown()
	chatConsole = rds.fdgui.chatWindow
	if chatConsole and chatConsole.script.isActive:
		if down and (event.key == KEY_RETURN and not event.isModifierDown()):
			# check if the in game menu is active
			if not rds.fdgui.inGameMenu.script.isActive and not chatConsole.script.editing:
				chatConsole.script.edit(1)  # if already editing then
				return True		    #  it'll catch return above
		elif down and (event.key == KEY_SLASH and not event.isModifierDown()):
			# check if the in game menu is active
			if not rds.fdgui.inGameMenu.script.isActive and not chatConsole.script.editing:
				chatConsole.script.edit(1,initialEditText = "/")  # if already editing then
				return True		    #  it'll catch return above
		elif down and (event.key == KEY_ESCAPE and not event.isModifierDown()) and chatConsole.script.isShowing():
			chatConsole.script.hideNow()
			return True
	return False

# -----------------------------------------------------------------------------
# Method: handleInputLangChangeEvent
# Description:
#	- This is called automatically when the current input language has changed.
# -----------------------------------------------------------------------------
def handleInputLangChangeEvent():
	return PyGUI.handleInputLangChangeEvent()

# -----------------------------------------------------------------------------
# Method: handleIMEEvent
# Description:
#	- This is called automatically when the IME UI state has changed.
# -----------------------------------------------------------------------------
def handleIMEEvent( event ):
	return PyGUI.handleIMEEvent( event )



class FantasyDemoActionHandler( BWKeyBindings.BWActionHandler ):

	# handle the change camera mode key event
	@BWKeyBindings.BWKeyBindingAction( "CameraKey" )
	def cameraKey( self, isDown ):
		if isDown:
			handleCameraKey()

	@BWKeyBindings.BWKeyBindingAction( "DisconnectFromServer" )
	def disconnectFromServer( self, isDown ):
		if isDown and BigWorld.server() is not None and BigWorld.player().inWorld:
			disconnectFromServer()
			return True
		else:
			return False

	@BWKeyBindings.BWKeyBindingAction( "CancelLoading" )
	def cancelLoading( self, isDown ):
		if isDown and BigWorld.player() is not None and not BigWorld.worldDrawEnabled():
			addMsg("User cancelled loading screen.")
			BigWorld.worldDrawEnabled(True)
			_showLogoScreen(False)
			_showLoadingBar(False)

			_activateChatWindow()

			return True
		else:
			return False

	@BWKeyBindings.BWKeyBindingAction( "EnableEnvironmentSync" )
	def enableEnvironmentSync( self, isDown ):
		if isDown:
			enableEnvironmentSync()
			return True
		else:
			return False

	@BWKeyBindings.BWKeyBindingAction( "DisableEnvironmentSync" )
	def disableEnvironmentSync( self, isDown ):
		if isDown:
			disableEnvironmentSync()
			return True
		else:
			return False

	@BWKeyBindings.BWKeyBindingAction( "ChatWindow" )
	def toggleChatWindow( self, isDown ):
		chatConsole = rds.fdgui.chatWindow
		if isDown and chatConsole:
			if chatConsole.script.isShowing():
				chatConsole.script.hideNow()
			else:
				chatConsole.script.edit(1)
			return True
		else:
			return False


	@BWKeyBindings.BWKeyBindingAction( "DefaultWebScreens" )
	def defaultWebScreens( self, isDown ):	
		if isDown:
			for entity in BigWorld.entities.values():
				if isinstance(entity, WebScreen):
					entity.setDefault()	

# -----------------------------------------------------------------------------
# Method: setCursorCameraSource
# Description:
#	- This is called to override the source matrix provider for the cursor camera.
# -----------------------------------------------------------------------------
def setCursorCameraSource( source ):
	rds.cc.source = source

# -----------------------------------------------------------------------------
# Method: handleCameraKey
# Description:
#	- This is called in response to the 'next camera' key being pressed.
# -----------------------------------------------------------------------------
def handleCameraKey( forceToStandardCamera = False ):

	if isinstance( BigWorld.player(), Avatar.PlayerAvatar) and BigWorld.player().firstPerson:
		resetCameraOffset()
		cameraDistanceOverride(rds.defaultPivotMaxDist)
		BigWorld.projection().nearPlane = rds.defaultNearPlane
		BigWorld.player().toggleFirstPersonMode(False)
		return

	if forceToStandardCamera:
		rds.cameraKeyIdx = 0
	else:
		rds.cameraKeyIdx = (rds.cameraKeyIdx + 1) % 3

	pivotMaxDist = 2
	if isinstance( cameraTarget, Ripper.PlayerRipper ):
		pivotMaxDist = 3.5

	changeCameraType( pivotMaxDist )

def changeCameraType( pivotMaxDist, enableOrbitCameraTargetting = False ):
	'''
	Toggle between three different camera types depending on what
	rds.cameraKeyIdx is set to.
	Following target, orbiting target or detached.
	@param pivotMaxDist max distance of the camera pivot.
	@param disableOrbitCameraTargetting set to True to disable the targetting
		system while in orbit camera mode.
	'''
	

	# Enable targeting system
	BigWorld.target.isEnabled = 1

	if rds.cameraKeyIdx == 0:
		rds.cc.inaccuracyProvider = None
		rds.cc.reverseView = False
		rds.updatePivotDist()
		cameraType( rds.CURSOR_CAMERA )

	elif rds.cameraKeyIdx == 1:
		cameraType( rds.CURSOR_CAMERA )

		# Disable targeting system
		if not enableOrbitCameraTargetting:
			BigWorld.target.clear()
			BigWorld.target.isEnabled = 0

		# Enable orbit camera
		v1 = Vector4LFO()
		v1.waveform = 'SAWTOOTH'
		v1.period = 20.0
		v1.amplitude = (3.141592654*2.0)
		v2 = Vector4(1,0,0,0)
		v = Vector4Product()
		v.a=v1
		v.b=v2
		rds.cc.inaccuracyProvider=v
		rds.cc.pivotMaxDist = pivotMaxDist
		rds.cc.maxDistHalfLife = 1.5

	elif rds.cameraKeyIdx == 2:
		# Free camera
		cameraType( rds.FREE_CAMERA )
		resetCameraOffset()
		rds.cc.inaccuracyProvider=None
		rds.cc.reverseView = False
		rds.updatePivotDist()

# -----------------------------------------------------------------------------
# Method: handleMouseEvent
# Description:
#	- This is called automatically when a mouse event is generated.
# -----------------------------------------------------------------------------
def handleMouseEvent( event ):

	# try the gui
	handled = PyGUI.handleMouseEvent( event )
	if not handled:
		handled = GUI.handleMouseEvent( event )
	if handled:
		return True

	# try replay controller
	if BWReplay.isLoaded() and BWReplay.handleMouseEvent( event ):
		return True

	# try the camera
	player = BigWorld.player()
	camMouseMove = True
	if isinstance( player, Avatar.PlayerAvatar ) and not getattr( player, "inMouseMove", True ):
		camMouseMove = False
	if camMouseMove is True:
		cam = BigWorld.camera()
		handled = cam.handleMouseEvent( event )

	if BigWorld.camera() != rds.frc and (isinstance( player, Avatar.PlayerAvatar ) and not player.inWebScreenMode()):
		if rds.middleMouseButtonDown and hasattr(rds.cc.source,'yaw'):
			msens = BigWorld.dcursor().mouseSensitivity * BigWorld.projection().fov / 1.04719755 #60 degrees
			newYaw = rds.cc.source.yaw + event.dx * BigWorld.dcursor().mouseHVBias * msens
			if BigWorld.dcursor().invertVerticalMovement:
				newPitch = rds.cc.source.pitch + event.dy * (1.0 - BigWorld.dcursor().mouseHVBias) * msens
			else:
				newPitch = rds.cc.source.pitch - event.dy * (1.0 - BigWorld.dcursor().mouseHVBias) * msens

			if newPitch > BigWorld.dcursor().maxPitch:
				newPitch = BigWorld.dcursor().maxPitch
			elif newPitch < BigWorld.dcursor().minPitch:
				newPitch = BigWorld.dcursor().minPitch

			# set the camera yaw and pitch
			rds.cc.source.setRotateYPR((newYaw, newPitch, rds.cc.source.roll))
			# we want to make the player 'looking' at the same direction as the camera
			BigWorld.dcursor().yawPitch(BigWorld.dcursor().yaw, newPitch)

		elif hasattr(rds, 'dYaw'):
			# fix the camera offset based on current player direction
			msens = BigWorld.dcursor().mouseSensitivity * BigWorld.projection().fov / 1.04719755 #60 degrees
			if BigWorld.dcursor().invertVerticalMovement:
				newPitch = rds.cc.source.pitch + dy * (1.0 - BigWorld.dcursor().mouseHVBias) * msens
			else:
				newPitch = rds.cc.source.pitch - dy * (1.0 - BigWorld.dcursor().mouseHVBias) * msens
			if newPitch > BigWorld.dcursor().maxPitch:
				newPitch = BigWorld.dcursor().maxPitch
			elif newPitch < BigWorld.dcursor().minPitch:
				newPitch = BigWorld.dcursor().minPitch

			rds.cc.source.setRotateYPR((BigWorld.dcursor().yaw + rds.dYaw,
										newPitch,
										rds.cc.source.roll))

		# don't try to move camera if player
		# is not the standard Player Avatar.
		if isinstance(BigWorld.player(), Avatar.PlayerAvatar):
			if event.dz != 0:
				clicks = event.dz/120.0	# add 20% for each notch... or something
				nextDist = math.exp(math.log(rds.cc.targetMaxDist) - clicks*math.log(1.2))
			if event.dz > 0:
				if nextDist < 0.5 and rds.cc.pivotMaxDist > 0.75:
					nextDist = 0.5	# don't go to first person until smoothly moved in close
				if nextDist >= 0.5:
					cameraDistanceOverride(nextDist)
					if nextDist <= rds.cameraCloseUpTrigger:
						BigWorld.projection().nearPlane = FIRST_PERSON_NEAR_CLIP_PLANE
				else:
					if player and player.inWorld and not player.firstPerson:
						player.toggleFirstPersonMode(True)
			elif event.dz < 0:
				if nextDist > 15.0: nextDist = 15.0
				if player and player.inWorld and hasattr( player, 'firstPerson' ) and player.firstPerson:
					if player.toggleFirstPersonMode(False):
						resetCameraOffset()
				else:
					cameraDistanceOverride(nextDist)
				if nextDist > rds.cameraCloseUpTrigger:
					BigWorld.projection().nearPlane = rds.defaultNearPlane

	if player and player.inWorld and hasattr(player, 'handleMouseEvent'):
		player.handleMouseEvent( event )

	if rds.middleMouseButtonDown:
		return 1

	return 0


# -----------------------------------------------------------------------------
# Method: resetCameraOffset
# Description:
#	- Reset the camera facing at the back of player
# -----------------------------------------------------------------------------
def resetCameraOffset():
	if id(rds.cc.source) != id(BigWorld.dcursor().matrix):
		rds.cc.source = BigWorld.dcursor().matrix
	if hasattr(rds, 'dYaw'):
		delattr(rds, 'dYaw')


# -----------------------------------------------------------------------------
# Method: resetCamera
# Description:
#	- Reset the camera
# -----------------------------------------------------------------------------
def resetCamera():
	resetCameraOffset()
	cameraDistanceOverride(rds.defaultPivotMaxDist)
	BigWorld.projection().nearPlane = rds.defaultNearPlane
	player = BigWorld.player()
	if player is not None:
		player.toggleFirstPersonMode(False)


# -----------------------------------------------------------------------------
# Method: handleAxisEvent
# Description:
#	- This is called automatically when an axis event is generated.
# -----------------------------------------------------------------------------
def handleAxisEvent( event ):
	# try the gui
	handled = GUI.handleAxisEvent( event )

	cam = BigWorld.camera()
	if cam is not None and handled is False:
		handled = cam.handleAxisEvent( event )

	return handled


def _activateChatWindow():
	rds.console.script.active(False)

	chatConsole = rds.fdgui.chatWindow
	if chatConsole:
		chatConsole.script.active(True)

def _deactivateChatWindow():
	rds.console.script.active(True)

	chatConsole = rds.fdgui.chatWindow
	if chatConsole:
		chatConsole.script.clear()
		chatConsole.script.active(False)




############################################################################
# Resource Updater notification handlers								   #
############################################################################

# -----------------------------------------------------------------------------
# Method: onResUpdateDownloadBegin
#
# A download has started, aiming to bring the given version point to the
# given version number. The download will occur in the background, even
# if these resources are required to enable entities, i.e. required to
# receive player data from the server. The first 3 elements of the
# progressV4Provider will indiciate the progress of the download:
# x: version number currently being downloaded
# y: files progress within current version number
# z: byte progress within file
# Note: If through script action, directly or indirectly, resources
# need to be loaded in the main from a non-root version point that is
# not up-to-date, then the main thread will block until those resources have
# been downloaded. The game will not progress except for processing messages
# from the server. This would be very bad! However, since scripts should
# never be loading resources in the main thread anyway - for the relatively
# small loading pause that would result - avoiding this is no extra burden.
# -----------------------------------------------------------------------------
def onResUpdateDownloadBegin(version, point, progressV4Provider):
	print 'onResUpdateDownloadBegin', version, point

# -----------------------------------------------------------------------------
# Method: onResUpdateDownloadEnd
#
# A download signalled above has ended. There may be a short time
# (up to one frame) when progressV4Provider.x is -1 before this function
# is called.
# Note: onResUpdateAutoRelaunch might be called before this function
# if an auto relaunch is going to occur.
# -----------------------------------------------------------------------------
def onResUpdateDownloadEnd(version, point, progressV4Provider):
	print 'onResUpdateDownloadEnd', version, point

# -----------------------------------------------------------------------------
# Method: onResUpdateLoadin
#
# It is time to begin loading in the updated resources in the client.
# Since the client doesn't yet have this capability for some resources,
# for now we must relaunch the client here. But give the user some
# notice first. (If we don't disconnect after a few minutes, the server
# will kick us off.)
# -----------------------------------------------------------------------------
def onResUpdateLoadin():
	print 'onResUpdateLoadin'
	BigWorld.callback(30, relaunchNow)

# The user has had enough time to prepare for the relaunch, so do it
def relaunchNow():
	try:
		BigWorld.player().base.logOff()
	except:	pass

	print 'Relaunching now'
	BigWorld.resUpdateInstallAndRelaunch()

# -----------------------------------------------------------------------------
# Method: onResUpdateAutoRelaunch
#
# We logged in but didn't enable entities / create a player, because
# out resources were out of date. We now have the new resources and they
# have been installed. The client is going to relaunch so it can use them
# as soon as this call returns.
# Note: onResUpdateDownloadBegin might not yet have been received if the update
# was very small or was a rollback. If it was received, then the corresponding
# onResUpdateDownloadEnd might not yet have been received before this call.
# -----------------------------------------------------------------------------
def onResUpdateAutoRelaunch():
	print 'onResUpdateAutoRelaunch'


def create(type):
	player = BigWorld.player()
	return BigWorld.createEntity(type, player.spaceID, 0, player.position, (0,0,0), {})


# ------------------------------------------------------------------------------
# Section: Macro expansion
# ------------------------------------------------------------------------------

# These are the python console macro expansions supported by FantasyDemo
PYTHON_MACROS = {
	"p":"BigWorld.player()",
	"t":"BigWorld.target()",
	"B":"BigWorld",
	"G":"doppleganger()",
	"a":"BigWorld.createEntity(\"Avatar\", BigWorld.player().spaceID, 0, BigWorld.player().position,(0,0,0),{})",
	"r":"BigWorld.entity(BigWorld.createEntity(\"Ripper\", BigWorld.player().spaceID, 0, BigWorld.player().position,(0,0,0),{}))",
	"s":"BigWorld.createEntity(\"Seat\", BigWorld.player().spaceID, 0,BigWorld.player().position,(0,0,0),{\"seatType\":1})",
	"e":"BigWorld.createEntity(\"Effect\", BigWorld.player().spaceID, 0,BigWorld.player().position,(0,0,BigWorld.player().yaw),{\"effectType\":6})",
	"o":"BigWorld.createEntity(\"Effect\", BigWorld.player().spaceID, 0,BigWorld.player().position,(0,0,0),{\"effectType\":3})",
	"S":"BigWorld.createEntity(\"Effect\", BigWorld.player().spaceID, 0,BigWorld.player().position,(0,0,0),{\"effectType\":4})",
	"v":"BigWorld.createEntity(\"Effect\", BigWorld.player().spaceID, 0,(-79.4,78.6,298.4),(0,0,0),{\"effectType\":6})",
	"V":"BigWorld.createEntity(\"VideoScreen\", BigWorld.player().spaceID, 0, BigWorld.player().position,(0,0,0),{})",
	"A":"m=BigWorld.Model('sets/items/xbow_bolt.model'); m.position=(0,1.2,-5); m.yaw = -1.55; BigWorld.player().addModel(m); h=BigWorld.Homer(); h.target=BigWorld.player().model; h.offset=(0,1.2,0); h.speed=1; h.turnRate=1; h.tripTime=8"
}

import re

# Implementation for BWPersonality.expandMacros() callback
def expandMacros( line ):

	# Glob together the keys from the macros dictionary into a pattern
	patt = "\$([%s])" % "".join( PYTHON_MACROS.keys() )

	def repl( match ):
		return PYTHON_MACROS[ match.group( 1 ) ]

	return re.sub( patt, repl, line )


rds = RDShare()
rds.init()
