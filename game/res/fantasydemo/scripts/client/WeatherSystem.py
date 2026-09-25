"""This module implements the WeatherSystem entity type."""


import BigWorld
from FDGUI import Minimap


class WeatherSystem(BigWorld.Entity):

	def __init__(self):
		BigWorld.Entity.__init__( self )


	def onEnterWorld( self, prereqs ):
		self.potID = BigWorld.addPot( self.matrix, self.radius, self.hitPot )
		Minimap.addEntity( self )


	def onLeaveWorld( self ):
		if hasattr( self, "potID" ):
			BigWorld.delPot( self.potID )
		Minimap.delEntity( self )


	# --------------------------------------------------------------------------
	# Method: hitPot
	#
	# This method is called when the player enters / leaves the radius.
	# --------------------------------------------------------------------------
	def hitPot( self, enter, id = None ):
		import Weather
		weather = Weather.weather()

		if enter:
			weather.override( self.name )
		else:
			weather.override( None )
