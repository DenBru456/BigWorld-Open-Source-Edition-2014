import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_037_floating_bones_skin.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_037_floating_bones_skin_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_037_floating_bones_skin_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_037_floating_bones_skin_actions.png" )
	ModelEditor.captureModel( "tmp/test_037_floating_bones_skin_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_037_floating_bones_skin.animation" )
	ModelEditor.loadAnim( animName )
	
	i = 0
	ModelEditor.stopAnim()
	while i < ModelEditor.numAnimFrames():
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		i += 5
		
	ModelEditor.exit( True )
