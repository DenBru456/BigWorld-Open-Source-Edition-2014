

def tradeCommit( 
		base, supervisor, tradeID, outItemsLock, 
		outItemsSerials, outGoldPieces,
		inItemsTypes, inGoldPieces ):

	if base.lastTradeID >= tradeID:
		errorMsg = "INFO: Buy %d already done to %d, for entity %d"
		print errorMsg % (tradeID, base.lastTradeID, base.id )
		supervisor.completeTrade( base, tradeID )
		return

	if base.lastTradeID + 1 != tradeID:
		errorMsg = "ERROR: Missing trades between %d and %d for entity %d"
		print errorMsg % (base.lastTradeID, tradeID-1, base.id )

	def completeTrade( inItemsSerials ):
		supervisor.completeTrade( base, tradeID )
		base.tradeCommitNotify( True, 
				outItemsLock, outItemsSerials, 
				outGoldPieces, inItemsTypes, 
				inItemsSerials, inGoldPieces )

	base.lastTradeID = tradeID
	inItemsSerials = base.inventoryMgr.itemsTrade( 
			outItemsSerials, outGoldPieces, inItemsTypes, 
			[], inGoldPieces, outItemsLock )

	base.writeToDB( lambda *args: completeTrade( inItemsSerials ) )

# TradeHelper.py
