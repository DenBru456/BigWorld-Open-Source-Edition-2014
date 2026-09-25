from MaterialSectionProcessorBase import MaterialSectionProcessorBase

# This class changes the name of effect files
class EffectNameChanger( MaterialSectionProcessorBase ):

	def __init__( self ):
		MaterialSectionProcessorBase.__init__( self )
		self.description = "Effect Name Changer"
		self.nameChangeMap = {}
		base = "shaders/std_effects/"
		self.nameChangeMap[ base + "character_lighting.fx" ] = base + "normalmap_glow.fx"
		self.nameChangeMap[ base + "character_lighting_alpha.fx" ] = base + "normalmap_glow_alpha.fx"
		self.nameChangeMap[ base + "character_lighting_chrome.fx" ] = base + "normalmap_chrome_glow.fx"
		self.nameChangeMap[ base + "character_lighting_chrome_hardskinned.fx" ] = base + "normalmap_chrome_glow_hardskinned.fx"
		self.nameChangeMap[ base + "character_lighting_chrome_skinned.fx" ] = base + "normalmap_chrome_glow_skinned.fx"
		self.nameChangeMap[ base + "character_lighting_hardskinned.fx" ] = base + "normalmap_glow_hardskinned.fx"
		self.nameChangeMap[ base + "character_lighting_skinned.fx" ] = base + "normalmap_glow_skinned.fx"
		self.nameChangeMap[ base + "character_lighting_specmap.fx" ] = base + "normalmap_specmap.fx"
		self.nameChangeMap[ base + "character_lighting_specmap_hardskinned.fx" ] = base + "normalmap_specmap_hardskinned.fx"
		self.nameChangeMap[ base + "character_lighting_specmap_skinned.fx" ] = base + "normalmap_specmap_skinned.fx"
		self.nameChangeMap[ base + "colourise_character_lighting_specmap_skinned.fx" ] = base + "colourise_normalmap_specmap_skinned.fx"
		
		
	def appliesTo( self ):
		return ("model","visual","mfm","chunk")
		
		
	#This method is not need here, but is included to make it obvious what is happening.
	#The base class processes the dbEntry and calls "processMaterialSection" when it
	#finds any materials sections.
	def process( self, dbEntry ):
		return MaterialSectionProcessorBase.process( self, dbEntry )
		
		
	def processMaterialSection( self, sect, dbEntry ):		
		effectName = sect.readString( "fx" )		
		if self.nameChangeMap.has_key( effectName ):			
			sect.deleteSection( "fx" )
			sect.writeString( "fx", self.nameChangeMap[effectName] )			
			return True
		return False
								