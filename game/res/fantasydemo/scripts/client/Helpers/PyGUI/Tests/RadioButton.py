import Helpers.PyGUI as PyGUI


class TestWindow( PyGUI.Window ):

	@PyGUI.PyGUIEvent( "radio1A", "onActivate", "A" )
	@PyGUI.PyGUIEvent( "radio1B", "onActivate", "B" )
	@PyGUI.PyGUIEvent( "radio1C", "onActivate", "C" )
	def group1OptionSelected( self, item ):
		print "Selected item", item, "from group 1."
		
	@PyGUI.PyGUIEvent( "radio2A", "onActivate", "A" )
	@PyGUI.PyGUIEvent( "radio2B", "onActivate", "B" )
	@PyGUI.PyGUIEvent( "radio2C", "onActivate", "C" )
	def group2OptionSelected( self, item ):
		print "Selected item", item, "from group 2."

	
def test():
	wnd = TestWindow.create( "system/maps/col_white.bmp", bind=False )
	wnd.colour = (128,128,128,255)
	wnd.materialFX = "BLEND"
	wnd.width = 1.0
	wnd.height = 1.5
	
	wnd.radio1A = PyGUI.RadioButton.create( label="Group 1, Item A", groupName="group1", visualStates="checkbox_test.xml" )
	wnd.radio1B = PyGUI.RadioButton.create( label="Group 1, Item B", groupName="group1", visualStates="checkbox_test.xml" )
	wnd.radio1C = PyGUI.RadioButton.create( label="Group 1, Item C", groupName="group1", visualStates="checkbox_test.xml" )
	
	wnd.radio1A.verticalPositionMode = "CLIP"
	wnd.radio1B.verticalPositionMode = "CLIP"
	wnd.radio1C.verticalPositionMode = "CLIP"
	
	wnd.radio1A.position.y = +0.75
	wnd.radio1B.position.y = +0.50
	wnd.radio1C.position.y = +0.25
	
	
	wnd.radio2A = PyGUI.RadioButton.create( label="Group 2, Item A", groupName="group2", visualStates="checkbox_test.xml" )
	wnd.radio2B = PyGUI.RadioButton.create( label="Group 2, Item B", groupName="group2", visualStates="checkbox_test.xml" )
	wnd.radio2C = PyGUI.RadioButton.create( label="Group 2, Item C", groupName="group2", visualStates="checkbox_test.xml" )
	
	wnd.radio2A.verticalPositionMode = "CLIP"
	wnd.radio2B.verticalPositionMode = "CLIP"
	wnd.radio2C.verticalPositionMode = "CLIP"
	
	wnd.radio2A.position.y = -0.25
	wnd.radio2B.position.y = -0.50
	wnd.radio2C.position.y = -0.75
	
	wnd.script.onBound()
	return wnd
