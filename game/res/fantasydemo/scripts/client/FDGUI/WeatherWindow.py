# -*- coding: utf-8 -*-

import BigWorld
import Helpers.PyGUI as PyGUI
from functools import partial
from bwdebug import ERROR_MSG
import types
import Cursor

from Helpers.PyGUI import PyGUIEvent
from FDToolTip import ToolTipInfo
import FantasyDemo

import weakref


class WeatherWindow( PyGUI.DraggableWindow ):

	factoryString = "FDGUI.WeatherWindow"

	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )
		self.timeCallback = None
		self.origTimeOfDay = "160" # The default in the C++ code
		self.weatherName = "Clear"
		self.weatherSystem = None
		self.weatherSystemName = None
		self.lastWindSpeed = 0.0


	def onActive( self ):
		self.onTimeOfDayUpdated()
		self.timeCallback = BigWorld.callback( 0.1 if self._isTimeAccelerated() else 1.0, self.timeOfDayCallback )

		if not hasattr( BigWorld, "getEnvironmentSync" ):
			self.component.environmentSyncCheckBox.script.buttonDisabled = True
			
		if self.weatherSystem == None and self.weatherSystemName == None:
			import Weather
			weather = Weather.weather()
			if weather.pendingWeatherChange:
				self.weatherSystemName = weather.pendingWeatherChange
			elif weather.system:
				self.weatherSystem = weather.system
			else:
				self.weatherSystemName = 'Clear'

		self._onWeatherUpdated()


	def avatarFini( self, avatar ):
		if self.timeCallback:
			BigWorld.cancelCallback( self.timeCallback )
			self.timeCallback = None


	def timeOfDayCallback( self ):
		if self.isActive:
			self.onTimeOfDayUpdated()
			self.timeCallback = BigWorld.callback( 0.1 if self._isTimeAccelerated() else 1.0, self.timeOfDayCallback )


	def _weather( self, system = None, systemName = None ):
		self.weatherSystem = system
		self.weatherSystemName = systemName
		self.lastWindSpeed = None
		self._onWeatherUpdated()


	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )


	def onTimeOfDayUpdated( self ):
		timeOfDayString = BigWorld.timeOfDay()
		if timeOfDayString == "":
			return

		self.component.timeOfDay.text = timeOfDayString
		hours, minutes = timeOfDayString.split(':')
		self.component.timeOfDaySlider.script.value = int(hours) + int(minutes) / 60.0

		self.component.accelerateTimeCheckBox.script.setToggleState( self._isTimeAccelerated() )


	def _isTimeAccelerated( self ):
		if BigWorld.server() is not None:
			secsPerHour = BigWorld.getWatcher( "Client Settings/Secs Per Hour" )
			if secsPerHour == None:
				secsPerHour = 1.0
			else:
				secsPerHour = int( secsPerHour )
			return secsPerHour < 50.0
		return False


	@PyGUIEvent( "timeOfDaySlider", "onValueChanged" )
	def onTimeOfDaySlider( self, value ):
		BigWorld.timeOfDay( str( value ) )
		self.component.timeOfDay.text = BigWorld.timeOfDay()


	@PyGUIEvent( "accelerateTimeCheckBox", "onActivate", True )
	@PyGUIEvent( "accelerateTimeCheckBox", "onDeactivate", False )
	def onAccelerateTimeCheckBox( self, on ):
		if on:
			self.origTimeOfDay = BigWorld.getWatcher( "Client Settings/Secs Per Hour" )
			BigWorld.setWatcher( "Client Settings/Secs Per Hour", 1.0 )
			if self.timeCallback:
				BigWorld.cancelCallback( self.timeCallback )
			self.timeOfDayCallback()
		else:
			BigWorld.setWatcher( "Client Settings/Secs Per Hour", self.origTimeOfDay )
			#BigWorld.setWatcher( "Client Settings/Time of Day", 15.0 )
		self.onTimeOfDayUpdated()


	def _onWeatherUpdated( self ):
		import Weather
		weather = Weather.weather()
		windSpeed = self.lastWindSpeed

		if self.weatherSystemName:
			weatherName = self.weatherSystemName
			system = weather.newSystemByName( weatherName )
		elif self.weatherSystem:
			system = self.weatherSystem
			weatherName = system.name

		if system:
			if windSpeed == None:
				windSpeed = system.windSpeed[0] + system.windSpeed[1]

		self.component.weatherName.text = weatherName
		if self.weatherButtons.has_key( weatherName ):
			self.weatherButtons[ weatherName ].script.setToggleState( True )
		else:
			button = self.weatherButtons.values()[0].script
			button.setToggleState( True )
			button.setToggleState( False )

		self.component.windSpeedSlider.script.value = windSpeed
		self.component.windSpeed.text = "%.1f m/s" % (windSpeed,)

		self.component.randomWeatherCheckBox.script.setToggleState( weather.isWeatherRandom() )
		self.component.environmentSyncCheckBox.script.setToggleState( \
			False if not hasattr( BigWorld, "getEnvironmentSync" ) else BigWorld.getEnvironmentSync() )


	@PyGUIEvent( "weatherGrid.clearWeatherButton", "onClick", "Clear" )
	@PyGUIEvent( "weatherGrid.cloudyWeatherButton", "onClick", "Cloudy" )
	@PyGUIEvent( "weatherGrid.cloudy2WeatherButton", "onClick", "Cloudy2" )
	@PyGUIEvent( "weatherGrid.cloudy3WeatherButton", "onClick", "Cloudy3" )
	@PyGUIEvent( "weatherGrid.stormyWeatherButton", "onClick", "Stormy" )
	@PyGUIEvent( "weatherGrid.rainyWeatherButton", "onClick", "Rainy" )
	@PyGUIEvent( "weatherGrid.hailWeatherButton", "onClick", "Hail" )
	@PyGUIEvent( "weatherGrid.dustStormWeatherButton", "onClick", "DustStorm" )
	@PyGUIEvent( "weatherGrid.snowWeatherButton", "onClick", "Snow" )
	@PyGUIEvent( "weatherGrid.blizzardWeatherButton", "onClick", "Blizzard" )
	@PyGUIEvent( "weatherGrid.fogWeatherButton", "onClick", "Fog" )
	@PyGUIEvent( "weatherGrid.peaSoupWeatherButton", "onClick", "PeaSoup" )
	def onWeatherButtonClick( self, weather ):
		import Weather
		Weather.weather().toggleRandomWeather( False )
		Weather.weather().summon( weather )
		self.component.weatherName.text = weather
		self.weatherName = weather
		self.lastWindSpeed = None


	@PyGUIEvent( "windSpeedSlider", "onValueChanged" )
	def onWindSpeedSlider( self, value ):
		self.lastWindSpeed = value
		if BigWorld.player() is not None:
			BigWorld.weather( BigWorld.player().spaceID ).windAverage( self.lastWindSpeed, 0.0 )
		else:
			BigWorld.weather( BigWorld.camera().spaceID ).windAverage( self.lastWindSpeed, 0.0 )
		self.component.windSpeed.text = "%.1f m/s" % (self.lastWindSpeed,)


	@PyGUIEvent( "randomWeatherCheckBox", "onActivate", True )
	@PyGUIEvent( "randomWeatherCheckBox", "onDeactivate", False )
	def onRandomWeatherCheckBox( self, on ):
		import Weather
		Weather.weather().toggleRandomWeather( on )


	@PyGUIEvent( "environmentSyncCheckBox", "onActivate", True )
	@PyGUIEvent( "environmentSyncCheckBox", "onDeactivate", False )
	def onEnvironmentSyncCheckBox( self, on ):
		if not hasattr( BigWorld, "setEnvironmentSync" ):
			return
		BigWorld.setEnvironmentSync( on )
		FantasyDemo.addChatMsg( -1, 'Environment Sync turned ' + ("off","on")[on] )


	def active( self, show ):
		if self.isActive == show:
			return

		import Weather
		if show:
			Weather.weather().addListener( "weather", self._weather )
		else:
			Weather.weather().removeListener( "weather", self._weather )
			self.weatherSystem = None
			self.weatherSystemName = None

		PyGUI.DraggableWindow.active( self, show )
		Cursor.showCursor( show )

		if show:
			self.onActive()


	def onBound( self ):
		PyGUI.DraggableWindow.onBound( self )

		weatherGrid = self.component.weatherGrid
		self.weatherButtons = {
			'Clear': weakref.proxy( weatherGrid.clearWeatherButton ),
			'Cloudy': weakref.proxy( weatherGrid.cloudyWeatherButton ),
			'Cloudy2': weakref.proxy( weatherGrid.cloudy2WeatherButton ),
			'Cloudy3': weakref.proxy( weatherGrid.cloudy3WeatherButton ),
			'Stormy': weakref.proxy( weatherGrid.stormyWeatherButton ),
			'Rainy': weakref.proxy( weatherGrid.rainyWeatherButton ),
			'Hail': weakref.proxy( weatherGrid.hailWeatherButton ),
			'DustStorm': weakref.proxy( weatherGrid.dustStormWeatherButton ),
			'Snow': weakref.proxy( weatherGrid.snowWeatherButton ),
			'Blizzard': weakref.proxy( weatherGrid.blizzardWeatherButton ),
			'Fog': weakref.proxy( weatherGrid.fogWeatherButton ),
			'PeaSoup': weakref.proxy( weatherGrid.peaSoupWeatherButton ),
		}

		for key, value in self.weatherButtons.iteritems():
			toolTipInfo = ToolTipInfo( value, "tooltip1line", {'text':key, 'shortcut':''}  )
			value.script.setToolTipInfo( toolTipInfo )

