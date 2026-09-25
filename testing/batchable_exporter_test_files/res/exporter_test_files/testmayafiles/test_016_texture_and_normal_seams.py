import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_016_texture_and_normal_seams.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_016_texture_and_normal_seams_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_016_texture_and_normal_seams_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_016_texture_and_normal_seams_actions.png" )
	ModelEditor.captureModel( "tmp/test_016_texture_and_normal_seams_model.png" )
	
	ModelEditor.exit( True )
