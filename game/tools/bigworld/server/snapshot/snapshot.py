#!/usr/bin/env python
"""
This utility takes a snapshot of the primary and secondary databases.
These databases are optionally consolidated. Messages are sent
to message_logger instead of stdout/stderr.
"""

import array
import sys
import os
import shutil
import time
import datetime
import socket
import subprocess
import tempfile
import MySQLdb
import optparse

# Import pycommon modules
import bwsetup
bwsetup.addPath( ".." )

from pycommon import bwconfig
from pycommon.cluster import Cluster
from pycommon import uid as uidmodule
from pycommon import util

import logging


if __name__ == "__main__":
	util.setUpBasicCleanLogging()

log = logging.getLogger( __name__ )


# Snapshots are achived in directories named in this time format
ARCHIVE_STR_F_TIME = "%Y%m%d_%H%M%S"

LOCK_FILE = ".lock"

SECONDARY_DB_FILE_LIST = "secondarydb.list"

WAIT_FOR_DB_REPORT_PERIOD_SECONDS = 30
PID_FILE_WAIT_TIMEOUT_SECONDS = 60

cluster = Cluster()
me = cluster.getUser( uidmodule.getuid() )

# ------------------------------------------------------------------------------
# Section: Main
# ------------------------------------------------------------------------------

USAGE = "usage: %prog [options] SNAPSHOT_DIR"

OPTIONS = [	( ["-b", "--bwlimit-kbps"], {"type": "int",
			  	"help": "file transfer bandwidth limit in kbps, "
						"default is unlimited"} ),
			( ["-n", "--no-consolidate"], {"action": "store_true",
			  	"help": "skip consolidation, default is false"} ) ]

def debug( msg, *args ):
	s = msg % args
	print s
	me.log( "Snapshot: " + s )

def error( msg, *args ):
	s = msg % args
	print "ERROR:", s
	me.log( "Snapshot: " + s, "ERROR" )

def main():
	# Parse command line
	parser = optparse.OptionParser( USAGE )
	for switches, kwargs in OPTIONS:
		parser.add_option( *switches, **kwargs )
	(options, args) = parser.parse_args()

	# Check snapshot directory arg
	if not args:
		parser.error( "missing argument" )

	snapshotDir = os.path.abspath( args[0] )
	if not os.access( snapshotDir, os.F_OK ):
		parser.error( "directory %s is non-existent" % snapshotDir )

	# Set options
	bwLimit = "0"
	if options.bwlimit_kbps:
		bwLimit = str( options.bwlimit_kbps )

	shouldConsolidate = True
	if options.no_consolidate:
		shouldConsolidate = not options.no_consolidate


	# Cannot take simultaneous snapshots
	errorMsg = lock( snapshotDir + os.sep + LOCK_FILE )
	if errorMsg is None:
		try:
			errorMsg = snapshot( snapshotDir, bwLimit,
				shouldConsolidate )
		finally:
			unlock( snapshotDir + os.sep + LOCK_FILE )

	if errorMsg:
		error( errorMsg )
		sys.exit( -1 )
	else:
		sys.exit( 0 )


# ------------------------------------------------------------------------------
# Section: Snapshot
# ------------------------------------------------------------------------------

def snapshot( snapshotDir, bwLimit, shouldConsolidate ):
	startTime = time.time()

	if not me.serverIsRunning():
		return "Server is not running"

	# Not using /tmp as it may not be on the same drive
	tempDir = os.path.join( snapshotDir, "temp" )
	if not os.path.exists( tempDir ):
		os.mkdir( tempDir )

	(errorMsg, secDBs, secDBFileList) = \
		requestSecondaryDBs( tempDir,bwLimit )
	if errorMsg:
		return errorMsg

	(errorMsg, priDB) = requestPrimaryDB( tempDir, bwLimit )
	if errorMsg:
		return errorMsg

	# Incomming databases
	dbs = [priDB]
	dbs.extend( secDBs )

	waitForDBs( dbs )

	filesToArchive = []
	filesToArchive.append( priDB )

	isConsolidated = shouldConsolidate

	if shouldConsolidate:
		errorMsg = consolidate( dbs, secDBFileList )
		if errorMsg:
			error( "Snapshot: %s", errorMsg)
			isConsolidated = False

	if not isConsolidated:
		debug( "Failed to consolidate" )
		filesToArchive.extend( secDBs )

	os.remove( secDBFileList )

	archiveDir = archive( filesToArchive, snapshotDir )

	shutil.rmtree( tempDir )

	endTime = time.time() - startTime

	debug( "Snapshot: Created %s in %s seconds (consolidated=%s)",
			archiveDir, int( endTime ), isConsolidated )


# ------------------------------------------------------------------------------
# Section: Helpers
# ------------------------------------------------------------------------------

def lock( lockFile ):
	if os.access( lockFile, os.F_OK ):
		return "A snapshot is still in progress: %s" % lockFile
	else:
		file = os.open( lockFile, 755 )
		os.close( file )
		return None


def unlock( lockFile ):
	os.remove( lockFile )


def findDBApp():
	p = me.getProc( "dbapp" )
	if p:
		return p.machine.ip
	else:
	 	return None


def requestSecondaryDBs( snapshotDir, bwLimit ):
	debug( "* Requesting Secondary DBs" )

	dbHost = bwconfig.get( "dbApp/host" )
	dbUser = bwconfig.get( "dbApp/username" )
	dbPass = bwconfig.get( "dbApp/password" )
	dbName = bwconfig.get( "dbApp/databaseName" )

	# It is only localhost for dbApp
	if dbHost == "localhost":
		dbHost = findDBApp()
		if dbHost == None:
			return ( "Could not find MySQL server localhost to DBApp", [], None )

	# Read secondary databases info
	try:
		conn = MySQLdb.connect( host = dbHost,
								user = dbUser,
								passwd = dbPass,
								db = dbName,
								charset = 'utf8' )

		cursor = conn.cursor()
		cursor.execute( "SELECT INET_NTOA(ip), location FROM "	\
			   			"bigworldSecondaryDatabases" )
		results = cursor.fetchall()
		cursor.close()
		conn.close()
	except:
		return ( "Could not read secondary database info from primary "	\
			   "database: %s" % dbHost, [], None )

	secDBs = []

	args = [ "snapshotsecondary",
			 "filenamePlaceHolder",
			 cluster.getMachine( socket.gethostname() ).ip,
			 snapshotDir,
			 bwLimit ]

	# Get SQLite files via transfer_db
	for ip, remotePath in results:
		m = cluster.getMachine( ip )
		if not m:
			return ( "Could not find %s to request %s" % (ip, remotePath),
				[], None )

		if isinstance( remotePath, array.array ):
			remotePath = remotePath.tostring()

		args[ 1 ] = remotePath

		if m.startProcWithArgs( "commands/transfer_db", args, me.uid ) == 0:
			return ( "Could not start transfer_db on %s" % ip, [], None )

		localPath = os.path.join( snapshotDir, os.path.basename( remotePath ) )
		secDBs.append( localPath )

	# Used as a consolidate_dbs args
	secDBFileList = os.path.join( snapshotDir, SECONDARY_DB_FILE_LIST )

	file = open( secDBFileList, "w" )
	for db in secDBs:
		file.write( db + "\n" )
	file.close()

	return ( None, secDBs, secDBFileList )


def requestPrimaryDB( snapshotDir, bwLimit ):
	debug( "* Requesting Primary DBs" )

	dbHost = bwconfig.get( "dbApp/host" )
	dbUser = bwconfig.get( "dbApp/username" )
	dbPass = bwconfig.get( "dbApp/password" )
	dbName = bwconfig.get( "dbApp/databaseName" )

	# It's only localhost for dbApp
	if dbHost == "localhost":
		dbHost = findDBApp()
		if dbHost == None:
			return ( "Could not resolve localhost to DBApp machine", None )

	m = cluster.getMachine( dbHost )

	args = ["snapshotprimary",
			cluster.getMachine( socket.gethostname() ).ip,
			snapshotDir,
			bwLimit]

	if m.startProcWithArgs( "commands/transfer_db", args, me.uid ) == 0:
		return ( "Could not start transfer_db on %s" % dbHost, None )

	localPath = os.path.join( snapshotDir, "mysql" )

	return ( None, localPath )


def waitForDBs( dbs ):
	debug( "* Waiting for DBs" )

	# transfer_db must send this file last
	indicators = ["%s.complete" % db for db in dbs]

	start = time.time()
	while indicators:
		time.sleep( 2 )
		for i in indicators:
			if os.access( i, os.F_OK ):
				os.remove( i )
				indicators.remove( i )
			elif time.time() - start > WAIT_FOR_DB_REPORT_PERIOD_SECONDS:
				debug( "Waiting for %s", i )



def consolidate( dbs, secDBFileList ):
	debug( "* Consolidating" )
	dbUser = bwconfig.get( "dbApp/username" )
	dbPass = bwconfig.get( "dbApp/password" )
	dbName = bwconfig.get( "dbApp/databaseName" )
	dbDataDir = dbs[0]
	dbSock = "%s/mysql.sock" % dbDataDir
	dbPidFile = "%s/snapshot.pid" % dbDataDir

	# Pick a free port
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.bind( ("127.0.0.1", 0) )
	dbPort = s.getsockname()[1]
	s.close()

	# Create temp MySQL config file
	mycnf = tempfile.mkstemp()[1]
	file = open( mycnf, "w" )
	file.writelines( ["[mysqld1]\n",
					"datadir=%s\n" % dbDataDir,
					"socket=%s\n" % dbSock,
					"port=%s\n" % dbPort,
					"pid-file=%s\n" % dbPidFile] )
	file.close()

	# Start a MySQL server
	cmd = "mysqld_multi --defaults-file=%s start 1 &> /dev/null" % mycnf
	if os.system( cmd ) != 0:
		return "Could not start MySQL server for consolidation "	\
				"(host = localhost, port = %s, dataDir = %s)" %		\
				( dbPort, dbDataDir )


	try:

		# Wait for MySQL server to ramp up
		# TODO: Currently tests forever
		while True:
			try:
				conn = MySQLdb.connect( user = dbUser,
										passwd = dbPass,
										db = dbName,
										unix_socket = dbSock )
				break
			except:
				time.sleep( 1 )

		# Consolidate
		scriptDir = os.path.dirname( os.path.abspath( __file__ ) )
		binaryPath = "../../../bin/%s" % util.MF_CONFIG()

		consolidateBinary = os.path.join( scriptDir, binaryPath,
			"commands/consolidate_dbs" )

		primaryDBArg = "%s;%s;%s;%s;%s" % \
			( cluster.getMachine( socket.gethostname() ).ip,
				dbPort, dbUser, dbPass, dbName )

		consolidateCommand = [consolidateBinary, primaryDBArg, secDBFileList]

		pipe = subprocess.Popen( consolidateCommand,
				stdin = None,
				stdout = subprocess.PIPE, stderr = subprocess.STDOUT )

		consolidateOutput = ''
		isConsolidateOK = True

		while pipe.poll() is None:
			consolidateOutput += pipe.stdout.read()

		exitCode = pipe.wait()
		consolidateOutput += pipe.stdout.read()

		if (not os.WIFEXITED( exitCode )) or os.WEXITSTATUS( exitCode ) != 0:
			if (os.WIFSIGNALED( exitCode )):
				debug( "Consolidate command was killed with signal %d",
					os.WTERMSIG( exitCode ) )
			elif os.WIFEXITED( exitCode ):
				debug( "Consolidate command failed with exit status %d",
					os.WEXITSTATUS( exitCode ) )
			error( "ConsolidateDBs failed" )
			isConsolidateOK = False

		# Deregister secondary databases
		if isConsolidateOK:
			cursor = conn.cursor()
			cursor.execute( "DELETE FROM bigworldSecondaryDatabases" )
			cursor.close()
			conn.commit()

		conn.close()

	finally:
		# Stop server
		cmdStop = "mysqld_multi --defaults-file=%s stop 1 &> /dev/null" % mycnf
		isStopOK = os.system( cmdStop ) == 0

		# Wait for MySQL server to ramp down
		# TODO: Currently tests forever

		canConnect = True
		while canConnect:
			try:
				conn = MySQLdb.connect( user = dbUser,
										passwd = dbPass,
										db = dbName,
										unix_socket = dbSock )
				conn.close()
				time.sleep( 1 )
			except:
				canConnect = False

		# Wait for the pid file to be removed. This might cause problems later
		# on when we archive the mysql data directory and it is removed while
		# we copy.
		pidFileExists = os.path.exists( dbPidFile )
		count = 0
		while pidFileExists and count < PID_FILE_WAIT_TIMEOUT_SECONDS:
			time.sleep( 1 )
			pidFileExists = os.path.exists( dbPidFile )
			count += 1

	if not isConsolidateOK:
		return "Could not consolidate: \n%s" % consolidateOutput

	# Remove secondary databsses
	for db in dbs[1:]:
		os.remove( db )
		dbs.remove( db )

	if not isStopOK:
		return "Could not stop MySQL server for consolidation "	\
				"(host=localhost, port=%s, dataDir=%s)" %		\
				( dbPort, dbDataDir )

	return None


def archive( dbs, snapshotDir ):
	debug( "* Archiving" )

	dt = datetime.datetime.now()
	archiveDir = snapshotDir + os.sep + dt.strftime( ARCHIVE_STR_F_TIME )
	os.mkdir( archiveDir )

	for db in dbs:
		dst = archiveDir + os.sep + db.split( os.sep )[-1]

		if os.path.isfile( db ):
			shutil.copy( db, dst )
		else:
			shutil.copytree( db, dst )

	return archiveDir


if __name__ == "__main__":
	sys.exit( main() )

# snapshot.py

