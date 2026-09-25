import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_035_duplicate_materials_name.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_035_duplicate_materials_name_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_035_duplicate_materials_name_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_035_duplicate_materials_name_actions.png" )
	ModelEditor.captureModel( "tmp/test_035_duplicate_materials_name_model.png" )
	
	ModelEditor.exit( True )
