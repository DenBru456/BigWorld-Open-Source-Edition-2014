

from GameData import TriggeredDustData


class TriggeredDust:
	def modelName( self, props ):
		return "helpers/props/standin.model"
	
	
	EFFECT_LIST = [ ( '', 'None' ), ]
	
	for i in TriggeredDustData.EFFECTS:
		EFFECT_LIST.append( ( i, i.split( '/' )[-1] ) )
	
	
	
	def getEnums_effectName( self ):
		return TriggeredDust.EFFECT_LIST


# TriggeredDust.py
