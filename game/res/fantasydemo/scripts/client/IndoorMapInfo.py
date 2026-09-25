"""This module implements the IndoorMapInfo entity type."""


import BigWorld
from functools import partial
import FantasyDemo
from FDGUI import Minimap


# ------------------------------------------------------------------------------
# Class IndoorMapInfo:
#
# A IndoorMapInfo entity tells the client what the bitmap will be for the minimap
# when the player goes into an indoor area, as well as specifying other minimap
# settings.
# ------------------------------------------------------------------------------
class IndoorMapInfo( BigWorld.Entity ):

	# --------------------------------------------------------------------------
	# Method: __init__
	# --------------------------------------------------------------------------
	def __init__( self ):
		BigWorld.Entity.__init__( self )

		#
		# Set all standard entity variables.
		#
		self.targetCaps = []
		self.model = None


	# --------------------------------------------------------------------------
	# Method: checkProperties
	# Description:
	#	- Checks all properties defined in the XML file to see if they are
	#	  valid.
	# --------------------------------------------------------------------------
	def checkProperties( self ):
		# methodName = "IndoorMapInfo.checkProperties: "
		pass


	# --------------------------------------------------------------------------
	# Method: onEnterWorld
	# --------------------------------------------------------------------------
	def onEnterWorld( self, prereqs ):
		self.potID = BigWorld.addPot( self.matrix, self.radius, self.hitPot )
		mi = Minimap.MinimapInfo( Minimap.Minimap.INDOOR_LAYER )
		mi.textureName = self.mapName
		mi.range = self.minimapRange
		mi.worldMapWidth = self.worldMapWidth
		mi.worldMapHeight = self.worldMapHeight
		mi.worldMapAnchor = self.worldMapAnchor
		mi.rotate = self.minimapRotate
		self.mi = mi


	# --------------------------------------------------------------------------
	# Method: onLeaveWorld
	# --------------------------------------------------------------------------
	def onLeaveWorld( self ):
		if hasattr( self, "potID" ):
			BigWorld.delPot( self.potID )
		self.prereqs = None


	# --------------------------------------------------------------------------
	# Method: hitPot
	#
	# This method is called when the player enters / leaves the radius.
	# --------------------------------------------------------------------------
	def hitPot( self, enter, id = None ):
		player = BigWorld.player()
		if not player:
			return
			
		if enter:
			try:
				ime = BigWorld.player().triggeredIndoorMapEntity
			except AttributeError:
				ime = 0
				
			if ime != self.id:
				BigWorld.player().triggeredIndoorMapEntity = self.id
				#re-trigger minimap creation.  This is necessary because the
				#player may have just teleported from one indoor area to another
				BigWorld.player().onChangeEnvironments( BigWorld.player().inside )


	# --------------------------------------------------------------------------
	# Method: mapInfo
	#
	# This method returns the information we want to set on the minimap.
	# --------------------------------------------------------------------------
	def mapInfo( self ):
		return self.mi
		
	# --------------------------------------------------------------------------
	# Method: name
	#
	# This method returns the name of this class.
	# --------------------------------------------------------------------------
	def name( self ):
		return "Indoor Map Info"


#IndoorMapInfo.py
