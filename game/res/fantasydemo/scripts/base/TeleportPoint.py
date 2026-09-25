import BigWorld
import FantasyDemo

class TeleportPoint( FantasyDemo.Base ):
	def __init__( self ):
		FantasyDemo.Base.__init__( self )

		fullyQualifiedName = \
			("TeleportPoint", self.realm, self.spaceName, self.label )

		self.registerGlobally( fullyQualifiedName, self.onRegister )


	def onRegister( self, succeeded ):
		if not succeeded:
			print "TeleportPoint.onRegister: Failed to register", \
					self.realm, self.spaceName, self.label


	def getTeleportPointInfo( self, sourceMB ):
		sourceMB.receiveTeleportPointInfo( self.cell, self.dstPos )


def find( realm, spaceName = "default", pointName = "default" ):
	try:
		return BigWorld.globalBases[
						("TeleportPoint", realm, spaceName, pointName ) ]
	except:
		return None


def match( realm, spaceName = None, pointName = None ):
	return [m for m in BigWorld.globalBases.keys()
				if m[ 0 ] == "TeleportPoint" and
					((realm is None) or
						(m[ 1 ] == realm)) and
					((spaceName is None) or
						(m[ 2 ] == spaceName)) and
					((pointName is None) or
						(m[ 3 ] == pointName))]


# TeleportPoint.py
