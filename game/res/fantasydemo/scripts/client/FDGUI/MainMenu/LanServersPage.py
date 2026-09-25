import BigWorld
import FantasyDemo

import Util

from TextListPage import TextListPage
from ConnectToServerPage import ConnectToServerPage
from MainMenuConstants import *


from functools import partial



SEARCH_TIMEOUT = 5.0

class LanServersPage( TextListPage ):
	caption = "LAN Servers"

	def __init__( self, menu ):		
		TextListPage.__init__( self, menu )		
		self.serverList = []

	def pageActivated( self, reason, outgoing ):
		TextListPage.pageActivated( self, reason, outgoing )
			
		# Don't let the user press escape on this status page
		self.menu.showProgressStatus( 'Searching for servers on local network...' )
		
		BigWorld.serverDiscovery.searching = True
		BigWorld.serverDiscovery.changeNotifier = self.serversDiscovered
		BigWorld.callback( SEARCH_TIMEOUT, self.noServersFound )
		
	def pageDeactivated( self, reason, incoming ):
		BigWorld.serverDiscovery.searching = False
		BigWorld.serverDiscovery.changeNotifier = None
		TextListPage.pageDeactivated( self, reason, incoming )
		
	def populate( self ):
		for i, (label, host) in enumerate(self.serverList):
			self.addItem( label, partial( self.serverSelected, host, label, i ) )
			
	def serversDiscovered( self ):	
		lastUsedServerUID = FantasyDemo.rds.userPreferences.readInt( 'lastServer/uid' )
		
		self.menu.clearStatus()
		
		self.serverList = [
			(Util.serverNiceName(server), Util.serverNetName(server))
			for server in BigWorld.serverDiscovery.servers if server.uid == lastUsedServerUID ]

		self.serverList = self.serverList + [
			(Util.serverNiceName(server), Util.serverNetName(server))
			for server in BigWorld.serverDiscovery.servers if server.uid != lastUsedServerUID ]
		
		self.repopulate()
		self.selectItem(0)
		
	def noServersFound( self ):
		sd = BigWorld.serverDiscovery
		if sd.searching and len(sd.servers) == 0:
			sd.searching = False			
			
			def onEscape():
				self.menu.clearStatus()
				self.menu.pop()
			self.menu.showPromptStatus( 'No servers found on local network', onEscape )
			
	def serverSelected( self, host, label, index ):
		self.menu.push( ConnectToServerPage( self.menu, host, label ) )
		
		
		
		
		