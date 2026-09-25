# Test USER_DATA type implementation

import struct

class TestType:
	def __init__( self, a, b, c ):
		# integer
		self.a = a
		# string
		self.b = b
		# list of floats
		self.c = c

class StreamUnpacker:
	def __init__( self, stream ):
		self._stream = stream
		self._offset = 0

	def unpack( self, format ):
		len = struct.calcsize( format )
		return struct.unpack( format, self.data( len ) )

	def data( self, dataLen ):
		if self._offset + dataLen > len( self._stream ):
			raise IndexError
		slice = self._stream[self._offset:self._offset + dataLen]
		self._offset += dataLen
		return slice

class TestEntityUserTypeWrapper:
	def addToStream( self, obj ):
		#print "addToStream"
		out = struct.pack( "ib", obj.a, len( obj.b ) )
		out += obj.b
		if len( obj.c ) < 0xFF:
			out += struct.pack( "B", len( obj.c ) )
		else:
			out += struct.pack( "i", ( len( obj.c ) << 8 ) | 0xFF )

		for v in obj.c:
			out += struct.pack( "f", v )
		return out

	def createFromStream( self, stream ):
		#print "createFromStream"
		packed = StreamUnpacker( stream )
		a, lenB = packed.unpack( "ib" )
		b = packed.data( lenB )
		lenC = packed.unpack( "B" )
		if lenC == 0xFF:
			lenC0, lenC1, lenC2 = packed.unpack( "BBB" )
			lenC = lenC0 | lenC1 << 8 | lenC2 << 16

		c = list( packed.unpack( "%df" % lenC ) )
		return TestType( a, b, c )

	def addToSection( self, obj, section ):
		#print "addToSection"
		section.createSection( 'a' )
		section['a'].asInt = obj.a
		section.createSection( 'b' )
		section['b'].asString = obj.b
		section.createSection( 'c' )
		# obj.c is usually a list, needs to be a tuple for writeFloats
		section['c'].writeFloats( "item", tuple( obj.c ) )

	def createFromSection( self, section ):
		#print "createFromSection"
		a = section['a'].asInt
		b = section['b'].asString
		c = list( section['c'].readFloats( "item" ) )
		return TestType( a, b, c )

	def fromStreamToSection( self, stream, section ):
		#print "fromStreamToSection"
		o = self.createFromStream( stream )
		self.addToSection( o, section )

	def fromSectionToStream( self, section ):
		#print "fromSectionToStream"
		o = self.createFromSection( section )
		return self.addToStream( o )

	def defaultValue( self ):
		#print "defaultValue"
		return TestType( 32, "TestType", [3., 4., 5.] )

	def bindSectionToDB( self, binder ):
		#print "bindSectionToDB"
		binder.bind( 'a', "INT32" )
		binder.bind( 'b', "STRING" )
		binder.bind( 'c', "ARRAY<of>FLOAT</of>" )

instance = TestEntityUserTypeWrapper()


# Custom wrapping FIXED_DICT into a class

import cPickle

class TestEntityCustomTypeWrapper( object ):          # wrapper type
	def __init__( self, dict ):
		self.a = dict[ "a" ]
		self.b = dict[ "b" ]


class TestEntityCustomTypeWrapperConverter( object ):    # type converter class
	def getDictFromObj( self, obj ):
		return { "a": obj.a, "b": obj.b }
  
	def createObjFromDict( self, dict ):
		return TestEntityCustomTypeWrapper( dict )

	def isSameType( self, obj ):
		return isinstance( obj, TestEntityCustomTypeWrapper )

	def addToStream( self, obj ):          # optional
		return cPickle.dumps( obj )

	def createFromStream( self, stream ):    # optional
		return cPickle.loads( stream )


instance_custom = TestEntityCustomTypeWrapperConverter()     # type converter object


class MemberProxy( object ):              # descriptor class
	def __init__( self, memberName ):
		self.memberName = memberName

	def __get__( self, instance, owner ):
		return instance.fixedDict[ self.memberName ]

	def __set__( self, instance, value ):
		instance.fixedDict[ self.memberName ] = value

	def __delete__( self, instance ):
		raise NotImplementedError( self.memberName )

class TestEntityCustomTypeWrapperWithDescriptors( object ):            # wrapper class
	a = MemberProxy( "a" )
	b = MemberProxy( "b" )

	def __init__( self, dict ):
		self.fixedDict = dict

class TestEntityCustomTypeWrapperConverterWithDescriptors( object ):      # type converter class
	def getDictFromObj( self, obj ):
		return obj.fixedDict        # must return original instance
  
	def createObjFromDict( self, dict ):
		return TestEntityCustomTypeWrapperWithDescriptors( dict )

	def isSameType( self, obj ):
		return isinstance( obj, TestEntityCustomTypeWrapperWithDescriptors )


instance_custom_with_desc = TestEntityCustomTypeWrapperConverterWithDescriptors()     # type converter object
