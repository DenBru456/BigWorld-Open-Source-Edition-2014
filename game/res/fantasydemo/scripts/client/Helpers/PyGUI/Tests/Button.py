import Helpers.PyGUI as PyGUI


class TestWindow( PyGUI.Window ):

	@PyGUI.PyGUIEvent( "button", "onClick" )
	def buttonClicked( self ):
		print "Button Pushed"

	
def test():
	wnd = TestWindow.create( "system/maps/col_white.bmp", bind=False )
	wnd.colour = (128,128,128,255)
	wnd.materialFX = "BLEND"
	wnd.width = 1.0
	wnd.height = 1.0
	
	wnd.button = PyGUI.Button.create( label="Push Me", visualStates="button_test.xml" )
	
	wnd.script.onBound()
	return wnd
