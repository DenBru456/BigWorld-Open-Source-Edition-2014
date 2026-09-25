import bwtest
from helpers.cluster import ClusterController, ClusterControllerError
import unittest

from bwtest import log, addParameterizedTestCases, \
				   addCombinedTestCases


class BasicFixtureTest( bwtest.TestCase ):
	name = "Basic fixture test" 
	description = "Tests ability to run the fixture extensions"
	tags = []


	def setUp( self ):
		# We define and create a nested TestCase here
		# so that it doesn't ge recognsied by bwharness

		class TestCase( bwtest.TestCase ):
			name = "nested test case"
			description = "test"

			tags = []

			def setUp( self ):
				self.addCleanup( self.cleanup1 )
				self.addCleanup( self.cleanup2 )
				self.calls = []

				self.fail( "test fail" )


			def cleanup1( self ):
				log.debug( "cleanup1 called" )
				self.calls.append( 1 )


			def cleanup2( self ):
				log.debug( "cleanup2 called" )
				self.calls.append( 2 )


			def tearDown( self ):
				# self.fail( "tearDown() should not be called" )
				return


			def runTest( self ):
				# self.fail( "runTest() should not be called" )
				return

		self._case = TestCase()


	def runTest( self ):
		"""
		Running a nested TestRunner to make sure cleanups are handled and
		called in proper order.
		"""

		self._suite = bwtest.TestSuite( "nested test suite", "test", [] ) 
		self._suite.addCases( [self._case] )		 

		result = unittest.TestResult()
		self._suite.run( result )
		self.assertFalse( result.wasSuccessful() )
		self.assertTrue( self._case.calls == [ 2, 1 ] )		


class BasicSnippetTest( bwtest.TestCase ):
	name = "Basic snippet test" 
	description = "Tests ability to run the server and snippets on it"
	tags = []


	def setUp( self ):
		self._cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def runTest( self ):
		cc = self._cc

		cc.setConfig( "dbApp/testing", "test value" )
		res = cc.getConfig( "dbApp/testing" )
		self.assertEqual( res, "test value" )

		#time.sleep(50)

		cc.start()

		cc.callOnApp( "baseapp", 1, "selfTestSnippetNoArg" )

		cc.callOnApp( "baseapp", 1, 
					"selfTestSnippetWithArg", arg1 = 1, arg2 = "test" )

		cc.loadSnippetModule( "baseapp", 1, "self_test/test_basic" )

		try:
			cc.callOnApp( "baseapp", 1, "non-existing-snippet" )
		except ClusterControllerError:
			pass
		else:
			self.assertTrue( False )

		r1, r2, r3 = cc.callOnApp( "baseapp", 1, "selfTestSnippetInModule" )
		self.assertEqual( r1, True )
		self.assertEqual( r2, "test" )
		self.assertEqual( r3, 123 )

		try:
			cc.loadSnippetModule( "baseapp",
										1, 
										"non-existing-snippet-module" )
		except ClusterControllerError:
			pass
		else:
			self.assertTrue( False )

		try:
			cc.callOnApp( "baseapp", 1, "selfTestSnippetInModuleWithFailure" )
		except ClusterControllerError:
			pass
		else:
			self.assertTrue( False )

		snippet = """
srvtest.assertTrue( {valueTrue} )
srvtest.assertEqual( {valueInt}, 15 )
srvtest.assertEqual( {valueStr}, "string" )
srvtest.finish( {valueInt} + 5 )
		"""	
		res = cc.sendAndCallOnApp( "baseapp", 1, snippet, 
					valueTrue = True, valueInt = 15, valueStr = "string" )
		self.assertEqual( res, 20 )

		res = cc.sendAndCallOnApp( "dbapp", None, snippet, 
					valueTrue = True, valueInt = 15, valueStr = "string" )
		self.assertEqual( res, 20 )

parameters = [{"key1": "A", "key2": "B", "key3": "C"},
			  {"key1": "D", "key2": "E", "key3": "F"}]

combinedParameters = {"key1": [3, 4], "key2": [1, 2]}

class TestParameterizedTestCases:
	
	tags = []
	name = "Parameterized Test Cases"
	description = "Testing the functionality of parameterized test cases"
	
	def setUp( self ):
		self.assertTrue(self.key1)
		self.assertTrue(self.key2)
		log.debug( "In setUp: key1 = %s, key2 = %s" % (self.key1, self.key2) )
		
	
	def runTest(self):
		self.assertTrue(self.key1)
		self.assertTrue(self.key2)
		log.debug( "In runTest: key1 = %s, key2 = %s" % (self.key1, self.key2) )

addParameterizedTestCases(TestParameterizedTestCases, parameters)
addCombinedTestCases(TestParameterizedTestCases, combinedParameters)
