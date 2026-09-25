import BigWorld
import FDConfig
import FantasyDemo

import logging

from GameData import FantasyDemoData
from Recorder import Recorder

nameSeparator = "/"

log = logging.getLogger( "SpaceLoader" )

class SpaceLoader( FantasyDemo.Base, Recorder ):
	def __init__( self ):
		log.info( "SpaceLoader %d spaceDir = %s", self.id, self.spaceDir )
		FantasyDemo.Base.__init__( self )
		Recorder.__init__( self )

		# A cell may have already been created in FantasyDemo.Base.__init__
		if not self.hasCell:
			self.createInNewSpace( shouldPreferThisMachine = False )

		self.cell.addGeometryMappingIfNeeded( self.spaceDir )

		self._entityLoader = None

	def onGetCell( self ):
		if FDConfig.LOAD_ENTITIES_FROM_CHUNKS:
			log.info( "SpaceLoader.onGetCell: loading space %s",
				self.spaceDir )

			self._entityLoader = EntityLoader( self, self.wasAutoLoaded ) 
			BigWorld.fetchEntitiesFromChunks( self.spaceDir,
					self._entityLoader )

		self.writeToDB( shouldAutoLoad = True )

	def onRestore( self ):
		self._entityLoader = None

	def onLoseCell( self ):
		if self._entityLoader is not None:
			self._entityLoader.active = False

		# Notify the entities we loaded that we are leaving
		for e in self.createdEntities:
			e.onSpaceLoaderDestroyed()

		# This may queue a respawn
		FantasyDemo.Base.onLoseCell( self )



AUTO_LOAD_TYPES = set( ("Merchant", "SpaceLoader") )

class EntityLoader:
	def __init__( self, spaceLoader, wasAutoLoaded ):
		self.spaceLoader = spaceLoader
		self.wasAutoLoaded = wasAutoLoaded
		self.active = True
		self.realm = spaceLoader.realm
		self.spaceDir = spaceLoader.spaceDir

		# Create and register the initial teleport point as soon as possible
		# instead of in onFinish as it may take a while for us to get there on 
		# larger spaces.
		if spaceLoader.isDefault:
			teleportPoint = BigWorld.createBaseLocally( 'TeleportPoint',
					realm = self.realm,
					createOnCell = spaceLoader.cell,
					dstPos = spaceLoader.startPosition,
					position = spaceLoader.startPosition,
					spaceName = "default",
					label = "default",
					direction = (0,0,0) )
			self.spaceLoader.createdEntities.append( teleportPoint )


	def onSection( self, entity, matrix ):
		entityType = entity.readString( "type" )
		properties = entity[ "properties" ]
		pos = matrix.applyToOrigin()

		if not self.active:
			return

		if self.wasAutoLoaded and entityType in AUTO_LOAD_TYPES:
			return

		extraArgs = {}

		if entityType == "TeleportPoint":
			extraArgs = dict( realm = self.realm,
						spaceName = self.spaceDir,
						dstPos = pos )

		newBase = BigWorld.createBaseAnywhere( entityType,
			properties,
			createOnCell = self.spaceLoader.cell,
			position = pos,
			direction = (matrix.roll, matrix.pitch, matrix.yaw),
			**extraArgs )
		self.spaceLoader.createdEntities.append( newBase )


	def onFinish( self ):
		if self.active:
			result = "Finished"
		else:
			result = "Aborted"

		log.info( "%s loading entities for space %s, %s",
				result, self.realm, self.spaceDir )

# SpaceLoader.py
