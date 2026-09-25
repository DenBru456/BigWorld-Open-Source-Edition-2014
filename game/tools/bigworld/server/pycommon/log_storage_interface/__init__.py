"""BigWorld log storage interface for accessing MessageLogger logs."""

import log_db_constants

HAS_MLDB_SUPPORT = False
mldbImportErrorMessage = None
try:
	from mldb_log_reader import MLDBLogReader
	HAS_MLDB_SUPPORT = True

except ImportError, ie:
	mldbImportErrorMessage = str( ie )


HAS_MONGODB_SUPPORT = False
mongoDBImportErrorMessage = None
try:
	import pymongo
	if str(pymongo.version) < '2.5.2':
		mongoDBImportErrorMessage = "pymongo library version is older than 2.5.2."

	HAS_MONGODB_SUPPORT = True
except ImportError:
	mongoDBImportErrorMessage = "Unable to import pymongo library"

if HAS_MONGODB_SUPPORT:
	from mongodb_log_reader import MongoDBLogReader


import bwsetup
bwsetup.addPath( "../.." )
from pycommon.exceptions import NotSupportedException, ServerStateException

import ConfigParser
import os
import logging
log = logging.getLogger( __file__ )


def createReader( storageType = None, rootLogPath = None ):
	"""
	Creates a reader object, as determined by the reader type. If storageType is
	not provided, the storageType stored in Message Logger configuration file
	will be used.
	"""
	config = getConfig()

	if not config:
		raise ServerStateException(
					"Failed to locate Message Logger config file.")

	# Determine the reader type from the config file
	if not storageType:
		storageType = config.get( 'message_logger', 'storage_type',
						log_db_constants.BACKEND_MLDB )

	# Force all lower case on config storage_type before we start comparing.
	storageType = storageType.lower()

	# When rootLogPath is provided, force the reader to read that path as an
	# MLDB data source (provides backward compatibility when reading from
	# uncompressed archives)
	if rootLogPath and (storageType != log_db_constants.BACKEND_MLDB):
		raise ValueError( "A log path was specified but storage type is "
			"not %s (%s)" % (log_db_constants.BACKEND_MLDB, storageType) )

	if storageType == log_db_constants.BACKEND_MLDB:
		if not HAS_MLDB_SUPPORT:
			log.error( "Unable to create MLDB reader." )
			raise NotSupportedException( mldbImportErrorMessage )

		if rootLogPath:
			return MLDBLogReader( config, rootLogPath )
		else:
			return MLDBLogReader( config )
	# log_db_constants.BACKEND_MLDB


	if storageType == log_db_constants.BACKEND_MONGODB:
		# Failure to import pymongo is not a fatal error until there is an
		# attempt to use it (as attempted use does not happen until runtime).
		if not HAS_MONGODB_SUPPORT:
			log.error( mongoDBImportErrorMessage )
			raise NotSupportedException( mongoDBImportErrorMessage )

		return MongoDBLogReader( config )
	# log_db_constants.BACKEND_MONGODB

	# If this point is reached then 
	raise NotSupportedException( "Reader type '%s' is not supported." %
		storageType )

# getReader


def getConfig():
	"""This function attempts to locate the MessageLogger configuration file
	in all the possible locations that it may be installed, both absolute
	paths and relative to the currently running application."""

	if os.path.isfile( "/etc/bigworld/message_logger.conf" ):
		mldir = "/etc/bigworld"
	else:
		# Try global one first
		try:
			config = ConfigParser.SafeConfigParser()
			config.read( "/etc/bigworld.conf" )
			globalConf = dict( config.items( "tools" ) )
			mldir = globalConf[ "location" ] + "/message_logger"

		# Otherwise fall back to the directory this file lives in
		except KeyError:
			mldir = os.path.join( bwsetup.appdir, "../../message_logger" )
		except ConfigParser.NoSectionError:
			mldir = os.path.join( bwsetup.appdir, "../../message_logger" )
	
	configFilePath = "%s/message_logger.conf" % mldir

	if not os.path.isfile( configFilePath ):
		log.error( "Config file (%s) doesn't exist.", configFilePath)
		return None

	config = ConfigParser.SafeConfigParser()
	config.read( configFilePath )

	# Add mldb section and mldir option to config object. These are used in MLDB
	if not config.has_section( "mldb" ):
		config.add_section( "mldb" )
	config.set( "mldb", "mldir", mldir )
	
	# Test to ensure config file is in newest format
	try:
		config.get( "message_logger", "storage_type" )
	except:
		# Old config format: attempt to convert to new format
		# (added here to prevent duplicate code in message_log.py. 
		# This adds these settings to the config object only, not the file
		try:
			config.set( "message_logger", "storage_type", "mldb" )
			config.set( "mldb", "logdir", config.get( "message_logger", 
					"logdir" ) )
			config.set( "mldb", "segment_size", config.get( "message_logger",
					"segment_size" ) )
			config.set( "mldb", "default_archive", config.get( "message_logger",
					"default_archive" ) )
		except:
			log.error( "Config file (%s) misconfigured.", configFilePath )
			return None

	return config

# getConfig


def getValidBackendsByName():
	return log_db_constants.VALID_BACKENDS

# getValidBackendsByName
