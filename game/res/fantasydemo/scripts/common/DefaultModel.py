'''The module implements a system for defining a default model
'''


import PresetModel

def load( modelData ):
	return PresetModel.load( modelData[ 'defaultModel' ] )
