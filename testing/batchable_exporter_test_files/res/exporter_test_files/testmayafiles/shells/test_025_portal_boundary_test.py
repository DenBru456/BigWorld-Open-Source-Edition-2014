import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_025_portal_boundary_test.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_025_portal_boundary_test_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_025_portal_boundary_test_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_025_portal_boundary_test_actions.png" )
	ModelEditor.captureModel( "tmp/test_025_portal_boundary_test_model.png" )
	
	ModelEditor.exit( True )
