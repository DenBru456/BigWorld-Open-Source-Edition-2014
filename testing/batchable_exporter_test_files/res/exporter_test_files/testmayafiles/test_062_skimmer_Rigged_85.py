import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_062_skimmer_Rigged_85.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_062_skimmer_Rigged_85_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_062_skimmer_Rigged_85_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_062_skimmer_Rigged_85_actions.png" )
	ModelEditor.captureModel( "tmp/test_062_skimmer_Rigged_85_model.png" )
	
	ModelEditor.exit( True )
