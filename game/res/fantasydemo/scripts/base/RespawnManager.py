import BigWorld
import cPickle

class RespawnManager( BigWorld.Base ):
	""" This singleton object managers entity respawn process.
	Any entity who wish to respawn should register with this
	object and pass in all necessary information (as a dictionary)
	for spawning a new entity with same characteristics of the early
	one """
	CHECK_INTERVAL = 10

	def __init__( self ):
		def onRegisterGlobally( success ):
			if success:
				self.addTimer( 1, self.CHECK_INTERVAL, 0 )
			else:
				print 'There is a RespawnManager already in existence. Abort!'
				self.destroy()

		print 'initiallising a RespawnManager'
		self.respawnList = []
		self.registerGlobally( 'RespawnManager', onRegisterGlobally )

	def onTimer( self, timerID, userData ):
		i = 0
		while i < len( self.respawnList ) and self.respawnList[i]['RespawnTime'] <= BigWorld.time():
			entityData = cPickle.loads( self.respawnList[i]['EntityData'] )
			entityType = self.respawnList[i]['EntityType']
			print 'Respawning a', entityType
			BigWorld.createBaseAnywhere( entityType, entityData )
			i += 1

		self.respawnList = self.respawnList[i:]

	def registerForRespawn( self, entityType, entityData, respawnInterval ):
		print 'Register a', entityType, 'for respawn in', respawnInterval * 60 ,'seconds!'
		respawnTime = BigWorld.time() + respawnInterval * 60
		cEntityData = cPickle.dumps( entityData,-1 )
		self.respawnList.append( {'EntityType':entityType, 'EntityData':cEntityData, 'RespawnTime':respawnTime} )

