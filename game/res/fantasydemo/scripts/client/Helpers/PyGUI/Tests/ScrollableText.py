import Helpers.PyGUI as PyGUI
import Keys

class TestWindow( PyGUI.Window ):
	
	def __init__( self, component ):
		PyGUI.Window.__init__( self, component )
		component.focus = True
		
	def handleKeyEvent( self, event ):
		handled = False
		if event.isKeyDown():
			if event.key == Keys.KEY_PGUP:
				self.component.textArea.script.scrollUp()
				handled = True
			elif event.key == Keys.KEY_PGDN:
				self.component.textArea.script.scrollDown()
				handled = True
		return handled

	
def test():
	wnd = TestWindow.create( "system/maps/col_white.bmp", bind=False )
	wnd.colour = (128,128,128,255)
	wnd.materialFX = "BLEND"
	wnd.width = 1.0
	wnd.height = 1.0
	
	wnd.textArea = PyGUI.ScrollableText.create()
	wnd.textArea.colour = (0,0,0,255)
	
	wnd.textArea.script.appendLine( "This is a line of text." )
	wnd.textArea.script.appendLine( "The quick brown fox jumped over the lazy dog." )
	wnd.textArea.script.appendLine( "A red line", (255,0,0,255) )
	wnd.textArea.script.appendLine( "\c00FF00FF;Multi \c00FFFFFF;coloured \cFFFF00FF;line!" )
	wnd.textArea.script.appendLine( "A bit more text." )
	wnd.textArea.script.appendLine( "And even more." )
	wnd.textArea.script.appendLine( "Press PGUP and PGDN to scroll..." )
	
	wnd.script.onBound()
	return wnd
