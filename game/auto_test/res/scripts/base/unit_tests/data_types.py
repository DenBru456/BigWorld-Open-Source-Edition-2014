from test_case import TestCase
from test_case import fail_on_exception

import random
import struct
import time
import unicode_test

import BigWorld

import functools

from user_types import MyObj2

class MemberProxy( object ):
	def __init__( self, name ):
		self.name = name

	def __get__( self, instance, owner ):
		return instance._fixedDict[ self.name ]

	def __set__( self, instance, value ):
		instance._fixedDict[ self.name ] = value

class WrappedFixedDict( object ):
	__slots__ = ['_fixedDict']

	def __init__( self, fixedDict ):
		self._fixedDict = fixedDict

	def __str__( self ):
		return "%r" % dict( self._fixedDict )

	def __repr__( self ):
		return "WrappedFixedDict( %r )" % dict( self._fixedDict )

	a = MemberProxy( 'a' )
	b = MemberProxy( 'b' )
	c = MemberProxy( 'c' )

class WrappedFixedDictConverter( object ):
	def getDictFromObj( self, obj ):
		if isinstance( obj, dict ):
			return obj
		else:
			return obj._fixedDict

	def createObjFromDict( self, dict ):
		return WrappedFixedDict( dict )

wrappedFixedDictConverter = WrappedFixedDictConverter()

def convert( v ):
	if isinstance( v, WrappedFixedDict ):
		v = v._fixedDict

	typename = type( v ).__name__

	if typename == "PyFixedDictDataInstance":
		return dict( v )
	elif typename == "PyArrayDataInstance":
		return list( v )

	return v

def compare( v1, v2 ):
	if isinstance( v1, float ):
		return abs( v1 - v2 ) < 0.0001

	return convert( v1 ) == convert( v2 )


TEST_DATA = (
# Test 3.1 - Lower bound
dict( int8 = -128,
	uint8 = 0,
	int16 = -32768,
	uint16 = 0,
	int32 = -2147483648,
	uint32 = 0,
	int64 = -9223372036854775808,
	uint64 = 0,
	float32 = -8.8,
	float64 = -8.8 ),

# Test3.1 - Upper bound
dict( int8 = 127,
	uint8 = 255,
	int16 = 32767,
	uint16 = 65535,
	int32 = 2147483647,
	uint32 = 4294967295,
	int64 = 9223372036854775807,
	uint64 = 18446744073709551615,
	float32 = 8.8,
	float64 = 8.8),

# Test 3.2
dict(
	stringVarCharLowerBound = 1 * 'x',
	stringVarCharUpperBound = 255 * 'x',
	stringTextLowerBound = 256 * 'x',
	stringTextUpperBound = 65535 * 'x',
	stringMediumTextLowerBound = 65536 * 'x',
	stringMediumTextUpperBound = 16777214 * 'x' ),

dict(
	python1 = { 1 : "one", 2 : "two" },
	python2 = range( 30 ),
	python3 = None ),

dict(
	chinese = unicode_test.chinese,
	japanese = unicode_test.japanese,
	russian = unicode_test.russian,
	blob = ''.join( chr( random.randrange( 256 ) ) for i in range( 1000 ) )
),

# Test 3.3 - User Type (in common/user_types.py)

dict(
		userType1 = (22, 31.5),

		userType2 = MyObj2( 7, range( 10 ) )
	),

# Test 3.4 - Array Type
dict(
		intArray = [0, 0, -2**31, 2**31-1, 22],
		stringTuple = ("", 20*'x', "Testing" )
	),

# Test 3.5 - FIXED_DICT Type
dict(
		fixedDict = { 'a' : 1, 'b' : 2.5, 'c' : "Test" },
		wrappedFixedDict = { 'a' : 1, 'b' : 2.5, 'c' : "Test" }
	)

)


class DefTypes( TestCase ):
	def __init__( self ):
		TestCase.__init__( self )
		self._index = -1

	def run( self ):
		self.nextTest()

	def nextTest( self ):
		self._index += 1

		if self._index >= len( TEST_DATA ):
			self.finishTest()
		else:
			e = BigWorld.createEntity( "DataTypes", **self.currData() )
			self._testStart = time.time()
			e.writeToDB( self.onWritten )

	def currData( self ):
		return TEST_DATA[ self._index ]

	@fail_on_exception
	def onWritten( self, isOkay, entityMB ):
		entity = BigWorld.entities[ entityMB.id ]
		BigWorld.addTimer(
				functools.partial( self.onDestroy, entity.databaseID ), 0.2 )
		entity.destroy()

	@fail_on_exception
	def onDestroy( self, dbID, *args ):
		BigWorld.createBaseFromDBID( "DataTypes", dbID, self.onCreate )

	@fail_on_exception
	def onCreate( self, baseRef, dbID, wasActive ):
		self.checkResult( BigWorld.entities[ baseRef.id ] )
		print "Dictionary %d took %.2f seconds" % \
			(self._index, time.time() - self._testStart)
		self.nextTest()

	def checkValue( self, entity, key, value ):
		v2 = getattr( entity, key )

		if not compare( value, v2 ):
			self.fail( "%s: %r != %r" % (key, value, v2) )

	def checkResult( self, entity ):
		data = self.currData()

		for key, value in data.items():
			self.checkValue( entity, key, value )

# data_types.py
