import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x

class ParticleFileProcessor:
	def __init__( self ):
		pass
		
	def buildDatabase(self,dbEntry):		
		sect = dbEntry.section()
		
		# lets do some particle processing shall we
		for value in sect.values():
			if value.has_key( "serialiseVersionData" ):
				renderer = value["Renderer"]
				if renderer != None:
					if renderer.has_key("AmpParticleRenderer"):
						dbEntry.addDependency(renderer.readString("AmpParticleRenderer/textureName_"))
					elif renderer.has_key("BlurParticleRenderer"):
						dbEntry.addDependency(renderer.readString("BlurParticleRenderer/textureName_"))
					elif renderer.has_key("MeshParticleRenderer"):
						dbEntry.addDependency(renderer.readString("MeshParticleRenderer/visualName_"))
					elif renderer.has_key("PointSpriteParticleRenderer"):
						dbEntry.addDependency(renderer.readString("PointSpriteParticleRenderer/textureName_"))
					elif renderer.has_key("SpriteParticleRenderer"):
						dbEntry.addDependency(renderer.readString("SpriteParticleRenderer/textureName_"))
					elif renderer.has_key("TrailParticleRenderer"):
						dbEntry.addDependency(renderer.readString("TrailParticleRenderer/textureName_"))
					elif renderer.has_key("VisualParticleRenderer"):
						dbEntry.addDependency(renderer.readString("VisualParticleRenderer/visualName_"))
				
	def process(self,dbEntry):
		return True
