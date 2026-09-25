""" Auction BigWorld data type implementation """

from AuctionHouseCommon import Auction
from AuctionHouse import Seller
from AuctionHouse import Bidder

class AuctionCollectionStreamer:
	""" 
	Streamer for AuctionCollection object. 
	This is a Python map from auction Ids to auction objects.
	"""
	def addToStream( self, obj ):
		""" 
		Convert the Python AuctionCollection object obj into a string 
		representation to be placed onto the network, and return that string.
		@param obj 	the Python AuctionCollection object
		"""
		raise NotImplementedError

	def createFromStream( self,	stream ):
		"""
		Create a Python AuctionCollection object from the string passed in 
		through stream.
		@param stream 	the stream string containing the representation of the 
						object
		"""
		raise NotImplementedError
	
	
	def addToSection( self, obj, section ):
		""" 
		Add a representation of Python AuctionCollection obj to the 
		section DataSection.
		@param obj 		the Python AuctionCollection object to add
		@param section 	the DataSection to add to
		"""
		raise NotImplementedError
	
	
	def createFromSection( self, section ):
		"""
		Create and return a Python object from its persisted representation 
		in section DataSection.
		@param section 	DataSection containing the representation for this 
						AuctionCollection
		"""
		raise NotImplementedError
	
	
	def fromStreamToSection( self, stream, section ):
		"""
		Convert data from a stream representation (a string) to a DataSection 
		representation in section.
		@param stream 	the stream string
		@param section 	the DataSection to add to
		"""
		self.addToSection( self.createFromStream( stream ), section )
	
	
	def fromSectionToStream( self, section ):
		"""
		Convert data from a DataSection representation in section to a stream 
		representation, and return it.
		@param section 	the DataSection to read from
		"""
		return self.addToStream( self.createFromSection( section ) )
	
	def defaultValue( self ):
		return {}
	

class AuctionStreamer:
	""" Streamer for Auction class. """
	def addToStream( self, obj ):
		""" 
		Convert the Python Auction object obj into a string 
		representation to be placed onto the network, and return that string.
		@param obj 	the Python Auction object
		"""
		raise NotImplementedError

	def createFromStream( self,	stream ):
		"""
		Create a Python Auction object from the string passed in through 
		stream.
		@param stream 	the stream string containing the representation of the 
						object
		"""
		raise NotImplementedError
	
	
	def addToSection( self, obj, section ):
		""" 
		Add a representation of Python Auction obj to the 
		section DataSection.
		@param obj 		the Python Auction object to add
		@param section 	the DataSection to add to
		"""
		raise NotImplementedError
	
	
	def createFromSection( self, section ):
		"""
		Create and return a Python object from its persisted representation 
		in section DataSection.
		@param section 	DataSection containing the representation for this 
						Auction
		"""
		raise NotImplementedError
	
	
	def fromStreamToSection( self, stream, section ):
		"""
		Convert data from a stream representation (a string) to a DataSection 
		representation in section.
		@param stream 	the stream string
		@param section 	the DataSection to add to
		"""
		self.addToSection( self.createFromStream( stream ), section )
	
	
	def fromSectionToStream( self, section ):
		"""
		Convert data from a DataSection representation in section to a stream 
		representation, and return it.
		@param section 	the DataSection to read from
		"""
		return self.addToStream( self.createFromSection( section ) )
	
	def defaultValue( self ):
		raise NotImplementedError
	
class BidderStreamer:
	""" Streamer for Bidder class. """
	def addToStream( self, obj ):
		""" 
		Convert the Python Bidder object obj into a string 
		representation to be placed onto the network, and return that string.
		@param obj 	the Python Bidder object
		"""
		raise NotImplementedError

	def createFromStream( self,	stream ):
		"""
		Create a Python Bidder object from the string passed in through 
		stream.
		@param stream 	the stream string containing the representation of the 
						object
		"""
		raise NotImplementedError
	
	
	def addToSection( self, obj, section ):
		""" 
		Add a representation of Bidder Seller obj to the 
		section DataSection.
		@param obj 		the Python Auction object to add
		@param section 	the DataSection to add to
		"""
		raise NotImplementedError
	
	
	def createFromSection( self, section ):
		"""
		Create and return a Python object from its persisted representation 
		in section DataSection.
		@param section 	DataSection containing the representation for this 
						Auction
		"""
		raise NotImplementedError
	
	
	def fromStreamToSection( self, stream, section ):
		"""
		Convert data from a stream representation (a string) to a DataSection 
		representation in section.
		@param stream 	the stream string
		@param section 	the DataSection to add to
		"""
		self.addToSection( self.createFromStream( stream ), section )
	
	
	def fromSectionToStream( self, section ):
		"""
		Convert data from a DataSection representation in section to a stream 
		representation, and return it.
		@param section 	the DataSection to read from
		"""
		return self.addToStream( self.createFromSection( section ) )
	
	def defaultValue( self ):
		return None

class SellerStreamer:
	""" Streamer for Auction class. """
	def addToStream( self, obj ):
		""" 
		Convert the Python Seller object obj into a string 
		representation to be placed onto the network, and return that string.
		@param obj 	the Python Seller object
		"""
		raise NotImplementedError

	def createFromStream( self,	stream ):
		"""
		Create a Python Auction object from the string passed in through 
		stream.
		@param stream 	the stream string containing the representation of the 
						object
		"""
		raise NotImplementedError
	
	
	def addToSection( self, obj, section ):
		""" 
		Add a representation of Python Seller obj to the 
		section DataSection.
		@param obj 		the Python Seller object to add
		@param section 	the DataSection to add to
		"""
		raise NotImplementedError
	
	
	def createFromSection( self, section ):
		"""
		Create and return a Python object from its persisted representation 
		in section DataSection.
		@param section 	DataSection containing the representation for this 
						Auction
		"""
		raise NotImplementedError
	
	
	def fromStreamToSection( self, stream, section ):
		"""
		Convert data from a stream representation (a string) to a DataSection 
		representation in section.
		@param stream 	the stream string
		@param section 	the DataSection to add to
		"""
		self.addToSection( self.createFromStream( stream ), section )
	
	
	def fromSectionToStream( self, section ):
		"""
		Convert data from a DataSection representation in section to a stream 
		representation, and return it.
		@param section 	the DataSection to read from
		"""
		return self.addToStream( self.createFromSection( section ) )
	
	def defaultValue( self ):
		raise NotImplementedError
	
auctionCollectionStreamer = AuctionCollectionStreamer()
auctionStreamer = AuctionStreamer()
bidderStreamer = BidderStreamer()
sellerStreamer = SellerStreamer()
