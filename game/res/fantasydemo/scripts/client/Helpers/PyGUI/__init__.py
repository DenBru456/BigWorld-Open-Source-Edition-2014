from PyGUIBase import PyGUIBase
from PyGUIEvent import PyGUIEvent
from Button import Button, ButtonVisualState
from CheckBox import CheckBox
from RadioButton import RadioButton
from ScrollableText import ScrollableText
from EditField import EditField
from Grid import Grid
from Slider import Slider, SliderThumb, SliderVisualState
from ScrollingList import ScrollingList
from ScrollWindow import ScrollWindow
from SmoothMover import SmoothMover
from TextField import TextField
from ToolTip import ToolTip
from ToolTip import ToolTipInfo
from ToolTip import ToolTipManager
from Window import Window
from Window import DraggableWindow
from Window import EscapableWindow
from Console import Console
from InternalBrowser import InternalBrowser
from LanguageIndicator import LanguageIndicator

from FocusManager import getFocusedComponent, setFocusedComponent, isFocusedComponent

import EditUtils
import Tests
import TextStyles
import Utils
import VisualStateComponent
import IME

from Listeners import *

# TODO: should these be in PyGUI?
from Helpers.videoFeeds import s_videoFeeds
from Helpers.videoFeeds import VideoFeed
from Helpers.ProgressBar import IProgressBar
from Helpers.ProgressBar import ProgressBar
from Helpers.ProgressBar import ChunkLoadingProgressBar
from Helpers.ProgressBar import TeleportProgressBar

	
def handleKeyEvent( event ):
	import DraggableComponent
	return DraggableComponent.dragManager.handleKeyEvent( event )
	

def handleMouseEvent( event ):
	if ToolTipManager.instance is not None:
		ToolTipManager.instance.handleMouseEvent( event )

	import DraggableComponent
	return DraggableComponent.dragManager.handleMouseEvent( event )
	
	
def handleIMEEvent( event ):
	import GUI
	handled = False

	import LanguageIndicator
	LanguageIndicator.handleIMEEvent( event )
	
	focused = getFocusedComponent()
	if focused is not None and hasattr( focused.script, 'handleIMEEvent' ):
		handled = focused.script.handleIMEEvent( event )

	# Make sure IME UI is hidden if we're turning off (in case there
	# isn't a component in focus to do it).
	import BigWorld		
	if not BigWorld.ime.enabled or BigWorld.ime.state == "OFF":
		IME.hideAll()
	
	return handled

def fini():
	import VisualStateComponent
	VisualStateComponent.VisualState.clearTextureCache()
	