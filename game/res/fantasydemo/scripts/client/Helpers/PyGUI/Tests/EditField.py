import Helpers.PyGUI as PyGUI


class TestWindow( PyGUI.Window ):

	@PyGUI.PyGUIEvent( "editField", "onEnter" )
	def editFieldEnterPressed( self, text ):
		print "You entered:", text
		self.component.editField.script.setText( "" )
		
	@PyGUI.PyGUIEvent( "editField", "onChangeFocus" )
	def editFieldOnChangeFocus( self, state ):
		print "Edit Field Focus Changed", state

	
def test():
	wnd = TestWindow.create( "system/maps/col_white.bmp", bind=False )
	wnd.colour = (128,128,128,255)
	wnd.materialFX = "BLEND"
	wnd.width = 1.0
	wnd.height = 1.0
	
	wnd.editField = PyGUI.EditField.create( texture="system/maps/col_black.bmp" )
	wnd.editField.script.enableIME = True
	
	wnd.editField.indicator = PyGUI.LanguageIndicator.create()
	wnd.editField.indicator.horizontalPositionMode = "CLIP"
	wnd.editField.indicator.horizontalAnchor = "RIGHT"
	wnd.editField.indicator.position.x = 1
	
	wnd.script.onBound()
	return wnd
