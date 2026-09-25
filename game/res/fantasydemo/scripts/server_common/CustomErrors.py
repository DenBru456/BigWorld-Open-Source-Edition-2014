from BWTwoWay import BWCustomError

class AuctionHouseError( BWCustomError ):
	pass

class BidError( BWCustomError ):
	pass

class BuyoutError( BWCustomError ):
	pass

class CreateEntityError( BWCustomError ):
	pass

class DBError( BWCustomError ):
	pass

class InsufficientGoldError( BWCustomError ):
	pass

class InvalidAuctionError( BWCustomError ):
	pass

class InvalidDamageAmountError( BWCustomError ):
	pass

class InvalidItemError( BWCustomError ):
	pass

class ItemLockError( BWCustomError ):
	pass

class PriceError( BWCustomError ):
	pass

class SearchCriteriaError( BWCustomError ):
	pass

# CustomErrors.py
