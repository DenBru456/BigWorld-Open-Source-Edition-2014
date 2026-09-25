import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_003b_advanced_preferences.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_003b_advanced_preferences_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_003b_advanced_preferences_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_003b_advanced_preferences_actions.png" )
	ModelEditor.captureModel( "tmp/test_003b_advanced_preferences_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_003b_advanced_preferences.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	for i in range(0,  ModelEditor.numAnimFrames() ):
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		
	ModelEditor.exit( True )
