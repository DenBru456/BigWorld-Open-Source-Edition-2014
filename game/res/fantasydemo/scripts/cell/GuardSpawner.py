import BigWorld
import math
import random
import Math

# This entity provides a button that players can use to spawn new Guards.

# Data Requirements:
# The connected graph is fully bidirectional for all links
# The 'typeName' corresponds to a known entity type
# The dictionary string can be resolved to a valid python dictionary


class GuardSpawner( BigWorld.Entity ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.entityCreationDictionary = {}
		try:
			dictionary = eval( self.dictionary )
			dictionary = dict( dictionary )
			if not 'playerName' in dictionary:
				dictionary['playerName'] = u'Orc'

			self.entityCreationDictionary = dictionary

		except:
			print 'GuardSpawner@', self.position, \
				' Bad dictionary parameter : ', \
				self.dictionary

		print 'GuardSpawner@', self.position, ' dictionary : ', \
			self.entityCreationDictionary

		self.base.setSpaceID( self.spaceID )


	#-------------------------------------------------------------------------
	# This method is called when a timer expires.
	#-------------------------------------------------------------------------
	def onTimer(self, timerID, userID):
		pass


	def onAllSpaceGeometryLoaded( self, spaceID, isBootstrap, mapping ):
		pass


	def createGuard( self, timeToLive ):
		"""
		Spawn a new Guard entity.
		If timeToLive is set, it will clean itself up automatically.
		If owner is set, it will register with that Base for later cleanup.
		"""
		try:
			nodeLink = random.choice( self.spawnPoints )

			guardDict = dict( self.entityCreationDictionary )

			guardDict['initialPatrolNode'] = nodeLink
			guardDict['spaceID'] = self.spaceID
			guardDict['position'] = nodeLink.position
			guardDict['timeToLive'] = timeToLive
			guardDict['owner'] = self.base
			guardDict['guardType'] = self.guardType

			BigWorld.createEntityOnBaseApp( 'Guard', guardDict )

		except BigWorld.UnresolvedUDORefException:
			print 'GuardSpawner.spawnOne UnresolvedUDORefException ', nodeLink.guid
			raise


	def setNumberOfGuards( self, numberOfGuards ):
		if self.numberOfGuards != numberOfGuards:
			self.numberOfGuards = numberOfGuards


	def setSpawning( self, spawning ):
		if self.spawning != spawning:
			self.spawning = spawning


	def spawnGuardsLocally( self, sourceID, numberOfGuards, 
			spawnDuration ):
		self.base.spawnGuardsLocally( self.base, numberOfGuards, self.maxGuards, 
			spawnDuration, self.guardTimeToLive )


# GuardSpawner.py



