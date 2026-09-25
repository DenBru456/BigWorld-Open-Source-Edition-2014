import BigWorld, GUI
import Helpers.PyGUI as PyGUI
import FDGUI

import FantasyDemo

from functools import partial

from Keys import *
from Helpers.PyGUI import PyGUIBase

import math

# -----------------------------------------------------------------------------
# Method: v4col
# Description:
#		- Helper function to turn a vector3 into a full-on vector4 colour
# -----------------------------------------------------------------------------
def v4col(v3col, alpha = 255):
	return (v3col[0], v3col[1], v3col[2], alpha)

class ChatConsole( PyGUIBase ):

	factoryString = "FDGUI.ChatConsole"

	def __init__( self, component ):
		PyGUIBase.__init__( self, component )
		self.editing = False
		self.autoHideCount = 0
		
	def fini( self ):
		pass		
		
	def clear( self ):
		self.component.console.script.clear()
		
	def handleConsoleInput( self, msg ):
		if msg == '':
			self.hideNow()
		else:
			if BigWorld.player() and hasattr( BigWorld.player(), "handleConsoleInput" ):
				BigWorld.player().handleConsoleInput( msg )
			self.showNow()
			self.hideLater()
			
			
	def handleEscapeKey( self ):
		self.setEditText( "" )
		self.hideNow()
		
		
	def edit( self, ison, nohide = False, initialEditText = "" ):
		if self.editing == ison:
			return

		self.setEditText( initialEditText )
		self.editing = ison
		self.component.visible = True
		
		self.component.console.script.enableEditField( ison )
		PyGUI.setFocusedComponent( self.component.console.editField if ison else None )
		
		if ison:
			self.showNow()
		elif not nohide:
			self.hideLater()
			
	def setEditText( self, text ):
		self.component.console.script.setEditText( text )

		
	def addMsg( self, msg, colourIndex ):
		self.component.console.script.appendLine( msg, self.colours[colourIndex] )
		self.showNow()
		self.hideLater()


	def appendMsg( self, msg, colourIndex ):
		self.component.console.script.appendLine( msg, self.colours[colourIndex] )
		self.showNow()
		self.hideLater()
		

	def hideLater( self, when = None):
		if self.autoHideEnable and not self.editing:
			self.autoHideCount += 1
			BigWorld.callback(
				self.autoHideTimeout if when is None else when,
				partial(self.autoHideStart, self.autoHideCount))


	def autoHideStart( self, count ):
		# make sure we haven't been cancelled
		if self.editing or count != self.autoHideCount: return

		# ok start fading ourselves out then
		self.alphaShader.alpha = 0
		self.alphaShader.speed = 1.0
		#if not visible make it not get key/mouse events
		self.component.focus = False
		self.component.moveFocus = False
		self.component.crossFocus = False
		self.component.mouseButtonFocus = False
		self.listeners.visibilityChanged( False )

		# could add another callback for when we're totally faded out,
		# but it's not actually necessary...
		
		
	def hideNow( self ):
		# stop editing if we were
		if self.editing:
			self.edit( False, True )

		# and start fading out immediately
		self.autoHideCount += 1
		self.autoHideStart(self.autoHideCount)


	def showNow( self ):
		self.autoHideCount += 1
		self.alphaShader.alpha = 1
		self.alphaShader.speed = 0
		self.component.visible = True
		self.component.focus = True
		self.component.moveFocus = True
		self.component.crossFocus = True
		self.component.mouseButtonFocus = True
		self.component.console.buffer.script.setScrollIndex(0)

		self.listeners.visibilityChanged( True )
		
		
	def isShowing( self ):
		return self.alphaShader.alpha > 0


	def handleMouseButtonEvent( self, comp, event ):
		if self.isShowing():
			PyGUI.setFocusedComponent( self.component.console.editField )
			return True
		else:
			return False
		
		
	def onRecreateDevice( self ):
		self.component.console.script.onRecreateDevice()
		
		
	def onBound( self ):
		PyGUIBase.onBound( self )
		
		self.component.console.script.onBound()
		self.component.console.script.handleConsoleInput = self.handleConsoleInput
		self.component.console.script.handleEscapeKey = self.handleEscapeKey
		self.component.focus = True
		
		# set the auto hide counter
		self.autoHideCount = 0
		
		# set chat window alpha shader for fading out
		self.alphaShader = GUI.AlphaShader('ALL')
		self.alphaShader.alpha = 0
		self.alphaShader.speed = 0
		self.component.alpha = self.alphaShader
		
		self.edit( False )
		self.component.console.script.enableEditField( False )
		self.hideNow()
		
		
		
	def onSave( self, dataSection ):
		PyGUIBase.onSave( self, dataSection )

		# save data to section
		dataSection.writeVector3( 'textColour',
				self.colours[FDGUI.TEXT_COLOUR] )
		dataSection.writeVector3( 'otherWhisperColour',
				self.colours[FDGUI.TEXT_COLOUR_OTHER_WISHPER] )
		dataSection.writeVector3( 'otherSayColour',
				self.colours[FDGUI.TEXT_COLOUR_OTHER_SAY] )
		dataSection.writeVector3( 'systemColour',
				self.colours[FDGUI.TEXT_COLOUR_SYSTEM] )
		dataSection.writeVector3( 'youSayColour',
				self.colours[FDGUI.TEXT_COLOUR_YOU_SAY] )
		dataSection.writeVector3( 'onlineColour',
				self.colours[FDGUI.TEXT_COLOUR_ONLINE] )
		dataSection.writeVector3( 'offlineColour',
				self.colours[FDGUI.TEXT_COLOUR_OFFLINE] )

		dataSection.writeBool( 'auto_hide' , self.autoHideEnable )
		dataSection.writeFloat( 'timeout' , self.autoHideTimeout )
		dataSection.writeVector3( 'colour', self.colour )
		dataSection.writeFloat( 'alpha', self.alpha )
		dataSection.writeBool( 'editable', self.editable )
		dataSection.writeInt( 'buffer_size', self.bufferSize )
		dataSection.writeInt( 'horizontal_padding', self.hpadding )
		dataSection.writeInt( 'vertical_padding', self.vpadding )
		dataSection.writeString( 'texture', self.texture )
		dataSection.writeBool( 'invert', self.invert )


	def onLoad( self, dataSection ):
		PyGUIBase.onLoad( self, dataSection )

		# load from data section
		self.colours = [
			v4col(dataSection.readVector3( 'textColour', (0,128,255) )),
			v4col(dataSection.readVector3( 'otherWhisperColour', (32,128,255) )),
			v4col(dataSection.readVector3( 'otherSayColour', (64, 128, 255) )),
			v4col(dataSection.readVector3( 'systemColour', (255, 128, 0) )) ,
			v4col(dataSection.readVector3( 'youSayColour', (74, 255, 204) )),
			v4col(dataSection.readVector3( 'onlineSayColour', (51, 204, 0) )),
			v4col(dataSection.readVector3( 'offlineColour', (255, 0, 51) ))]
		self.autoHideEnable = dataSection.readBool( 'auto_hide' , 1 )
		self.autoHideTimeout = dataSection.readFloat( 'timeout' , 10.0 )
		self.colour = dataSection.readVector3( 'colour', (0, 0, 0) )
		self.alpha = dataSection.readFloat( 'alpha', 0 )
		self.editable = dataSection.readBool( 'editable', False )
		self.bufferSize = dataSection.readInt( 'buffer_size', 250 )
		self.hpadding = dataSection.readInt( 'horizontal_padding', 0 )
		self.vpadding = dataSection.readInt( 'vertical_padding', 0 )
		self.texture = dataSection.readString( 'texture', 'system/maps/aid_null.bmp' )		
		self.invert = dataSection.readBool( 'invert', False )	


