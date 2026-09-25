import BigWorld
from Recorder import Recorder

class TestRecorder( BigWorld.Base, Recorder ):

	def __init__( self ):
		BigWorld.Base.__init__( self )
		Recorder.__init__( self )

		if not hasattr( self, "cell" ):
			self.createInNewSpace( shouldPreferThisMachine = False )


# TestRecorder.py
