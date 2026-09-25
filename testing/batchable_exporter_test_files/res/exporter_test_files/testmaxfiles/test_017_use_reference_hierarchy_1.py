import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_017_use_reference_hierarchy_1.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_017_use_reference_hierarchy_1_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_017_use_reference_hierarchy_1_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_017_use_reference_hierarchy_1_actions.png" )
	ModelEditor.captureModel( "tmp/test_017_use_reference_hierarchy_1_model.png" )
	
	
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_017_use_reference_hierarchy_1.animation" )
	ModelEditor.loadAnim( animName )
	
	fileName = "test_017_use_reference_hierarchy_1_with_"
	
	ModelEditor.stopAnim()
	for i in range(0,  30 ):
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/" + fileName + animName + "_" + str( i ) + ".png" )
		
	animName = ModelEditor.addAnim( "exporter_test_files/testmaxfiles/test_017_use_reference_hierarchy_2.animation" )
	ModelEditor.loadAnim( animName )
	
	ModelEditor.stopAnim()
	for i in range(0,  30 ):
		ModelEditor.playAnimFrame( i )
		yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
		ModelEditor.captureModel( "tmp/" + fileName + animName + "_" + str( i ) + ".png" )
		
	ModelEditor.exit( True )

