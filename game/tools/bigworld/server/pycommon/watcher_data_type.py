#!/usr/bin/env python

import struct
from cStringIO import StringIO

def BW_PACK3( dataLen ):
	if dataLen >= 255:
		return struct.pack( "<I", (dataLen << 8) | 0xff)
	else:
		return struct.pack( "B", dataLen )

def BW_UNPACK3( fileObj ):
	"""
	Unpacks size. Only usable on a filelike object like StringIO.
	"""
	sizeStr = fileObj.read( 1 )
	if ord( sizeStr ) != 0xff:
		return ord( sizeStr )
	else:
		(size,) = struct.unpack( "<I", fileObj.read(3) + chr(0) )
		return size


# from watcher import Constants
import watcher_constants as Constants


# Constants
# -----------------------------------------------------------------------------
# TODO: Remove these and use Constants
WATCHER_TYPE_UNKNOWN    = Constants.TYPE_UNKNOWN
WATCHER_TYPE_INT        = Constants.TYPE_INT
WATCHER_TYPE_UINT       = Constants.TYPE_UINT
WATCHER_TYPE_FLOAT      = Constants.TYPE_FLOAT
WATCHER_TYPE_BOOL       = Constants.TYPE_BOOL
WATCHER_TYPE_STRING     = Constants.TYPE_STRING
WATCHER_TYPE_TUPLE      = Constants.TYPE_TUPLE
WATCHER_TYPE_TYPE       = Constants.TYPE_TYPE

def toString( typeNum ):
	result = None
	if (typeNum == WATCHER_TYPE_UNKNOWN):
		result = "Unknown"
	elif (typeNum == WATCHER_TYPE_INT):
		result = "Int"
	elif (typeNum == WATCHER_TYPE_UINT):
		result = "Unsigned Int"
	elif (typeNum == WATCHER_TYPE_FLOAT):
		result = "Float"
	elif (typeNum == WATCHER_TYPE_BOOL):
		result = "Bool"
	elif (typeNum == WATCHER_TYPE_STRING):
		result = "String"
	elif (typeNum == WATCHER_TYPE_TUPLE):
		result = "Tuple"
	elif (typeNum == WATCHER_TYPE_TYPE):
		result = "Type"
	else:
		result = "No matching watcher type %d" % typeNum

	return result


# Constants
# -----------------------------------------------------------------------------
class WatcherDataType( object ):
	def __init__( self, value=None ):
		self.value = None
		if value != None:
			self.set( value )

	def toStream( self ):
		raise NotImplemented

	def set( self, x ):
		raise NotImplemented

	def fromStream( self, data ):
		raise NotImplemented

	@classmethod
	def asStr( cls, val ):
		return str( val )

	@classmethod
	def unpack( cls, s ):
		wdt = cls()
		wdt.fromStream( s )
		return wdt



class WatcherDataTypeUnknown( WatcherDataType ):
	"""Data type corresponding to the Watcher Protocol (v2) data type
	   enumeration WATCHER_TYPE_UNKNOWN (0). This type is essentially a
	   place holder in order to deal with anything that is streamed onto
       onto the network that we don't know about."""
	type = WATCHER_TYPE_UNKNOWN


	def fromStream( self, data ):
		self.value = None

	def __repr__(self):
		return "<WDT Unknown %s>" % str(None)


class WatcherDataTypeInt( WatcherDataType ):
	"""Data type corresponding to the Watcher Protocol (v2) data type
	   enumeration WATCHER_TYPE_INT (1). This type can represent either
	   a 32 bit integer or a 64 bit integer depending on the size prefix
	   on the stream."""
	type = WATCHER_TYPE_INT


	def set( self, x ):
		self.value = int(x)

	def toStream( self ):
		assert self.value != None, "Value must be set before converting to stream"
		data = StringIO()
		# Pack our type on
		data.write( struct.pack( "<B", self.type ) )
		# Now the size and the actual data
		if self.value > 0xffff:
			data.write( BW_PACK3( 8 ) )
			data.write( struct.pack( "<q", self.value ) )
		else:
			data.write( BW_PACK3( 4 ) )
			data.write( struct.pack( "<i", self.value ) )
		return data.getvalue()


	def fromStream( self, data ):
		assert len(data) in (4,8), "Int type must be 4 or 8 bytes long"
		if len(data) == 4:
			(value,) = struct.unpack( "<i", data )
		elif len(data) == 8:
			(value,) = struct.unpack( "<q", data )
		self.value = value

	def __repr__(self):
		return "<WDT Int %d>" % (self.value)



class WatcherDataTypeUInt( WatcherDataType ):
	"""Data type corresponding to the Watcher Protocol (v2) data type
	   enumeration WATCHER_TYPE_UINT (2). This type can represent either
	   a 32 bit integer or a 64 bit integer depending on the size prefix
	   on the stream."""
	type = WATCHER_TYPE_UINT


	def set( self, x ):
		self.value = int(x)

	def toStream( self ):
		assert self.value != None, "Value must be set before converting to stream"
		data = StringIO()
		# Pack our type on
		data.write( struct.pack( "<B", self.type ) )
		# Now the size and the actual data
		if self.value > 0xffff:
			data.write( BW_PACK3( 8 ) )
			data.write( struct.pack( "<Q", self.value ) )
		else:
			data.write( BW_PACK3( 4 ) )
			data.write( struct.pack( "<I", self.value ) )
		return data.getvalue()


	def fromStream( self, data ):
		assert len(data) in (4,8), "UInt type must be 4 or 8 bytes long"
		if len(data) == 4:
			(value,) = struct.unpack( "<I", data )
		elif len(data) == 8:
			(value,) = struct.unpack( "<Q", data )
		self.value = value

	def __repr__(self):
		return "<WDT UInt %d>" % (self.value)


class WatcherDataTypeFloat( WatcherDataType ):
	"""Data type corresponding to the Watcher Protocol (v2) data type
	   enumeration WATCHER_TYPE_FLOAT (3). This type can represent either
	   a float (32 bit) or a double (64 bit) depending on the size prefix
	   on the stream."""

	type = WATCHER_TYPE_FLOAT

	def set(self, val):
		self.value = float(val)

	@classmethod
	def asStr( cls, val ):
		return "%.4f" % val

	def toStream( self ):
		assert self.value != None, "Value must be set before converting to stream"
		data = StringIO()
		# Pack our type on
		data.write( struct.pack( "<B", self.type ) )

		# Now the size and the actual data
		# NB: we always send floating point numbers across as 8 bytes (doubles)
		#     and cast back to floats if required in C.
		data.write( BW_PACK3( 8 ) )
		data.write( struct.pack( "<d", self.value ) )

		return data.getvalue()


	def fromStream( self, data ):
		assert len(data) in (4,8), "Float type must be 4 or 8 bytes long"
		if len(data) == 4:
			(value,) = struct.unpack( "<f", data )
		elif len(data) == 8:
			(value,) = struct.unpack( "<d", data )
		self.value = value


	def __repr__(self):
		return "<WDT Float %f>" % (self.value)



class WatcherDataTypeBool( WatcherDataType ):
	"""Data type corresponding to the Watcher Protocol (v2) data type
	   enumeration WATCHER_TYPE_BOOL (4)."""

	type = WATCHER_TYPE_BOOL


	def set(self, val):
		if isinstance(val, str):
			if val.lower() == "false":
				self.value = False
			elif val.lower() == "true":
				self.value = True
			else:
				self.value = None
		else:
			self.value = bool(val)


	def toStream( self ):
		assert self.value != None, "Value must be set before converting to stream"
		data = StringIO()

		# Pack our type on
		data.write( struct.pack( "<B", self.type ) )

		# Now the size and the actual data
		data.write( BW_PACK3( 1 ) )
		data.write( struct.pack( "<B", self.value ) )

		return data.getvalue()


	def fromStream( self, data ):
		assert len(data) == 1, "Bool type must be 1 byte long"
		(value,) = struct.unpack( "<B", data )
		self.value = bool( value )


	def __repr__(self):
		return "<WDT Bool %s>" % (self.value)


class WatcherDataTypeString( WatcherDataType ):
	"""Data type corresponding to the Watcher Protocol (v2) data type
	   enumeration WATCHER_TYPE_STRING (5)."""
	type = WATCHER_TYPE_STRING

	# __glenc__ TODO: Implement a constructor like this that calls through to
	# set() for each watcher type.
	def __init__( self, s = None ):
		WatcherDataType.__init__( self )
		self.set( s )

	def set( self, x ):
		self.value = str(x)

	def toStream( self ):
		assert self.value != None, "Value must be set before converting to stream"
		data = StringIO()
		# Pack our type on
		data.write( struct.pack( "<B", self.type ) )
		# Now the size and the actual data
		dataLen = len(self.value)
		data.write( BW_PACK3( dataLen ) )
		data.write( struct.pack( "<%ds" % dataLen, self.value ) )
		return data.getvalue()

	def fromStream( self, data ):
		self.value = data

	def __repr__(self):
		return "<WDT String \"%s\">" % (self.value)




class WatcherDataTypeTuple( WatcherDataType ):
	"""Data type corresponding to the Watcher Protocol (v2) data type
	   enumeration WATCHER_TYPE_TUPLE (6)."""
	type = WATCHER_TYPE_TUPLE

	def set( self, x ):
		if hasattr( x, "__iter__" ):
			self.value = [ WDTRegistry.toWDT(i) for i in x ]
		else:
			self.value = [ WDTRegistry.toWDT(x) ]


	def toStream( self ):
		assert self.value != None, "Value must be set before converting to " \
			"stream"
		data = StringIO()

		# Pack our type on
		data.write( struct.pack( "<B", self.type ) )

		# Build the tuple string so we can find the size of the
		# data we are sending

		# Put the count of number of tuple elements on then all
		# the tuple elements
		tupleData  = BW_PACK3( len(self.value) )
		tupleData += "".join( i.toStream() for i in self.value )

		# Now generate the package with the size prefix then the actual data
		data.write( BW_PACK3( len(tupleData) ) )
		data.write( tupleData )

		return data.getvalue()



	def fromStream( self, data ):

		ENTRY_PREFIX = "BB"

		stream = StringIO( data )

		tupleCount = BW_UNPACK3( stream )

		results = []
		for i in xrange(tupleCount):
			# Read the type and mode
			(tmpType, tmpMode) = struct.unpack( ENTRY_PREFIX,
							stream.read( struct.calcsize( ENTRY_PREFIX ) ) )

			# Now read off the size of the data chunk
			tmpSize = BW_UNPACK3( stream )
			tmpData = stream.read( tmpSize )

			# Dispatch unpack to WatcherDataType
			wdtClass = WDTRegistry.getClass( tmpType )
			wdtObj   = wdtClass.unpack( tmpData )

			results.append( wdtObj )

		self.value = tuple( results )


	def __iter__(self):
		return iter( self.value )

	def __repr__(self):
		return "<WDT Tuple %s>" % str(self.value)



class WatcherDataTypeType( WatcherDataType ):
	"""Data type corresponding to the Watcher Protocol (v2) data type
	   enumeration WATCHER_TYPE_TYPE (7)."""

	type = WATCHER_TYPE_TYPE


	def fromStream( self, data ):
		assert len(data) == 1, "Type type must be 1 byte long"
		(value,) = struct.unpack( "<B", data )
		self.value = WDTRegistry.getClass( value )


	def __repr__(self):
		return "<WDT Type %s>" % (self.value)





# WDT Registry
# -----------------------------------------------------------------------------
class WDTRegistry( object ):
	"""
	Class which manages different watcher classes
	"""
	converters = { }
	classRegistry = { }

	@classmethod
	def toWDT( cls, x ):
		if isinstance( x, WatcherDataType ):
			return x
		else:
			varType = type(x)
			if varType in cls.converters:
				return cls.converters[varType]( x )
			else:
				# Fallback option
				return WatcherDataTypeString.fromValue( str(x) )

	@classmethod
	def registerClass( cls, wdt, fromType = None ):
		cls.classRegistry[wdt.type] = wdt
		if fromType == None:
			return
		if hasattr( fromType, "__iter__" ):
			for t in fromType:
				cls.converters[t] = wdt
		else:
			cls.converters[fromType] = wdt

	@classmethod
	def getClass( cls, enum ):
		try:
			return cls.classRegistry[enum]
		except KeyError:
			raise Exception("Unknown Watcher Protocol Type (%s)" % enum)

WDTRegistry.registerClass( WatcherDataTypeUnknown,   None )
WDTRegistry.registerClass( WatcherDataTypeInt,       [int, long]    )
WDTRegistry.registerClass( WatcherDataTypeUInt,       )
WDTRegistry.registerClass( WatcherDataTypeFloat,     float )
WDTRegistry.registerClass( WatcherDataTypeString,    str )
WDTRegistry.registerClass( WatcherDataTypeBool,      bool )
WDTRegistry.registerClass( WatcherDataTypeTuple, [tuple, list] )
WDTRegistry.registerClass( WatcherDataTypeType, )
