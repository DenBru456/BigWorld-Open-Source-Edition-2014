import WorldEditor

# Personality is a way of collecting game specific information for each space.
# On save, the Personality module named in the worldeditor options.xml
# and correspondingly defined in res\entities\editor is called.
# e.g. the Personality module could record the locations of particular types
#      of entities or count the number of particular guards, any space related
#      information that the game may need

cameraSpaceChangeListeners = {}
environmentChangeListeners = {}
saveSpaceListeners = {}
cameraSpaceID = 0
spaceNameMap = {}


def getPersonalityModule():
	global personalityModule

	if personalityModule != 0: return personalityModule

	personalityModule = None
	personalityName = WorldEditor.opts._personality.asString
	personalityModule = __import__( personalityName )
	return personalityModule


def callPersonalityFunction( fnname ):
	try:
		fn = getattr( getPersonalityModule(), fnname )
	except:
		return
	fn()


def preFullSave():
	callPersonalityFunction( "preFullSave" )


def preQuickSave():
	callPersonalityFunction( "preQuickSave" )


def addChatMsg(id, msg):	
	WorldEditor.addCommentaryMsg( msg )


# -----------------------------------------------------------------------------
# Method: onCameraSpaceChange
# Description:
#	- This is called automatically when the camera moves from one space to
#	another.
#	- The space ID and space.settings datasection is passed in to this
#	function.
# -----------------------------------------------------------------------------
def onCameraSpaceChange(spaceID, spaceSettings):
	global cameraSpaceID
	global cameraSpaceChangeListeners
	cameraSpaceID = spaceID
	for listener in cameraSpaceChangeListeners.keys():
		listener(spaceID,spaceSettings)


def addCameraSpaceChangeListener(listener):
	global cameraSpaceChangeListeners
	cameraSpaceChangeListeners[listener] = listener


def delCameraSpaceChangeListener(listener):
	global cameraSpaceChangeListeners
	del cameraSpaceChangeListeners[listener]


# -----------------------------------------------------------------------------
# Method: onSave
# Description:
#	- This is called when the user presses save.
#	- The space name and space.settings datasection is passed in to this
#	function.
#	- The space.settings is saved in engine code after this function call,
#	so you do not need to save it yourself.
# -----------------------------------------------------------------------------
def onSave(spaceName, spaceSettings):
	for listener in saveSpaceListeners.keys():
		listener(spaceName,spaceSettings)


def addSaveSpaceListener(listener):
	global saveSpaceListeners
	saveSpaceListeners[listener] = listener


def delSaveSpaceListener(listener):
	global saveSpaceListeners
	del saveSpaceListeners[listener]


def spaceName( spaceID ):
	#In WE we only have one space open at once, so supposedly
	#the spaceID will match the currently loaded space
	return WorldEditor.spaceName()


# -----------------------------------------------------------------------------
# Method: isDirty
# Description:
#	- This is called when the WorldEditor wants to know whether there are
#	any script-based editors that have active changes.
# -----------------------------------------------------------------------------
def isDirty():
	import WeatherUIAdapter	
	return WeatherUIAdapter.g_dirty


# -----------------------------------------------------------------------------
# Method: forceClean
# Description:
#	- This is called when the WorldEditor orders everyone to behave as though
#	nothing has changed.  Currently only called when restarting due to a
#	language or graphics settings change, and the user decides to ignore and
#	not save changes.
# -----------------------------------------------------------------------------
def forceClean():
	import WeatherUIAdapter
	WeatherUIAdapter.g_dirty = False
