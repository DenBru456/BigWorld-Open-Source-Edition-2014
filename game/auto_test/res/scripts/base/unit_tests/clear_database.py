from test_case import TestCase
from test_case import fail_on_exception

import BigWorld
import functools

class ClearDatabase( TestCase ):
	def __init__( self ):
		TestCase.__init__( self )
		self._numOutstanding = 0

	def run( self ):
		# Clear all of the tables starting with tbl_.
		BigWorld.executeRawDatabaseCommand(
				"SHOW TABLES LIKE 'tbl_%'", self.onTables )

	@fail_on_exception
	def onTables( self, resultSet, numAffectedRows, errorMsg ):
		for result in resultSet:
			self.query( "DELETE FROM %s" % result[0] )

		self.query( "DELETE FROM bigworldLogOns" )

	def query( self, cmd ):
		self._numOutstanding += 1
		BigWorld.executeRawDatabaseCommand( cmd,
				functools.partial( self.dbResponse, cmd ) )

	@fail_on_exception
	def dbResponse( self, cmd, resultSet, numAffectedRows, errorMsg ):
		self.assertEqual( errorMsg, None )

		if errorMsg:
			print "Command '%s' failed: %s" % (cmd, errorMsg )
		self._numOutstanding -= 1

		if self._numOutstanding == 0:
			self.finishTest()

# clear_database.py
