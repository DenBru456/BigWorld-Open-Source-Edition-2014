
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
import base.Avatar as Avatar
import base.Merchant as Merchant
import common.AvatarMode as AvatarMode
import common.Inventory as Inventory


class CellStub:
	
	REPLY_ACTIONS = (
		COUNT,
		DENY,
		ACCEPT,
		FAIL ) = range(4)

	def __init__( self ):
		self.lockItemSuccess = 0
		self.lockItemFail = 0
		self.failCount = 0
		self.unlockCount = 0
		self.unlockDenyCount = 0
	
	def itemsLockNotify( self, success, itemsLock, itemsSerials, itemsTypes, goldPieces ):
		if success:
			self.lockItemSuccess += 1
		else:
			self.lockItemFail += 1
				
	def tradeCommitNotify( self, success, outItemsLock = 0, 
			outItemsSerials = [], outGoldPieces = 0, 
			inItemsTypes = [], inItemsSerials = [], inGoldPieces = 0 ):
		if success:
			pass
		else:
			self.failCount += 1

	def itemsUnlockNotify( self, success, lockHandle ):
		if success:
			self.unlockCount += 1
		else:
			self.unlockDenyCount += 1


class BaseAvatarStub:
	def __init__( self ):
		self.syncCount = 0
		self.failCount = 0
		self.syncFailCount = 0
	
	def tradeSyncRequest( self, partnerBase, partnerTradeParams ):
		self.syncCount += 1

	def tradeCommitNotify( self, success, outItemsLock = 0, 
			outItemsSerials = [], outGoldPieces = 0,
			inItemsTypes = [], inItemsSerials = [], inGoldPieces = 0 ):
		if success:
			pass
		else:
			self.failCount += 1

	def tradeSyncFail( self ):
		self.syncFailCount += 1

	def tradeCommit( self, base, tradeIDA, lockHandle, itemsSerialsA, outGoldPieces, itemsTypesB, goldPiecesB ):
		pass

	def writeToDB( self, callback = None ):
		if callback:
			callback()


class TradingSuperStub:
	def __init__( self ):
		self.commenceReply = CellStub.COUNT
		self.commenceCount = 0
		self.completeCount = 0
		self.pendingReply  = CellStub.ACCEPT
	
	def commenceTrade( self, A, tradeParamsA, B, tradeParamsB ):
		if self.commenceReply == CellStub.COUNT:
			self.commenceCount += 1
			return True
		elif self.commenceReply == CellStub.FAIL:
			return False
		elif self.commenceReply == CellStub.ACCEPT:
			A.tradeCommit( self, tradeParamsA[ "tradeID" ], 
							tradeParamsA[ "lockHandle" ], 
							tradeParamsA[ "itemsSerials" ], 
							tradeParamsA[ "goldPieces" ], 
							tradeParamsB[ "itemsTypes" ], 
							tradeParamsB[ "goldPieces" ] )
			B.tradeCommit( self, tradeParamsB[ "tradeID" ], 
							tradeParamsB[ "lockHandle" ], 
							tradeParamsB[ "itemsSerials" ], 
							tradeParamsB[ "goldPieces" ], 
							tradeParamsA[ "itemsTypes" ], 
							tradeParamsA[ "goldPieces" ] )
			return True

	def completeTrade( self, base, tradeID ):
		self.completeCount += 1


	def isAPendingTrade( self, id, lockHandle ):
		return self.pendingReply != CellStub.ACCEPT


class AvatarTest( unittest.TestCase ):

	def setUp( self ):
		self.avatar = Avatar.Avatar()
		self.supervisor = TradingSuperStub()
		BigWorld.globalBases = { 'TradingSupervisor' : self.supervisor }
				
		self.avatar.cell = CellStub()


	def lockRequest( self ):
		lockHandle = 1
		self.avatar.itemsLockRequest( lockHandle, [12, 15], 25 )
		return lockHandle


	def testTradeRequest( self ):
		self.lockRequest()
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( len( self.avatar.inventoryLocks ) == 1 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 75 )
		self.assert_( self.avatar.cell.lockItemSuccess == 1 )
		self.assert_( self.avatar.cell.lockItemFail == 0 )


	def testTradeFailGold( self ):
		self.avatar.itemsLockRequest( 1, [12, 15], 125 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryLocks == [] )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )
		self.assert_( self.avatar.cell.lockItemSuccess == 0 )
		self.assert_( self.avatar.cell.lockItemFail == 1 )


	def testTradeFailItemIndex( self ):
		self.avatar.itemsLockRequest( 1, [15, 33], 25 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryLocks == [] )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )
		self.assert_( self.avatar.cell.lockItemSuccess == 0 )
		self.assert_( self.avatar.cell.lockItemFail == 1 )


	def _tradeCommitActive( self ):
		lockHandle = self.lockRequest()
		self.avatar.tradeCommitActive( lockHandle )
		return lockHandle


	def testTradeCommitPassive( self ):
		lockHandle = self._tradeCommitActive()
		activeBase = BaseAvatarStub()
		self.avatar.tradeCommitPassive( lockHandle, activeBase )
		self.assert_( activeBase.syncCount == 1 )
		

	def testTradeCommitPassiveFail( self ):
		lockHandle = self._tradeCommitActive()
		activeBase = BaseAvatarStub()
		self.avatar.tradeCommitPassive( lockHandle + 1, activeBase )
		self.assert_( activeBase.syncCount == 0 )
		self.assert_( activeBase.syncFailCount == 1 )
		self.assert_( self.avatar.cell.failCount == 1 )


	def testTradeSyncCount( self ):
		self._tradeCommitActive()
		activeBase = BaseAvatarStub()
		tradeParams = { "dbID": 0, \
						"tradeID": 0, \
						"lockHandle": -1, \
						"itemsSerials": [3,4,5], \
						"itemsTypes": [9, 9, 9], \
						"goldPieces": 66 }
		self.avatar.tradeSyncRequest( activeBase, tradeParams )
		self.assert_( self.supervisor.commenceCount == 1 )
		self.assert_( self.supervisor.completeCount == 0 )


	def testTradeSyncFail( self ):
		self._tradeCommitActive()
		activeBase = BaseAvatarStub()
		self.supervisor.commenceReply = CellStub.FAIL
		tradeParams = { "dbID": 0, \
						"tradeID": 0, \
						"lockHandle": -1, \
						"itemsSerials": [3,4,5], \
						"itemsTypes": [9, 9, 9], \
						"goldPieces": 66 }
		self.avatar.tradeSyncRequest( activeBase, tradeParams )
		self.assert_( self.supervisor.commenceCount == 0 )
		self.assert_( self.supervisor.completeCount == 0 )
		self.assert_( activeBase.failCount == 1 )
		self.assert_( self.avatar.cell.failCount == 1 )


	def testTradeSyncAccept( self ):
		self._tradeCommitActive()
		activeBase = BaseAvatarStub()
		self.supervisor.commenceReply = CellStub.ACCEPT
		tradeParams = { "dbID": 0, \
						"tradeID": 0, \
						"lockHandle": -1, \
						"itemsSerials": [3,4,5], \
						"itemsTypes": [9, 9, 9], \
						"goldPieces": 66 }
		self.avatar.tradeSyncRequest( activeBase, tradeParams )
		self.assert_( self.supervisor.commenceCount == 0 )
		self.assert_( self.supervisor.completeCount == 1 )
		self.assert_( activeBase.failCount == 0 )
		self.assert_( self.avatar.cell.failCount == 0 )
		self.assert_( len( self.avatar.inventoryLocks ) == 0 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 141 )
		self.assert_( self.avatar.inventoryItems[0][ "itemType" ] == 6 )
		self.assert_( self.avatar.inventoryItems[1][ "itemType" ] == 9 )
		self.assert_( self.avatar.inventoryItems[2][ "itemType" ] == 9 )
		self.assert_( self.avatar.inventoryItems[3][ "itemType" ] == 9 )


	def testItemsUnlockRequestDeny( self ):
		lockHandle = self.lockRequest()
		self.supervisor.pendingReply = CellStub.DENY
		self.avatar.itemsUnlockRequest( lockHandle )
		self.assert_( self.avatar.cell.unlockDenyCount == 1 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 75 )


	def testItemsUnlockRequestAccept( self ):
		lockHandle = self.lockRequest()
		self.avatar.itemsUnlockRequest( lockHandle )
		self.assert_( self.avatar.cell.unlockCount == 1 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )


	def testItemsUnlockRequestAcceptExept( self ):
		lockHandle = self.lockRequest()
		self.avatar.itemsUnlockRequest( lockHandle + 1 )
		self.assert_( self.avatar.cell.unlockCount == 1 )
		self.assert_( self.avatar.inventoryItems[0][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[1][ "lockHandle" ] == Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryItems[2][ "lockHandle" ] != Inventory.NOLOCK )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 75 )


	def _prepareMerchant( self ):
		self.merchant = Merchant.Merchant()
		self.merchant.inventoryItems = [
			{ "itemType": 4, "serial": 12, "lockHandle": Inventory.NOLOCK }, 
			{ "itemType": 6, "serial": 13, "lockHandle": Inventory.NOLOCK },
			{ "itemType": 9, "serial": 15, "lockHandle": Inventory.NOLOCK } ]
		self.merchant.inventoryGoldPieces = 100


	def testCommerceSellFail( self ):
		self._prepareMerchant()
		self.supervisor.commenceReply = CellStub.ACCEPT
		self.avatar.commerceSellRequest( 1, 33, self.merchant )
		self.assert_( self.merchant.inventoryItems[0][ "itemType" ] == 4 )
		self.assert_( self.merchant.inventoryItems[1][ "itemType" ] == 6 )
		self.assert_( self.merchant.inventoryItems[2][ "itemType" ] == 9 )
		self.assert_( self.merchant.inventoryMgr.availableGoldPieces() == 100 )
		self.assert_( self.avatar.inventoryItems[0][ "itemType" ] == 4 )
		self.assert_( self.avatar.inventoryItems[1][ "itemType" ] == 6 )
		self.assert_( self.avatar.inventoryItems[2][ "itemType" ] == 4 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )


	def testCommerceSellRequestAccept( self ):
		self._prepareMerchant()
		self.supervisor.commenceReply = CellStub.ACCEPT
		self.avatar.commerceSellRequest( 1, 12, self.merchant )
		self.assert_( len( self.merchant.inventoryItems ) == 4 )
		self.assert_( self.merchant.inventoryItems[0][ "itemType" ] == 4 )
		self.assert_( self.merchant.inventoryItems[1][ "itemType" ] == 6 )
		self.assert_( self.merchant.inventoryItems[2][ "itemType" ] == 9 )
		self.assert_( self.merchant.inventoryItems[3][ "itemType" ] == 4 )
		self.assert_( self.merchant.inventoryMgr.availableGoldPieces() < 100 )
		self.assert_( len( self.avatar.inventoryItems ) == 2 )
		self.assert_( self.avatar.inventoryItems[0][ "itemType" ] == 6 )
		self.assert_( self.avatar.inventoryItems[1][ "itemType" ] == 4 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() > 100 )
		
		
	def testCommerceBuyRequestFail( self ):
		self._prepareMerchant()
		self.supervisor.commenceReply = CellStub.ACCEPT
		self.merchant.commerceSellRequest( 1, 3, self.avatar )
		self.assert_( len( self.merchant.inventoryItems ) == 3 )
		self.assert_( self.merchant.inventoryItems[0][ "itemType" ] == 4 )
		self.assert_( self.merchant.inventoryItems[1][ "itemType" ] == 6 )
		self.assert_( self.merchant.inventoryItems[2][ "itemType" ] == 9 )
		self.assert_( self.merchant.inventoryMgr.availableGoldPieces() == 100 )
		self.assert_( len( self.avatar.inventoryItems ) == 3 )
		self.assert_( self.avatar.inventoryItems[0][ "itemType" ] == 4 )
		self.assert_( self.avatar.inventoryItems[1][ "itemType" ] == 6 )
		self.assert_( self.avatar.inventoryItems[2][ "itemType" ] == 4 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() == 100 )


	def testCommerceBuyRequestAccept( self ):
		self._prepareMerchant()
		self.supervisor.commenceReply = CellStub.ACCEPT
		self.merchant.commerceSellRequest( 1, 2, self.avatar )
		self.assert_( len( self.merchant.inventoryItems ) == 2 )
		self.assert_( self.merchant.inventoryItems[0][ "itemType" ] == 4 )
		self.assert_( self.merchant.inventoryItems[1][ "itemType" ] == 6 )
		self.assert_( self.merchant.inventoryMgr.availableGoldPieces() > 100 )
		self.assert_( len( self.avatar.inventoryItems ) == 4 )
		self.assert_( self.avatar.inventoryItems[0][ "itemType" ] == 4 )
		self.assert_( self.avatar.inventoryItems[1][ "itemType" ] == 6 )
		self.assert_( self.avatar.inventoryItems[2][ "itemType" ] == 4 )
		self.assert_( self.avatar.inventoryItems[3][ "itemType" ] == 9 )
		self.assert_( self.avatar.inventoryMgr.availableGoldPieces() < 100 )


if __name__ == '__main__':
    unittest.main()
