import Helpers.PyGUI as PyGUI


class TestWindow( PyGUI.Window ):

	@PyGUI.PyGUIEvent( "slider", "onValueChanged" )
	def sliderValueChanged( self, value ):
		print "Slider Value Changed", value
		
	@PyGUI.PyGUIEvent( "slider", "onBeginDrag" )
	def sliderBeginDrag( self, value ):
		print "Slider begin drag", value
		
	@PyGUI.PyGUIEvent( "slider", "onEndDrag" )
	def sliderEndDrag( self, value ):
		print "Slider end drag", value

	
def test():
	wnd = TestWindow.create( "system/maps/col_white.bmp", bind=False )
	wnd.colour = (128,128,128,255)
	wnd.materialFX = "BLEND"
	wnd.width = 1.0
	wnd.height = 1.0
	
	wnd.slider = PyGUI.Slider.create( visualStates="slider_test.xml" )
	
	wnd.script.onBound()
	return wnd
