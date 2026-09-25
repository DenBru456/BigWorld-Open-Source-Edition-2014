import BigWorld
import ResMgr
import GUI
import Helpers.PyGUI as PyGUI
import Cursor

from Helpers.PyGUI import PyGUIEvent
from Helpers.PyGUI.Utils import applyMapping

import Helpers.PyGUI.TextStyles as TextStyles

from bwdebug import ERROR_MSG

HELP_TEXT = ResMgr.openSection( "scripts/data/help.xml" )

HEADING_TEXT_STYLE = "Heading"
DESC_TEXT_STYLE = "Label"

TEXT_VERTICAL_GAP = 25
HEADING_GAP = 30
MARGIN_TOP = 25


class HelpWindow( PyGUI.DraggableWindow ):

	factoryString = "FDGUI.HelpWindow"
	
	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )
		self.currentPageIndex = 0
		self.currentPage = None
		self.pageGuis = []


	def updateHelp( self ):	
		prevEnabled = self.currentPageIndex == 0
		nextEnabled = self.currentPageIndex == len(self.pageGuis)-1
		
		self.component.prevButton.script.setDisabledState( prevEnabled )
		self.component.nextButton.script.setDisabledState( nextEnabled )
		
		# Hide current page
		if self.currentPage is not None:
			self.currentPage.visible = False
			self.currentPage = None

		# Get the new GUI
		newGui = self.pageGuis[self.currentPageIndex]
		if newGui is None:
			ERROR_MSG( "updateHelp: failed to load help page %d ('%s')" % \
						(self.currentPageIndex+1, resource) )
			return

		# Add the component as a child of the page region, which is a WindowGUIComponent.
		newGui.visible = True
		self.currentPage = newGui
		
		# Update label.
		self.component.pageLabel.text = "Page %d/%d" % (self.currentPageIndex+1, len(self.pageGuis))
			
	
	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )
				
		
	@PyGUIEvent( "nextButton", "onClick" )
	def nextButtonClick( self ):
		self.currentPageIndex = min( self.currentPageIndex+1, len(self.pageGuis)-1 )
		self.updateHelp()
		
		
	
	@PyGUIEvent( "prevButton", "onClick" )
	def prevButtonClick( self ):
		self.currentPageIndex = max( self.currentPageIndex-1, 0 )			
		self.updateHelp()
		

		
	def active( self, show ):
		if self.isActive == show:
			return
			
		PyGUI.DraggableWindow.active( self, show )
		Cursor.showCursor( show )


	def _initPages( self ):
		
		for category in [ x for x in HELP_TEXT.values() if x.name == "category" ]:

			page, currentY = self._addPage( category.asString)

			# Add each item
			for item in [ x for x in category.values() if x.name == "item" ]:
				desc = item.asString
				action = item._action.asString if item.has_key("action") else ""

				descText = GUI.Text(desc)
				descText.verticalPositionMode = "PIXEL"
				descText.horizontalAnchor = "LEFT"
				descText.horizontalPositionMode = "CLIP"
				descText.position.x = -0.9
				TextStyles.setStyle( descText, DESC_TEXT_STYLE )
				descText.position.y = currentY
				page.addChild( descText )

				if action != "":
					descText = GUI.Text(action)
					descText.verticalPositionMode = "PIXEL"
					descText.horizontalAnchor = "RIGHT"
					descText.horizontalPositionMode = "CLIP"
					descText.position.x = 0.9
					TextStyles.setStyle( descText, DESC_TEXT_STYLE )
					descText.position.y = currentY
					page.addChild( descText )

				currentY += TEXT_VERTICAL_GAP


		
	def _addPage( self, headingText ):
		page = GUI.Simple( "" )
		page.horizontalPositionMode = page.verticalPositionMode = "CLIP"
		page.widthMode = page.heightMode = "CLIP"
		page.width = page.height = 2.0
		page.visible = False
		self.component.pageRegion.addChild( page )
		self.pageGuis.append( page )
		
		heading = GUI.Text(headingText)
		heading.verticalPositionMode = "PIXEL"
		TextStyles.setStyle( heading, HEADING_TEXT_STYLE )
		heading.position.y = MARGIN_TOP
		page.addChild( heading )
		
		return page, MARGIN_TOP + HEADING_GAP


	def onBound( self ):
		PyGUI.DraggableWindow.onBound( self )
		self._initPages()
		self.updateHelp()

