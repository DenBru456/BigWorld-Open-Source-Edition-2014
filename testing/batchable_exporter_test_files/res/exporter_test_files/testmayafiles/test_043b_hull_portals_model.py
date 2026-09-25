import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_043b_hull_portals_model.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_043b_hull_portals_model_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_043b_hull_portals_model_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_043b_hull_portals_model_actions.png" )
	ModelEditor.captureModel( "tmp/test_043b_hull_portals_model_model.png" )
	
	ModelEditor.exit( True )
