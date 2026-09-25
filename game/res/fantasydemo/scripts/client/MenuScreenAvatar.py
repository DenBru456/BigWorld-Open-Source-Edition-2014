import BigWorld
import AvatarModel
import PlayerModel

from functools import partial
from Helpers.CallbackHelpers import *

class MenuScreenAvatar( BigWorld.Entity ):

	def __init__( self ):
		self.avatarModel = AvatarModel.defaultModel()


	def prerequisites( self ):
		return AvatarModel.getPrerequisites( self.avatarModel )


	def onEnterWorld( self, prereqs ):
		self.model = AvatarModel.create( self.avatarModel )


	def onLeaveWorld( self ):
		pass


	def set_avatarModel( self, oldValue = None, callback = lambda: None ):
		BigWorld.loadResourceListBG( AvatarModel.getPrerequisites( self.avatarModel ),
									partial( self.set_avatarModel_stage2, self.avatarModel, callback ) )

	@IgnoreCallbackIfDestroyed
	def set_avatarModel_stage2( self, unpackedAvatarModel, callback, resourceRefs ):
		self.model = AvatarModel.create( unpackedAvatarModel, self.model )

		callback()


	def setModel( self, avatarModel ):
		self.avatarModel = avatarModel
		self.set_avatarModel()



