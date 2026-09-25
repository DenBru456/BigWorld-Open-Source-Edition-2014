import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_071_cue_tracks.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_071_cue_tracks_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_071_cue_tracks_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_071_cue_tracks_actions.png" )
	ModelEditor.captureModel( "tmp/test_071_cue_tracks_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_071_cue_tracks.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	i = 0
	while i < ModelEditor.numAnimFrames():
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%03d.png" % (animName,  i ) )
		i += 10
		
	ModelEditor.exit( True )