import FantasyDemo
import BigWorld
import Avatar
import AvatarMode
import AvatarModel
from Helpers import Caps
from ModeTarget import ModeTarget

from GameData import MerchantData
from FDGUI import Minimap


class Merchant( BigWorld.Entity, ModeTarget ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.cancelTradePot = None


	def prerequisites( self ):
		'''This is called by BigWorld when the Entity
		is about to enter the world.  We return a list of
		our prerequisite resources; these will get loaded by
		BigWorld in the background thread for us, before
		EnterWorld is called.
		'''
		return AvatarModel.getPrerequisites( AvatarModel.unpack( MerchantData.AVATAR_MODEL_DATA ) )


	def onEnterWorld( self, prereqs ):
		'''This is called by BigWorld when the Entity
		enters AOI, through creation or movement.
		'''

		self.filter = BigWorld.AvatarDropFilter()
		self.targetCaps  = [ Caps.CAP_CAN_USE ]
		self.overheadGui = None
		Minimap.addEntity( self )

		try:
			self.model  = AvatarModel.create( AvatarModel.unpack( MerchantData.AVATAR_MODEL_DATA ), BigWorld.Model('') )
			self.focalMatrix = self.model.node('biped Head')
		except Exception, e:
			print 'Error: could not load merchant model'
			print e
			self.model = BigWorld.Model('helpers/props/standin.model')

		if( ModeTarget._isModeTargetReady(self) == False ):
			ModeTarget._waitForModeTarget( self )

		self.cancelTradePot = BigWorld.addPot(	self.model.matrix,
												self.cancelTradeRadius,
												self.onCancelTradePot )


	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		'''This is called by BigWorld when the Entity
		leaves AOI, through destruction or movement.
		'''
		self.model = None
		if self.cancelTradePot is not None:
			BigWorld.delPot( self.cancelTradePot )
			self.cancelTradePot = None


	def onCancelTradePot( self, enter, potId ):
		if enter == False and \
				isinstance( BigWorld.player(), Avatar.PlayerAvatar ) and \
				BigWorld.player().mode == AvatarMode.COMMERCE:
			BigWorld.player().commerceCancel()


	def use( self ):
		'''Player wants to use this Merchant.
		'''
		if Caps.CAP_CAN_USE in self.targetCaps:
			BigWorld.player().onCommerceKey( True, self )


	def modeTargetFocus( self, avatar ):
		'''This Merchant is now focus of the player mode's target.
		'''
		if avatar == BigWorld.player():
			FantasyDemo.rds.fdgui.targetGui.source = self.model.bounds


	def modeTargetBlur( self, avatar ):
		'''This Merchant is no longer focus of the player's mode target.
		'''
		if avatar == BigWorld.player():
			FantasyDemo.rds.fdgui.targetGui.source = None


	def tradeAnimateAccept( self ):
		'''Plays the trade accept animation on this NPC.
		'''
		self.model.Shake_B_Extend().Shake_B_Accept()


	def disagree( self ):
		'''Plays the disagree animation on this NPC
		'''
		self.model.Shrug()


	def name( self ):
		return "Merchant"

	def chat( self, message ):
		FantasyDemo.addChatMsg( self.id, message )

# Merchant.py
