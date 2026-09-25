

import WorldEditor
from GameData import GuardData

class Guard:

	def modelName( self, props ):
		model = GuardData.GUARD_MODELS[ props['guardType'] ].createInstanceWithRandomCustomisations()

		return model['models'][0]


	def canLink( self, propName, thisInfo, otherInfo ):
		thisProps = thisInfo["properties"]
		otherProps = otherInfo["properties"]

		if propName == "initialPatrolNode":
			if otherInfo["type"] != "PatrolNode":
				# Only allows linking to PatrolNodes
				return False

		return True


	def getEnums_guardType( self ):
		return GuardData.GUARD_TYPES.items()




# Guard.py
