import operator
import re

# This class is used for notifications of roster events. It enables the
# Avatar entity to avoid circular references with the XMPPRoster class.
class XMPPRosterVisitor( object ):

	def onFriendAdd( self, friend, transport ):
		pass

	def onFriendDelete( self, friend, transport ):
		pass

	def onFriendPresenceChange( self, friend, transport,
			oldPresence, newPresence ):
		pass

	# This method must be supplied with a user friendly error message
	def onError( self, message ):
		pass


class XMPPRoster( object ):

	def __init__( self ):
		self.transports = {}


	#---------------------------------
	# Private Methods
	#---------------------------------

	def _getTransport( self, transport ):

		# If we don't already have the transport, add it
		if not self.transports.has_key( transport ):
			self.transports[ transport ] = {}

		return self.transports[ transport ]


	# TODO: Might be useful to have a 'pending' friends list, so we can
	#       confirm events that occur for pending friends rather than
	# 		treat them as unknown errors.
	# NB: Probably not a good idea to have a rosterVisitor for this one.
	def _addFriendPending( self, friendID, transport, rosterVisitor = None ):
		pass


	# This private method performs the addition of a friend to the roster
	# and notifies the visitor on success.
	#
	# @returns True on success, False if the friend is already in the roster.
	def _addFriend( self, friendID, transport, initialPresence,
					rosterVisitor = None ):

		# If this is the first user to be added we need _getTransport to
		# create the roster for us.
		transportRoster = self._getTransport( transport )

		if transportRoster.has_key( friendID ):
			return False

		transportRoster[ friendID ] = initialPresence

		if rosterVisitor:
			rosterVisitor.onFriendAdd( friendID, transport )

		return True


	def _delFriend( self, friendID, transport, rosterVisitor = None ):

		if not self.transports.has_key( transport ):
			return False

		transportRoster = self.transports[ transport ]

		if not transportRoster.pop( friendID, None ):
			return False

		if rosterVisitor:
			rosterVisitor.onFriendDelete( friendID, transport )

		return True


	def _removeNonExistentFriends( self, friendsList, rosterVisitor = None ):

		# Create a new list of friends
		newFriendsList = [ item[ "friendID" ] for item in friendsList ]

		for transport in self.transports.keys():
			transportRoster = self._getTransport( transport )
			transportFriends = set( transportRoster.keys() )

			removalItems = transportFriends.difference( newFriendsList )

			# Now we know the friends that no longer exist, get rid of them
			for friendID in removalItems:

				# There is no need to provide a default return value for pop.
				# We are in control of the transport roster so we know the
				# friend exists at this point.
				if transportRoster.pop( friendID ) and rosterVisitor:
					rosterVisitor.onFriendDelete( friendID, transport )
				

	#---------------------------------
	# Public Methods
	#---------------------------------

	# This method updates the roster with the provided friends list. If a
	# visitor is provided, notifications of state changes will be performed.
	def update( self, friendsList, rosterVisitor = None ):

		# Don't notify any visitors on initial population
		if not len( self.transports ):
			rosterVisitor = None

		self._removeNonExistentFriends( friendsList, rosterVisitor )

		for friend in friendsList:
			friendID  = friend[ "friendID" ]
			transport = friend[ "transport" ]

			self._addFriend( friendID, transport, "unavailable", rosterVisitor )

		return


	# This method updates the presence of the specified friend.
	# Returns True on success, False on failure.
	def updatePresence( self, friendID, transport, presence,
			rosterVisitor = None ):

		transportRoster = self._getTransport( transport )

		if not transportRoster.has_key( friendID ):
			# No error message is sent to the visitor here as this is mainly
			# triggered by server logic that the user doesn't need to know of.
			return False

		oldPresence = transportRoster[ friendID ]
		transportRoster[ friendID ] = presence

		if oldPresence != presence and rosterVisitor:
			rosterVisitor.onFriendPresenceChange( friendID, transport,
													oldPresence, presence )

		return True


	# This method adds a friend to our roster.
	def add( self, friendID, transport,
				initialPresence = "unavailable", rosterVisitor = None ):

		# Add our new friend.
		wasAdded = self._addFriend( friendID, transport, initialPresence,
									rosterVisitor )

		if not wasAdded and rosterVisitor:
			rosterVisitor.onError( "%s is already a friend." % friendID )

		return wasAdded


	# This method removes a friend from our roster.
	def remove( self, friendID, transport, rosterVisitor = None ):

		wasRemoved = self._delFriend( friendID, transport, rosterVisitor )

		if not wasRemoved and rosterVisitor:
			rosterVisitor.onError( "%s is not one of your friends." % friendID )
	
		return wasRemoved


	# TODO: this may not be needed...
	def addPendingFriendRemoval( self, friendID, transport ):
		pass


	# This method returns a bool indicating whether or not the specified
	# friend is known in our roster.
	def isFriend( self, friendID, transport ):

		if not self.transports.has_key( transport ):
			return False

		return self.transports[ transport ].has_key( friendID )


	# This method returns a list of any friends in the roster that match the
	# provided pattern
	def findFriendsLike( self, friendPattern, searchTransports = None ):

		matchedFriends = []
		for transport, transportRoster in self.transports.iteritems():

			if searchTransports and transport not in searchTransports:
				continue

			transportFriends = transportRoster.keys()

			for friend in transportFriends:
				if re.search( friendPattern, friend ):
					matchedFriends.append( (friend, transport) )

		return matchedFriends


	def friendsByStatus( self ):
		statusDict = {}

		for transport in self.transports.keys():

			transportRoster = self.transports[ transport ]

			for friendID, presence in transportRoster.iteritems():
				if not statusDict.has_key( presence ):
					statusDict[ presence ] = []

				statusFriendList = statusDict.get( presence )
				statusFriendList.append( friendID )

		return statusDict

