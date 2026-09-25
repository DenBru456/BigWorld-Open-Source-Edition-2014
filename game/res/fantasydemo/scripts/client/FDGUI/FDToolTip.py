
import BigWorld
import FantasyDemo
import GUI
import Keys
import copy
import Helpers.PyGUI as PyGUI
from Helpers.PyGUI.ToolTip import ToolTip
from Helpers.PyGUI.ToolTip import ToolTipInfo
from Helpers.PyGUI.ToolTip import ToolTipManager

import Helpers.BWKeyBindings as BWKeyBindings

allModifiers = (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL, Keys.KEY_LSHIFT, Keys.KEY_RSHIFT,
				Keys.KEY_LALT, Keys.KEY_RALT, Keys.KEY_CAPSLOCK, Keys.KEY_NUMLOCK,
				Keys.KEY_LWIN, Keys.KEY_RWIN, Keys.KEY_APPS,
				BWKeyBindings.KEY_ALIAS_CONTROL,
				BWKeyBindings.KEY_ALIAS_ALT,
				BWKeyBindings.KEY_ALIAS_SHIFT,
				BWKeyBindings.KEY_ALIAS_WINDOWS)
				
displayNames = {Keys.KEY_LCONTROL:'Left Ctrl', Keys.KEY_RCONTROL:'Right Ctrl',
				Keys.KEY_LSHIFT:'Left Shift', Keys.KEY_RSHIFT:'Right Shift',
				Keys.KEY_LALT:'Left Alt', Keys.KEY_RALT:'Right Alt',
				Keys.KEY_CAPSLOCK:'Caps Lock', Keys.KEY_NUMLOCK:'Num Lock',
				Keys.KEY_LWIN:'Left Windows', Keys.KEY_RWIN:'Right Windows', Keys.KEY_APPS:'App Key',
				Keys.KEY_ESCAPE:'Esc', Keys.KEY_MINUS:'Minus', Keys.KEY_EQUALS:'=',
				Keys.KEY_BACKSPACE:'Backspace', Keys.KEY_TAB:'Tab',
				Keys.KEY_LBRACKET:'[', Keys.KEY_RBRACKET:']', Keys.KEY_RETURN:'Enter',
				Keys.KEY_SEMICOLON:';', Keys.KEY_APOSTROPHE:"'", Keys.KEY_GRAVE:'`',
				Keys.KEY_BACKSLASH:'\\', Keys.KEY_COMMA:',', Keys.KEY_PERIOD:'.',
				Keys.KEY_SLASH:'/', Keys.KEY_SPACE:'Space', Keys.KEY_SCROLL:'ScrLck',
				Keys.KEY_NUMPADSTAR:'Num Pad *', Keys.KEY_NUMPADMINUS:'Num Pad -',
				Keys.KEY_ADD:'Num Pad +', Keys.KEY_NUMPADPERIOD:'Num Pad .',
				Keys.KEY_NUMPADSLASH:'Num Pad /', Keys.KEY_NUMPADENTER:'Num Pad Enter',
				Keys.KEY_NUMPADEQUALS:'Num Pad =', Keys.KEY_NUMPADCOMMA:'Num Pad ,',
				Keys.KEY_NUMPAD0:'Num Pad 0', Keys.KEY_NUMPAD1:'Num Pad 1',
				Keys.KEY_NUMPAD2:'Num Pad 2', Keys.KEY_NUMPAD3:'Num Pad 3',
				Keys.KEY_NUMPAD4:'Num Pad 4', Keys.KEY_NUMPAD5:'Num Pad 5',
				Keys.KEY_NUMPAD6:'Num Pad 6', Keys.KEY_NUMPAD7:'Num Pad 7',
				Keys.KEY_NUMPAD8:'Num Pad 8', Keys.KEY_NUMPAD9:'Num Pad 9',
				Keys.KEY_HOME:'Home', Keys.KEY_END:'End', Keys.KEY_INSERT:'Insert',
				Keys.KEY_DELETE:'Delete', Keys.KEY_PGUP:'Page Up', Keys.KEY_PGDN:'Page Down',
				Keys.KEY_LEFTARROW:'Left Arrow', Keys.KEY_RIGHTARROW:'Right Arrow',
				Keys.KEY_UPARROW:'Up Arrow', Keys.KEY_DOWNARROW:'Down Arrow',
				Keys.KEY_PAUSE:'Break',				
				BWKeyBindings.KEY_ALIAS_CONTROL: "Ctrl",
				BWKeyBindings.KEY_ALIAS_ALT: "Alt",
				BWKeyBindings.KEY_ALIAS_SHIFT: "Shift",
				BWKeyBindings.KEY_ALIAS_WINDOWS: "Windows",
				}

def _getKeyDisplayName( key ):
	if displayNames.has_key( key ):
		return displayNames[ key ] 
	else:
		return BigWorld.keyToString( key )

def _buildShortcut( bindings ):
	if len( bindings ) == 0:
		return ''

	# If there's more than one key binding take the first
	firstBindings = bindings[0]
	
	# Find all modifier keys and non-modifier keys
	modifiers = []
	nonmodifiers = []
	for key in firstBindings:
		if key in allModifiers:
			modifiers.append( key )
		else:
			nonmodifiers.append( key )

	shortcut = ''
	for key in modifiers:
		if shortcut:
			shortcut += '+'
		shortcut += _getKeyDisplayName( key )
	for key in nonmodifiers:
		if shortcut:
			shortcut += '+'
		shortcut += _getKeyDisplayName( key )

	return shortcut


class FDGUIOneLineToolTip( ToolTip ):

	SHORTCUT_GAP = 20

	def __init__( self, component ):
		ToolTip.__init__( self, component )


	def doLayout( self, parent ):
		widthMode = self.component.widthMode
		self.component.widthMode = 'PIXEL'

		text = self.component.text
		textLength, textHeight = text.stringDimensions( text.text )
		textHorizontalPositionMode = text.horizontalPositionMode
		text.horizontalPositionMode = 'PIXEL'
		textGap = text.position.x

		shortcut = self.component.shortcut
		shortcutLength = shortcut.stringWidth( shortcut.text )
		shortcutHorizontalPositionMode = shortcut.horizontalPositionMode
		shortcut.horizontalPositionMode = 'PIXEL'
		shortcutGap = self.component.width - shortcut.position.x

		guiResolution = GUI.screenResolution()
		scalex = guiResolution[0] / BigWorld.screenWidth()
		scaley = guiResolution[1] / BigWorld.screenHeight()
		
		if shortcutLength == 0:
			totalLength = textLength
		else:
			totalLength = textLength + FDGUIOneLineToolTip.SHORTCUT_GAP + shortcutLength

		t = self.component.frame.texture
		
		cWidth = (totalLength + textGap + shortcutGap) * scalex
		self.component.width = max( t.width * 2.0, cWidth )
		shortcut.position.x = self.component.width - shortcutGap
		
		heightMode = self.component.heightMode
		self.component.heightMode = "PIXEL"
		
		totalHeight = (textHeight + textHeight/2) * scaley
		self.component.height = max( t.width * 2.0, totalHeight )
		
		self.component.widthMode = widthMode
		self.component.heightMode = heightMode
		text.horizontalPositionMode = textHorizontalPositionMode
		shortcut.horizontalPositionMode = shortcutHorizontalPositionMode
		
		self.component.frame.filterType = "POINT"

		return ToolTip.doLayout( self, parent )


class FDToolTipManager( ToolTipManager ):

	def __init__( self, rootGUI, zorder ):
		ToolTipManager.__init__( self, rootGUI, zorder )

		self.addToolTipTemplate( "tooltip1line", "gui/tooltip_1line_window.gui" )

		self.actionToolTips = {}

	def addToolTipTemplate( self, templateName, guiFileName ):
		ret = ToolTipManager.addToolTipTemplate( self, templateName, guiFileName )
		FantasyDemo.rds.fdgui.setupFontsInternal( ret )
		return ret


	def readInActionToolTips( self, dataSection ):
		for key, section in dataSection.items():
			infoDictionary = { 'shortcut': "" }

			actionName = section.asString
			infoDictionary[ 'text' ] = section._text.asString

			templateName = "tooltip1line"

			toolTipInfo = ToolTipInfo( None, templateName, infoDictionary )
			self.actionToolTips[ actionName ] = toolTipInfo


	def addKeyboardShortcutsToActionToolTips( self, keyBindings ):
		for actionName, toolTipInfo in self.actionToolTips.iteritems():
			bindings = keyBindings.getBindingsForAction( actionName )
			toolTipInfo.infoDictionary[ 'shortcut' ] = _buildShortcut( bindings )


	def getToolTipForAction( self, actionName ):
			return copy.copy( self.actionToolTips.get( actionName, None ) )


	def setToolTipFromAction( self, guiScript, actionName ):
		toolTipInfo = self.getToolTipForAction(  actionName )
		guiScript.setToolTipInfo( toolTipInfo )


