"""This module implements the Landmark entity type."""


import BigWorld
#from Helpers.alertsGui import instance as Alerts
import FantasyDemo
from FDGUI import Minimap

from Helpers.CallbackHelpers import *


# ------------------------------------------------------------------------------
# Class Landmark:
#
# A Landmark entity simply informs the player when they are entering an area
# designated as being interesting;  a landmark if you will.
#
# Currently text is displayed - area name, time.
#
# ------------------------------------------------------------------------------

class Landmark( BigWorld.Entity ):


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
		self.playerInside = False
		self.timerCount = 0
		self.delaying = False


	# --------------------------------------------------------------------------
	# Method: checkProperties
	# Description:
	#	- Checks all properties defined in the XML file to see if they are
	#	  valid.
	# --------------------------------------------------------------------------
	def checkProperties( self ):
		# methodName = "Landmark.checkProperties: "
		pass


	# --------------------------------------------------------------------------
	# Method: onEnterWorld
	# Description:
	#	- Sets a time for the effect in appear after the model anchor has been
	#	  drawn.
	# --------------------------------------------------------------------------
	def onEnterWorld( self, prereqs ):
		self.potID = BigWorld.addPot( self.matrix, self.radius, self.hitPot )
		Minimap.addEntity( self )


	# --------------------------------------------------------------------------
	# Method: onLeaveWorld
	# --------------------------------------------------------------------------
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
		if enter:
			FantasyDemo.rds.region.onEnterRegion( self.description )
		else:
			FantasyDemo.rds.region.onLeaveRegion( self.description )
			
		player = BigWorld.player()
		if not player:
			return

		self.playerInside = enter

		if enter:
			if not self.delaying:
				self.timerCount += 1
				BigWorld.callback( self.initialTriggerDelay, self.onTimer )


	# --------------------------------------------------------------------------
	# Method: hitPot
	#
	# This method is called when the player enters / leaves the radius.
	# --------------------------------------------------------------------------
	@IgnoreCallbackIfDestroyed
	def onTimer( self ):
		self.timerCount -= 1
		if self.timerCount == 0:
			if self.playerInside == True:
				self.showMessage()
				self.delaying = True
				BigWorld.callback( self.retriggerDelay, self.releaseDelay )


	# --------------------------------------------------------------------------
	# Method: releaseDelay
	# --------------------------------------------------------------------------
	@IgnoreCallbackIfDestroyed
	def releaseDelay( self ):
		self.delaying = False


	# --------------------------------------------------------------------------
	# Method: showMessage
	# --------------------------------------------------------------------------
	@IgnoreCallbackIfDestroyed
	def showMessage( self ):
		if BigWorld.player().spaceID != None:			
			timeOfDay = BigWorld.spaceTimeOfDay( BigWorld.player().spaceID )
			msg = "%s, %s hours" % (self.description, timeOfDay)
#			alert = Alerts.add( "landmark", msg )
		else:
			BigWorld.callback( 5.0, self.showMessage )


	# --------------------------------------------------------------------------
	# Method: name
	# Description:
	#	- Part of the entity interface: This allows the client to get a string
	#	  name for the Landmark.
	# --------------------------------------------------------------------------
	def name( self ):
		if hasattr( self, "label" ):
			return "Landmark : " + self.label
		return "Landmark"


#Landmark.py
