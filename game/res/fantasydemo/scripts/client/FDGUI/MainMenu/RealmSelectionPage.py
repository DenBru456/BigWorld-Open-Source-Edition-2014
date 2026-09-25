import BigWorld
import FantasyDemo
import Account

from GameData import FantasyDemoData
from TextListPage import TextListPage

from CharacterSelectionPage import CharacterSelectionPage
from MainMenuConstants import *
from Helpers.BWCoroutine import *

from functools import partial

class RealmSelectionPage( TextListPage ):
	caption = "Select Realm"

	def populate( self ):
		for realm in FantasyDemoData.REALMS.values():
			self.addItem( realm.displayName, self.coSelectRealm( realm.name ).run )
		
	def pageActivated( self, reason, outgoing ):
		TextListPage.pageActivated( self, reason, outgoing )
		if reason == REASON_PUSHING and len( FantasyDemoData.REALMS ) == 1:
			self.menu.pop()
			self.coSelectRealm( FantasyDemoData.REALMS.keys()[0] ).run()
			
	def onBack( self ):
		FantasyDemo.disconnectFromServer()
		return False
		
	@BWMemberCoroutine
	def coSelectRealm( self, realmName ):
		assert isinstance( BigWorld.player(), Account.Account )
		
		self.menu.showProgressStatus( 'Waiting for Character List...' )		
		BigWorld.player().base.selectRealm( realmName )
		
		try:
			yield BWWaitForCondition( lambda: BigWorld.player().selectedRealm == realmName, timeout = 120 )
		except BWCoroutineTimeoutException, e:
			FantasyDemo.disconnectFromServer()
			return

		self.menu.push( CharacterSelectionPage( self.menu ) )
		
	