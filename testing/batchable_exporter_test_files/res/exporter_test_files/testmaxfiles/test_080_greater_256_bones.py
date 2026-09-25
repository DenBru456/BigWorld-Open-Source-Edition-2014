import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_080_greater_256_bones.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_080_greater_256_bones_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_080_greater_256_bones_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_080_greater_256_bones_actions.png" )
	ModelEditor.captureModel( "tmp/test_080_greater_256_bones_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_080_greater_256_bones.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	for i in range(0,  6 ):
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		
	ModelEditor.exit( True )
