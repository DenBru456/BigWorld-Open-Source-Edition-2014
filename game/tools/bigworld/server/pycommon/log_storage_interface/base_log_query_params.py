"""
This class provides an abstract method for setting, validating and iterating
over supplied log qurey parameters.

The validation and formatting of the parameters will be uniquely specific to
each datastore and will never be exposed outside of the implementation layer.

Consequently this class does not necessarily need to be implemented for every DB
storage method derived from BaseLogReader and BaseLogQuery (as the class is
never exposed outside of the implementation layer).

However it is still recommended to follow this structure if possible.
"""

class BaseLogQueryParams( object ):
	"""
	As derived instances of this class are never exposed outside of the
	implementation layer, it is up to each implementation layer to provide
	their own initialisation routine with whatever args/kwargs are necessary for
	the datastore.

	For example:
	def __init__( self, logReader, params ):
	"""


	@classmethod
	def iterateParam( primitiveOrIterable ):
		"""
		A convenience method to return an iterable object from a collection type
		or scalar value, with the important exception that strings are treated
		as scalars not collections.
		"""

		try:
			# if string or unicode, treat as singleton scalar
			if isinstance( primitiveOrIterable, basestring ):
				raise ValueError( 'avoid iterating over strings' )

			for it in primitiveOrIterable:
				yield it
		except:
			yield primitiveOrIterable
		raise StopIteration()
	# iterateParam

# BaseLogQueryParams
