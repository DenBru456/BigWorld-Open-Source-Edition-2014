class GuardRallyPoint:
	def modelName( self, props ):
		try:
			return props[ 'modelName' ]
		except:
			return "helpers/props/standin.model"

# GuardRallyPoint.py
