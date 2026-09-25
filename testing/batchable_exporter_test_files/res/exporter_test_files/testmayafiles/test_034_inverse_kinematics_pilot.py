import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_034_inverse_kinematics_pilot.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_034_inverse_kinematics_pilot_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_034_inverse_kinematics_pilot_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_034_inverse_kinematics_pilot_actions.png" )
	ModelEditor.captureModel( "tmp/test_034_inverse_kinematics_pilot_model.png" )
	
	ModelEditor.exit( True )
