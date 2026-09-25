from test_case import TestCase
from test_case import fail_on_exception

import BigWorld

TABLE_NAME = "testTable"
COL_NAME = "sm_aString"
colValue = "billybobmartin"

def IsNone( v ): return v is None
def Equals( v1 ): return lambda v2: v1 == v2
def Not( func ): return lambda *args: not func( *args )
def DoNotCheck( v ): return True

# SQL command to execute plus functions to check results.
# Results are: resultSet, numAffectsRows, errorMsg
commandData = (
("DROP TABLE IF EXISTS %s" % TABLE_NAME,
	(IsNone, DoNotCheck, IsNone ) ),

("CREATE TABLE %s (%s char(20))" % (TABLE_NAME, COL_NAME),
	(IsNone, Equals( 0 ), IsNone)),

("INSERT INTO %s VALUES( '%s' )" % (TABLE_NAME, colValue),
 	(IsNone, Equals( 1 ), IsNone)),

("SELECT * FROM %s" % TABLE_NAME,
 	(Equals( [[colValue]] ), IsNone, IsNone)),

("DROP TABLE %s" % TABLE_NAME,
 	(IsNone, Equals( 0 ), IsNone)),

("__BIGWORLD__",
 	(IsNone, IsNone, Not( IsNone ))))

class Command( object ):
	def __init__( self, queryStr, resultTests ):
		self.queryStr = queryStr
		self.resultTests = resultTests

	def checkResult( self, args ):
		for name, value, test in \
				zip( ("resultSet", "numAffectsRows", "errorMsg"),
						args, self.resultTests ):
			if not test( value ):
				return "Command '%s' returned invalid %s %r" % \
					(self.queryStr, name, value)


commands = [Command( *c ) for c in commandData]

class ExecuteDBCmd( TestCase ):
	def cmd( self, cmd, func ):
		BigWorld.executeRawDatabaseCommand( cmd, func )

	def gen( self ):
		for cmd in commands:
			errorMsg = cmd.checkResult( (yield cmd.queryStr) )
			if errorMsg:
				self.fail( errorMsg )

	def run( self ):
		self._generator = self.gen()
		cmd = self._generator.next()
		BigWorld.executeRawDatabaseCommand( cmd, self.dbResult )

	@fail_on_exception
	def dbResult( self, *args ):
		try:
			cmd = self._generator.send( args )
			BigWorld.executeRawDatabaseCommand( cmd, self.dbResult )
		except StopIteration:
			self.finishTest()

# db_cmds.py
