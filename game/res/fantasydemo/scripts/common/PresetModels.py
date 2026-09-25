'''The module implements a system for loading preset models
'''


import PresetModel


def load( modelData ):
	result = []

	for modelData in modelData.values():
		if modelData.name == 'presetModel':
			result.append( PresetModel.load( modelData ) )

	return result
