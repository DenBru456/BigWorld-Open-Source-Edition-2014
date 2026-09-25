
import WorldEditor
from GameData import GuardData


class GuardSpawner:
	def modelName( self, props ):
		return 'characters/npc/fd_orc_guard/statue.model'


	def getEnums_guardType( self ):
		return GuardData.GUARD_TYPES.items()


# GuardSpawner.py



