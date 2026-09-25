import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_030_portals_of_different_sizes_portals.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_030_portals_of_different_sizes_portals_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_030_portals_of_different_sizes_portals_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_030_portals_of_different_sizes_portals_actions.png" )
	ModelEditor.captureModel( "tmp/test_030_portals_of_different_sizes_portals_model.png" )
	
	ModelEditor.exit( True )
