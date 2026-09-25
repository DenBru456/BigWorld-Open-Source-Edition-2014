import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_017_use_reference_hierarchy_2.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_017_use_reference_hierarchy_2_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_017_use_reference_hierarchy_2_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_017_use_reference_hierarchy_2_actions.png" )
	ModelEditor.captureModel( "tmp/test_017_use_reference_hierarchy_2_model.png" )
	
	ModelEditor.exit( True )
