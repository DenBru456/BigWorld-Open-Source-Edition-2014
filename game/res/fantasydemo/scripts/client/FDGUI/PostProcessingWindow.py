# -*- coding: utf-8 -*-

import BigWorld
import Helpers.PyGUI as PyGUI
import ResMgr
import Keys
from bwdebug import ERROR_MSG
from bwdebug import INFO_MSG
import Cursor
import PostProcessing
from PostProcessing.Effects import *

from Helpers.PyGUI import PyGUIEvent
from FDToolTip import ToolTipInfo

import traceback
import weakref

class EffectSliderInfo:
	def __init__( self, prop, min = 0.0, max = 1.0, uiDesc = "" ):
		self.prop = prop
		self.minValue = min
		self.maxValue = max
		self.uiDesc = uiDesc


	def apply( self, slider, label, amountLabel ):

		# Dummy slider - mark as "Unavailable" 
		if self.uiDesc == DUMMY_SLIDER_NAME:
			label.text = "Unavailable"
			amountLabel.text = ""
			slider.script._setValue( 0 )

		# Real slider - get name and value
		else:
			label.text = self.uiDesc
			slider.script.minValue = self.minValue
			slider.script.maxValue = self.maxValue
			slider.script.stepSize = (self.maxValue - self.minValue) / 500.0
			try:
				value = self.prop.get()
				if value != None:
					try:
						amountLabel.text = self.prop.format(value)
						slider.script._setValue( value )
					except:
						amountLabel.text = "err"
			except NameError:
				label.text = "Unavailable"
				amountLabel.text = ""


	def updateAmountLabel( self, label ):
		
		# Get value
		value = None
		if self.uiDesc != DUMMY_SLIDER_NAME:
			value = self.prop.get()

		# Update label
		if value != None:
			label.text = self.prop.format(value)

OFF_BUTTON_PRESET = "off"
DEFAULT_BUTTON_PRESET = "default"
DEFAULT_PLUS_BUTTON_PRESET = "default plus"
FXAA_BUTTON_PRESET = "fxaa"
FXAA_PLUS_BUTTON_PRESET = "fxaa plus"
NEXT_BUTTON_PRESET = "next"
PREVIOUS_BUTTON_PRESET = "previous"
DUMMY_BUTTON_PRESET = "unavailable"

DUMMY_SLIDER_NAME = "Dummy slider"
DUMMY_SLIDER_VALUE = MaterialFloatProperty( "Dummy slider", -1, "alpha", primary = True )

class EffectButtonInfo:
	def __init__( self, name, tooltip, preset, sl1 = None, sl2 = None, sl3 = None ):
		self.name = name
		self.tooltip = tooltip
		self.preset = preset

		if sl1 is None:
			sl1 = DUMMY_SLIDER_NAME

		if sl2 is None:
			sl2 = DUMMY_SLIDER_NAME

		if sl3 is None:
			sl3 = DUMMY_SLIDER_NAME

		self.sliderName = [sl1,sl2,sl3]

		self.component = None


	def isSupported( self ):
		if self.preset is not None:
			if self.preset == OFF_BUTTON_PRESET:
				return True
			if self.preset == NEXT_BUTTON_PRESET:
				return True
			if self.preset == PREVIOUS_BUTTON_PRESET:
				return True
			elif self.preset == DEFAULT_BUTTON_PRESET:
				return True
			elif self.preset == DEFAULT_PLUS_BUTTON_PRESET:
				return True
			else:

				supported = False
				try:
					supported = PostProcessing.isSupported( self.preset )
				except AttributeError as e:
					ERROR_MSG( "%s not supported: %s" % ( self.preset, e ) )
				except ValueError as e:
					ERROR_MSG( "%s not supported: %s" % ( self.preset, e ) )

				return supported
		else:
			#it comes down to the sliders.  Currently just
			#allow the button to be supported, and the sliders
			#themselves report as 'unavailable' or not.
			return True

class PostProcessingWindow( PyGUI.DraggableWindow ):

	PAGE_COUNT = 2
	BUTTONS_PER_PAGE = 8
	SLIDERS_PER_PAGE = 3

	factoryString = "FDGUI.PostProcessingWindow"
	sliders = {}
	sliders['Sharpness'] = EffectSliderInfo( Sharpen.amount,0.0,1.0,"Sharpness" )

	sliders['Colour Correction'] = EffectSliderInfo( ColourCorrect.amount,0.0,1.0,"Colour Correction" )
	sliders['Saturation'] = EffectSliderInfo( ColourCorrect.saturation,-1.0,1.0,"Saturation" )
	sliders['Brightness'] = EffectSliderInfo( ColourCorrect.brightness,-1.0,1.0,"Brightness" )
	sliders['Tone Map'] = EffectSliderInfo( ColourCorrect.toneMap,0.0,1.0,"Tone Map" )

	sliders['Bloom'] = EffectSliderInfo( Bloom.amount, 0.0,2.0,"Bloom Amount" )
	#sliders['Focal Length'] = EffectSliderInfo( DepthOfField.focalLength,0.0,0.5,"Focal Length" )
	#sliders['Aperture'] = EffectSliderInfo( DepthOfField.aperture,0.001,0.1,"Aperture" )
	#sliders['Focal Distance'] = EffectSliderInfo( DepthOfField.zFocus,0.1,100.0,"Focal Distance" )
	sliders['Noise Threshold'] = EffectSliderInfo( ScotopicVision.noiseThreshold,0.0,1.0,"Noise Threshold" )
	sliders['Noise Level'] = EffectSliderInfo( ScotopicVision.noiseLevel,0.0,20.0,"Noise Level" )
	sliders['Texture Scale'] = EffectSliderInfo( ScotopicVision.textureScale,0.1,15.0,"Texture Scale" )
	sliders['Edge Dilation Threshold'] = EffectSliderInfo( Posterise.edgeDilation,0.0,1.0,"Edge Dilation Threshold" )
	sliders['PoEAmount'] = EffectSliderInfo( Posterise.amount,0.0,1.0,"Amount" )
	#sliders['SetMaxCoC2'] = EffectSliderInfo( DepthOfField.maxCoC2,0.0,64.0,"Circle of Confusion max." )
	#sliders['Bokeh Amount'] = EffectSliderInfo( DepthOfField.bokehAmount,0.0,4.0,"Bokeh Amount" )
	#sliders['Bokeh Type'] = EffectSliderInfo( DepthOfField.bokehType,0.0,1.0,"Bokeh Type" )
	#sliders['Dof2Falloff'] = EffectSliderInfo( DepthOfField.falloff,0.0,10.0,"Falloff" )
	#sliders['Dof2ZNear'] = EffectSliderInfo( DepthOfField.zNear,0.0,1.0,"Near Z" )
	#sliders['Dof2ZFar'] = EffectSliderInfo( DepthOfField.zFar,0.0,1.0,"Far Z" )
	sliders['DistortAlpha'] = EffectSliderInfo( DistortionTransfer.alpha,0.0,1.0,"Alpha" )
	sliders['DistortScale'] = EffectSliderInfo( DistortionTransfer.scale,0.0,1.0,"Amount" )
	sliders['DistortTile'] = EffectSliderInfo( DistortionTransfer.tile,1.0,128.0,"Tile" )
	sliders['FilmGrainAlpha'] = EffectSliderInfo( FilmGrain.alpha,0.0,5.0,"Alpha" )
	sliders['Speed'] = EffectSliderInfo( FilmGrain.speed,0.0,0.5,"Speed" )
	sliders['FilmGrainScale'] = EffectSliderInfo( FilmGrain.scale,1.0,50.0,"Scale" )
	sliders['FilmGrainAlpha2'] = EffectSliderInfo( FilmGrain.alpha2,0.0,5.0,"Alpha" )
	sliders['Speed2'] = EffectSliderInfo( FilmGrain.speed2,0.0,0.5,"Speed" )
	sliders['FilmGrainScale2'] = EffectSliderInfo( FilmGrain.scale2,1.0,50.0,"Scale" )
	sliders['Hatching Power'] = EffectSliderInfo( Hatching.power,0.5,64.0,"Power" )
	sliders['Hatching Tile'] = EffectSliderInfo( Hatching.tile,1.0,128.0,"Tile" )
	sliders['Hatching Scale'] = EffectSliderInfo( Hatching.scale,0.0,15.0,"Scale" )
	#sliders['Dof3Alpha'] = EffectSliderInfo( DepthOfField.dof3Alpha,0.0,1.0,"Alpha" )
	#sliders['Dof3Overdrive'] = EffectSliderInfo( DepthOfField.dof3Overdrive,0.0,5.0,"Overdrive" )
	#sliders['Rainbow Amount'] = EffectSliderInfo( Rainbow.amount,0.0,1.0,"Amount" )
	#sliders['Rainbow Droplet Size'] = EffectSliderInfo( Rainbow.dropletSize,0.0,1.0,"Droplet Size" )

	# Use this slider when you don't have another value to adjust
	sliders[DUMMY_SLIDER_NAME] = EffectSliderInfo( DUMMY_SLIDER_VALUE, 0.0, 1.0, DUMMY_SLIDER_NAME )
	
	buttons = []

	# Name of button, preset xml file, then the identifier of the 3 sliders for that page.
	# The "default" and "fxaa" presets are special cases, they do not specify
	# a file here, they load a file based on the current "high", "med" or "low"
	# graphics setting
	# The "unavailable" preset is for placeholder buttons, that are disabled
	# and made invisible
	buttons.append( EffectButtonInfo(
	'Off',
	"Turn off post processing",
	OFF_BUTTON_PRESET ) )

	buttons.append( EffectButtonInfo(
	'Next',
	"Next page",
	NEXT_BUTTON_PRESET ) )

	buttons.append( EffectButtonInfo(
	'Previous',
	"Previous page",
	PREVIOUS_BUTTON_PRESET ) )

	buttons.append( EffectButtonInfo(
	'Default only',
	"Default post processing chain",
	DEFAULT_BUTTON_PRESET,
	'Sharpness',
	'Colour Correction',
	'Tone Map') )

	buttons.append( EffectButtonInfo(
	'Def+weather',
	"Default plus weather effects",
	DEFAULT_PLUS_BUTTON_PRESET,
	'Sharpness',
	'Colour Correction',
	'Tone Map') )

	buttons.append( EffectButtonInfo(
	'C. Aberration',
	"Chromatic aberration",
	"system/post_processing/chains/chromatic aberration.ppchain" ) )

	buttons.append( EffectButtonInfo(
	'B/W',
	"Quantised black & white",
	"system/post_processing/chains/quantised_black_and_white.ppchain" ) )

	buttons.append( EffectButtonInfo(
	'Underwater',
	"Underwater",
	"system/post_processing/chains/underwater.ppchain" ) )

	buttons.append( EffectButtonInfo(
	'Tone Mapping',
	"Tone mapping",
	"system/post_processing/chains/preset_tone_mapping.ppchain",
	'Colour Correction',
	'Tone Map',
	'Saturation') )

	buttons.append( EffectButtonInfo(
	'Cartoon',
	"Cartoon",
	"system/post_processing/chains/preset_cartoon.ppchain",
	'PoEAmount',
	'Edge Dilation Threshold',
	'Saturation') )

	buttons.append( EffectButtonInfo(
	'Film Noir',
	"Flim noir",
	"system/post_processing/chains/preset_film_noir.ppchain",
	'Saturation',
	'FilmGrainScale',
	'FilmGrainScale2') )

	buttons.append( EffectButtonInfo(
	'Cross Hatching',
	"Cross hatching",
	"system/post_processing/chains/preset_cross_hatching.ppchain",
	'Hatching Scale',
	'Hatching Power',
	'Hatching Tile') )

	buttons.append( EffectButtonInfo(
	'Night Vision',
	"Night vision",
	"system/post_processing/chains/preset_night_vision.ppchain",
	'Noise Threshold',
	'Noise Level',
	'Texture Scale') )

	buttons.append( EffectButtonInfo(
	'Weird',
	"Freaky...",
	"system/post_processing/chains/preset_weird.ppchain",
	'Sharpness',
	'Saturation',
	'Brightness') )

	# Dummy b
	buttons.append( EffectButtonInfo( "Unavailable1", "Unavailable", DUMMY_BUTTON_PRESET ) )
	buttons.append( EffectButtonInfo( "Unavailable2", "Unavailable", DUMMY_BUTTON_PRESET ) )
	buttons.append( EffectButtonInfo( "Unavailable3", "Unavailable", DUMMY_BUTTON_PRESET ) )
	buttons.append( EffectButtonInfo( "Unavailable4", "Unavailable", DUMMY_BUTTON_PRESET ) )
	buttons.append( EffectButtonInfo( "Unavailable5", "Unavailable", DUMMY_BUTTON_PRESET ) )
	buttons.append( EffectButtonInfo( "Unavailable6", "Unavailable", DUMMY_BUTTON_PRESET ) )
	buttons.append( EffectButtonInfo( "Unavailable7", "Unavailable", DUMMY_BUTTON_PRESET ) )
	buttons.append( EffectButtonInfo( "Unavailable8", "Unavailable", DUMMY_BUTTON_PRESET ) )

	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )
		self.dg = None
		PostProcessing.registerGraphicsSettingListener( self._onSelectQualityOption )

	def printChain( self ):
		'''
		Print the effects and phases contained in the current chain.
		'''
		if PostProcessing.chain() is not None:
			for e in PostProcessing.chain():
				INFO_MSG("effect %s" % (e.name,))
				for p in e.phases:
					INFO_MSG("    phase %s" % (p.name,))

		return
	def setPage( self, page ):
		self.buttons = []

		# Make sure page is between 0 and PAGE_COUNT
		page = page % PostProcessingWindow.PAGE_COUNT
		self._page = page

		# When adding pages here, check the page number and PAGE_COUNT
		# are correct
		# Use the "Unavailable[1-8]" buttons if you want a blank space
		if page == 0:
			self.buttons.append( "Def+weather" )
			self.buttons.append( "Default only" )
			self.buttons.append( "Tone Mapping" )
			self.buttons.append( "Off" )
			self.buttons.append( "Cartoon" )
			self.buttons.append( "Film Noir" )
			self.buttons.append( "Previous" )
			self.buttons.append( "Next" )
		elif page == 1:
			self.buttons.append( "Cross Hatching" )
			self.buttons.append( "Night Vision" )
			self.buttons.append( "Weird" )
			self.buttons.append( "C. Aberration" )
			self.buttons.append( "B/W" )
			self.buttons.append( "Underwater" )
			self.buttons.append( "Previous" )
			self.buttons.append( "Next" )
		else:
			ERROR_MSG( "Unknown page %d" % ( page, ) )
			self.buttons.append( "Unavailable1" )
			self.buttons.append( "Unavailable2" )
			self.buttons.append( "Unavailable3" )
			self.buttons.append( "Unavailable4" )
			self.buttons.append( "Unavailable5" )
			self.buttons.append( "Unavailable6" )
			# Add next/previous buttons so the user can get back
			self.buttons.append( "Previous" )
			self.buttons.append( "Next" )

		assert( len(self.buttons) == PostProcessingWindow.BUTTONS_PER_PAGE )

		effectsGrid = self.component.effectsGrid
		self._findButtonInfo(0).component 	= weakref.proxy( effectsGrid.effect1Button.box )
		self._findButtonInfo(0).label 		= weakref.proxy( effectsGrid.effect1Button.label )
		self._findButtonInfo(1).component 	= weakref.proxy( effectsGrid.effect2Button.box )
		self._findButtonInfo(1).label 		= weakref.proxy( effectsGrid.effect2Button.label )
		self._findButtonInfo(2).component 	= weakref.proxy( effectsGrid.effect3Button.box )
		self._findButtonInfo(2).label 		= weakref.proxy( effectsGrid.effect3Button.label )
		self._findButtonInfo(3).component 	= weakref.proxy( effectsGrid.effect4Button.box )
		self._findButtonInfo(3).label 		= weakref.proxy( effectsGrid.effect4Button.label )
		self._findButtonInfo(4).component 	= weakref.proxy( effectsGrid.effect5Button.box )
		self._findButtonInfo(4).label 		= weakref.proxy( effectsGrid.effect5Button.label )
		self._findButtonInfo(5).component 	= weakref.proxy( effectsGrid.effect6Button.box )
		self._findButtonInfo(5).label 		= weakref.proxy( effectsGrid.effect6Button.label )
		self._findButtonInfo(6).component 	= weakref.proxy( effectsGrid.effect7Button.box )
		self._findButtonInfo(6).label 		= weakref.proxy( effectsGrid.effect7Button.label )
		self._findButtonInfo(7).component	= weakref.proxy( effectsGrid.effect8Button.box )
		self._findButtonInfo(7).label 		= weakref.proxy( effectsGrid.effect8Button.label )

		self.updateButtonEnableStates()
		self._setupTooltips()


	def _onSelectQualityOption( self, idx ):
		# Reset page
		self.setPage( self._page )
		self._updateSliders()


	def updateButtonEnableStates( self ):
		for i in xrange( 0, PostProcessingWindow.BUTTONS_PER_PAGE ):
			info = self._findButtonInfo(i)
			buttonScript = info.component.script
			if info.preset == DUMMY_BUTTON_PRESET:
				buttonScript.setDisabledState( True )
			elif info.preset == OFF_BUTTON_PRESET:
				buttonScript.setDisabledState( False )
			elif info.preset == NEXT_BUTTON_PRESET:
				buttonScript.setDisabledState( False )
			elif info.preset == PREVIOUS_BUTTON_PRESET:
				buttonScript.setDisabledState( False )
			else:
				buttonScript.setDisabledState( not info.isSupported() )


	def _setupTooltips( self ):
		for i in xrange( 0, PostProcessingWindow.BUTTONS_PER_PAGE ):
			button = self._findButtonInfo(i)
			
			buttonScript = button.component.script
			if buttonScript.buttonDisabled:
				toolTipText = "Not supported by hardware"
			else:
				toolTipText = button.tooltip
				if not ( (button.preset == DUMMY_BUTTON_PRESET) or
						 (button.preset == NEXT_BUTTON_PRESET) or
						 (button.preset == PREVIOUS_BUTTON_PRESET) ):
					toolTipText += ", Alt+click for debug"
				
			toolTipInfo = ToolTipInfo( button.component, "tooltip1line", {'text':toolTipText, 'shortcut':''}  )
			button.component.script.setToolTipInfo( toolTipInfo )

			# Make dummy button invisible
			if button.preset == DUMMY_BUTTON_PRESET:
				button.label.text = ""
				button.component.visible = False
			# Make button visible
			else:
				button.label.text = button.name
				button.component.visible = True

	def onActive( self ):
		'''Called when this window appears.'''
		
		# Refresh page and enabled/disabled states
		self.setPage( self._page )
		self._updateSliders()


	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )
		
		
	def save(self, filename = "scripts/data/post_processing.xml" ):
		ds = ResMgr.openSection( filename, True )
		for (key,s) in PostProcessingWindow.sliders.items():
			#print key, s.getFn
			ds.writeFloat(key, s.prop.get())
		ds.save()


	def load(self, filename = "scripts/data/post_processing.xml", speed = 0.5 ):
		ds = ResMgr.openSection( filename, False )
		if ds is not None:
			for (key,s) in PostProcessingWindow.sliders.items():
				s.prop.set( ds.readFloat(key), speed )


	@PyGUIEvent( "effectsGrid.effect1Button.box", "onActivate", True, 0 )
	@PyGUIEvent( "effectsGrid.effect1Button.box", "onDeactivate", False, 0 )
	@PyGUIEvent( "effectsGrid.effect2Button.box", "onActivate", True, 1 )
	@PyGUIEvent( "effectsGrid.effect2Button.box", "onDeactivate", False, 1 )
	@PyGUIEvent( "effectsGrid.effect3Button.box", "onActivate", True, 2 )
	@PyGUIEvent( "effectsGrid.effect3Button.box", "onDeactivate", False, 2 )
	@PyGUIEvent( "effectsGrid.effect4Button.box", "onActivate", True, 3 )
	@PyGUIEvent( "effectsGrid.effect4Button.box", "onDeactivate", False, 3 )
	@PyGUIEvent( "effectsGrid.effect5Button.box", "onActivate", True, 4 )
	@PyGUIEvent( "effectsGrid.effect5Button.box", "onDeactivate", False, 4 )
	@PyGUIEvent( "effectsGrid.effect6Button.box", "onActivate", True, 5 )
	@PyGUIEvent( "effectsGrid.effect6Button.box", "onDeactivate", False, 5 )
	@PyGUIEvent( "effectsGrid.effect7Button.box", "onActivate", True, 6 )
	@PyGUIEvent( "effectsGrid.effect7Button.box", "onDeactivate", False, 6 )
	@PyGUIEvent( "effectsGrid.effect8Button.box", "onActivate", True, 7 )
	@PyGUIEvent( "effectsGrid.effect8Button.box", "onDeactivate", False, 7 )
	def onEffectButton( self, on, idx ):	
		# This will turn off file access warnings while we switch effects...
		currentWDE = BigWorld.worldDrawEnabled()
		BigWorld.worldDrawEnabled( False )

		# Try to change pages
		try:
			# Alt + click -- show debug gui
			if BigWorld.isKeyDown( Keys.KEY_LALT ):
				# Create new debug gui
				if not self.dg:
					self.dg = PostProcessing.debugGui()
					self.dg.visible = True
				# Toggle debug gui visibility
				else:
					self.dg.visible = not self.dg.visible
			# Click -- activate button
			else:
				self._activateButton( on, idx )

		# Catch everything
		# Make sure world drawing is turned back on <- important
		except:
			ERROR_MSG( "Could not change pages" )
			traceback.print_exc()

		BigWorld.worldDrawEnabled( currentWDE )

	def _findButtonInfo( self, idx ):
		name = self.buttons[idx]
		for i in PostProcessingWindow.buttons:
			if name == i.name:
				return i
		raise IndexError( idx )
	
	
	def _activateButton( self, on, idx ):
		'''Activate the button given by the button at index idx.

		This function is called when a button is left clicked on/activated.

		Sets up the sliders to correspond to the appropriate
		information.  Also, if the button has an associated
		preset, set that on the post-processing chain.
		'''

		#print "_activateButton on ", on, " id ", idx

		# Only check button selection (not deselection)
		if not on:
			return

		buttonInfo = self._findButtonInfo(idx)

		# Load default "high", "medium" or "low" settings
		# Based on current graphics setting
		if buttonInfo.preset == DEFAULT_BUTTON_PRESET:
			# Set the chain
			INFO_MSG( "Loading default chain" )
			PostProcessing.defaultChain()

			# Set the sliders
			self._fillSliderInfo( idx )
			self._updateSliders()

		# Load default "high", "medium" or "low" settings
		# Plus weather effects
		# Based on current graphics setting
		elif buttonInfo.preset == DEFAULT_PLUS_BUTTON_PRESET:
			# Set the chain
			INFO_MSG( "Loading default chain plus weather" )
			PostProcessing.defaultChain()

			# Set the sliders
			self._fillSliderInfo( idx )
			self._updateSliders()

			# Add weather effects
			import Weather
			Weather.weather().loadEffects()

		# Remove chain
		elif buttonInfo.preset == OFF_BUTTON_PRESET:
			# Set the chain
			INFO_MSG( "Turning chain off" )
			PostProcessing.chain( None )

			# Set the sliders
			self._fillSliderInfo( idx )
			self._updateSliders()

		# Do nothing
		elif buttonInfo.preset == NEXT_BUTTON_PRESET:
			INFO_MSG( "Next" )
			self.setPage( self._page + 1 )

		# Do nothing
		elif buttonInfo.preset == PREVIOUS_BUTTON_PRESET:
			INFO_MSG( "Previous" )
			self.setPage( self._page - 1 )

		# Load whatever the button does
		elif buttonInfo.preset is not None:
			# Set the chain
			INFO_MSG( "Loading " + buttonInfo.preset )
			PostProcessing.RenderTargets.clearRenderTargets()
			PostProcessing.chain( PostProcessing.load(buttonInfo.preset) )

			# Set the sliders
			self._fillSliderInfo( idx )
			self._updateSliders()


	def _fillSliderInfo( self, idx ):
		'''Fill the self.sliderInfo list with the 3 sliders appropriate
		to the button given by the index parameter.'''
		buttonInfo = self._findButtonInfo(idx)
		self.sliderInfo = []
		for i in xrange( 0, PostProcessingWindow.SLIDERS_PER_PAGE ):
			sliderInfo = PostProcessingWindow.sliders[buttonInfo.sliderName[i]]
			self.sliderInfo.append( sliderInfo )


	def _updateSliders( self ):
		'''Update the slider area to represent the current state
		of the post-processing chain.'''
		c = self.component
		amounts = [c.slAmount1,c.slAmount2,c.slAmount3]
		labels = [c.slLabel1,c.slLabel2,c.slLabel3]
		sliders = [c.slider1,c.slider2,c.slider3]
		for i in xrange( 0, PostProcessingWindow.SLIDERS_PER_PAGE ):
			self.sliderInfo[i].apply( sliders[i], labels[i], amounts[i] )


	@PyGUIEvent( "slider1", "onValueChanged", 0 )
	@PyGUIEvent( "slider2", "onValueChanged", 1 )
	@PyGUIEvent( "slider3", "onValueChanged", 2 )
	def onSlider( self, idx, value ):
		c = self.component
		amounts = [c.slAmount1,c.slAmount2,c.slAmount3]
		try:
			self.sliderInfo[idx].updateAmountLabel(amounts[idx])
			self.sliderInfo[idx].prop.set(value,0.01)
		except NameError:
			pass


	def active( self, show ):
		if self.isActive == show:
			return

		PyGUI.DraggableWindow.active( self, show )
		Cursor.showCursor( show )

		if show:
			self.onActive()


	def onBound( self ):
		"""
		Create the window.

		Note: this gets called before PostProcessing.__init__().
		So setting the enabled/disabled states of the buttons here is useless.
		"""
		PyGUI.DraggableWindow.onBound( self )

		# Need to set page, but enabled/disabled buttons won't be correct
		# until after PostProcessing.__init__()
		self.setPage( 0 )

		self._fillSliderInfo( 0 )
		self._updateSliders()

		effectsGrid = self.component.effectsGrid
		effectsGrid.script.doLayout()
