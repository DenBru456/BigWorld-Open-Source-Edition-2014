
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
import cell.Avatar as Avatar
import cell.Merchant as Merchant
import common.AvatarMode as AvatarMode


class ClientStub:

	REPLY_ACTIONS = (
		COUNT,
		DENY,
		ACCEPT,
		FAIL ) = range(4)

	def __init__( self ):
		self.denyCount = 0
		self.offerCount = 0
		self.offerDenyCount = 0
		self.commitSuccessCount = 0
		self.commitFailCount   = 0
		self.unlockDenyCount   = 0
		self.unlockCount       = 0
		self.commerceDenyCount = 0

	def tradeDeny( self ):
		self.denyCount += 1

	def tradeOfferItemNotify( self, itemsLock ):
		self.offerCount +=1

	def tradeOfferItemDeny( self, itemsLock ):
		self.offerDenyCount += 1

	def tradeAcceptNotify( self, accepted ):
		pass

	def tradeCommitNotify( self, success, outItemsLock, 
			outItemsSerials, outGoldPieces, 
			inItemsTypes, inItemsSerials, inGoldPieces ):
		if success:
			self.commitSuccessCount += 1
		else:
			self.commitFailCount += 1

	def itemsUnlockNotify( self, success, lockHandle ):
		if success:
			self.unlockCount += 1
		else:
			self.unlockDenyCount += 1
			
	def commerceStartDeny( self ):
		self.commerceDenyCount += 1


class BaseStub:
	def __init__( self, cell ):
		self.cell = cell
		self.requestCount = 0
		self.commitActiveReply = ClientStub.COUNT
		self.commitActiveCount = 0
		self.commitPassiveReply = ClientStub.COUNT
		self.commitPassiveCount = 0
		self.lockReply = ClientStub.COUNT
		self.unlockCount = 0
		self.sellCount   = 0

	def itemsLockRequest( self, itemsLock, itemsIndexes, goldPieces ):
		if self.lockReply == ClientStub.COUNT:
			self.requestCount += 1
		elif self.lockReply == ClientStub.DENY:
			self.cell.itemsLockNotify( False, itemsLock, [], [], 0 )
		elif self.lockReply == ClientStub.ACCEPT:
			self.cell.itemsLockNotify( True, itemsLock, [12], [4], goldPieces )

	def tradeCommitActive( self, outItemsLock ):
		if self.commitActiveReply == ClientStub.COUNT:
			self.commitActiveCount += 1
		elif self.commitActiveReply == ClientStub.DENY:
			self.cell.tradeCommitNotify( False, outItemsLock, [], 0, [], [], 0 )
		elif self.commitActiveReply == ClientStub.ACCEPT:
			self.cell.tradeCommitNotify( True, outItemsLock, [12], 30, [10], [111], 0 )

	def tradeCommitPassive( self, itemsLock, activeBase ):
		if self.commitPassiveReply == ClientStub.COUNT:
			self.commitPassiveCount += 1
		elif self.commitPassiveReply == ClientStub.DENY:
			self.cell.tradeCommitNotify( False, itemsLock, [], 0, [], [], 0 )
		elif self.commitPassiveReply == ClientStub.ACCEPT:
			self.cell.tradeCommitNotify( True, itemsLock, [10], 0, [12], [111], 30 )

	def itemsUnlockRequest( self, lockHandle ):
		self.unlockCount += 1

	def commerceSellRequest( self, itemLock, itemSerial, merchantBase ):
		self.sellCount += 1
		

class AvatarTest( unittest.TestCase ):

	def setUp( self ):
		self.avatar         = Avatar.Avatar()
		self.avatar.client  = ClientStub()
		self.avatar.base    = BaseStub( self.avatar )
		BigWorld.entities[ self.avatar.id ] = self.avatar

		self.partner        = Avatar.Avatar()
		self.partner.id     = 666
		self.partner.client = ClientStub()
		self.partner.base   = BaseStub( self.partner )
		BigWorld.entities[ self.partner.id ] = self.partner


	def testTradeStartDenyMode( self ):
		self.avatar.mode = AvatarMode.COMMERCE
		self.avatar.tradeStartRequest( self.avatar.id, self.partner.id )
		self.assert_( self.avatar.client.denyCount == 1 )
		self.assert_( self.avatar.modeTarget == AvatarMode.NO_TARGET )


	def testTradeStartDenyTarget( self ):
		self.avatar.tradeStartRequest( self.avatar.id, self.partner.id + 1 )
		self.assert_( self.avatar.client.denyCount == 1 )
		self.assert_( self.avatar.modeTarget == AvatarMode.NO_TARGET )
		self.assert_( self.avatar.mode == AvatarMode.NONE )


	def testTradeStartDenyTargetMode( self ):
		self.partner.mode = AvatarMode.TRADE_PASSIVE
		self.partner.modeTarget = 333
		self.avatar.tradeStartRequest( self.avatar.id, self.partner.id )
		self.assert_( self.avatar.client.denyCount == 1 )
		self.assert_( self.avatar.modeTarget == AvatarMode.NO_TARGET )
		self.assert_( self.avatar.mode == AvatarMode.NONE )


	def testTradeStartPassive( self ):
		self.partner.mode = AvatarMode.NONE
		self.avatar.tradeStartRequest( self.avatar.id, self.partner.id )
		self.assert_( self.avatar.client.denyCount == 0 )
		self.assert_( self.avatar.modeTarget == self.partner.id )
		self.assert_( self.avatar.mode == AvatarMode.TRADE_PASSIVE )


	def enterTradeActive( self ):
		self.partner.mode = AvatarMode.TRADE_PASSIVE
		self.partner.modeTarget = self.avatar.id
		self.avatar.tradeStartRequest( self.avatar.id, self.partner.id )


	def testTradeStartActive( self ):
		self.enterTradeActive()
		self.assert_( self.avatar.client.denyCount == 0 )
		self.assert_( self.avatar.modeTarget == self.partner.id )
		self.assert_( self.avatar.mode == AvatarMode.TRADE_ACTIVE )


	def testTradeCancel( self ):
		self.enterTradeActive()
		self.avatar.tradeCancelRequest( self.avatar.id )
		self.assert_( self.avatar.modeTarget == AvatarMode.NO_TARGET )
		self.assert_( self.avatar.mode == AvatarMode.NONE )
		self.assert_( self.partner.modeTarget == AvatarMode.NO_TARGET )
		self.assert_( self.partner.mode == AvatarMode.NONE )


	def preparePartner( self ):
		self.partner.mode = AvatarMode.TRADE_PASSIVE
		self.partner.modeTarget = self.avatar.id


	def testTradeOfferItem( self ):
		self.enterTradeActive()
		self.preparePartner()
		itemsLock = 1
		self.avatar.tradeOfferItemRequest( self.avatar.id, itemsLock, 13 )
		self.assert_( self.partner.client.offerCount == 0 )
		self.assert_( self.avatar.base.requestCount == 1 )


	def testTradeOfferItemDeny( self ):
		self.enterTradeActive()
		self.preparePartner()
		self.avatar.base.lockReply = ClientStub.DENY
		itemsLock = 1
		self.avatar.tradeOfferItemRequest( self.avatar.id, itemsLock, 13 )
		self.assert_( self.partner.client.offerCount == 0 )
		self.assert_( self.avatar.client.offerDenyCount == 1 )


	def offerItem( self ):
		self.enterTradeActive()
		self.preparePartner()
		self.avatar.base.lockReply = ClientStub.ACCEPT
		itemsLock = 1
		self.avatar.tradeOfferItemRequest( self.avatar.id, itemsLock, 13 )
		return itemsLock


	def testTradeOfferItemAccept( self ):
		itemsLock = self.offerItem()
		self.assert_( self.partner.client.offerCount == 1 )
		self.assert_( self.avatar.client.offerDenyCount == 0 )
		self.assert_( self.avatar.tradeOutboundLock == itemsLock )
		self.assert_( self.avatar.tradePartnerAccepted == False )


	def testTradeAcceptRequestActive( self ):
		self.offerItem()
		self.avatar.tradeOfferItem( 9 )
		self.partner.tradeAcceptRequest( self.partner.id, True )
		self.assert_( self.avatar.client.offerCount == 1 )
		self.assert_( self.partner.tradeSelfAccepted == True )
		self.assert_( self.partner.tradePartnerAccepted == False )
		self.assert_( self.partner.base.commitActiveCount == 0 )
		self.assert_( self.partner.base.commitPassiveCount == 0 )
		self.assert_( self.avatar.base.commitPassiveCount == 0 )
		self.assert_( self.avatar.base.commitActiveCount == 0 )
		self.assert_( self.avatar.tradePartnerAccepted == True )
		self.assert_( self.avatar.tradeSelfAccepted == False )


	def offerItemRequestBoth( self ):
		self.enterTradeActive()
		self.avatar.base.lockReply = ClientStub.ACCEPT
		itemsLock1 = 1
		self.avatar.tradeOfferItemRequest( self.avatar.id, itemsLock1, 12 )

		self.preparePartner()
		self.partner.base.lockReply = ClientStub.ACCEPT
		itemsLock2 = 1
		self.partner.tradeOfferItemRequest( self.partner.id, itemsLock2, 13 )


	def testTradeAcceptRequestPassive( self ):
		self.offerItemRequestBoth()
		self.partner.tradeAcceptRequest( self.partner.id, True )
		self.assert_( self.partner.client.offerCount == 1 )
		self.assert_( self.partner.tradeSelfAccepted == True )
		self.assert_( self.partner.tradePartnerAccepted == False )
		self.assert_( self.partner.base.commitActiveCount == 0 )
		self.assert_( self.partner.base.commitPassiveCount == 0 )
		self.assert_( self.avatar.base.commitPassiveCount == 0 )
		self.assert_( self.avatar.base.commitActiveCount == 0 )
		self.assert_( self.avatar.tradePartnerAccepted == True )
		self.assert_( self.avatar.tradeSelfAccepted == False )


	def tradeAcceptRequestBoth( self ):
		self.offerItemRequestBoth()
		self.avatar.tradeAcceptRequest( self.avatar.id, True )
		self.partner.tradeAcceptRequest( self.partner.id, True )


	def testTradeAcceptRequestCount( self ):
		self.tradeAcceptRequestBoth()
		self.assert_( self.avatar.base.commitPassiveCount == 0 )
		self.assert_( self.avatar.base.commitActiveCount == 1 )
		self.assert_( self.avatar.client.commitFailCount == 0 )
		self.assert_( self.avatar.client.commitSuccessCount == 0 )
		self.assert_( self.partner.base.commitActiveCount == 0 )
		self.assert_( self.partner.base.commitPassiveCount == 1 )
		self.assert_( self.partner.client.commitFailCount == 0 )
		self.assert_( self.partner.client.commitSuccessCount == 0 )


	def testTradeAcceptRequestDeny( self ):
		self.avatar.base.commitActiveReply = ClientStub.DENY
		self.partner.base.commitPassiveReply = ClientStub.DENY
		self.tradeAcceptRequestBoth()
		self.assert_( self.avatar.client.commitFailCount == 1 )
		self.assert_( self.avatar.client.commitSuccessCount == 0 )
		self.assert_( self.partner.client.commitFailCount == 1 )
		self.assert_( self.partner.client.commitSuccessCount == 0 )


	def testTradeAcceptRequestAccept( self ):
		self.avatar.base.commitActiveReply = ClientStub.ACCEPT
		self.partner.base.commitPassiveReply = ClientStub.ACCEPT
		self.tradeAcceptRequestBoth()
		self.assert_( self.avatar.tradeOutboundLock == -1 )
		self.assert_( self.avatar.tradePartnerAccepted == False )
		self.assert_( self.avatar.client.commitFailCount == 0 )
		self.assert_( self.avatar.client.commitSuccessCount == 1 )
		self.assert_( self.partner.tradeOutboundLock == -1 )
		self.assert_( self.partner.tradePartnerAccepted == False )
		self.assert_( self.partner.client.commitFailCount == 0 )
		self.assert_( self.partner.client.commitSuccessCount == 1 )


	def testItemsUnlockRequestCount( self ):
		self.offerItemRequestBoth()
		self.avatar.itemsUnlockRequest( self.avatar.id, 1 )
		self.assert_( self.avatar.base.unlockCount == 1 )


	def testItemsUnlockNotify( self ):
		self.offerItemRequestBoth()
		self.avatar.itemsUnlockNotify( True, 1 )
		self.assert_( self.avatar.tradeOutboundLock == -1 )
		self.assert_( self.avatar.tradeSelfAccepted == False );
		self.assert_( self.avatar.tradePartnerAccepted == False );
		self.assert_( self.partner.client.offerCount == 2 );
		self.assert_( self.avatar.client.unlockCount == 1 )
		self.assert_( self.partner.tradeSelfAccepted == False );
		self.assert_( self.partner.tradePartnerAccepted == False );


	def testCommerceStartDenyState( self ):
		self.avatar.mode == AvatarMode.TRADE_ACTIVE
		self.avatar.commerceStartRequest( self.avatar.id, 0 )
		self.assert_( self.avatar.client.commerceDenyCount == 1 )


	def testCommerceStartDenyTarget( self ):
		self.avatar.commerceStartRequest( self.avatar.id, 0 )
		self.assert_( self.avatar.client.commerceDenyCount == 1 )


	def testCommerceStartDenyInstance( self ):
		id = 333
		BigWorld.entities[ id ] = None
		self.avatar.commerceStartRequest( self.avatar.id, id )
		self.assert_( self.avatar.client.commerceDenyCount == 1 )


	def testCommerceStartDenyBusy( self ):
		pass


	def testCommerceStartAccept( self ):
		class MerchantBaseStub:
			def __init__( self ):
				self.itemsRequest = 0
			def commerceItemsRequest( self, avatarId ):
				self.itemsRequest += 1
			
		merchant = Merchant.Merchant()
		merchant.id = 333
		merchant.base = MerchantBaseStub()
		BigWorld.entities[ merchant.id ] = merchant
		self.avatar.commerceStartRequest( self.avatar.id, merchant.id )
		self.assert_( self.avatar.client.commerceDenyCount == 0 )
		self.assert_( merchant.base.itemsRequest == 1 )


	def testCommerceStartResponseAccept( self ):
		self.avatar.commerceStartResponse( True, 333 )
		self.assert_( self.avatar.mode == AvatarMode.COMMERCE )
		self.assert_( self.avatar.modeTarget == 333 )
		self.assert_( self.avatar.client.commerceDenyCount == 0 )


	def testCommerceStartResponseDeny( self ):
		self.avatar.commerceStartResponse( False, 333 )
		self.assert_( self.avatar.mode == AvatarMode.NONE )
		self.assert_( self.avatar.modeTarget == AvatarMode.NO_TARGET )
		self.assert_( self.avatar.client.commerceDenyCount == 1 )
	
	
	def testCommerceCancelRequest( self ):
		class MerchantStub:
			def __init__( self ):
				self.id = 333
				self.cancelCount = 0
			def commerceCancelRequest( self ):
				self.cancelCount += 1
			
		merchant = MerchantStub()
		BigWorld.entities[ merchant.id ] = merchant
		self.avatar.mode = AvatarMode.COMMERCE
		self.avatar.modeTarget = merchant.id
		merchant.modeTarget = self.avatar.id
		self.avatar.commerceCancelRequest( self.avatar.id )
		self.assert_( merchant.cancelCount == 1 )
		self.assert_( self.avatar.mode == AvatarMode.NONE )
		self.assert_( self.avatar.modeTarget == AvatarMode.NO_TARGET )

	
	def testCommerceBuyRequest( self ):
		class MerchantBaseStub:
			def __init__( self ):
				self.id = 333
				self.buyCount = 0
			def commerceSellRequest( mech, itemLock, itemSerial, avatarBase ):
				self.assert_( avatarBase == self.avatar.base )
				mech.buyCount += 1
				
		merchant = Merchant.Merchant()
		merchant.base = MerchantBaseStub()
		BigWorld.entities[ merchant.id ] = merchant
		self.avatar.mode = AvatarMode.COMMERCE
		merchant.modeTarget = self.avatar.id		
		self.avatar.modeTarget = merchant.id
		self.avatar.commerceBuyRequest( self.avatar.id, 1, 1 )
		self.assert_( merchant.base.buyCount == 1 )


	def testCommerceSellRequest( self ):
		merchant = Merchant.Merchant()
		merchant.base = None
		BigWorld.entities[ merchant.id ] = merchant
		merchant.modeTarget = self.avatar.id		
		self.avatar.mode = AvatarMode.COMMERCE
		self.avatar.modeTarget = merchant.id
		self.avatar.commerceSellRequest( self.avatar.id, 13, 1 )
		self.assert_( self.avatar.base.sellCount == 1 )


if __name__ == '__main__':
    unittest.main()
