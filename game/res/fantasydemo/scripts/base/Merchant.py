import BigWorld
import FantasyDemo
import TradeHelper
import Inventory
import ItemBase
import Avatar
from GameData import MerchantData




class Merchant( FantasyDemo.Base ):

	def __init__( self ):
		FantasyDemo.Base.__init__( self )

		self.inventoryMgr = Inventory.InventoryMgr( self )
		self._restockInventory()

		self.writeToDB( shouldAutoLoad = True )

	def onRestore( self ):
		self.inventoryMgr = Inventory.InventoryMgr( self )


	# -------------------------------------------------------------------------
	# Section: Items trading
	# -------------------------------------------------------------------------

	def tradeCommit(
			self, supervisor, tradeID, outItemsLock,
			outItemsSerials, outGoldPieces,
			inItemsTypes, inGoldPieces, withWhom ):
		'''Performs the trade for this entity.
		Params:
			supervisor			mailbox of trading supervisor
			tradeID				ID of this trade
			outItemsLock		handle to lock of items being traded out
			inItemType			type of item being traded in
			inGoldPieces      ammount of gold begin traded in
		'''
		TradeHelper.tradeCommit(
			self, supervisor, tradeID, outItemsLock,
			outItemsSerials, outGoldPieces,
			inItemsTypes, inGoldPieces )

		if inGoldPieces > 0:
			self.numCustomers += 1
			withWhom.cell.sayToMe( self.id , u"Thank you, you are my %d%s customer!" % 
				(self.numCustomers, 
					self._getOrdinalSuffix( self.numCustomers ) ) )


	@staticmethod
	def _getOrdinalSuffix( num ):
		if ((num % 100) > 10 and (num % 100) < 20):
			return u"th"
		elif num % 10 == 1:
			return u"st"
		elif num % 10 == 2:
			return u"nd"
		elif num % 10 == 3:
			return u"rd"
		else:
			return u"th"

	def tradeCommitNotify( self, success,
			outItemsLock, outItemsSerials,
			outGoldPieces, inItemsTypes,
			inItemsSerials, inGoldPieces ):
		'''The trade has been completed. If it failed, unlock the trade items.
		Params:
			success:				True is trade was successful. False is it failed
			outItemsLock		lock handle to items being traded out
			inItemsTypes	   types of items being traded in
			inGoldPieces      ammount of goldPieces being traded in
		'''
		if not success and outItemsLock != 0:
			try:
				self.inventoryMgr.itemsUnlock( outItemsLock )
			except Inventory.LockError:
				errorMsg = "Merchant.tradeCommitNotify: couldn't unlock items (lock=%d)"
				print errorMsg % outItemsLock

	# -------------------------------------------------------------------------
	# Section: Items commerce
	# -------------------------------------------------------------------------

	def commerceItemsRequest( self, avatarBase ):
		'''Cell is requesting inventory list in the behalf of an avatar.
		Params:
			avatarBase		base mailbox of avatar interested in inventory list
		'''
		if avatarBase.className != 'Avatar':
			errorMsg = 'Merchant.commerceItemsRequest: entity not an Avatar: %d'
			print errorMsg % avatarBase.id
			return;

		self._restockInventory()
		avatarBase.client.commerceItemsNotify( self.inventoryItems )


	def commerceSellRequest( self, avatarLock, itemIndex, avatarBase ):
		'''Cell is requesting to sell an item to an avatar.
		Params:
			avatarLock			handle to locked items in avatar's inventory
			itemIndex			index of item to be sold
			avatarBase			avatar's base mailbox
		'''
		try:
			inventoryMgr = self.inventoryMgr
			itemSerial   = inventoryMgr.itemIndex2Serial( itemIndex )
			itemsLock = inventoryMgr.itemsLock( [itemSerial], 0 )
			itemsSerials, itemsTypes, goldPieces = \
					inventoryMgr.itemsLockedRetrieve( itemsLock )
			avatarBase.commerceBuyRequest( avatarLock, self,
					self.databaseID, self.lastTradeID+1,
					itemsLock, itemsSerials, itemsTypes )
		except (Inventory.LockError, IndexError):
			avatarBase.tradeCommitNotify( False, 0, [], 0, [], [], 0 )
			errorMsg = "Merchant.commerceSellRequest: couldn't lock item (idx=%d)"
			print errorMsg % itemIndex


	def commerceBuyRequest( self, avatarLock,
			itemsSerials, itemTypes, avatarBase ):
		'''Avatar's base is requesting us to buy an item from him.
		Params:
			avatarLock			handle to locked items in avatar's inventory
			itemTypes			types of items to be sold
			avatarBase			avatar's base mailbox
		'''
		try:
			itemPrice = ItemBase.price( itemTypes[0] )
			itemsLock = self.inventoryMgr.itemsLock( [], itemPrice )

			selfTradeParams = { "dbID": self.databaseID, \
								"tradeID": self.lastTradeID+1, \
								"lockHandle": itemsLock, \
								"itemsSerials": [], \
								"itemsTypes": [], \
								"goldPieces": itemPrice	}

			avatarBase.tradeSyncRequest( self, selfTradeParams )

		except Inventory.LockError:
			avatarBase.tradeCommitNotify( False, avatarLock, [], 0, [], [], 0 )
			errorMsg = "Merchant.commerceBuyRequest: couldn't lock gold (gold=%d)"
			print errorMsg % itemPrice


	def _restockInventory( self ):
		for item in list(self.inventoryItems):
			if item['itemType'] not in MerchantData.MERCHANT_ITEMS:
				try:
					self.inventoryMgr.removeItem( item['serial'] )
				except Inventory.LockError:
					pass

		for itemType in MerchantData.MERCHANT_ITEMS:
			serials = []
			for i in self.inventoryItems:
				if i['itemType'] == itemType:
					serials.append( i['serial'] )

			for i in serials[MerchantData.MAX_STOCK:]:
				try:
					self.inventoryMgr.removeItem( i )
				except Inventory.LockError:
					pass

			for i in range( MerchantData.MIN_STOCK - len( serials ) ):
				self.inventoryMgr.addItem( itemType )


# Merchant.py

