import BigWorld
import ResMgr
import FantasyDemo
from ActionBar import ActionBar
from CharStats import CharStats
from InGameMenu import InGameMenu
from InventoryWindow import InventoryWindow, InventorySlot, DraggedItem, ItemDropRegion
from AdvertisingScreen import AdvertisingScreen
from HelpWindow import HelpWindow
from StatsWindow import StatsWindow
from TraderWindow import TraderWindow
from FDToolTip import FDGUIOneLineToolTip
from FDToolTip import FDToolTipManager
from WeatherWindow import WeatherWindow
from PostProcessingWindow import PostProcessingWindow
from JobSystemWindow import JobSystemWindow
from WebWindow import WebWindow
from FriendsWindow import FriendsWindow
from HTMLChatWindow import HTMLChatWindow
from WebControlsWindow import WebControlsWindow
from WebGameControlsWindow import WebGameControlsWindow
from ReplayControls import ReplayControls

from MainMenu import MainMenu
from MainMenu.TextListPage import TextListWindow as MainMenuTextListWindow
from MainMenu.TextListPage import MenuItem as MainMenuItem
from MainMenu.TextListPage import SmoothMover as MainMenuSmoothMover
from MainMenu.TextListPage import BackButton as MainMenuBackButton
from MainMenu.TextInputPage import TextInputWindow as MainMenuTextInputWindow
from MainMenu.StatusWindow import StatusWindow as MainMenuStatusWindow

from Helpers import BWKeyBindings
from Helpers.BWKeyBindings import BWKeyBindingAction
import Minimap
from SmallMinimap import SmallMinimap
from LargeMinimap import LargeMinimap
from Minimap import MinimapWindow
from SystemConsole import SystemConsole
from ChatConsole import ChatConsole
from DSLR import DSLR
import weakref

import Helpers.PyGUI as PyGUI
import Helpers.Caps as Caps

import BigWorld
import GUI
import Cursor
import Info
import Cursor
from functools import partial
from bwdebug import ERROR_MSG, INFO_MSG, WARNING_MSG

import Scaleform
from ScaleformDemo import ScaleformDemo

import traceback


MINIMUM_RES = (1280, 1024)

# Defining the Z ordering for all the elements so they can be ordered properly.
# Rear to front:
Z_ORDER_DROP_REGION = 0.9
Z_ORDER_COMBAT_TARGET = 0.85
Z_ORDER_INTERACTION_ICON = 0.84
Z_ORDER_SMALLMINIMAP_MAP = 0.81
Z_ORDER_SMALLMINIMAP_FRAME = 0.8
Z_ORDER_OFFLINE_INDICATOR = 0.8
Z_ORDER_CHAR_STATS = 0.7
Z_ORDER_ACTION_BAR = 0.6
Z_ORDER_REAR_WINDOW = 0.5
Z_ORDER_WINDOW_LIMIT = 0.4
Z_ORDER_INFO = 0.3
Z_ORDER_LARGEMINIMAP_MAP = 0.21
Z_ORDER_LARGEMINIMAP_FRAME = 0.2
Z_ORDER_INGAME_MENU = 0.1
Z_ORDER_BINOCULARS = 0.09
Z_ORDER_CHAT_BACKGROUND = 0.06
Z_ORDER_CHAT_CONSOLE = 0.05
Z_ORDER_TOOLTIP = 0.03

TEXT_COLOUR = 0
TEXT_COLOUR_OTHER_WISHPER = 1
TEXT_COLOUR_OTHER_SAY = 2
TEXT_COLOUR_SYSTEM = 3
TEXT_COLOUR_YOU_SAY = 4
TEXT_COLOUR_ONLINE = 5
TEXT_COLOUR_OFFLINE = 6

IS_HUD = 0
IS_WINDOW = 1
IS_NON_WINDOW = 2
IS_SPECIAL = 3
INITIALLY_VISIBLE = True
INITIALLY_INVISIBLE = False

NO_PIXEL_SNAP = False
PIXEL_SNAP = True

FDGUI_COMPONENTS = [
	("inGameMenu", 		"gui/ingame_menu.gui",		INITIALLY_INVISIBLE,	IS_NON_WINDOW,	Z_ORDER_INGAME_MENU),
	("environmentWindow", 	"gui/weather_window.gui",	INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW),
	("statsWindow", 	"gui/stats_window.gui", 	INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW),
	("helpWindow", 		"gui/help_window.gui", 		INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW),
	("inventoryWindow", "gui/inventory_window.gui",	INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW),
	("traderWindow", 	"gui/trader_window.gui",	INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW),
	("chatWindow",		"gui/chat_window.gui",		INITIALLY_INVISIBLE,	IS_NON_WINDOW,	Z_ORDER_CHAT_BACKGROUND),
	("webWindow", 	"gui/web.gui",		INITIALLY_INVISIBLE,		IS_WINDOW,	Z_ORDER_REAR_WINDOW),
	("friendsWindow", 	"gui/friends_window.gui",		INITIALLY_INVISIBLE,		IS_WINDOW,	Z_ORDER_REAR_WINDOW),
	("htmlChatWindow", 	"gui/html_chat_window.gui",		INITIALLY_INVISIBLE,		IS_WINDOW,	Z_ORDER_REAR_WINDOW),
	("webControls", 	"gui/web_controls.gui",		INITIALLY_INVISIBLE,		IS_WINDOW,	Z_ORDER_REAR_WINDOW),
	("webGameControls", 	"gui/web_game_controls.gui",		INITIALLY_INVISIBLE,		IS_WINDOW,	Z_ORDER_REAR_WINDOW),
	("charStats", 		"gui/char_stats.gui",		INITIALLY_VISIBLE,		IS_NON_WINDOW,	Z_ORDER_CHAR_STATS),
	("minimap", 		"gui/minimap.gui",			INITIALLY_VISIBLE,		IS_NON_WINDOW,	Z_ORDER_SMALLMINIMAP_MAP),
	("offlineIndicator","gui/offline_indicator.gui",INITIALLY_VISIBLE,		IS_NON_WINDOW,	Z_ORDER_OFFLINE_INDICATOR),
	("gammaGui", 		"gui/gamma.gui",			INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW),
	("targetGui", 		"gui/target.gui",			INITIALLY_VISIBLE,		IS_HUD,			Z_ORDER_COMBAT_TARGET),
	("binocularGui", 	"gui/binocular.gui",		INITIALLY_INVISIBLE,	IS_SPECIAL,		Z_ORDER_BINOCULARS),
	("postProcessingWindow", 	"gui/post_processing_window.gui",		INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW),
	("jobSystemWindow",	"gui/job_system_window.gui", 	INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW),	
	("infoBox", "gui/info.gui", INITIALLY_INVISIBLE, IS_NON_WINDOW, Z_ORDER_INFO),
	("actionBar", 		"gui/action_bar.gui",		INITIALLY_VISIBLE,		IS_NON_WINDOW,	Z_ORDER_ACTION_BAR),
	("replayWindow",	"gui/replay_controls.gui", 	INITIALLY_INVISIBLE,	IS_WINDOW,		Z_ORDER_REAR_WINDOW)
]

TARGET_GUI_STYLE2_DS = ResMgr.openSection( "gui/target_style2.gui" )
USE_TARGET_GUI_STYLE2 = False


class ResBracket(object):
	def __init__( self, **kwargs ):
		self.override = kwargs.get( "override", None )
		self.exact = kwargs.get( "exact", None )
		self.min = kwargs.get( "min", (0,0) )
		self.max = kwargs.get( "max", (99999,99999) )
		self.fontAliases = kwargs.get( "fontAliases", {} )
		self.fontAliasesFSC = kwargs.get( "fontAliasesFSC", self.fontAliases )

	def __str__( self ):
		if self.exact is not None:
			return "ResBracket: exact %s%s" % (str(self.exact), " (Has Override)" if self.override is not None else "")
		else:
			return "ResBracket: min %s, max %s%s" % (self.min, self.max, " (Has Override)" if self.override is not None else "")

	def matches( self, width, height, fullscreen ):
		#print "testing match", width, height, fullscreen, self.exact, self.min, self.max
		if self.exact is not None:
			return self.exact[0] == width and self.exact[1] == height

		elif   height >= width and width >= self.min[0] and width < self.max[0] or \
			   width > height and height >= self.min[1] and height < self.max[1]:
			return True

		return False

	def getFontAliases( self ):
		return self.fontAliasesFSC if self.fullScreenCompensated else self.fontAliases

	def applyResolutionOverride( self, resolutionOverrideHandlers ):
		fullscreen = not BigWorld.isVideoWindowed()
		fsAspect = BigWorld.getFullScreenAspectRatio()
		actualAspect = BigWorld.screenWidth()/BigWorld.screenHeight()
		resolutionOverride = self.override

		self.fullScreenCompensated = False

		if fullscreen:
			# We're in fullscreen mode. If the full screen aspect differs from the actual aspect, then
			# setup a resolution override that adjusts for this discrepancy.
			if abs(actualAspect - fsAspect) > 0.0001:
				#WARNING_MSG( "Adjusting full screen UI due to difference between actual aspect and fullscreen aspect." )
				if resolutionOverride is not None:
					height = resolutionOverride[1]
				else:
					height = BigWorld.screenHeight()
				resolutionOverride = (height*fsAspect, height)
				self.fullScreenCompensated = True
			elif resolutionOverride is not None:
				# If we're at the correct fullscreen aspect ratio for this resolution, but we have a resolution
				# override which is wrong for this resolution, then adjust.
				overrideAspect = float(resolutionOverride[0])/float(resolutionOverride[1])
				if abs(overrideAspect - actualAspect) > 0.0001:
					#WARNING_MSG( "Adjusting fullscreen resolution %s for different aspects (%f, %f)." %
					#			(repr(resolutionOverride), actualAspect, overrideAspect) )

					if BigWorld.screenWidth() > BigWorld.screenHeight():
						resolutionOverride = (resolutionOverride[1]*actualAspect, resolutionOverride[1])
					else:
						resolutionOverride = (resolutionOverride[0], resolutionOverride[0]/actualAspect)
					self.fullScreenCompensated = True

		else:
			# We're in windowed mode. If there is a resolution override, and we have been scaled into
			# a different aspect ratio than the override, adjust the override so we don't get
			# a squished UI (we don't do anything if there isnt an override because we'd be at
			# 1-1 pixel mapping anyway).
			if resolutionOverride is not None:
				overrideAspect = float(resolutionOverride[0])/float(resolutionOverride[1])
				if abs(actualAspect - overrideAspect) > 0.0001:
					#WARNING_MSG( "Adjusting windowed resolution override %s for different aspects (%f, %f)." %
					#			(repr(resolutionOverride), actualAspect, overrideAspect) )

					if BigWorld.screenWidth() > BigWorld.screenHeight():
						resolutionOverride = (resolutionOverride[1]*actualAspect, resolutionOverride[1])
					else:
						resolutionOverride = (resolutionOverride[0], resolutionOverride[0]/actualAspect)

		if resolutionOverride is not None:
			GUI.setResolutionOverride( resolutionOverride )
		else:
			GUI.setResolutionOverride( (0,0) )

		for handler in resolutionOverrideHandlers:
			handler.updateResolutionOverride()

FONT_ALIASES_TINY = {
	'Label.font': 	'Label_tiny.font',
	'Heading.font': 'Heading_tiny.font',
	'verdana_medium.font': 'verdana_small.font',
}

FONT_ALIASES_TINY_FSC = {
	'Label.font': 	'Label_tiny.font',
	'Heading.font': 'Heading_tiny.font',
	'verdana_medium.font': 'verdana_small.font',
}

FONT_ALIASES_SMALL = {
	'Label.font': 	'Label_small.font',
	'Heading.font': 'Heading_small.font',
	'verdana_medium.font': 'verdana_medium.font',
}

FONT_ALIASES_SMALL_FSC = {
	'Label.font': 	'Label_tiny.font',
	'Heading.font': 'Heading_tiny.font',
	'verdana_medium.font': 'verdana_medium.font',
}

FONT_ALIASES_MEDIUM = {
	'Label.font': 	'Label_medium.font',
	'Heading.font': 'Heading_medium.font',
	'verdana_medium.font': 'verdana_medium.font',
}

FONT_ALIASES_MEDIUM_FSC = {
	'Label.font': 	'Label_small.font',
	'Heading.font': 'Heading_small.font',
	'verdana_medium.font': 'verdana_medium.font',
}

FONT_ALIASES_LARGE = {
	'Label.font': 	'Label.font',
	'Heading.font': 'Heading.font',
	'verdana_medium.font': 'verdana_medium.font',
}

FONT_ALIASES_LARGE_FSC = {
	'Label.font': 	'Label_small.font',
	'Heading.font': 'Heading_small.font',
	'verdana_medium.font': 'verdana_medium.font',
}

RESOLUTION_BRACKETS_OTHER = (

	# Anything <= 1280, 1024 we should start scaling.
	# Define two blocks so we can switch in different fonts.
	ResBracket( min=(0,0), max=(640,480),
				override=(1280,1024),
				fontAliases=FONT_ALIASES_TINY ),

	ResBracket( min=(640,480), max=(1024,768),
				override=(1280,1024),
				fontAliases=FONT_ALIASES_SMALL ),

	ResBracket( min=(1024,768), max=(1280,1024),
				override=(1280,1024),
				fontAliases=FONT_ALIASES_MEDIUM ),


	# This bracket will be the final choice if nothing else got picked.
	# Just map it 1:1.
	ResBracket()
)

RESOLUTION_BRACKETS_4_3 = (

	# Common 4:3 resolutions that require scaling.
	ResBracket( exact=(640,480),
				override=(1408, 1056),
				fontAliases=FONT_ALIASES_TINY,
				fontAliasesFSC=FONT_ALIASES_TINY_FSC ),

	ResBracket( exact=(800,600),
				override=(1320, 990),
				fontAliases=FONT_ALIASES_SMALL,
				fontAliasesFSC=FONT_ALIASES_SMALL_FSC ),

	ResBracket( exact=(1024, 768),
				override=(1024*1.25, 768*1.25),
				fontAliases=FONT_ALIASES_MEDIUM,
				fontAliasesFSC=FONT_ALIASES_MEDIUM_FSC ),

	ResBracket( exact=(1152, 864),
				override=(1408, 1056),
				fontAliases=FONT_ALIASES_MEDIUM,
				fontAliasesFSC=FONT_ALIASES_MEDIUM_FSC ),

	ResBracket( exact=(1280, 960),
				override=(1408, 1056),
				fontAliasesFSC=FONT_ALIASES_LARGE_FSC ),

	# Catch-all bracket for small resolutions
	ResBracket( min=(0,0), max=(640, 480),
				override=(1408, 1056),
				fontAliases=FONT_ALIASES_TINY ),

	ResBracket( min=(640,480), max=(1024, 768),
				override=(1408, 1056),
				fontAliases=FONT_ALIASES_SMALL ),

	ResBracket( min=(1024,768), max=(1152, 864),
				override=(1408, 1056),
				fontAliases=FONT_ALIASES_MEDIUM ),

	# Everything else just match 1:1
	ResBracket(),
)

RESOLUTION_BRACKETS_5_4 = (
	ResBracket( exact=(720, 576),
				override=(1332, 1065.6),
				fontAliases=FONT_ALIASES_TINY ),

	ResBracket( exact=(1280, 1024),
				fontAliasesFSC=FONT_ALIASES_LARGE_FSC ),

	# Fallback to these if someone manages to pick this exact aspect
	RESOLUTION_BRACKETS_OTHER[0],
	RESOLUTION_BRACKETS_OTHER[1],
	RESOLUTION_BRACKETS_OTHER[2],

	# Everything else just match 1:1
	ResBracket(),
)

RESOLUTION_BRACKETS_9_6 = (
	ResBracket( exact=(720, 480),
				override=(1584, 1056),
				fontAliases=FONT_ALIASES_TINY ),

	# Fallback to these if someone manages to pick this exact aspect
	RESOLUTION_BRACKETS_OTHER[0],
	RESOLUTION_BRACKETS_OTHER[1],
	RESOLUTION_BRACKETS_OTHER[2],

	# Everything else just match 1:1
	ResBracket(),
)

RESOLUTION_BRACKETS_15_9 = (

	# Common 16:9 resolutions that require scaling.
	ResBracket( exact=(1280, 768),
				override=(1280*1.35, 768*1.35),
				fontAliases=FONT_ALIASES_SMALL ),

	# Fallback to these if someone manages to pick this exact aspect
	RESOLUTION_BRACKETS_OTHER[0],
	RESOLUTION_BRACKETS_OTHER[1],
	RESOLUTION_BRACKETS_OTHER[2],

	# Everything else just match 1:1
	ResBracket(),
)

RESOLUTION_BRACKETS_16_9 = (

	# Common 16:9 resolutions that require scaling.
	ResBracket( exact=(1280, 720),
				override=(1728, 972),
				fontAliases=FONT_ALIASES_SMALL ),

	ResBracket( exact=(1600, 900),
				override=(1840, 1035),
				fontAliases=FONT_ALIASES_SMALL ),

	ResBracket( min=(0,0), max=(1280, 720),
				override=(1728, 972),
				fontAliases=FONT_ALIASES_SMALL ),

	ResBracket( min=(1280,720), max=(1600, 900),
				override=(1840, 1035),
				fontAliases=FONT_ALIASES_SMALL ),

	# Fallback to these if someone manages to pick this exact aspect
	RESOLUTION_BRACKETS_OTHER[0],
	RESOLUTION_BRACKETS_OTHER[1],
	RESOLUTION_BRACKETS_OTHER[2],

	# Everything else just match 1:1
	ResBracket(),
)

RESOLUTION_BRACKETS_16_10 = (

	# Common 16:10 resolutions that require scaling.
	ResBracket( exact=(960, 600),
				override=(1600, 1000),
				fontAliases=FONT_ALIASES_MEDIUM,
				fontAliasesFSC=FONT_ALIASES_MEDIUM_FSC ),

	ResBracket( exact=(1440, 900),
				override=(1600, 1000),
				fontAliases=FONT_ALIASES_MEDIUM ),

	ResBracket( min=(0,0), max=(1440, 900),
				override=(1600, 1000),
				fontAliases=FONT_ALIASES_MEDIUM ),

	# Fallback to these if someone manages to pick this exact aspect
	RESOLUTION_BRACKETS_OTHER[0],
	RESOLUTION_BRACKETS_OTHER[1],
	RESOLUTION_BRACKETS_OTHER[2],

	# Everything else just match 1:1
	ResBracket(),
)

RESOLUTION_BRACKETS_53_30 = (
	ResBracket( exact=(848, 480),
				override=(1781, 1008),
				fontAliases=FONT_ALIASES_SMALL,
				fontAliasesFSC=FONT_ALIASES_SMALL_FSC ),

	# Fallback to these if someone manages to pick this exact aspect
	RESOLUTION_BRACKETS_OTHER[0],
	RESOLUTION_BRACKETS_OTHER[1],
	RESOLUTION_BRACKETS_OTHER[2],

	# Everything else just match 1:1
	ResBracket(),
)

RESOLUTION_BRACKETS = (
	( (4,3),   RESOLUTION_BRACKETS_4_3   ),
	( (5,4),   RESOLUTION_BRACKETS_5_4   ),
	( (9,6),   RESOLUTION_BRACKETS_9_6   ),
	( (15,9),  RESOLUTION_BRACKETS_15_9  ),
	( (16,9),  RESOLUTION_BRACKETS_16_9  ),
	( (16,10), RESOLUTION_BRACKETS_16_10 ),
	( (53,30), RESOLUTION_BRACKETS_53_30 ),
	( None,    RESOLUTION_BRACKETS_OTHER ),
)

def _pickResolutionBracket():

	screenWidth, screenHeight = BigWorld.screenSize()

	fullscreen = not BigWorld.isVideoWindowed()
	fsAspect = BigWorld.getFullScreenAspectRatio()
	actualAspect = float(screenWidth)/float(screenHeight)

	#print "_pickResolutionBracket", screenWidth, screenHeight, fullscreen, fsAspect, actualAspect

	# Find the most appropriate bracket for the current settings.
	for aspect, bracketList in RESOLUTION_BRACKETS:
		if aspect is not None:
			bracketAspect = float(aspect[0])/float(aspect[1])
		else:
			#WARNING_MSG( "Failed to match aspect ratio %f to a bracket list, falling back to 'OTHER'." % (actualAspect,) )
			bracketAspect = actualAspect

		if abs(actualAspect-bracketAspect) < 0.01:
			for bracket in bracketList:
				if bracket.matches( screenWidth, screenHeight, fullscreen ):
					#INFO_MSG( 'Using resolution bracket %s (from aspect list %s).' % (bracket, aspect) )
					return bracket

	return None


class FDGUI( BWKeyBindings.BWActionHandler ):

	def __init__( self ):
		BWKeyBindings.BWActionHandler.__init__( self )

		self.windows = dict()
		self.openWindowsOrder = []
		self._root = None
		self.filterConvertedComponents = []
		self.aliasedFontComponents = []
		self.bracket = None
		#list of handlers to get a callback when resolution override is set
		self.resolutionOverrideHandlers = []
		self.componentNames = []

		PyGUI.IME.init()


	def setupGUI( self, actionToolTipsSection, keyBindings ):
		# All FDGUI elements are children of an invisible simple GUI component.
		# This allows us to easily toggle visibility of the HUD, as well as
		# control the overall sorted Z position of the hud relative to non-HUD
		# components.
		self._root = GUI.Simple("")
		self._root.script = PyGUI.PyGUIBase( self._root )
		self._root.size = (2,2)
		self._root.visible = False
		GUI.addRoot( self._root )
		self._root.visible = False

		self.toolTipManager = FDToolTipManager( self._root, Z_ORDER_TOOLTIP )
		self.toolTipManager.readInActionToolTips( actionToolTipsSection )
		self.toolTipManager.addKeyboardShortcutsToActionToolTips( keyBindings )

		for name, filename, initiallyVisible, hudType, zorder in FDGUI_COMPONENTS:

			try:
				component = GUI.load( filename )
				if not component:
					ERROR_MSG( "Error loading FDGUI component '%s' from '%s'" %
						(name, filename) )
					continue

				self.componentNames.append( name )
				setattr( self, name, component )
				component.position.z = zorder
				if component.script:
					if hudType == IS_WINDOW:
						self.setupWindowListeners( component )
					if hudType != IS_SPECIAL:
						component.script.parent = self._root
				if initiallyVisible:
					component.script.active( True )
					#self._root.addChild( component, name )
				if hudType == IS_WINDOW:
					self.windows[ name ] = component
			except:
				ERROR_MSG( "Exception while loading FDGUI component '%s':" %
					(name) )
				print traceback.format_exc()

		self.webWindow.script.setEditEventHandler()
		self.webWindow.script.addObserver()
		self.webControls.script.addObserver()
		self.webControls.script.setEditEventHandler()

		self.friendsWindow.script.init()
		self.htmlChatWindow.script.init()

		self.dropRegion = GUI.load( "gui/item_drop_region.gui" )
		self.dropRegion.position.z = Z_ORDER_DROP_REGION
		self.dropRegion.script.parent = self._root
		self.dropRegion.script.active( True )

		self.interactionGui = GUI.Simple( "" )
		self.interactionGui.width = 0 # to stop it displaying wierd textures
		self.interactionGui.position.z = Z_ORDER_INTERACTION_ICON
		self._root.interactionGui = self.interactionGui

		self.scaleformDemo = None

		FantasyDemo.rds.keyBindings.addHandler( self )
		FantasyDemo.addDeviceListener( self )

	def fini( self ):

		self.filterConvertedComponents = None

		self.chatWindow.script.fini()
		self.inGameMenu = None
		for window in self.windows.values():
			window.script.active( False )
		self.windows = None
		self.dropRegion.script.active( False )
		self.dropRegion = None
		FantasyDemo.rds.keyBindings.removeHandler( self )
		self.toolTipManager.fini()
		self.toolTipManager = None

		for compName in self.componentNames:
			delattr( self, compName )

		GUI.delRoot( self._root )
		self._root = None

		PyGUI.IME.fini()


	def onPlayerAvatarEnterWorld( self, avatar ):
		for c in [ x[1] for x in self._root.children ]:
			if hasattr( c.script, "avatarInit" ):
				c.script.avatarInit( avatar )

		self._root.visible = True
		self.offlineIndicator.visible = (BigWorld.server() == "")


	def onPlayerAvatarLeaveWorld( self, avatar ):
		if self._root is None:
			return

		for c in [ x[1] for x in self._root.children ]:
			if hasattr( c.script, "avatarFini" ):
				c.script.avatarFini( avatar )

		self._root.visible = False


	def setVisible( self, visible ):
		self._root.visible = visible
		Cursor.showCursor( visible )

	def getVisible( self ):
		return self._root.visible

	visible = property( getVisible, setVisible )


	def addChild( self, component ):
		if self._root is not None:
			self._root.addChild( component )

	def delChild( self, component ):
		if self._root is not None:
			self._root.delChild( component )

	def hasChild( self, component, deepSearch ):
		if self._root is None:
			return False
		else:
			return self._root.hasChild( component, deepSearch )


	def windowClicked( self, window ):
		if window in self.openWindowsOrder:
			self.bringWindowToFront( window )


	def windowActivated( self, window, activated ):
		if activated:
			if window not in self.openWindowsOrder:
				self.openWindowsOrder.append( window )
			self.bringWindowToFront( window )
		else:
			if window  in self.openWindowsOrder:
				self.openWindowsOrder.remove( window )


	def bringWindowToFront( self, window ):
		if window not in self.openWindowsOrder:
			ERROR_MSG( "Attempting to bring hidden window to front", window )
			return

		self.openWindowsOrder.remove( window )
		self.openWindowsOrder.append( window )

		zposition = Z_ORDER_REAR_WINDOW
		increment = (Z_ORDER_WINDOW_LIMIT - Z_ORDER_REAR_WINDOW) / len(self.openWindowsOrder)
		for window in self.openWindowsOrder:
			window.position.z = zposition
			zposition += increment

		self._root.reSort()


	def setupWindowListeners( self, window ):
		weak = weakref.proxy( window )
		window.script.addListener( "activated", partial( self.windowActivated, weak ) )
		window.script.addListener( "windowClicked", partial( self.windowClicked, weak ) )
		window.script.addListener( "onBeginDrag", partial( self.windowClicked, weak ) )


	def onRecreateDevice( self ):
		self.chooseResolutionBracket()


	def chooseResolutionBracket( self ):
		self.bracket = _pickResolutionBracket()
		assert self.bracket is not None

		self.bracket.applyResolutionOverride(self.resolutionOverrideHandlers)
		self.setupFilterTypes()
		self.setupFonts()
		self.chatWindow.script.onRecreateDevice()


	def setupFilterTypes( self ):

		# Restore original filter types
		for component in self.filterConvertedComponents:
			component[0].filterType = component[1]

		self.filterConvertedComponents = []

		self.setupFilterTypesInternal( self._root )
		self.setupFilterTypesInternal( self.minimap.m.script.smallMinimap )
		self.setupFilterTypesInternal( self.minimap.m.script.largeMinimap )
		for c in FDGUI_COMPONENTS:
			if hasattr( self, c[0] ):
				self.setupFilterTypesInternal( getattr( self, c[0] ) )


	def setupFilterTypesInternal( self, component ):
		ft = str(component.filterType)
		# Map any "POINT" filtered components to "LINEAR" if we have a res override
		if GUI.screenResolution() != BigWorld.screenSize():
			mappings = {'POINT':'LINEAR'}
		else:
			mappings = {}

		if type(component) is not GUI.Text and ft in mappings:
			component.filterType = mappings[ft]
			self.filterConvertedComponents.append( (component, ft) )

		for child in component.children:
			self.setupFilterTypesInternal( child[1] )


	def setupFonts( self ):

		# First restore to original fonts of any previously aliased components.
		for component in self.aliasedFontComponents:
			component[0].font = component[1]

		self.aliasedFontComponents = []

		# Set the pygui text styles
		fontAliases = self.bracket.getFontAliases()
		PyGUI.TextStyles.fontAliases = dict( [ (key, value) for (key, value) in fontAliases.iteritems() ] )

		# Go through and find text components
		self.setupFontsInternal( self._root )
		self.setupFontsInternal( self.minimap.m.script.smallMinimap )
		self.setupFontsInternal( self.minimap.m.script.largeMinimap )
		for c in FDGUI_COMPONENTS:
			if hasattr( self, c[0] ):
				self.setupFontsInternal( getattr( self, c[0] ) )

		# Go through tool tips and update
		for component in self.toolTipManager.toolTipGUIs.values():
			self.setupFontsInternal( component )


	def setupFontsInternal( self, component ):
		if self.bracket is None:
			return

		fontAliases = self.bracket.getFontAliases()

		if type(component) is GUI.Text:
			curFontName = str(component.font)
			if curFontName in fontAliases:
				alias = fontAliases[ curFontName ]
				component.font = alias

				# Remember this component so we can restore original font
				self.aliasedFontComponents.append( (component, curFontName) )


		for child in component.children:
			self.setupFontsInternal( child[1] )



	def _componentAdded( self, component ):
		self.setupFilterTypesInternal( component )
		self.setupFontsInternal( component )


	def isScaling( self ):
		return self.bracket is not None and self.bracket.has_key( 'resolutionOverride' )

	@BWKeyBindingAction( "Character" )
	def toggleCharacter( self, isDown=True ):
		pass


	@BWKeyBindingAction( "Equipment" )
	def toggleEquipment( self, isDown=True ):
		pass


	@BWKeyBindingAction( "Inventory" )
	def toggleInventory( self, isDown=True ):
		if isDown:
			self.inventoryWindow.script.toggleActive()


	@BWKeyBindingAction( "PostProcessing" )
	def togglePostProcessing( self, isDown=True ):
		if isDown:
			self.postProcessingWindow.script.toggleActive()


	@BWKeyBindingAction( "JobSystem" )
	def toggleJobSystemWindow( self, isDown=True ):
		if isDown:
			self.jobSystemWindow.script.toggleActive()


	@BWKeyBindingAction( "Environment" )
	def toggleEnvironment( self, isDown=True ):
		if isDown:
			self.environmentWindow.script.toggleActive()


	@BWKeyBindingAction( "Help" )
	def toggleHelp( self, isDown=True ):
		if isDown:
			self.helpWindow.script.toggleActive()


	@BWKeyBindingAction( "ClientServerStats" )
	def toggleClientServerStats( self, isDown=True ):
		if isDown:
			self.statsWindow.script.toggleActive()

	@BWKeyBindingAction( "InGameMenu" )
	def toggleInGameMenu( self, isDown=True ):
		if isDown:
			self.inGameMenu.script.toggleActive()

	@BWKeyBindingAction( "Web" )
	def toggleWeb( self, isDown=True ):
		if isDown:
			self.webWindow.script.toggleActive()

	@BWKeyBindingAction( "Friends" )
	def toggleFriends( self, isDown=True ):
		if isDown:
			self.friendsWindow.script.toggleActive()

	@BWKeyBindingAction( "ReplayControls" )
	def toggleReplayControls( self, isDown=True ):
		if isDown:
			self.replayWindow.script.toggleActive()

	@BWKeyBindingAction( "Chat" )
	def toggleChat( self, isDown=True ):
		if isDown:
			self.htmlChatWindow.script.toggleActive()

	def activateWebControls( self, state ):
		self.webControls.script.active(state)

	def activateWebGameControls( self, state ):
		self.webGameControls.script.active(state)

	@BWKeyBindingAction( "HideGUI" )
	def toggleHideGUI( self, isDown=True ):
		if isDown:
			if self.binocularGui.script.isActive:
				# When hiding the GUI for screen shots we don't want to hide the
				# binoculars gui, as that's what the screen shot would be of.
				# But hide (or show) the offline indication label anyway.
				self.offlineIndicator.visible = not self.offlineIndicator.visible

			elif self.visible:
				self.chatWindow.script.addMsg( 'Press Esc to show the GUI again.' , 3 )
				self.chatWindow.script.hideLater( 2 )
				self.visible = False
				Info.setVisibilityOfAllInfoEntities( False )
			else:
				self.visible = True
				Info.setVisibilityOfAllInfoEntities( True )


	@BWKeyBindingAction( "GammaGui" )
	def toggleGammaGui(self, isDown):
		if isDown:
			self.gammaGui.script.toggleActive()


	@BWKeyBindingAction( "Web" )
	def toggleWeb( self, isDown=True ):
		if isDown:
			self.webWindow.script.toggleActive()

	@BWKeyBindingAction( "EscapeKey" )
	def handleEscapeKey( self, isDown=True ):
		if not isDown:
			return False

		if self.scaleformDemo is not None:
			self.scaleformDemo.script.active( False )
			self.scaleformDemo = None
			self.visible = True
			return True

		if not self.visible:
			self.toggleHideGUI()
			return True

		# This closes all open windows before opening the in-game menu.
		#if self.inGameMenu.script.isActive:
		#	self.toggleInGameMenu()
		#elif not self.hideAllWindows():
		#	self.toggleInGameMenu()

		# This simply toggles the in-game menu without first closing windows.
		self.toggleInGameMenu()

		return True

	@BWKeyBindingAction( "ScaleformDemo" )
	def handleScaleformDemoKey( self, isDown ):
		if isDown:
			if not Scaleform.AVAILABLE:
				FantasyDemo.addMsg( "Scaleform not available in this build." )
				return

			nextIdx = 0
			if self.scaleformDemo is not None:
				oldMovieIdx = self.scaleformDemo.script.movieIdx
				self.scaleformDemo.script.active( False )
				nextIdx = (oldMovieIdx+1) % len(ScaleformDemo.MOVIES)

			self.scaleformDemo = ScaleformDemo.create( nextIdx )
			self.scaleformDemo.script.active( True )
			self.visible = False
			Cursor.showCursor( True )


	def showBinoculars( self, show ):
		self._root.visible = not show
		self.binocularGui.script.active( show )


	def targetFocus( self, entity ):

		healthBarVisible = Caps.CAP_CAN_HIT in entity.targetCaps

		overheadText = FantasyDemo.getEntityName( entity.id )

		if USE_TARGET_GUI_STYLE2:
			if getattr( entity, "targetGuiAttachment", None ) is not None:
				entity.model.root.detach( entity.targetGuiAttachment )
				entity.targetGuiAttachment = None

			c = GUI.load( TARGET_GUI_STYLE2_DS )
			c.health.visible = healthBarVisible
			c.health.position.y += entity.model.height

			nameComponent = c.name
			nameComponent.position.y += entity.model.height

			nameComponent.text = overheadText
			nameComponent.width = 0 # Setting this to zero with "explicitSize" maintains aspect

			entity.targetGuiAttachment = GUI.Attachment()
			entity.targetGuiAttachment.faceCamera = True
			entity.targetGuiAttachment.component = c
			entity.model.root.attach( entity.targetGuiAttachment )
		else:
			self.targetGui.healthBk.visible = healthBarVisible
			self.targetGui.health.visible = healthBarVisible

			nameComponent = self.targetGui.name
			nameComponent.text = overheadText
			self.targetGui.source = entity.model.bounds

		if hasattr( entity, "targettingColour" ):
			nameComponent.colour = entity.targettingColour
		else:
			nameComponent.colour = (255, 255, 255, 255)

		self.updateTargetHealth( instantly = True )


	def targetBlur( self, entity ):
		if USE_TARGET_GUI_STYLE2:
			if getattr( entity, "targetGuiAttachment", None ) is not None:
				entity.model.root.detach( entity.targetGuiAttachment )
				entity.targetGuiAttachment = None
		else:
			try:
				self.targetGui.source = None
			except AttributeError:
				#TODO : This happens if the player leaves the world and then targetBlur is called.
				#BigWorld should never call targetBlur if there is no player entity
				pass


	def updateTargetHealth( self, instantly = False ):
		entity = BigWorld.target()
		try:
			healthPercent = entity.healthPercent / 100.0
		except:
			healthPercent = 1.0

		if USE_TARGET_GUI_STYLE2:
			if getattr( entity, "targetGuiAttachment", None ) is None:
				return
			healthBar = entity.targetGuiAttachment.component.health
		else:
			healthBar = self.targetGui.health

		healthBar.clipper.value = healthPercent
		healthBar.colourer.value = healthPercent
		if instantly:
			healthBar.colourer.reset()
			healthBar.clipper.reset()

	def hideAllWindows( self ):

		# Note: this doesn't include the in-game menu
		windowsActive = False
		for windowComponent in self.windows.itervalues():
			if windowComponent.script.isActive:
				windowComponent.script.active( False )
				windowsActive = True

		return windowsActive


	def handleDisconnectionFromServer( self ):
		# Hide all in-game UI's that may be visible.
		self.inGameMenu.script.active( False )


	def addResolutionOverrideHandler( self, handler ):
		self.resolutionOverrideHandlers.append( weakref.proxy(handler) )


	def removeResolutionOverrideHandler( self, handler ):
		self.resolutionOverrideHandlers.remove( weakref.proxy(handler) )


