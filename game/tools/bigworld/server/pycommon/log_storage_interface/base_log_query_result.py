class BaseLogQueryResult( object ):
	"""This class provides the common base implementation for the storage
	abstractions to use. Primarily it is to ensure that the asDict() method is
	implemented by the storage result classes. It is also used to provide a
	common method of outputting log messages to a stream."""

	def writeToStream( self, outputStream, showMetadata = False ):
		"""This method is used to write an individual log message result to
		the desired output stream. The output stream may change depending on
		where it is called from."""

		logDict = self.asDict()

		outputStream.write( logDict[ 'message' ] )
		if showMetadata:
			# Only attempt to get metadata if we are showing it
			metadata = logDict[ 'metadata' ]

			if metadata:
				# it's possible the de-jsonification from MLDB may have failed.
				# check whether it is a dict first, otherwise print it as a
				# string.
				if type( metadata ) == dict:
					outputStream.write( "{\n" )
					for key, value in metadata.items():
						outputStream.write( "  " + str( key ) + ": " \
							+ str( value ) + ",\n" )
					outputStream.write( "}\n" )

				else:
					outputStream.write( str( metadata ) )
	# writeToStream


	#
	# Abstract functions - must be implemented by subclasses
	#

	def asDict( self ):
		"""This method is used to return the results as a dictionary."""

		raise NotImplementedError(
			"BaseLogQueryResults.asDict method not implemented. "
			"Unable to call abstract method." )
	# asDict

# BaseLogQueryResult
