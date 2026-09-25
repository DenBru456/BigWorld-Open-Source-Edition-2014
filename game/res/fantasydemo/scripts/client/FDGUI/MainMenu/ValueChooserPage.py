
from TextListPage import TextListPage
from functools import partial

class ValueChooserPage( TextListPage ):

	def __init__( self, menu, valueItems, initialSel, callback, caption=None ):
		TextListPage.__init__( self, menu, initialSel )
		self.valueItems = valueItems
		self.valueCallback = callback
		self.caption = caption
		
		
	def populate( self ):
		for desc, value in self.valueItems:
			self.addItem( desc, None if value is None else partial( self.valueSelected, value ) )
		
	def valueSelected( self, value ):
		self.menu.pop()
		self.valueCallback( value )
	