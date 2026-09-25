import BigWorld

class TestEntity( BigWorld.Entity ):

	def __init__( self ):
		self.chatMsg = None
		self.chatLODMsg = None

	def chat( self, msg ):
		self.chatMsg = msg

	def chatLOD( self, msg ):
		self.chatLODMsg = msg