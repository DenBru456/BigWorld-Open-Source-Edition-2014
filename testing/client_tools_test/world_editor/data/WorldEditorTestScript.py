#you must define LOCATION 
import WorldEditor

def run():
 WorldEditor.pause( 1 )
 WorldEditor.showEditorRenderables( 0 )
 WorldEditor.showUDOLinks( 0 )
 WorldEditor.goToBookmark( LOCATION )
 WorldEditor.setReadyForScreenshotCallback( captureSceneAndQuit )

def captureSceneAndQuit():
 WorldEditor.captureScene( LOCATION )
 WorldEditor.exit( True )
 
 