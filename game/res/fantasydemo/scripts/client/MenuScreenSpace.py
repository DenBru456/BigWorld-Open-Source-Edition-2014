
import BigWorld
import ResMgr
import Math
import math

import CameraNode

from MenuScreenAvatar import MenuScreenAvatar

from GameData import FantasyDemoData

from Helpers.BWCoroutine import *

MENU_SPACE_RESPATH = "spaces/menu_space"
MENU_CAMERA_NAME_PREFIX = "MenuCamera_"

g_menuSpaceID = None
g_menuCamera = None

g_loaded = False


@BWCoroutine
def init():
	global g_loaded
	assert not g_loaded

	global g_menuSpaceID
	g_menuSpaceID = BigWorld.createLocalSpace()
	BigWorld.addSpaceGeometryMapping( g_menuSpaceID, None, MENU_SPACE_RESPATH )

	_initCamera()

	try:
		yield BWWaitForCondition( lambda: BigWorld.spaceLoadStatus() == 1.0 and realmNodesLoaded(), timeout=120.0 )
	except BWCoroutineTimeoutException:
		if BigWorld.spaceLoadStatus() == 1.0:
			print "Not enough camera and avatar nodes for all realms"
		else:
			print "Menu space took too long to load, continuing. Artifacts may occur."

	g_loaded = True


def clear():	
	global g_menuSpaceID
	
	if g_menuSpaceID != None:
		BigWorld.clearLocalSpace( g_menuSpaceID )
		g_menuSpaceID = None
		
		
@BWCoroutine
def fini():
	global g_menuSpaceID
	global g_menuCamera
	global g_loaded

	if g_menuSpaceID != None and not g_loaded:
		yield BWWaitForCondition( lambda: g_loaded )

	g_loaded = False

	if g_menuCamera == BigWorld.camera():
		BigWorld.camera( None )
	g_menuCamera = None

	clear()


def menuCameraNodes():
	cameraNodes = [ i for i in BigWorld.userDataObjects.values() if isinstance( i, CameraNode.CameraNode ) ]
	return dict( [ (i.name, i) for i in cameraNodes if i.name.startswith( MENU_CAMERA_NAME_PREFIX ) ] )


def menuAvatars():
	return dict( [ (i.realm, i) for i in BigWorld.entities.values() if isinstance( i, MenuScreenAvatar ) ] )


def realmNodesLoaded():
	numRealms = len( FantasyDemoData.REALMS )
	return len( menuCameraNodes() ) >= numRealms and len( menuAvatars() ) >= numRealms


def setRealmCamera( realm ):

	# Find the camera
	cameraNodes = menuCameraNodes()
	
	if len(cameraNodes) == 0:
		print "ERROR: setRealmCamera: there are no valid camera nodes available."
		return
	
	try:
		node = cameraNodes[ MENU_CAMERA_NAME_PREFIX + realm ]
	except KeyError:
		print "ERROR: No menu space realm info for realm '%s'." % realm
		node = cameraNodes.values()[0]
		
	# Set the transform and FOV
	m = Math.Matrix()
	m.setRotateYPR( (node.yaw, node.pitch, node.roll) )
	m.translation = node.position
	m.invert()
	g_menuCamera.set( m )
	
	BigWorld.projection().fov = math.radians( node.fov )



def setRealmAvatarModel( realm, modelInfo ):

	avatars = menuAvatars()
	if len(avatars) == 0:
		print "ERROR: setRealmAvatarModel: there are no MenuScreenAvatar's available."
		return
	
	try:
		ent = avatars[ realm ]
	except KeyError:
		print "ERROR: No MenuScreenAvatar for realm '%s'." % realm
		ent = avatars.values()[0]
	
	ent.setModel( modelInfo )


def _initCamera():
	global g_menuCamera

	if not isinstance( g_menuCamera, BigWorld.FreeCamera ):
		g_menuCamera = BigWorld.FreeCamera()

	g_menuCamera.fixed = True
	m = Math.Matrix()
	m.setRotateYPR( (0,0,0) )
	m.translation = (50, 2, 50)
	m.invert()
	g_menuCamera.set( m )
	g_menuCamera.spaceID = g_menuSpaceID

	BigWorld.camera( g_menuCamera )
	BigWorld.clearTextureStreamingViewpoints()
	BigWorld.registerTextureStreamingViewpoint( BigWorld.camera(), BigWorld.projection() )






