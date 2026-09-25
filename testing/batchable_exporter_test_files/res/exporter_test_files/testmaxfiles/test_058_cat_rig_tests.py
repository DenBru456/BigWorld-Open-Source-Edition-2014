import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_058_cat_rig_tests.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_058_cat_rig_tests_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_058_cat_rig_tests_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_058_cat_rig_tests_actions.png" )
	ModelEditor.captureModel( "tmp/test_058_cat_rig_tests_model.png" )
	
	ModelEditor.exit( True )