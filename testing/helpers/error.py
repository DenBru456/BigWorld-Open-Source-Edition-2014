"""Module for user-defined exceptions
"""

class HelperError( Exception ):
	""" Base class for helper exceptions """
	
	def __init__(self, value):
		"""Constructor.
		@param value: User-defined value for the exception
		"""
		self.value = value

	def __str__( self ):
		return repr(self.value)	
