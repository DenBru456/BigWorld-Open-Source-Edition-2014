import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_070_custombsp_materials.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_070_custombsp_materials_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_070_custombsp_materials_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_070_custombsp_materials_actions.png" )
	ModelEditor.captureModel( "tmp/test_070_custombsp_materials_model.png" )
	
	ModelEditor.exit( True )
