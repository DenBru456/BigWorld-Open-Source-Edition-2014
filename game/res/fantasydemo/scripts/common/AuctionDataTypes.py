"""
Module for implementing the FIXED_DICT data types AuctionDataType, the
auction type (associated with IncrementalAuction), and AuctionsDataType,
the mapping collection type (associated with dict).
"""

from AuctionHouseCommon import IncrementalAuction, FantasyDemoSeller, \
	FantasyDemoBidder
import BigWorld

# TODO: see if there's any benefit to implementing createFromStream and
# addToStream

class AuctionDataType:
	"""
	Class implementing the Auction data type.
	"""

	def getDictFromObj( self, auction ):
		"""
		Return a dictionary of values representing the given auction. This
		dictionary is to be saved to the database.
		"""

		# print "AuctionDataTypes.AuctionDataType.getDictFromObj( %s )" % \
		#		(str( auction ))

		itemLock, itemType, itemSerial = auction.item

		buyoutPrice = auction.buyoutPrice
		if buyoutPrice is None:
			buyoutPrice = -1

		bidderDBID = -1
		bidderLockHandle = -1
		highestBidderMaxBid = -1
		if not auction.highestBidder is None:
			bidderDBID = auction.highestBidder.databaseID
			bidderLockHandle = auction.highestBidder.lockHandle
			highestBidderMaxBid = auction.highestBidderMaxBid


		bidders = []
		for bidder in auction.bidders:
			bidders.append( {
				"databaseID" 	: bidder.databaseID,
				"lockHandle"	: bidder.lockHandle
			})
		# save an IncrementalAuction's and its associated seller, item and
		# highestBidder properties
		return {
			"id"						: auction.auctionID,
			"sellerDBID"				: auction.seller.databaseID,
			"highestBidderDBID"			: bidderDBID,
			"highestBidderLockHandle"	: bidderLockHandle,
			"currentBid"				: auction.currentBid,
			"buyoutPrice"				: buyoutPrice,
			"itemLock"					: itemLock,
			"itemType"					: itemType,
			"itemSerial"				: itemSerial,
			"expiry"					: auction.expiry,
			"finalised"					: auction.finalised,
			"highestBidderMaxBid"		: highestBidderMaxBid,
			"increment"					: auction.increment,
			"bidders"					: bidders
		}

	def createObjFromDict( self, dictValue ):
		"""
		Create an Auction object from dictionary values.
		"""

		# print "AuctionDataTypes.AuctionDataType.createObjFromDict( %s )" %\
		#		(str( dict( dictValue ) ))

		buyoutPrice = dictValue['buyoutPrice']
		if buyoutPrice == -1:
			buyoutPrice = None

		# construct a new auction
		result = IncrementalAuction(
			auctionID 		= dictValue['id'],
			house 			= None, # this is filled by AuctionHouse.__init__
			seller 			= FantasyDemoSeller( dictValue['sellerDBID'] ),
			item 			= (dictValue['itemLock'],
								dictValue['itemType'],
								dictValue['itemSerial'] ),
			bidPrice 		= dictValue['currentBid'],
			buyoutPrice 	= buyoutPrice,
			expiry 			= dictValue['expiry'],
		)
		if dictValue['highestBidderDBID'] != -1:
			result.highestBidder = FantasyDemoBidder(
				dictValue['highestBidderDBID'],
				dictValue['highestBidderLockHandle']
			)
		result.finalised	= dictValue['finalised']
		result.highestBidderMaxBid = dictValue['highestBidderMaxBid']
		if result.highestBidderMaxBid == -1:
			result.highestBidderMaxBid = None
		result.increment	= dictValue['increment']

		bidders = set()
		for item in dictValue['bidders']:
			bidders.add(
				FantasyDemoBidder(
					item['databaseID'],
					item['lockHandle']
				)
			)
		result.bidders		= bidders

		return result

	def	isSameType( self, obj ):
		"""
		Return whether the given object is of the user data type, that is,
		IncrementalAuction.

		@type obj:		object
		@param obj:		the object to compare against
		@return bool
		"""
	# print "AuctionDataTypes.AuctionDataType.isSameType( %s )" % str( obj )

		return isinstance( obj, IncrementalAuction )


auctionDataInstance = AuctionDataType()

class AuctionsDataType:
	"""
	Class implementing the collection of auctions.
	"""

	def getDictFromObj( self, obj ):
		"""
		Creates a dictionary object conforming to the AUCTIONS data def with the
		values of the given Auctions collection
		"""

		# print "AuctionDataTypes.AuctionsDataType.getDictFromObj( %s )" %\
		#		(str( obj ))
		out = []
		for auctionID, auction in obj.items():
			auctionDict = auctionDataInstance.getDictFromObj( auction )

		# print "Adding auctionID = %s, auction = %s" % \
		#			(auctionID, str( auctionDict ))
			out.append(
				{
					"auctionID" : auctionID,
					"auction"	: auction,
				}
			)
		return { "list" : out }

	def createObjFromDict( self, dictValues ):
		"""
		Creates a dictionary object from auction ID to auction objects
		from the dictionary values.
		"""
		# print "AuctionDataTypes.AuctionsDataType.createObjFromDict( %s )" %\
		#		(str( dict( dictValues ) ))
		out = {}
		for mapping in dictValues['list']:
			out[ mapping['auctionID'] ] = mapping['auction']

		return out

	def isSameType( self, obj ):
		# print "AuctionDataTypes.AuctionsDataType.isSameType( %s )" % \
		#		(str( obj ))
		return type(obj) is dict


auctionsDataInstance = AuctionsDataType()
