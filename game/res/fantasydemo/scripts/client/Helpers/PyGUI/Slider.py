'''
'''

import BigWorld, GUI
import Keys
import math

from PyGUIBase import PyGUIBase
from DraggableComponent import DraggableComponent
from Utils import clipPosition, clipSize, applyMapping
from VisualStateComponent import VisualState, VisualStateComponent, StandardComponentState


class SliderVisualState( VisualState ):

	def __init__( self ):
		VisualState.__init__( self )
		self.background = StandardComponentState()
		self.thumb = StandardComponentState()


	def onSave( self, dataSection ):
		VisualState.onSave( self, dataSection )
		backgroundSection = dataSection.createSection( "background" )
		self.background.onSave( backgroundSection )

		thumbSection = dataSection.createSection( "thumb" )
		self.thumb.onSave( thumbSection )


	def onLoad( self, dataSection ):
		VisualState.onLoad( self, dataSection )

		if dataSection.has_key( "background" ):
			backgroundSection = dataSection._background
			self.background.onLoad( self, backgroundSection )

		if dataSection.has_key( "thumb" ):
			thumbSection = dataSection._thumb
			self.thumb.onLoad( self, thumbSection )


	def apply( self, componentScript ):
		VisualState.apply( self, componentScript )
		if hasattr( componentScript, "sliderBackground" ):
			self.background.apply( componentScript.sliderBackground )

		if hasattr( componentScript, "sliderThumb" ):
			self.thumb.apply( componentScript.sliderThumb )


class SliderThumb( PyGUIBase, DraggableComponent ):

	factoryString="PyGUI.SliderThumb"

	def __init__( self, component, isHorizontal = True ):
		PyGUIBase.__init__( self, component )
		DraggableComponent.__init__( self, isHorizontal, not isHorizontal, True )

		self.component.focus = True
		self.component.mouseButtonFocus = True
		self.component.moveFocus = True
		self.component.crossFocus = True

		self.onBeginDrag = self._onBeginDrag
		self.onEndDrag = self._onEndDrag
		self.onDragging = self._onDragging


	def _setValue( self, value ):
		sliderWidth, sliderHeight = clipSize( self.component )

		slider = self.component.parent.script
		thumbPos = (value - slider.minValue) / (slider.maxValue - slider.minValue)
		if slider.isHorizontal:
			thumbPos = (2.0 - sliderWidth) * thumbPos - 1.0 + sliderWidth / 2
		else:
			thumbPos = (2.0 - sliderHeight) * thumbPos - 1.0 + sliderHeight / 2
		self.component.position = (thumbPos, 0, 1) if slider.isHorizontal else (0, thumbPos, 1)


	def _setValueFromMouse( self, pos ):
		slider = self.component.parent.script
		parent = self.component.parent
		
		origHorzPosMode = self.component.horizontalPositionMode
		self.component.horizontalPositionMode = "CLIP"
		origParentWidthMode = parent.widthMode
		parent.widthMode = "PIXEL"
		
		position = parent.screenToLocal( pos )
		self.component.position = (2 * position[0] / parent.width - 1.0, 0, 1) \
							if slider.isHorizontal else (0, 2 * position[1] / parent.height - 1.0, 1)
		
		parent.widthMode = origParentWidthMode
		self.component.horizontalPositionMode = origHorzPosMode
		self._onDragging()

		
	def _onBeginDrag( self ):
		slider = self.component.parent.script
		slider.onBeginDrag( slider.value )
		
	def _onEndDrag( self ):
		slider = self.component.parent.script
		slider.onEndDrag( slider.value )

	def _onDragging( self ):
		position = clipPosition( self.component )
		sliderWidth, sliderHeight = clipSize( self.component )
		slider = self.component.parent.script
		if slider.isHorizontal:
			thumbPos = (position[0] + 1.0 - sliderWidth / 2) / (2.0 - sliderWidth)
		else:
			thumbPos = (position[1] + 1.0 - sliderHeight / 2) / (2.0 - sliderHeight)

		thumbPos = min( max( 0.0, thumbPos ), 1.0 )
		newValue = thumbPos * (slider.maxValue - slider.minValue) + slider.minValue
		newValue += slider.stepSize / 2.0
		newValue -= math.fmod( newValue, slider.stepSize )

		# Causes the thumb to move to the new step position
		self._setValue( newValue )

		slider.value = newValue
		slider.onValueChanged( newValue )


	def handleMouseButtonEvent( self, comp, event ):
		PyGUIBase.handleMouseButtonEvent( self, comp, event )

		slider = self.component.parent.script
		if event.key == Keys.KEY_LEFTMOUSE:
			if event.isKeyDown() and not slider.thumbPressed:
				slider.thumbPressed = True
			elif not event.isKeyDown() and slider.thumbPressed:
				slider.thumbPressed = False
		slider._updateVisualState( hover=True )

		return DraggableComponent.handleMouseButtonEvent( self, comp, event )


	def handleMouseEnterEvent( self, comp ):
		PyGUIBase.handleMouseEnterEvent( self, comp )

		slider = self.component.parent.script
		slider.handleMouseEnterEvent( comp )

		# Only stay pressed if the LMB is still down.
		slider.thumbPressed = slider.thumbPressed and BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
		slider._updateVisualState( hover=True )
		return True


	def handleMouseLeaveEvent( self, comp ):
		slider = self.component.parent.script
		slider._updateVisualState( hover=False )
		return True


	@staticmethod
	def create( slider, thumbTexture = "", isHorizontal = True ):
		c = GUI.Window( thumbTexture )
		c.materialFX = "BLEND"
		c.widthMode = slider.component.widthMode
		c.heightMode = slider.component.heightMode
		c.horizontalPositionMode = 'CLIP'
		c.verticalPositionMode = 'CLIP'
		c.position = (0, 0, 1)

		slider.component.addChild( c, "thumb" )

		s = SliderThumb( c, isHorizontal )
		s.onBound()
		return s


class Slider( PyGUIBase, VisualStateComponent ):

	NORMAL_STATE = 'normal'
	HOVER_STATE = 'hover'
	PRESSED_STATE = 'pressed'
	DISABLED_STATE = 'disabled'

	factoryString="PyGUI.Slider"
	visualStateString="PyGUI.SliderVisualState"

	def __init__( self, component ):
		PyGUIBase.__init__( self, component )
		VisualStateComponent.__init__( self, component, Slider.visualStateString )
		component.script = self

		self.isHorizontal = True
		self.minValue = 0.0
		self.maxValue = 1.0
		self.stepSize = 0.1
		self._value = 0.0

		self.thumbPressed = False
		self.sliderDisabled = False

		self.component.focus = True
		self.component.mouseButtonFocus = True
		self.component.crossFocus = True
		self.component.moveFocus = True

		self.onBeginDrag = lambda v:None
		self.onEndDrag = lambda v:None
		self.onValueChanged = lambda v:None


	def _updateVisualState( self, hover ):
		if self.sliderDisabled:
			visualStateName = Slider.DISABLED_STATE
		elif self.thumbPressed:
			visualStateName = Slider.PRESSED_STATE
		elif hover:
			visualStateName = Slider.HOVER_STATE
		else:
			visualStateName = Slider.NORMAL_STATE

		self.setVisualState( visualStateName )


	def _onValueChanged( self ):
		self.onValueChanged( self.value )


	def _getValue( self ):
		return self._value

	def _setValue( self, value ):
		self._value = value
		self.component.thumb.script._setValue( value )

	value = property( _getValue, _setValue )


	def handleMouseButtonEvent( self, comp, event ):
		if event.key == Keys.KEY_LEFTMOUSE and event.isKeyDown():
			self.component.thumb.script._setValueFromMouse( event.cursorPosition )
			# Call this to start dragging the thumb, now that it's been moved into position.
			self.component.thumb.script.handleMouseButtonEvent( self.component.thumb, event )
		return True


	def onSave( self, dataSection ):
		PyGUIBase.onSave( self, dataSection )
		dataSection.writeBool( "isHorizontal", self.isHorizontal )
		dataSection.writeFloat( "minValue", self.minValue )
		dataSection.writeFloat( "maxValue", self.maxValue )
		dataSection.writeFloat( "value", self._value )
		dataSection.writeFloat( "stepSize", self.stepSize )
		VisualStateComponent.onSave( self, dataSection )


	def onLoad( self, dataSection ):
		PyGUIBase.onLoad( self, dataSection )
		self.isHorizontal = dataSection.readBool( "isHorizontal", self.isHorizontal )
		self.minValue = dataSection.readFloat( "minValue", self.minValue )
		self.maxValue = dataSection.readFloat( "maxValue", self.maxValue )
		self.stepSize = dataSection.readFloat( "stepSize", self.stepSize )
		self._value = dataSection.readFloat( "value", self._value )
		VisualStateComponent.onLoad( self, dataSection )


	def onBound( self ):
		self.value = self._value
		self.sliderBackground = self.component
		self.sliderThumb = self.component.thumb
		self._updateVisualState( hover=False )


	@staticmethod
	def create( texture="", thumbTexture="", isHorizontal=True, minValue=0.0, maxValue=1.0, visualStates="", **kwargs ):
		c = GUI.Window( texture )
		c.materialFX = 'BLEND'
		c.widthMode = 'CLIP'
		c.heightMode = 'CLIP'
		c.horizontalPositionMode = 'CLIP'
		c.verticalPositionMode = 'CLIP'

		s = Slider( c, **kwargs )
		s.minValue = minValue
		s.maxValue = maxValue
		s.isHorizontal = isHorizontal

		thumb = SliderThumb.create( s, thumbTexture, isHorizontal )
		thumb.width = 0.2 if isHorizontal else 2.0
		thumb.height = 2.0 if isHorizontal else 0.2
		
		if visualStates:
			s.loadVisualStates( visualStates )

		s.onBound()
		return c

