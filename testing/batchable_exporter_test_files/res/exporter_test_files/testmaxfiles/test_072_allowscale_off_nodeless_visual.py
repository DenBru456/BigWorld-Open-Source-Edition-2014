import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_072_allowscale_off_nodeless_visual.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_072_allowscale_off_nodeless_visual_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_072_allowscale_off_nodeless_visual_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_072_allowscale_off_nodeless_visual_actions.png" )
	ModelEditor.captureModel( "tmp/test_072_allowscale_off_nodeless_visual_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_072_allowscale_off_nodeless_visual.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	ModelEditor.playAnimFrame( 1 )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	ModelEditor.captureModel( "tmp/" + animName + "_" + str( 1 ) + ".png" )
	
	ModelEditor.playAnimFrame( 10 )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	ModelEditor.captureModel( "tmp/" + animName + "_" + str( 10 ) + ".png" )

	ModelEditor.playAnimFrame( 29 )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	ModelEditor.captureModel( "tmp/" + animName + "_" + str( 29 ) + ".png" )	
		
	ModelEditor.exit( True )

