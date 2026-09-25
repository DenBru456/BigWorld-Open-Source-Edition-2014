#!/usr/bin/env python

# Import pycommon modules (always do this first!)
import bwsetup
bwsetup.addPath("..")

from pycommon import util, uid

# Import standard modules
import time
import sys
import os
import constants
import logging
import signal
from optparse import OptionParser
from optparse import OptionGroup

# Logging module, set it up before importing local files
logging.basicConfig( format = '%(asctime)s: %(levelname)s  %(message)s' )
logging.getLogger().setLevel( logging.INFO )
log = logging.getLogger( __name__ )

# Import local files
import prefxml
import utilities
import comparepref
from stat_gatherer import StatGatherer
from model.db_store import DbStore
from model.carbon_store import CarbonStore

from pycommon import watcher_data_message

#------------------------------------------------------------------------------
# Section: main function
#------------------------------------------------------------------------------
def main( args ):
	"""
	StatLogger main function.
	"""

	# Check pref filename to use
	if args.prefFilename:
		prefFilename = args.prefFilename
	else:
		prefFilename = constants.prefFilename

	# Read preferences
	try:
		options, prefTree = prefxml.loadPrefsFromXMLFile( prefFilename )
		# args uid overrides
		if args.uid:
			options.uid = int(args.uid)
	except prefxml.StatLoggerPrefError, e:
		log.error( "Error in preference file '%s':\n%s", prefFilename, e )
		sys.exit( 1 )

	# Adjust xml output format
	utilities.xmlModifyWriter()

	# Create and initialise stores
	# Now only support one DB and one Carbon, but easy to extend to support more
	dbStore = None
	carbonStore = None
	
	if options.dbStoreConfig and options.dbStoreConfig.enabled:
		try:
			dbStore = DbStore( options.dbStoreConfig,
				options.sampleTickInterval,	prefTree,
				args.allowCreate, args.dbName, args.useDbPrefs )
		except Exception, ex:
			log.error( "Failed to initialise DbStore for %s:%s.",
				options.dbStoreConfig.host, options.dbStoreConfig.port )
			sys.exit( 1 )
			
		# use the preference tree from database store module.
		prefTree = dbStore.getPrefTree()
	
	if options.carbonStoreConfig and options.carbonStoreConfig.enabled:
		try:
			carbonStore = CarbonStore( options.carbonStoreConfig, prefTree )
		except Exception, ex:
			log.error( "Failed to initialise CarbonStore for %s:%s, error: %s.",
				options.carbonStoreConfig.host,
				options.carbonStoreConfig.port,
				ex )
			if dbStore:
				dbStore.finalise()
			sys.exit( 1 )
		
	if not dbStore and not carbonStore: 
		log.error( "No backend data store is enabled. Exiting" )
		sys.exit( 1 )
	
	if args.listDb:
		if dbStore:
			dbStore.printLogList()
			dbStore.finalise()
			sys.exit( 0 )
		else:
			log.error( "DB store is not enabled in preference file" )
			sys.exit( 1 )		

	# Create gatherer and add enabled data stores
	usingFileOutput = (args.stdoutFile != None)
	gatherer = StatGatherer( sampleTickInterval = options.sampleTickInterval,
					usingFileOutput = usingFileOutput,
					prefTree = prefTree,
					uid = options.uid )
					
	if dbStore:
		gatherer.addDataStore( dbStore )
	if carbonStore:
		gatherer.addDataStore( carbonStore )
	
	# Start the gatherer
	gatherer.setDaemon( True )
	gatherer.start()

	# Setup the SIGUSR1 signal handler (to make it start debugger)
	def sigHandler( signum, frame ):
		gatherer.pushDebug()
	signal.signal( signal.SIGUSR1, sigHandler )
	
	# Enter thread monitor loop
	log.info( "Collecting stats, press Ctrl-C to stop..." )
	try:
		while gatherer.isAlive():
			time.sleep( 1.0 )
		log.error( "Gather thread exited unexpectedly, aborting." )
		sys.exit( 1 )
	except KeyboardInterrupt:
		log.info( "KeyboardInterrupt received. Finishing." )
	
	# This may be raised when receiving SIGTERM signal ( in daemon mode)
	# We should catch this and then pass to stop gatherer part
	# Otherwise the gatherer will continues running
	except SystemExit:
		log.info( "SystemExit received. Finishing." )
	
	if gatherer.isAlive():
		#Telling Gather thread to finish up
		gatherer.pushFinish()

		# Wait for the Gather thread to finish up writing log
		log.info( "Waiting for Gather thread to complete logging" )

		# If there's an error which freezes, time out after a minute
		gatherer.join( 60.0 )
	

def readArgs():
	"""
	Parse the command line arguments.
	"""
	#usage= "usage: %prog [options]"

	parser = OptionParser()
	parser.add_option( "-f", "--config-file",
		default = constants.prefFilename, dest = "prefFilename",
		metavar = "<preference_file>",
		help="Specifies a preference file to use instead of the default " \
			"(which is \"%default\")" )

	parser.add_option( "-n", "--database-name",
		default = None, type = "string", dest = "dbName",
		metavar = "db_name",
		help = "Name of the database to use. If the database does not exist, "\
				"it will automatically create it unless -p was specified. "\
				"Note: If using an existing database, it is recommended to "\
				"enable --use-db-prefs as well")

	parser.add_option( "-u", "--uid", default = None, dest = "uid",
		help = "uid of the processes to log" )

	parser.add_option( "-p", "--no-auto-create-db",
		default = True, dest = "allowCreate",
		action = "store_false",
		help = "Prevents creation of a new log database under any " \
				"circumstance." )

	parser.add_option("--pid", dest = "pidFile",
		metavar = "<pid_file>", default = "stat_logger.pid",
		help = "[daemon mode] Location to store PID file." )

	parser.add_option( "", "--use-db-prefs",
		default = False, dest = "useDbPrefs",
		action = "store_true",
		help = "Retrieve and use preferences from the log database being used "\
			"(ignores preference file)" )

	parser.add_option( "-l", "--list",
			default = False, action = "store_true",
			dest = "listDb",
			help = "Print a list of log databases" )

	parser.add_option( "-o", "--output",
			default = None, dest = "stdoutFile",
			metavar = "<output_file>",
			help = "Log file to dump standard output (default is stdout)" )

	parser.add_option( "-e", "--erroutput",
			default = None, dest = "stderrFile",
			metavar = "<output_file>",
			help = "Log file to dump error output (default is stderr)" )

	parser.add_option( "-d", "--daemon",
			default = True, action = "store_false", dest = "foreground",
			help = "Run stat_logger in daemon mode " \
					"(default is to run in foreground)" )

	parser.add_option( "-c", "--chdir",
		type = "string", dest = "chdir",
		help = "daemon working directory" )

	deprecated = OptionGroup( parser, "Deprecated Options",
		"These options have been deprecated and may be removed "
		"in the future." )

	deprecated.add_option( "", "--home",
		type = "string", dest = "home",
		help = "daemon working directory (superseded by --chdir)" )

	parser.add_option_group( deprecated )


	args, remain = parser.parse_args()

	return args

# readArgs


class AbortConnect( Exception ):
	""" Exception when we can't connect to the database. """
	pass
	

def testStores( args ):
	# Check pref filename to use
	if args.prefFilename:
		prefFilename = args.prefFilename
	else:
		prefFilename = constants.prefFilename

	# Read preferences
	try:
		options, prefTree = prefxml.loadPrefsFromXMLFile( prefFilename )
	except prefxml.StatLoggerPrefError, e:
		log.error( "Error in preference file '%s':\n%s", prefFilename, e )
		return False
		
	dbOk = None
	carbonOk = None
	
	# Test DB if enabled
	if options.dbStoreConfig and options.dbStoreConfig.enabled:
		if not DbStore.testConnection( options.dbStoreConfig ):
			log.error( "Failed to connect to DB." )
			dbOk = False
		else:
			dbOk = True
	else:
		log.info( "Database data store is not enabled." )
	
	# Test Carbon if enabled
	if options.carbonStoreConfig and options.carbonStoreConfig.enabled:
		if not CarbonStore.testConnection( options.carbonStoreConfig ):
			log.error( "Failed to connect to Carbon." )
			carbonOk = False
		else:
			carbonOk = True
	else:
		log.info( "Carbon data store is not enabled." )
	
	# If no data store is enabled or failed to connect any enabled, return False
	if ( dbOk == None and carbonOk == None) \
			or dbOk == False or carbonOk == False:
		return False
	
	return True
	
	
if __name__ == "__main__":
	# Read arguments
	args = readArgs()
	
	if args.foreground:
		main( args )
	else:
		# redirect log to files
		util.redirectLogOutputToFiles( args.stdoutFile, args.stderrFile )
		
		# not to start as daemon when cannot connect to all enabled data stores
		if not testStores( args ):
			log.error( "Failed to connect to data stores. Exiting." )
			sys.exit( 1 )

		chdirPath = ""

		if args.home:
			log.warn( "'--home' has been deprecated and may be removed "
				"in the future.\nUse '--chdir' instead." )

		if args.chdir:
			if args.home:
				log.warn( "defaulting to chdir rather than home" )

			chdirPath = args.chdir

		elif args.home:
			chdirPath = args.home

		if not chdirPath:
			defaultDir = os.path.abspath( os.path.dirname( sys.argv[0] ) )
			log.warn( "defaulting daemon cwd to stat_logger directory: '%s'",
				defaultDir )
			chdirPath = defaultDir


		from pycommon.daemon import Daemon
		d = Daemon( run = main,
			args = (args,),
			workingDir = chdirPath,
			outFile = args.stdoutFile,
			errFile = args.stderrFile,
			pidFile = args.pidFile,
			umask = 0033
		)
		d.start()

# stat_logger.py
