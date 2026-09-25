import FantasyDemo
from AvatarCommon import AvatarCommon
from GameData import GuardData
import AvatarModel

# ------------------------------------------------------------------------------
# Section: class Guard
# ------------------------------------------------------------------------------

class Guard( FantasyDemo.Base, AvatarCommon ):

	def __init__( self ):
		if len( self.cellData[ "playerName" ] ) == 0:
			self.cellData[ "playerName" ] = unicode( GuardData.GUARD_SHOWNAMES[ self.guardType ] )

		self.cellData[ "rightHand" ] = -1

		# add in any attributes that needed to respawn a new
		# entity with
		if self.respawnInterval != 0:
			self.entityData = self.cellData
			self.entityData[ 'respawnInterval' ] = self.respawnInterval


		model = GuardData.GUARD_MODELS[ self.guardType ].createInstanceWithRandomCustomisations()
		self.cellData['avatarModel'] = AvatarModel.pack( model )


		if self.owner:
			self.owner.registerGuard( self )

		FantasyDemo.Base.__init__( self )
		AvatarCommon.__init__( self )

	def onLoseCell( self ):
		if self.owner:
			self.owner.deregisterGuard( self.id )
			self.owner = None
		AvatarCommon.onLoseCell( self )

	def destroyGuard( self ):
		self.destroyCellEntity()

# Guard.py
