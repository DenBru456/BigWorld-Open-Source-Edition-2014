import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_045_edit_normals.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_045_edit_normals_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_045_edit_normals_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_045_edit_normals_actions.png" )
	ModelEditor.captureModel( "tmp/test_045_edit_normals_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_045_edit_normals.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	i = 0
	while i < ModelEditor.numAnimFrames():
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		i += 10
		
	ModelEditor.exit( True )

