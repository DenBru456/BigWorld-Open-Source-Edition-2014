import BigWorld
from Keys import *
from Helpers import Caps
from FDGUI import Minimap
import Math

class Building( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.chunkModel = None
		self.targetCaps = [ Caps.CAP_CAN_USE ]
		
	def prerequisites( self ):
		return ("sets/town/props/pillar_stage1.model",
				"sets/town/props/pillar_stage2.model",
				"sets/town/props/pillar_stage3.model",
				"sets/town/props/pillar_stage4.model" )

	def onEnterWorld( self, prereqs ):
		self.prereqs = prereqs
		self.model = BigWorld.Model( "" )
		self.model.scale = (1,1,1)
		self.set_modelName()
		self.focalMatrix = Math.Matrix()
		self.focalMatrix.setTranslate( (0, 2, 0) )
		self.focalMatrix.preMultiply( self.matrix )
		self.targetFullBounds = True
		Minimap.addEntity( self )

	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.prereqs = None
		self.model = None

	def set_modelName( self, oldModelName = None ):
		if self.isDestroyed:
			return
		try:
			# add the model as a first class chunk model item!
			self.model = BigWorld.PyModelObstacle( self.modelName, self.matrix, False )
		except EnvironmentError:
			# If chunk not yet loaded try again in 5s
			BigWorld.callback( 5, self.set_modelName )


	def use( self ):
		if BigWorld.isKeyDown( KEY_LSHIFT ) or \
				BigWorld.isKeyDown( KEY_RSHIFT ):
			self.cell.destruct()
		else:
			self.cell.construct()
			
	def name( self ):
		return "Building"
