import Avatar
import BigWorld
import Cursor
import InventoryWindow



class TraderWindow( InventoryWindow.InventoryWindow ):
	base = InventoryWindow.InventoryWindow
	factoryString="FDGUI.TraderWindow"

	def __init__( self, component ):
		TraderWindow.base.__init__( self, component )
		self.inventoryItems = None

	def __str__( self ):
		return "TraderWindow(%s)" % self.inventoryMgr

	def onSave( self, dataSection ):
		TraderWindow.base.onSave( self, dataSection )
		pass


	def onLoad( self, dataSection ):
		TraderWindow.base.onLoad( self, dataSection )
		pass


	def handleDropEvent( self, comp, dropped ):
		if not isinstance( dropped.script, InventoryWindow.InventorySlot ):
			return False

		inventoryWindow = dropped.parent.script
		if inventoryWindow and inventoryWindow.inventoryMgr:
			inventoryWindow.inventoryMgr._entity.onSellItem( dropped.script.item['serial'] )
			return True

		return False


	def onCloseBoxClick( self ):

		if isinstance( BigWorld.player(), Avatar.PlayerAvatar ):
			BigWorld.player().commerceCancel()

		TraderWindow.base.onCloseBoxClick( self )


	def active( self, show ):
		if self.isActive == show:
			return

		TraderWindow.base.active( self, show )
		Cursor.showCursor( show )


	def updateInventory( self, inventoryItems, goldPieces = None ):
		TraderWindow.base.updateInventory( self, inventoryItems, goldPieces )


	@staticmethod
	def create( texture ):
		c = GUI.Window( texture )
		return TraderWindow( c ).component


# TraderWindow.py

