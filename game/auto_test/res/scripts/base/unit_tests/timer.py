from test_case import TestCase
from test_case import fail_on_exception

import BigWorld

class TimerTest( TestCase ):
	def run( self ):
		self.timerID = BigWorld.addTimer( self.onTimer, 0.2 )

	@fail_on_exception
	def onTimer( self, id, userData ):
		self.assertEqual( self.timerID, id )
		self.assertEqual( 0, userData )
		self.finishTest()

# timer.py
