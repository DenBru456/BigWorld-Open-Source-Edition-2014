
import os
import sys
import unittest

# add to python path
bw_res_path = os.environ[ 'BW_RES_PATH' ]
paths = bw_res_path.split( ';' )
for path in paths:
	sys.path.append( r'%s\entities\client' % path  )
	sys.path.append( r'%s\entities\common' % path  )
	sys.path.append( r'%s\entities\testing\bwstubs' % path  )


import BigWorld
import base.Avatar as Avatar
import base.TradingSupervisor as TradingSupervisor


class BaseAvatarStub:

	REPLY_ACTIONS = (
		COUNT,
		DENY,
		ACCEPT,
		FAIL ) = range(4)

	def __init__( self, id ):
		self.id = id
		self.commitReply = BaseAvatarStub.COUNT
		self.commitCount = 0
	
	def tradeCommit( self, supervisor, tradeID, lockHandle,
			outItemsSerials, outGoldPieces, 
			inItemsTypes, inGoldPieces ):
		if self.commitReply == BaseAvatarStub.COUNT:
			self.commitCount += 1
		elif self.commitReply == BaseAvatarStub.ACCEPT:
			supervisor.completeTrade( self, tradeID )


class TradingSupervisorTest( unittest.TestCase ):

	def setUp( self ):
		self.super = TradingSupervisor.TradingSupervisor()
		self.avatar1 = BaseAvatarStub( 1 )
		self.avatar2 = BaseAvatarStub( 2 )


	def testCommenceTradeCount( self ):
		tradeParams1 = { "dbID": self.avatar1.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 25	}
		tradeParams2 = { "dbID": self.avatar2.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 50	}
		result = self.super.commenceTrade( 
			self.avatar1, tradeParams1, self.avatar2, tradeParams2 )
		self.assert_( result == True )
		self.assert_( self.avatar1.commitCount == 1 )
		self.assert_( self.avatar2.commitCount == 1 )
		print self.super.outstandingTrades
		self.assert_( self.super.outstandingTrades == 
				[[self.avatar1.id, self.avatar2.id]] )


	def testCommenceTradeFalse( self ):
		tradeParams1 = { "dbID": self.avatar1.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 25	}
		tradeParams2 = { "dbID": self.avatar2.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 50	}
		result1 = self.super.commenceTrade( 
			self.avatar1, tradeParams1, self.avatar2, tradeParams2 )
		result2 = self.super.commenceTrade( 
			self.avatar1, tradeParams1, self.avatar2, tradeParams2 )
		self.assert_( result1 == True )
		self.assert_( result2 == False )
		self.assert_( self.avatar1.commitCount == 1 )
		self.assert_( self.avatar2.commitCount == 1 )
		print self.super.outstandingTrades
		self.assert_( self.super.outstandingTrades == 
				[[self.avatar1.id, self.avatar2.id]] )


	def testCommenceTradeComplete( self ):
		self.avatar1.commitReply = BaseAvatarStub.ACCEPT
		self.avatar2.commitReply = BaseAvatarStub.ACCEPT
		tradeParams1 = { "dbID": self.avatar1.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 25	}
		tradeParams2 = { "dbID": self.avatar2.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 50	}
		result = self.super.commenceTrade( 
			self.avatar1, tradeParams1, self.avatar2, tradeParams2 )
		self.assert_( self.super.outstandingTrades == [] )
		self.assert_( result == True )


	def testIsAPendingTrade( self ):
		tradeParams1 = { "dbID": self.avatar1.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 25	}
		tradeParams2 = { "dbID": self.avatar2.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 50	}
		self.super.commenceTrade( 
			self.avatar1, tradeParams1, self.avatar2, tradeParams2 )
		result1 = self.super.isAPendingTrade( self.avatar1.id, 1 )
		result2 = self.super.isAPendingTrade( self.avatar1.id, 2 )
		result3 = self.super.isAPendingTrade( self.avatar1.id + 100, 1 )
		result4 = self.super.isAPendingTrade( self.avatar1.id + 100, 2 )
		result5 = self.super.isAPendingTrade( self.avatar2.id, 1 )
		result6 = self.super.isAPendingTrade( self.avatar2.id, 2 )
		self.assert_( result1 == True )
		self.assert_( result2 == False )
		self.assert_( result3 == False )
		self.assert_( result4 == False )
		self.assert_( result5 == True )
		self.assert_( result6 == False )


	def testIsAPendingTradeComplete( self ):
		self.avatar1.commitReply = BaseAvatarStub.ACCEPT
		self.avatar2.commitReply = BaseAvatarStub.ACCEPT
		tradeParams1 = { "dbID": self.avatar1.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 25	}
		tradeParams2 = { "dbID": self.avatar2.id, \
						"tradeID": 1, \
						"lockHandle": 1, \
						"itemsSerials": [], \
						"itemsTypes": [], \
						"goldPieces": 50	}
		self.super.commenceTrade( 
			self.avatar1, tradeParams1, self.avatar2, tradeParams2 )
		result1 = self.super.isAPendingTrade( self.avatar1.id, 1 )
		result2 = self.super.isAPendingTrade( self.avatar2.id, 1 )
		self.assert_( result1 == False )
		self.assert_( result2 == False )


if __name__ == '__main__':
    unittest.main()
