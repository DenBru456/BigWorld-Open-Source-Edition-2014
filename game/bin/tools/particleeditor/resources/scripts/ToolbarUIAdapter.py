import ParticleEditorDirector
import ParticleEditor
import WorldEditor
import ResMgr

def doZoomExtents( item ):
	"""This function centres the particle system in view and zooms the camera until
 	the particle system just fits in view."""
	ParticleEditor.zoomToExtents()

def doViewFree( item ):
	"""This function enables the free view camera mode."""
	ParticleEditor.doViewFree()
    
def updateFreeCamera( item ):
	return ParticleEditor.cameraMode() == 0 

def doViewX( item ):
	"""This function positions the camera to look toward the origin along the X-axis."""
	ParticleEditor.doViewX()

def updateXCamera( item ):
	return ParticleEditor.cameraMode() == 1
    
def doViewY( item ):
	"""This function positions the camera to look toward the origin along the Y-axis."""
	ParticleEditor.doViewY()
    
def updateYCamera( item ):
	return ParticleEditor.cameraMode() == 2 
    
def doViewZ( item ):
	"""This function positions the camera to look toward the origin along the Z-axis."""
	ParticleEditor.doViewZ()
    
def updateZCamera( item ):
	return ParticleEditor.cameraMode() == 3 
	
def doViewOrbit( item ):
	"""This function enables the orbit view camera mode."""
	ParticleEditor.doViewOrbit()
    
def updateOrbitCamera( item ):
	return ParticleEditor.cameraMode() == 4 
	
def updateCamera():
	value = WorldEditor.getOptionString( "camera/speed" )
	c = ParticleEditor.camera()
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

def doSetBkClr( item ):
	"""This function enabled the ParticleEditor Colour Picker Dialog, which allows the 
 	background colour to be changed."""
	ParticleEditor.doSetBkClr()

def updateBkClr( item ):
	"""Checks whether a background colour is currently set."""
	return ParticleEditor.updateBkClr()
   
def doUndo( item ):
	"""This function undoes the most recent operation."""
	ParticleEditor.undo()

def updateUndo( item ):
	"""This function checks whether it is possible to undo the most recent operation."""
	return ParticleEditor.canUndo()
  
def doRedo( item ):
	"""This function redoes the most recent undo operation."""
	ParticleEditor.redo()
  
def updateRedo( item ):
	"""This function checks whether it is possible to redo the most recent undo operation."""
	return ParticleEditor.canRedo()
    
def doSpawn( item ):
	"""This function spawns the currently selected Particle System and sets its state to 'playing'."""
	ParticleEditor.doSpawn()

def doRestart( item ):
	"""This function restarts the currently selected Particle System and sets its state to 'playing'."""
	ParticleEditor.doRestart()

def doPlay( item ):
	"""This function spawns the currently selected Particle System and sets its state to 'playing'."""
	ParticleEditor.doPlay()
    
def updateDoPlay( item ):
	return ParticleEditor.getState() == 0
    
def doPause( item ):
	"""This function sets the the currently selected Particle System state to 'paused'."""
	ParticleEditor.doPause()
    
def updateDoPause( item ):
	return ParticleEditor.getState() == 1    
    
def doStop( item ):
	"""This function sets the the currently selected Particle System state to 'stopped'."""
	ParticleEditor.doStop()
    
def updateDoStop( item ):
	return ParticleEditor.getState() == 2



