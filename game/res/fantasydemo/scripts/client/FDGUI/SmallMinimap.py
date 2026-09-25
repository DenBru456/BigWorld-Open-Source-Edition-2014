import BigWorld
import Cursor
from Keys import *
import Helpers.PyGUI as PyGUI
from Helpers.PyGUI import PyGUIEvent
from Listener import Listenable
from Helpers import BWKeyBindings
from Helpers.BWKeyBindings import BWKeyBindingAction
import FantasyDemo


#------------------------------------------------------------------------------
# This class handles the minimap when it is in 'small' mode
#------------------------------------------------------------------------------
class SmallMinimap( PyGUI.Window, BWKeyBindings.BWActionHandler ):

	factoryString = "FDGUI.SmallMinimap"

	def __init__( self, component ):
		PyGUI.Window.__init__( self, component )
		BWKeyBindings.BWActionHandler.__init__( self )
		self.component.script = self
		self.minimap = None
		self.zoom = 200


	def onActive( self ):
		self.boundariesButton.setToggleState( self._minimap().cellBoundsVisible )
		self.entriesButton.setToggleState( self._minimap().simpleEntriesVisible )
		m = self._minimap()
		m.maskName = self.maskName
		m.script.maxZoom = 1500
		m.script.minZoom = 50
		m.range = self.zoom
		m.currentRange = self.zoom


	def active( self, state ):
		if state == True:
			FantasyDemo.rds.region.addListener( self )
			FantasyDemo.rds.keyBindings.addHandler( self )
			self.component.region.text = FantasyDemo.rds.region.describeCurrent()
		else:
			FantasyDemo.rds.region.delListener( self )
			FantasyDemo.rds.keyBindings.removeHandler( self )
		self.component.focus = state
		self._minimap().mouseEntryPicking = state
		PyGUI.Window.active( self, state )
		self.onActive()


	def avatarInit( self, avatar ):
		#This looks ok except when rotate=1 is used,
		#but since it isn't right now, it's not an issue
		self._minimap().viewpoint = avatar.matrix


	@PyGUIEvent( "cellBoundaries", "onActivate", True )
	@PyGUIEvent( "cellBoundaries", "onDeactivate", False )
	def onCellBoundariesActivate( self, activated ):
		self._minimap().cellBoundsVisible = activated


	@PyGUIEvent( "simpleEntries", "onActivate", True )
	@PyGUIEvent( "simpleEntries", "onDeactivate", False )
	def onSimpleEntriesActivate( self, activated ):
		self._minimap().simpleEntriesVisible = activated


	@BWKeyBindingAction( "ToggleMinimap" )
	@PyGUIEvent( "maximise", "onClick" )
	def onMaximiseClick( self, isDown = True ):
		if isDown:
			self._minimap().script.maximise( True )


	@PyGUIEvent( "zoomIn", "onClick" )
	def onZoomInClick( self ):
		self._minimap().script.zoomIn()
		self.zoom = self._minimap().range


	@PyGUIEvent( "zoomOut", "onClick" )
	def onZoomOutClick( self ):
		self._minimap().script.zoomOut()
		self.zoom = self._minimap().range


	def onBound( self ):
		PyGUI.Window.onBound( self )
		self.boundariesButton = self.component.cellBoundaries.script
		self.entriesButton = self.component.simpleEntries.script
		self.containerSize = (241,309)
		self.minimapSize = (214,214)
		self.maskName = "gui/maps/mini_map_mask.dds"
		self.maskTexture = BigWorld.PyTextureProvider( self.maskName ) # Keep reference around to avoid reloading


	#Callback from region event listener
	def onEnterRegion( self, description ):
		self.component.region.text = description


	#Callback from region event listener
	def onLeaveRegion( self, description ):
		self.component.region.text = description


	def _minimap( self ):
		return self.minimap


	@BWKeyBindingAction( "Teleport" )
	def teleport( self, isDown = True ):
		if isDown:
			return self._minimap().script.handleTeleport()
		return False

