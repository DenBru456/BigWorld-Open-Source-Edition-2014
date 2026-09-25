import Math

class Cursor:
	def __init__( self ):
		self.visible = False

class Simple:
	def __init__( self, *args ):
		self.children = []
		self.position = Math.Vector3()
		self.height = 0
		self.width = 0
	
	def __getattr__( self, name ):
		return Simple()
	
	def delChild( self, name ):
		pass


	def addChild( self, *args ):
		pass
	
	def __call__( self, *args ):
		pass
	
	def __hash__( self ):
		return 0

Frame   = Simple
Text    = Simple
Latency = Simple
BoundingBox = Simple

def load( name ):
	return Simple()

def addRoot( *args ):
	pass

def reSort( *args ):
	pass

def mcursor( *args ):
	return Cursor()

