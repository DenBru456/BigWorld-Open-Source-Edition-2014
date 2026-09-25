
def iterable( primitiveOrIterable ):
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
# iterable

