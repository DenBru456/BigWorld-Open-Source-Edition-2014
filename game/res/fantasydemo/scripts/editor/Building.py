class Building:
	def modelName( self, props ):
		try:
			return props[ "models" ][ props[ "stage" ] ]
		except:
			return "helpers/props/standin.model"

# Building.py
