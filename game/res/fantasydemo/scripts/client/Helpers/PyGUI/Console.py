import BigWorld, GUI
import Keys

import math

from Listeners import registerDeviceListener
from PyGUIEvent import PyGUIEvent
from PyGUIBase import PyGUIBase

MAX_HISTORY_ENTRIES = 50

class Console( PyGUIBase ):

	factoryString = "PyGUI.Console"

	@staticmethod
	def create():
		component = GUI.Window( "system/maps/col_white.bmp" )
		component.colour = (0, 0, 0, 255)
		component.materialFX = "SOLID"
		component.height = 0.75
		component.width = 1.5

		component.addChild( ScrollableText.create(), "buffer" )
		component.buffer.colour = (0,0,0,0)
		component.buffer.widthMode = "CLIP"
		component.buffer.width = 2.0
		component.buffer.height = 1.8
		component.buffer.verticalAnchor = "TOP"
		component.buffer.verticalPositionMode = "CLIP"
		component.buffer.position.y = 1.0

		component.addChild( EditField.create(), "editField" )
		component.editField.colour = (64,64,64,255)
		component.editField.verticalPositionMode = "CLIP"
		component.editField.verticalAnchor = "BOTTOM"
		component.editField.position.y = -1.0
		component.editField.height = 0.2
		component.editField.widthMode = "CLIP"
		component.editField.width = 2.0
		component.script = Console( component )
		
		component.script.onBound()
		return component


	def __init__( self, component=None ):
		PyGUIBase.__init__( self, component )

		self.__history = []
		self.__historyShown = -1

		registerDeviceListener( self )


	def enableEditField( self, state ):
		self.component.editField.script.setEnabled( state )
		
		
	def clear( self ):
		self.component.buffer.script.clear()

	def editFieldChangeFocus( self, editField, state ):
		try:
			languageIndicator = self.component.languageIndicator
			languageIndicator.visible = state and editField.enabled
		except AttributeError:
			pass

	@PyGUIEvent( "editField", "onEnter" )
	def _onEnterText( self, text ):
		self.component.editField.script.setText("")
		if len(text) > 0:
			self._insertHistory( text )
		self.handleConsoleInput( text )

	@PyGUIEvent( "editField", "onEscape" )
	def _onEscape( self ):
		self.handleEscapeKey()

	def handleConsoleInput( self, msg ):
		pass
		
	def handleEscapeKey( self ):
		pass

	def getMaxLines( self ):
		return self.component.buffer.script.getMaxLines()


	def setMaxLines( self, maxLines ):
		# TODO: refresh buffer
		self.component.editField.script.setMaxLines( maxLines )

	def appendLine( self, msg, colour ):
		self.component.buffer.script.appendLine( msg, colour )


	def setEditText( self, text ):
		self.component.editField.script.setText( text )

		
	def getEditText( self ):
		return self.component.editField.script.getText()


	def fini( self ):
		if self.editable:
			self.editCallback( None )
		self.active(False)


	def enableEdit( self ):
		self.component.editField.script.setKeyFocus( True )


	def disableEdit( self ):
		self.component.editField.script.setKeyFocus( False )


	def handleEditFieldKeyEvent( self, event ):
		handled = False
		if event.isKeyDown():
			if event.key == Keys.KEY_PGDN:
				self.component.buffer.script.scrollDown()
				handled = True
			elif event.key == Keys.KEY_PGUP:
				self.component.buffer.script.scrollUp()
				handled = True
			elif event.key == Keys.KEY_UPARROW:
				editText = self.getEditText()
				if len(self.__history) > 0:
					if self.__historyShown == -1:
						self.__history.insert( 0, editText )
						self.__historyShown = 1
					else:
						if len( editText ) > 0:
							self.__history[ self.__historyShown ] = editText
						self.__historyShown += 1
					self._showHistory()

				handled = True
			elif event.key == Keys.KEY_DOWNARROW:
				editText = self.getEditText()
				if len(self.__history) > 0:
					if self.__historyShown == -1:
						self.__history.insert( 0, editText )
						self.__historyShown = len(self.__history) - 1
					else:
						if len(editText) > 0:
							self.__history[self.__historyShown] = editText
						self.__historyShown -= 1

					self._showHistory()

				handled = True

		return handled

		
	def _insertHistory( self, s ):
		if len(s) > 0:
			if len(self.__history) > 0 and self.__historyShown != -1:
				self.__history[ 0 ] = s
			else:
				self.__history.insert( 0, s )
		else:
			if len(self.__history) > 0 and len(self.__history[0]) == 0:
				self.__history.pop(0)

		# clamp history
		if len(self.__history) > MAX_HISTORY_ENTRIES:
			self.__history.pop()

		self.__historyShown = -1


	def _showHistory( self ):
		if self.__historyShown < 0:
			self.__historyShown = len(self.__history) - 1
		elif self.__historyShown == len(self.__history):
			 self.__historyShown = 0

		self.setEditText( self.__history[ self.__historyShown ] );


	def onBound( self ):
		PyGUIBase.onBound( self )

		self.component.editField.script.onBound()
		self.component.editField.script.setExternalKeyEventHandler( self.handleEditFieldKeyEvent )



	def onRecreateDevice( self ):
		self.component.editField.script.onRecreateDevice()
		self.component.editField.script.fitVertically()
		self.component.editField.heightMode = "CLIP"
		self.component.buffer.heightMode = "CLIP"
		self.component.buffer.height = 2.0 - self.component.editField.height


	def isShowing( self ):
		return self.alphaShader.value > 0

