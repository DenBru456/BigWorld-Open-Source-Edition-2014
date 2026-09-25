import GUI
import Helpers.PyGUI as PyGUI

from Page import Page
from functools import partial

# ------------------------------------------------------------------------------
# Section: class TextInputWindow
# ------------------------------------------------------------------------------
class TextInputWindow( PyGUI.Window ):
	factoryString = "FDGUI.MainMenuTextInputWindow"
	
	def __init__( self, component ):
		PyGUI.Window.__init__( self, component )
		
	def doLayout( self, parent ):
		PyGUI.Window.doLayout( self, parent )
		
	
		ok = self.component.container.okButton
		cancel = self.component.container.cancelButton
		
		cancelX, cancelY = PyGUI.Utils.pixelPosition( cancel )
		cancelW, cancelH = PyGUI.Utils.pixelSize( cancel )
		okW, okH = PyGUI.Utils.pixelSize( ok )
		
		ok.horizontalPositionMode = "PIXEL"
		ok.position.x = cancelX - cancelW - 20
	

# ------------------------------------------------------------------------------
# Section: class TextInputPage
# ------------------------------------------------------------------------------
class TextInputPage( Page ):

	component = None

	@staticmethod
	def init( parentComponent=None ):
		TextInputPage.component = GUI.load( "gui/main_menu_text_input.gui" )
		TextInputPage.component.script.parent = parentComponent		
		
	@staticmethod
	def fini():
		TextInputPage.component = None

	def __init__( self, menu ):
		Page.__init__( self, menu )

	def pageActivated( self, reason, outgoing ):
		Page.pageActivated( self, reason, outgoing )
		comp = TextInputPage.component
		
		editField = comp.container.editArea.edit
		editField.script.onEnter = self.onEnter
		editField.script.onEscape = self.onCancel
		editField.script.onChangeValue = self.onTextChanged
		PyGUI.setFocusedComponent( editField )
		
		okButton = comp.container.okButton
		okButton.script.onClick = self._onOKClicked
		
		cancelButton = comp.container.cancelButton
		cancelButton.script.onClick = self.onCancel
		
		comp.container.caption.text = self.caption
		
		comp.script.active( True )
		comp.script.doLayout( comp.parent )
		
	def pageDeactivated( self, reason, incoming ):
		TextInputPage.component.script.active( False )
		Page.pageDeactivated( self, reason, incoming )
		
	def _onOKClicked( self ):
		self.onEnter( self.getText() )
		
	def onEnter( self, value ):
		pass
		
	def onTextChanged( self, value ):
		pass
		
	def onCancel( self ):
		if len(self.menu.stack) > 1:
			self.menu.pop()
			
	def enableOK( self, enable ):
		self.component.container.okButton.script.setDisabledState( not enable )
		
	def getText( self ):
		return self.component.container.editArea.edit.script.getText()
		
	def setText( self, text ):
		return self.component.container.editArea.edit.script.setText( text )
	
	@property
	def visible( self ):
		return self.isActive() and TextInputPage.component.visible
		
	@visible.setter
	def visible( self, visible ):
		if self.isActive():
			TextInputPage.component.visible = visible

	@property
	def caption( self ):
		return "Implement Caption Property"
	
	
		