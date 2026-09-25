import re

class VersionFileParser( object ):
	"""
	Class to parse the bwversion header file.
	"""

	def __init__( self, versionFilePath ):
		"""
		Constructor.

		@param versionFilePath 	The path to the bwversion.hpp file.
		"""
		self.major = None
		self.minor = None
		self.patch = None

		self._processVersionHeader( versionFilePath )
		self._validate()


	def _processVersionHeader( self, versionFilePath ):
		fp = open( versionFilePath )

		for line in fp:
			match = re.match( "#define *BW_VERSION_(\w+) *(\d+)", line )
			if match:
				if match.group( 1 ) == "MAJOR":
					self.major = match.group( 2 )

				elif match.group( 1 ) == "MINOR":
					self.minor = match.group( 2 )

				elif match.group( 1 ) == "PATCH":
					self.patch = match.group( 2 )

				else:
					print "WARNING: unexpected BW_VERSION match in:", line

		fp.close()


	def _validate( self ):
		if self.major is None:
			raise ValueError, "Missing element for major version"
		elif self.minor is None:
			raise ValueError, "Missing element for minor version"
		elif self.patch is None:
			raise ValueError, "Missing element for patch version"

# version_file_parser.py
