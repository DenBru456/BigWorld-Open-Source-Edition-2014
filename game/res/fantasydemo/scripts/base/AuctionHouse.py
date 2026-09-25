"""
Module implementing the AuctionHouse entity type.

This module defines some subclasses of abstract types defined in
AuctionHouseCommon, to adapt the mechanisms for the BigWorld engine.

"""

# -----------------------------------------------------------------------------
# Section: Imports
# -----------------------------------------------------------------------------

import BigWorld
import cPickle
import CustomErrors
from functools import partial
from AuctionHouseCommon import FantasyDemoSeller, FantasyDemoBidder, \
	IncrementalAuction, AuctionSearchCriteria, BidRangeSearchCriteria, \
	AndSearchCriteria, OrSearchCriteria, \
	AbstractAuctionHouse, BidError, \
	debug, error


import XMPPEventNotifier
from twisted.internet import defer

# -----------------------------------------------------------------------------
# Section: Module constants
# -----------------------------------------------------------------------------


# Check auctions every 5 seconds
AUCTION_CHECK_PERIOD = 5.0

# -----------------------------------------------------------------------------
# Section: Auction search criteria
# -----------------------------------------------------------------------------


class ItemTypeSearchCriteria ( AuctionSearchCriteria ):
	"""
	Search criteria that selects auctions by their item type.
	"""

	def __init__( self, itemTypesList ):
		"""
		Constructor.

		@param itemTypesList 	the item types list
		"""

		if type( itemTypesList ) != list:
			raise ValueError, "itemTypesList must be a list"
		self.itemTypesList = itemTypesList


	def filter( self, auction ):
		"""
		Filters an auction. Returns True if the auction's item type is in the
		item types list, False otherwise.

		@param 	auction 	the auction to be filtered
		@return 			True if the auction complies with this criteria's
							condition, False otherwise
		"""
		(itemLock, itemType, itemSerial) = auction.item
		return itemType in self.itemTypesList


	def __str__( self ):
		""" Return a string representation of this criteria. """

		if not self.itemTypesList:
			return "No item type"
		elif len( self.itemTypesList ) > 1:
			return "item type in (%s)" % \
				", ".join( map( str, self.itemTypesList ) )
		else:
			return "item type == %s" % (self.itemTypesList[ 0 ])


class SellerCriteria( AuctionSearchCriteria ):
	"""
	Search criteria that filters auctions based on seller's database ID.
	"""

	def __init__( self, databaseID ):
		"""
		@param databaseID	the database ID of the seller to compare against.
		"""
		self.databaseID = databaseID

	def filter( self, auction ):
		"""
		Filters an auction. Returns True if the auction's seller database ID
		matches the database ID given at init time, False otherwise.

		@param 	auction 	the auction to be filtered
		@return 			True if the auction complies with this criteria's
							condition, False otherwise
		"""
		return auction.seller.databaseID == self.databaseID

	def __str__( self ):
		""" Return a string representation of this criteria. """
		return "seller DBID = %d" % (self.databaseID)

class BidderCriteria( AuctionSearchCriteria ):
	"""
	Filters auctions based on bidder's database ID.
	"""

	def __init__( self, databaseID ):
		"""
		@param databaseID	the database ID of the seller to compare against.
		"""
		self.databaseID = databaseID

	def filter( self, auction ):
		"""
		Filters an auction. Returns True if the auction's has at least one
		match for bidder database ID for any of its bidders. False otherwise.

		@param 	auction 	the auction to be filtered
		@return 			True if the auction complies with this criteria's
							condition, False otherwise
		"""
		for bidder in auction.bidders:
			if self.databaseID == bidder.databaseID:
				return True

		return False

	def __str__( self ):
		""" Return a string representation of this criteria. """
		return "bidder DBID:%d has bidded" % (self.databaseID)

# -----------------------------------------------------------------------------
# Section: AuctionHouse entity
# -----------------------------------------------------------------------------

class AuctionHouse( BigWorld.Base, AbstractAuctionHouse ):
	"""
	Implements the AbstractAuctionHouse interface by making
	auctions persist in the BigWorld game state.
	"""

	def __init__( self ):
		""" Constructor. """
		BigWorld.Base.__init__( self )

		# register ourselves globally
		if self.name == "":
			self.name = "AuctionHouse"

		# Check if there is another AuctionHouse instance out there
		if BigWorld.globalBases.has_key( self.name ):
			print "AuctionHouse( %d ): " \
				"Another AuctionHouse instance is already registered as %s, " \
				"destroying ourselves" % (self.name, self.id)
			self.destroy()
			return

		self.registerGlobally( self.name, self._registerGloballyResult )

		# register the auction check timer
		self.addTimer(
			AUCTION_CHECK_PERIOD, AUCTION_CHECK_PERIOD )


		# auction.house reference is invalid when our state gets saved
		# give all our auctions references to this house
		for auctionID, auction in self.auctions.items():
			auction.house = self


	def cleanup( self ):
		""" Deregister and destroy ourself """
		self.deregisterGlobally( self.name )
		self.destroy()


	def _registerGloballyResult( self, success ):
		""" Callback from self.registerGlobally. """

		if not success:
			# There's likely already an AuctionHouse entity out there,
			# so we're not needed.
			self.destroy()

		def onInitWriteToDB( success, entity ):
			if not success:
				# There's probably already an AuctionHouse in the database,
				# or some other database problem.
				print "AuctionHouse(%d)._registerGloballyResult.onInitWriteToDB: " \
					"Failed to write to DB, destroying" % entity.id
				entity.destroy()

			else: pass # otherwise we're good to go

		self.writeToDB( onInitWriteToDB, shouldAutoLoad=True )


	def onTimer( self, id, userArg ):
		""" Timer callback. """
		self.checkAuctions( BigWorld.time() )


	def createAuction( self, sellerDBID, itemLock, itemType,
			itemSerial, startBid, expiryAmount, buyoutPrice ):
		"""
		Creates an auction, and returns the auction ID back to the seller player
		through its mailbox through the onCreateAuction method.

		@param	sellerDBID		the seller player database ID
		@param	itemLock		the seller player's item lock
		@param	itemType		the type ID of the seller player's item
		@param	itemSerial		the serial of the seller player's item
		@param	startbid		the requested starting bid price.
		@param	expiryAmount	the requested expiry relative to auction
								creation
		@param	buyoutPrice		the requested buyout amount, -1 if none
		"""

		debug( "AuctionHouse.createAuction: "
			"seller dbid=%d, itemLock=%d, itemType=%d, itemSerial=%d",
			sellerDBID, itemLock, itemType, itemSerial )

		if buyoutPrice == -1:
			buyoutPrice = None
		elif buyoutPrice != None and buyoutPrice < startBid:
			return defer.fail( CustomErrors.PriceError(
				"Buyout amount is less than the starting bid" ) )

		expiry = BigWorld.time() + expiryAmount

		# construct auction ID from the seller's database ID and the current
		# BigWorld.time()
		auctionID = str( sellerDBID ) + "/" + str( BigWorld.time() )

		# construct the Seller proxy obejct
		seller = FantasyDemoSeller( sellerDBID )

		# create an incremental auction, instead of a standard one
		# change the line below to use whatever Auction subclass you
		# have implemented if you wish to change it. See the AuctionHouseCommon
		# module.

		self.auctions[ auctionID ] = IncrementalAuction(
			auctionID	= auctionID,
			house		= self,
			seller		= seller,
			item		= (itemLock, itemType, itemSerial),
			bidPrice	= startBid,
			buyoutPrice	= buyoutPrice,
			expiry		= expiry
		)

		deferred = defer.Deferred()
		deferred.addCallback( partial( self.onAuctionCreated, auctionID,
			itemSerial ) )
		self.writeToDB( lambda isOkay, entity: deferred.callback( isOkay ) )
		return deferred


	def onAuctionCreated( self, auctionID, itemSerial, isOkay ):
		if not isOkay:
			# can't write to DB - rollback auction
			self.removeAuctionById( auctionID, saveToDB=False )
			return defer.fail( CustomErrors.DBError( "Could not write to DB" ) )

		return (auctionID,)


	def getAuction( self, auctionID ):
		"""Get an auction based on its auction ID. """

		return self.auctions[ auctionID ]


	def getAuctionIds( self ):
		""" Retrieve a list of valid auction IDs. """

		return self.auctions.keys()


	def removeAuction( self, auction, saveToDB = True ):
		""" Remove an auction. """

		del self.auctions[ auction.auctionID ]
		if saveToDB:
			self.writeToDB( self._removeAuction2 )


	def removeAuctionById( self, auctionID, saveToDB = True ):
		""" Remove an auction based on its auction ID. """

		del self.auctions[auctionID]
		if saveToDB:
			self.writeToDB( self._removeAuction2 )


	def _removeAuction2( self, success, entity ):

		if not success:
			error( "Could not remove auction - database write failed." )


	def bidOnAuction( self, player, databaseID, auctionID, amount, lockHandle ):
		"""
		Called when a bidder player bids on an auction.
		"""

		debug( "AuctionHouse.bidOnAuction: bidder dbid = %d, auctionID = %s, "
				"amount = %d, lockHandle = %d",
			databaseID, auctionID, amount, lockHandle )

		if not self.auctions.has_key( auctionID ):
			return defer.fail( CustomErrors.InvalidAuctionError(
						"Auction does not exist" ) )

		auction = self.auctions[ auctionID ]
		if auction.seller.databaseID == databaseID:
			return defer.fail( CustomErrors.InvalidAuctionError(
						"Can't bid on own auction" ) )

		if auction.highestBidder and \
				auction.highestBidder.databaseID == databaseID:
			return defer.fail( CustomErrors.BidError(
						"Already the highest bidder" ) )

		try:
			bidder = FantasyDemoBidder( databaseID, lockHandle )

			oldHighestMaxBid = None
			if not auction.highestBidder is None:
				oldHighestMaxBid = auction.highestBidderMaxBid

			auction.increaseBid( amount, bidder )
		except BidError, e:
			return defer.fail( CustomErrors.BidError( str( e ) ) )

		if amount <= oldHighestMaxBid:

			if auction.highestBidder.databaseID == databaseID:
				return defer.fail( CustomErrors.BidError(
					"You have previously entered a higher maximum bid" ) )

			else:
				result = ("You have been outbid by another player's maximum bid",)
		else:
			result = ("You are the highest bidder",)

		self.writeToDB( self._reportDBError )

		return result


	def _reportDBError( self, success, entity ):

		if not success:
			error( "AuctionHouse: Could not write to DB!" )

	def buyoutAuction( self, player, databaseID, auctionID ):
		"""
		Called when a bidder buys out an auction.
		"""

		if not self.auctions.has_key( auctionID ):
			return defer.fail( CustomErrors.InvalidAuctionError(
				"Auction has already expired or does not exist" ) )

		auction = self.auctions[ auctionID ]

		if auction.seller.databaseID == databaseID:
			return defer.fail( CustomErrors.InvalidAuctionError(
						"Can't buy out own auction" ) )

		if auction.buyoutPrice is None:
			return defer.fail( CustomErrors.BuyoutError(
						"Auction has no buyout price" ) )

		existingLock = -1

		if not auction.highestBidder is None and \
				auction.highestBidder.databaseID == databaseID:
			# buying out player already is the highest bidder on this auction
			# need to unlock before buying it out
			existingLock = auction.highestBidder.lockHandle
			auction.highestBidder = None

		deferred = player.lockAuctionGold( auctionID,
				auction.buyoutPrice, existingLock )

		deferred.addCallback(
			partial( self._buyoutAuction2, auctionID, databaseID ) )

		return deferred


	def _buyoutAuction2( self, auctionID, databaseID, returnValues ):
		newLockHandle, = returnValues

		bidder = FantasyDemoBidder( databaseID, newLockHandle )
		auction = self.auctions[ auctionID ]
		auction.buyout( bidder )

		return ("Auction bought out",)


	def completeAuction( self, auctionID, bidderEntity, lockHandle ):
		"""
		Completion method called from Avatar with a new lockhandle for the
		possibly reduced bid price.
		"""

		auction = self.auctions[ auctionID ]

		debug( "AuctionHouse.completeAuction: "
				"auctionID=%s, bidderEntity=%s(%d), lockHandle = %d",
			auctionID, str( bidderEntity ), auction.highestBidder.databaseID,
			lockHandle )

		# get the seller entity
		BigWorld.createBaseFromDBID(
			"Avatar", auction.seller.databaseID,
			partial( self._completeAuction2, auction,
				bidderEntity, lockHandle )
		)


	def _completeAuction2( self, auction, bidderEntity,
			bidderLockHandle, sellerEntity, dbID, wasActive ):

		if sellerEntity == None:
			# entity does not exist
			debug( "AuctionHouse.completeAuction: "\
					"Seller entity %d does not exist or "\
					"could not be loaded",
				auction.seller.databaseID )

		else:
			debug( "AuctionHouse.completeAuction: "
					"seller entity %d: %s",
				dbID, str( sellerEntity ) )
			# do the swap
			(itemLockHandle, itemType, itemSerial) = auction.item

			sellerEntity.tradeCommitActive( itemLockHandle )
			bidderEntity.tradeCommitPassive( bidderLockHandle,
				sellerEntity )

			self.onSold( auction )

			msg = "Auction %s won by %s (dbID=%d). Item type=%s, gold pieces" \
							"=%d, seller=%s (dbID=%d). Trade pending." % \
						(auction.auctionID,
							bidderEntity.className,
							auction.highestBidder.databaseID,
							auction.item[1],
							auction.currentBid,
							sellerEntity.className,
							auction.seller.databaseID ) 				
			XMPPEventNotifier.broadcast( msg )

	def webTestMethod( self, first_arg, second_arg ):
		return (2 * first_arg, second_arg.upper())

	def webSearchAuctions( self, searchCriteriaPickle ):
		"""
		Web method to enable searches. Searches use criteria, and can be
		combined using AND and OR operators. The criteria themselves are
		pickeld instances of AuctionHouseCommon.AuctionSearchCriteria
		subclasses. If criteria is an empty string, then all auctions are
		returned.

		@param	searchCriteriaPickle	the search criteria, pickled

		Return values
		searchedAuctions
			A list of auction IDs that match the given criteria, or all
			auction IDs if an empty string was supplied for the criteria.
		"""

		if not isinstance( searchCriteriaPickle, str ):
			return defer.fail( CustomErrors.SearchCriteriaError(
				"Search criteria must be string "\
				"(containing a pickle or empty) or None" ) )

		if searchCriteriaPickle == '':
			# return all auction IDs
			debug( "AuctionHouse.webSearchAuctions: "
					"returning all auction IDs: %s",
				str( self.getAuctionIds() ) )
			return (self.getAuctionIds(),)

		try:
			searchCriteria = cPickle.loads( searchCriteriaPickle )
			debug( "AuctionHouse.webSearchAuctions: "
				"Search criteria: %s", str( searchCriteria ) )
		except cPickle.PickleError, e:
			return defer.fail( CustomErrors.SearchCriteriaError(
						"Search criteria unpickle failed" ) )

		# filter using the criteria
		return ([auctionID for auctionID, auction in self.auctions.items()
			if searchCriteria.filter( auction )],)


	def webGetAuctionInfo( self, auctions ):
		"""
		Web method to retrieve information about auctions. The form of the
		return value is a list of idctionaries that descrive the auction
		for a give auction ID.

		@param	auctions 	the list of auction IDs

		Response return values:
		auctionInfo
			List of dictionaries describing an auction for each auction IDs
			given. Each dictionary contains the keys auctionID, finalised,
			itemLock, itemSerial, itemType, sellerDBID, expiry, currentBid,
			currentMaxBid, buyoutPrice.

		"""

		out = []
		for auctionID in auctions:
			try:
				auction = self.auctions[ auctionID ]
			except KeyError:
				continue

			itemLock, itemType, itemSerial = auction.item
			auctionInfo = {
				"auctionID": 		auctionID,
				"finalised":		auction.finalised,
				"itemLock": 		itemLock,
				"itemType":			itemType,
				"itemSerial":		itemSerial,
				"sellerDBID":		auction.seller.databaseID,
				"expiry":			auction.expiry,
				"currentBid": 		auction.currentBid,
				"currentMaxBid":	auction.highestBidderMaxBid,
				"buyoutPrice":		auction.buyoutPrice,
				"highestBidder":	-1
			}


			if auction.highestBidder:
				auctionInfo["highestBidder"] = \
					auction.highestBidder.databaseID

			auctionInfo['bidders'] = [bidder.databaseID for bidder in auction.bidders]
			out.append( auctionInfo )

		return (out,)


	def webCreateItemTypeCriteria( self, itemTypes ):
		"""
		Web method that creates an item type criteria, which matches
		auctions against a list of item type IDs.

		@param	itemTypes	a list of item types to match against

		Response return values:
		criteria
			The pickled criteria object.
		"""

		# work around unpickle-ability of PyDataArrayInstance
		# TODO: was this fixed?
		itemTypesList = [ itemType for itemType in itemTypes ]

		return (cPickle.dumps( ItemTypeSearchCriteria( itemTypesList ) ),)


	def webCreateBidRangeCriteria( self, minBid, maxBid ):
		"""
		Web method that creates a bid range auction search criteria,
		which matches auctions with a a current bid amount within a range.
		Either (but not both) minimum and maximum can be omitted from the
		range to create open-ended ranges.

		@param	minBid		the minimum bid, or -1 for no minimum
		@param	maxBid		the maximum bid, or -1 for no maximum

		Response return values:
		criteria
			The pickled criteria object
		"""

		if minBid == -1:
			minBid = None
		if maxBid == -1:
			maxBid = None

		return (cPickle.dumps( BidRangeSearchCriteria( minBid, maxBid ) ),)


	def webCreateSellerCriteria( self, databaseID ):
		"""
		Web method that creates a seller criteria, which matches auctions
		with a particular seller database ID.

		@param	databaseID	the seller database ID

		Response return values:
		criteria
			The pickled criteria object
		"""

		return (cPickle.dumps( SellerCriteria( databaseID ) ),)


	def webCreateBidderCriteria( self, databaseID ):
		"""
		Creates a bidder databaseID criteria object, and returns it as a
		pickle
		@param	databaseID	the bidder database ID

		Response return values:
		criteria
			The pickled criteria object
		"""

		return (cPickle.dumps( BidderCriteria( databaseID ) ),)


	def webCombineAnd( self, crit1Pickle, crit2Pickle ):
		"""
		Combines two criterias through an AndSearchCriteria, creating a criteria
		that is equivalent to crit1 && crit2.

		@param	crit1Pickle	the first pickled criteria
		@param	crit2Pickle	the second pickled criteria

		Response return values:
		criteria
			The pickled combined criteria object
		"""

		crit1 = cPickle.loads( crit1Pickle )
		crit2 = cPickle.loads( crit2Pickle )
		if not isinstance( crit1, AndSearchCriteria ) and \
				not isinstance( crit2, AndSearchCriteria ):

			andCriteria = AndSearchCriteria( [crit1, crit2] )
		else:
			if isinstance( crit1, AndSearchCriteria ):
				andCriteria = crit1
				otherCrit = crit2
			else:
				andCriteria = crit2
				otherCrit = crit1
			andCriteria.append( otherCrit )

		return (cPickle.dumps( andCriteria ),)


	def webCombineOr( self, crit1Pickle, crit2Pickle ):
		"""
		Combines two criterias through an OrSearchCriteria, creating a criteria
		that is equivalent to crit1 || crit2.

		@param	crit1Pickle	the first pickled criteria
		@param	crit2Pickle	the second pickled criteria

		Response return values:
		criteria
			The pickled combined criteria object
		"""

		crit1 = cPickle.loads( crit1Pickle )
		crit2 = cPickle.loads( crit2Pickle )
		if not isinstance( crit1, OrSearchCriteria ) and \
				not isinstance( crit2, OrSearchCriteria ):

			orCriteria = OrSearchCriteria( [crit1, crit2] )
		else:
			if isinstance( crit1, OrSearchCriteria ):
				orCriteria = crit1
				otherCrit = crit2
			else:
				orCriteria = crit2
				otherCrit = crit1
			orCriteria.append( otherCrit )

		return (cPickle.dumps( orCriteria ),)


	def webGetTime( self ):
		"""
		Retrieves BigWorld.time() for use in determining the relative expiry
		times.

		Response return values:
		time
			the value of BigWorld.time()
		"""

		return (BigWorld.time(),)

# class AuctionHouse

# -----------------------------------------------------------------------------
# Section: Utility functions
# -----------------------------------------------------------------------------


def wakeup():
	"""
	Activate the AuctionHouse singleton entity.
	"""

	if not BigWorld.globalBases.has_key( 'AuctionHouse' ):
		# Check if the singleton instance is saved in the database.
		BigWorld.createBaseAnywhereFromDB( 'AuctionHouse', 'AuctionHouse',
			_wakeup2 )


def _wakeup2( entity, dbID, wasActive ):
	if entity is None:
		# Singleton doesn't exist in the database - spawn it somewhere,
		# anywhere.
		print "Creating new instance of AuctionHouse"
		BigWorld.createBaseAnywhere( 'AuctionHouse',
			dict( name="AuctionHouse" ), _wakeup3 )
	else:
		print "AuctionHouse entity loaded (%d)" % entity.id


def _wakeup3( entity ):
	if entity is None:
		print "Could not create AuctionHouse entity (with createBaseAnywhere)"
	else:
		print "AuctionHouse entity created (%d)" % entity.id

def destroyAuctionHouse():
	"""
	Destroy the global instance of the Auction House.
	"""
	if BigWorld.globalBases.has_key( "AuctionHouse" ):
		ah = BigWorld.globalBases['AuctionHouse']
		if BigWorld.entities.has_key( ah.id ):
			print "Deregistering and destroying AuctionHouse %d" % ah.id
			ah.cleanup()

# AuctionHouse.py
