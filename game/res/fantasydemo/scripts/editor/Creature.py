from GameData import CreatureData

# This is an example of how to place an Entity in the world via WorldEditor. On the
# Entity panel, select Creature and place the Entity in the world by pressing
# enter. The placeholder model refered to by modelName() will be placed into the
# WorldEditor representation of the world and the Entity will be placed into the
# appropriate chunk file when the world is saved. Game script can then be used
# to load the entities into the game world. See BigWorld.fetchEntitiesFromChunks
# in BaseApp's Python API.

class Creature:
	
	def modelName( self, props ):
		return CreatureData.modelNames[ props[ "creatureType" ] ]

	def getEnums_creatureType( self ):
		l = []
		for (id,name) in CreatureData.displayNames.items():
			l.append( (id,name) )
		return tuple(l)
			
	def getEnums_creatureMonthOfBirth( self ):
		return ((0, "Jan"),
			(1, "Feb"),
			(2, "Mar"),
			(3, "Apr"),
			(4, "May"),
			(5, "Jun"),
			(6, "Jul"),
			(7, "Aug"),
			(8, "Sep"),
			(9, "Oct"),
			(10, "Nov"),
			(11, "Dec"))
			
	def getEnums_creatureRecoverRate( self ):
		return ((0.5, "Slow"),
			(1.5, "Normal"),
			(2.5, "Fast"),
			(10.9, "Ultra"))

# Creature.py
