import BigWorld
#import math
#import random
#import Math

# This entity provides a rally point for guards not already on a patrol path.
# Unconnected Guards will search for GuardRallyPoints in order to connect 
# to a patrol path.



class GuardRallyPoint( BigWorld.Entity ):

	#-------------------------------------------------------------------------
	# Constructor.
	#-------------------------------------------------------------------------
	def __init__( self ):
		BigWorld.Entity .__init__( self )


	#-------------------------------------------------------------------------
	# This method is called when a timer expires.
	#-------------------------------------------------------------------------
	def onTimer(self, timerId, userId):
		pass


	#-------------------------------------------------------------------------
	# This method is called when we've finished moving to a point.
	#-------------------------------------------------------------------------
	def onMove(self, controllerId, userId):
		pass
	
	
# GuardRallyPoint.py
