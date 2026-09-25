import BigWorld
import FantasyDemo

from TextListPage import TextListPage
from LanServersPage import LanServersPage
from OfflineSpacesPage import OfflineSpacesPage
from SettingsPage import SettingsPage
from ValueChooserPage import ValueChooserPage
from ConnectToServerPage import ConnectToServerPage
from ReplaySelectionPage import ReplaySelectionPage

from WeakMethod import WeakMethod

from MainMenuConstants import *

def getXMLServers():
	return FantasyDemo.rds.scriptsConfig.readStrings( 'login/host' )
	
def shouldConnectOnStartup():
	return FantasyDemo.rds.scriptsConfig.readBool( 'login/connectOnStartup', False )

class RootPage( TextListPage ):
	caption = "Main Menu"
		
	def pageActivated( self, reason, outgoing ):
		TextListPage.pageActivated( self, reason, outgoing )
		if reason == REASON_PUSHING and shouldConnectOnStartup():
			self.menu.pop() # Get rid of this root menu so they can't get back.
			self.xmlServerSelected( getXMLServers()[0] )
	
	def populate( self ):
		# Don't let them into the game if we need to restart the client
		if BigWorld.graphicsSettingsNeedRestart():
			self.addItem( 'New settings require a restart', None )
		else:
			self.addItem( 'Connect to Standard Server...', WeakMethod( self.selectXmlServers ) )
			self.addItem( 'Search for Servers on Local Network...', WeakMethod( self.selectLanServers ) )
			self.addItem( 'Explore Space Offline...', WeakMethod( self.selectOfflineSpaces ) )
			if FantasyDemo.rds.scriptsConfig.readString( "replay/host" ):
				self.addItem( 'Replay a Recording...', WeakMethod( self.selectReplay ) )
		self.addItem( 'Change Display Settings...', WeakMethod( self.selectSettings ) )
		
		if BigWorld.graphicsSettingsNeedRestart():
			self.addItem( 'Restart', WeakMethod( BigWorld.restartGame) )
		
		self.addItem( 'Quit', WeakMethod( self.selectQuit ) )
		
	def selectXmlServers( self ):
		xmlServers = getXMLServers()
		items = [ (host, host) for host in xmlServers ]
		page = ValueChooserPage( self.menu, items, 0, self.xmlServerSelected, "Connect To Server" )
		self.menu.push( page )
		
	def xmlServerSelected( self, host ):
		self.menu.push( ConnectToServerPage( self.menu, host, host ) )
		
	def selectLanServers( self ):
		self.menu.push( LanServersPage(self.menu) )
		
	def selectOfflineSpaces( self ):
		self.menu.push( OfflineSpacesPage(self.menu) )
		
	def selectSettings( self ):
		self.menu.push( SettingsPage(self.menu) )
		
	def selectReplay( self ):
		self.menu.push( ReplaySelectionPage( self.menu ) )
		
	def selectQuit( self ):
		FantasyDemo.quitGame()
