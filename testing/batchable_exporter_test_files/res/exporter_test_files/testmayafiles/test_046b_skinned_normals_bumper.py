import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_046b_skinned_normals_bumper.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_046b_skinned_normals_bumper_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_046b_skinned_normals_bumper_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_046b_skinned_normals_bumper_actions.png" )
	ModelEditor.captureModel( "tmp/test_046b_skinned_normals_bumper_model.png" )
	
	ModelEditor.exit( True )
