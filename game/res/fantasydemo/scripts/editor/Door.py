from GameData import DoorData

class Door:
	def modelName( self, props ):
		return DoorData.modelNames[ props[ "doorType" ] ]

	def getEnums_doorType( self ):
		l = []
		for (id,name) in DoorData.editorDisplayNames.items():
			l.append( (id,name) )
		return tuple(l)

# Door.py
