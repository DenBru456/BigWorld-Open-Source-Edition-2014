import BigWorld
from bwdebug import *
from FX import s_sectionProcessors
from FX.Actor import Actor


class ShockWaveModel( Actor ):
	stdModel = "objects/models/fx/fx_shockwave.model"


	def modelName( self, pSection ):
		name = pSection.asString
		if name == "":
			name = ShockWaveModel.stdModel
		return name


	def load( self, pSection, prereqs = None ):
		name = self.modelName( pSection )
		try:
			actor = prereqs.pop(name)
		except:
			try:
				actor = BigWorld.Model(name)
			except:
				ERROR_MSG( "Could not create Model", name )
				actor = None
		return actor


	def prerequisites( self, pSection ):
		return [pSection.asString,self.modelName(pSection)]


s_sectionProcessors[ "ShockWaveModel" ] = ShockWaveModel
