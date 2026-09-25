import BigWorld
import srvtest

from random import random
from functools import partial

# -----------------------------------------------------------------------
# Snippets for TestDatatypes



testFailureMessage =        "  * %s test %s failed. Expecting %s, but got %s."
testSectionFailureMessage = "[FAILED]: %s: %d/%d tests passed"
testSectionPassMessage =    "    %s: All %d tests passed"

totalFailed = 0

failureString = ""

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


def addFailure( msg ):
	global failureString
	failureString += msg + "\n"


def testEqual( expecting, actual ):

	global tests
	tests += 1

	if expecting == actual:
		return True

	# Wrapped sequence types
	if hasattr( expecting, 'equals_seq' ):
		return expecting.equals_seq( actual )
	elif hasattr( actual, 'equals_seq' ):
		return actual.equals_seq( expecting )

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
		addFailure( msg )
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
		addFailure( testSectionFailureMessage %\
					 (testName, tests - failed, tests) )

		global totalFailed
		totalFailed += failed
	else:
		print testSectionPassMessage % (testName, tests)


@srvtest.testSnippet
def snippetWrite():
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
	t1.python = testEqual


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

	# FIXED_DICT
	t1.fixedDict.a = 1
	t1.fixedDict.b = "1"
	t1.fixedDict.c = [10, 11, 12, 13, 14]

	t2.fixedDict.a = 2
	t2.fixedDict.b = "2"
	t2.fixedDict.c = [20, 21, 22, 23, 24]

	t1.userType.a = 10
	t1.userType.b = "10"
	t1.userType.c = [10.0, 11.0, 12.0, 13.0, 14.0]

	t2.userType.a = 20
	t2.userType.b = "20"
	t2.userType.c = [20.0, 21.0, 22.0, 23.0, 24.0]

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



	t1.writeToDB( writeCallback1 )
	t1.destroy()
	srvtest.assertTrue( t1.isDestroyed )


@srvtest.testStep
def writeCallback1( result, ent ):
	global t1
	global t2
	srvtest.assertTrue( result )

	t2.writeToDB( writeCallback2 )
	t2.destroy()
	srvtest.assertTrue( t2.isDestroyed )


@srvtest.testStep
def writeCallback2( result, ent ):
	global t1
	global t2
	srvtest.assertTrue( result )

	srvtest.finish()


@srvtest.testSnippet
def snippetRead():
	global t1
	global t2

	srvtest.assertTrue( t1.databaseID > 0 )
	srvtest.assertTrue( t2.databaseID > 0 )

	BigWorld.createBaseFromDBID( "TestEntity", t1.databaseID, readCallback1 )


@srvtest.testStep
def readCallback1( base, dbID, wasActive ):
	srvtest.assertEqual( dbID, t1.databaseID )

	BigWorld.createBaseFromDBID( "TestEntity", t2.databaseID, readCallback2 )


@srvtest.testStep
def readCallback2( base, dbID, wasActive ):
	srvtest.assertEqual( dbID, t2.databaseID )
	srvtest.finish()


@srvtest.testSnippet
def snippetTest():
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
	testEqual( t1.python, testEqual )

	# FIXED_DICT
	testEqual( t1.fixedDict.a, 1 )
	testEqual( t1.fixedDict.b, "1" )
	testEqual( t1.fixedDict.c, [10, 11, 12, 13, 14] )

	testEqual( t2.fixedDict.a, 2 )
	testEqual( t2.fixedDict.b, "2" )
	testEqual( t2.fixedDict.c, [20, 21, 22, 23, 24] )

	testEqual( t1.userType.a, 10 )
	testEqual( t1.userType.b, "10" )
	testEqual( t1.userType.c, [10.0, 11.0, 12.0, 13.0, 14.0] )

	testEqual( t2.userType.a, 20 )
	testEqual( t2.userType.b, "20" )
	testEqual( t2.userType.c, [20.0, 21.0, 22.0, 23.0, 24.0] )

	endSection()
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
	testEqual( str( t1.array ), str( [1, 2, 3, 4, 5] ) )

	testEqual( t1.tuple, (1, 2, 3, 4, 5) )
	testEqual( t2.tuple, () )

	# Vector
	testEqual( t1.vector2, (0, -1.3) )
	testEqual( t1.vector3, (67.39, 4386, -0.007) )
	testEqual( t1.vector4, (-12352.7, .00054, 3, 32769) )

	endSection()

	deleteFromDB()


@srvtest.testStep
def deleteFromDB():
	global t1

	dbID = t1.databaseID
	t1.destroy( deleteFromDB = True )
	BigWorld.createBaseFromDBID( "TestEntity", dbID, onCreate1 )


@srvtest.testStep
def onCreate1( mb, dbID, wasActive ):
	srvtest.assertEqual( mb, None )
	srvtest.assertEqual( dbID, 0 )
	srvtest.assertFalse( wasActive )

	global t2

	dbID  = t2.databaseID
	t2.destroy( deleteFromDB = True )
	BigWorld.createBaseFromDBID( "TestEntity", dbID, onCreate2 )


@srvtest.testStep
def onCreate2( mb, dbID, wasActive ):
	srvtest.assertEqual( mb, None )
	srvtest.assertEqual( dbID, 0 )
	srvtest.assertFalse( wasActive )

	srvtest.assertTrue( totalFailed == 0, msg = failureString )
	srvtest.finish()
