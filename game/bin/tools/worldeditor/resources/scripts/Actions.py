import WorldEditor
import ResMgr
from WorldEditorDirector import bd

# ------------------------------------------------------------------------------
# Section: Default Action execution
# ------------------------------------------------------------------------------

class OptionSet:
	"""This class is used to implement action handlers that sets an option based
	on a simple value."""

	def __init__( self, path, value ):
		self.path = path
		self.value = value

	def __call__( self ):
		WorldEditor.setOption( self.path, self.value )

class OptionSetPlus( OptionSet ):
	"""This class is used to implement action handlers that sets an option based
	on a simple value."""

	def __init__( self, path, value, postFunction ):
		OptionSet.__init__( self, path, value )
		self.postFunction = postFunction

	def __call__( self ):
		OptionSet.__call__( self )
		self.postFunction( self.value )

class OptionToggle:
	"""This class is used to implement action handlers that toggles an option."""

	def __init__( self, path, postFunction = None ):
		self.path = path
		self.postFunction = postFunction

	def __call__( self ):
		oldValue = WorldEditor.getOptionInt( self.path )
		newValue = not oldValue
		WorldEditor.setOptionInt( self.path, newValue )
		if self.postFunction:
			self.postFunction( newValue )
			

class OptionSetFunction:
	"""This class is used to implement action handlers that sets an option based
	on a simple function."""

	def __init__( self, path, fn ):
		self.path = path
		self.fn = fn

	def __call__( self ):
		WorldEditor.setOption( self.path, self.fn() )

def defaultActionExecute( name ):
	"""This function is the default handler for executing actions."""
	msg = ResMgr.localise( "SCRIPT/ACTIONS_PY/EXECUTE_NOT_IMPLEMENTED", name )
	WorldEditor.addCommentaryMsg( msg )

# ------------------------------------------------------------------------------
# Section: Default Action enablers
# ------------------------------------------------------------------------------

boolReader = WorldEditor.getOptionBool
intReader = WorldEditor.getOptionInt
floatReader = WorldEditor.getOptionFloat
stringReader = WorldEditor.getOptionString
vector3Reader = WorldEditor.getOptionVector3
vector4Reader = WorldEditor.getOptionVector4

class OptionCheck:
	def __init__( self, path, value, reader = intReader ):
		self.path = path
		self.value = value
		self.readValue = reader

	def __call__( self ):
		return (1, self.readValue( self.path ) == self.value )

def defaultActionUpdate( name ):
	return (1, 0)
	

# Mark menu items for unimplemented features as disabled
	
def actPreferencesUpdate():
	return (0, 0)
	
def actNewProjectUpdate():
	return (0, 0)
	
def actOpenProjectUpdate():
	return (0, 0)
	
def actZoomExtentsUpdate():
	return (0, 0)
	
def actSaveProjectAsUpdate():
	return (0, 0)
	
def actUndoHistoryUpdate():
	return (0, 0)

def actAnimateDayNight():
	return (0, 0)

# ------------------------------------------------------------------------------
# Section: Specialised Action execution
# ------------------------------------------------------------------------------
def actSaveChunkTemplateExecute():
	if bd.itemTool.functor.script.selection.size:
		WorldEditor.saveChunkTemplate( bd.itemTool.functor.script.selection )
	else:
		WorldEditor.addCommentaryMsg( "`SCRIPT/ACTIONS_PY/NOTHING_SELECTED" )
		
def actSelectAllExecute():
	"""This function selects all editable items in all loaded chunks."""
	group = WorldEditor.selectAll()
	if ( group != None ):
		bd.itemTool.functor.script.selection.rem( bd.itemTool.functor.script.selection )
		bd.itemTool.functor.script.selection.add( group )
		bd.itemTool.functor.script.selUpdate()

def actDeselectAllExecute():
	if bd.itemTool.functor.script.selection.size:
		bd.itemTool.functor.script.selection.rem( bd.itemTool.functor.script.selection )
		bd.itemTool.functor.script.selUpdate()
		
def actImportExecute():
	WorldEditor.importDataGUI()

def actExportExecute():
	WorldEditor.exportDataGUI()

def actProjectOverlayNoneExecute():
	WorldEditor.setOptionInt("render/misc/drawOverlayLocks", 0)
	WorldEditor.setOptionInt("render/misc/drawOverlayLOD", 0)

def actProjectOverlayLocksExecute():
	WorldEditor.setOptionInt("render/misc/drawOverlayLocks", 1)
	WorldEditor.setOptionInt("render/misc/drawOverlayLOD", 0)

def actProjectOverlayLODExecute():
	WorldEditor.setOptionInt("render/misc/drawOverlayLocks", 0)
	WorldEditor.setOptionInt("render/misc/drawOverlayLOD", 1)
	WorldEditor.projectUpdateLODOverlay()


# ------------------------------------------------------------------------------
# Section: Specialised Action enablers
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Section: Radio button
# ------------------------------------------------------------------------------

def updateCamera( value ):
	c = WorldEditor.camera()
	c.speed = WorldEditor.getOptionFloat( "camera/speed/" + value )
	c.turboSpeed = WorldEditor.getOptionFloat( "camera/speed/" + value + "/turbo" )

def onUpdateSnaps( value ):
	bd.updateItemSnaps()
# below method for borland big bang where only two buttons
#	bd.toggleItemSnaps()	

def onUpdateCoordMode( value ):
	bd.updateCoordMode()

def onOrthoMode( self ):
	if WorldEditor.getOptionInt( "camera/ortho" == 1 ):
		WorldEditor.changeToCamera(1)
	else:
		WorldEditor.changeToCamera(0)
		
def toggleBSP( self ):
	bd.showBSPMsg()

radioButtons = (
	("actMoveSlow",					"camera/speed", "Slow",		updateCamera ),
	("actMoveMedium",				"camera/speed", "Medium",	updateCamera ),
	("actMoveFast",					"camera/speed", "Fast",		updateCamera ),
	("actMoveSuperFast",			"camera/speed", "SuperFast", updateCamera ),

	("actLightingStd",				"render/lighting", 0, bd.lightingModeMsg ),
	("actLightingDynamic",			"render/lighting", 1, bd.lightingModeMsg ),
	("actLightingSpecular",			"render/lighting", 2, bd.lightingModeMsg ),

	("actDrawBSPNormal",			"drawBSP", 0 ),
	("actDrawBSPCustom",			"drawBSP", 1 ),
	("actDrawBSPAll",				"drawBSP", 2 ),

	("actXZSnap",					"snaps/itemSnapMode", 0, onUpdateSnaps ),
	("actTerrainSnaps",				"snaps/itemSnapMode", 1, onUpdateSnaps ),
	("actObstacleSnap",				"snaps/itemSnapMode", 2, onUpdateSnaps ),
	
	("actCoordWorld",				"coordMode/coordMode", 0, onUpdateCoordMode ),
	("actCoordObject",				"coordMode/coordMode", 1, onUpdateCoordMode ),
	("actCoordView",				"coordMode/coordMode", 2, onUpdateCoordMode ),
)

toggleButtons = (
	("actDrawScenery",					"render/scenery", 0 ),
	("actDrawSceneryWireframe",			"render/scenery/wireFrame" ),
	("actDrawSceneryParticle",			"render/scenery/particle" ),
	("actDrawWater",					"render/scenery/drawWater" ),
	("actDrawWaterReflection",			"render/scenery/drawWater/reflection"),
	("actDrawShells",					"render/scenery/shells" ),
	("actDrawShellNeighboursPortals",	"render/scenery/shells/gameVisibility" ),
	("actDrawChunkFlares",				"render/scenery/drawChunkFlares" ),
	("actDrawChunkLights",				"render/scenery/drawChunkLights" ),
		
	("actDrawSceneryBSP",				"render/drawBSP", toggleBSP ),
	("actDrawSpeedTreesBSP",			"render/drawBSP/SpeedTrees", toggleBSP ),
	("actDrawOtherModelsBSP",			"render/drawBSP/OtherModels", toggleBSP ),
	("actDrawDebugBB",					"debugBB" ),
		
	("actDrawProxys",					"render/proxys" ),
	("actDrawEditorProxies",			"render/misc/drawEditorProxies" ),
	
	("actDrawParticleProxy",			"render/proxys/particleProxys" ),
	("actDrawLargeParticleProxy",		"render/proxys/particleProxyLarge" ),
	
	("actDrawLightProxys",				"render/proxys/lightProxys" ),
	("actDrawStaticLightProxy",			"render/proxys/staticLightProxys" ),
	("actDrawLargeStaticLightProxy",	"render/proxys/staticLightProxyLarge" ),
	
	("actDrawDynamicLightProxy",		"render/proxys/dynamicLightProxys" ),
	("actDrawLargeDynamicLightProxy",	"render/proxys/dynamicLightProxyLarge" ),

	("actDrawSpecularLightProxy",		"render/proxys/specularLightProxys" ),
	("actDrawLargeSpecularLightProxy",	"render/proxys/specularLightProxyLarge" ),
	
	("actDrawAmbientLightProxy",		"render/proxys/ambientLightProxys" ),
	("actDrawLargeAmbientLightProxy",	"render/proxys/ambientLightProxyLarge" ),
	
	("actDrawPulseLightProxy",		"render/proxys/pulseLightProxys" ),
	("actDrawLargePulseLightProxy",	"render/proxys/pulseLightProxyLarge" ),
	
	("actDrawSpotLightProxy",		"render/proxys/spotLightProxys" ),
	("actDrawLargeSpotLightProxy",	"render/proxys/spotLightProxyLarge" ),
	
	("actDrawFlareProxy",		"render/proxys/flareProxys" ),
	("actDrawLargeFlareProxy",	"render/proxys/flareProxyLarge" ),
	

	
	("actDrawTerrain",					"render/terrain", 0 ),
	("actDrawTerrainWireframe",			"render/terrain/wireFrame" ),
	# TODO: It would probably be better to change the action's name.
	("actRenderTerrainWireframe",		"render/terrain/wireFrame" ),
	("actToggleLOD",					"render/terrain/LOD", bd.toggleLod ),
	("actDrawTerrainLODLocks",			"render/terrain/LODLocks"),

	("actStaticDecals",					"render/decals", 0),
	("actShowStaticTextureAtlas",		"render/decals/showTextureAtlas"),
	("actShowStaticDecalsOverdraw",		"render/decals/showOverdraw"),
	("actAutoSizeDecals",				"render/decals/autoSize"),

	("actDrawGameObjects",				"render/gameObjects" ),
	("actDrawEntities",					"render/gameObjects/drawEntities" ),
	("actDrawUserDataObjects",			"render/gameObjects/drawUserDataObjects" ),
	("actDrawChunkMetaData",			"render/gameObjects/drawChunkMetaData" ),

	("actOrthoMode",					"camera/ortho", onOrthoMode ),

	("actToggleSnaps",					"snaps/xyzEnabled", bd.objectSnapMsg ),

	("actDrawEnvironment",				"render/environment" ),
	("actDrawSky",						"render/environment/drawSky" ),
	("actDrawSkyBoxes",					"render/environment/drawSkyBoxes" ),
	("actDrawSunAndMoon",				"render/environment/drawSunAndMoon" ),
	("actDrawFog",						"render/environment/drawFog" ),
	
	("actDrawMisc",						"render/misc" ),
	("actDrawHeavenAndEarth",			"render/misc/drawHeavenAndEarth" ),
	("actShadeReadOnlyAreas",			"render/misc/shadeReadOnlyAreas" ),
	("actShadeFrozenObjects",			"render/misc/shadeFrozenObjects" ),

	("actDragOnSelect",					"dragOnSelect", bd.dragOnSelectMsg ),
)


for entry in radioButtons:
	value = entry[2]

	if len(entry) == 3:
		locals()[ entry[0] + "Execute" ]	= OptionSet( entry[1], value )
	else:
		locals()[ entry[0] + "Execute" ]	= OptionSetPlus( entry[1], value, entry[3] )

	if isinstance( value, bool ):
		reader = boolReader
	elif isinstance( value, int ):
		reader = intReader
	elif isinstance( value, float ):
		reader = floatReader
	elif isinstance( value, str ):
		reader = stringReader
	elif isinstance( value, tuple ):
		if len(value) == 3:
			reader = vector3Reader
		else:
			reader = vector4Reader
	locals()[ entry[0] + "Update" ]		= OptionCheck( entry[1], value, reader )

for entry in toggleButtons:
	if len(entry) == 3:
		locals()[ entry[0] + "Execute" ] = OptionToggle( entry[1], entry[2] )
	else:
		locals()[ entry[0] + "Execute" ] = OptionToggle( entry[1] )

	locals()[ entry[0] + "Update"  ] = OptionCheck( entry[1], len(entry) != 4 )

# ------------------------------------------------------------------------------
# Section: Action list - description of actions
# ------------------------------------------------------------------------------

# actAnimateDayNight
# actAnimateScene
# actConstrainToBox
# actContinuousUpdate
# actDebugMessages
# actDelete
# actDeselectAll
# actDeselectRoot
# actDrawGradientSkyDome
# actDrawSky
# actDrawSunAndMoon
# actExit
# actFogEnabled
# actForceDraw
# actFreeSnaps
# actGameAnimationSpeed
# actHelp
# actKeyboard
# actLightAmbient
# actLightAmbientDirectional
# actLightAmbientOnly
# actLightDirectional
# actLightEnabled
# actLightGame
# actLightOmni
# actLightsFlareColourize
# actLightSpot
# actMiscSnapsAlignmentAbsolute
# actMiscSnapsAlignmentRelative
# actMiscSnapsAlignmentRelativeToObjectWorld
# actMoveFast
# actMoveMedium
# actMoveSlow
# actMoveSuperFast
# actNewProject
# actOpenProject
# actOrthoMode
# actPreferences
# actProjectEnvironmentSave
# actRedo
# actRenderSceneryHide
# actRenderSceneryShow
# actRenderSceneryShowRootOnly
# actRenderScenerySolid
# actRenderSceneryWireframe
# actRenderShellModelSolid
# actRenderShellModelWireframe
# actRenderShellNeighboursDirectOnly
# actRenderShellNeighboursHideAll
# actRenderShellNeighboursHideContents
# actRenderShellNeighboursIsolated
# actRenderShellNeighboursShowAll
# actRenderShellPortals
# actRenderTerrainHide
# actRenderTerrainShow
# actRenderTerrainSolid
# actRenderTerrainWireframe
# actRootFollowsCamera
# actSaveProject
# actSaveProjectAs
# actSceneryDefaults
# actShellDefaults
# actShellSnaps
# actShowAreaOfEffect
# actShowLightModels
# actSnapshot
# actTerrainDefaults
# actToggleSnaps
# actUndo
# actUndoHistory
# actUserDefaults
# actZoomExtents
