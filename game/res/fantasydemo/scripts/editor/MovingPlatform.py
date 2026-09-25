from GameData import MovingPlatformData

class MovingPlatform:
	def modelName( self, props ):
		return MovingPlatformData.modelNames[ props[ "platformType" ] ]

	def getEnums_platformType( self ):
		l = []
		for (id,name) in MovingPlatformData.editorDisplayNames.items():
			l.append( (id,name) )
		return tuple(l)

	# platform nodes linking conditions
	def canLink( self, propName, thisInfo, otherInfo ):
		if otherInfo['type'] == 'PlatformNode':
			return True
		else:
			return False

# MovingPlatform.py
