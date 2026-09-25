import BigWorld
import ResMgr
from cPickle import dumps

from SpaceData import SPACE_DATA_SPACE_LOADER
from Recorder import Recorder

START_TIME_OF_DAY = 7.5 * 60 * 60 # 7:30
GAME_SECONDS_PER_SECOND = \
	ResMgr.openSection( 'scripts/data/fantasy_demo.xml' ).readInt( 
		'gameSecondsPerSecond', 6 )


class SpaceLoader( BigWorld.Entity, Recorder ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		Recorder.__init__( self )

		self.spaceEntryID = None

		BigWorld.setSpaceData( self.spaceID, SPACE_DATA_SPACE_LOADER, 
			dumps( self.base ) )


	def addGeometryMappingIfNeeded( self, geometryToMap ):
		"""
		Add the given space geometry at the origin.
		"""

		# If space data was archived, it would have already been mapped.
		if not BigWorld.getSpaceGeometryMappings( self.spaceID ):
			self.spaceEntryID = BigWorld.addSpaceGeometryMapping(
					self.spaceID, None, geometryToMap )

		BigWorld.setSpaceTimeOfDay( self.spaceID, 
			START_TIME_OF_DAY, GAME_SECONDS_PER_SECOND )


	def onSpaceDataDeleted( self, spaceID, deletedEntryID, key, deletedValue ):
		if self.spaceEntryID == deletedEntryID:
			self.spaceEntryID = None
			self.destroy()


	def onDestroy( self ):
		Recorder.onDestroy( self )
		if self.spaceEntryID is not None:
			BigWorld.delSpaceData( self.spaceID, self.spaceEntryID )
			self.spaceEntryID = None

# SpaceLoader.py
