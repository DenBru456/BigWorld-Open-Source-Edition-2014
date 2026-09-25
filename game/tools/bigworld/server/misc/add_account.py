#!/usr/bin/env python

# This script adds an account when using the MySQL database and its default
# billing system.

import MySQLdb
import warnings

# TODO: Read these from bw.xml
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_USER = "bigworld"
DEFAULT_DB_PASSWD = "bigworld"
DEFAULT_DB_NAME = "fantasydemo"


USAGE = "usage: %prog [options] [username [password]]"

def addAccount( username, password, loginDetails ):
	try:
		db = MySQLdb.connect( **loginDetails )
	except MySQLdb.OperationalError, e:
		print "Failed to connect to MySQL database server:"
		print "    ", e[1]
		return False

	if username is None:
		username = raw_input( "Input username: " )

	if password is None:
		password = raw_input( "Input password for %s: " % (username,) )

	cursor = db.cursor()

	try:
		cursor.execute(
			"""INSERT INTO bigworldLogOnMapping (logOnName, password)
				VALUES (%s, 
					IF( (SELECT isPasswordHashed FROM bigworldInfo),
						MD5( CONCAT( %s, logOnName ) ),
						%s ))""",
					(username, password, password ) )
	except MySQLdb.IntegrityError:
		print "Username %s already exists" % (username,)
		return False
	cursor.close()

	db.commit()

	print "Successfully added new user '%s'" % username

	return True

def main( *args ):
	from optparse import OptionParser
	parser = OptionParser( usage = USAGE )

	parser.add_option( "-H", "--host", dest="db_host",
			default=DEFAULT_DB_HOST,
			help = "Connect to the MySQL server on the given host." )
	parser.add_option( "-u", "--user", dest="db_user",
			default=DEFAULT_DB_USER )
	parser.add_option( "-p", "--password", dest="db_passwd",
			default=DEFAULT_DB_PASSWD )
	parser.add_option( "-d", "--db_name", dest="db_name",
			default=DEFAULT_DB_NAME )

	(options, args) = parser.parse_args()

	loginDetails = dict(
		host = options.db_host,
		user = options.db_user,
		passwd = options.db_passwd,
		db = options.db_name )

	numArgs = len( args )

	if numArgs > 2:
		print "Too many arguments"
		parser.print_usage()
		return -1

	username, password = args + (2-numArgs) * [None]

	if not addAccount( username, password, loginDetails ):
		return -1

	return 0

if __name__ == '__main__':
	import sys
	try:
		sys.exit( main( sys.argv ) )
	except KeyboardInterrupt:
		print

# add_account.py
