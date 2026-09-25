import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_036_automatic_shader_assignment.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_036_automatic_shader_assignment_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_036_automatic_shader_assignment_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_036_automatic_shader_assignment_actions.png" )
	ModelEditor.captureModel( "tmp/test_036_automatic_shader_assignment_model.png" )
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_036_automatic_shader_assignment.animation" )
	ModelEditor.loadAnim( animName )
	
	i = 0
	ModelEditor.stopAnim()
	while i < 30:
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/%s_%02d.png" % (animName,  i ) )
		i += 3
		
	ModelEditor.exit( True )
