import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_034_inverse_kinematics.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_034_inverse_kinematics_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_034_inverse_kinematics_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_034_inverse_kinematics_actions.png" )
	ModelEditor.captureModel( "tmp/test_034_inverse_kinematics_model.png" )
	ModelEditor.exit( True )

