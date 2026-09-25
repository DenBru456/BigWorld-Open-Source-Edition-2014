import BigWorld
import GUI
import Keys
import Helpers.PyGUI as PyGUI

from Page import Page
from MainMenuConstants import *
from GameData.MainMenuGUIData import *

def _readItemText(i):
	return str(i()) if callable(i) else str(i)

# ------------------------------------------------------------------------------
# Section: class BackButton
# ------------------------------------------------------------------------------
class BackButton( PyGUI.Button ):

	def doLayout( self, parent ):
		PyGUI.Button.doLayout( self, parent )

		leftW, leftH = PyGUI.Utils.pixelSize( self.component.left )
		rightW, rightH = PyGUI.Utils.pixelSize( self.component.right )
		
		label = self.component.label
		labelW, labelH = label.stringDimensions( label.text )
		labelW = (labelW+5)  * PyGUI.Utils.getHPixelScalar()
		labelH = (labelH+10) * PyGUI.Utils.getHPixelScalar()
		
		self.component.widthMode = "PIXEL"
		self.component.width = leftW + labelW + rightW
		self.component.mid.width = labelW
		
		self.component.heightMode = "PIXEL"
		self.component.height = labelH
		

# ------------------------------------------------------------------------------
# Section: class TextListWindow
# ------------------------------------------------------------------------------
class TextListWindow( PyGUI.Window ):
	factoryString = "FDGUI.MainMenuTextListWindow"
	
	INITIAL_SCROLL_RATE = 0.25
	SCROLL_RATE = 0.1
	
	def __init__( self, component = None ):
		PyGUI.Window.__init__( self, component )
		self.timerHandle = None
		self.scrollCount = 0
		self.scrollDist = 0
		self.mouseOverScroll = False
		self.mouseDownScroll = False
		self.bigFont = "default_medium.font"
		self.smallFont = "default_small.font"
	
	@PyGUI.PyGUIEvent( "container.menu.scrollUp", "onLButtonDown", -1 )
	@PyGUI.PyGUIEvent( "container.menu.scrollDown", "onLButtonDown", 1 )
	def scrollButtonPressed( self, dist ):
		self.scrollDist = dist
		self.mouseOverScroll = True
		self.mouseDownScroll = True
		self._setupTimer()
		self._scrollNow()
		
		
	@PyGUI.PyGUIEvent( "container.menu.scrollUp", "onLButtonUp" )
	@PyGUI.PyGUIEvent( "container.menu.scrollDown", "onLButtonUp" )
	def scrollButtonReleased( self ):
		self.mouseOverScroll = False
		self.mouseDownScroll = False
		self._cancelTimer()
		
	@PyGUI.PyGUIEvent( "container.menu.scrollUp", "onMouseEnter", True )
	@PyGUI.PyGUIEvent( "container.menu.scrollDown", "onMouseEnter", True )
	@PyGUI.PyGUIEvent( "container.menu.scrollUp", "onMouseLeave", False )
	@PyGUI.PyGUIEvent( "container.menu.scrollDown", "onMouseLeave", False )
	def scrollButtonMouseCross( self, entered ):
		self.mouseOverScroll = entered
		if entered:
			self.mouseDownScroll = BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )			
			if not self.mouseDownScroll:
				self.scrollCount = 0
			self._setupTimer()
		
	def _scrollNow( self ):
		scrollingList = self.component.container.menu.script
		scrollingList.scrollList( self.scrollDist )
		self.scrollCount += 1
		
	def _setupTimer( self ):
		self._cancelTimer()
		delay = self.INITIAL_SCROLL_RATE if self.scrollCount == 0 else self.SCROLL_RATE
		self.timerHandle = BigWorld.callback( delay, self._scrollCB )

	def _cancelTimer( self ):
		if self.timerHandle is not None:
			BigWorld.cancelCallback( self.timerHandle )
		self.timerHandle = None
		
	def _scrollCB( self ):
		self.timerHandle = None
		if not self.mouseDownScroll or not self.mouseOverScroll:
			return

		self._scrollNow()
		self.timerHandle = BigWorld.callback( self.SCROLL_RATE, self._scrollCB )
		
	def onLoad( self, section ):
		PyGUI.Window.onLoad( self, section )
		self.smallFont = section.readString( "smallFont", self.smallFont )
		self.bigFont = section.readString( "bigFont", self.bigFont )
		
	def doLayout( self, parent ):
		w, h = PyGUI.Utils.pixelSize( self.component )
		
		container = self.component.container
		menu = self.component.container.menu
		header = self.component.container.header
		
		self.component.container.width = w-8
		self.component.container.height = h-28
		self.component.container.position.x = 2
		self.component.container.position.y = 2
		
		screenWidth, screenHeight = BigWorld.screenSize()
		if screenWidth < 700 or screenHeight < 700:
			header.caption.font = self.smallFont
		else:
			header.caption.font = self.bigFont
		
		sw, sh = header.caption.stringDimensions( header.caption.text )
		
		header.height = (sh+15) * PyGUI.Utils.getVPixelScalar()
		menu.height = container.height - header.height - 20		
		header.caption.verticalAnchor = "CENTER"
		PyGUI.Window.doLayout( self, parent )
		
	def adjustFont( self, width, height ):
		self.component.name.reset()
		self.component.status.reset()

# ------------------------------------------------------------------------------
# Section: class SmoothMover
# ------------------------------------------------------------------------------
class SmoothMover( PyGUI.SmoothMover ):

	factoryString = "FDGUI.MainMenuSmoothMover"

	def __init__( self, component ):
		PyGUI.SmoothMover.__init__( self, component )

	def doLayout( self, parent ):
		self.component.width = parent.component.width
		PyGUI.SmoothMover.doLayout( self, parent )
		
# -------------------------------------------------------------------------
# Section: class MenuItem
# This class implements an individual item in the a scrolling list page.
# Each item is initialised with a text label and a functor
# -------------------------------------------------------------------------
class MenuItem( PyGUI.PyGUIBase ):

	factoryString = "FDGUI.MainMenuItem"
	
	def __init__( self, component ):
		PyGUI.PyGUIBase.__init__( self, component )
		self.event = None
		component.focus = True
		component.mouseButtonFocus = True
		component.crossFocus = True
		component.moveFocus = True
		
		self.selected = False
		self.mouseOver = False
		
	#when the list item is created, what to do.
	def setup( self, setupParams, listIdx ):
		self.component.name.text = _readItemText( setupParams[0] )
		self.event = setupParams[1]		
		if len(setupParams) > 2:
			self.component.status.text = _readItemText( setupParams[2] )
		else:
			self.component.status.text = ""			
		self.listIdx = listIdx

	def canSelect( self ):
		return not (self.event == None)

	def adjustFont( self, width, height ):
		if width < 700 or height < 700:
			self.component.name.font = self.smallFont
			self.component.status.font = self.smallFont
		else:
			self.component.name.font = self.bigFont
			self.component.status.font = self.bigFont
			
		self.component.name.reset()
		self.component.status.reset()
		
		heightMode = self.component.heightMode
		self.component.heightMode = "LEGACY"	
		self.component.height = self.component.name.height * 1.1
		self.component.heightMode = heightMode
		return self.component.height

	#arggh generic item colouring
	def setupHighlights( self ):
		if not self.event:
			self.component.colour = ITEM_COLOUR_BG_UNSELECTABLE
			self.component.name.colour = ITEM_COLOUR_TEXT_UNSELECTABLE
		elif self.selected:
			self.component.colour = ITEM_COLOUR_BG_SELECTED
			self.component.name.colour = ITEM_COLOUR_TEXT_SELECTED
		else:
			self.component.colour = ITEM_COLOUR_BG_UNSELECTED
			self.component.name.colour = ITEM_COLOUR_TEXT_UNSELECTED


	def select( self, state ):
		self.selected = state
		self.setupHighlights()


	def doLayout( self, parent ):
		#self.component.width = parent.component.width
		#self.component.name.width = parent.component.width
		#self.component.name.position.x = -parent.component.width / 2 + 0.05

		PyGUI.PyGUIBase.doLayout( self, parent )

	#i.e. the button was pressed. make event happen
	def onSelect( self, mainGui ):
		if self.event:
			mainGui.active(0)
			self.event()
			
	def selectSelf( self, bringIntoView = True ):
		scrollingList = self.component.parent.parent.script
		if scrollingList.canSelect( self.listIdx ):
			scrollingList.selectItem( self.listIdx, bringIntoView )

	def onLoad( self, section ):
		self.smallFont = section.readString( "smallFont", "default_small.font" )
		self.bigFont = section.readString( "bigFont", "default_medium.font" )


	def handleMouseClickEvent( self, comp ):
		scrollingList = self.component.parent.parent.script
		if scrollingList.canSelect( self.listIdx ):
			scrollingList.selectItem( self.listIdx )
			scrollingList.executeSelected()
			
		return True

	def handleMouseEnterEvent( self, comp ):
		self.mouseOver = True
		return True


	def handleMouseLeaveEvent( self, comp ):
		self.mouseOver = False
		return True


	def handleMouseEvent( self, comp, event ):
		PyGUI.PyGUIBase.handleMouseEvent( self, comp, event )
		if event.dx != 0 or event.dy != 0: # Don't select if its only mouse wheel
			self.selectSelf( False )
		return False

	def handleMouseButtonEvent( self, comp, event ):
		PyGUI.PyGUIBase.handleMouseButtonEvent( self, comp, event )
		if event.key == Keys.KEY_LEFTMOUSE and event.isKeyDown():
			self.selectSelf()
			return True	
	
		return False


		
# ------------------------------------------------------------------------------
# Section: class TextListPage
# ------------------------------------------------------------------------------
class TextListPage( Page ):

	component = None
	enableBackButton = True

	@staticmethod
	def init( parentComponent=None ):
		comp = GUI.load( "gui/main_menu_text_page.gui" )
		comp.script.parent = parentComponent
		comp.container.menu.script.scrollUp = comp.container.menu.scrollUp
		comp.container.menu.script.scrollDown = comp.container.menu.scrollDown
		TextListPage.component = comp
		TextListPage.origMenuHeight = comp.container.menu.height
		
	@staticmethod
	def fini():
		TextListPage.component = None

	
	def __init__( self, menu, initialSel=0 ):
		Page.__init__( self, menu )
		self.items = []
		self._initialSel = initialSel
		
		
	def populate( self ):
		pass
		
		
	def repopulate( self ):
		assert self.isActive() # Only allow repopulate if we're the active page
		
		currentSelection = self.selectedItem
		self.items = []
		self.populate()
		self.menuComponent.script.setupItems( self.onBack, self.items )
		self.selectItem( currentSelection )
		
		
	def onBack( self ):
		if self.enableBackButton and len(self.menu.stack) > 1:
			self.menu.pop()
		return True
		
	def onSelectionChanged( self, index ):
		pass
		
	def mouseScroll( self, amt ):
		self.menuComponent.script.scrollList( amt )
		
	def selectItem( self, index ):
		self.menuComponent.script.selectItem( index, animate=False, forceReselect=True )
	
	
	def pageActivated( self, reason, outgoing ):
		Page.pageActivated( self, reason, outgoing )
		
		self.items = []
		self.populate()
	
		component = TextListPage.component
		component.script.active( True )
		self.menuComponent.script.selectItemCallback = self.onSelectionChanged
		self.menuComponent.script.setupItems( self.onBack, self.items )
		self.itemsComponent.script.scrollTo(0, 0)
		self.itemsComponent.script.scrollTransform.setIdentity()
		self.itemsComponent.transform.reset()
		
		backButton = component.container.header.backButton
		if len(self.menu.stack) > 1 and self.enableBackButton:
			backButton.visible = True
			caption = self.menu.stack[-2].caption
			if caption is not None:
				backButton.script.setLabel( caption )
		else:
			backButton.visible = False
		backButton.script.onClick = self.onBack
		
		if hasattr( self, "caption" ) and self.caption is not None:
			self.headerComponent.caption.text = self.caption
			
		component.script.doLayout( component.parent )
		
		if reason == REASON_PUSHING:
			self.selectItem( self._initialSel )
		else:
			self.selectItem( self._lastSelectedItem )
		
		
	def pageDeactivated( self, reason, incoming ):		
		self._lastSelectedItem = self.selectedItem
		component = TextListPage.component
		component.script.active( False )
		Page.pageDeactivated( self, reason, incoming )
		
		
	def addItem( self, title, callback, statusText=None ):
		if statusText is None:
			self.items.append( (title, callback) )
		else:
			self.items.append( (title, callback, statusText) )

	
	@property
	def visible( self ):
		return self.isActive() and TextListPage.component.visible
		
	@visible.setter
	def visible( self, visible ):
		if self.isActive():
			TextListPage.component.visible = visible
	
	@property
	def selectedItem( self ):
		return self.menuComponent.script.selection

	@property
	def headerComponent( self ):
		return TextListPage.component.container.header
	
	@property
	def menuComponent( self ):
		return TextListPage.component.container.menu
	
	@property
	def itemsComponent( self ):
		return TextListPage.component.container.menu.items
	
