'''
'''


import BigWorld
import GUI
import Keys
import TextStyles
from PyGUIBase import PyGUIBase
from VisualStateComponent import VisualState, VisualStateComponent, StandardComponentState
import Utils


def _getRadioParent( parent, groupDepth ):
	while groupDepth > 1 and parent is not None:
		parent = parent.parent
		groupDepth -= 1
	return parent


def _sameRadioButtonGroup( comp, groupName ):
	return (comp.script \
			and getattr(comp.script, "buttonStyle", None) == Button.RADIOBUTTON_STYLE \
			and comp.script.groupName == groupName)


def _getRadioButtons( comp, groupName ):
	if comp is None:
		return []
	else:
		radioButtons = []
		for (name,child) in comp.children:
			radioButtons += _getRadioButtons( child, groupName )
			if _sameRadioButtonGroup(child, groupName):
				radioButtons.append( child )
		return radioButtons


class ButtonVisualState( VisualState ):

	def __init__( self ):
		VisualState.__init__( self )
		self.icon = StandardComponentState()
		self.frame = None

	def onSave( self, dataSection ):
		VisualState.onSave( self, dataSection )
		if self.textStyle:
			dataSection.writeString( "textStyle", self.textStyle )
		self.icon.onSave( dataSection.createSection( "icon" ) )
		if self.frame is not None:
			self.frame.onSave( dataSection.createSection( "frame" ) )

	def onLoad( self, dataSection ):
		VisualState.onLoad( self, dataSection )
		self.textStyle = dataSection.readString( "textStyle", "" )
		if dataSection.has_key( "icon" ):
			self.icon.onLoad( self, dataSection._icon )
		if dataSection.has_key( "frame" ):
			self.frame = StandardComponentState()
			self.frame.onLoad( self, dataSection._frame )

	def apply( self, componentScript ):
		VisualState.apply( self, componentScript )
		if getattr( componentScript, "buttonLabel", None ) is not None and self.textStyle:
			TextStyles.setStyle( componentScript.buttonLabel, self.textStyle )

		if hasattr( componentScript, "buttonIcon" ):
			self.icon.apply( componentScript.buttonIcon )
			
		if self.frame is not None and hasattr( componentScript.component, "frame" ):
			self.frame.apply( componentScript.component.frame )


class Button( PyGUIBase, VisualStateComponent ):

	PRESSBUTTON_STYLE = 'pressbutton'
	TOGGLEBUTTON_STYLE = 'togglebutton'
	CHECKBOX_STYLE = 'checkbox'
	RADIOBUTTON_STYLE = 'radiobutton'
	TOGGLABLE_BUTTON_STYLES = (TOGGLEBUTTON_STYLE, CHECKBOX_STYLE, RADIOBUTTON_STYLE)

	NORMAL_STATE = 'normal'
	HOVER_STATE = 'hover'
	PRESSED_STATE = 'pressed'
	ACTIVE_STATE = 'active'
	DISABLED_STATE = 'disabled'
	HOVER_ACTIVE_STATE = 'hover_active'
	PRESSED_ACTIVE_STATE = 'pressed_active'
	DISABLED_ACTIVE_STATE = 'disabled_active'

	factoryString="PyGUI.Button"
	visualStateString="PyGUI.ButtonVisualState"

	def __init__( self, component ):
		PyGUIBase.__init__( self, component )
		VisualStateComponent.__init__( self, component, Button.visualStateString )
		
		self.component.focus = True
		self.component.mouseButtonFocus = True
		self.component.moveFocus = True
		self.component.crossFocus = True

		self.buttonStyle = Button.PRESSBUTTON_STYLE
		self.buttonPressed = False
		self.buttonActive = False
		self.buttonDisabled = False
		self.groupName = ""
		self.groupDepth = 1
		self.hovering = False

		self.onClick = lambda:None
		self.onActivate = lambda:None
		self.onDeactivate = lambda:None


	def _updateVisualState( self ):
		if self.buttonDisabled:
			visualStateName = Button.DISABLED_STATE if not self.buttonActive else Button.DISABLED_ACTIVE_STATE
		elif self.buttonPressed and self.hovering:
			visualStateName = Button.PRESSED_STATE if not self.buttonActive else Button.PRESSED_ACTIVE_STATE
		elif self.hovering:
			visualStateName = Button.HOVER_STATE if not self.buttonActive else Button.HOVER_ACTIVE_STATE
		else:
			visualStateName = Button.NORMAL_STATE if not self.buttonActive else Button.ACTIVE_STATE

		self.setVisualState( visualStateName )


	def _onClick( self ):
		if self.buttonDisabled:
			return

		if self.buttonStyle in Button.TOGGLABLE_BUTTON_STYLES:
			self._makeActive( not self.buttonActive )
			if self.buttonActive:
				self.onActivate()
			else:
				self.onDeactivate()
		self.onClick()

	def setDisabledState( self, state ):
		if self.buttonDisabled == state:
			return

		self.buttonDisabled = state
		self._updateVisualState()


	def setToggleState( self, state ):
		self._makeActive( state )
		self._updateVisualState()
		
	def setLabel( self, value ):
		if self.buttonLabel is not None:
			self.buttonLabel.text = value

	def _makeActive( self, active = True ):
		if self.buttonStyle == Button.RADIOBUTTON_STYLE:
			if self.buttonActive == True:
				# We're already active. Don't call base so it won't deactivate us.
				return

			if active:
				# We're about to come active, disable all our siblings in the same group.
				radioParent = _getRadioParent( self.component.parent, self.groupDepth )
				siblings = _getRadioButtons( radioParent, self.groupName )
				siblings = [ sibling for sibling in siblings if sibling.script != self ]
				for sibling in siblings:
					if sibling.script.buttonActive:
						sibling.script.buttonActive = False
						sibling.script.onDeactivate()
						sibling.script._updateVisualState()

		if self.buttonStyle in Button.TOGGLABLE_BUTTON_STYLES:
			self.buttonActive = active


	def handleMouseButtonEvent( self, comp, event ):
		PyGUIBase.handleMouseButtonEvent( self, comp, event )

		if event.key == Keys.KEY_LEFTMOUSE:
			if event.isKeyDown() and not self.buttonPressed:
				self.buttonPressed = True
			elif not event.isKeyDown() and self.buttonPressed:
				self.buttonPressed = False
				self._onClick()

		self._updateVisualState()
		return True


	def handleMouseEnterEvent( self, comp ):
		PyGUIBase.handleMouseEnterEvent( self, comp )

		# Only stay pressed if the LMB is still down.
		self.buttonPressed = self.buttonPressed and BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
		self.hovering = True
		self._updateVisualState()

		return True


	def handleMouseLeaveEvent( self, comp ):
		PyGUIBase.handleMouseLeaveEvent( self, comp )
		self.hovering = False
		self._updateVisualState()
		return True


	def onSave( self, dataSection ):
		PyGUIBase.onSave( self, dataSection )

		dataSection.writeBool( "buttonDisabled", self.buttonDisabled )
		dataSection.writeString( "buttonStyle", self.buttonStyle )
		if self.groupName != "":
			dataSection.writeString( "groupName", self.groupName )
			dataSection.writeInt( "groupDepth", self.groupDepth )
		VisualStateComponent.onSave( self, dataSection )


	def onLoad( self, dataSection ):
		PyGUIBase.onLoad( self, dataSection )

		self.buttonStyle = dataSection.readString( "buttonStyle" )
		self.buttonDisabled = dataSection.readBool( "buttonDisabled", False )
		self.groupName = dataSection.readString( "groupName" )
		self.groupDepth = dataSection.readInt( "groupDepth", 1 )
		VisualStateComponent.onLoad( self, dataSection )

	def onBound( self ):
		self._updateVisualState()
		
	def doLayout( self, parent ):
		PyGUIBase.doLayout( self, parent )
		self._updateVisualState()
		
	@property
	def buttonIcon( self ):
		return self.component
		
	@property
	def buttonLabel( self ):
		return getattr( self.component, "label", None )
		
	
		

	@staticmethod
	def create( texture="", label="", visualStates="", toggle=False, **kwargs ):
		c = GUI.Window( texture )
		c.materialFX = 'BLEND'
		c.widthMode = 'CLIP'
		c.heightMode = 'CLIP'
		c.horizontalPositionMode = 'CLIP'
		c.verticalPositionMode = 'CLIP'

		c.label = GUI.Text( label )

		b = Button( c, **kwargs )
		if visualStates:
			b.loadVisualStates( visualStates )
			
		b.onBound()
		b.toggleButton = toggle
		return c
