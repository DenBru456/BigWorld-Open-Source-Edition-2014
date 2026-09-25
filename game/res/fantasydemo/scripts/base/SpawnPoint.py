import FantasyDemo
import BigWorld
import random
import spawnPointArgs

# ------------------------------------------------------------------------------
# Section: class SpawnPoint
# ------------------------------------------------------------------------------

class SpawnPoint( FantasyDemo.Base ):

	def spawn(self, position, direction):
		if(random.random() < self.rarePercent / 100.0):
			entityType = spawnPointArgs.spawnPointArgs[ self.spawnName ][ 'rareEntityType' ]
			args = spawnPointArgs.spawnPointArgs[ self.spawnName ][ 'rareSpawn' ]
		else:
			entityType = spawnPointArgs.spawnPointArgs[ self.spawnName ][ 'commonEntityType' ]
			args = spawnPointArgs.spawnPointArgs[ self.spawnName ][ 'commonSpawn' ]

		cellOnlySpawn = spawnPointArgs.spawnPointArgs[ self.spawnName ].has_key( 'cellOnly' )

		args[ 'position' ] = position
		args[ 'direction' ] = direction
		if cellOnlySpawn:
			self.cell.spawn( entityType, args )
		else:
			# pass our own mailbox so the created entity can register back
			# if it expects to be instantiated from a SpawnPoint
			args[ 'createOnCell' ] = self.cell
			obj = BigWorld.createBaseLocally( entityType, args )
			self.cell.register( obj.id )

# SpawnPoint.py
