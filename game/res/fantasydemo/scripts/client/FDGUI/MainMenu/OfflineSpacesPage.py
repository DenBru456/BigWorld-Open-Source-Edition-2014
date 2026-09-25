import FantasyDemo

from TextListPage import TextListPage
from functools import partial

class OfflineSpacesPage( TextListPage ):
	caption = "Offline Spaces"

	def populate( self ):
		spaces = FantasyDemo.enumOfflineSpaces()		
		for printName, name in spaces:
			self.addItem( printName, partial( self.selectSpace, name ) )
			
	def selectSpace( self, space ):
		message = 'Exploring offline space: %s...' % space
		self.menu.showProgressStatus( message )
		FantasyDemo.coExploreOfflineSpace( space ).run()
		