import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_069_shared_vertex_colour.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_069_shared_vertex_colour_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_069_shared_vertex_colour_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_069_shared_vertex_colour_actions.png" )
	ModelEditor.captureModel( "tmp/test_069_shared_vertex_colour_model.png" )
	
	ModelEditor.exit( True )
