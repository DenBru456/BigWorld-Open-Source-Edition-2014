"This module implements the InscrutableMachine entity."

import BigWorld

# ------------------------------------------------------------------------------
# Section: class InscrutableMachine
# ------------------------------------------------------------------------------

class InscrutableMachine( BigWorld.Entity ):
	"An InscrutableMachine entity."

	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def switched( self, desiredState ):
		print "InscrutableMachine::switched to", desiredState
		self.machineState = desiredState

# InscrutableMachine.py
