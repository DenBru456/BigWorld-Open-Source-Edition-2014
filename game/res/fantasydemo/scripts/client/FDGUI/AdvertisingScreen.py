import BigWorld
import GUI
import Helpers.PyGUI as PyGUI
from Helpers.PyGUI import PyGUIEvent


class AdvertisingScreen( PyGUI.EscapableWindow ):

	factoryString = "FDGUI.AdvertisingScreen"

	def __init__( self, component ):
		PyGUI.EscapableWindow.__init__( self, component )
		self.component.script = self
		self.component.focus = True
		self.component.moveFocus = True
		self.component.crossFocus = True


	def onBound( self ):
		PyGUI.EscapableWindow.onBound( self )
		self.doLayout( None )


	def doLayout( self, parent ):
		screenWidth, screenHeight = BigWorld.screenSize()

		screenAspectRatio = screenWidth / screenHeight
		graphicAspectRatio = float(self.component.advertisingGraphic.texture.width) / \
								float(self.component.advertisingGraphic.texture.height)

		self.component.advertisingGraphic.width = min( 2.0, 2.0 * (graphicAspectRatio / screenAspectRatio) )
		self.component.advertisingGraphic.height = min( 2.0, 2.0 * (screenAspectRatio / graphicAspectRatio) )


	@PyGUIEvent( "advertisingGraphic.closeButton", "onClick" )
	def closeButtonClick( self ):
		if self.onEscape is not None:
			self.onEscape()



