'''The module implements a system for defining a list of models and possible customisations that can be used to to generate data in the form used by the avatar model system. All models and their customisations (dyes etc.) are required
to be present in the AvatarModelData module.
'''


import ResMgr
from GameData import AvatarModelData
import AvatarModel
import random
import traceback

class BaseElement( object ):
	def loadCustomisations( self, dataSection ):
		customisations = []
		for tag, section in dataSection.items():
			if tag == "modelCustomisation":
				customisations.append( ModelCustomisation( section ) )

			if tag == "materialCustomisation":
				customisations.append( MaterialCustomisation( section ) )
		return customisations


class Model( BaseElement ):
	'''This class holds the list of required models and available customisations
	for one 'base model' such has Human Male.
	'''

	def __init__( self, dataSection ):
		self.name = dataSection.readString( "name" )
		self.models = dataSection.readStrings( "models/resPath" )
		self.customisations = self.loadCustomisations( dataSection["customisations"] )
		if not self.checkModel():
			raise Exception()

	def checkModel( self ):
		ok = True

		for model in self.models:
			if not model in AvatarModelData.MODEL_INDEXES.keys():
				print "ASSET ERROR: model '%s' not in AvatarModelData" % model
				ok = False

		if not ok:
			return False

		referencedModels = []
		for modelPath in self.models:
			modelIndex = AvatarModelData.MODEL_INDEXES[modelPath]
			referencedModels.append( AvatarModelData.INDEXED_MODELS[modelIndex] )
		mergedDyes = AvatarModel.mergeDyes( referencedModels )

		for customisation in self.customisations:
			if isinstance( customisation, ModelCustomisation ):
				for model in customisation.models:
					ok = ok and model.checkModel()

			if isinstance( customisation, MaterialCustomisation ):
				for materialGroup in customisation.materialGroups:
					if not materialGroup in mergedDyes:
						print "ASSET ERROR: material group '%s' not in model ['%s']" % ( materialGroup, "', '".join( self.models ) )
						ok = False
					else:
						for tint in customisation.tints:
							if not tint.tintName in mergedDyes[materialGroup]:
								print "ASSET ERROR: '%s' is not a tint of material group '%s' in model ['%s']" % ( tint, materialGroup, "', '".join( self.models ) )
								ok = False
		return ok


	def __str__ (self):
		ret = "Model Name %s\n " % self.name
		if len(self.models) > 0:
			ret += "self.models %s\n" % ["%s" % model for model in self.models]
		if len(self.customisations) > 0:
			ret += "self.customisations %s " % ["%s" % custom for custom in self.customisations]
		return ret

class Tint( BaseElement ):
	'''This class holds the list of required Tints and available customisations
	for one 'base model' such has Human Male.
	'''

	def __init__( self, dataSection ):
		self.tintName = dataSection.readString("tintName")
		self.customisations = self.loadCustomisations( dataSection["customisations"] )

	def __str__ (self):
		ret = "self.tintName %s\n" % self.tintName
		if len(self.customisations) > 0:
			ret += "self.customisations %s " % ["%s" % custom for custom in self.customisations]
		return ret


class BaseModel( Model ):
	'''This class represents a base level model which can be built up using
	customisations.
	'''

	def __init__( self, dataSection ):
		Model.__init__( self, dataSection )
		self.realm = dataSection.readString( 'realm', 'fantasy' )


	def _internalResolve( self, customisations ):
		models = []
		otherCustomisations = []
		for customisation in customisations:
			if isinstance( customisation, ModelCustomisation ):
					newModels, newCustomisations = self._resolveModelCustomisations( random.choice( customisation.models ) )
					models.extend( newModels )
					otherCustomisations.extend( newCustomisations )

			if isinstance( customisation, MaterialCustomisation ):
				newModels, newCustomisations = self._resolveMaterialCustomisations( random.choice( customisation.tints ), customisation.materialGroups[0] )
				models.extend( newModels )
				otherCustomisations.extend( newCustomisations )

		return models, otherCustomisations


	def _resolveModelCustomisations( self, model ):
		models = list( model.models )
		otherDyes = []

		internalModels, dyes = self._internalResolve( model.customisations )
		models.extend( internalModels )
		otherDyes.extend( dyes )

		return models, otherDyes


	def _resolveMaterialCustomisations( self, material, materialGroup ):
		models = []
		otherDyes = [ { 'materialGroup': materialGroup,
						'tint': material.tintName } ]

		internalModels, dyes = self._internalResolve( material.customisations )
		models.extend( internalModels )
		otherDyes.extend( dyes )

		return models, otherDyes


	def createInstanceWithRandomCustomisations( self ):
		'''This function returns the data of an avatar model containing this base model and a random selection of customisations.
		'''

		models = []
		dyes = []
		sfx = []

		models, dyes = self._resolveModelCustomisations( self )
		return {'models':models,
				'dyes':dyes,
				'sfx':sfx }



class Customisation( object ):
	def __init__( self, dataSection ):
		self.name = dataSection.readString( "name" )


class ModelCustomisation( Customisation ):
	'''This class represents a customisation where each option adds a new model
	to the base. These models can also then have their own customisations.
	'''
	def __init__( self, dataSection ):
		Customisation.__init__( self, dataSection )
		self.models = []
		for modelData in dataSection["models"].values():
			try:
				self.models.append( Model( modelData ) )
			except Exception, e:
				print "ASSET ERROR: Could not load avatar model '%s'" % modelData.readString( "name", "Unknown" )
				traceback.print_exc()
				print e
		
	def __str__ ( self ):
		if len(self.models) > 0:
			return "ModelCustomisation models %s " % ["%s" % model for model in self.models]
		return "ModelCustomisation []"
	
class MaterialCustomisation( Customisation ):
	'''This class represents a material customisation where each option applies
	a different dye to the model.
	'''
	def __init__( self, dataSection ):
		Customisation.__init__( self, dataSection )
		self.materialGroups = dataSection.readStrings( "materialGroups/materialGroup" )
		self.tints = []
		for tintData in dataSection["tints"].values():
			try:
				self.tints.append( Tint( tintData ) )
			except Exception, e:
				print "ASSET ERROR: Could not load avatar model '%s'" % modelData.readString( "name", "Unknown" )
				traceback.print_exc()
				print e

	def __str__ ( self ):
		ret =  "MaterialCustomisation materialGroup %s \n" % self.materialGroups 
		if len(self.tints) > 0:
			ret += "MaterialCustomisation tints %s " % self.tints
		return ret


def load( modelData ):
	result = []

	for modelData in modelData['baseModels'].values():
		try:
			#print "Loading CustomModel info: '%s'" % modelData.readString( "name" )
			result.append( BaseModel( modelData ) )
		except Exception, e:
			print "ASSET ERROR: Could not load CustomModel info for '%s'" % modelData.readString( "name", "Unknown" )
			traceback.print_exc()
			print e

	return result





