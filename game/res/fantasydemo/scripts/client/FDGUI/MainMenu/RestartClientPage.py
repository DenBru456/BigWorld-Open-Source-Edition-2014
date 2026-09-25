import BigWorld

from TextListPage import TextListPage
from functools import partial

class RestartClientPage( TextListPage ):
	caption = "Restart Required"
	enableBackButton = False
	

	def __init__( self, menu, msg, restartLaterCB ):
		TextListPage.__init__( self, menu, 1 )
		self.restartMessage = msg
		self.restartLaterCB = restartLaterCB
		
		
	def populate( self ):
		self.addItem( self.restartMessage, None )
		self.addItem( 'Restart Now', BigWorld.restartGame )
		self.addItem( 'Restart Later', self.onRestartLater )
		
	def onRestartLater( self ):
		self.menu.pop()
		if self.restartLaterCB is not None:
			self.restartLaterCB()
	
	def onBack( self ):
		return False # Force the user to make a selection, no back button.
