import BigWorld
import FantasyDemo

from TextListPage import TextListPage
from MainMenuConstants import *
from functools import partial
import ReplayHandler

import json
from urllib import urlencode

FETCH_TIMEOUT = 5.0


class ReplaySelectionPage( TextListPage ):
	"""
	This page queries a replay server and displays options for replaying
	recordings.
	"""
	

	def __init__( self, component = None ):
		""" Constructor. """
		TextListPage.__init__( self, component )
		self._files = []
		self._host = FantasyDemo.rds.scriptsConfig.readString( "replay/host" )
		
		
	def pageActivated( self, reason, outgoing ):
		""" Override from TextListPage. """
		TextListPage.pageActivated( self, reason, outgoing )
		
		if self._host:
			url = "http://" + self._host + "/replays" + "?" + \
				urlencode( [('version', BigWorld.protocolVersion), 
					('digest', BigWorld.digest)] )
			self.menu.showProgressStatus( 
				'Querying server for available recordings...' )
			BigWorld.fetchURL( url, self.onURLFetched, [], FETCH_TIMEOUT, 
				"GET" )
		else:
			def onEscape():
				self.menu.clearStatus()
				self.menu.pop()
			self.menu.showPromptStatus( 'No replay server URL configured',
				onEscape )
		
		
	def onURLFetched( self, response ):
		"""
		Call back function from URL request.
		"""
		try:
			if response.responseCode != 200:
				raise ValueError( "Invalid response code" )
				
			self._files = json.loads( response.body )
			self._files.sort( lambda x, y: cmp( x['mtime'], y['mtime'] ) )
			self.menu.clearStatus()
			self.repopulate()
		except Exception as e:
			def onEscape():
				self.menu.clearStatus()
				self.menu.pop()
			self.menu.showPromptStatus( 
				'Got bad response from replay server: %s' % e,
				onEscape )

				
	def populate( self ):
		""" Override from TextListPage. """

		TextListPage.populate( self )
		
		for file in self._files:
			url = "http://" + self._host + "/replays/" + file['path']
			self.addItem( file['path'], 
				partial( self.onSelectRecording, url ) )


	def onSelectRecording( self, url ):
		""" Callback when a recording is selected. """
		self.menu.showProgressStatus( "Loading replay..." )
		ReplayHandler.coPlayRecording( url ).run()
		
	
	
