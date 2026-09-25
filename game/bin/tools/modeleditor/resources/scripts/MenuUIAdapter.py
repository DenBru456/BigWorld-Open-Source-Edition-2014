import ModelEditorDirector
import ModelEditor
import ResMgr

#---------------------------
# The file menu
#---------------------------

def doOpenFile( item ):
	"""This function enables the Open ModelEditor File Dialog, which allows a model to be loaded."""
	ModelEditor.openFile()
	
def doAddModel( item ):
	"""This function enables the Open ModelEditor File Dialog, which allows a model to be 
	added to the currently loaded model."""
	ModelEditor.addFile()
	
def doRemoveAddedModels( item ):
	"""This function removes any added models from the loaded model."""
	ModelEditor.removeAddedModels()
	
def doRevertModel( item ):
	"""This function reverts the model to the last saved model. Any modifications made
 	to the model that have not been saved will be lost."""
	ModelEditor.revertModel()
	
def hasAddedModels( item ):
	"""This function checks to see if the loaded model currently has any added models."""
	return ModelEditor.hasAddedModels()
	
def doReloadTextures( item ):
	"""This function forces all the textures to be reloaded."""
	ModelEditor.reloadTextures();
	
def isModelLoaded( item ):
	"""This function checks to see if there currently is a loaded model."""
	return ModelEditor.isModelLoaded()
	
def doRegenBoundingBox( item ):
	"""This function forces the model's Visibility Bounding Box to be recalculated."""
	ModelEditor.regenBoundingBox();
	
def isModelDirty( item ):
	"""This function checks to see if the model is dirty.
 	A dirty model is a model that has been modified and not yet saved."""
	return ModelEditor.isModelDirty()
	
def doSaveFile( item ):
	"""This function saves the changes made to the model."""
	ModelEditor.saveModel()
	
def doSaveFileAs( item ):
	"""This function allows the model to be saved in a chosen directory and 
	under a chosen name."""
	ModelEditor.saveModelAs()

#---------------------------
# The edit menu
#---------------------------

def doPrefs( item ):
	"""This function opens up ModelEditor's preferences dialog."""
	ModelEditor.appPrefs()
	
#---------------------------
# The view menu
#---------------------------
	
def doShowAssetLocatorPanel( item ):
	"""This function displays the Asset Locator Panel."""
	ModelEditor.showPanel( "UAL", 1 )
	
def doShowDisplayPanel( item ):
	"""This function displays the Display Panel."""
	ModelEditor.showPanel( "Display", 1 )
	
def doShowObjectPanel( item ):
	"""This function displays the Object Panel."""
	ModelEditor.showPanel( "Object", 1 )
	
def doShowAnimationsPanel( item ):
	"""This function displays the Animations Panel."""
	ModelEditor.showPanel( "Animations", 1 )
	
def doShowActionsPanel( item ):
	"""This function displays the Actions Panel."""
	ModelEditor.showPanel( "Actions", 1 )

def doShowLODPanel( item ):
	"""This function displays the LOD Panel."""
	ModelEditor.showPanel( "LOD", 1 )

def doShowLightsPanel( item ):
	"""This function displays the Lights Panel."""
	ModelEditor.showPanel( "Lights", 1 )

def doShowMaterialsPanel( item ):
	"""This function displays the Materials Panel."""
	ModelEditor.showPanel( "Materials", 1 )

def doShowMessagesPanel( item ):
	"""This function displays the Messages Panel."""
	ModelEditor.showPanel( "Messages", 1 )
