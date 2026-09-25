"""
This module allows the easy creation of a timed cache of objects
of a specified class type. Items are cached in a list, keeping one item for
each matching set of keyword pairs, and will expire after a set timeout.

The only requirement for the class is that its __init__ function accepts no
arguments (other than self) or only accepts ( self, **kw ).

Even if the class does not accept **kw arguments, the **kw argument (if
provided) is still used to match cached objects.
"""

import threading
import time

DEFAULT_CACHE_TIMEOUT = 1.0


class _ExpiringCacheItem( object ):
	""" This is an object wrapper which allows it to be cached by keywords and
	to maintain a creation time against which it can expire. """

	def __init__( self, cachedObject, kw ):
		self.cachedObject = cachedObject
		self._kw = kw
		self._time = time.time()
	# __init__


	def matches( self, kw ):
		return kw == self._kw
	# matches


	def isOld( self, timeout ):
		return ((time.time() - self._time) > timeout)
	# isOld

# _ExpiringCacheItem


class ExpiringCache( object ):
	""" A timed cache of objects of the specified class. """

	
	def __init__( self, cachedClass, timeout = DEFAULT_CACHE_TIMEOUT ):
		"""
		@param cachedClass	The class of objects being cached.
		@param timeout		The length of time to keep and reuse cache objects.
							Defaults to 1 second.
		"""

		self._items = []
		self._lock = threading.RLock()
		self._cachedClass = cachedClass
		self.timeout = float( timeout )
	# __init__


	def _expunge( self ):
		"""
		Clears out-of-date items in the cache.
		"""

		self._items = [item for item in self._items
					   if not item.isOld( self.timeout )]
	# _expunge

	
	def get( self, **kw ):
		"""
		Factory method that accepts the same params as the constructor.  Use
		this if you want to recycle items that are being created in
		quick succession.

		@param kw			The keywords with which to match the item, and to
							be passed on to the cached object's constructor.
		"""

		try:
			self._lock.acquire()
			self._expunge()

			# Try to find a cache object that is new enough
			for item in self._items:
				if item.matches( kw ):
					return item.cachedObject

			newObject = self._cachedClass( **kw )
			self._add( _ExpiringCacheItem( newObject, kw ) )
			return newObject

		finally:
			self._lock.release()
	# get


	def _add( self, item ):
		"""
		Adds the specified item to the cached list of items
		"""
		self._lock.acquire()
		self._expunge()
		self._items.append( item )
		self._lock.release()
	# _add

# ExpiringCache


