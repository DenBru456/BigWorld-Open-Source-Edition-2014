
class AuthenticationException( Exception ):
	""" Indicates that the credentials supplied by the user are invalid for the
		requested resource or method """
	pass


class AuthorisationException( AuthenticationException ):
	""" Indicates that the current user does not have the required permissions
		for the requested resource or method. """
	pass


class ServerStateException( Exception ):
	""" Indicates that the current state of the BigWorld server is incompatible
		with the state required to fulfill a given request. """
	pass


class ConfigurationException( Exception ):
	""" Indicates that a BigWorld component or tool is not correctly configured. """
	pass


class NotSupportedException( Exception ):
	""" Indicates that a requested feature or library is not supported in the
	current environment. """
	pass


class QueryParamException( Exception ):
	"""
	Indicates that a provided query parameter was not valid.
	"""

	def __init__( self, message = None, paramName = None, paramValue = None ):

		if not message:
			message = "Invalid value for param '%s': %r" % (paramName, paramValue)

		Exception.__init__( self, message )
		self.paramName = paramName
		self.paramValue = paramValue
	# __init__

# end class QueryParamException


class IllegalArgumentException( Exception ):
	"""
	Indicates that a method argument was not valid.
	"""

	def __init__( self, message = None, argName = None, argValue = None ):

		if not message:
			message = "Invalid value for argument '%s': %r" % (argName, argValue)

		Exception.__init__( self, message )
		self.argName = argName
		self.argValue = argValue
	# __init__

# end class IllegalArgumentException

