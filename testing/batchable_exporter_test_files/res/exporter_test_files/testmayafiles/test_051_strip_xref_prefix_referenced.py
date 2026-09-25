import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_051_strip_xref_prefix_referenced.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_051_strip_xref_prefix_referenced_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_051_strip_xref_prefix_referenced_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_051_strip_xref_prefix_referenced_actions.png" )
	ModelEditor.captureModel( "tmp/test_051_strip_xref_prefix_referenced_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmayafiles/test_051_strip_xref_prefix_referenced_anim.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	i = 0
	while i < ModelEditor.numAnimFrames():
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		i += 3
		
	ModelEditor.exit( True )