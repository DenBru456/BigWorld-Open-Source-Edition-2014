import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_078_edit_normals_multiple_mesh.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_078_edit_normals_multiple_mesh_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_078_edit_normals_multiple_mesh_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_078_edit_normals_multiple_mesh_actions.png" )
	ModelEditor.captureModel( "tmp/test_078_edit_normals_multiple_mesh_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_078_edit_normals_multiple_mesh.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	i = 0
	while i < 44 :
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		i += 4
		
	ModelEditor.exit( True )
