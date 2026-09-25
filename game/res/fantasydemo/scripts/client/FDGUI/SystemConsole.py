import BigWorld, GUI
import Helpers.PyGUI as PyGUI
import FDGUI

import FantasyDemo

from functools import partial

from Keys import *
from Helpers.PyGUI import ScrollableText

import math

# -----------------------------------------------------------------------------
# Method: v4col
# Description:
#		- Helper function to turn a vector3 into a full-on vector4 colour
# -----------------------------------------------------------------------------
def v4col(v3col, alpha = 255):
	return (v3col[0], v3col[1], v3col[2], alpha)


class SystemConsole( ScrollableText ):

	factoryString = "FDGUI.SystemConsole"

	def __init__( self, component ):
		ScrollableText.__init__( self, component )
		self.autoHideCount = 0
		self.autoHideTimeout = 10
		
	def fini( self ):
		pass
		
	def addMsg( self, msg, colourIndex ):
		self.appendLine( msg, self.colours[colourIndex] )


	def appendMsg( self, msg, colourIndex ):
		self.appendLine( msg, self.colours[colourIndex] )
		self.showNow()
		self.hideLater()
		
		
	def showNow( self ):
		self.component.visible = True
		self.autoHideCount += 1
		self.listeners.visibilityChanged( True )
		
		
	def hideNow( self ):
		self.autoHideCount += 1
		self.autoHideStart( self.autoHideCount )
		
		
	def hideLater( self, when = None ):
		self.autoHideCount += 1
		BigWorld.callback(
				self.autoHideTimeout if when is None else when,
				partial(self.autoHideStart, self.autoHideCount))

		
	def autoHideStart( self, count ):
		if count != self.autoHideCount: return
		self.component.visible = False
		self.listeners.visibilityChanged( False )
		

	def onBound( self ):
		ScrollableText.onBound( self )
		
		
	def onSave( self, dataSection ):
		ScrollableText.onSave( self, dataSection )

		# save data to section
		dataSection.writeVector3( 'textColour', 		self.colours[FDGUI.TEXT_COLOUR] )
		dataSection.writeVector3( 'otherWhisperColour', self.colours[FDGUI.TEXT_COLOUR_OTHER_WISHPER] )
		dataSection.writeVector3( 'otherSayColour',		self.colours[FDGUI.TEXT_COLOUR_OTHER_SAY] )
		dataSection.writeVector3( 'systemColour',		self.colours[FDGUI.TEXT_COLOUR_SYSTEM] )
		dataSection.writeVector3( 'youSayColour',		self.colours[FDGUI.TEXT_COLOUR_YOU_SAY] )
		dataSection.writeVector3( 'onlineColour',		self.colours[FDGUI.TEXT_COLOUR_ONLINE] )
		dataSection.writeVector3( 'offlineColour',		self.colours[FDGUI.TEXT_COLOUR_OFFLINE] )

		dataSection.writeFloat( 'timeout' , self.autoHideTimeout )		


	def onLoad( self, dataSection ):
		ScrollableText.onLoad( self, dataSection )

		# load from data section
		self.colours = [
			v4col(dataSection.readVector3( 'textColour', (0,128,255) )),
			v4col(dataSection.readVector3( 'otherWhisperColour', (32,128,255) )),
			v4col(dataSection.readVector3( 'otherSayColour', (64, 128, 255) )),
			v4col(dataSection.readVector3( 'systemColour', (255, 128, 0) )) ,
			v4col(dataSection.readVector3( 'youSayColour', (74, 255, 204) )),
			v4col(dataSection.readVector3( 'onlineSayColour', (51, 204, 0) )),
			v4col(dataSection.readVector3( 'offlineColour', (255, 0, 51) ))
			]
		self.autoHideTimeout = dataSection.readFloat( 'timeout' , 10.0 )
		
		


