import BigWorld, GUI, Keys

from PyGUIBase import PyGUIBase
from DraggableComponent import DraggableComponent

class Window( PyGUIBase ):

	factoryString="PyGUI.Window"

	def __init__( self, component ):
		PyGUIBase.__init__( self, component )


	def onSave( self, dataSection ):
		PyGUIBase.onSave( self, dataSection )


	def onLoad( self, dataSection ):
		PyGUIBase.onLoad( self, dataSection )


	@classmethod
	def create( cls, texture, bind=True ):
		return Window._createInternal( cls, texture, bind )
		
	@staticmethod
	def _createInternal( cls, texture, bind ):
		c = GUI.Window( texture )
		s = cls( c )
		if bind:
			s.onBound()
		return c

class EscapableWindow( Window ):

	factoryString="PyGUI.EscapableWindow"

	def __init__( self, component = None ):
		Window.__init__( self, component )
		self.onEscape  = None

	def handleKeyEvent( self, event ):
		if ( event.isKeyDown() ):
			if ( event.key == Keys.KEY_ESCAPE ) :
				if self.onEscape is not None:
					self.onEscape()
					return True
		return False
		
	@classmethod
	def create( cls, texture, bind=True ):
		c = Window._createInternal( cls, texture, bind )
		c.focus = True
		return c


class DraggableWindow( Window, DraggableComponent ):

	factoryString="PyGUI.DraggableWindow"

	def __init__( self, component, horzDrag = True, vertDrag = True, restrictToParent = True ):
		Window.__init__( self, component )
		DraggableComponent.__init__( self, horzDrag, vertDrag, restrictToParent )
		self.onBeginDrag = self._onBeginDrag


	def handleMouseButtonEvent( self, comp, event ):
		return DraggableComponent.handleMouseButtonEvent( self, comp, event )


	def onSave( self, dataSection ):
		DraggableComponent.onSave( self, dataSection )
		Window.onSave( self, dataSection )


	def onLoad( self, dataSection ):
		DraggableComponent.onLoad( self, dataSection )
		Window.onLoad( self, dataSection )


	def _onBeginDrag( self ):
		self.listeners.onBeginDrag()

	
	@classmethod
	def create( cls, texture, bind=True ):
		c = Window._createInternal( cls, texture, bind )
		c.mouseButtonFocus = True
		c.moveFocus = True
		c.crossFocus = True
		return c

