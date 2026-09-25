"""This module implements the VideoScreen entity type."""


import BigWorld
from Helpers import Caps
import VideoScreen
from FDGUI import Minimap

class VideoScreenChanger( BigWorld.Entity ):

	modelName = "sets/items/upperskull.model"

	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def prerequisites( self ):
		return [VideoScreenChanger.modelName]		


	def onEnterWorld( self, prereqs ):
		self.model = prereqs[VideoScreenChanger.modelName]
		self.focalMatrix = self.model.matrix	
		Minimap.addEntity( self )
		self.targetCaps = [Caps.CAP_CAN_USE]


	def onLeaveWorld( self ):
		Minimap.delEntity( self )


	def use( self ):
		videoScreen = self.findEntity()
		if videoScreen != None:
			videoScreen.changeFeed()
		
	def findEntity( self ):
		for e in BigWorld.entities.values():
			if type(e) == VideoScreen.VideoScreen and e.textureFeedName == "bone_tv":
				return e
		return None
		
	def name( self ):
		return "Change Channel"

#VideoScreenChanger.py
