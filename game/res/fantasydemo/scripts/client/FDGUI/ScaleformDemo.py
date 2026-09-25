import BigWorld
import GUI
import FantasyDemo
import Scaleform
import Keys

import Helpers.PyGUI as PyGUI

import weakref

from bwdebug import *

class ScaleformDemo( PyGUI.PyGUIBase ):

	# (filename, backgroundAlpha)
	MOVIES = [
		("d3d9guide.swf",			0.1),
		("fieldgenerator.swf",		0.5),
		("fireworks.swf",			1.0),
	]
	
	@staticmethod
	def create( movieIdx ):
		movieName, backgroundAlpha = ScaleformDemo.MOVIES[ movieIdx ]

		# Disable world drawing temporarily to avoid warnings about hitting the main thread.
		wde = BigWorld.worldDrawEnabled()
		BigWorld.worldDrawEnabled( False )		
		view, movie = Scaleform.createMovieInstance( "scaleform/" + movieName )
		BigWorld.worldDrawEnabled( wde )

		if view is None:
			ERROR_MSG( "Error loading Scaleform movie '%s'" % (movieName,) )
			return None
			
		view.backgroundAlpha = backgroundAlpha
		component = GUI.Flash( view )
		component.width = 2.0
		component.height = 2.0
		component.materialFX = "BLEND"
		component.focus = True
		component.mouseButtonFocus = True
		component.crossFocus = True
		component.moveFocus = True
		component.dragFocus = True
		component.script = ScaleformDemo( movieIdx, component )
		
		return component

	def __init__( self, movieIdx, component ):
		PyGUI.PyGUIBase.__init__( self, component )
		self.movieIdx = movieIdx
		
	def handleKeyEvent( self, event ):
	
		# Don't pass ScaleForm demo keys into flash
		actionName = FantasyDemo.rds.keyBindings.getActionForKeyState( event.key )
		if actionName in [ "EscapeKey", "ScaleformDemo" ]:
			return False
		
		return self.component.movie.handleKeyEvent( event )
		
		
	def handleMouseButtonEvent( self, comp, event ):
		self.component.movie.handleMouseButtonEvent( event )
		return self.component.movie.hitTest( event.cursorPosition )


	def handleMouseEvent( self, comp, event ):
		self.component.movie.handleMouseEvent( event )
		return self.component.movie.hitTest( event.cursorPosition )
		
		
	def allowAutoDefocus( self ):
		return False


