"""
Functions used by the ml* family of shell utilities.
"""

import optparse
import os
import sys

import bwsetup
bwsetup.addPath( ".." )

import pycommon.log_storage_interface

import logging
log = logging.getLogger( __name__ )


def getBasicOptionParser( usage = None ):
	"""
	Creates an option parser that supports all the basic arguments that tools in
	the ml*.py suite are expected to understand.
	"""

	opt = optparse.OptionParser( usage or "%prog [options] [logdir]" )
	opt.add_option( "-u", "--uid",
					help = "Specify the UID or username to work with" )
	return opt


def initReader( storageType = None, args = None ):
	"""
	Parse command line options using the given parser and return a log object,
	kwarg dictionary for fetches, and the parsed options.
	"""

	logDir = None

	if args:
		logDir = args[ 0 ]

	reader = pycommon.log_storage_interface.createReader( storageType, logDir )

	return reader


def getServerUser( options, reader ):

	# We're happy to use os.getuid() instead of uidmodule.getuid() because this
	# won't work on win32 anyways as bwlog.so is required.
	if options.uid is None:
		options.uid = os.getuid()

	serveruser = None

	try:
		options.uid = int( options.uid )

		# Log reader clients now pass usernames as params (rather than uids) to
		# the abstract query layer. Ask the DB layer for the username matching
		# the provided uid.
		foundUID = None

		for user in reader.getUsers().items():
			if options.uid == user[1]:
				serveruser = user[0]
				break
	except:
		# uid is a string (username)
		username = options.uid

		# confirm the validity of the provided username
		options.uid = reader.getUIDFromUsername( username )

		if options.uid:
			# if the above line was successful in retrieving the UID then store
			# the username as the serveruser
			serveruser = username
		else:
			log.error( "No log entries for user %s", username )
			sys.exit( 1 )

	# Store the serveruser as a queryable parameter
	return serveruser


def getUserUID( options, reader ):
	if options.uid is None:
		options.uid = os.getuid()

	try:
		options.uid = int( options.uid )

		for user in reader.getUsers().items():
			if options.uid == user[1]:
				return options.uid
	except:
		# uid is a string (username)
		username = options.uid

		# confirm the validity of the provided username
		options.uid = reader.getUIDFromUsername( username )
		if options.uid:
			return options.uid
		else:
			options.uid = username

	# If this point has been reached then the uid was not found in
	# the database. Report an error.
	log.error( "No log entries for user %s", options.uid )
	sys.exit( 1 )
