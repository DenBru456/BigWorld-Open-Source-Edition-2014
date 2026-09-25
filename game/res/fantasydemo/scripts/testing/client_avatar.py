
import os
import sys
import unittest

# add to python path
bw_res_path = os.environ[ 'BW_RES_PATH' ]
paths = bw_res_path.split( ';' )
for path in paths:
	sys.path.append( r'%s\entities\client' % path  )
	sys.path.append( r'%s\entities\common' % path  )
	sys.path.append( r'%s\entities\testing\bwstubs' % path  )

import BigWorld
import GUI
import client.Avatar as Avatar
import client.Merchant as Merchant
import common.AvatarMode as AvatarMode
import Inventory


class CellStub:

	REPLY_ACTIONS = (
		COUNT,
		DENY,
		ACCEPT,
		FAIL ) = range(4)

	def __init__( self, client ):
		self.client = client
		self.requestReply  = CellStub.COUNT
		self.requestCount  = False
		self.offerReply    = CellStub.COUNT
		self.offerCount    = False
		self.cancelCount   = 0
		self.unlockReply   = CellStub.COUNT
		self.unlockCount   = 0
		self.commerceReply = CellStub.COUNT
		self.commerceCount = 0
		self.sellReply     = CellStub.COUNT
		self.sellCount     = 0
		self.buyReply     = CellStub.COUNT
		self.buyCount     = 0

	def setRightHand( self, *args ):
		pass

	def didGesture( self, *args ):
		pass

	def tradeStartRequest( self, partnerID ):
		if self.requestReply == CellStub.COUNT:
			self.requestCount += 1
		elif self.requestReply == CellStub.DENY:
			self.client.tradeDeny()

	def tradeCancelRequest( self ):
		self.cancelCount += 1

	def tradeOfferItemRequest( self, itemsLock, itemSerial ):
		if self.offerReply == CellStub.COUNT:
			self.offerCount += 1
		elif self.offerReply == CellStub.DENY:
			self.client.tradeOfferItemDeny( itemsLock )
		elif self.offerReply == CellStub.ACCEPT:
			items, types, gold = self.client.inventoryMgr.itemsLockedRetrieve( itemsLock )
			self.client.tradeCommitNotify( True, itemsLock, items, gold, [9], [111], 0 )
		elif self.offerReply == CellStub.FAIL:
			self.client.tradeCommitNotify( False, itemsLock, [], 0, [], [], 0 )

	def itemsUnlockRequest( self, lockHandle ):
		if self.unlockReply == CellStub.COUNT:
			self.unlockCount += 1
		elif self.unlockReply == CellStub.DENY:
			self.client.itemsUnlockNotify( False, lockHandle )
		elif self.unlockReply == CellStub.ACCEPT:
			self.client.itemsUnlockNotify( True, lockHandle )

	def commerceStartRequest( self, partnerID ):
		if self.commerceReply == CellStub.COUNT:
			self.commerceCount += 1
		elif self.commerceReply == CellStub.DENY:
			self.client.commerceStartDeny()

	def commerceSellRequest( self, itemsLock, itemSerial ):
		if self.sellReply == CellStub.COUNT:
			self.sellCount += 1
		elif self.sellReply == CellStub.DENY:
			self.client.tradeCommitNotify( False, itemsLock, [], 0, [], [], 0 )
		elif self.sellReply == CellStub.ACCEPT:
			items, types, gold = self.client.inventoryMgr.itemsLockedRetrieve( itemsLock )
			self.client.tradeCommitNotify( True, itemsLock, items, gold, [], [], 25 )

	def commerceBuyRequest( self, itemsLock, itemSerial ):
		if self.buyReply == CellStub.COUNT:
			self.buyCount += 1
		elif self.buyReply == CellStub.DENY:
			self.client.tradeCommitNotify( False, itemsLock, [], 0, [], [], 0 )
		elif self.buyReply == CellStub.ACCEPT:
			items, types, gold = self.client.inventoryMgr.itemsLockedRetrieve( itemsLock )
			self.client.tradeCommitNotify( True, itemsLock, items, gold, [6], [111], 0 )


class AvatarTest( unittest.TestCase ):

	def setUp( self ):
		self.avatar = Avatar.PlayerAvatar()
		BigWorld.test_setPlayer( self.avatar )

		self.partner = Avatar.Avatar()
		BigWorld.test_setTarget( self.partner )

		self.avatar._initInternalData()
		self.avatar._initMovementData()
		self.avatar._initCombatData()
		self.avatar._initTradeData()
		self.avatar.setUpMovementSpeedsFromModel()
		self.avatar._initInventoryGUI()
		self.avatar._initGuiStuff()
		self.avatar._initInventory()

		self.avatar.cell = CellStub( self.avatar )


	def testTradeRequestCount( self ):
		self.avatar.onTradeKey( True )
		self.assert_( self.avatar.doingAction )
		self.assert_( self.avatar.cell.requestCount == 1 )


	def testTradeRequestDeny( self ):
		self.avatar.cell.requestReply = CellStub.DENY
		self.avatar.onTradeKey( True )
		self.assert_( not self.avatar.doingAction )


	def _requestTradeMode( self ):
		self.avatar.cell.requestReply = CellStub.ACCEPT
		self.avatar.onTradeKey( True )


	def testTradeRequestAccept( self ):
		self._requestTradeMode()
		self.assert_( self.avatar.doingAction )


	def testTradeRequestCancel( self ):
		self._requestTradeMode()
		self.avatar.mode = AvatarMode.TRADE_PASSIVE
		self.avatar.onTradeKey( True )
		self.assert_( self.avatar.cell.cancelCount == 1 )


	def _enterTradeActive( self ):
		target = Avatar.Avatar()
		target.mode = AvatarMode.TRADE_PASSIVE
		BigWorld.entities = { 666 : target }
		self.avatar.modeTarget = 666
		self.avatar.mode = AvatarMode.TRADE_ACTIVE
		self.avatar.tradeActiveEnterMode()


	def testTradeOfferCount( self ):
		self._enterTradeActive()
		self.avatar.onTradeOfferItem( 13 )
		self.assert_( self.avatar.cell.offerCount == 1 )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( len( self.avatar.inventoryLocks ) == 1 )
		self.assert_(
			self.avatar.inventoryLocks[0][ "lockHandle" ] ==
			self.avatar.inventoryItems[1][ "lockHandle" ] )


	def testTradeOfferDeny( self ):
		self._enterTradeActive()
		self.avatar.cell.offerReply = CellStub.ACCEPT
		self.avatar.onTradeOfferItem( 15 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )


	def testTradeOfferFail( self ):
		self._enterTradeActive()
		self.avatar.cell.offerReply = CellStub.FAIL
		self.avatar.onTradeOfferItem( 666 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )


	def _offerItem( self ):
		self._enterTradeActive()
		self.avatar.onTradeOfferItem( 13 )


	def testOnUnlockItemCount( self ):
		self._offerItem()
		self.avatar.onUnlockItem( 1 )
		self.assert_( self.avatar.cell.unlockCount == 1 )


	def testOnUnlockItemDeny( self ):
		self._offerItem()
		self.avatar.cell.unlockReply = CellStub.DENY
		self.avatar.onUnlockItem( 1 )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( len( self.avatar.inventoryLocks ) == 1 )


	def testOnUnlockItemAccept( self ):
		self._offerItem()
		self.avatar.cell.unlockReply = CellStub.ACCEPT
		self.avatar.onUnlockItem( 1 )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )


	def testCommerceRequestWrongTarget( self ):
		BigWorld.test_setTarget( Avatar.Avatar() )
		self.avatar.onCommerceKey( True )
		self.assert_( self.avatar.cell.commerceCount == 0 )
		self.assert_( not self.avatar.doingAction )


	def testCommerceRequestCount( self ):
		merchant = Merchant.Merchant()
		BigWorld.test_setTarget( merchant )
		self.avatar.onCommerceKey( True )
		self.assert_( self.avatar.cell.commerceCount == 1 )
		self.assert_( self.avatar.modeTarget == merchant.id )
		self.assert_( self.avatar.doingAction )


	def testCommerceRequestDeny( self ):
		merchant = Merchant.Merchant()
		BigWorld.test_setTarget( merchant )
		self.avatar.cell.commerceReply = CellStub.DENY
		self.avatar.onCommerceKey( True )
		self.assert_( self.avatar.modeTarget == AvatarMode.NO_TARGET )
		self.assert_( not self.avatar.doingAction )


	def _commerceEnterMode( self ):
		itemsList = [4,6,9]
		self.avatar.mode = AvatarMode.COMMERCE
		merchant = Merchant.Merchant()
		merchant.overheadGui = None
		BigWorld.entities = { 666 : merchant }
		self.avatar.modeTarget = 666
		self.avatar.commerceEnterMode()
		self.avatar.commerceItemsNotify( itemsList )
		return itemsList


	def testCommerceItemsNotify( self ):
		itemsList = self._commerceEnterMode()
		self.assert_( self.avatar._commerceItems == itemsList )


	def testOnSellItemCount( self ):
		itemsList = self._commerceEnterMode()
		self.avatar.onSellItem( 13 )
		self.assert_( self.avatar.cell.sellCount == 1 )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( len( self.avatar.inventoryLocks ) == 1 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )


	def testOnSellItemError( self ):
		itemsList = self._commerceEnterMode()
		self.avatar.onSellItem( 666 )
		self.assert_( self.avatar.cell.sellCount == 0 )
		self.assert_( self.avatar.inventoryLocks == [] )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )


	def testOnSellItemDeny( self ):
		itemsList = self._commerceEnterMode()
		self.avatar.cell.sellReply = CellStub.DENY
		self.avatar.onSellItem( 13 )
		self.assert_( self.avatar._commerceItems == itemsList )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )


	def testOnSellItemAccept( self ):
		itemsList = self._commerceEnterMode()
		self.avatar.cell.sellReply = CellStub.ACCEPT
		self.avatar.onSellItem( 13 )
		self.assert_( self.avatar._commerceItems == [4,6,9,6] )
		self.assert_( len( self.avatar.inventoryItems ) == 2 )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 125 )


	def testOnBuyItemCount( self ):
		itemsList = self._commerceEnterMode()
		self.avatar.onBuyItem( 1 )
		self.assert_( self.avatar.cell.buyCount == 1 )
		self.assert_( self.avatar.inventoryLocks[0][ "goldPieces" ] > 0 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() < 100 )
		self.assert_( self.avatar._buyItemIndex == 1 )


	def testOnBuyItemError( self ):
		itemsList = self._commerceEnterMode()
		self.avatar.onBuyItem( 3 )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )
		self.assert_( self.avatar._buyItemIndex == None )


	def testOnBuyItemDeny( self ):
		itemsList = self._commerceEnterMode()
		self.avatar.cell.buyReply = CellStub.DENY
		self.avatar.onBuyItem( 1 )
		self.assert_( self.avatar._commerceItems == itemsList )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )
		self.assert_( self.avatar._buyItemIndex == None )


	def testOnBuyItemAccept( self ):
		itemsList = self._commerceEnterMode()
		self.avatar.cell.buyReply = CellStub.ACCEPT
		self.avatar.onBuyItem( 1 )
		self.assert_( self.avatar._commerceItems == [4,9] )
		self.assert_( len( self.avatar.inventoryItems ) == 4 )
		self.assert_( self.avatar.inventoryItems[3][ "itemType" ] == 6 )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() < 100 )
		self.assert_( self.avatar._buyItemIndex == None )


	def testItemsLockNotify( self ):
		self.avatar.itemsLockNotify( 10, [12, 15], 50 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] == 10 )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] == 10 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 50 )


	def testItemsLockNotifyTrue( self ):
		self.avatar.itemsLockNotify( 10, [12, 15], 50 )
		self.avatar.itemsUnlockNotify( True, 10 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )


	def testItemsLockNotifyFalse( self ):
		self.avatar.itemsLockNotify( 10, [12, 15], 50 )
		self.avatar.itemsUnlockNotify( False, 10 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] == 10 )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] == 10 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 50 )


if __name__ == '__main__':
    unittest.main()
