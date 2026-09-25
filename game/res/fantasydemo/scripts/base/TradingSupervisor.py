import BigWorld

import XMPPEventNotifier

class TradingSupervisor( BigWorld.Base ):
	"""
	This class supervises trades to ensure that items are not lost even if
	there is a catastrophic system failure in the middle of the trade.
	"""

	def __init__( self ):
		BigWorld.Base.__init__( self )

		if self.globalName == "":
			self.globalName = "TradingSupervisor"

		# If two TradingSupervisor bases are created at the same time, only one
		# will successfully registered globally. The others should destroy
		# themselves.
		def registerGloballyResult( success ):
			if not success:
				print "TradingSupervisor(%d).__init__: " \
						"registerGloballyResult reported failure, going down" % \
					self.id
				self.destroy()

		self.registerGlobally( self.globalName, registerGloballyResult )

		if self.recentTrades == []:
			self.outstandingTrades = []
			self._readyToGo()
		else:
			# go through and replay all recent trades
			self.outstandingTrades = [[0,0]] * len(self.recentTrades)
			self.replaying = True
			for trade in self.recentTrades:
				self._replayTrade( trade )

		self.writeToDB( self._initWriteToDB, shouldAutoLoad=True )


	def cleanup( self ):
		""" Deregister and destroy ourself """
		self.deregisterGlobally( self.globalName )
		self.destroy()


	def _initOnLookupTrader( self, databaseId, entity ):
		if type( entity ) == bool:
			if not entity:
				print "TradingSupervisor.__init__:" \
				"trader entity %d does not exist: %d" % (databaseId)
			else:
				BigWorld.createBaseFromDBID( "Avatar", databaseId,
					self._initOnLoadTrader )


	def _initOnLoadTrader( self, entity, databaseId, wasActive ):
		if entity is None:
			print "TradingSupervisor.__init__: " \
				"Failed to load trader entity DBID: %d" % (databaseId)
		print "TradingSupervisor.__init__: "\
			"Loaded trader entity %d" % (databaseId)


	def _initWriteToDB( self, success, entity ):
		print "TradingSupervisor.initWriteToDB: "\
			"success=%s, entity=%s, dbId=%d" % \
			(str( success ), str( entity ), entity.databaseID)


	def _replayTrade( self, trade ):
		# Note: This needs to be in a function instead of being inlined because
		# of how lambda substitutes its values.
		traderMBs = [None, None]
		BigWorld.createBaseFromDBID( trade[ "typeA" ],
			trade[ "paramsA" ][ "dbID" ],
			lambda mb, dbID, wasActive: self._collectMailbox( trade[ "typeA" ],
				trade, traderMBs, 0, mb ) )
		BigWorld.createBaseFromDBID( trade[ "typeB" ],
			trade[ "paramsB" ][ "dbID" ],
			lambda mb, dbID, wasActive: self._collectMailbox( trade[ "typeB" ],
				trade, traderMBs, 1, mb ) )


	def _collectMailbox( self, entityType, trade, traderMBs, ind, box ):
		if box == None:
			# None from createBaseFromDBID
			print "ERROR: Entity involved in trade no longer exists!"
			tradeIndex = self.recentTrades.index( trade )
			self.outstandingTrades.pop( tradeIndex )
			self.recentTrades.pop( tradeIndex )
			if len(self.outstandingTrades) == 0:
				self._readyToGo()
			return


		# normally the entity will already be around since it should have
		# been around when we crashed and thus will have been restored
		traderMBs[ ind ] = box
		if traderMBs[ ind^1 ] == None: return	# still missing other mailbox

		# ok we have both mailboxes, so look up trade in recentTrades
		pos = self.recentTrades.index( trade )
		# set the ids into the right spot in outstandingTrades
		self.outstandingTrades[pos] = [traderMBs[0].id, traderMBs[1].id]
		# and replay this trade
		self._tradeStep2( traderMBs[0], trade[ "paramsA" ], traderMBs[1],
			trade[ "paramsB" ] )


	def _readyToGo( self ):
		self.replaying = False
		# tell everyone that they can start playing again
		# FantasyDemo._readyToGo += 1 ... or something


	def commenceTrade( self, A, paramsA, B, paramsB ):

		if self._hasPendingTrade( A.id, B.id ):
			A.tradeSyncReject()
			return

		tradeLog = { "typeA": A.className, "paramsA": paramsA,
					"typeB": B.className, "paramsB": paramsB }

		self.recentTrades.append( tradeLog )
		self.outstandingTrades.append( [A.id, B.id] )

		def doTradeStep2( *args ):
			self._tradeStep2( A, paramsA, B, paramsB )
		self.writeToDB( doTradeStep2 )


	def _tradeStep2( self, A, paramsA, B, paramsB ):

		A.tradeCommit(
			self, paramsA[ "tradeID" ], paramsA[ "lockHandle" ],
			paramsA[ "itemsSerials" ], paramsA[ "goldPieces" ],
			paramsB[ "itemsTypes" ], paramsB[ "goldPieces" ] ,
			B)
		B.tradeCommit(
			self, paramsB[ "tradeID" ], paramsB[ "lockHandle" ],
			paramsB[ "itemsSerials" ], paramsB[ "goldPieces" ],
			paramsA[ "itemsTypes" ], paramsA[ "goldPieces" ] ,
			A)


	def completeTrade( self, who, tradeID ):
		#~ print "completeTrade", who.id, tradeID
		# go through our outstanding trades and find the right one,
		# and if it is complete, remove it as well as removing the
		# corresponding element from recentTrades

		nost = []
		for t in self.outstandingTrades:
			completedTrade = None

			if t[0] == who.id:
				if t[1] == 0:
					completedTrade = self.recentTrades.pop(len(nost))
					#~ print "TradingSupervisor: trade complete by A"
				else:
					nost.append( [0,t[1]] )
			elif t[1] == who.id:
				if t[0] == 0:
					completedTrade = self.recentTrades.pop(len(nost))
					#~ print "TradingSupervisor: trade complete by B"
				else:
					nost.append( [t[0],0] )
			else:
				nost.append( t )

			if completedTrade:
				# Trader is the one with the items
				if completedTrade['paramsA']['itemsTypes']:
					(trader, reciever) = ("A", "B")
				else:
					(trader, reciever) = ("B", "A")

				msg = "Trade %d complete. %s (dbID=%d) traded item types "	\
					   "%s to %s (dbID=%d) for %d gold pieces" %			\
					   (tradeID,											\
						completedTrade['type'+trader],						\
						completedTrade['params'+trader]['dbID'],			\
						completedTrade['params'+trader]['itemsTypes'],		\
						completedTrade['type'+reciever],					\
						completedTrade['params'+reciever]['dbID'],			\
						completedTrade['params'+reciever]['goldPieces'] )	
				XMPPEventNotifier.broadcast( msg )

		self.outstandingTrades = nost
		# don't bother writing it to the DB... we can do that when we get the
		# next trade

		if self.replaying and len(self.recentTrades) == 0:
			self.writeToDB()	# write out the cleared list for sanity
			self._readyToGo()


	def _hasPendingTrade( self, AID, BID = -1 ):
		if BID != -1:
			for trade in self.outstandingTrades:
				if AID in trade or BID in trade:
					return True
		else:
			for trade in self.outstandingTrades:
				if AID in trade:
					return True
		return False


	def isAPendingTrade( self, avatarID, lockHandle ):
		for i, trade in enumerate( self.outstandingTrades ):
			recentTrade = self.recentTrades[i]
			if trade[0] == avatarID and recentTrade[ "paramsA" ][ "lockHandle" ] == lockHandle:
				return True
			elif trade[1] == avatarID and recentTrade[ "paramsB" ][ "lockHandle" ] == lockHandle:
				return True
		return False


	def onRestore( self ):
		# In BW1.6, our fault tolerance copy could be older than our
		# copy in the database, so we destroy then get ourself back
		# from the database
		print "TradingSupervisor %d/dbID=%d onRestore: recreating from DB" % \
			(self.id, self.databaseID)
		dbID = self.databaseID # save this away before we destroy
		self.destroy( writeToDB=False )

		class RecreateFromDBCallback( object ):
			def __init__( self ):
				self.retriesMax = 5
				self.retries = 0

			def __call__( self, result, dbID, wasActive ):
				if not result is None and wasActive:
					# This can happen if the database was in the middle of
					# TradingSupervisor was in the middle of logging off due to
					# the destroy call above when it gets the request to create
					# TradingSupervisor. Keep trying a few more times.
					print "TradingSupervisor(id=%d, dbID=%d) " \
							"still not destroyed, retry #%d" % \
						(result.id, dbID, self.retries + 1)
					if self.retries < self.retriesMax:
						BigWorld.createBaseAnywhereFromDBID( 
							"TradingSupervisor", dbID, self )
						self.retries += 1
					else:
						print "TradingSupervisor(dbID=%d): "\
								"Could not recreate TradingSupervisor after " \
								"%d retries" % \
							self.retries

				elif result is None:
					print "Could not recreate TradingSupervisor due to DB error"
				else:
					print "Recreated TradingSupervisor(id=%d,dbID=%d) " \
							"successfully" % \
						(result.id, dbID)

		BigWorld.createBaseAnywhereFromDBID( "TradingSupervisor", 
			dbID, RecreateFromDBCallback() )
	
	def onOnload( self ):
		print "TradingSupervisor %d/dbID=%d onOnload: resuming operation" % \
			(self.id, self.databaseID)


# -------------------------------------------------------------------------
# Initialisation and destruction of the supervisor
# -------------------------------------------------------------------------

def wakeupTradingSupervisor():
	"""
	Wakes the TradingSupervisor singleton.
	"""

	def checkLoadFromDB( result, dbID, wasActive ):
		if result:
			print 'TradingSupervisor loaded from DB'
		else:
			# Create new TradingSupervisor.
			BigWorld.createBaseAnywhere( 'TradingSupervisor' )
			print 'Creating new TradingSupervisor'

	# Check for the existing TradingSupervisor singleton, create it if
	# necessary.
	if not BigWorld.globalBases.has_key( 'TradingSupervisor' ):
		# Try loading supervisor from database.

		BigWorld.createBaseFromDB( 'TradingSupervisor', 'TradingSupervisor',
			checkLoadFromDB )


def destroyTradingSupervisor():
	"""
	Destroy the singleton instance of TradingSupervisor.
	"""
	if BigWorld.globalBases.has_key( 'TradingSupervisor' ):
		# delete supervisor from DB on controlled shutdown
		supervisor = BigWorld.globalBases[ 'TradingSupervisor' ]
		if BigWorld.entities.has_key( supervisor.id ):
			supervisor.cleanup()

# TradingSupervisor.py
