'''This module holds data about AvatarModels loaded form the file
avatar_model_data.xml and the .model files themselves. All models listed in
should exist in the resource path.
'''

import ResMgr

INDEXED_MODELS = None
INDEXED_SFX = None

MODEL_INDEXES = None
SFX_INDEXES = None


class ModelData:
	'''The class represents one .model file and its available dyes including
	those inherited from its parent.
	'''

	def __init__( self, modelDataSection ):
		self.resPath = modelDataSection.asString
		self.dyes = ModelData.loadDyes( self.resPath )


	def __str__( self ):
		return "ModelData '%s'" % self.resPath

	@staticmethod
	def loadDyes( resPath ):
		dyes = {}
		if resPath != "":
			parentModel = ResMgr.openSection( resPath ).readString( "parent", "" )
			if parentModel != "":
				dyes = ModelData.loadDyes( parentModel + ".model" )
	
			for dyeTag, dyeSection in ResMgr.openSection( resPath ).items(): 
				if dyeTag == "dye":
					materialGroupName = dyeSection.readString( "matter" )
					if not materialGroupName in dyes:
						dyes[dyeSection.readString( "matter" )] = set(["Default"])
					for tintTag, tintSection in dyeSection.items():
						if tintTag == "tint":
							dyes[materialGroupName].add( tintSection.readString( "name" ) )

		return dyes


def load():
	models = []
	modelsSection = ResMgr.openSection( "scripts/data/avatar_model_data.xml/models" )
	for modelDataSection in modelsSection.values():
		try:
			#print "Loading AvatarModelData for: '%s'" % modelDataSection.asString
			model = ModelData( modelDataSection )
			models.append( model )
		except:
			print "ASSET ERROR: AvatarModelData could not load model '%s'" % modelDataSection.asString

	global INDEXED_MODELS
	INDEXED_MODELS = dict( enumerate( models ) )

	global MODEL_INDEXES
	MODEL_INDEXES = dict( [(m.resPath, i) for i, m in INDEXED_MODELS.items()] )

	global INDEXED_SFX
	sfxSections = ResMgr.openSection( "scripts/data/avatar_model_data.xml/specialEffects" )
	INDEXED_SFX = dict( enumerate( sfxSections.readStrings( "sfx" ) ) )

	global SFX_INDEXES
	SFX_INDEXES = dict( [(e, i) for i, e in INDEXED_SFX.items()] )

load()
