import BigWorld
import GUI
import Helpers.PyGUI as PyGUI

import Cursor

from Helpers.PyGUI import PyGUIEvent

class InGameMenu( PyGUI.Window ):

	factoryString = "FDGUI.InGameMenu"

	def __init__( self, component ):
		PyGUI.Window.__init__( self, component )
		self.component.focus = True
		self.component.moveFocus = True
		self.component.crossFocus = True


	@PyGUIEvent( "menu.graphicsOptionsButton", "onClick" )
	def graphicsOptionsClick( self ):
		print "graphicsOptionsClick"


	@PyGUIEvent( "menu.audioOptionsButton", "onClick" )
	def audioOptionsClick( self ):
		print "audioOptionsClick"


	@PyGUIEvent( "menu.logoutButton", "onClick" )
	def logoutClick( self ):
		import FantasyDemo
		FantasyDemo.disconnectFromServer()


	@PyGUIEvent( "menu.quitButton", "onClick" )
	def quitClick( self ):
		import FantasyDemo
		FantasyDemo.showAdvertisingScreen( 30.0, BigWorld.quit )


	@PyGUIEvent( "menu.resumeButton", "onClick" )
	def resumeClick( self ):
		self.active( False )


	# Override these methods so that everything under will not receive events
	def handleMouseClickEvent( self, *args ):
		return True

	def handleMouseButtonEvent( self, *args ):
		return True

	def handleMouseEvent( self, *args ):
		return True

	def handleMouseEnterEvent( self, *args ):
		return True

	def handleMouseLeaveEvent( self, *args ):
		return True


	def active( self, show ):
		if self.isActive == show:
			return

		PyGUI.Window.active( self, show )		
		Cursor.showCursor( show )
		if show:
			GUI.reSort()

