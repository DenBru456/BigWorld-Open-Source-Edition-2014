import ModelEditorDirector
import ModelEditor
import WorldEditor
import ResMgr

#---------------------------
# The main toolbar
#---------------------------

def doUndo( item ):
	"""This function undoes the most recent operation, returning
 	its description. If it is passed a positive integer argument,
 	then it just returns the description for that level of the
 	undo stack and doesn't actually undo anything.
 	If there is no undo level, the empty string is returned."""
	ModelEditor.undo()

def updateUndo( item ):
	if (ModelEditor.undo(0) != "" ):
		return 1
	return 0

def doRedo( item ):
	"""This function redoes the most recent undo operation, returning
 	its description. If it is passed a positive integer argument,
 	then it just returns the description for that level of the
 	redo stack and doesn't actually redo anything.
 	If there is no redo level, the empty string is returned."""
	ModelEditor.redo()

def updateRedo( item ):
	if (ModelEditor.redo(0) != "" ):
		return 1
	return 0

def doThumbnail( item ):
	"""This function makes a thumbnail picture for the model."""
	ModelEditor.makeThumbnail()
	
def updateThumbnail( item ):
	return 1
	
def doZoomExtents( item ):
	"""This function centres the model in view and zooms the camera until
 	the model just fits in view."""
	ModelEditor.zoomToExtents()
	
def doFreeCamera( item ):
	ModelEditor.camera().mode = 0
	
def updateFreeCamera( item ):
	return ModelEditor.camera().mode == 0
	
def doXCamera( item ):
	ModelEditor.camera().mode = 1
	
def updateXCamera( item ):
	return ModelEditor.camera().mode == 1
	
def doYCamera( item ):
	ModelEditor.camera().mode = 2
	
def updateYCamera( item ):
	return ModelEditor.camera().mode == 2
	
def doZCamera( item ):
	ModelEditor.camera().mode = 3
	
def updateZCamera( item ):
	return ModelEditor.camera().mode == 3
	
def doOrbitCamera( item ):
	ModelEditor.camera().mode = 4
	
def updateOrbitCamera( item ):
	return ModelEditor.camera().mode == 4
			
def updateCamera():
	value = WorldEditor.getOptionString( "camera/speed" )
	c = ModelEditor.camera()
	speed = 1
	if value == "Medium":
		speed = 8
	elif value == "Fast":
		speed = 24
	elif value == "SuperFast":
		speed = 48
	c.speed = WorldEditor.getOptionFloat( "camera/speed/" + value, speed )
	c.turboSpeed = WorldEditor.getOptionFloat( "camera/speed/" + value + "/turbo", 2*speed )

def doSlowCamera( item ):
	WorldEditor.setOptionString( "camera/speed", "Slow" );
	updateCamera()

def doMediumCamera( item ):
	WorldEditor.setOptionString( "camera/speed", "Medium" );
	updateCamera()

def doFastCamera( item ):
	WorldEditor.setOptionString( "camera/speed", "Fast" );
	updateCamera()

def doSuperFastCamera( item ):
	WorldEditor.setOptionString( "camera/speed", "SuperFast" );
	updateCamera()
	
#---------------------------
# The animations toolbar
#---------------------------
	
def updateLockedAnim( item ):
	return not ModelEditor.isAnimLocked()
	
def doAddAmin( item ):
	"""This function enables the Open ModelEditor File Dialog, which allows an action to be loaded."""
	ModelEditor.addAnim()
	
def doPlayAnim( item ):
	"""This function plays the currently selected animation."""
	ModelEditor.playAnim()
	
def updatePlayAnim( item ):
	return not ModelEditor.animPlaying()

def doStopAnim( item ):
	"""This function plays the currently selected animation."""
	ModelEditor.stopAnim()
	
def updateStopAnim( item ):
	return ModelEditor.animPlaying()

def doLoopAnim( item ):
	"""This function toggles whether the animation should loop play."""
	ModelEditor.loopAnim()
	
def updateLoopAnim( item ):
	return not ModelEditor.animLooping()

def doRemoveAnim( item ):
	"""This function removes the currently selected animation."""
	ModelEditor.removeAnim()

#---------------------------
# The compression toolbar
#---------------------------

def doShowOriginalAnim( item ):
	show = WorldEditor.getOptionInt( "settings/showOriginalAnim", 0 );
	show = not show
	WorldEditor.setOptionInt( "settings/showOriginalAnim", show );
	
def updateShowOriginalAnim( item ):
	return not WorldEditor.getOptionInt( "settings/showOriginalAnim", 0 );
	
def doSaveAnim( item ):
	"""This function saves the compressed animation."""
	ModelEditor.saveAnimComp()
	
def canViewAnim( item ):
	"""This function checks whether it is possible to view the uncompressed animation."""
	return ModelEditor.canViewAnimComp()
	
def canSaveAnim( item ):
	"""This function checks whether it is possible to save the compressed animation."""
	return ModelEditor.canSaveAnimComp()

#---------------------------
# The actions toolbar
#---------------------------
	
def updateLockedAct( item ):
	return not ModelEditor.isActLocked()

def doNewAct( item ):
	"""This function enables the Create Action Dialog."""
	ModelEditor.newAct()
	
def doRemoveAct( item ):
	"""This function removes the currently selected action from the model."""
	ModelEditor.removeAct()
	
def doPromoteAct( item ):
	"""This function promotes the currently selected action.
 	Promoting an action moves it higher up the actions list.
 	When the action matcher chooses an action to trigger, actions
 	higher on the actions list will take preference over other actions
 	that may match in the action matcher."""
	ModelEditor.promoteAct()
	
def doDemoteAct( item ):
	"""This function demotes the currently selected action.
 	Promoting an action moves it lower down the actions list.
 	When the action matcher chooses an action to trigger, actions
 	higher on the actions list will take preference over other actions
 	that may match in the action matcher."""
	ModelEditor.demoteAct()
	
def doPlayAct( item ):
	"""This function forces the currently selected action to play."""
	ModelEditor.playAct()
	
def doStopAct( item ):
	"""This function stops all currently playing actions."""
	ModelEditor.stopAct()
	
def doShowActions( item ):
	show = WorldEditor.getOptionInt( "settings/showActions", 0 );
	show = not show
	WorldEditor.setOptionInt( "settings/showActions", show );
	
def updateShowActions( item ):
	return not WorldEditor.getOptionInt( "settings/showActions", 0 );
	
#---------------------------
# The LOD toolbar
#---------------------------

def updateLockedLod( item ):
	return not ModelEditor.isLockedLod()

def doNewLod( item ):
	"""This function enables the Open ModelEditor File Dialog, which allows a LOD model to be loaded."""
	ModelEditor.newLod()
	
def doChangeLodModel( item ):
	"""This function enables the Open ModelEditor File Dialog, which allows the currently
 	selected LOD model to be changed to a different model."""
	ModelEditor.changeLodModel()
	
def updateChangeLodModel( item ):
	return ModelEditor.lodSelected() and not ModelEditor.isFirstLod() and not ModelEditor.isLockedLod() 

def doMoveLodUp( item ):
	"""This function moves the currently selected LOD model higher up the LOD list."""
	ModelEditor.moveLodUp()
	
def updateMoveLodUp( item ):
	return ModelEditor.lodSelected() and ModelEditor.canMoveLodUp() and not ModelEditor.isLockedLod() and not ModelEditor.isMissingLod()

def doMoveLodDown( item ):
	"""This function moves the currently selected LOD model lower down the LOD list."""
	ModelEditor.moveLodDown()
	
def updateMoveLodDown( item ):
	return ModelEditor.lodSelected() and ModelEditor.canMoveLodDown() and not ModelEditor.isLockedLod() and not ModelEditor.isMissingLod()

def doSetLodDist( item ):
	"""This function sets the LOD model's state to 'Hidden'. If the LOD model is 
 	the highest on the LOD list then it's maximum LOD distance is set to the distance
 	between the model and the camera position."""
	ModelEditor.setLodToDist()

def doExtendLodForever( item ):
	"""This function sets the currently selected LOD model's maximum LOD distance to infinity.
 	Actively making this LOD model visible for all distances further then its minimum LOD distance."""
	ModelEditor.extendLodForever()
	
def updateLodDist( item ):
	return ModelEditor.lodSelected() and ModelEditor.isFirstLod() or not ModelEditor.isLockedLod() and not ModelEditor.isMissingLod()
	
def doRemoveLod( item ):
	"""This function removes the currently selected LOD model."""
	ModelEditor.removeLod()
	
def updateRemoveLod( item ):
	return ModelEditor.lodSelected() and not ModelEditor.isFirstLod() and not ModelEditor.isLockedLod()
	
#---------------------------
# The Lights toolbar
#---------------------------

def doNewLights( item ):
	"""This function disables all the custom lighting and allows for a new light's display settings to be created."""
	ModelEditor.newLights()

def doOpenLights( item ):
	"""This function enables the Open ModelEditor File Dialog, which allows a light to be loaded."""
	ModelEditor.openLights()

def doSaveLights( item ):
	"""This function opens the Save ModelEditor Dialog, for saving the current light's display settings."""
	ModelEditor.saveLights()
	
#---------------------------
# The Materials toolbar
#---------------------------

def doNewTint( item ):
	"""This function enables ModelEditor's Create Tint Dialog."""
	ModelEditor.newTint()
	
def doLoadMFM( item ):
	"""This function enables the Open ModelEditor File Dialog, which allows a MFM to be loaded."""
	ModelEditor.loadMFM()
	
def doSaveMFM( item ):
	"""This function saves the currently selected MFM."""
	ModelEditor.saveMFM()
	
def doDeleteTint( item ):
	"""This function deletes the currently selected tint."""
	ModelEditor.deleteTint()

def updateDeleteTint( item ):
	"""Checks whether the currently selected tint can be deleted."""
	return ModelEditor.canDeleteTint()