'''Client side inventory class.
'''
import ItemBase
import weakref


NOLOCK = -1
NOITEM = -1


class LockError( Exception ):
	pass


class InventoryMgr:
	
	def __init__( self, entity, addAsListener = False ):
		self._entity = weakref.proxy( entity )
		self._curItemIndex = NOITEM
		self._initItemSerial()
		self._initLockHandle()
		self._listener = addAsListener


	def addItem( self, itemType, itemSerial = None ):
		'''Adds item to inventory.
		'''
		if itemSerial is None:
			itemSerial = self._genItemSerial()
		entry = { "itemType": itemType, "serial": itemSerial, "lockHandle": NOLOCK }
		self._entity.inventoryItems.append( entry )
		if self._listener:
			self._entity.onAddItem( itemType, itemSerial )
		return itemSerial


	def removeItem( self, itemSerial ):
		index = self._itemSerial2Index( itemSerial ) # throws is serial not found
		entry = self._retrieveIfNotLocked( index )   # throws if item is locked
		
		removeItem( self._entity.inventoryItems, index )
		if self._curItemIndex == index:
			self._curItemIndex = -1
		elif self._curItemIndex > index:
			self._curItemIndex -= 1
		if self._listener:
			self._entity.onRemoveItem( entry[ "itemType" ], itemSerial )
		return entry[ "itemType" ]


	def removeCurrentItem( self ):
		if self._curItemIndex >= 0:
			index  = self._curItemIndex
			serial = self._entity.inventoryItems[ index ][ "serial" ]
			return self.removeItem( serial )
		else:
			errorMsg = 'No items currently selected'
			raise ValueError, errorMsg


	def selectItem( self, itemSerial ):
		if itemSerial >= 0:
			index = self._itemSerial2Index( itemSerial )
			entry = self._retrieveIfNotLocked( index )
			self._curItemIndex = index
			return entry[ "itemType" ]
		else:
			self._curItemIndex = NOITEM
			return ItemBase.ItemBase.NONE_TYPE


	def itemIndex2Serial( self, itemIndex ):
		try:
			return self._entity.inventoryItems[ itemIndex ][ "serial" ]
		except IndexError:
			errorMsg = 'itemIndex2Serial: invalid item index (idx=%d)'
			raise IndexError, errorMsg % itemIndex


	def _itemSerial2Index( self, itemSerial ):
		try:
			return iter( index
				for index, entry 
					in enumerate( self._entity.inventoryItems )
						if entry[ "serial" ] == itemSerial ).next()
		except StopIteration:
			errorMsg = 'Item serial not found (serial=%d)'
			raise ValueError, errorMsg % itemSerial


	def _retrieveIfNotLocked( self, index ):
		entry = self._entity.inventoryItems[ index ]
		if entry[ "lockHandle" ] != NOLOCK:
			errorMsg = 'Item locked (idx=%d)'
			raise LockError, errorMsg % index
		return entry

	
	def currentItemSerial( self ):
		if self._curItemIndex != NOITEM:
			return self._entity.inventoryItems[ self._curItemIndex ][ "serial" ]
		else:
			raise ValueError, 'No current item'
	

	def currentItemIndex( self ):
		return self._curItemIndex
		

	def currentItem( self ):
		if self._curItemIndex != NOITEM:
			return self._entity.inventoryItems[ self._curItemIndex ][ "itemType" ]
		else:
			return ItemBase.ItemBase.NONE_TYPE


	def selectNextItem( self, selectionFilter = lambda x: True ):
		newIndex = self._curItemIndex
		lenItems = len( self._entity.inventoryItems )
		while True:
			newIndex = ( newIndex + 1 ) % ( lenItems + 1 )
			if newIndex == lenItems:
				self._curItemIndex = -1
				break
			entry = self._entity.inventoryItems[ newIndex ]
			if entry[ "lockHandle" ] == NOLOCK and selectionFilter( 
					entry[ "itemType" ], entry[ "serial" ] ):
				self._curItemIndex = newIndex 
				break


	def selectPreviousItem( self, selectionFilter = lambda x: True ):
		newIndex = self._curItemIndex
		lenItems = len( self._entity.inventoryItems )
		while True:
			newIndex = ( newIndex - 1 ) % ( lenItems + 1 )
			if newIndex == lenItems:
				self._curItemIndex = -1
				break
			entry = self._entity.inventoryItems[ newIndex ]
			if entry[ "lockHandle" ] == NOLOCK and selectionFilter( 
					entry[ "itemType" ], entry[ "serial" ] ):
				self._curItemIndex = newIndex 
				break

	
	def selectSuitableItem( self, selectionFilter ):
		newIndex = self._curItemIndex
		lenItems = len( self._entity.inventoryItems )
		while True:
			newIndex = ( newIndex + 1 ) % ( lenItems + 1 )
			if newIndex ==  lenItems:
				newIndex = -1
			if newIndex == self._curItemIndex:
				return False
			entry = self._entity.inventoryItems[ newIndex ]
			if entry[ "lockHandle" ] == NOLOCK and selectionFilter( entry[ "itemType" ] ):
				self._curItemIndex = newIndex
				return True


	def itemsLock( self, itemsSerials, goldPieces ):
		lockHandle = self._getNextLockHandle()
		self.itemsRelock( lockHandle, itemsSerials, goldPieces )
		return lockHandle


	def itemsRelock( self, lockHandle, itemsSerials, goldPieces ):
		try:
			# if call doesn't throw, lock already exists and we cannot 
			# create a new lock with this handle. Raise exception.
			self._getLockedItemsIndex( lockHandle )
			lockExists = True
		except LockError:
			lockExists = False

		if lockExists:
			errorMsg = 'Lock already exists (%d)' 
			raise LockError, errorMsg % lockHandle
		if goldPieces < 0:
			raise LockError, "Cannot lock negative gold pieces"
		if self.availableGoldPieces() < goldPieces:
			errorMsg = 'Not enough gold (gold=%d)' 
			raise LockError, errorMsg % goldPieces
			
		itemsIndexes = []
		for serial in itemsSerials:
			index = self._itemSerial2Index( serial )
			if self._entity.inventoryItems[ index ][ "lockHandle" ] != NOLOCK:
				errorMsg = 'Item item already locked (idx=%d)' 
				raise LockError, errorMsg % index
			itemsIndexes.append( index )

		for index in itemsIndexes:
			self._entity.inventoryItems[ index ][ "lockHandle" ] = lockHandle
			
		lockedEntry = { "lockHandle": lockHandle, "goldPieces": goldPieces }
		self._entity.inventoryLocks.append( lockedEntry )


	def itemsLockedRetrieve( self, lockHandle ):
		itemsTypes = []
		itemsSerials = []
		for entry in self._entity.inventoryItems:
			if entry[ "lockHandle" ] == lockHandle:
				itemsSerials.append( entry[ "serial" ] )
				itemsTypes.append( entry[ "itemType" ] )
		index = self._getLockedItemsIndex( lockHandle )
		lockedEntry = self._entity.inventoryLocks[ index ]
		return ( itemsSerials, itemsTypes, lockedEntry[ "goldPieces" ] )
	

	def itemsUnlock( self, lockHandle ):
		index = self._getLockedItemsIndex( lockHandle )
		lockedEntry = self._entity.inventoryLocks[ index ]
		self._entity.inventoryLocks.pop( index )		
		for entry in self._entity.inventoryItems:
			if entry[ "lockHandle" ] == lockHandle:
				entry[ "lockHandle" ] = NOLOCK


	def itemsTrade( 
			self, outItemsSerials, outGoldPieces, 
			inItemsTypes, inItemsSerials, 
			inGoldPieces, hintHandle = -1 ):
		
		assert len( inItemsTypes ) >= len( inItemsSerials )
		
		lockHandle = NOLOCK
		for serial in outItemsSerials:
			index = self._itemSerial2Index( serial )
			item  = self._entity.inventoryItems[ index ]
			if item[ "lockHandle" ] != NOLOCK:
				assert lockHandle == NOLOCK or lockHandle == item[ "lockHandle" ]
				lockHandle = item[ "lockHandle" ]
		
		if lockHandle == NOLOCK:
			lockHandle = hintHandle
			
		if lockHandle != NOLOCK:
			index = self._getLockedItemsIndex( lockHandle )
			lockedItems = self._entity.inventoryLocks
			lockedItems.pop( index )		
		
		# remove items by serial (reversed iteration)
		inventory = self._entity.inventoryItems
		for i in range( len( inventory ), 0, -1 ):
			if inventory[i-1][ "serial" ] in outItemsSerials:
				inventory.pop( i-1 )

		self._entity.inventoryGoldPieces += inGoldPieces - outGoldPieces

		# unlock any locked items left behind
		for entry in inventory:
			if entry[ "lockHandle" ] == lockHandle:
				entry[ "lockHandle" ] = NOLOCK
		
		# add incomming items
		
		serials = []
		if inItemsTypes:
			inItemsSerials.extend( [None] * ( len( inItemsTypes ) - len( inItemsSerials ) ) )
			for itemType, itemSerial in zip( inItemsTypes, inItemsSerials ):
				serials.append( self.addItem( itemType, itemSerial ) )

		return serials


	def availableGoldPieces( self ):
		availGoldPieces = self._entity.inventoryGoldPieces
		for entry in self._entity.inventoryLocks:
			availGoldPieces -= entry[ "goldPieces" ]
		return availGoldPieces
		

	def _initLockHandle( self ):
		if self._entity.inventoryLocks:
			lockedItems = self._entity.inventoryLocks
			lockedHandles = [entry[ "lockHandle" ] for entry in lockedItems]
			self._lockHandle = max( lockedHandles ) # get max handle
		else:
			self._lockHandle = 0


	def _getNextLockHandle( self ):
		self._lockHandle += 1
		return self._lockHandle


	def _initItemSerial( self ):
		if self._entity.inventoryItems:
			inventory = self._entity.inventoryItems
			itemSerials = [entry[ "serial" ] for entry in inventory]
			self._itemSerial = max( itemSerials ) # get max handle
		else:
			self._itemSerial = 0


	def _genItemSerial( self ):
		self._itemSerial += 1
		return self._itemSerial
		

	def _getLockedItemsIndex( self, lockHandle ):
		try:
			return iter( index
				for index, entry 
					in enumerate( self._entity.inventoryLocks )
						if entry[ "lockHandle" ] == lockHandle ).next()
		except StopIteration:
			errorMsg = 'Lock handle not found (handle=%d)'
			raise LockError, errorMsg % lockHandle


def addItems( inventory, itemsTypes ):
	inventory.extend( itemsTypes )
	return len( inventory ) - 1


def removeItem( inventory, itemIndex ):
	try:
		item = inventory[ itemIndex ]
		inventory.pop( itemIndex )
		return item
	except IndexError:
		errorMsg = 'removeItem: invalid item index (idx=%d)'
		raise IndexError, errorMsg % itemIndex
