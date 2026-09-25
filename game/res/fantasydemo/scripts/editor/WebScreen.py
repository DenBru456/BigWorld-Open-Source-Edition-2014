from GameData import WebScreenData

class WebScreen:
	def modelName( self, props ):
		return WebScreenData.modelNames[ props[ "webScreenType" ] ]


	def getEnums_webScreenType( self ):
		l = []
		for (id,name) in WebScreenData.editorDisplayNames.items():
			l.append( (id,name) )
		return tuple(l)

	def getEnums_graphicsSettingsBehaviour( self ):
		l = []
		for (id,name) in WebScreenData.editorDisplayGraphicsSettingsBehaviour.items():
			l.append( (id,name) )
		return tuple(l)
# WebScreen.py
