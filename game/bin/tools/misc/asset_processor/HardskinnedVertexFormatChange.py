from LogFile import errorLog
from FileUtils import fullName
from EffectNameChanger import EffectNameChanger
import AssetProcessorSystem

#------------------------------------------------------------------------------
# Any Individual Asset Processor must have
#
# a list of extensions that the processor applies to
# a process( dbEntry ) method
#
# the process method returns true iff the file was updated.
#------------------------------------------------------------------------------

#This class converts hardskinned vertices to softskinned ones.
class HardskinnedVertexFormatChange( EffectNameChanger ):
	def __init__( self ):
		EffectNameChanger.__init__( self )
		self.nameChangeMap = {}
		base = "shaders/std_effects/"
		self.nameChangeMap[ base + "normalmap_chrome_glow_hardskinned.fx" ] = base + "normalmap_chrome_glow_skinned.fx"
		self.nameChangeMap[ base + "normalmap_glow_hardskinned.fx" ] = base + "normalmap_glow_skinned.fx"
		self.nameChangeMap[ base + "normalmap_specmap_hardskinned.fx" ] = base + "normalmap_specmap_skinned.fx"
		self.nameChangeMap[ base + "character_lighting_chrome_hardskinned.fx" ] = base + "normalmap_chrome_glow_skinned.fx"
		self.nameChangeMap[ base + "character_lighting_hardskinned.fx" ] = base + "normalmap_glow_skinned.fx"
		self.nameChangeMap[ base + "character_lighting_specmap_hardskinned.fx" ] = base + "normalmap_specmap_skinned.fx"
		self.nameChangeMap[ base + "lightonly_hardskinned.fx" ] = base + "lightonly_skinned.fx"
		self.nameChangeMap[ base + "lightonly_hardskinned_chrome.fx" ] = base + "lightonly_skinned_chrome.fx"
		self.nameChangeMap[ base + "lightonly_hardskinned_glow.fx" ] = base + "lightonly_skinned_glow.fx"
		self.nameChangeMap[ base + "subsurface_hardskinned.fx" ] = base + "subsurface_skinned.fx"
		self.nameChangeMap[ base + "shadows/caster_hardskinned.fx" ] = base + "shadows/caster_skinned.fx"
		self.nameChangeMap[ base + "shadows/receiver_hardskinned.fx" ] = base + "shadows/receiver_skinned.fx"
		self.nameChangeMap[ base + "shimmer/shimmer_hardskinned.fx" ] = base + "shimmer/shimmer_skinned.fx"
		self.nameChangeMap[ base + "stipple/stipple_hardskinned.fx" ] = base + "stipple/stipple_skinned.fx"
		self.description = "Hard-skinned to soft-skinned vertices"			
		
	#Note - we only want to change the vertices if the material used is in the list,
	#i.e. this way we avoid changing the vertex format of mesh particle system files.
	def process( self, dbEntry ):	
		if EffectNameChanger.process( self, dbEntry ):			
			errorMsg = ""
			formatChanged = AssetProcessorSystem.upgradeHardskinnedVertices( dbEntry.name, errorMsg )
			if errorMsg != "":
				errorLog.errorMsg(ret)
			return formatChanged
		else:
			return False
