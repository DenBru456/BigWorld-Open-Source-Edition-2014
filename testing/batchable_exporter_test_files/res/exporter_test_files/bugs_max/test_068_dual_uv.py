import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_068_dual_uv.model" )
	captureModelAndQuit().run()
	
@BWCoroutine
def captureModelAndQuit():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_068_dual_uv_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_068_dual_uv_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_068_dual_uv_actions.png" )
	ModelEditor.captureModel( "tmp/test_068_dual_uv_model.png" )
	
	ModelEditor.exit( True )
