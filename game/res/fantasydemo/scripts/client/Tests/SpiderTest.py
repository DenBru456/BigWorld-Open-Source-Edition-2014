
from bwdebug import *
from GameData import CreatureData
import BigWorld
import Avatar
from functools import partial

class SpiderTest:
	'''
	A test to make a spider regularly repeat the digging action.
	Usage: import Tests.Spider
	t = Tests.SpiderTest.SpiderTest()
	t.start()
	t.stop()
	'''

	time = 3.0

	def __init__( self ):
		self.entityID = 0
		pass

	def spiderHide( self, spiderID ):

		spider = BigWorld.entities[ spiderID ]
		if spider is None:
			ERROR_MSG( "Could not get spider" )
			return
		spider.performHideAction()
		BigWorld.callback( SpiderTest.time,
			partial( SpiderTest.spiderReveal, self, spiderID ) )

	def spiderReveal( self, spiderID ):

		spider = BigWorld.entities[ spiderID ]
		if spider is None:
			ERROR_MSG( "Could not get spider" )
			return
		spider.performRevealAction()

		if not self.quit:
			BigWorld.callback( SpiderTest.time,
				partial( SpiderTest.spiderHide, self, spiderID ) )
		
	def start( self ):

		if (BigWorld.player() is None or not
			isinstance( BigWorld.player(), Avatar.Avatar )):
			ERROR_MSG( "Cannot run test without player" )
			return

		self.quit = False

		if self.entityID == 0:
			typeName = "Creature"
			properties = { 'creatureType': int( CreatureData.SPIDER ),
				'creatureName': "Summoned Spider",
				'creatureState': int( CreatureData.ALIVE ) }

			self.entityID = BigWorld.player().summonEntity( typeName, properties )

			if self.entityID == 0:
				ERROR_MSG( "Could not summon spider" )
				return

		BigWorld.callback( SpiderTest.time,
			partial( SpiderTest.spiderHide, self, self.entityID ) )

	def stop( self ):
		self.quit = True

	def destroy( self ):
		if self.entityID != 0:
			try:
				BigWorld.destroyEntity( self.entityID )
			except:
				pass
			self.entityID = 0
