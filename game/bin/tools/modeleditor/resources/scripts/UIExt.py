import ModelEditorDirector
import ModelEditor
import WorldEditor
import ResMgr
from os import startfile

def contextMenuGetItems( type, fileName ):

	pos = fileName.rfind(".")
	ext = fileName[pos+1:]
	
	if ext == "model":
		return [ ( 1, ResMgr.localise("UAL/UAL_DIALOG/OPEN_MODEL" ) ), ( 2, ResMgr.localise("UAL/UAL_DIALOG/ADD_MODEL" ) ) ]
	elif ext == "mvl" or (type == "PRESET" and fileName == "UseGameLighting"):
		return [ ( 1, ResMgr.localise("UAL/UAL_DIALOG/USE_LIGHTING_SETUP" )) ]
		
	return []

def contextMenuHandleResult( type, fileName, command ):
	if command == 1:
		openFile( fileName )
	if command == 2:
		addModel( fileName )
		
def openFile( fileName ):

	#Lets handle our custom item events first
	if fileName == "UseGameLighting":
		WorldEditor.setOptionInt( "settings/useCustomLighting", 0 )
		return

	pos = fileName.rfind(".")
	ext = fileName[pos+1:]
	
	if ext == "model":
		loadModel( fileName )
	elif ext == "mvl":
		loadLights( fileName )
		
def loadModel( fileName ):
	return ModelEditor.loadModel( fileName )
	
def addModel( fileName ):
	return ModelEditor.addModel( fileName )
		 
def loadLights( fileName ):
	return ModelEditor.loadLights( fileName )

def doRequestFeature( item ):
	startfile( "mailto:support@bigworldtech.com?subject=ModelEditor %2D Feature Request %2F Bug Report" )