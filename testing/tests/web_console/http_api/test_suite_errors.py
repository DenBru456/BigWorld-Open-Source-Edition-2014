"""
There are multiple ways for WebConsole to trigger exceptions. This test suite
should hit all of them and confirm that they all behave as expected.
"""

import sys
import time

from test_common import *
from primitives import WebConsoleAPI

class ErrorCommon( TestCase ):
	name = 'Common Error parent class'
	description = "Doesn't run any tests!"

	def setUp( self ):
		assert( TestCommon.restartServer() )
		self.webConsole = StartWebConsoleAPI()

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()

class LoginErrorScenario( ErrorCommon ):
	name = 'Login error tests'
	description = "Test that login fails with bad credentials"
	tags = ['test_suite_errors']

	def runTest( self ):
		"""Check the error behaviour on login"""
		timestamp = str( time.time() )
		for args in (
			# Wrong username and password
			{'user': timestamp, 'passwd': timestamp},
			# Correct user, bad password
			{'passwd': timestamp},
			# Correct user, no password
			{'passwd': ''},
		):
			w = WebConsoleAPI.WebConsoleAPI( **args )
			code, data = w.logsSearch()
			self.assertEquals( code, 403 )
			self.assertTrue( 'Anonymous access denied' in data['message'] )


class AdminErrorScenario( ErrorCommon ):
	name = 'Admin error tests'
	description = "All admin errors go through the same handler, so test how" +\
		" the admin application handles a few different scenarios"
	tags = ['test_suite_errors']

	ADMIN_USER = 'admin'
	ADMIN_PASSWORD = 'admin'

	def runTest( self ):
		"""Check the behaviour of errors under the admin application"""

		w = WebConsoleAPI.WebConsoleAPI( user=self.ADMIN_USER,
										passwd=self.ADMIN_PASSWORD )

		# Check user verification
		code, data = w.getProcs( 'ZZZZZZ' )
		self.assertEquals( code, 403 )
		self.assertEquals( data['exception'], 'AuthorisationException' )
		self.assertTrue( "No known user" in data['message'] )

		# Some endpoints are inaccessible to admins
		code, data = w.getProcs( w.user )
		self.assertEquals( code, 403 )
		self.assertEquals( data['exception'], 'AuthorisationException' )
		self.assertTrue( 
					"You don't have sufficient permissions" in data['message'] )

		# Some endpoints don't exist
		code, data = w.rawRequest( 'ZZZZ', {} )
		self.assertEquals( code, 404 )
		self.assertEquals( data['exception'], 'NotFound' )
		code, data = w.profilerRequest( 'ZZZZ', {} )
		self.assertEquals( code, 404 )
		self.assertEquals( data['exception'], 'NotFound' )

		# Test a real admin error - duplicate user. Note that this returns
		# a 200 error, because most of them do. Will need to revisit this if
		# we restructure to return more meaningful codes.
		code, data = w.rawRequest( 'admin/edit',
								{'action': 'add', 'username': w.user} )
		self.assertEquals( code, 200 )
		self.assertTrue( 'already exists' in data['message'] )

class UserPathErrorScenario( ErrorCommon ):
	name = 'User path error tests'
	description = "Test some path-related errors"
	tags = ['test_suite_errors']

	def runTest( self ):
		"""Check the behaviour of path errors under the user application"""

		# Some endpoints don't exist
		code, data = self.webConsole.rawRequest( 'ZZZZ', {} )
		self.assertEquals( code, 404 )
		self.assertEquals(  data['exception'], 'NotFound' )
		self.assertEquals( data['message'], "The path '/ZZZZ' was not found." )
		code, data = self.webConsole.profilerRequest( 'ZZZZ', {} )
		self.assertEquals( code, 404 )
		self.assertEquals( data['exception'], 'NotFound' )
		self.assertEquals( data['message'],
							"The path '/profiler/ZZZZ' was not found." )

class UserArgumentErrorScenario( ErrorCommon ):
	name = 'User argument error tests'
	description = "Test some argument-related errors"
	tags = ['test_suite_errors']

	def runTest( self ):
		"""Check the behaviour of argument errors under the user application"""

		testPath = 'watchers/filtered/csv'
		# No arguments
		code, data = self.webConsole.rawRequest( testPath, {} )
		self.assertEquals( code, 500 )
		self.assertEquals( data['exception'], 'TypeError' )
		self.assertTrue( 'takes at least 3 arguments' in data['message'] )

		# Invalid arguments
		arguments = {
			'processes': 'ZZZZ',
			'path': 'ZZZZ',
			'filename': 'ZZZZ',
		}
		code, data = self.webConsole.rawRequest( testPath, arguments )
		self.assertEquals( code, 200 )
		self.assertEquals( data['error'], 'Invalid filter request' )

class DisplayErrorScenario( ErrorCommon ):
	name = 'UI display error tests'
	description = "Test some error message display endpoints that don't " + \
		"actually trigger HTTP error codes"
	tags = ['test_suite_errors']

	def runTest( self ):
		"""Check the behaviour of display errors under the user application"""

		# All of these errors are informational only, so they should return 200
		code, data = self.webConsole.rawRequest( 'cc/error', {'message': 'ZZ'} )
		self.assertEquals( code, 200 )
		self.assertEquals( data['error'], 'ERROR' )
		self.assertEquals( data['message'], 'ZZ' )
		code, data = self.webConsole.rawRequest( 'exception', {'enum': 0} )
		self.assertEquals( code, 200 )
		self.assertEquals( data['error'], 'Exception Raised' )
		self.assertEquals( data['message'], "Exception number '0' is invalid." )
		# Previously triggered a failure exception when enum was non-integer
		code, data = self.webConsole.rawRequest( 'exception', {'enum': 'z'} )
		self.assertEquals( code, 200 )
		self.assertEquals( data['error'], 'Exception Raised' )
		self.assertEquals( data['message'], "Exception number 'z' is invalid." )
