
import unittest
import common.Inventory as Inventory


class EntityStub:
	def __init__( self ):
		self.inventoryItems = [
			{ "itemType": 2, "serial": 12, "lockHandle": Inventory.NOLOCK }, 
			{ "itemType": 3, "serial": 13, "lockHandle": Inventory.NOLOCK },
			{ "itemType": 4, "serial": 15, "lockHandle": Inventory.NOLOCK } ]
		self.inventoryLocks = []
		self.inventoryGoldPieces  = 100


	def __str__( self ):
		return '%d | %s | %s' % (
			self.inventoryGoldPieces,
			self.inventoryItems,
			self.inventoryLocks )


class InventoryTest( unittest.TestCase ):

	def _initEntityInventory( self ):
		entity = EntityStub()
		inventory = Inventory.InventoryMgr( entity )
		return entity, inventory


	def setUp( self ):
		self.entity, self.inventory = self._initEntityInventory()
		

	def testAddSingleSerial( self ):
		serial = self.inventory.addItem( 4, 11 )
		self.assert_( len( self.entity.inventoryItems ) == 4 )
		self.assert_( serial == 11 )
		self.assert_( self.entity.inventoryItems[3][ "itemType" ] == 4 )
		self.assert_( self.entity.inventoryItems[3][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[3][ "serial" ] == serial )


	def testAddSingleNoSerial( self ):
		serial = self.inventory.addItem( 4 )
		self.assert_( len( self.entity.inventoryItems ) == 4 )
		self.assert_( serial == 16 )
		self.assert_( self.entity.inventoryItems[3][ "itemType" ] == 4 )
		self.assert_( self.entity.inventoryItems[3][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[3][ "serial" ] == serial )


	def testRemove( self ):
		item = self.inventory.removeItem( 13 )
		self.assert_( len( self.entity.inventoryItems ) == 2 )
		self.assert_( item == 3 )
		self.assert_( self.entity.inventoryItems[0][ "itemType" ] == 2 )
		self.assert_( self.entity.inventoryItems[0][ "serial" ] == 12 )
		self.assert_( self.entity.inventoryItems[1][ "itemType" ] == 4 )
		self.assert_( self.entity.inventoryItems[1][ "serial" ] == 15 )


	def testRemoveInvalid( self ):
		def remove():
			self.inventory.removeItem( 17 )
		self.assertRaises( ValueError, remove )
		self.assert_( len( self.entity.inventoryItems ) == 3 )


	def testSelect( self ):
		item = self.inventory.selectItem( 13 )
		self.assert_( item == 3 )
		self.assert_( self.inventory._curItemIndex == 1 )


	def testSelectInvalid( self ):
		def select():
			self.inventory.selectItem( 17 )
		self.assertRaises( ValueError, select )
		self.assert_( self.inventory._curItemIndex == Inventory.NOITEM )


	def testRemoveBeforeSelected( self ):
		self.inventory.selectItem( 13 )
		self.inventory.removeItem( 12 )
		self.assert_( self.inventory._curItemIndex == 0 )


	def testRemoveSelected( self ):
		self.inventory.selectItem( 13 )
		self.inventory.removeItem( 13 )
		self.assert_( self.inventory._curItemIndex == Inventory.NOITEM )


	def testLockSingle( self ):
		handle = self.inventory.itemsLock( [12], 25 )
		self.assert_( self.entity.inventoryItems[0][ "lockHandle" ] == handle )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( len( self.entity.inventoryLocks ) == 1 )
		self.assert_( self.entity.inventoryLocks[0][ "lockHandle" ] == handle )
		self.assert_( self.entity.inventoryLocks[0][ "goldPieces" ] == 25 )
		self.assert_( self.inventory.availableGoldPieces() == 75 )


	def testSelectLocked( self ):
		handle = self.inventory.itemsLock( [12], 0 )
		
		def select():
			self.inventory.selectItem( 12 )
		self.assertRaises( Inventory.LockError, select )
		self.assert_( self.inventory._curItemIndex == Inventory.NOITEM )


	def testRemoveLocked( self ):
		handle = self.inventory.itemsLock( [12], 0 )
		
		def remove():
			self.inventory.removeItem( 12 )
		self.assertRaises( Inventory.LockError, remove )
		self.assert_( len( self.entity.inventoryItems ) == 3 )


	def testLockList( self ):
		handle = self.inventory.itemsLock( [12, 15], 50 )
		self.assert_( self.entity.inventoryItems[0][ "lockHandle" ] == handle )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[2][ "lockHandle" ] == handle )
		self.assert_( len( self.entity.inventoryLocks ) == 1 )
		self.assert_( self.entity.inventoryLocks[0][ "lockHandle" ] == handle )
		self.assert_( self.entity.inventoryLocks[0][ "goldPieces" ] == 50 )
		self.assert_( self.inventory.availableGoldPieces() == 50 )


	def testLockEmpty( self ):
		handle = self.inventory.itemsLock( [], 50 )
		self.assert_( self.entity.inventoryItems[0][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( len( self.entity.inventoryLocks ) == 1 )
		self.assert_( self.entity.inventoryLocks[0][ "lockHandle" ] == handle )
		self.assert_( self.entity.inventoryLocks[0][ "goldPieces" ] == 50 )
		self.assert_( self.inventory.availableGoldPieces() == 50 )


	def testRelock( self ):
		self.inventory.itemsRelock( 10, [15, 12], 25 )
		self.assert_( self.entity.inventoryItems[0][ "lockHandle" ] == 10 )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[2][ "lockHandle" ] == 10 )
		self.assert_( len( self.entity.inventoryLocks ) == 1 )
		self.assert_( self.entity.inventoryLocks[0][ "lockHandle" ] == 10 )
		self.assert_( self.entity.inventoryLocks[0][ "goldPieces" ] == 25 )
		self.assert_( self.inventory.availableGoldPieces() == 75 )


	def testRelockMultiple( self ):
		self.inventory.itemsRelock( 10, [13], 22 )
		self.inventory.itemsRelock( 11, [15, 12], 28 )
		self.assert_( self.entity.inventoryItems[0][ "lockHandle" ] == 11 )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == 10 )
		self.assert_( self.entity.inventoryItems[2][ "lockHandle" ] == 11 )
		self.assert_( len( self.entity.inventoryLocks ) == 2 )
		self.assert_( self.entity.inventoryLocks[0][ "lockHandle" ] == 10 )
		self.assert_( self.entity.inventoryLocks[0][ "goldPieces" ] == 22 )
		self.assert_( self.entity.inventoryLocks[1][ "lockHandle" ] == 11 )
		self.assert_( self.entity.inventoryLocks[1][ "goldPieces" ] == 28 )
		self.assert_( self.inventory.availableGoldPieces() == 50 )


	def testRelockFailExists( self ):
		self.inventory.itemsRelock( 10, [12, 15], 25 )
		def relock():
			self.inventory.itemsRelock( 10, [13], 25 )
		self.assertRaises( Inventory.LockError, relock )
		

	def testRelockFailGold( self ):
		def relock():
			self.inventory.itemsRelock( 10, [13], 125 )
		self.assertRaises( Inventory.LockError, relock )


	def testRelockFailInvalid( self ):
		def relock():
			self.inventory.itemsRelock( 10, [13, 16], 125 )
		self.assertRaises( Inventory.LockError, relock )


	def testRelockFailLocked( self ):
		self.inventory.itemsRelock( 10, [13, 12], 25 )
		def relock():
			self.inventory.itemsRelock( 11, [15, 13], 25 )
		self.assertRaises( Inventory.LockError, relock )


	def testUnlock( self ):
		handle1 = self.inventory.itemsLock( [13], 23 )
		handle2 = self.inventory.itemsLock( [15], 27 )
		self.inventory.itemsUnlock( handle1 )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( len( self.entity.inventoryLocks ) == 1 )
		self.assert_( self.entity.inventoryLocks[0][ "lockHandle" ] == handle2 )
		self.assert_( self.inventory.availableGoldPieces() == 73 )


	def testUnlockError( self ):
		handle1 = self.inventory.itemsLock( [12, 15], 23 )
		def unlock():
			self.inventory.itemsUnlock( 13 )
		self.failUnlessRaises( Inventory.LockError, unlock )


	def testLockedRetrieve( self ):
		handle = self.inventory.itemsLock( [15, 12], 25 )
		lockEntry = self.inventory.itemsLockedRetrieve( handle )		
		self.assert_( lockEntry == ( [12, 15], [2, 4], 25 ))


	def testLockedRetrieveError( self ):
		handle = self.inventory.itemsLock( [15, 12], 25 )
		def retrieve():
			lockEntry = self.inventory.itemsLockedRetrieve( handle + 1 )		
		self.failUnlessRaises( Inventory.LockError, retrieve )


	def testTradeNoSerial( self ):
		handle = self.inventory.itemsLock( [15, 12], 25 )
		serials = self.inventory.itemsTrade( [15, 12], 25, [5, 6], [], 100, 123123 )
		self.assert_( len( self.entity.inventoryLocks ) == 0 )
		self.assert_( len( self.entity.inventoryItems ) == 3 )
		self.assert_( self.entity.inventoryItems[0][ "itemType" ] == 3 )
		self.assert_( self.entity.inventoryItems[1][ "itemType" ] == 5 )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[1][ "serial" ] == serials[0] )
		self.assert_( self.entity.inventoryItems[2][ "itemType" ] == 6 )
		self.assert_( self.entity.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[2][ "serial" ] == serials[1] )
		self.assert_( self.entity.inventoryGoldPieces == 175 )


	def testTradeSerial( self ):
		handle = self.inventory.itemsLock( [15, 12], 25 )
		serials = self.inventory.itemsTrade( [15, 12], 25, [5, 6], [111, 222], 100, 123123 )
		self.assert_( serials == [111, 222] )
		self.assert_( len( self.entity.inventoryLocks ) == 0 )
		self.assert_( len( self.entity.inventoryItems ) == 3 )
		self.assert_( self.entity.inventoryItems[0][ "itemType" ] == 3 )
		self.assert_( self.entity.inventoryItems[1][ "itemType" ] == 5 )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[1][ "serial" ] == serials[0] )
		self.assert_( self.entity.inventoryItems[2][ "itemType" ] == 6 )
		self.assert_( self.entity.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[2][ "serial" ] == serials[1] )
		self.assert_( self.entity.inventoryGoldPieces == 175 )


	def testTradePartial( self ):
		handle = self.inventory.itemsLock( [15, 12], 25 )
		self.inventory.itemsTrade( [15], 25, [5, 6], [], 100 )
		self.assert_( len( self.entity.inventoryLocks ) == 0 )
		self.assert_( len( self.entity.inventoryItems ) == 4 )
		self.assert_( self.entity.inventoryItems[0][ "itemType" ] == 2 )
		self.assert_( self.entity.inventoryItems[0][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[0][ "serial" ] == 12 )
		self.assert_( self.entity.inventoryItems[1][ "itemType" ] == 3 )
		self.assert_( self.entity.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[1][ "serial" ] == 13 )
		self.assert_( self.entity.inventoryItems[2][ "itemType" ] == 5 )
		self.assert_( self.entity.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[2][ "serial" ] == 16 )
		self.assert_( self.entity.inventoryItems[3][ "itemType" ] == 6 )
		self.assert_( self.entity.inventoryItems[3][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[3][ "serial" ] == 17 )
		self.assert_( self.entity.inventoryGoldPieces == 175 )


	def testTradeBuy( self ):
		handle = self.inventory.itemsLock( [], 33 )
		self.inventory.itemsTrade( [], 33, [5, 6], [], 0, handle )
		self.assert_( len( self.entity.inventoryLocks ) == 0 )
		self.assert_( len( self.entity.inventoryItems ) == 5 )
		self.assert_( self.entity.inventoryItems[3][ "itemType" ] == 5 )
		self.assert_( self.entity.inventoryItems[3][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[3][ "serial" ] == 16 )
		self.assert_( self.entity.inventoryItems[4][ "itemType" ] == 6 )
		self.assert_( self.entity.inventoryItems[4][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.entity.inventoryItems[4][ "serial" ] == 17 )
		self.assert_( self.entity.inventoryGoldPieces == 67 )


	def testTradeSell( self ):
		handle = self.inventory.itemsLock( [15, 13], 0 )
		self.inventory.itemsTrade( [15, 13], 0, [], [], 33 )
		self.assert_( len( self.entity.inventoryLocks ) == 0 )
		self.assert_( len( self.entity.inventoryItems ) == 1 )
		self.assert_( self.entity.inventoryItems[0][ "itemType" ] == 2 )
		self.assert_( self.entity.inventoryGoldPieces == 133 )


	def testTradeError( self ):
		handle = self.inventory.itemsLock( [15], 0 )
		def trade():
			self.inventory.itemsTrade( [16], 0, [5, 6], [], 100, handle )
		self.failUnlessRaises( ValueError, trade )
		self.assert_( len( self.entity.inventoryLocks ) == 1 )
		self.assert_( len( self.entity.inventoryItems ) == 3 )
		self.assert_( len( self.entity.inventoryItems ) == 3 )


if __name__ == '__main__':
    unittest.main()
