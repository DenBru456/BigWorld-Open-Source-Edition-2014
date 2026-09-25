import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_007_custom_bsp_off.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_007_custom_bsp_off_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_007_custom_bsp_off_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_007_custom_bsp_off_actions.png" )
	ModelEditor.captureModel( "tmp/test_007_custom_bsp_off_model.png" )
	
	ModelEditor.exit( True )
