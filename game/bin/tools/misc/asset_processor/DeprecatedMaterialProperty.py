from MaterialSectionProcessorBase import MaterialSectionProcessorBase
from LogFile import errorLog

#
# Any Individual Asset Processor must have
#
# a list of extensions that the processor applies to
# a process( dbEntry ) method
#
# the process method returns true iff the file was updated.
#

# This class strips out deprecated properties from material sections.
# Just add property names to the stripList and enable the processor in
# the AssetDatabase class
class DeprecatedMaterialPropertyFix( MaterialSectionProcessorBase ):

	def __init__( self ):
		MaterialSectionProcessorBase.__init__( self )
		self.description = "Deprecated Material Property Fix"
		# stripList is a list of the deprecated properties 
		#  : ( property Name, FX file association, on-fix callback )
		self.stripList = []
		self.stripList.append( ("heightMap","shaders/std_effects/parallax_lighting_specmap.fx", self.onHeightMapFixApplied) )		
		self.stripList.append( ("diffuseLightExtraModulation",None, None) )
		self.stripList.append( ("useSpecularMap",None, None) )
		self.stripList.append( ("specularColour",None, None) )
		self.stripList.append( ("lightDir",None, None) )
		self.stripList.append( ("lightColour",None, None) )
		self.stripList.append( ("lightEnable",None, None) )
		
		
	def appliesTo( self ):
		return ("model","visual","mfm","chunk")
		
		
	#This method is not need here, but is included to make it obvious what is happening.
	#The base class processes the dbEntry and calls "processMaterialSection" when it
	#finds any materials sections.
	def process( self, dbEntry ):
		return MaterialSectionProcessorBase.process( self, dbEntry )
		
	def onHeightMapFixApplied( self, property, effect, sect ):
		for (j,k) in sect.items():
			if j == "Texture":
				errorLog.infoMsg( "redundant : %s" % (k.asString) )
		
		
	def processMaterialSection( self, sect, dbEntry ):
		changed = False
		validSectionList = []
		sectionNames = []
		effect = sect.readString( "fx" )		
				
		for (key,value) in sect.items():
			foundMatch = False
			if key == "property":				
				for (propName, fxName, callback) in self.stripList:					
					if value.asString == propName:
						if (fxName == None or fxName == effect):
							foundMatch = True
							if callback != None:
								callback(propName,fxName,value)
			
			if foundMatch:
				changed = True
			else:
				validSectionList.append((key,value))
				
			sectionNames.append(key)
		
		if changed:
			for key in sectionNames:
				sect.deleteSection(key)
				
			for (key,value) in validSectionList:
				ds = sect.createSection(key)
				ds.copy(value)
							
		return changed