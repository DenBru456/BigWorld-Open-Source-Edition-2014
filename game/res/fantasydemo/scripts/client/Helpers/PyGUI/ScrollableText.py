import BigWorld
import GUI
import re

from PyGUIBase import PyGUIBase
from Helpers.PyGUI.Utils import getHPixelScalar, WHITESPACE
from Helpers.PyGUI.Listeners import registerDeviceListener

import Utils

import StringIO
import string

_colourTagLen = len( r'\cAABBCCDD;' )
_colourTagRE = re.compile( r'(?<!\\)\\[cC][0-9a-fA-F]{8};' )

# Takes a Vector4 style colour and packs it into a colour tag
# suitable for TextGUIComponent richFormatting mode.
def _packColourTag( colour ):
	return "\\c%.2x%.2x%.2x%.2x;" % ( int(colour[0]), int(colour[1]), int(colour[2]), int(colour[3]) )

def _findStartOfWord( s, offset ):
	# Word backwards until we find the first whitespace.
	# Returns -1 if there was none found.
	i = offset
	while i >= 0:
		# Skip past colour tags.
		if i >= _colourTagLen and _colourTagRE.match( s, i-_colourTagLen ) != None:
			i -= _colourTagLen+1
			continue

		if s[i] in WHITESPACE:
			return i+1
		else:
			i -= 1
	return -1

# TODO: implement a _wrapLine that works backwards rather than forwards, probably a bit more efficient.	
# Improvement ideas:
# - Skip ahead by word, not just characters
# - Accumulate stringWidth as you go, not recalculate it every iteration.
# - Make a guestimate as to how many might fit on the line based on a widest char.
# - Begin with ret = [s], then iteratively split off the tail string in ret.
def _wrapLine( s, desiredWidth, textComponent ):
	"""
		Wraps the given string into a list of lines. If there is no
		wrapping performed, a list of length 1 is returned.
	"""
	if s == "":
		return [""]
	
	ret = []
	i = 0

	# Keep iterating through each character until it is too wide.
	while i < len(s):

		# Skip past formatting tags.
		while _colourTagRE.match( s, i ) != None and i < len(s):
			i += _colourTagLen

		if i >= len(s):
			break

		subStr = s[:i]
		subStrWidth = textComponent.stringWidth( subStr )

		# If it is too wide, move back until the beginning of the word (previous whitespace).
		if subStrWidth > desiredWidth:

			wordStart = _findStartOfWord( s, i )
			if wordStart >= 0:
				subStr = s[:wordStart]
			else:
				# There was no previous whitespace to break at. Just move back character
				# by character until we find somewhere that fits
				while subStrWidth > desiredWidth and i > 0:
					i -= 1
					subStr = s[:i]
					subStrWidth = textComponent.stringWidth( subStr )

				# Make sure we get at least one character on this line...
				if i == 0: i = 1
				subStr = s[:i]

			# Put this in the return buffer.
			ret.append( subStr )
			s = s[len(subStr):]
			i = 0
		else:
			i += 1

	# Put the everything is onto its own line
	if len(s):
		ret.append( s )
	return ret
	
	

class ScrollableText( PyGUIBase ):

	factoryString = "PyGUI.ScrollableText"
	
	@staticmethod
	def create():
		component = GUI.Window( "system/maps/col_white.bmp" )
		component.colour = (128, 128, 128, 255)
		component.materialFX = "BLEND"
		component.widthMode = "CLIP"
		component.heightMode = "CLIP"

		component.addChild( GUI.Text(""), "text" )
		component.text.horizontalAnchor = "LEFT"
		component.text.horizontalPositionMode = "CLIP"
		component.text.verticalAnchor = "BOTTOM"
		component.text.verticalPositionMode = "CLIP"
		component.text.position = (-1.0, -1.0, 0.5)
		component.text.multiline = True
		component.text.colourFormatting = True
		component.text.colour = (255,255,255,255)
		component.script = ScrollableText( component )
		component.script.onBound()
		
		return component

	def __init__( self, component=None ):
		PyGUIBase.__init__( self, component )

		self.maxLines = 255
		self.wordWrap = True
		self.minVisibleLines = 4 # Always keep this number visible when scrolling.
		self.autoSelectionFonts = [ "default_medium.font" ]
		self.idealCharactersPerLine = 80

		self.lines = []
		self.wrappedLines = []
		self.scrollIndex = 0
		self._displayedLineCount = 0
		
		registerDeviceListener( self )

	def clear( self ):
		self.lines = []
		self.scrollIndex = 0;
		self._recalcWrapping()
		
		
	def getMaxLines( self ):
		return self.maxLines


	def setMaxLines( self, maxLines ):
		self.maxLines = maxLines
		self.scrollIndex = min( self.scrollIndex, self.maxLines )
		self.scrollIndex = min( self.scrollIndex, self._displayedLineCount-self.minVisibleLines )
		self._updateScroll()
	
	
	def scrollUp( self, amt=4 ):
		self.scrollIndex = min( self.scrollIndex+amt, self.maxLines )
		self.scrollIndex = min( self.scrollIndex, self._displayedLineCount-self.minVisibleLines )
		self._updateScroll()
		
		
	def scrollDown( self, amt=4 ):
		self.scrollIndex = max( self.scrollIndex-amt, 0 )
		self._updateScroll()
		
		
	def setScrollIndex( self, idx ):
		self.scrollIndex = min( idx, self.maxLines )
		self.scrollIndex = max( self.scrollIndex, 0 )
		self.scrollIndex = min( self.scrollIndex, self._displayedLineCount-self.minVisibleLines )
		self._updateScroll()
		

	def onBound( self ):
		if len(self.autoSelectionFonts) == 0:
			self.autoSelectionFonts = [ self.component.text.font ]
		self._recalcFontMetrics()
		self._selectFontBestMatch()


	def onSave( self, dataSection ):
		PyGUIBase.onSave( self, dataSection )
		dataSection.writeInt( 'maxLines', self.maxLines )
		dataSection.writeBool( 'wordWrap', self.wordWrap )
		
		dataSection.writeInt( 'idealCharactersPerLine', self.idealCharactersPerLine )
		if len(self.autoSelectionFonts) > 0:
			dataSection.writeStrings( "autoFont", self.autoSelectionFonts )


	def onLoad( self, dataSection ):
		PyGUIBase.onLoad( self, dataSection )
		self.maxLines = dataSection.readInt( 'maxLines', self.maxLines )
		self.wordWrap = dataSection.readBool( 'wordWrap', self.wordWrap )
		
		self.idealCharactersPerLine = dataSection.readInt( 'idealCharactersPerLine', self.idealCharactersPerLine )
		fonts = dataSection.readStrings( 'autoFont' )
		if len(fonts) > 0:
			self.autoSelectionFonts = fonts


	def appendLine( self, str, colour=(255,255,255,255) ):
		io = StringIO.StringIO( _packColourTag(colour) + unicode(str) )
		newLines = [ unicode(x).rstrip() for x in io.readlines() ]

		if len(newLines) + len(self.lines) >= self.maxLines:
			diff = self.maxLines - len(self.lines)
			self.lines = self.lines[diff:]

		self.lines.extend( newLines )
		
		widthInPixels = self._widthInPixels()
		for line in newLines:
			wrapped = _wrapLine( line, widthInPixels, self.component.text )
			self.wrappedLines.extend( wrapped )
		
		self._refillBuffer()
		
		if self.scrollIndex > 0:
			self.setScrollIndex( self.scrollIndex + len(newLines) )


	def onRecreateDevice( self ):
		self._selectFontBestMatch()

		
	def _recalcWrapping( self ):
		widthInPixels = self._widthInPixels()

		self.wrappedLines = []
		for x in self.lines:
			self.wrappedLines.extend( _wrapLine( x, widthInPixels, self.component.text ) )

		self._refillBuffer()

		
	def _refillBuffer( self ):
		buffer = '\n'.join( self.wrappedLines )
		self.component.text.text = buffer
		self._displayedLineCount = len(self.wrappedLines)
		self._recalcMaxScroll()
		self._updateScroll()
		

	def _recalcMaxScroll( self ):
		totalPixelHeight = self._lineHeight * self._displayedLineCount
		self.component.minScroll.y = -totalPixelHeight / (BigWorld.screenHeight() * 0.5)


	def _recalcFontMetrics( self ):
		_, self._lineHeight = self.component.text.stringDimensions( "W" )


	def _widthInPixels( self ):
		widthMode = self.component.widthMode
		self.component.widthMode = "PIXEL"
		w = self.component.width
		self.component.widthMode = widthMode
		return w / getHPixelScalar()
		
		
	def _updateScroll( self ):
		self.component.scroll.y = -self.scrollIndex * (self._lineHeight/(BigWorld.screenHeight() * 0.5))
		
		
	def _selectFontBestMatch( self ):
		selectedFont = Utils.autoSelectFont( self.autoSelectionFonts,
								self.idealCharactersPerLine,
								self._widthInPixels(),
								self.component.text	)
		
		#print "_selectFontBestMatch", self, desiredWidth, self.autoSelectionFonts, self.idealCharactersPerLine, selectedFont
		
		self.component.text.font = selectedFont
		self._recalcFontMetrics()
		self._recalcMaxScroll()
		self._recalcWrapping()
		
		
	@staticmethod
	def test():
		for x in GUI.roots(): GUI.delRoot(x)

		global testUI
		testUI = ScrollableText().component
		GUI.addRoot(testUI)

		testUI.script.appendLine( "AAAA\nBBBB\CCCC\nDDDD" )
		testUI.script.appendLine( "XYZ" )
		testUI.script.appendLine( "ABCD" )
		testUI.script.appendLine( "EFG" )
		testUI.script.appendLine( "HIJKL" )
		testUI.script.appendLine( "VRRRRFRF" )
		testUI.script.appendLine( "\cFF0000FF;test one two three four" )
		testUI.script.appendLine( "\c00FF00FF;the fat cat sat on the MAT" )
		testUI.script.appendLine( "\c0000FFFF;The quick brown fox jumped over the lazy dog" )

