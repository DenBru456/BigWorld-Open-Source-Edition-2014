import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_018_use_current_scene_state.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_018_use_current_scene_state_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_018_use_current_scene_state_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_018_use_current_scene_state_actions.png" )
	ModelEditor.captureModel( "tmp/test_018_use_current_scene_state_model.png" )
	
	ModelEditor.exit( True )
