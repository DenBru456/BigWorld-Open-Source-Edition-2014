import logging
import re

log = logging.getLogger( __name__ )

# ------------------------------------------------------------------------------
# Section: Exposed
# ------------------------------------------------------------------------------

class ExposedType( type ):
	"""
	This is a metaclass used by Exposed (below) to assist with the static
	tracking of member methods marked with @expose.
	"""

	def __init__( cls, *args, **kw ):

		type.__init__( cls, *args, **kw )

		# Track marked exposed methods
		cls.s_exposedMethods = []
		for superclass in cls.__mro__:
			for name, meth in superclass.__dict__.items():
				if hasattr( meth, "exposedLabel" ):
					cls.s_exposedMethods.append( name )


class Exposed( object ):
	"""
	This is the exposed capabilties interface for cluster objects.  Classes
	wishing to expose methods using this interface should decorate their methods
	with the @expose function defined below.

	Any derived class that wishes to provide random-esque access to its
	instances (i.e. the Web Console's root controller callExposed() method) must
	also implement getExposedID().  getExposedID() should return enough
	information to reacquire a reference to the object later on.
	"""

	__metaclass__ = ExposedType


	def __json__( self ):
		if hasattr( self, '__dict__' ):
			return self.__dict__
		else:
			log.warning( "Cannot convert object %s to json, returning None", self )
			return None
	# __json__


	@staticmethod
	def expose( label = None, args = [], precond = lambda self: True ):
		"""
		Decorator used to expose a method of an Exposed derived class.

		A user-defined label can be supplied for the method, or a name based on
		the function name will be inferred instead.

		If the method takes any arguments, they should be passed as a list of
		(name, description) tuples.  This list is used in interactive apps to
		prompt the user for input values.  The method should expect these values
		to be passed as strings irrespective of their intrinsic type.

		A precondition for this method's execution can also be supplied, which
		MUST BE a method that accepts a single argument (the instance itself).
		"""

		# We tag the decorated method with attributes that are used by init() to
		# actually populate the static list with the exposed methods
		def inner( f, label = label, args = args, precond = precond ):
			f.exposedPrecond = precond
			f.exposedArgs = args

			if label is None:
				label = re.sub( "[A-Z]", lambda m: " " + m.group( 0 ),
								f.__name__ )
				label = re.sub( "^[a-z]", lambda m: m.group( 0 ).upper(),
								label )

			f.exposedLabel = label

			return f

		return inner


	def getExposedMethods( self ):
		methods = []
		for funcname in self.s_exposedMethods:
			func = getattr( self, funcname )
			if func.exposedPrecond( self ):
				methods.append( (func.__name__,
								 func.exposedLabel,
								 func.exposedArgs) )
		return methods


	def getExposedID( self ):
		log.critical( "You really need to implement getExposedID() for %s",
					  self.__class__.__name__ )

# exposed.py
