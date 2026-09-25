import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_057_removing_coplanar_verts.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_057_removing_coplanar_verts_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_057_removing_coplanar_verts_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_057_removing_coplanar_verts_actions.png" )
	ModelEditor.captureModel( "tmp/test_057_removing_coplanar_verts_model.png" )
	
	ModelEditor.exit( True )
