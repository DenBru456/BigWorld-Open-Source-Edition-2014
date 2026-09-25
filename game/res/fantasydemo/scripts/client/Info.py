###This module implements the Info client-only entity type.
###This entity shows information text when approached.

import BigWorld
import FantasyDemo
import Math
import GUI
import FDGUI
from FDGUI import Minimap
from Helpers import Caps

#Austin GDC 2007 - ability to toggle visibility of all info entities
allInfoEntities = []
infoEntitiesVisible = True

def setVisibilityOfAllInfoEntities( state ):
	global infoEntitiesVisible
	infoEntitiesVisible = state
	for i in allInfoEntities:
		i.model.visible = state

class Info( BigWorld.Entity ):
	MODEL_NONE			= 0
	MODEL_INFO			= 1
	MODEL_ARROW			= 2

	modelNames = {
		MODEL_NONE:			"",
		MODEL_INFO:			"sets/items/information.model",
		MODEL_ARROW:		"sets/items/arrow.model",
		}

	curInfoEntity = None

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.chunkModel = None
		self.targetCaps = []
		self.seen = False
		self.active = False
		# allows activation when distance is equal or less to 'activateDist':
		if self.showWhenNear:
			self.activateDist = 3
		else:
			self.activateDist = 6

	# entity callbacks
	def prerequisites( self ):
		return [self.modelName()]

	def onEnterWorld( self, prereqs ):
		allInfoEntities.append(self)
		self.model = prereqs.pop(self.modelName())
		self.model.scale = (1,1,1)
		self.targetFullBounds = True
		self.setupTrap()
		self.model.visible = infoEntitiesVisible
		FantasyDemo.addDeviceListener(self)
		Minimap.addEntity( self )

	def onLeaveWorld( self ):
		gui = self.getGUI()
		if gui is not None:
			gui.script.active( False )
			
		self.model = None
		Minimap.delEntity( self )
		if hasattr(self, "potID"):
			BigWorld.delPot(self.potID)
			del self.potID

		FantasyDemo.delDeviceListener(self)
		allInfoEntities.remove(self)

	def name( self ):
		return "Info"

	def use( self ):
		dist = Math.Vector3( self.model.position - BigWorld.player().position).length
		if dist > self.activateDist:
			return

		if not self.active:
			self.activate( True )
		else:
			self.activate( False )

	# methods for internal use:
	def modelName( self ):
		return Info.modelNames[ self.modelType ]

	def setupTrap( self ):
		try:
			self.potID = BigWorld.addPot( self.model.matrix, self.activateDist, self.infoTrap )
			self.activate( False )
		except EnvironmentError:
			# If chunk not yet loaded try again in 5s
			BigWorld.callback( 5, self.setupTrap )

	def infoTrap( self, entered, handle ):
		if entered:
			# in range anymore, activate.
			if self.showWhenNear:
				self.activate( True )
		else:
			# if not in range anymore, deactivate.
			self.activate( False )

	def activate( self, doActivate ):
		self.active = doActivate
		gui = self.getGUI()
		if gui is not None:
			if doActivate is True:
				Info.curInfoEntity = self
				gui.script.active( True )
			else:
				if Info.curInfoEntity is self:
					gui.script.active( False )
					Info.curInfoEntity = None
		
		if doActivate:
			self.invalidate()
			if not self.seen and self.modelType != Info.MODEL_NONE:
				self.model.PlayInactive()
				self.model.empty_skinned = 'inactive'
			self.seen = True
		else:
			if not self.seen and self.modelType != Info.MODEL_NONE:
				self.model.PlayActive()
				self.model.empty_skinned = 'Default'

	def onRecreateDevice( self ):
		self.invalidate()

	def invalidate( self ):
		gui = self.getGUI()
		if gui != None:
			gui.windowGUI.script.text( self.text )
			gui.windowGUI.script.invalidate()
			minHeight = gui.frameGUI.texture.width * 2.0
			oldHeightMode = gui.windowGUI.heightMode
			gui.windowGUI.heightMode = "PIXEL"
			if gui.windowGUI.height < minHeight:
				gui.windowGUI.height = minHeight
			gui.windowGUI.heightMode = oldHeightMode
			gui.frameGUI.height = gui.windowGUI.height
			gui.height = gui.windowGUI.height

	def getGUI( self ):
		try:
			return FantasyDemo.rds.fdgui.infoBox
		except AttributeError:
			return None

#Info.py
