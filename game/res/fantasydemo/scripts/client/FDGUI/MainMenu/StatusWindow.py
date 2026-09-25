import BigWorld
import Keys

import Helpers.PyGUI as PyGUI


class StatusWindow( PyGUI.EscapableWindow ):

	factoryString = "FDGUI.MainMenuStatusWindow"
	
	def __init__( self, component ):
		PyGUI.EscapableWindow.__init__( self, component )		
		self.bigFont = "default_medium.font"
		self.smallFont = "default_small.font"
		
	def onLoad( self, section ):
		PyGUI.EscapableWindow.onLoad( self, section )
		self.smallFont = section.readString( "smallFont", self.smallFont )
		self.bigFont = section.readString( "bigFont", self.bigFont )
		
	def onBound( self ):
		PyGUI.EscapableWindow.onBound( self )
		self.origWidth = self.component.width
		self.origWidthMode = self.component.widthMode
		self.origHeight = self.component.height
		self.origHeightMode = self.component.heightMode
		
		
	def doLayout( self, parent ):
		PyGUI.EscapableWindow.doLayout( self, parent )
		
		textContainer = self.component.textContainer
		buttonContainer = self.component.buttonContainer
		caption = textContainer.text
		spinner = textContainer.spinner
		details = self.component.details
		
		gotButtons = self.component.buttonContainer.visible		
		gotDetailButton = buttonContainer.detailsButton.visible
		gotDetails = details.visible
		
		# Reset to default size to start with
		self.component.widthMode = self.origWidthMode
		self.component.width = self.origWidth
		self.component.heightMode = self.origHeightMode
		self.component.height = self.origHeight
		
		# Setup an appropriate font
		screenWidth, screenHeight = BigWorld.screenSize()
		if screenWidth < 700 or screenHeight < 700:
			caption.font = self.smallFont
		else:
			caption.font = self.bigFont
		
		# Size the text container to fit content
		hps = PyGUI.Utils.getHPixelScalar()
		vps = PyGUI.Utils.getVPixelScalar()
		
		sw, sh = PyGUI.Utils.pixelSize( spinner )
		tw, th = caption.stringDimensions( caption.text+'  ' )
		tw *= hps
		th *= vps
		
		textContainer.widthMode = "PIXEL"
		textContainer.heightMode = "PIXEL"
		textContainer.width = tw + sw
		textContainer.height = max(sh, th)
		
		# Setup the width of the dialog to fit the caption
		self.component.widthMode = "PIXEL"
		self.component.width = (tw + hps*sw) + 100
			
		# Put the caption in the correct spot.
		textContainer.verticalPositionMode = "CLIP"
		textContainer.position.y = 0
		if gotButtons:
			textContainer.verticalAnchor = "BOTTOM"
		else:
			textContainer.verticalAnchor = "CENTER"
			
		if gotDetails:
			textContainer.verticalPositionMode = "PIXEL" # make it stay where it is relative to the top
			textContainer.heightMode = "PIXEL"
			
			# Position details box just under
			details.verticalPositionMode = "PIXEL"
			details.verticalAnchor = "TOP"
			details.position.y = textContainer.position.y + 10
			
			self.component.widthMode = "PIXEL"
			if self.component.width < screenWidth * 0.75:
				self.component.width = screenWidth * 0.75
		
			details.horizontalPositionMode = "PIXEL"
			details.widthMode = details.heightMode = "PIXEL"
			details.width = self.component.width - details.position.x * 2
			details.script._recalcWrapping()
			
			dw, dh = details.text.stringDimensions( details.text.text )
			dw *= hps
			dh *= vps
			details.height = dh
			
			self.component.height += dh
			
		# Setup the button positions
		okButton = buttonContainer.okButton
		detailsButton = buttonContainer.detailsButton
		
		okButton.widthMode = "PIXEL"
		buttonWidth = okButton.width
		if gotDetailButton:
			buttonWidth = buttonWidth * 2 + 25;
		
		buttonContainer.widthMode = "PIXEL"
		buttonContainer.width = buttonWidth		
		
		buttonContainer.verticalPositionMode = "PIXEL"
		buttonContainer.position.y = self.component.height - 20
			
			
	def setupStatus( self, message, showSpinner=False, okButton=False, onEscape=None, detailMsg=None ):
		self.component.textContainer.text.text = message
		self.component.textContainer.spinner.visible = showSpinner
		self.component.buttonContainer.visible = okButton
		self.detailMsg = detailMsg
		self.onEscape = onEscape
		
		self.component.details.script.clear()
		if detailMsg is not None:
			self.component.details.script.appendLine( self.detailMsg )
		self.component.details.visible = False
		self.component.buttonContainer.detailsButton.visible = detailMsg is not None
		
		self.doLayout( self.component.parent )
		
		
	def handleKeyEvent( self, event ):
		# If we have the OK button, then let the user hit enter to keep going.
		if self.component.buttonContainer.visible:
			if event.isKeyDown() and event.key == Keys.KEY_RETURN:
				if self.onEscape is not None:
					self.onEscape()
					return True
		return PyGUI.EscapableWindow.handleKeyEvent( self, event )
		
		
	@PyGUI.PyGUIEvent( "buttonContainer.okButton", "onClick" )
	def buttonClicked( self ):
		self.onEscape()
		
	@PyGUI.PyGUIEvent( "buttonContainer.detailsButton", "onClick" )
	def detailsButtonClicked( self ):
		self.component.details.visible = True
		self.component.buttonContainer.detailsButton.visible = False
		self.doLayout( self.component.parent )
	