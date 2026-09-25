import BigWorld
import GUI

import Helpers.PyGUI as PyGUI
from Helpers.BWCoroutine import *

import FDGUI.Cursor

import RootPage
import RealmSelectionPage

from MainMenuConstants import *

import TextListPage
import TextInputPage


STATUS_GUI = "gui/main_menu_status.gui"


def fixAspectRatio( c, graphicAspectRatio ):
	screenWidth, screenHeight = BigWorld.screenSize()
	screenAspectRatio = screenWidth / screenHeight	
	c.width = (graphicAspectRatio/screenAspectRatio) * 2.0
	c.height = 2.0
	

# ------------------------------------------------------------------------------
# Section: class  MainMenu
# ------------------------------------------------------------------------------
class MainMenu( PyGUI.Window ):

	factoryString = "FDGUI.MainMenu"

	def __init__( self, component ):
		PyGUI.Window.__init__( self, component )
		self.backgroundAspectRatio = 0		
		self.stack = []		
		
		TextListPage.TextListPage.init( component )
		TextInputPage.TextInputPage.init( component )
		
	def fini( self ):
		TextListPage.TextListPage.fini()
		TextInputPage.TextInputPage.fini()
		
	def reset( self ):
		while len(self.stack) > 0:
			self.pop()
		
	def restartMenu( self ):
		self.reset()
		self.clearStatus()
		self.push( RootPage.RootPage( self ) )
		
	def connectedToServer( self ):
		self.reset()
		self.clearStatus()
		self.push( RealmSelectionPage.RealmSelectionPage( self ) )
		
		
	def showStatus( self, message, onEscape=lambda:None, showSpinner=False, showButton=False, detailMsg=None ):
		if len(self.stack) > 0:
			self.stack[-1].visible = False
			
		sw = self.component.statusWindow
		sw.script.setupStatus( message, showSpinner,  okButton=showButton, 
						onEscape=onEscape, detailMsg=detailMsg )
		sw.visible = True
		
	def showProgressStatus( self, message, onEscape=lambda:None ):
		self.showStatus( message, onEscape, True, False )
		
	def showPromptStatus( self, message, onEscape=lambda:None, detailMsg=None ):
		self.showStatus( message, onEscape, False, True, detailMsg=detailMsg )
		
	def clearStatus( self ):
		if self.statusVisible():
			self.component.statusWindow.visible = False
			if len(self.stack) > 0:
				self.stack[-1].visible = True
		
	def statusVisible( self ):
		return self.component.statusWindow.visible
		
	def push( self, page ):
		assert page is not None
		assert page not in self.stack
		
		outgoing = None
		
		if len(self.stack) > 0:
			#print "deactivating", self.stack[-1]
			outgoing = self.stack[-1]
			
			# Hide any existing page while we're changing (in case someone decides to 
			# do a latent change using coroutines).
			outgoing.visible = False
			
			outgoing.pageDeactivated( REASON_PUSHING, page )
		else:
			# NOTE: If there was an existing menu page, then the existing
			# one will do the actual stack push and page activation in the
			# base Page.pageDeactivated. This is done so that pages can delay
			# calling the base class implementation and thus delay the menu change.
			# But since we mightn't have had an existing menu we have to do it
			# immediately here:
			#print "pushing", page
			self.stack.append( page )
			self._activatePage( page, REASON_PUSHING, outgoing )
		
	def pop( self ):
		assert len(self.stack) > 0
		
		if len(self.stack) >= 2:
			incoming = self.stack[-2]
		else:
			incoming = None
		
		outgoing = self.stack[-1]
		#print "deactivating", outgoing
		
		# Hide any existing page while we're changing (in case someone decides to 
		# do a latent change using coroutines).
		outgoing.visible = False
		
		# NOTE: Page.pageDeactivated will do the popping and activation
		# of the new page. This is done so pages can delay calling the
		# base class implementation and thus delay the menu change.
		outgoing.pageDeactivated( REASON_POPPING, incoming )		
		
			
	def top( self ):
		if len(self.stack) > 0:
			return self.stack[-1]
		else:
			return None
		
	def _activatePage( self, page, reason, outgoing ):
		#print "activating", page
		page.pageActivated( reason, outgoing )		
		page.visible = not self.statusVisible()
		
	
	@BWMemberCoroutine
	def coShowCharacterScreen( self, active, fadeSpeed = 2.0 ):
		fader = self.component.background.fader
		if active:
			if fader.value == 0.0:
				return
			
			fader.speed = fadeSpeed
			fader.value = 0.0
			
			BigWorld.worldDrawEnabled( True )

			if fadeSpeed > 0:
				yield BWWaitForPeriod( fadeSpeed )
		else:
			if fader.value == 1.0:
				return
				
			fader.speed = fadeSpeed
			fader.value = 1.0
			
			if fadeSpeed > 0:
				yield BWWaitForPeriod( fadeSpeed )

			BigWorld.worldDrawEnabled( False )
			
	def handleMouseEvent( self, comp, event ):
		if len(self.stack) > 0 and self.stack[-1].visible:
			self.stack[-1].mouseScroll( -event.dz / 120 )
		return False
		
	def onSave( self, section ):
		section.writeFloat( "backgroundAspectRatio", self.backgroundAspectRatio )
		
	def onLoad( self, section ):
		self.backgroundAspectRatio = section.readFloat( "backgroundAspectRatio", 0 )
		
	def onBound( self ):
		self.component.statusWindow = GUI.load( STATUS_GUI )
		self.component.statusWindow.visible = False
		PyGUI.Window.onBound( self )
		
	def doLayout( self, parent=None ):
		if self.backgroundAspectRatio == 0:
			t1 = self.component.background.texture
			t2 = self.component.mainBackground.texture
			aspectRatio1 = t1.width / t1.height
			aspectRatio2 = t2.width / t2.height
		else:
			aspectRatio1 = self.backgroundAspectRatio
			aspectRatio2 = self.backgroundAspectRatio

		fixAspectRatio( self.component.background, aspectRatio1 )
		fixAspectRatio( self.component.mainBackground, aspectRatio2 )
		PyGUI.PyGUIBase.doLayout( self, parent )

	
	def active( self, state ):
		PyGUI.PyGUIBase.active( self, state )
		FDGUI.Cursor.showCursor( state )
