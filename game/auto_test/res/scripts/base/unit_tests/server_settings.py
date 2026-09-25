from test_case import TestCase
from test_case import fail_on_exception

import BigWorld
import BWConfig

class ServerSettings( TestCase ):
	def run( self ):
		self.assertEqual( BWConfig.readString( "dbMgr/type" ), "mysql" )
		# Set the following in /etc/my.cnf
		# max_allowed_packet=32MB
		BigWorld.executeRawDatabaseCommand(
				"SHOW VARIABLES LIKE 'max_allowed_packet'", self.step1 )

	@fail_on_exception
	def step1( self, resultSet, numAffectedRows, errorMsg ):
		self.assertEqual( resultSet[0][0], 'max_allowed_packet' )

		max_allowed_packet = int( resultSet[0][1] )

		if int( resultSet[0][1] ) < 16000000:
			self.fail( "MySQL's max_allowed_packet is %d. " 
						"This should be set to 32MB in /etc/my.cnf" %
					max_allowed_packet )

		self.finishTest()

# server_settings.py
