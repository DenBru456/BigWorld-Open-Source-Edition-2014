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
# This class handles the minimap when it is in 'large' mode.  The buttons and
# events are different to when it is in 'small' mode.
#------------------------------------------------------------------------------
class LargeMinimap( PyGUI.Window, BWKeyBindings.BWActionHandler ):

	factoryString = "FDGUI.LargeMinimap"

	def __init__( self, component ):
		PyGUI.Window.__init__( self, component )
		BWKeyBindings.BWActionHandler.__init__( self )
		self.component.script = self
		self.minimap = None
		self.timeCallback = None
		self.zoom = 500


	def onActive( self ):
		BigWorld.callback( 1.0, self._updateCallback )
		self.boundariesButton.setToggleState( self._minimap().cellBoundsVisible )
		self.entriesButton.setToggleState( self._minimap().simpleEntriesVisible )
		m = self._minimap()
		m.maskName = self.maskName
		m.script.maxZoom = 5000
		m.script.minZoom = 250
		m.range = self.zoom
		m.currentRange = self.zoom


	def _updateCallback( self ):
		if self.isActive:
			BigWorld.callback( 1.0, self._updateCallback )
			self.updateStats()


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
		self._updateRangeLabel()
		player = BigWorld.player()
		if player:
			try:
				player.cell.enableEntityInfoCapture(state)
			except AttributeError, e:
				pass


	@PyGUIEvent( "cellBoundaries", "onActivate", True )
	@PyGUIEvent( "cellBoundaries", "onDeactivate", False )
	def onCellBoundariesActivate( self, activated ):
		self._minimap().cellBoundsVisible = activated


	@PyGUIEvent( "simpleEntries", "onActivate", True )
	@PyGUIEvent( "simpleEntries", "onDeactivate", False )
	def onSimpleEntriesActivate( self, activated ):
		self._minimap().simpleEntriesVisible = activated


	@PyGUIEvent( "spawn", "onClick" )
	def onSpawnClick( self ):
		maxGuards = 500

		if BigWorld.isKeyDown( KEY_LSHIFT ) or \
			BigWorld.isKeyDown( KEY_RSHIFT ):
			maxGuards = 1000

		try:
			BigWorld.player().base.spawnGuardsInSpace( BigWorld.player().spaceID, 100, maxGuards, 100.0, 300.0 )
		except AttributeError, e:
			pass


	@PyGUIEvent( "destroy", "onClick" )
	def onDestroyClick( self ):
		try:
			BigWorld.player().base.removeGuardsFromSpace( BigWorld.player().spaceID, 100 )
		except AttributeError, e:
			pass


	@BWKeyBindingAction( "ToggleMinimap" )
	@BWKeyBindingAction( "MinimiseMinimap" )
	@PyGUIEvent( "minimise", "onClick" )
	def onMinimiseClick( self, isDown = True ):
		if isDown:
			self._minimap().script.maximise( False )


	@PyGUIEvent( "zoomIn", "onClick" )
	def onZoomInClick( self ):
		self._minimap().script.zoomIn()
		self._updateRangeLabel()
		self.zoom = self._minimap().range


	@PyGUIEvent( "zoomOut", "onClick" )
	def onZoomOutClick( self ):
		self._minimap().script.zoomOut()
		self._updateRangeLabel()
		self.zoom = self._minimap().range


	def _updateRangeLabel( self ):
		range = self._minimap().range
		prefix = "Visible Map Range: "
		if range < 1000.0:
			self.component.visibleMapRange.text = prefix + "%dm" % (int(range))
		else:
			self.component.visibleMapRange.text = prefix + "%0.1fkm" % (range/1000.0)


	def onBound( self ):
		PyGUI.Window.onBound( self )
		self.boundariesButton = self.component.cellBoundaries.script
		self.entriesButton = self.component.simpleEntries.script
		self.containerSize = (1024,900)
		self.minimapSize = self.containerSize
		self.maskName = ""


	#Callback from region event listener
	def onEnterRegion( self, description ):
		self.component.region.text = description


	#Callback from region event listener
	def onLeaveRegion( self, description ):
		self.component.region.text = description


	def updateStats( self ):
		self.component.entitiesInAOI.text = "Entities in Area of Interest: " + BigWorld.getWatcher( "Entities/Active Entities" )
		if BigWorld.player() is not None:
			try:
				self.component.entitiesOnCell.text = "Entities on Current Cell: " + str(BigWorld.player().entityInfo)
				self.component.currentCellID.text = "Current Cell ID: " + str(BigWorld.player().cellAppID)
			except AttributeError, e:
				self.component.entitiesOnCell.text = "Entities on Current Cell: "
				self.component.currentCellID.text = "Current Cell ID: "


	def _minimap( self ):
		return self.minimap


	@BWKeyBindingAction( "Teleport" )
	def teleport( self, isDown = True ):
		if isDown:
			return self._minimap().script.handleTeleport()
		return False


	def avatarFini( self, avatar ):
		""" Function called when our PlayerAvatar leaves the world. """
		#~ # Large minimap does not get left in a valid state when maximised, so minimise it when we leave.
		self._minimap().script.maximise( False )


	#This prevents the large minimap enpassing LBTN, RBTN events further, while allowing
	#MBTN to be handled normally, i.e to do the teleport.
	def handleMouseButtonEvent( self, comp, event ):
		if event.key == KEY_MIDDLEMOUSE:
			return False
		return True
