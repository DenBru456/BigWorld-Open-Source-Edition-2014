'''This module contains a number of helper functions intended simplify
implementing callback functions in a safe way.
'''

import BigWorld

def IgnoreCallbackIfDestroyed( function ):
	def checkIfDestroyed( self, *args, **kwargs ):
		assert isinstance( self, BigWorld.Entity )
		if not self.isDestroyed:
			return function( self, *args, **kwargs )
		else:
			pass
			#print "Call to function '%s' was ignored because %s %d has been destroyed." % (str(function.__name__), str(type(self).__name__), self.id)

	return checkIfDestroyed





