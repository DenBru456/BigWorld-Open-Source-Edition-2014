import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_029_maya_shelf.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_029_maya_shelf_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_029_maya_shelf_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_029_maya_shelf_actions.png" )
	ModelEditor.captureModel( "tmp/test_029_maya_shelf_model.png" )
	
	ModelEditor.exit( True )
