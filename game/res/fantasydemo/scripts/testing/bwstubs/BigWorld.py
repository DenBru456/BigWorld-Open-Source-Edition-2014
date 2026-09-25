import Math
import Inventory
import AvatarMode

class Base:
	def __init__( self ):
		self.id          = 1
		self.databaseID  = 1
		self.lastTradeID = 1

		self.globalName   = ''
		self.playerName   = ''
		self.recentTrades = []
				
		self.inventoryItems = [
			{ "itemType": 4, "serial": 12, "lockHandle": Inventory.NOLOCK }, 
			{ "itemType": 6, "serial": 13, "lockHandle": Inventory.NOLOCK },
			{ "itemType": 4, "serial": 15, "lockHandle": Inventory.NOLOCK } ]
			
		self.inventoryLocks = []
		self.inventoryGoldPieces  = 100
		
	def writeToDB( self, callback = None ):
		if callback:
			callback( True, self )
	
	def registerGlobally( self, globalName, callback = None ):
		self.globalName = 'globalName'
		if callback:
			callback( self )
	
Proxy = Base

class Entity:
	def __init__( self ):
		self.inWorld     = True
		self.physics     = Physics()
		self.tracker     = Tracker()
		self.model       = Model( '' )
		self.matrix      = Math.Matrix()
		self.rightHand   = None
		self.mode        = -1
		self.id          = 1
		self.modeTarget  = AvatarMode.NO_TARGET
		self.health      = 100
		self.maxHealth   = 100
		self.entityDirProvider = None
		self.tradeOutboundLock = -1
		self.tradeSelfAccepted = False
		self.tradePartnerAccepted = False

		self.inventoryItems = [
			{ "itemType": 4, "serial": 12, "lockHandle": Inventory.NOLOCK }, 
			{ "itemType": 6, "serial": 13, "lockHandle": Inventory.NOLOCK },
			{ "itemType": 4, "serial": 15, "lockHandle": Inventory.NOLOCK } ]
			
		self.inventoryLocks = []
		self.inventoryGoldPieces  = 100
	
	def addProximity( self, range ):
		pass

class ActionMatcher:
	def __init__( self, entity ):
		self.matchCaps = []

class Action:
	def __init__( self ):
		self.duration = 0
		self.blendOutTime = 0
		self.seekInv = Math.Matrix()
	
	def __call__( self ):
		return Model( '' )

class Model:
	def __init__( self, name ):
		self.queue = []
		self.Shrug           = Action()
		self.ChangeItemBegin = Action()
		self.ChangeItemEnd   = Action()
		self.Shake_A_Extend  = Action()
		self.Shake_A_Accept  = Action()
		self.Shake_B_Extend  = Action()
		self.Shake_B_Accept  = Action()
		self.bounds          = Math.Matrix()

class Physics:
	def __init__( self ):
		self.seeking = False
		self.chasing = False
	
	def seek( self, matrix, vel, dist, callback ):
		callback( True )

class Tracker:
	def __init__( self ):
		self.directionProvider = None

class FlexiCam:
	def __init__( self ):
		pass
	
def player():
	global _player
	return _player

def target():
	global _target
	return _target

def entity( *args ):
	return None

def camera( *args ):
	return None

def setCursor( *args ):
	pass

def getRegister( *args ): 
	pass

def addWatcher( *args ): 
	pass

def time():
	return 0

def callback( time, func ):
	pass

def lookUpBaseByName( type, name, callback ):
	callback( False )

# ---

entities = {}

# ---

def test_setPlayer( player ):
	global _player
	_player = player

_player = None


def test_setTarget( target ):
	global _target
	_target = target

_target = None