"""
Auction House common module.
"""
import BigWorld
from functools import partial

DEBUG = False

def debug( msg, *args ):
	if DEBUG:
		if args:
			print "DEBUG: %s" % (msg % args)
		else:
			print "DEBUG: %s" % msg

def error( msg, *args ):
	print "ERROR: %s" % (msg % args)

class BidError ( Exception ):
	""" Bidding exception. """
	pass

class SampleAuctionItem:
	"""
	Represents an auction item, although any python object can be used
	in its place with the Auction class. The name and description attributes
	are not actually used for anything internally in this module.
	"""

	def __init__( self, itemType, itemSerial ):
		"""
		Constructor.

		@param itemType 		the item type
		@param itemSerial 	the item serial number
		"""
		self.itemType = itemType
		self.itemSerial = itemSerial


class Auction:
	"""
	Represents an auction. Auctions have expiry values, which are any value
	that can be compared meaningfully with the type of the time argument
	to AuctionHouse.checkAuctions method. This class is not meant for
	external instantiation - it is created by the
	AuctionHouse.registerAuction method.
	"""

	def __init__( self, auctionID, house, seller, item, bidPrice,
			buyoutPrice, expiry ):
		"""
		Constructor. Never directly called by client code.

		@param auctionID 	the ID of the auction
		@param house 		the auction house object to which this auction
							belongs
		@param item 		the item being auctioned
		@param seller 		a reference to this auction's seller (of type
							Seller)
		@param currentBid 	the current bidding price
		@param buyoutPrice 	the immediate buyout price, or None if none
							exists
		@param expiry 		the expiry value

		"""
		self.house 			= house
		self.auctionID 		= auctionID
		self.seller 		= seller
		self.highestBidder 	= None
		self.currentBid 	= bidPrice
		self.buyoutPrice 	= buyoutPrice
		self.item 			= item
		self.expiry 		= expiry
		self.finalised		= False

		debug( "Auction.__init__: auctionID = %s, seller = %s, expiry = %s",
			auctionID, str( seller ), str( expiry ) )
		debug( "Auction.__init__: currentBid = %s, buyout = %s, item = %s",
			str( bidPrice ), str( buyoutPrice ), str( item ) )


	def __str__( self ):
		""" Return the string representation of this auction. """
		return "Auction id=%s@%s: %s sold by %s " \
			"[bid/buyout:%s/%s -> %s], expiry: %s" \
			% ( self.auctionID, self.house, self.item, self.seller,
			self.currentBid, self.buyoutPrice, self.highestBidder,
			self.expiry)


	def increaseBid( self, proposedBid, bidder ):
		"""
		Register the given bidder's new proposed bid.

		@param proposedBid 	the proposed bidding value
		@param bidder 		the bidder
		@throws BidError 	if the bid is equal to or lower than the current bid
		"""
		debug( "Auction.increaseBid: proposedBid = %d", proposedBid )
		if proposedBid <= self.currentBid:
			raise BidError, "Bid is too low"
		oldBidder = self.highestBidder
		if oldBidder != None:
			oldBidder.onOutbid( self )

		self.currentBid = proposedBid
		self.highestBidder = bidder

		self.seller.onIncreasedBid( self, proposedBid, oldBidder, bidder )
		self.house.onIncreasedBid( self )


	def buyout( self, bidder ):
		"""
		Indicates that the given bidder immediately buys out this auction.

		@param	bidder		the bidder
		@throws	BidError	if this auction has no buyout price.
		"""
		debug( "Auction( %s ).buyout: bidder dbid=%d",
			self.auctionID, bidder.databaseID )

		if self.buyoutPrice == None:
			raise BidError, "No buyout price"
		self.currentBid = self.buyoutPrice

		if self.highestBidder != None:
			debug( "Auction( %s ).buyout: "\
					"this auction has existing highest bidder",
				self.auctionID )
			self.highestBidder.onOutbid( self )

		self.highestBidder = bidder
		self.seller.onSold( self, bidder )
		bidder.onWin( self )
		self.finalised = True


	def _checkExpiry( self, time ):
		"""
		Check that the expired time for this auction has not elapsed.

		@return 	True if the expired time has elapsed, otherwise
					return False
		"""
		if time > self.expiry:
			return True
		else:
			return False


	def checkAuction( self, time ):
		"""
		Notify the auction of the time. If the auction has expired, perform
		the appropriate actions to notify the seller and the highest bidder,
		and to remove itself from the Auction House.

		@param time 	the current time value to compare the expiry value to
		"""
		if self._checkExpiry( time ):
			if self.highestBidder != None:
				self.highestBidder.onWin( self )
				self.seller.onSold( self, self.highestBidder )
			else:
				self.seller.onExpired( self )
				self.house.onExpired( self )
			self.finalised = True



class IncrementalAuction( Auction ):
	"""
	An incremental auction is one where bidders place their maximum bids, and
	the bid amount is incremented each time a bid is placed until a previous
	bidder's maximum bid about is exceeded.
	"""

	def __init__( self, auctionID, house, seller, item, bidPrice,
			buyoutPrice, expiry, increment = 1 ):
		"""
		@param	auctionID	the auction ID
		@param	house		the auction house
		@param	seller		the seller
		@param	item		the auction item
		@param	bidPrice	the bidding price
		@param	buyoutPrice	the buyout price
		@param	expiry		the expiry
		@param	increment	The amount of currency to increment the
							bid by when a bid is contested.
		"""
		Auction.__init__( self,
			auctionID = auctionID, house = house,
			seller = seller, item = item, bidPrice = bidPrice,
			buyoutPrice = buyoutPrice, expiry = expiry )

		self.highestBidderMaxBid = None

		if not increment is None:
			self.increment = increment
		else:
			# increment by a single currency unit if None specified
			self.increment = 1
		debug( "IncrementalAuction(%s).increment = %d",
			self.auctionID, self.increment )

		# all bidders who have ever bid on this auction
		self.bidders = set()


	def increaseBid( self, maxBid, bidder ):
		"""
		Register the given bidder's new proposed maximum bid.

		@param maxBid 		the proposed maximum bidding value
		@param bidder 		the bidder
		@throws BidError 	if the bid is equal to or lower than the current bid
		"""

		debug(
			"IncrementalAuction( %s ).increaseBid: "
				"maxBid=%d, bidder.databaseID=%d, bidder.lockHandle=%d",
			self.auctionID, maxBid, bidder.databaseID, bidder.lockHandle
		)

		if maxBid <= self.currentBid:
			raise BidError, \
				"Submitted maximum bid of %d is lower than "\
				"the current bid of %d" % \
				(maxBid, self.currentBid)

		if self.buyoutPrice != None and maxBid >= self.buyoutPrice:
			raise BidError, \
				"Bid amount is equal to or greater than the buyout price"

		losingBidder = None

		if self.highestBidder is None:
			# no bidder
			self.currentBid += self.increment
			self.highestBidder = bidder
			self.highestBidderMaxBid = maxBid

		elif self.highestBidder != bidder:
			if self.highestBidderMaxBid == maxBid:
				# special case, precedence goes to current highest bidder
				losingBidder = bidder
				self.currentBid = self.highestBidderMaxBid

			else:
				if self.highestBidderMaxBid < maxBid:
					# the new bidder is the winner
					nextMaxBid = self.highestBidderMaxBid
					self.highestBidderMaxBid = maxBid
					losingBidder = self.highestBidder
					self.highestBidder = bidder

				elif self.highestBidderMaxBid > maxBid:
					# the old bidder retains the bid
					nextMaxBid = maxBid
					losingBidder = bidder

				# increment until we hit the lower of the two max bids
				while self.currentBid <= nextMaxBid:
					self.currentBid += self.increment

			if losingBidder:
				losingBidder.onOutbid( self )


		else: # highestBidder == bidder
			# current highest bidder wants to increase their bid
			# TODO: this is disabled in Avatar.webBidOnAuction for now

			return

		self.bidders.add( bidder )
		self.house.onIncreasedBid( self )


	def __str__( self ):
		""" Return the string representation of this auction. """
		return "IncrementalAuction id=%s@%s: %s sold by %s " \
			"[bid/buyout:%s/%s -> %s], expiry:%s, " \
			"increment = %d" % \
			(self.auctionID, self.house, self.item, self.seller,
			self.currentBid, self.buyoutPrice, self.highestBidder,
			self.expiry, self.increment)


class Bidder:
	"""
	Defines the interface to a bidder.

	The callback functions are:

	* onOutbid( self, auction )
	* onWin( self, auction )
	"""

	def __init__( self ):
		""" Constructor. """
		pass

	def onOutbid( self, auction ):
		""" Called when this bidder has been outbid on an auction.

			@param auction the auction lost
		"""
		pass

	def onWin( self, auction ):
		""" Called when this bidder has won an auction.

			@param auction the auction won
		"""
		pass


class Seller:
	"""
	Defines the interface to a seller.

	The callback functions are:
	* onIncreasedBid( self, auction, newPrice, oldBidder, newBidder )
	* onSold( self, auction, highestBidder )
	* onExpired( self, auction )

	"""

	def __init__( self ):
		""" Constructor. """
		pass

	def onIncreasedBid( self, auction, newPrice, oldBidder, newBidder ):
		"""
		Called when the auction's bid has been increased.
		@param auction 		the auction
		@param newPrice 	the new bidding price
		@param oldBidder 	the old bidder
		@param newBidder 	the new bidder
		"""
		pass

	def onSold( self, auction, highestBidder ):
		"""
		Called when the auction's bid has been sold, either by expiry or by
		buyout.
		@param auction 		the auction
		"""
		pass

	def onExpired( self, auction ):
		"""
		Called when the auction's bid has expired without being sold.
		@param auction 		the auction
		"""
		pass


class AbstractAuctionHouse:
	"""
	Represents an abstract AuctionHouse. Many of these can exist in the same
	memory space at a time. Each auction contains a reference to the house
	that it belongs to.

	There are some hooks that will enable subclasses to hook in customised
	behaviour: this includes the registerAuction and the various callbacks
	such as onExpired and onSold.

	The method checkAuctions should be called periodically with some
	representation of time passed into it (or at least something that
	monotonically increases as time increases).

	Subclasses should override these functions for implementing persistent
	auctions:
	registerAuction, getAuction, getAuctionIds, removeAuction

	Subclasses should not have to override these methods:
	bid, buyout, checkAuctions

	If subclasses choose to override the following methods, they should also
	call the base class's methods:
	onIncreasedBid, onBuyout, onExpired, onSold
	"""

	def __init__( self ):
		""" Constructor. """
		pass

	def getAuction( self, auctionID ):
		"""Get an auction based on its auction ID. """
		raise NotImplementedError


	def getAuctionIds( self ):
		""" Retrieve a list of valid auction IDs. """
		raise NotImplementedError


	def removeAuction( self, auction ):
		""" Remove an auction. """
		raise NotImplementedError

	def bid( self, auctionID, proposedBid, bidder ):
		"""
		Bid on an auction.

		@param auctionID 	the auction ID
		@param proposedBid 	the proposed bid amount
		@param bidder 		the bidder
		"""
		auction = self.getAuction( auctionID )
		auction.increaseBid( proposedBid, bidder )


	def buyout( self, auctionID, bidder ):
		"""
		Buyout an auction.

		@param auctionID 	the auction ID
		@param bidder 		the bidder
		"""
		auction = self.getAuction( auctionID )
		auction.buyout( bidder )


	def checkAuctions( self, time ):
		"""
		Check auction expiry using the given time.

		@param time the current time value
		"""
		for auctionID in self.getAuctionIds():
			auction = self.getAuction( auctionID )
			auction.checkAuction( time )


	def onIncreasedBid( self, auction ):
		"""
		Callback from the auction when its bid has been increased.

		@param auction 	the auction
		"""
		pass


	def onBuyout( self, auction, bidder ):
		"""
		Callback from the auction when it has been bought-out.

		@param auction 	the bought-out auction
		@param bidder 	the buying-out bidder
		"""
		self.removeAuction( auction )


	def onExpired( self, auction ):
		"""
		Callback from the auction when it has been expired.

		@param auction 	the expired auction
		"""
		self.removeAuction( auction )


	def onSold( self, auction ):
		"""
		Callback from the auction when it has been sold.

		@param auction 	the sold auciton
		"""
		self.removeAuction( auction )


class AuctionSearchCriteria:
	"""
	Search criteria base class.
	"""
	def __init__( self ):
		pass

	def filter( self, auction ):
		"""
		Filters an auction. Returns True if the auction complies with the
		criteria condition, or False otherwise.
		@param 	auction 	the auction to be filtered
		@return 			True if the auction complies with this
							criteria's condition, False otherwise
		"""
		raise NotImplementedError

	def __str__( self ):
		""" Return a string representation of this criteria. """
		return "AuctionSearchCriteria Base"

class AndSearchCriteria ( AuctionSearchCriteria ):
	"""
	Search criteria that AND's the results of its child criterias.
	"""

	def __init__( self, criterias ):
		"""
		Constructor.

		@param criterias 	a list of criterias
		"""

		self.criterias = None

		if type( criterias ) != list:
			raise ValueError, "criterias must be a list"
		if len( criterias ) < 2:
			raise ValueError, "Must be at least two criterias"
		self.criterias = criterias


	def append( self, criteria ):
		self.criterias.append( criteria )


	def filter( self, auction ):
		"""
		Filters an auction. Returns True if the auction complies with ALL
		criterias contained within this one, or False otherwise.

		@param 	auction 	the auction to be filtered
		@return 			True if the auction complies with this criteria's
							condition, False otherwise
		"""
		for criteria in self.criterias:
			if not criteria.filter( auction ):
				return False
		return True

	def __str__( self ):
		""" Return a string representation of this criteria. """
		return "(" + " AND ".join( map( str, self.criterias ) ) + ")"


class OrSearchCriteria ( AuctionSearchCriteria ):
	"""
	Search criteria that OR's the results of its child criterias.
	"""
	def __init__( self, criterias ):
		"""
		Constructor.

		@param criterias 	a list of criterias
		"""

		self.criterias = None

		if type( criterias ) != list:
			raise ValueError, "criterias must be a list"
		if len( criterias ) < 2:
			raise ValueError, "Must be at least two criterias"
		self.criterias = criterias

		# delegate some methods to criterias list


	def append( self, criteria ):
		self.criterias.append( criteria )


	def filter( self, auction ):
		"""
		Filters an auction. Returns True if the auction complies with ANY
		criterias contained within this one, or False otherwise.

		@param 	auction 	the auction to be filtered
		@return 			True if the auction complies with this criteria's
							condition, False otherwise
		"""
		for criteria in self.criterias:
			if criteria.filter( auction ):
				return True
		return False

	def __str__( self ):
		""" Return a string representation of this criteria. """
		return "(" + " OR ".join( map( str, self.criterias ) ) + ")"


class BidRangeSearchCriteria ( AuctionSearchCriteria ):
	"""
	Search criteria that selects auctions by their bid range.
	"""
	def __init__( self, minBid, maxBid ):
		"""
		Constructor. At most one of minBid and maxBid must not be None

		@param minBid 	the minimum bid price, inclusive
		@param maxBid 	the maximum bid price, inclusive
		"""

		if minBid != None and \
				( type( minBid ) != long and type( minBid ) != int ):
			raise ValueError, "minBid must be either an int or a long"
		self.minBid = minBid

		if maxBid != None and \
				( type( maxBid ) != long and type( maxBid ) != int ):
			raise ValueError, "maxBid must be either an int or a long"
		self.maxBid = maxBid
		if minBid == None and maxBid == None:
			raise ValueError, \
				"At least one of minBid and maxBid must not be None"


	def filter( self, auction ):
		"""
		Filters an auction. Returns True if the auction complies with ANY
		criterias contained within this one, or False otherwise.

		@param 	auction 	the auction to be filtered
		@return 			True if the auction complies with this criteria's
							condition, False otherwise
		"""
		if self.minBid != None and auction.currentBid < self.minBid:
			return False
		if self.maxBid != None and auction.currentBid > self.maxBid:
			return False

		return True


	def __str__( self ):
		""" Return a string representation of this criteria. """
		out = []
		if self.minBid != None:
			out.append( 'bid amount >= %d' % (self.minBid) )
		if self.maxBid != None:
			out.append( 'bid amount <= %d' % (self.maxBid) )
		return " AND ".join( out )


class BuyoutRangeSearchCriteria ( AuctionSearchCriteria ):
	"""
	Search criteria that selects auctions by their buyout range.
	"""
	def __init__( self, minBid, maxBid ):
		"""
		Constructor. At most one of minBid and maxBid must not be None

		@param minBid 	the minimum bid price, inclusive
		@param maxBid 	the maximum bid price, inclusive
		"""

		if minBid != None and \
		( type( minBid ) != long and type( minBid ) != int ):
			raise ValueError, "minBid must be either an int or a long"
		self.minBid = minBid

		if maxBid != None and \
		( type( maxBid ) != long and type( maxBid ) != int ):
			raise ValueError, "maxBid must be either an int or a long"
		self.maxBid = maxBid
		if minBid == None and maxBid == None:
			raise ValueError, \
				"At least one of minBid and maxBid must not be None"


	def filter( self, auction ):
		"""
		Filters an auction. Returns True if the auction complies with ANY
		criterias contained within this one, or False otherwise.

		@param 	auction 	the auction to be filtered
		@return 			True if the auction complies with this criteria's
							condition, False otherwise
		"""
		if self.minBid != None and auction.buyoutPrice < self.minBid:
			return False
		if self.maxBid != None and auction.buyoutPrice > self.maxBid:
			return False

		return True


	def __str__( self ):
		""" Return a string representation of this criteria. """
		out = []
		if self.minBid != None:
			out.append( 'buyout amount >= %d' % (self.minBid) )
		if self.maxBid != None:
			out.append( 'buyout amount <= %d' % (self.maxBid) )
		return " AND ".join( out )

# -----------------------------------------------------------------------------
# Section: FantasyDemoBidder proxy class
# -----------------------------------------------------------------------------

class FantasyDemoBidder( Bidder ):
	"""
	FantasyDemo Bidder class.

	Instances of this class remain in the same address space as the
	AuctionHouse entity, but the bidder player entities may not reside on the
	same BaseApp. This is a proxy class that holds the database ID of the
	seller, and, when the AuctionHouse requires the entity to call methods on,
	looks up the entity, or failing that, loads the entity from
	database and then invokes the required methods.
	"""

	def __init__( self, databaseID, lockHandle ):
		"""
		Constructor.
		@param databaseID 	the player database ID of the bidder.
		@param lockHandle	the lock handle of the bid
		"""
		Bidder.__init__( self )
		self.databaseID = databaseID
		self.lockHandle = lockHandle


	def __cmp__( self, other ):
		"""
		Comparison operator, equality is based on database IDs.
		@param 	other		the other object to compare to
		@return				-1 if self < other,
							0 if self == other,
							1 if self > other
		"""
		# defer comparison to database ID long
		if not other:
			return 1

		return cmp( self.databaseID, other.databaseID )


	def __hash__( self ):
		"""
		Hash function, uses a hash of the database ID.

		@return				the hash value for this bidder
		"""
		# This is defined so that IncrementalAuction.bidders instance variable
		# set works as expected.

		# defer hash function to database ID long
		return hash( self.databaseID )


	def __str__( self ):
		""" Return a string representation of this bidder object. """
		return "Bidder Database ID: %d" % (self.databaseID)


	def onOutbid( self, auction ):
		"""
		Called when this bidder has been outbid on an auction.

		@param auction the auction lost
		"""
		debug( "Bidder(%d).onOutbid: auctionID = %s",
			self.databaseID, auction.auctionID )
		BigWorld.createBaseFromDBID( 'Avatar', self.databaseID,
			partial( self._onOutbid2, auction ) )


	def _onOutbid2( self, auction, bidderEntity, dbID, wasActive ):
		if bidderEntity is None:
			error( "Bidder(%d).onOutbid: bidder entity does not exist!",
				self.databaseID )
		else:
			debug( "Bidder(%d).onOutbid: got outbid bidder entity (%d)",
				self.databaseID, bidderEntity.id )
			bidderEntity.onAuctionOutbid( auction.auctionID, self.lockHandle )


	def onWin( self, auction ):
		"""
		Called when this bidder has won an auction.
		@param auction the auction won
		"""
		# get entity for this bidder
		BigWorld.createBaseFromDBID( "Avatar", long( self.databaseID ),
			partial( self._onWin2, auction ) )
		# callback on _onWin2


	def _onWin2( self, auction, bidderEntity, dbID, wasActive ):
		if bidderEntity is None:
			error( "Bidder(%d).onWin: bidder entity does not exist!",
				self.databaseID )
		else:
			# should only pay the bid price, not the amount that was locked
			# away!

			# ask the entity to relock the new amount
			debug( "Bidder(%d).onWin: calling onAuctionWon with "\
					"lockHandle=%d",
				self.databaseID,
				self.lockHandle )

			bidderEntity.onAuctionWon( auction.auctionID,
				auction.highestBidder.lockHandle,
				auction.currentBid )
			# AuctionHouse.completeAuction is called from the bidder when this
			# is done


# -----------------------------------------------------------------------------
# Section: Seller proxy class
# -----------------------------------------------------------------------------

class FantasyDemoSeller( Seller ):
	"""
	FantasyDemo Seller class.

	Instances of this class remain in the same address space as the
	AuctionHouse entity, but the seller player entities may not reside on the
	same BaseApp. This is a proxy class that holds the database ID of the
	seller, and, when the AuctionHouse requires the entity to call methods on,
	looks up the entity, or failing that, loads the entity from
	database and then invokes the required methods.
	"""

	def __init__( self, databaseID ):
		"""
		Constructor.
		@param databaseID 	the player database ID of the seller.
		"""
		Seller.__init__( self )
		self.databaseID = databaseID


	def __cmp__( self, other ):
		"""
		Comparison operator, equality is based on database IDs.
		@param	other	the other object to compare to
		"""

		if not other:
		   	return 1

		return cmp( self.databaseID, other.databaseID )


	def __str__( self ):
		""" Return the string representation of this seller object. """
		return "Seller Database ID:%d" % (self.databaseID)


	def onIncreasedBid( self, auction, newPrice, oldBidder, newBidder ):
		"""
		From AuctionHouseCommon.Seller.

		Called when the auction's bid has been increased.
		@param auction 		the auction
		@param newPrice 	the new bidding price
		@param oldBidder 	the old bidder
		@param newBidder 	the new bidder
		"""
		# player doesn't need informing
		pass


	def onSold( self, auction, highestBidder ):
		"""
		From AuctionHouseCommon.Seller.

		Called when the auction's bid has been sold, either by expiry or by
		buyout.
		@param auction 		the auction
		"""
		# bidder initiates the actual trade transaction, see Bidder.onWin
		pass


	def onExpired( self, auction ):
		"""
		From AuctionHouseCommon.Seller.

		Called when the seller's auction has expired without being bid on.
		@param auction 		the auction
		"""
		BigWorld.createBaseFromDBID( "Avatar", self.databaseID,
			partial(self._onExpired2, auction) )


	def _onExpired2( self, auction, sellerEntity, dbID, wasActive ):
		if sellerEntity is None:
			error( "Seller(%d).onExpired: seller entity does not exist",
				self.databaseID )
		else:
			debug( "Seller(%d).onExpired: auction=%s, sellerEntity=%s",
				self.databaseID, str( auction ), str( sellerEntity ) )
			(itemLock, itemType, itemSerial) = auction.item
			sellerEntity.onAuctionExpired( auction.auctionID, itemLock )

# AuctionHouseCommon.py
