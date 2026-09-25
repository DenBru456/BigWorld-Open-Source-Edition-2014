import ModelEditor

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

def addChatMsg(id, msg):	
	ModelEditor.addCommentaryMsg( msg )

def addCameraSpaceChangeListener(listener):
	global cameraSpaceChangeListeners
	cameraSpaceChangeListeners[listener] = listener

def delCameraSpaceChangeListener(listener):
	global cameraSpaceChangeListeners
	del cameraSpaceChangeListeners[listener]

def addSaveSpaceListener(listener):
	global saveSpaceListeners
	saveSpaceListeners[listener] = listener

def delSaveSpaceListener(listener):
	global saveSpaceListeners
	del saveSpaceListeners[listener]

def spaceName( spaceID ):
	#In ME we only have one space open at once, so supposedly
	#the spaceID will match the currently loaded space
	return "helpers/spaces/pe"
	#return ModelEditor.spaceName()
