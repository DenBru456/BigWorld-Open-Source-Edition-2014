import BigWorld
from Recorder import Recorder


class TestRecorder( BigWorld.Entity, Recorder ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		Recorder.__init__( self )


	def onDestroy( self ):
		Recorder.onDestroy( self )

# TestRecorder.py
