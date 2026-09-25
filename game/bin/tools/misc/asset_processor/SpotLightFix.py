from LogFile import errorLog
import AssetProcessorSystem
import ResMgr
from FileUtils import extractSectionsByName
import math

# This class finds  the spot light in .chunk ,and reverse it's direction
class SpotLightFix:

	def __init__( self ):		
		self.description = "Reverse the spot light direction and use correct cosConeAngle value for static spot light in chunk file."


	def appliesTo( self ):
		return ("chunk",)


	def process( self, dbEntry ):
		sect = dbEntry.section()
		if sect is None:
			return False
		
		changed = False
		spotLights = extractSectionsByName( sect, "spotLight" )
		for lightSect in spotLights:
			version = lightSect.readFloat("editorOnly/version", 0)
			if version != 2.0:
				lightSect.writeFloat("editorOnly/version", 2.0)
				
				# for static spot light, fix cosConeAngle, because from the new version, cosConeAngle is actually cosHalfConeAngle instead of cosConeAngle, 
				# but we want the customer's already placed static spot light won't change effect when doing recaculation 
				# for dynamic spot light, cosConeAngle has been cosHalfConeAngle already, so no need change anything for them.
				if lightSect.readBool( "static" ):
					cosConeAngle = lightSect.readFloat( "cosConeAngle" )
					cosConeAngle = math.cos( math.acos( cosConeAngle ) / 2.0 )
					lightSect.writeFloat( "cosConeAngle",  cosConeAngle)		
					errorLog.infoMsg( "spotLight set cosConeAngle %s is done" %  cosConeAngle )

				#reverse the direction
				dir = - lightSect.readVector3( "direction" )
				lightSect.writeVector3 ( "direction",  dir )
				errorLog.infoMsg( "spotLight revert direction %s is done" %  dir )
				if not changed:
					changed = True
		if changed:
			sect.save()
			errorLog.infoMsg( "changed" )
		else:
			errorLog.infoMsg( "not changed" )
		return True
