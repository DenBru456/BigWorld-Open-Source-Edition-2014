import BigWorld
from functools import partial
from random import random

testFailureMessage =        "  * %s test %s failed. Expecting %s, but got %s."
testSectionFailureMessage = "[FAILED]: %s: %d/%d tests passed"
testSectionPassMessage =    "    %s: All %d tests passed"

totalFailed = 0

# Integers
P7 = pow( 2, 7 )
P8 = pow( 2, 8 )
P15 = pow( 2, 15 )
P16 = pow( 2, 16 )
P31 = pow( 2, 31 )
P32 = pow( 2, 32 )
P63 = pow( 2, 63 )
P64 = pow( 2, 64 )

# Strings
S8 = "a" * pow( 2, 8 )
S16 = "a" * pow( 2, 16 )
S24 = "a" * pow( 2, 24 )

# BLOBs
B8 = '\0' * pow( 2, 8 )
B16 = "\0" * pow( 2, 16 )
B24 = "\0" * pow( 2, 24 )

# Misc. class
class TestClass:
	x=0
	y=5
	def foo( self, a ):
		print a+3
		return a-3
	def bar( self ):
		self.foo( self.y )


def writeEntity( e ):
	e.writeToDB()
	e.destroy()

def readEntity( e ):
	if e.databaseID == 0:
		raise KeyError( "No entry exists for databaseID %d" % (e.databaseID) )

	BigWorld.createBaseFromDBID( "TestEntity", e.databaseID )

def test( result ):
	if not result:
		raise ValueError( "Test failed" )

def testEqual( expecting, actual ):

	global tests
	tests += 1

	if expecting == actual:
		return True

	# Try for floats
	try:
		if abs( expecting - actual ) < 0.001:
			return True
	except TypeError:
		pass

	# Try for tuples
	if type( actual ) == tuple:
		try:
			tupleMatches = True
			for i in range( len( expecting ) ):
				if abs( expecting[ i ] - actual[ i ] ) > 0.001:
					tupleMatches = False
			if tupleMatches:
				return True
		except:
			pass


	if expecting != actual:
		global failed
		global testName
		failed += 1
		msg = testFailureMessage % \
			(testName, tests.__str__(), expecting.__str__(),  actual.__str__() )
		#raise ValueError( msg )
		print msg
		return False

	return True

def newSection( name ):
	global tests
	global failed
	global testName

	tests = 0
	failed = 0
	testName = name

def endSection():
	global tests
	global failed
	global testName

	if failed > 0:
		print testSectionFailureMessage % (testName, tests - failed, tests)

		global totalFailed
		totalFailed += failed
	else:
		print testSectionPassMessage % (testName, tests)

def cleanup():
	global t1
	global t2

	t1.destroy()
	t2.destroy()

	BigWorld.deleteBaseByDBID( "TestEntity", t1.databaseID )
	BigWorld.deleteBaseByDBID( "TestEntity", t2.databaseID )



def write():
	global t1
	global t2

	t1=BigWorld.createEntity( "TestEntity" )
	t2=BigWorld.createEntity( "TestEntity" )

	t1.name = random().__str__()
	t2.name = random().__str__()


# 3.1 Numerical
	t1.int8 = P7-1
	t2.int8 = -P7

	t1.uint8 = 0
	t2.uint8 = P8-1

	t1.int16 = P15-1
	t2.int16 = -P15

	t1.uint16 = 0
	t2.uint16 = P16-1

	t1.int32 = P31-1
	t2.int32 = -P31

	t1.uint32 = 0
	t2.uint32 = P32-1

	t1.int64 = P63-1
	t2.int64 = -P63

	t1.uint64 = 0
	t2.uint64 = P64-1

	t1.float = -4.56789
	t2.float = 2.34567

	t1.float32 = -4.56789
	t2.float32 = 2.34567

	t1.float64 = -4.56789
	t2.float64 = 2.34567



# 3.2 Buffer	
	# Strings
	t1.strVarCharLowerBound = "a"
	t1.strVarCharUpperBound = S8[1:]
	t1.strTextLowerBound = S8
	t1.strTextUpperBound = S16[1:]
	t1.strMediumTextLowerBound = S16
#	t1.strMediumTextUpperBound = S24[2:]

	# Unicode string
	t1.unicodeString = u"asdf"

	# Blob
	t1.blobTinyLowerBound = "\0"
	t1.blobTinyUpperBound = B8[1:]
	t1.blobLowerBound = B8
	t1.blobUpperBound = B16[1:]
	t1.blobMediumLowerBound = B16
#	t1.blobMediumUpperBound = B24[2:]

	t2.blobTinyLowerBound = "a"
	t2.blobTinyUpperBound = S8[1:]
	t2.blobLowerBound = S8
	t2.blobUpperBound = S16[1:]
	t2.blobMediumLowerBound = S16
#	t2.blobMediumUpperBound = S24[2:]

	# Python
	t1.pyBlob = "bl\0b"
	t1.python = writeEntity


# 3.3 User type

	t1.nestedArray = []
	t2.nestedArray = \
		[ \
			{"inner": [1, 2, 3]}, \
			{"inner": [-445, 123, 8879]}, \
			{"inner": [0, -P31, P31-1]}, \
			None \
		]

	t1.nestedArraySingle = {"inner": [1, 2, 3]}
	# t2.nestedArraySingle is not set, so default of None is used.

	t2.python = None


# 3.4 Array

	# Array
	t1.array = [1, 2, 3, 4, 5]
	t2.array = []

	# Tuple
	t1.tuple = (1, 2, 3, 4, 5)
	t2.tuple = ()

	# Vector
	t1.vector2 = (0, -1.3)
	t1.vector3 = (67.39, 4386, -0.007)
	t1.vector4 = (-12352.7, .00054, 3, 32769)


	writeEntity( t1 )
	writeEntity( t2 )


def read():
	global t1
	global t2
	readEntity( t1 )
	readEntity( t2 )


def test():
	global t1
	global t2

	testEntities = [i for i in BigWorld.entities.values() if i.__class__.__name__ == "TestEntity"]

	t1 = [i for i in testEntities if i.databaseID == t1.databaseID][0]
	t2 = [i for i in testEntities if i.databaseID == t2.databaseID][0]

	dummy = BigWorld.createEntity( "TestEntity", name = random().__str__() )


# 3.1 Numerical
	newSection( "[3.1] Numerical types" )

	testEqual( t1.int8, P7-1 )
	testEqual( t1.int8, P7-1 )
	testEqual( t2.int8, -P7 )

	testEqual( t1.uint8, 0 )
	testEqual( t2.uint8, P8-1 )

	testEqual( t1.int16, P15-1 )
	testEqual( t2.int16, -P15 )

	testEqual( t1.uint16, 0 )
	testEqual( t2.uint16, P16-1 )

	testEqual( t1.int32, P31-1 )
	testEqual( t2.int32, -P31 )

	testEqual( t1.uint32, 0 )
	testEqual( t2.uint32, P32-1 )

	testEqual( t1.int64, P63-1 )
	testEqual( t2.int64, -P63 )

	testEqual( t1.uint64, 0 )
	testEqual( t2.uint64, P64-1 )

	testEqual( t1.float, -4.56789 )
	testEqual( t2.float, 2.34567 )

	testEqual( t1.float32, -4.56789 )
	testEqual( t2.float32, 2.34567 )

	testEqual( t1.float64, -4.56789 )
	testEqual( t2.float64, 2.34567 )
	endSection()



# 3.2 Buffer
	newSection( "[3.2] Buffer types" )

	# Strings
	testEqual( t1.strVarCharLowerBound, "a" )
	testEqual( t1.strVarCharUpperBound, S8[1:] )
	testEqual( t1.strTextLowerBound, S8 )
	testEqual( t1.strTextUpperBound, S16[1:] )
	testEqual( t1.strMediumTextLowerBound, S16 )
#	testEqual( t1.strMediumTextUpperBound, S24[2:] )

	# Unicode string
	testEqual( t1.unicodeString, u"asdf" )

	# Blob
	testEqual( t1.blobTinyLowerBound, "\0" )
	testEqual( t1.blobTinyUpperBound, B8[1:] )
	testEqual( t1.blobLowerBound, B8 )
	testEqual( t1.blobUpperBound, B16[1:] )
	testEqual( t1.blobMediumLowerBound, B16 )
#	testEqual( t1.blobMediumUpperBound, B24[2:] )

	testEqual( t2.blobTinyLowerBound, "a" )
	testEqual( t2.blobTinyUpperBound, S8[1:] )
	testEqual( t2.blobLowerBound, S8 )
	testEqual( t2.blobUpperBound, S16[1:] )
	testEqual( t2.blobMediumLowerBound, S16 )
#	testEqual( t2.blobMediumUpperBound, S24[2:] )

	# Python
	testEqual( t1.pyBlob, "bl\0b" )
	testEqual( t1.python, writeEntity )

	endSection()



# 3.3 User type
	newSection( "[3.3] User types" )

	dummy.nestedArray = []
	testEqual( t1.nestedArray, dummy.nestedArray )

	dummy.nestedArray = [ \
			{"inner": [1, 2, 3]}, \
			{"inner": [-445, 123, 8879]}, \
			{"inner": [0, -P31, P31-1]}, \
			None \
		]
	testEqual( t2.nestedArray, dummy.nestedArray )

	dummy.nestedArraySingle = {"inner": [1, 2, 3]}
	testEqual( t1.nestedArraySingle, dummy.nestedArraySingle )

	testEqual( t2.nestedArraySingle, None )

	testEqual( t2.python, None )

	endSection()



# 3.4 Array
	newSection( "[3.4] Array types" )

	dummy.array = [1, 2, 3, 4, 5]
	testEqual( t1.array, dummy.array )
	dummy.array = []
	testEqual( t2.array, dummy.array )

	# Bug 32668
	testEqual( t1.array, [1, 2, 3, 4, 5] )

	testEqual( t1.tuple, (1, 2, 3, 4, 5) )
	testEqual( t2.tuple, () )

	# Vector
	testEqual( t1.vector2, (0, -1.3) )
	testEqual( t1.vector3, (67.39, 4386, -0.007) )
	testEqual( t1.vector4, (-12352.7, .00054, 3, 32769) )

	endSection()


	cleanup()
