import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_012_static_with_nodes_hp_points_and_custom_bsp_on.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_012_static_with_nodes_hp_points_and_custom_bsp_on_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_012_static_with_nodes_hp_points_and_custom_bsp_on_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_012_static_with_nodes_hp_points_and_custom_bsp_on_actions.png" )
	ModelEditor.captureModel( "tmp/test_012_static_with_nodes_hp_points_and_custom_bsp_on_model.png" )
	
	ModelEditor.exit( True )
