import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_008_custom_bsp_on_softskinned_object_off.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_008_custom_bsp_on_softskinned_object_off_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_008_custom_bsp_on_softskinned_object_off_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_008_custom_bsp_on_softskinned_object_off_actions.png" )
	ModelEditor.captureModel( "tmp/test_008_custom_bsp_on_softskinned_object_off_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_008_custom_bsp_on_softskinned_object.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	for i in range(0,  ModelEditor.numAnimFrames() ):
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		
	ModelEditor.exit( True )

