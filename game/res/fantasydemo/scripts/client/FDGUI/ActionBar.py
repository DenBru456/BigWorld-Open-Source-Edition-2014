import BigWorld
import Helpers.PyGUI as PyGUI

import FDGUI
import FantasyDemo

from Helpers.PyGUI import PyGUIEvent
from Helpers.PyGUI.ToolTip import ToolTipInfo

from Helpers import BWKeyBindings
from Helpers.BWKeyBindings import BWKeyBindingAction

from functools import partial
from bwdebug import *

def setWireFrameMode( terrain, object ):

	mode = {
		(False, False): 0,
		(False, True): 1,
		(True, False): 2,
		(True, True): 3	} [ (object, terrain) ]

	BigWorld.setWatcher( "Render/Wireframe Mode", mode )


def getWireFrameModes():
	currentMode = int( BigWorld.getWatcher( "Render/Wireframe Mode" ) ) % 4
	terrain = (currentMode == 1 or currentMode == 3)
	object  = (currentMode == 2 or currentMode == 3)
	return terrain, object


def toggleTerrainWireframe():
	terrain, object = getWireFrameModes()
	setWireFrameMode( not terrain, object )
	return not terrain


def toggleObjectWireframe():
	terrain, object = getWireFrameModes()
	setWireFrameMode( terrain, not object )
	return not object


def toggleConsoleState( name ):
	newState = not (BigWorld.getWatcher( "Debug/activeConsole" ) == name)
	BigWorld.setWatcher( "Debug/activeConsole", name if newState else "")
	return newState


def toggleWatcher( name ):
	curState = BigWorld.getWatcher( name )
	newState = not (curState.upper() == 'TRUE')
	BigWorld.setWatcher( name, newState )
	return newState



class ActionBar( PyGUI.Window, BWKeyBindings.BWActionHandler ):

	factoryString = "FDGUI.ActionBar"

	def __init__( self, component ):
		PyGUI.Window.__init__( self, component )
		BWKeyBindings.BWActionHandler.__init__( self )
		self.component.script = self
		self.monitoredConsoles = {}
		self.__maxFlightPathWaitTime = 300	# Time in seconds. 5 minutes should be enough time.
		self.__avatarInitTime = 0
		
	def onBound( self ):
		PyGUI.Window.onBound( self )

		fdgui = FantasyDemo.rds.fdgui

		# Check that the attributes exist in case we couldn't load one
		if hasattr(fdgui, "inGameMenu"):
			fdgui.inGameMenu.script.addListener( "activated", self.inGameMenuActivated )

		if hasattr(fdgui, "environmentWindow"):
			fdgui.environmentWindow.script.addListener( "activated", self.environmentWindowActivated )

		if hasattr(fdgui, "statsWindow"):
			fdgui.statsWindow.script.addListener( "activated", self.networkStatsActivated )

		if hasattr(fdgui, "jobSystemWindow"):
			fdgui.jobSystemWindow.script.addListener( "activated", self.jobSystemWindowActivated )

		if hasattr(fdgui, "inventoryWindow"):
			fdgui.inventoryWindow.script.addListener( "activated", self.inventoryWindowActivated )

		if hasattr(fdgui, "helpWindow"):
			fdgui.helpWindow.script.addListener( "activated", self.helpWindowActivated )

		if hasattr(fdgui, "chatWindow"):
			fdgui.chatWindow.script.addListener( "visibilityChanged", self.chatWindowVisibilityChanged )

		if hasattr(fdgui, "webWindow"):
			fdgui.webWindow.script.addListener( "activated", self.webWindowActivated )

		if hasattr(fdgui, "postProcessingWindow"):
			fdgui.postProcessingWindow.script.addListener( "activated", self.postProcessingWindowActivated )
		
		FantasyDemo.rds.addListener( "flyThroughModeActivated", self.flyThroughModeActivated )

		self.getButton( "umbra" ).setToggleState( BigWorld.getWatcher( "Render/Umbra/enabled" ) )

		self.monitorConsoleState( "Python", "python" )
		self.monitorConsoleState( "Watcher", "watcher" )
		self.monitorConsoleState( "Statistics", "fps" )
		self.monitorConsoleState( "Histogram", "histogram" )

		toolTipManager = fdgui.toolTipManager
		toolTipManager.setToolTipFromAction( self.getButton( "inventory" ), 'Inventory' )
		toolTipManager.setToolTipFromAction( self.getButton( "voip" ), 'VOIPWindow' )
		toolTipManager.setToolTipFromAction( self.getButton( "chat" ), 'ChatWindow' )
		toolTipManager.setToolTipFromAction( self.getButton( "environmentWindow" ), 'Environment' )
		toolTipManager.setToolTipFromAction( self.getButton( "help" ), 'Help' )
		toolTipManager.setToolTipFromAction( self.getButton( "networkStats" ), 'ClientServerStats' )
		toolTipManager.setToolTipFromAction( self.getButton( "jobSystem" ), 'JobSystem' )
		toolTipManager.setToolTipFromAction( self.getButton( "ingameMenu" ), 'EscapeKey' )
		toolTipManager.setToolTipFromAction( self.getButton( "web" ), 'Web' )
		toolTipManager.setToolTipFromAction( self.getButton( "postProcessingWindow" ), 'PostProcessing' )

		toolTipManager.setToolTipFromAction( self.getButton( "umbra" ), 'ToggleUmbra' )
		toolTipManager.setToolTipFromAction( self.getButton( "uiDisplay" ), 'HideGUI' )
		toolTipManager.setToolTipFromAction( self.getButton( "python" ), 'TogglePythonConsole' )
		toolTipManager.setToolTipFromAction( self.getButton( "watcher" ), 'ToggleWatcherConsole' )
		toolTipManager.setToolTipFromAction( self.getButton( "fps" ), 'ToggleStatsConsole' )
		toolTipManager.setToolTipFromAction( self.getButton( "terrainWireframe" ), 'ToggleTerrainWireframe' )
		toolTipManager.setToolTipFromAction( self.getButton( "objectWireframe" ), 'ToggleObjectWireframe' )
		toolTipManager.setToolTipFromAction( self.getButton( "histogram" ), 'ToggleHistogram' )
		toolTipManager.setToolTipFromAction( self.getButton( "cellBounds" ), 'CellBoundaryVisualisation' )
		toolTipManager.setToolTipFromAction( self.getButton( "flyThrough" ), 'ToggleFlyThroughMode' )

		# Tooltips can also be done manual, so in this code:
		#umbraButton = self.getButton( "umbra" )
		#toolTipInfo = ToolTipInfo( umbraButton.component, "tooltip3line",
		#	{'title':'Umbra', 'line1':'umbra is used', 'line2':'to make the game', 'line3':'FASTER!', 'shortcut': '!!'}  )
		#umbraButton.setToolTipInfo( toolTipInfo )


	def active( self, state ):
		if state == True:
			FantasyDemo.rds.keyBindings.addHandler( self )
		else:
			FantasyDemo.rds.keyBindings.removeHandler( self )
		PyGUI.Window.active( self, state )


	def avatarInit( self, avatar ):
		avatar.addListener( "cellBoundsEnabled", self.cellBoundsEnabled )
		self.__avatarInitTime = BigWorld.time()
		self._checkFlyThrough()
		
		
	def _checkFlyThrough( self ):
		if FantasyDemo.rds.getFlightPathStartNode() != None:
			#DEBUG_MSG( "Flight path has completed loading, enabling flyThrough button." )
			self.getButton( "flyThrough" ).setDisabledState( False )
		else:
			self.getButton( "flyThrough" ).setDisabledState( True )
			timeDiff = BigWorld.time() - self.__avatarInitTime
			if timeDiff < self.__maxFlightPathWaitTime:
				BigWorld.callback( 5, self._checkFlyThrough )
			else:
				#DEBUG_MSG( "Flight path failed to load within %s seconds." % 
				#			self.__maxFlightPathWaitTime )
				pass

	@PyGUIEvent( "inventoryButton", "onClick" )
	def inventoryButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'Inventory' )
		
	@PyGUIEvent( "postProcessingWindowButton", "onClick" )
	def postProcessingWindowButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'PostProcessing' )
		
	@PyGUIEvent( "voipButton", "onClick" )
	def voipButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'VOIPWindow' )
		
	@PyGUIEvent( "chatButton", "onClick" )
	def chatButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'ChatWindow' )


	@PyGUIEvent( "environmentWindowButton", "onClick" )
	def environmentMenuButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'Environment' )


	@PyGUIEvent( "networkStatsButton", "onClick" )
	def networkStatsButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'ClientServerStats' )


	@PyGUIEvent( "jobSystemButton", "onClick" )
	def jobSystemButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'JobSystem' )


	@PyGUIEvent( "helpButton", "onClick" )
	def helpButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'Help' )


	@PyGUIEvent( "ingameMenuButton", "onClick" )
	def inGameMenuButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'InGameMenu' )

	@PyGUIEvent( "webButton", "onClick" )
	def webButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'Web' )

	@BWKeyBindingAction( "ToggleUmbra" )
	@PyGUIEvent( "umbraButton", "onClick" )
	def umbraButtonClicked( self, isDown=True ):
		if isDown:
			newState = toggleWatcher( "Render/Umbra/enabled" )
			self.getButton( "umbra" ).setToggleState( newState )
			if newState:
				FantasyDemo.addChatMsg( -1, "Umbra code path is enabled" )
			else:
				FantasyDemo.addChatMsg( -1, "Umbra code path is disabled" )


	@PyGUIEvent( "uiDisplayButton", "onClick" )
	def uiDisplayButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'HideGUI' )


	@BWKeyBindingAction( "TogglePythonConsole" )
	@PyGUIEvent( "pythonButton", "onClick" )
	def pythonButtonClicked( self, isDown=True ):
		if isDown:
			newState = toggleConsoleState( "Python" )
			self.getButton( "python" ).setToggleState( newState )


	@BWKeyBindingAction( "ToggleWatcherConsole" )
	@PyGUIEvent( "watcherButton", "onClick" )
	def watcherButtonClicked( self, isDown=True ):
		if isDown:
			newState = toggleConsoleState( "Watcher" )
			self.getButton( "watcher" ).setToggleState( newState )


	@BWKeyBindingAction( "ToggleStatsConsole" )
	@PyGUIEvent( "fpsButton", "onClick" )
	def fpsButtonClicked( self, isDown=True ):
		if isDown:
			newState = toggleConsoleState( "Statistics" )
			self.getButton( "fps" ).setToggleState( newState )


	@BWKeyBindingAction( "ToggleHistogram" )
	@PyGUIEvent( "histogramButton", "onClick" )
	def histogramButtonClicked( self, isDown=True ):
		if isDown:
			newState = toggleConsoleState( "Histogram" )
			self.getButton( "histogram" ).setToggleState( newState )


	@BWKeyBindingAction( "ToggleTerrainWireframe" )
	@PyGUIEvent( "terrainWireframeButton", "onClick" )
	def terrainWireframeButtonClicked( self, isDown=True ):
		if isDown:
			newState = toggleTerrainWireframe()
			self.getButton( "terrainWireframe" ).setToggleState( newState )
			if newState:
				FantasyDemo.addChatMsg( -1, "Terrain wireframe mode enabled" )
			else:
				FantasyDemo.addChatMsg( -1, "Terrain wireframe mode disabled" )


	@BWKeyBindingAction( "ToggleObjectWireframe" )
	@PyGUIEvent( "objectWireframeButton", "onClick" )
	def objectWireframeButtonClicked( self, isDown=True ):
		if isDown:
			newState = toggleObjectWireframe()
			self.getButton( "objectWireframe" ).setToggleState( newState )
			if newState:
				FantasyDemo.addChatMsg( -1, "Object wireframe mode enabled" )
			else:
				FantasyDemo.addChatMsg( -1, "Object wireframe mode disabled" )


	@PyGUIEvent( "cellBoundsButton", "onClick" )
	def cellBoundsButtonClicked( self ):
		FantasyDemo.rds.keyBindings.callActionByName( 'CellBoundaryVisualisation' )


	@BWKeyBindingAction( "ToggleFlyThroughMode" )
	@PyGUIEvent( "flyThroughButton", "onClick" )
	def flyThroughButtonClicked( self, isDown=True ):
		if isDown:
			newState = FantasyDemo.rds.toggleFlyThroughMode()
			btn = self.getButton( "flyThrough" )
			btn.setToggleState( newState )
			if newState == True:
				btn.setDisabledState( False )

	#
	# Listener events
	def inGameMenuActivated( self, activated ):
		self.getButton( "ingameMenu" ).setToggleState( activated )
		
	def postProcessingWindowActivated( self, activated ):
		self.getButton( "postProcessingWindow" ).setToggleState( activated )

	def environmentWindowActivated( self, activated ):
		self.getButton( "environmentWindow" ).setToggleState( activated )

	def networkStatsActivated( self, activated ):
		self.getButton( "networkStats" ).setToggleState( activated )

	def jobSystemWindowActivated( self, activated ):
		self.getButton( "jobSystem" ).setToggleState( activated )

	def inventoryWindowActivated( self, activated ):
		self.getButton( "inventory" ).setToggleState( activated )

	def helpWindowActivated( self, activated ):
		self.getButton( "help" ).setToggleState( activated )

	def cellBoundsEnabled( self, activated ):
		self.getButton( "cellBounds" ).setToggleState( activated )

	def chatWindowVisibilityChanged( self, activated ):
		self.getButton( "chat" ).setToggleState( activated )

	def flyThroughModeActivated( self, activated, resultList ):
		self.getButton( "flyThrough" ).setToggleState( activated )
		if activated == FantasyDemo.rds.fdgui.visible:
			FantasyDemo.rds.keyBindings.callActionByName( 'HideGUI' )

	def webWindowActivated( self, activated ):
		self.getButton( "web" ).setToggleState( activated )

	#
	# Misc utility methods
	def getButton( self, name ):
		return getattr( self.component, name + "Button" ).script


	def monitorConsoleState( self, consoleName, buttonName ):
		self.monitoredConsoles[ consoleName ] = self.getButton( buttonName )

		if len(self.monitoredConsoles) == 1:
			BigWorld.callback( 0.25, self._checkConsoles )


	def _checkConsoles( self ):

		activeConsole = BigWorld.getWatcher( "Debug/activeConsole" )

		# Set the current button toggle states for all buttons that
		# manipulate the active console.
		for consoleName, button in self.monitoredConsoles.iteritems():
			button.setToggleState( consoleName == activeConsole )

		# Keep checking while we still have consoles
		if len(self.monitoredConsoles) > 0:
			BigWorld.callback( 0.25, self._checkConsoles )


