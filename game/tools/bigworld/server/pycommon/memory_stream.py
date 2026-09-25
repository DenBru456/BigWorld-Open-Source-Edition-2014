"""
Basically an implementation of MemoryOStream from network/memory_stream.hpp.  We
need this because machined writes packets using these classes so Python tools
need to be able to speak this too.
"""

import struct
from StringIO import StringIO

class MemoryStream( StringIO ):

	def __init__( self, buf = "" ):
		StringIO.__init__( self, buf )

	def pack( self, *args ):
		"""
		The args to this method need to be either tuples that would be passed to
		struct.pack() or plain strings (which will be packed according to the
		variable length BinaryStream format).  This is basically supposed to
		implement the << operator.  eg:

		ms.pack( ('BII', 1, 2, 3), 'Hello world!', ('f', 0.123) )
		"""

		for a in args:
			if type( a ) == tuple:
				fmt, params = (self._pack1( a[0] ), a[1:])
				self.write( struct.pack( fmt, *params ) )
			else:
				if len( a ) >= 255:
					self.write( struct.pack( "I", (len( a ) << 8) | 0xff) )
				else:
					self.write( struct.pack( "B", len( a ) ) )
				self.write( a )

	def unpack( self, *args ):
		"""
		The args to this either need to be struct.pack()-style formats or the
		single string 's' to indicate a variable length BinaryStream string.
		This implements the >> operator.  eg:

		ms.unpack( 'BII', 's', 'f' ) -> [ 1, 2, 3, 'Hello world!', 0.123 ]
		"""

		ret = []
		for fmt in args:
			if fmt == "s":
				size = ord( self.read( 1 ) )
				if size == 0xff:
					size, = struct.unpack( "I", self.read( 3 ) + chr( 0 ) )
				data = self.read( size )
				self._checkSize( data, size, fmt )
				ret.append( data )
			else:
				fmt = self._pack1( fmt )
				size = struct.calcsize( fmt )
				data = self.read( size )
				self._checkSize( data, size, fmt )
				for i in struct.unpack( fmt, data ):
					ret.append( i )
		return ret

	def peek( self ):
		"""
		Tries to return the next character to be read from the stream
		"""

		mark = self.tell()
		byte, = struct.unpack( "B", self.read( 1 ) )
		self.seek( mark )
		return byte

	def data( self ):
		"""
		For similarity to C++ void * MemoryOStream::data()
		"""
		return self.getvalue()

	def remainingLength( self ):
		return self.len - self.tell()

	def _pack1( self, fmt ):
		"""
		Make struct formats compatible with #pragma pack 1
		"""

		if fmt[0] != "=":
			return "=" + fmt
		else:
			return fmt

	def _checkSize( self, s, size, fmt ):
		if len( s ) < size:
			raise self.error, "Only %d bytes on stream for fmt %s (needed %d)" \
				  % (len( s ), fmt, size)

	def calculateStreamedSize( self, s ):
		strLen = len( s )
		if strLen >= 0xff:
			return 4 + strLen
		else:
			return 1 + strLen

	class error( Exception ):
		def __init__( self, s = "" ):
			Exception.__init__( self, s )

# Test code
if __name__ == "__main__":
	m = MemoryStream()
	m.pack( "HelloWorld" * 100, ("BBI", 1, 2, 3) )
	m.seek( 0 )
	try:
		print m.unpack( "s", "BBI" )
	except MemoryStream.error, e:
		print "Got exception:", e
