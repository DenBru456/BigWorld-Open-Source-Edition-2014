import BigWorld
import FantasyDemo
import random
from bwdebug import *
from GameData import GuardSpawnerData


# ------------------------------------------------------------------------------
# Section: class GuardSpawner
# ------------------------------------------------------------------------------

def isGuardSpawnerReady( targetSpace ):
	globalBaseKey = GuardSpawner._globalBaseKey( targetSpace )
	return BigWorld.globalBases.has_key( globalBaseKey )

def spawnGuardsInSpace( targetSpace, numberOfGuards, maxGuards, spawnDuration, 
		timeToLive ):
	if not isGuardSpawnerReady( targetSpace ):
		return
	globalBaseKey = GuardSpawner._globalBaseKey( targetSpace )
	guardSpawner = BigWorld.globalBases[globalBaseKey]
	guardSpawner.spawnGuardsGlobally( numberOfGuards, maxGuards, 
		float( spawnDuration ), float( timeToLive ) )


def removeGuardsFromSpace( targetSpace, numberOfGuards ):
	if not isGuardSpawnerReady( targetSpace ):
		return
	globalBaseKey = GuardSpawner._globalBaseKey( targetSpace )
	guardSpawner = BigWorld.globalBases[globalBaseKey]
	guardSpawner.removeGuardsGlobally( numberOfGuards )


class GuardSpawner( FantasyDemo.Base ):

	LOCAL_REQUEST_SPAWN_TIMER = 1
	GLOBAL_REQUEST_SPAWN_TIMER = 2
	GLOBAL_REMOVE_TIMER = 3
	LOCAL_SPAWNING_TIMER = 4
	GUARD_RECOUNT_TIMER = 5

	def __init__( self ):
		FantasyDemo.Base.__init__( self )

		self.guardSpawners = dict()
		self.localSpawnRequests = dict()
		self.globalSpawnRequests = dict()
		self.guardRemoveRequests = dict()
		self.spawnTimers = dict()

	def setSpaceID( self, spaceID ):
		self.spaceID = spaceID
		self.registerGlobally( GuardSpawner._globalBaseKey( spaceID ),
				self.registerGloballyCallback )


	def registerGloballyCallback( self, success ):
		try:
			globalBaseKey = GuardSpawner._globalBaseKey( self.spaceID )
			masterGuardSpawner = BigWorld.globalBases[ globalBaseKey ]
			masterGuardSpawner.addGuardSpawner( self )
			if masterGuardSpawner.id == self.id:
				self.addTimer( 2.0, 2.0, GuardSpawner.GUARD_RECOUNT_TIMER )

		except KeyError, e:
			ERROR_MSG( "GuardSpawner failed to register "
					"or find global base '%s'" % 
				GuardSpawner._globalBaseKey( self.spaceID ) )


	def onTimer( self, controllerID, userData ):
		if userData == GuardSpawner.LOCAL_REQUEST_SPAWN_TIMER:
			self._initiateLocalGuardSpawns( controllerID )

		elif userData == GuardSpawner.GLOBAL_REQUEST_SPAWN_TIMER:
			self._initiateGlobalGuardSpawns( controllerID )

		elif userData == GuardSpawner.GLOBAL_REMOVE_TIMER:
			self._initiateGuardRemoval( controllerID )

		elif userData == GuardSpawner.LOCAL_SPAWNING_TIMER:
			self.spawnOne( controllerID )

		elif userData == GuardSpawner.GUARD_RECOUNT_TIMER:
			totalSpawnedGuards = sum( [spawnedGuards 
					for spawnedGuards, pendingGuards in 
						self.guardSpawners.values()] )

			for guardSpawnerMailbox in self.guardSpawners:
				guardSpawnerMailbox.cell.setNumberOfGuards( totalSpawnedGuards )

			self.recountGuards()


	@staticmethod
	def _globalBaseKey( spaceID ):
		return ("GuardSpawner", spaceID)


	def addGuardSpawner( self, guardSpawnerMailbox ):
		assert guardSpawnerMailbox not in self.guardSpawners
		self.guardSpawners[ guardSpawnerMailbox ] = (0, 0)


	def spawnGuardsLocally( self, targetGuardSpawner, numberOfGuards, 
			maxGuards, spawnDuration, timeToLive ):

		globalBaseKey = GuardSpawner._globalBaseKey( self.spaceID )
		masterSpawner = BigWorld.globalBases[ globalBaseKey ]

		if self.id != masterSpawner.id:
			masterSpawner.spawnGuardsLocally( targetGuardSpawner, 
				numberOfGuards, maxGuards, spawnDuration, timeToLive )
			return

		controllerID = self.addTimer( 0.5, 0.0, 
			GuardSpawner.LOCAL_REQUEST_SPAWN_TIMER )
		self.localSpawnRequests[ controllerID ] = LocalGuardSpawnRequest( 
			targetGuardSpawner, numberOfGuards, maxGuards, spawnDuration, 
			timeToLive )
		self.recountGuards()


	def spawnGuardsGlobally( self, numberOfGuards, maxGuards, spawnDuration, 
			timeToLive ):
		controllerID = self.addTimer( 0.5, 0.0, 
			GuardSpawner.GLOBAL_REQUEST_SPAWN_TIMER )
		self.globalSpawnRequests[ controllerID ] = GuardSpawnRequest( 
			numberOfGuards, maxGuards, spawnDuration, timeToLive )
		self.recountGuards()


	def removeGuardsGlobally( self, numberOfGuards ):
		controllerID = self.addTimer( 0.5, 0.0, 
			GuardSpawner.GLOBAL_REMOVE_TIMER )
		self.guardRemoveRequests[ controllerID ] = \
			GuardRemoveRequest( numberOfGuards )
		self.recountGuards()


	def recountGuards( self ):
		for guardSpawnerMailbox in self.guardSpawners:
			guardSpawnerMailbox.queryNumberOfGuards( self )


	def queryNumberOfGuards( self, returnMailbox ):
		spawnedGuards = len( self.guardList )
		pendingGuards = sum( [numberOfGuards 
			for numberOfGuards, timeToLive in self.spawnTimers.values()] )

		returnMailbox.notifyNumberOfGuards( self, spawnedGuards, pendingGuards )


	def notifyNumberOfGuards( self, spawnerMailbox, spawnedGuards, 
			pendingGuards ):
		#self.guardSpawners[ spawnerMailbox ] = (spawnedGuards, pendingGuards)

		for i in self.guardSpawners:
			if i.id == spawnerMailbox.id:
				self.guardSpawners[i] = (spawnedGuards, pendingGuards)


	def totalGuardsForSpawner( self, spawnerMailbox ):
		for s, (existingGuards, pendingGuards) in self.guardSpawners.items():
			if s.id == spawnerMailbox.id:
				return existingGuards + pendingGuards
		return 0

	def addPendingGuardCounts( self, spawnerMailbox, newGuards ):
		for s, (existingGuards, pendingGuards) in self.guardSpawners.items():
			if s.id == spawnerMailbox.id:
				self.guardSpawners[s] = \
					(existingGuards, pendingGuards + newGuards)
		return 0



	def _initiateLocalGuardSpawns( self, controllerID ):

		localSpawnRequest = self.localSpawnRequests[ controllerID ]

		# Don't spawn more than the spawner's maximum number of guards.

		totalGuards = self.totalGuardsForSpawner( 
			localSpawnRequest.targetGuardSpawner )

		maxGuardsToSpawn = max( 0, 
			localSpawnRequest.maxGuards - totalGuards )

		guardsToSpawn = min( localSpawnRequest.numberOfGuards, 
			maxGuardsToSpawn )

		localSpawnRequest.targetGuardSpawner.spawnGuards( guardsToSpawn, 
			localSpawnRequest.spawnDuration, localSpawnRequest.timeToLive )

		self.addPendingGuardCounts( localSpawnRequest.targetGuardSpawner,
			guardsToSpawn )

		del self.localSpawnRequests[ controllerID ]


	def _initiateGlobalGuardSpawns( self, controllerID ):

		globalSpawnRequest = self.globalSpawnRequests[ controllerID ]
		totalGuards = sum( [spawnedGuards + pendingGuards 
			for spawnedGuards, pendingGuards in self.guardSpawners.values()] )
		maxGuardsToSpawn = max( 0, globalSpawnRequest.maxGuards - totalGuards )
		guardsToSpawn = min( globalSpawnRequest.numberOfGuards, 
			maxGuardsToSpawn )

		for spawner, (spawnedGuards, pendingGuards) in \
				self.guardSpawners.items():
			numberOfGuards = guardsToSpawn // len( self.guardSpawners )
			spawner.spawnGuards( numberOfGuards, 
				globalSpawnRequest.spawnDuration, 
				globalSpawnRequest.timeToLive )
			self.guardSpawners[spawner] = \
				(spawnedGuards, pendingGuards + numberOfGuards)

		del self.globalSpawnRequests[ controllerID ]


	def _initiateGuardRemoval( self, controllerID ):

		guardRemoveRequest = self.guardRemoveRequests[ controllerID ]
		totalSpawnedGuards = sum( [spawnedGuards 
			for spawnedGuards, pendingGuards in self.guardSpawners.values()] )

		if totalSpawnedGuards == 0:
			return

		guardsToRemove = min( guardRemoveRequest.numberOfGuards, 
			totalSpawnedGuards )

		for spawner, (spawnedGuards, pendingGuards) in \
				self.guardSpawners.items():
			spawner.removeGuards( 
				guardsToRemove * (float( spawnedGuards ) / totalSpawnedGuards ))

		del self.guardRemoveRequests[ controllerID ]


	def registerGuard( self, guardMailbox ):
		self.guardList.append( guardMailbox )


	def deregisterGuard( self, guardID ):
		#self.guardList.remove( guardMailbox )

		for i in self.guardList:
			if i.id == guardID:
				self.guardList.remove( i )
				break


	def spawnGuards( self, numberOfGuards, spawnDuration, timeToLive ):
		if numberOfGuards > 0:
			frequency = spawnDuration / numberOfGuards

			timer = self.addTimer( 0, frequency, 
				GuardSpawner.LOCAL_SPAWNING_TIMER )
			self.spawnTimers[timer] = (numberOfGuards, timeToLive)
			self.cell.setSpawning( True )


	def spawnOne( self, controllerID ):
			numberOfGuards, timeToLive = self.spawnTimers[ controllerID ]

			self.cell.createGuard( timeToLive )

			numberOfGuards -= 1
			self.spawnTimers[ controllerID ] = (numberOfGuards, timeToLive)

			if numberOfGuards <= 0:
				self.delTimer( controllerID )
				del self.spawnTimers[ controllerID ]
				if len( self.spawnTimers ) == 0:
					self.cell.setSpawning( False )

	def removeGuards( self, numberOfGuards ):
		for guard in random.sample( self.guardList, 
				min( numberOfGuards, len( self.guardList ) ) ):
			guard.destroyGuard()


class GuardSpawnRequest:
	def __init__( self, numberOfGuards, maxGuards, spawnDuration, timeToLive ):
		self.numberOfGuards = numberOfGuards
		self.maxGuards = min( maxGuards, 
			GuardSpawnerData.SPAWNED_GUARDS_POPULATION_LIMIT )
		self.spawnDuration = spawnDuration
		self.timeToLive = timeToLive


class LocalGuardSpawnRequest( GuardSpawnRequest ):
	def __init__( self, targetGuardSpawner, numberOfGuards, maxGuards, 
			spawnDuration, timeToLive ):
		GuardSpawnRequest.__init__( self, numberOfGuards, maxGuards, 
			spawnDuration, timeToLive )
		self.targetGuardSpawner = targetGuardSpawner


class GuardRemoveRequest:
	def __init__( self, numberOfGuards ):
		self.numberOfGuards = numberOfGuards




# GuardSpawner.py




