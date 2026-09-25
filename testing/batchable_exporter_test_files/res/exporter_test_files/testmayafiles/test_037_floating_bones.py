import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_037_floating_bones.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_037_floating_bones_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_037_floating_bones_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_037_floating_bones_actions.png" )
	ModelEditor.captureModel( "tmp/test_037_floating_bones_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmayafiles/test_037_floating_bones_anim.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	i = 0
	while i < 50:
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		i += 4
		
	ModelEditor.exit( True )