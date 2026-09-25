# -*- coding: utf-8 -*-

import BigWorld
import Math
import types
import GUI
from PyGUIBase import PyGUIBase
from VisualStateComponent import VisualState, VisualStateComponent
import Utils
import Keys
import FantasyDemo

from FocusManager import setFocusedComponent, isFocusedComponent

class InternalBrowser( PyGUIBase ):
	factoryString = "PyGUI.InternalBrowser"
	visualStateString="PyGUI.ButtonVisualState"

	def __init__( self, component = None):
		PyGUIBase.__init__( self, component )
		self.component.script = self
		# Flag to mark whether we dynamically focus the browser or not.
		self.mozillaHandlesKeyboard = True
		self.focusObserver = None
		self.webPage = None
		
	def onLoad( self, dataSection ):
		if not hasattr( BigWorld, "AwesomiumProvider" ):
			return
		self.exactWidth = dataSection.readInt( "exactWidth", 0 )
		self.exactHeight = dataSection.readInt( "exactHeight", 0 )
		
		componentWidth, componentHeight  = Utils.pixelSize( self.component )
		try:
			#self.webPage = BigWorld.WebPageProvider(componentWidth, componentHeight, True, False, u"http://www.google.com", resQuality)
			self.webPage = BigWorld.AwesomiumProvider( componentWidth, componentHeight )
		except AttributeError, e:
			print "Failed to load BigWorld.AwesomiumProvider: %s" % ( e, )
			return

		self.webPage.loadURL( "http://www.google.com" )
		
		self.component.focus = False
		self.component.mouseButtonFocus = True
		self.component.moveFocus = True
		self.component.crossFocus = True
		self.component.texture = self.webPage
		self.component.materialFX = "SOLID"
	
	
	# get the mouse web coordinates
	def _getWebCoordinates( self, cursorPosition ):
		return
		
		c = self.component
		pos = c.screenToLocal( cursorPosition )
		if pos.x > c.width or pos.y > c.height or pos.x < 0 or pos.y < 0:
			return None
		# Note if the texture was scaled the coordinates should be scaled 
		# (downscaled) accordingly especially as the componentWidth does not take
		# into account the resolution override
		componentWidth, componentHeight  = Utils.pixelSize(self.component)
		pos.x = pos.x * self.webPage.width / componentWidth
		pos.y = pos.y * self.webPage.height / componentHeight
		return pos
	
	
	def handleMouseButtonEvent( self, comp, event ):
		PyGUIBase.handleMouseButtonEvent( self, comp, event )
		if event.isKeyDown():
			setFocusedComponent( self.component )
		self.webPage.injectKeyEvent( event )
		return True
	
	
	def handleMouseEvent( self, comp, event ):
		c = self.component
		
		loc = c.screenToLocal( event.cursorPosition )
		if loc.x > 0 and loc.y > 0:
			self.webPage.injectMouseMoveEvent( loc.x, loc.y )
		if event.dz != 0:
			self.webPage.injectMouseWheelEvent( event.dz )
		return True
	
	
	def handleMouseEnterEvent( self, comp ):
		return True
		self.webPage.allowCursorInteraction(True)
		return True
	
	
	def handleMouseLeaveEvent( self, comp ):
		return True
		self.webPage.allowCursorInteraction(False)
		return True
	
	
	def handleKeyEvent( self, event ):
		if not isFocusedComponent( self.component ) and not self.mozillaHandlesKeyboard:
			return False
		if event.isMouseButton():
			return False
		
		if event.key == Keys.KEY_LEFTARROW and event.isAltDown():
			self.webPage.goBack()
		elif event.key == Keys.KEY_RIGHTARROW and event.isAltDown():
			self.webPage.goForward()
		elif event.key == Keys.KEY_F5:
			self.webPage.reload( False )
		else:
			self.webPage.injectKeyEvent( event )
		return True
		

	def addFocusObserver( self, focusObserver ):
		self.focusObserver = focusObserver

		
	def focus( self, state ):
		if self.mozillaHandlesKeyboard:
			if state:
				self.webPage.focus()
			else:
				self.webPage.unfocus()
		if self.focusObserver:
			self.focusObserver.focus( state )
	
	
	def navigate( self, url ):
		if self.webPage is not None:
			self.webPage.loadURL( url )
	
		
	def navigateBack( self ):
		if self.webPage is not None:
			self.webPage.goBack()
	
		
	def navigateForward( self ):
		if self.webPage is not None:
			self.webPage.goForward()
	
		
	def addObserver( self, observer ):
		if self.webPage is not None:
			self.webPage.script = observer

