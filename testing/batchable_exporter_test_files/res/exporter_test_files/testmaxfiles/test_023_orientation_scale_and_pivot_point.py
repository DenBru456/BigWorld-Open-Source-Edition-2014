import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_023_orientation_scale_and_pivot_point.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_023_orientation_scale_and_pivot_point_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_023_orientation_scale_and_pivot_point_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_023_orientation_scale_and_pivot_point_actions.png" )
	ModelEditor.captureModel( "tmp/test_023_orientation_scale_and_pivot_point_model.png" )
	
	ModelEditor.exit( True )
