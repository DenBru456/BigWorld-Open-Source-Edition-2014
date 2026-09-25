import weakref

from MainMenuConstants import *

class Page( object ):
	caption = None
	
	def __init__( self, menu ):
		try:
			self.menu = weakref.proxy( menu )
		except TypeError:
			self.menu = menu
		
	@property
	def visible( self ):
		raise NotImplementedError, "You should implement the visible getter"
		
	@visible.setter
	def visible( self, visible ):
		raise NotImplementedError, "You should implement the visible setter"
		
	def mouseScroll( self, amt ):
		pass
	
	def pageActivated( self, reason, outgoing ):
		pass
		
	def pageDeactivated( self, reason, incoming ):
		# NOTE: If you override this method, call this base class at the END
		# of the derived method (i.e. it should be the last operation performed), 
		# otherwise things may get out of order.
		if reason == REASON_POPPING:
			#print "popping", self
			self.menu.stack.pop()
			
		if incoming is not None:
			if reason == REASON_PUSHING:
				#print "pushing", incoming, reason
				self.menu.stack.append( incoming )
			self.menu._activatePage( incoming, reason, self )
		
		
		
	def isActive( self ):
		return len(self.menu.stack) > 0 and self.menu.top() is self
		
