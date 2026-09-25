'''This module contains a number of utility functions for dealing with avatar
model data including converting to and from its network efficient 'packed' form
as well as constructing the resultant PyModels.
'''

import BigWorld
import ResMgr
from GameData import AvatarModelData


def create( unpackedModelData, model = None ):
	'''This function takes the data of an un-packed avatar model data and
	produces the resultant PyModel. An existing PyModel can optionally be
	provided for with which the function will attempt to sync up its action
	queues.
	Parameters: PERSISTENT_AVATAR_MODEL [,PyModel]
	Returns: PyModel
	'''

	modelList = set( unpackedModelData['models'] )
	if '' in modelList:
		modelList.remove('')

	if len( modelList ) > 0:
		modelList = list( modelList )
	else:
		modelList = ['']

	model = BigWorld.Model( *modelList )

	referencedModels = []
	for modelPath in unpackedModelData['models']:
		modelIndex = AvatarModelData.MODEL_INDEXES[modelPath]
		referencedModels.append( AvatarModelData.INDEXED_MODELS[modelIndex] )
	mergedDyes = mergeDyes( referencedModels )

	dyes = {}
	for dye in unpackedModelData['dyes']:
		dyes[dye['materialGroup']] = dye['tint']

	for materialGroup in mergedDyes.keys():
		if materialGroup in dyes:
			try:
				setattr( model, materialGroup, dyes[materialGroup] )
			except Exception, e:
				print "ERROR: Setting model.%s = '%s' for model ['%s']" % materialGroup, dyes[materialGroup], "', '".join(unpackedModelData['models'])
				print e
		else:
			try:
				setattr( model, materialGroup, "Default" )
			except:
				pass

	return model


def getPrerequisites( unpackedModelData ):
	'''This function gathers the resource prerequisits of the given un-packed
	avatar model data.
	Parameters: PERSISTENT_AVATAR_MODEL
	Returns: tuple([str,])
	'''
	prerequisites = []
	prerequisites.extend( unpackedModelData['models'] )
	prerequisites.extend( unpackedModelData['sfx'] )
	return tuple( prerequisites )


def pack( persistentModelData ):
	'''This function takes an un-packed avatar model and packs it into a network
	friendly form.
	Parameters: PERSISTENT_AVATAR_MODEL
	Returns: PACKED_AVATAR_MODEL
	'''
	modelData = {}
	modelData['models'] = []

	for resPath in persistentModelData['models']:
		if AvatarModelData.MODEL_INDEXES.has_key( resPath ):
			modelData['models'].append( AvatarModelData.MODEL_INDEXES[resPath] )
		else:
			print "Warning: Cannot find model %s in AvatarModel.pack" % resPath

	modelData['dyes'] = []
	mergedDyes = mergeDyes( [AvatarModelData.INDEXED_MODELS[model] for model in modelData['models']] )

	for persistendDye in persistentModelData['dyes']:
		try:
			dye = {}
			dye['materialGroup'] = sorted( mergedDyes.keys() ).index( persistendDye['materialGroup'] )
			dye['tint'] = sorted( mergedDyes[persistendDye['materialGroup']] ).index( persistendDye['tint'] )
			modelData['dyes'].append( dye )
		except Exception, e:
			print "Warning: Cannot find dye %s or tint %s in AvatarModel.pack" % \
				( persistendDye['materialGroup'], persistendDye['tint'] )

	modelData['sfx'] = []

	return modelData


def unpack( modelData ):
	'''This function takes an avatar model that has been packed for network
	transfer and returns the fully restored data suitable for persistent storage
	or constructing a PyModel.
	Parameters: PACKED_AVATAR_MODEL
	Returns: PERSISTENT_AVATAR_MODEL
	'''
	persistentModelData = {}
	persistentModelData['models'] = [AvatarModelData.INDEXED_MODELS[modelIndex].resPath for modelIndex in modelData['models']]

	persistentModelData['dyes'] = []
	mergedDyes = mergeDyes( [AvatarModelData.INDEXED_MODELS[modelIndex] for modelIndex in modelData['models']])
	for dye in modelData['dyes']:
		persistendDye = {}
		persistendDye['materialGroup'] = sorted( mergedDyes.keys() )[dye['materialGroup']]
		persistendDye['tint'] = sorted( mergedDyes[persistendDye['materialGroup']] )[dye['tint']]
		persistentModelData['dyes'].append( persistendDye )

	persistentModelData['sfx'] = []

	return persistentModelData


def mergeDyes( models ):
	'''This function takes a list of AvatarModelData models and builds the
	collection of dye options those models would have it they were combined into
	a single PyModel. The resulting dictionary has an entry for each material
	group with its full set of available tints.
	Parameters: list([AvatarModelData.ModelData,])
	Returns: dict([(str,set([str,])),])
	'''
	materialGroups = set()
	for model in models:
		for materialGroupName in model.dyes.keys():
			materialGroups.add( materialGroupName )

	mergedDyes = {}
	for materialGroupName in materialGroups:
		mergedDyes[materialGroupName] = set()
		for model in models:
			mergedDyes[materialGroupName] = mergedDyes[materialGroupName].union( model.dyes.get( materialGroupName, set() ) )
	return mergedDyes


def defaultModel():
	'''This function returns the default avatar model which is a single empty
	model.
	Returns: PERSISTENT_AVATAR_MODEL
	'''
	return {'models':['',],
			'dyes':[],
			'sfx':[] }



