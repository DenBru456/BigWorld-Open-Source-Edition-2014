import WorldEditor
import ResMgr


class Ecotypes:
	def __init__( self ):
		self.textureLayers = [ "blank", "blank", "blank", "blank" ]
		self.textureAmounts = [0,0,0,0]
		self.textureToEcotype={}
		self.textureFactor={}
		self.maximumSlope = 30.0

		ecotype = 0
		floraXMLname = ResMgr.root.readString( "resources.xml/environment/floraXML", "" )
		print floraXMLname
		floraXML = ResMgr.openSection( floraXMLname+"/ecotypes" )
		print floraXML
		if (floraXML != None) and (len(floraXML.items()) > 0):
			for i in floraXML.values():
				for (key,sect) in i.items():
					if key == "texture":	
						textureName = sect.asString			
						self.textureToEcotype[textureName] = ecotype
						self.textureFactor[textureName] = sect.readFloat("weight", 1.0)
				ecotype += 1
		else:
			print "ERROR Ecotypes.py:__init__ - found no ecotypes.  please check your Flora XML file"

	#This method is called before a number of chunks are calculated.
	#Currently it does nothing but print a message to WorldEditor.
	#Because updates and rendering are stopped throughout, this message
	#will only come up when finished.
	def begin( self, dummyValue ):
		WorldEditor.addCommentaryMsg( "`SCRIPT/ECOTYPES_PY/FINISHED_CALC_ECOTYPES", 0 )

	#This method is called per chunk, to let ecotypes.py know
	#which textures the current chunk is using for the four
	#blending layers.
	def textureLayer( self, index, textureName ):
		self.textureLayers[ index ] = textureName

	#This rule returns 1 for the maximum texture found, or 0
	def textureRule( self, ecotype ):
		texName = self.textureLayers[ecotype]
		return self.textureAmounts[ecotype] * self.textureFactor[texName]

	#This rule reduces all detail objects at higher slopes
	#If the slope is great, then favour ecotype 0 - the empty set
	def slopeRule( self, ecotype, slope ):
		if ( slope > self.maximumSlope ):
			return -10.0
		return 0.0

	#This is the main function to call for ecotypes.py.
	#This method returns the id of the best ecotype at the given height pole.
	#The id returned is a direct lookup into the list of <mapping> tags in flora.xml
	def calculateEcosystem( self, elevation, relativeElevation, slope, a1, a2, a3, a4 ):
		#calculate how much texture is at this height pole
		self.textureAmounts[0] = a1
		self.textureAmounts[1] = a2
		self.textureAmounts[2] = a3
		self.textureAmounts[3] = a4

		#apply rules
		#and save the maximum probability

		maxIndex = -1
		maxAmount = 0.0
		probabilities = [0.0,0.0,0.0,0.0]

		for i in xrange(0,4):
			if self.textureToEcotype.has_key( self.textureLayers[i] ):
				probabilities[i] += self.textureRule( i )
				probabilities[i] += self.slopeRule( i, slope )
			else:
				probabilities[i] = -10

			if (probabilities[i] > maxAmount):
				maxIndex = i
				maxAmount = probabilities[i]

		#no ecotype found that had a positive probability
		if maxIndex == -1:
			return 0

		chosenTexture = self.textureLayers[maxIndex]

		#print ( "ecotype chosen was %s" % chosenTexture )

		if probabilities[maxIndex] > 0.0:
			if self.textureToEcotype.has_key( chosenTexture ):
				return self.textureToEcotype[chosenTexture]
			else:
				return 0
		else:
			return 0