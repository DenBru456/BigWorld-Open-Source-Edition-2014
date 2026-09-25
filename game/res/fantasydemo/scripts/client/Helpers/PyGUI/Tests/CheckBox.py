import Helpers.PyGUI as PyGUI


class TestWindow( PyGUI.Window ):

	@PyGUI.PyGUIEvent( "check1", "onActivate", True )
	@PyGUI.PyGUIEvent( "check1", "onDeactivate", False )
	def check1Activated( self, activated ):
		print "Checkbox 1 Clicked", activated
		
	@PyGUI.PyGUIEvent( "check2", "onActivate", True )
	@PyGUI.PyGUIEvent( "check2", "onDeactivate", False )
	def check2Activated( self, activated ):
		print "Checkbox 2 Clicked", activated

	
def test():
	wnd = TestWindow.create( "system/maps/col_white.bmp", bind=False )
	wnd.colour = (128,128,128,255)
	wnd.materialFX = "BLEND"
	wnd.width = 1.0
	wnd.height = 1.0
	
	wnd.check1 = PyGUI.CheckBox.create( label="Check Box 1", visualStates="checkbox_test.xml" )
	wnd.check2 = PyGUI.CheckBox.create( label="Check Box 2", visualStates="checkbox_test.xml" )
	
	wnd.check1.position.y = +0.25
	wnd.check2.position.y = -0.25
	
	wnd.script.onBound()
	return wnd
