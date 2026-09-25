"This module implements the SpawnPoint entity."

import BigWorld
import Math
from random import random

#TODO: When an entity leaves our AoI, we should not forget about it. (bases?)
#TODO: When an ID gets reused by a new entity, we should not get confused.

class SpawnPoint( BigWorld.Entity ):

	POLL_INTERVAL = 30

	def __init__(self):
		self.spawnedIDs = [0]*self.spawnCount
		self.respawnTimes = [0.0]*self.spawnCount

		self.addTimer(1, self.POLL_INTERVAL, 0)

	def onTimer(self, timerId, userId):
		for i in range(self.spawnCount):
			if self.spawnedIDs[i]:
				try:
					BigWorld.entities[self.spawnedIDs[i]]
				except KeyError:
					self.respawnTimes[i] = BigWorld.time() + self.spawnInterval * 60
					self.spawnedIDs[i] = 0
			elif self.respawnTimes[i] < BigWorld.time():
				if self.spawnCount == 1:
					realPos = self.position
				else:
					realPos = self.position + Math.Vector3(
						random()*40 - 20, 0, random()*40 - 20 )
				self.base.spawn( realPos, self.direction )

	def register( self, id ):
		for i in range(self.spawnCount):
			if self.spawnedIDs[i] == 0 and self.respawnTimes[i] < BigWorld.time():
				self.spawnedIDs[i] = id
				return
		print "SpawnPoint",self.id,": no slot for spawned entity",id,"!"

	#This method spawns a cell-only entity.  It is still called from the base.
	def spawn( self, entityType, args ):
		obj = BigWorld.createEntity( entityType, self.spaceID,
			args["position"], args["direction"], args )
		self.register( obj.id )

# SpawnPoint.py
