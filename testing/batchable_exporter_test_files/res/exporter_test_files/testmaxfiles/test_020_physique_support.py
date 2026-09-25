import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_020_physique_support.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_020_physique_support_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_020_physique_support_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_020_physique_support_actions.png" )
	ModelEditor.captureModel( "tmp/test_020_physique_support_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_020_physique_support.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	i = 0
	while i < ModelEditor.numAnimFrames():
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		i += 3
		
	ModelEditor.exit( True )

