import ModelEditorDirector
import ModelEditor
import WorldEditor


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
	"This class is used to implement action handlers that toggles an option."

	def __init__( self, path, postFunction = None ):
		self.path = path
		self.postFunction = postFunction

	def __call__( self ):
		oldValue = WorldEditor.getOptionInt( self.path )
		newValue = not oldValue
		WorldEditor.setOption( self.path, newValue )
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
	ModelEditor.addCommentaryMsg( "%s execute not yet implemented" % name )
	pass

# ------------------------------------------------------------------------------
# Section: Default Action enablers
# ------------------------------------------------------------------------------

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
		
class OptionIndex:
	def __init__( self, test ):
		self.test = test

	def __call__( self ):
		return (1, self.test())

# ------------------------------------------------------------------------------
# Section: Control Functionality
# ------------------------------------------------------------------------------

def updateCamera( value ):
	pass
	
def shadowIndex():
	quality = WorldEditor.getOptionInt( "renderer/shadows/quality", 0 )
	return quality
		
def enableShadowing( value ):
	WorldEditor.setOptionInt( "settings/showShadowing", 1 )

def disableShadowing( value ):
	WorldEditor.setOptionInt( "settings/showShadowing", 0 )
	
def bkgIndex():
	terrain = WorldEditor.getOptionInt( "settings/useTerrain", 1 )
	floor = WorldEditor.getOptionInt( "settings/useFloor", 0 )
	if terrain:
		return 2
	else:
		return floor
		
def disableFloor( value ):
	WorldEditor.setOptionInt( "settings/useFloor", 0 )	
		
def disableTerrain( value ):
	WorldEditor.setOptionInt( "settings/useTerrain", 0 )
		
# ------------------------------------------------------------------------------
# Section: Control handler layout
# ------------------------------------------------------------------------------

radioButtons = (
	("actMoveSlow",       "camera/speed",  "Slow",       updateCamera ),
	("actMoveMedium",     "camera/speed",  "Medium",     updateCamera ),
	("actMoveFast",       "camera/speed",  "Fast",       updateCamera ),
	("actMoveSuperFast",  "camera/speed",  "SuperFast",  updateCamera ),
	
	("actGetShadowIndex", shadowIndex),
	
	("actShadowMaxQuality",  "renderer/shadows/quality",  0,  enableShadowing ),
	("actShadowHighQuality", "renderer/shadows/quality",  1,  enableShadowing ),
	("actShadowMedQuality",  "renderer/shadows/quality",  2,  enableShadowing ),
	("actShadowLowQuality",  "renderer/shadows/quality",  3,  enableShadowing ),
	("actShadowOff",         "renderer/shadows/quality",  4,  disableShadowing ),
	
	("actGetBkgIndex", bkgIndex),
	
	("actBkgTerrain",	"settings/useTerrain",	1,	disableFloor),
	("actBkgFloor",		"settings/useFloor",	1,	disableTerrain),
	("actBkgNone",		"settings/useFloor",	0,	disableTerrain),
)

toggleButtons = (
	("actShowAxes",               "settings/showAxes",               0 ),
	("actCheckForSparkles",       "settings/checkForSparkles",       0 ),
	("actEnableFog",			  "render/environment/drawFog",		 0 ),
	("actEnableHDR",			  "settings/enableHDR",				 0 ),
	("actEnableSSAO",			  "settings/enableSSAO",			 0 ),
	
	("actShowModel",              "settings/showModel",              0 ),
	("actShowWireframe",          "settings/showWireframe",          0 ),
	("actShowSkeleton",           "settings/showSkeleton",           0 ),
	("actShowShadowing",          "settings/showShadowing",          0 ),
	("actShowBsp",                "settings/showBsp",                0 ),
	("actShowBoundingBox",        "settings/showBoundingBox",        0 ),
	("actShowPortals",            "settings/showPortals",            0 ),
	("actShowNormals",            "settings/showNormals",            0 ),
	("actShowBinormals",          "settings/showBinormals",          0 ),
	("actShowCustomHull",         "settings/showCustomHull",         0 ),
	("actShowHardPoints",         "settings/showHardPoints",         0 ),
	("actGroundModel",            "settings/groundModel",            0 ),
	("actCentreModel",            "settings/centreModel",            0 ),
	
	("actShowFloor",              "settings/showFloor",              0 ),
	
	("actShowEditorProxy",			"settings/showEditorProxy",		0 ),
	
	("actUseCustomLighting",		"settings/useCustomLighting",	0 ),
	("actShowLightModels",			"settings/showLightModels",		0 ),
	
	("actShowOriginalAnim",			"settings/showOriginalAnim",	0 ),
)

# ------------------------------------------------------------------------------
# Section: Create control handlers
# ------------------------------------------------------------------------------

for entry in radioButtons:

	#A special case for returning an index
	if len(entry) == 2:
		locals()[ entry[0] + "Update" ] = OptionIndex( entry[1] )
	else:
	
		value = entry[2]

		if len(entry) == 3:
			locals()[ entry[0] + "Execute" ]	= OptionSet( entry[1], value )
		else:
			locals()[ entry[0] + "Execute" ]	= OptionSetPlus( entry[1], value, entry[3] )

		if isinstance( value, int ):
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
	