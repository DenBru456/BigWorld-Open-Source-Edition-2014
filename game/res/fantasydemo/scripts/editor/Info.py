class Info:
	MODEL_NONE			= 0
	MODEL_INFO			= 1
	MODEL_ARROW			= 2

	modelNames = {
		MODEL_NONE:			"helpers/props/standin.model",
		MODEL_INFO:			"sets/items/information.model",
		MODEL_ARROW:		"sets/items/arrow.model",
		}

	def modelName( self, props ):
		try:
			return Info.modelNames[ props[ 'modelType' ] ]
		except:
			return "helpers/props/standin.model"

	def getEnums_modelType( self ):
		return ((Info.MODEL_NONE, "None"),
			(Info.MODEL_INFO, "Information"),
			(Info.MODEL_ARROW, "Arrow"))

# Info.py
