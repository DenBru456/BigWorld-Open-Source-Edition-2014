"This module implements the TestEntity entity."

import BigWorld

# ------------------------------------------------------------------------------
# Section: class TestEntity
# ------------------------------------------------------------------------------

class TestEntity( BigWorld.Entity ):
	"A TestEntity entity."

	def __init__( self ):
		BigWorld.Entity.__init__( self )


# TestEntity.py
# Test for default values in properties

DEF_TEST_SPACE = 2
import Math
from TestUserType import TestType
from TestUserType import TestEntityCustomTypeWrapper
from TestUserType import TestEntityCustomTypeWrapperWithDescriptors

def test_entity_defs():
	pos = (0, 0, 0)
	dir = (0, 0, 0)
	for ent in BigWorld.entities.values():
		if ent.className == 'Avatar':
			pos = ent.position
			dir = ent.direction
	testentity = BigWorld.createEntity( "TestEntity", DEF_TEST_SPACE, pos, dir )  
	
	print "[TEST] Testing default values in properties\n"
	
	passed = True
	
	def test( val, dval, msg ):
		if val != dval:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testseq( val, dval, msg ):
		# Bug 32668
		if tuple(val) != tuple(dval):
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testdict( val, dval, msg ):
		if val.a != dval[ 'a' ] or val.b != dval[ 'b' ]:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testut( val, dval, msg ):
		if val.a != dval.a or val.b != dval.b or val.c != dval.c:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testb( val, dval, msg ):
		if val[:11] != dval[:11]:
			print "  failed ", msg, ": read val = '%s' def val should be = '%s'\n" % (val, dval)
			print "types: ", type( val ), type( dval ), "\n"
			return False
		return passed
	
	passed = test( testentity.tp_FLOAT32, 0, "FLOAT32 primitive" ) 
	passed = test( testentity.tp_FLOAT64, 0, "FLOAT64 primitive" ) 
	passed = test( testentity.tp_INT8, 0, "INT8 primitive" ) 
	passed = test( testentity.tp_INT16, 0, "INT16 primitive" )
	passed = test( testentity.tp_INT32, 0, "INT32 primitive" ) 
	passed = test( testentity.tp_INT64, 0, "INT64 primitive" ) 
	passed = test( testentity.tp_UINT8, 0, "UINT8 primitive" ) 
	passed = test( testentity.tp_UINT16, 0, "UINT16 primitive" ) 
	passed = test( testentity.tp_UINT32, 0, "UINT32 primitive" ) 
	passed = test( testentity.tp_UINT64, 0, "UINT64 primitive" ) 
	passed = test( testentity.tp_STRING, '', "STRING primitive" ) 
	passed = test( testentity.tp_UNICODE_STRING, '', "STRING primitive" ) 
	passed = test( testentity.tp_VECTOR2, Math.Vector2(0, 0), "VECTOR2 primitive" ) 
	passed = test( testentity.tp_VECTOR3, Math.Vector3(0, 0, 0), "VECTOR3 primitive" ) 
	passed = test( testentity.tp_VECTOR4, Math.Vector4(0, 0, 0, 0), "VECTOR4 primitive" ) 
	passed = testseq( testentity.tp_ARRAY, [], "ARRAY" ) 
	passed = testseq( testentity.tp_ARRAY_INT32, [], "ARRAY from alias.xml" ) 
	passed = testseq( testentity.tp_ARRAY_INT32_WITH_DEFAULT, [1, 2, 3], "ARRAY from alias.xml with defaults" ) 
	passed = test( testentity.tp_PYTHON, None, "PYTHON" ) 
	passed = testdict( testentity.tp_FIXED_DICT_NO_NONE, dict( a = 0, b = '' ), "FIXED_DICT None disallowed" ) 
	passed = test( testentity.tp_FIXED_DICT_ALLOW_NONE, None, "FIXED_DICT None allowed" ) 
	passed = testut( testentity.tp_USER_TYPE, TestType( 32, "TestType", [3., 4., 5.] ), "USER_TYPE" )
	passed = testb( testentity.tp_BLOB, '', "BLOB primitive" ) 

	passed = test( testentity.tpd_FLOAT32, 1.5, "FLOAT32 in .def" ) 
	passed = test( testentity.tpd_FLOAT64, 1.23456789, "FLOAT64 in .def" ) 
	passed = test( testentity.tpd_INT8, -8, "INT8 in .def" ) 
	passed = test( testentity.tpd_INT16, -16, "INT16 in .def" ) 
	passed = test( testentity.tpd_INT32, -32, "INT32 in .def" ) 
	passed = test( testentity.tpd_INT64, -64, "INT64 in .def" ) 
	passed = test( testentity.tpd_UINT8, 8, "UINT8 in .def" ) 
	passed = test( testentity.tpd_UINT16, 16, "UINT16 in .def" ) 
	passed = test( testentity.tpd_UINT32, 32, "UINT32 in .def" ) 
	passed = test( testentity.tpd_UINT64, 64, "UINT64 in .def" ) 
	passed = test( testentity.tpd_STRING, 'STRING', "STRING in .def" ) 
	passed = test( testentity.tpd_UNICODE_STRING, 'UNICODE_STRING', "UNICODE_STRING in .def" ) 
	passed = test( testentity.tpd_VECTOR2, Math.Vector2(0.1, -0.2), "VECTOR2  in .def" ) 
	passed = test( testentity.tpd_VECTOR3, Math.Vector3(0.1, -0.2, 0.3), "VECTOR3 in .def" ) 
	passed = test( testentity.tpd_VECTOR4, Math.Vector4(0.1, -0.2, 0.3, -0.4), "VECTOR4 in .def" ) 
	passed = testseq( testentity.tpd_ARRAY, [1, 2, 3], "ARRAY with defaults" ) 
	passed = testseq( testentity.tpd_ARRAY_INT32, [4, 5, 6], "ARRAY from alias.xml with overridden defaults" ) 
	passed = testseq( testentity.tpd_ARRAY_INT32_WITH_DEFAULT, [7, 8, 9], "ARRAY from alias.xml with overridden defaults" ) 
	passed = test( testentity.tpd_PYTHON, { 'a': 90, 'b': 77 }, "PYTHON in .def" ) 
	passed = testdict( testentity.tpd_FIXED_DICT_NO_NONE, dict( a = 7, b = 'bbb' ), "FIXED_DICT None disallowed" ) 
	passed = testdict( testentity.tpd_FIXED_DICT_ALLOW_NONE, dict( a = 8, b = 'ccc' ), "FIXED_DICT None allowed" ) 
	passed = testut( testentity.tpd_USER_TYPE, TestType( 33, "TestTypeMod", [4., 5., 6.] ), "USER_TYPE" )
	passed = testb( testentity.tpd_BLOB, 'Hello World!', "BLOB in .def" ) 


	if passed:
		print "Test result: Passed\n"
		return 0
	else:
		print "Test result: Failed\n"
		return -1


# Test for data propagation in properties
def create_entity( id ):
	pos = BigWorld.entities[ id ].position
	dir = BigWorld.entities[ id ].direction
	spaceID = BigWorld.entities[ id ].spaceID
	testentity = BigWorld.createEntity( "TestEntity", spaceID, pos, dir )
	return testentity.id


def find_ghost_entity():
	id = 0
	for ent in BigWorld.entities.values():
		if ent.className == 'TestEntity' and not ent.isReal():
			id = ent.id
			break

	print "[TEST] Now run TestEntity.test_propagation_real_1( %d ) on the first CellApp\n" % id	
		
	return id


def test_propagation_real_1( id = 0 ):
	pos = (0, 0, 0)
	dir = (0, 0, 0)

	passed = True

	if id == 0: 
		for ent in BigWorld.entities.values():
			if ent.className == 'Avatar':
				pos = ent.position
				dir = ent.direction
	else:
		pos = BigWorld.entities[ id ].position
		dir = BigWorld.entities[ id ].direction
		
	testentity = BigWorld.createEntity( "TestEntity", DEF_TEST_SPACE, pos, dir )  

	try:
		testentity.tpp_FIXED_DICT_NO_NONE = None
	except:
		pass
	else:
		print "  fail: None assignment to a FIXED_DICT without AllowNone didn't raise an exception.\n"
		passed = False

	try:
		testentity.tpp_FIXED_DICT_ALLOW_NONE = dict( a = 1, c = 'c' )
	except:
		pass
	else:
		print "  fail: Assigning a non-compatible dictionary to FIXED_DICT didn't raise an exception.\n"
		passed = False

	testentity.tpp_Nested = [ dict( a = 1, b = 'uuu' ), dict( a = 2, b = 'vvv' ) ]
	testentity.tpp_FIXED_DICT_NO_NONE.a = 3
	testentity.tpp_FIXED_DICT_ALLOW_NONE = dict( a = 1, b = 'iii' )

	testentity.tpp_WRAPPED_FIXED_DICT_NO_DESC = TestEntityCustomTypeWrapper( dict( a = 8, b = 'wrapped' ) )
	testentity.tpp_WRAPPED_FIXED_DICT_WITH_DESC.a = 9
	testentity.tpp_WRAPPED_FIXED_DICT_WITH_DESC.b = 'wrapped_desc'

	print "[TEST] Testing property propagation, test entity id = ", testentity.id, "\n"	
	print "[TEST] Now run TestEntity.test_propagation_ghost_1( %d ) on the second CellApp\n" % testentity.id	

	return testentity.id,  passed


def test_propagation_ghost_1( id ):
	testentity = BigWorld.entities[ id ]

	print "[TEST] Testing default propagated values on ghost\n"
	
	passed = True
	
	def test( val, dval, msg ):
		if val != dval:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testseq( val, dval, msg ):
		# Bug 32668
		if tuple(val) != tuple(dval):
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testdict( val, dval, msg ):
		if val.a != dval[ 'a' ] or val.b != dval[ 'b' ]:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testut( val, dval, msg ):
		if val.a != dval.a or val.b != dval.b or val.c != dval.c:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testb( val, dval, msg ):
		if val[:11] != dval[:11]:
			print "  failed ", msg, ": read val = '%s' def val should be = '%s'\n" % (val, dval)
			print "types: ", type( val ), type( dval ), "\n"
			return False
		return passed

	def testnest( val, dval, msg ):
		def testone( v1, v2 ):
			return v1.a == v2['a'] and v1.b == v2['b']
		if not testone( val[0], dval[0] ) or not testone( val[1], dval[1] ):
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed
	
	passed = test( testentity.tp_FLOAT32, 0, "FLOAT32 primitive" ) 
	passed = test( testentity.tp_FLOAT64, 0, "FLOAT64 primitive" ) 
	passed = test( testentity.tp_INT8, 0, "INT8 primitive" ) 
	passed = test( testentity.tp_INT16, 0, "INT16 primitive" ) 
	passed = test( testentity.tp_INT32, 0, "INT32 primitive" ) 
	passed = test( testentity.tp_INT64, 0, "INT64 primitive" ) 
	passed = test( testentity.tp_UINT8, 0, "UINT8 primitive" ) 
	passed = test( testentity.tp_UINT16, 0, "UINT16 primitive" ) 
	passed = test( testentity.tp_UINT32, 0, "UINT32 primitive" ) 
	passed = test( testentity.tp_UINT64, 0, "UINT64 primitive" ) 
	passed = test( testentity.tp_STRING, '', "STRING primitive" ) 
	passed = test( testentity.tp_UNICODE_STRING, '', "STRING primitive" ) 
	passed = test( testentity.tp_VECTOR2, Math.Vector2(0, 0), "VECTOR2 primitive" ) 
	passed = test( testentity.tp_VECTOR3, Math.Vector3(0, 0, 0), "VECTOR3 primitive" ) 
	passed = test( testentity.tp_VECTOR4, Math.Vector4(0, 0, 0, 0), "VECTOR4 primitive" ) 
	passed = testseq( testentity.tp_ARRAY, [], "ARRAY" ) 
	passed = testseq( testentity.tp_ARRAY_INT32, [], "ARRAY from alias.xml" ) 
	passed = testseq( testentity.tp_ARRAY_INT32_WITH_DEFAULT, [1, 2, 3], "ARRAY from alias.xml with defaults" ) 
	passed = test( testentity.tp_PYTHON, None, "PYTHON" ) 
	passed = testdict( testentity.tp_FIXED_DICT_NO_NONE, dict( a = 0, b = '' ), "FIXED_DICT None disallowed" ) 
	passed = test( testentity.tp_FIXED_DICT_ALLOW_NONE, None, "FIXED_DICT None allowed" ) 
	passed = testut( testentity.tp_USER_TYPE, TestType( 32, "TestType", [3., 4., 5.] ), "USER_TYPE" )
	passed = testb( testentity.tp_BLOB, '', "BLOB primitive" ) 

	passed = testnest( testentity.tpp_Nested, [ dict( a = 1, b = 'uuu' ), dict( a = 2, b = 'vvv' ) ], "ARRAY_WITH_NESTED_DICT nested prop change" )
	passed = testdict( testentity.tpp_FIXED_DICT_NO_NONE, dict( a = 3, b = 'ddd' ), "FIXED_DICT nested prop change" )
	passed = testdict( testentity.tpp_FIXED_DICT_ALLOW_NONE, dict( a = 1, b = 'iii' ), "FIXED_DICT_ALLOW_NONE nested prop change" )

	passed = testdict( testentity.tpp_WRAPPED_FIXED_DICT_NO_DESC, dict( a = 8, b = 'wrapped' ), "Wrapped FIXED_DICT without descriptors" )
	passed = testdict( testentity.tpp_WRAPPED_FIXED_DICT_WITH_DESC, dict( a = 9, b = 'wrapped_desc' ), "Wrapped FIXED_DICT with descriptors" )

	if passed:
		print "Test result: Passed\n"
	else:
		print "Test result: Failed\n"

	print "[TEST] Now run TestEntity.test_propagation_real_2( %d ) on the first CellApp\n" % testentity.id	

	return testentity.id,  passed


def test_propagation_real_2( id ):
	testentity = BigWorld.entities[ id ]

	print "[TEST] Testing property propagation, changing prop values on entity id = ", testentity.id, "\n"

	passed = True
	
	testentity.tp_FLOAT32 = 1.5 
	testentity.tp_FLOAT64 = 1.23456789 
	testentity.tp_INT8 = -8 
	testentity.tp_INT16 = -16 
	testentity.tp_INT32 = -32 
	testentity.tp_INT64 = -64 
	testentity.tp_UINT8 = 8 
	testentity.tp_UINT16 = 16 
	testentity.tp_UINT32 = 32 
	testentity.tp_UINT64 = 64 
	testentity.tp_STRING = 'STRING' 
	testentity.tp_UNICODE_STRING = u'UNICODE_STRING' 
	testentity.tp_VECTOR2 = Math.Vector2(0.1, -0.2) 
	testentity.tp_VECTOR3 = Math.Vector3(0.1, -0.2, 0.3) 
	testentity.tp_VECTOR4 = Math.Vector4(0.1, -0.2, 0.3, -0.4) 
	testentity.tp_ARRAY = [1, 2, 3] 
	testentity.tp_ARRAY_INT32 = [4, 5, 6] 
	testentity.tp_ARRAY_INT32_WITH_DEFAULT = [7, 8, 9] 
	testentity.tp_PYTHON = { 'a': 90, 'b': 77 } 
	testentity.tp_FIXED_DICT_NO_NONE = dict( a = 7, b = 'bbb' ) 
	testentity.tp_FIXED_DICT_ALLOW_NONE = dict( a = 8, b = 'ccc' ) 
	testentity.tp_USER_TYPE = TestType( 33, "TestTypeMod", [4., 5., 6.] )
	testentity.tp_BLOB = 'Hello World!' 

	try:
		testentity.tpp_FIXED_DICT_ALLOW_NONE = None
	except:
		print "  fail: None assignment to a FIXED_DICT with AllowNone raised an exception.\n"
		passed = False

	testentity.tpp_WRAPPED_FIXED_DICT_WITH_DESC.a = 10
	testentity.tpp_WRAPPED_FIXED_DICT_WITH_DESC.b = 'wrapped_desc_mod'

	testentity.tpp_Nested[ 0 ] = dict( a = 3, b = 'uuu' )
	testentity.tpp_Nested[ 1 ].b = 'www'
		
	print "[TEST] Now run TestEntity.test_propagation_ghost_2( %d ) on the second CellApp\n" % testentity.id
	
	return testentity.id,  passed	


def test_propagation_ghost_2( id ):
	testentity = BigWorld.entities[ id ]

	print "[TEST] Testing changed propagated values on ghost\n"
	
	passed = True
	
	def test( val, dval, msg ):
		if val != dval:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testseq( val, dval, msg ):
		# Bug 32668
		if tuple(val) != tuple(dval):
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testdict( val, dval, msg ):
		if val.a != dval[ 'a' ] or val.b != dval[ 'b' ]:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testut( val, dval, msg ):
		if val.a != dval.a or val.b != dval.b or val.c != dval.c:
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed

	def testb( val, dval, msg ):
		if val[:11] != dval[:11]:
			print "  failed ", msg, ": read val = '%s' def val should be = '%s'\n" % (val, dval)
			print "types: ", type( val ), type( dval ), "\n"
			return False
		return passed

	def testnest( val, dval, msg ):
		def testone( v1, v2 ):
			return v1.a == v2['a'] and v1.b == v2['b']
		if not testone( val[0], dval[0] ) or not testone( val[1], dval[1] ):
			print "  failed ", msg, ": read val = ", val, "def val should be = ", dval, "\n"
			return False
		return passed
	
	passed = test( testentity.tp_FLOAT32, 1.5, "FLOAT32 changed" ) 
	passed = test( testentity.tp_FLOAT64, 1.23456789, "FLOAT64 changed" ) 
	passed = test( testentity.tp_INT8, -8, "INT8 changed" ) 
	passed = test( testentity.tp_INT16, -16, "INT16 changed" ) 
	passed = test( testentity.tp_INT32, -32, "INT32 changed" ) 
	passed = test( testentity.tp_INT64, -64, "INT64 changed" ) 
	passed = test( testentity.tp_UINT8, 8, "UINT8 changed" ) 
	passed = test( testentity.tp_UINT16, 16, "UINT16 changed" ) 
	passed = test( testentity.tp_UINT32, 32, "UINT32 changed" ) 
	passed = test( testentity.tp_UINT64, 64, "UINT64 changed" ) 
	passed = test( testentity.tp_STRING, 'STRING', "STRING changed" ) 
	passed = test( testentity.tp_UNICODE_STRING, 'UNICODE_STRING', "UNICODE_STRING changed" ) 
	passed = test( testentity.tp_VECTOR2, Math.Vector2(0.1, -0.2), "VECTOR2  changed" ) 
	passed = test( testentity.tp_VECTOR3, Math.Vector3(0.1, -0.2, 0.3), "VECTOR3 changed" ) 
	passed = test( testentity.tp_VECTOR4, Math.Vector4(0.1, -0.2, 0.3, -0.4), "VECTOR4 changed" ) 
	passed = testseq( testentity.tp_ARRAY, [1, 2, 3], "ARRAY with defaults" ) 
	passed = testseq( testentity.tp_ARRAY_INT32, [4, 5, 6], "ARRAY from alias.xml with overridden defaults" ) 
	passed = testseq( testentity.tp_ARRAY_INT32_WITH_DEFAULT, [7, 8, 9], "ARRAY from alias.xml with overridden defaults" ) 
	passed = test( testentity.tp_PYTHON, { 'a': 90, 'b': 77 }, "PYTHON changed" ) 
	passed = testdict( testentity.tp_FIXED_DICT_NO_NONE, dict( a = 7, b = 'bbb' ), "FIXED_DICT None disallowed" ) 
	passed = testdict( testentity.tp_FIXED_DICT_ALLOW_NONE, dict( a = 8, b = 'ccc' ), "FIXED_DICT None allowed" ) 
	passed = testut( testentity.tp_USER_TYPE, TestType( 33, "TestTypeMod", [4., 5., 6.] ), "USER_TYPE" )
	passed = testb( testentity.tp_BLOB, 'Hello World!', "BLOB changed" ) 

	passed = testdict( testentity.tpp_WRAPPED_FIXED_DICT_WITH_DESC, dict( a = 10, b = 'wrapped_desc_mod' ), "Wrapped FIXED_DICT with descriptors" )

	passed = testnest( testentity.tpp_Nested, [ dict( a = 3, b = 'uuu' ), dict( a = 2, b = 'www' ) ], "ARRAY_WITH_NESTED_DICT nested prop change" )
	passed = test( testentity.tpp_FIXED_DICT_ALLOW_NONE, None, "FIXED_DICT_ALLOW_NONE None assignment" )
	

	if passed:
		print "Test result: Passed\n"
	else:
		print "Test result: Failed\n"

	return testentity.id,  passed
