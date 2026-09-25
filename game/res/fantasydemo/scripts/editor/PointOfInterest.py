class PointOfInterest:
	def modelName( self, props ):
		try:
			return props[ 'modelName' ]
		except:
			return "helpers/props/standin.model"

# PointOfInterest.py
