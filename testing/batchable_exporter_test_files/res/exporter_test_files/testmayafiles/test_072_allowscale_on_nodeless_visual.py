import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_072_allowscale_on_nodeless_visual.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_072_allowscale_on_nodeless_visual_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_072_allowscale_on_nodeless_visual_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_072_allowscale_on_nodeless_visual_actions.png" )
	ModelEditor.captureModel( "tmp/test_072_allowscale_on_nodeless_visual_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmayafiles/test_072_allowscale_on_nodeless_visual_anim.animation" )
	ModelEditor.loadAnim( animName )
	
	i = 0
	ModelEditor.stopAnim()
	while i < ModelEditor.numAnimFrames():
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		i += 2
		
	ModelEditor.exit( True )
