import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_074_very_large_object_checker_off.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_074_very_large_object_checker_off_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_074_very_large_object_checker_off_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_074_very_large_object_checker_off_actions.png" )
	ModelEditor.captureModel( "tmp/test_074_very_large_object_checker_off_model.png" )
	
	ModelEditor.exit( True )
