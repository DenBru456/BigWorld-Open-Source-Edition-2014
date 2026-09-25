import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_067_export_custom_hull.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_067_export_custom_hull_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_067_export_custom_hull_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_067_export_custom_hull_actions.png" )
	ModelEditor.captureModel( "tmp/test_067_export_custom_hull_model.png" )
	
	ModelEditor.exit( True )
