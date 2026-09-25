import BigWorld, GUI
import Keys
import weakref
from bwdebug import *

from functools import partial

from Listener import Listenable


# TODO: evaluate this more in depth and clean up (e.g. activate stuff is a bit questionable).

MOUSE_BUTTON_EVENTS = {
	Keys.KEY_LEFTMOUSE: "onLButton",
	Keys.KEY_RIGHTMOUSE: "onRButton",
	Keys.KEY_MIDDLEMOUSE: "onMButton",
}

"""
This is the base class for all python gui classes.
There is a simple interface.

active(bool)		//must use this entry point to show the gui
setEventHandler(ev)	//this function gets called back on an event
self.component		//the underlying component.  Must be set by derived classes/
"""
class PyGUIBase(object, Listenable):

	def __init__( self, component = None ):
		Listenable.__init__( self )
		#derived classes must set this
		try:
			self.component = weakref.proxy( component )
		except TypeError:
			self.component = component
			
		if component is not None:
			component.script = self
			
		self.eventHandler = None
		self._parent = None
		self.isActive = False

	def active( self, state ):
		if state == self.isActive:
			return

		if not self.component:
			return

		self.isActive = state
		if state:
			if not self._parent:
				GUI.addRoot( self.component )
			else:
				self._parent.addChild( self.component )

			self.component.mouseButtonFocus = True
			self.component.moveFocus = True
			self.component.crossFocus = True
		else:
			if not self._parent:
				GUI.delRoot( self.component )
			else:
				self._parent.delChild( self.component )

			self.component.mouseButtonFocus = False
			self.component.moveFocus = False
			self.component.crossFocus = False

		self.listeners.activated( state )

	def _setparent( self, parent ):
		if self.isActive:
			if not self._parent:
				GUI.delRoot( self.component )
			else:
				self._parent.delChild( self.component )

		if parent:
			try:
				self._parent = weakref.proxy(parent)
			except TypeError:
				self._parent = parent
		else:
			self._parent = parent

		if self.isActive:
			if not self._parent:
				GUI.addRoot( self.component )
			else:
				self._parent.addChild( self.component )


	def _getparent( self ):
		return self._parent

	parent = property(_getparent, _setparent)

	def getWindow( self ):
		import Window
		if isinstance( self, Window.Window ):
			return self
		elif self.component.parent and self.component.parent.script:
			return self.component.parent.script.getWindow()
		else:
			return None

	def toggleActive( self ):
		self.active( not self.isActive )

	def setEventHandler( self, eh ):
		self.eventHandler = eh

	def doLayout( self, parent ):
		for name, child in self.component.children:
			if child.script is not None:
				child.script.doLayout( self )


	def setToolTipInfo( self, toolTipInfo ):
		self.toolTipInfo = toolTipInfo


	def removeToolTipInfo( self ):
		if hasattr( self, toolTipInfo ):
			del self.toolTipInfo


	#stubbing out fns that SimpleGUIComponent ( C++ ) calls into
	def focus( self, state ):
		pass
		
	def mouseButtonFocus( self, state ):
		pass
		
	def handleInputLangChangeEvent( self ):
		return False

	def handleKeyEvent( self, event ):
		return False

	def handleMouseEvent( self, comp, event ):
		return False

	def handleMouseButtonEvent( self, comp, event ):
		window = self.getWindow()
		if window:
			window.listeners.windowClicked()
			
		eventName = MOUSE_BUTTON_EVENTS.get( event.key, None )
		if eventName is not None:
			direction = "Up" if event.isKeyUp() else "Down"
			eventName += direction
			self._callEvent( eventName )
		return False


	def handleMouseClickEvent( self, component ):
		return False


	def handleMouseEnterEvent( self, comp ):
		if getattr( self, 'toolTipInfo', None ):
			import ToolTip
			ToolTip.ToolTipManager.instance.setupToolTip( self.component, self.toolTipInfo )
		self._callEvent( "onMouseEnter" )
		return False


	def handleMouseLeaveEvent( self, comp ):
		self._callEvent( "onMouseLeave" )
		return False


	def handleAxisEvent( self, event ):
		return False


	def handleDragStartEvent( self, comp ):
		return False


	def handleDragStopEvent( self, comp ):
		return False


	def handleDragEnterEvent( self, comp, dragged ):
		return False


	def handleDragLeaveEvent( self, comp, dragged ):
		return False


	def handleDropEvent( self, comp, dropped ):
		return False
		
		
	def handleIMEEvent( self, event ):
		return False
		
	

	def onLoad( self, dataSection ):
		if dataSection.has_key( "toolTipInfo" ):
			import ToolTip
			self.toolTipInfo = ToolTip.ToolTipInfo()
			self.toolTipInfo.onLoad( dataSection._toolTipInfo )

	def onSave( self, dataSection ):
		if hasattr( self, "toolTipInfo" ) and self.toolTipInfo is not None:
			toolTipInfoSection = dataSection.createSection( "toolTipInfo" )
			self.toolTipInfo.onSave( toolTipInfoSection )

	def onBound( self ):
		for name, child in self.component.children:
			if child.script is None:
				child.script = PyGUIBase( weakref.proxy(child) )
			assert isinstance( child.script, PyGUIBase )

		# Bind event handler decorators
		self.bindEvents( self.__class__ )


	def bindEvents( self, cls ):
		for name, function in cls.__dict__.iteritems():
			if hasattr( function, "_PyGUIEventHandler" ):
				for componentName, eventName, args, kargs in function._PyGUIEventHandler:
					assert( callable( function ) )

					component = self.component
					for name in componentName.split("."):
						component = getattr( component, name, None )
						if component is None:
							break

					if component is None:
						print( "Error: PyGUIBase.bindEvents: '%s' has no component named '%s'." % (str(self), componentName,) )
						continue

					function = getattr( self, function.__name__ )
					setattr( component.script, eventName, partial( function, *args, **kargs ) )

		for base in cls.__bases__:
			self.bindEvents( base )

	def _callEvent( self, eventName, *args, **kwargs ):
		if hasattr( self, eventName ):
			getattr( self, eventName )( *args, **kwargs )
