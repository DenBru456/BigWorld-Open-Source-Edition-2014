'''The module implements a system for loading a preset model
'''


import ResMgr


def load( modelData ):
	result = {}

	result[ 'models' ] = list( modelData.readStrings( 'model' ) )
	result[ 'dyes' ] = []
	result[ 'sfx' ] = []

	for modelData in modelData.values():
		if modelData.name == 'dye':
			dye = {}
			dye[ 'tint' ] = modelData.readString( 'tint' )
			dye[ 'materialGroup' ] = modelData.readString( 'materialGroup' )
			result[ 'dyes' ].append( dye )

	return result
