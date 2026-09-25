import BigWorld
import ModelEditor
from Helpers.BWCoroutine import *

def run():
	#ModelEditor.loadModel( "exporter_test_files/testmaxfiles/test_027_multi_faceted_portals_portal.model" )
	ModelEditor.onEditorReady( captureModelAndQuit )

def captureModelAndQuit():
	captureModelAndQuitCoroutine().run()
	
@BWCoroutine
def captureModelAndQuitCoroutine():
	yield BWWaitForCondition( lambda: ModelEditor.isModelLoaded() )
	yield BWWaitForCondition( lambda: ModelEditor.canCaptureModel() )
	
	ModelEditor.capturePanel( "Display", "tmp/test_027_multi_faceted_portals_portal_display.png" )
	#ModelEditor.capturePanel( "Object", "tmp/test_027_multi_faceted_portals_portal_objects.png" )
	ModelEditor.capturePanel( "Actions", "tmp/test_027_multi_faceted_portals_portal_actions.png" )
	ModelEditor.captureModel( "tmp/test_027_multi_faceted_portals_portal_model.png" )
	
	ModelEditor.exit( True )
