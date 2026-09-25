import BigWorld, GUI, Keys

from PyGUIBase import PyGUIBase
import copy

import BigWorld
import GUI
import Math
import Keys

import Helpers.PyGUI.IME
import Utils

from Helpers.PyGUI.Listeners import registerDeviceListener
from Helpers.PyGUI.Utils import BlinkingCursor
from Helpers.PyGUI.Utils import blinkingColourProvider
from Helpers.PyGUI.Utils import getHPixelScalar, getVPixelScalar
from Helpers.PyGUI.Utils import CURSOR_WIDTH
from Helpers.PyGUI import PyGUIBase

from Helpers.PyGUI.FocusManager import *

import weakref

SCROLL_SKIP_AMOUNT 	= 8 		# Amount to jump when the cursor hits one of the sides

DEFAULT_TEXT_COLOUR_ACTIVE = ( 255, 255, 255, 255 )
DEFAULT_TEXT_COLOUR_INACTIVE = ( 155, 155, 155, 255 )

def gotComposition():
	return len(BigWorld.ime.composition) > 0

def skipWordRight( s, cursorPos ):
	s = unicode(s)
	i = cursorPos

	# Find the next whitespace
	while i < len(s) and s[i] not in Utils.WHITESPACE:
		i += 1

	# Now skip to the end of the whitespace
	while i < len(s) and s[i] in Utils.WHITESPACE:
		i += 1

	return i

def skipWordLeft( s, cursorPos ):
	s = unicode(s)
	i = cursorPos-1

	# Find the previous first non-whitespace
	while i > 0 and s[i] in Utils.WHITESPACE:
		i -= 1

	# Now skip to the first letter of this word
	while i > 0 and s[i-1] not in Utils.WHITESPACE:
		i -= 1

	return i

def skipWord( s, cursorPos, direction ):
	if direction > 0:
		return skipWordRight( s, cursorPos )
	else:
		return skipWordLeft( s, cursorPos )


class EditField( PyGUIBase ):

	factoryString = "PyGUI.EditField"

	def __init__( self, component = None  ):
		PyGUIBase.__init__( self, component )

		self.cursorIndex = 0
		self.scrollInPixels = 0

		self.onEnter   = None
		self.onEscape  = None
		self.onChangeFocus = None
		self.onChangeValue = None
		self.maxLength = 256
		self.enabled = True
		self.enableIME = False
		self.focusViaMouse = True
		self.focusObserver = None
		self.shouldAdjustClipping = False
		self.__externalKeyEventHandler = None
		self.__allowAutoDefocus = True

		self.autoSelectionFonts = [ "default_medium.font" ]
		self.idealVisibleCharacters = 80
		
		registerDeviceListener( self )


	def setExternalKeyEventHandler( self, cb ):
		self.__externalKeyEventHandler = cb


	def onBound( self ):
	
		# Remove any existing cursor as we want to set this up ourselves.
		if hasattr( self.component, "cursor" ):
			self.component.delChild( self.component.cursor )

		# Text
		text = self.component.text
		text.horizontalAnchor = "LEFT"
		text.horizontalPositionMode = "PIXEL"
		text.position.x = 0
		text.colour = self.inactiveColour
		
		if len(self.autoSelectionFonts) == 0:
			self.autoSelectionFonts = [ self.component.text.font ]

		# Cursor
		self.component.cursor = BlinkingCursor.create()
		self._updateCursor()
		self.component.cursor.script.enable( False )

		PyGUIBase.onBound( self )
		
		self._selectFontBestMatch()

	def active( self, state ):
		PyGUIBase.active( self, state )
		if not state:
			self.focus( False )
			if isFocusedComponent( self.component ):
				setFocusedComponent( None )
		
	def setEnabled( self, state ):
		self.enabled = state
		if not state:
			self.focus( False )


	def fitVertically( self ):
		heightMode = self.component.heightMode
		self.component.heightMode = "PIXEL"
		_, self.component.height = self.component.text.stringDimensions("W")
		self.component.height *= getVPixelScalar()
		self.component.heightMode = heightMode


	def setText( self, text ):
		c = self.component.text
		c.text = unicode( text[:self.maxLength] )
		self.scrollInPixels = 0
		self.component.scroll.x = 0
		self.cursorIndex = len( c.text )
		self._updateCursor()


	def getText( self ):
		return self.component.text.text


	def onLoad( self, dataSection ):
		PyGUIBase.onLoad( self, dataSection )

		self.maxLength = dataSection.readInt( "maxLength", self.maxLength )
		self.focusViaMouse = dataSection.readBool( "focusViaMouse", True )
		self.enableIME = dataSection.readBool( "enableIME", False )
		self.shouldAdjustClipping = dataSection.readBool( "shouldAdjustClipping", False )
		self.activeColour = dataSection.readVector4( "activeColour", DEFAULT_TEXT_COLOUR_ACTIVE )
		self.inactiveColour = dataSection.readVector4( "inactiveColour", DEFAULT_TEXT_COLOUR_INACTIVE )
		self.__allowAutoDefocus = dataSection.readBool( "allowAutoDefocus", True )
		
		self.idealVisibleCharacters = dataSection.readInt( 'idealVisibleCharacters', self.idealVisibleCharacters )
		fonts = dataSection.readStrings( 'autoFont' )
		if len(fonts) > 0:
			self.autoSelectionFonts = fonts
		


	def onSave( self, dataSection ):
		PyGUIBase.onSave( self, dataSection )

		dataSection.writeInt( "maxLength", self.maxLength )
		dataSection.writeBool( "focusViaMouse", self.focusViaMouse )
		dataSection.writeBool( "enableIME", self.enableIME )
		dataSection.writeBool( "shouldAdjustClipping", self.shouldAdjustClipping )
		dataSection.writeVector4( "activeColour", self.activeColour )
		dataSection.writeVector4( "inactiveColour", self.inactiveColour )
		dataSection.writeBool( "allowAutoDefocus", self.__allowAutoDefocus )
		
		if len(self.autoSelectionFonts) > 0:
			dataSection.writeStrings( "autoFont", self.autoSelectionFonts )
		

	def addFocusObserver(self, focusObserver):
		self.focusObserver = focusObserver


	def handleKeyEvent( self, event ):
		if not self.enabled:
			return False
			
		if event.isMouseButton():
			return False			
				
		c = self.component.text
		character = event.character
		beginText = c.text
		
		
		handled = False
		touchCursor = False

		# Cursor logic...
		if event.isKeyDown():
			if event.key in [ Keys.KEY_RETURN, Keys.KEY_NUMPADENTER ]:
				handled = True
				if self.eventHandler is not None:
					textString = c.text
					self.eventHandler.onClick( c.text )
				elif self.onEnter is not None:
					self.onEnter( c.text )
			elif event.key == Keys.KEY_BACKSPACE:
				if self.cursorIndex > 0:
					c.text = c.text[:self.cursorIndex-1] + c.text[self.cursorIndex:]
					self.cursorIndex -= 1
					self._updateCursor()
				touchCursor = True
				handled = True
			elif event.key == Keys.KEY_DELETE:
				if self.cursorIndex < len(c.text):
					c.text = c.text[:self.cursorIndex] + c.text[self.cursorIndex+1:]
					self._updateCursor()
				touchCursor = True
				handled = True
			elif event.key in [ Keys.KEY_LEFTARROW, Keys.KEY_RIGHTARROW ]:
				direction = 1 if event.key == Keys.KEY_RIGHTARROW else -1
				if event.isCtrlDown():
					self.cursorIndex = skipWord( c.text, self.cursorIndex, direction )
				else:
					self.cursorIndex += direction
				self._updateCursor() # Will clamp position
				touchCursor = True
				handled = True
			elif event.key == Keys.KEY_HOME:
				self.cursorIndex = 0
				self._updateCursor()
				touchCursor = True
				handled = True
			elif event.key == Keys.KEY_END:
				self.cursorIndex = len( self._getText().text )
				self._updateCursor()
				touchCursor = True
				handled = True
			elif event.key == Keys.KEY_ESCAPE:
 				if self.onEscape is not None:
 					self.onEscape()
 					handled = True
			elif character is not None:
				self._insertString( character )
				touchCursor = True
				handled = True
			elif self.__externalKeyEventHandler is not None:
				handled = self.__externalKeyEventHandler( event )

		if touchCursor:
			self.component.cursor.script.touch()
			
		if c.text != beginText and self.onChangeValue is not None:
			self.onChangeValue( self.getText() )

		return handled


	def handleMouseButtonEvent( self, comp, event ):
		if self.enabled and event.isKeyDown() and event.key == Keys.KEY_LEFTMOUSE:
			setFocusedComponent( self.component )
			self.cursorIndex = self.screenToCharacterIndex( GUI.mcursor().position )
			self._updateCursor()
			self.component.cursor.script.touch()
			return True

		return False


	def handleIMEEvent( self, event ):
		self._updateCursor()
		
		cursorPosClip = self.component.cursor.script.getScreenClipPosition()
		clipMin, clipMax = Utils.clipRegion( self.component )
		Helpers.PyGUI.IME.handleIMEEvent( event, cursorPosClip, clipMin, clipMax, self.component.text.font )
		return False # Allow other components (eg LanguageIndicator) to get this event.


	def focus( self, state ):
		if self.component.parent is not None and self.component.parent.script is not None:
			pscript = self.component.parent.script
			if hasattr( pscript, 'editFieldChangeFocus' ):
				pscript.editFieldChangeFocus( self, state )
				
		if self.onChangeFocus is not None:
			self.onChangeFocus( state )
			
		if not self.enabled and state:
			setFocusedComponent( None )
			return
			
		BigWorld.ime.enabled = state and self.enableIME
		self.component.text.colour = self.activeColour if state else self.inactiveColour
		self._updateCursor()
		if not state:
			self.component.cursor.script.enable( False )


	def screenToCharacterIndex( self, clipPos ):
		"""
			Given a screen clip space position, this will calculate
			the closest index into the edit field text.
		"""

		oldWidthMode = self.component.widthMode
		self.component.widthMode = "PIXEL"
		locPos = self.component.screenToLocal( clipPos )
		self.component.widthMode = oldWidthMode

		clickedAtPixel = locPos.x / getHPixelScalar()

		w = 0
		idx = 0
		text = self.component.text.text
		for c in text:
			cw = self.component.text.stringWidth( c )
			if clickedAtPixel <= w + cw/2:
				return idx

			w += cw
			idx += 1


		return len( text )


	def allowAutoDefocus( self ):
		return self.__allowAutoDefocus


	def _insertString( self, s ):
		"""
			Inserts the given string at the cursor position. Moves the cursor position
			along to the end of the inserted string.
		"""
		c = self.component.text

		curLen = len(c.text)
		s = s[:max(self.maxLength - curLen, 0)]

		c.text = c.text[:self.cursorIndex] + s + c.text[self.cursorIndex:]
		self.cursorIndex += len(s)
		self._updateCursor()


	def _updateCursor( self ):
		"""
			Updates the cursor position, clamping it to a valid index range.
			The visual cursor representation is positioned.
		"""
		text = self._getText()
		textLen = len( text.text )
		self.cursorIndex = max( self.cursorIndex, 0 )
		self.cursorIndex = min( self.cursorIndex, textLen )

		cursorComp = self.component.cursor
		cursorComp.position.x = text.stringWidth( text.text[:self.cursorIndex] ) * getHPixelScalar()

		self._scrollIntoView()

		# Enable/disable cursor based on whether we are in a composition string or not.
		self.component.cursor.script.enable( self.enabled and not gotComposition() and isFocusedComponent( self.component ) )


	def _scrollIntoView( self ):
		"""
			Makes sure the cursor is visible by applying an appropriate scroll amount.
		"""
		hratio = getHPixelScalar()
		textArea = self.component

		# Get the width of the view in (real) pixels
		widthMode = textArea.widthMode
		textArea.widthMode = "PIXEL"
		textAreaWidth = textArea.width / hratio
		textArea.widthMode = widthMode

		# If we're already in view don't do anything
		cursorPosInPixels = textArea.cursor.position.x / hratio
		relCursorPos = cursorPosInPixels - self.scrollInPixels
		#print "_scrollIntoView", textAreaWidth, cursorPosInPixels, relCursorPos
		if relCursorPos > 0 and relCursorPos < textAreaWidth:
			return

		# Pull us in the correct direction so that the cursor is visible
		textComponent = textArea.text
		cursorIdx = self.cursorIndex

		if relCursorPos < 0:
			# Jump left by SKIP_AMOUNT (calculate the substring width)
			startingString = textComponent.text[ cursorIdx-SCROLL_SKIP_AMOUNT:cursorIdx+1 ]
			startingWidth = textComponent.stringWidth( startingString )
			self.scrollInPixels = cursorPosInPixels - startingWidth
		elif relCursorPos > textAreaWidth-5:
			# Jump right by SKIP_AMOUNT (calculate the substring width)
			trailingString = textComponent.text[ cursorIdx-1:cursorIdx+SCROLL_SKIP_AMOUNT ]
			trailingWidth = textComponent.stringWidth( trailingString )
			self.scrollInPixels = (cursorPosInPixels - textAreaWidth) + trailingWidth

		# Clamp the scroll position. When scrolling right, allow room for the cursor to be visible at
		# the end of the edit field. Note that scrollInPixels ranges from 0 to +N (even though scrolling
		# pushes the text left).
		self.scrollInPixels = max( self.scrollInPixels, 0 )
		self.scrollInPixels = min( self.scrollInPixels, abs(self._textWidthInPixels()-textAreaWidth)+CURSOR_WIDTH )

		self._applyScroll()


	def _applyScroll( self ):
		"""
			Takes the internal scrollInPixels and applies it to the textArea.
		"""
		scrollX = -self.scrollInPixels / (GUI.screenResolution()[0]*0.5)
		scrollX = scrollX * getHPixelScalar()
		self.component.scroll = ( scrollX, 0.0 )


	def _getCursor( self ):
		return self.component.cursor


	def _getText( self ):
		return self.component.text


	def _textWidthInPixels( self ):
		c = self._getText()
		return c.stringWidth( c.text )
		
		
	def _selectFontBestMatch( self ):
		selectedFont = Utils.autoSelectFont( self.autoSelectionFonts,
								self.idealVisibleCharacters,
								self._widthInPixels(),
								self.component.text	)
		
		self.component.text.font = selectedFont


	def _widthInPixels( self ):
		widthMode = self.component.widthMode
		self.component.widthMode = "PIXEL"
		w = self.component.width
		self.component.widthMode = widthMode
		return w / getHPixelScalar()
		
		
	def onRecreateDevice( self ):
		self._selectFontBestMatch()
		self._updateCursor()
		self.component.cursor.script.touch()

		# Force a refresh on our IME
		if self.component.focus and self.enableIME:
			cursorPosClip = self.component.cursor.script.getScreenClipPosition()
			clipMin, clipMax = Utils.clipRegion( self.component )
			Helpers.PyGUI.IME.refresh( cursorPosClip, clipMin, clipMax, self.component.text.font )


	@staticmethod
	def create( texture="",
				activeColour=DEFAULT_TEXT_COLOUR_ACTIVE, 
				inactiveColour=DEFAULT_TEXT_COLOUR_INACTIVE ):
		component = GUI.Window( texture )
		component.materialFX = "BLEND"
		component.width = 0.75
		component.height = 0.1
		component.heightMode = "CLIP"
		component.widthMode = "CLIP"
		component.minScroll = (-100,-100)
		component.maxScroll = (+100,+100)
		component.mouseButtonFocus = True
		
		text = GUI.Text( "" )
		text.horizontalPositionMode = "PIXEL"
		text.verticalPositionMode = "CLIP"
		text.horizontalAnchor = "LEFT"
		text.verticalAnchor = "CENTER"
		text.position.x = 0
		text.position.y = 0
		component.addChild( text, "text" )
		
		component.script = EditField( component )	
		component.script.activeColour = activeColour
		component.script.inactiveColour = inactiveColour
		
		component.script.onBound()
		return component
