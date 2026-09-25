#!/usr/bin/env python

"""
Delete log segments that were terminated before the designated time.

Default behaviour is delete all logs that are older than 1 week.

With the --dirty switch, the time is ignored and log segments included in the
dirty_files list in the log directory will be deleted (along with dirty_files
itself).

Compatibility
-------------

This utility is specific to the MLDB backend and requires MLDB-specific
functionality that exists only within the MessageLog class. It will therefore
continue to use the original MessageLog class.
"""

import os
import sys
import time

import util

import bwsetup; bwsetup.addPath( ".." )
import pycommon.util
from pycommon.log_storage_interface.log_db_constants import BACKEND_MLDB

import logging
pycommon.util.setUpBasicCleanLogging()
log = logging.getLogger( __name__ )


USAGE = "%prog [options] [logdir]\n" + __doc__.rstrip()


def main():
	parser = util.getBasicOptionParser( USAGE )
	parser.add_option( "-a", "--all", action = "store_true",
					   help = "Delete segments for all users" )
	parser.add_option( "--hours", type = "int",
					   help = "Specify period in hours" )
	parser.add_option( "--days", type = "int", default = 7,
					   help = "Specify period in days" )
	parser.add_option( "--dirty", action = "store_true",
					   help = "Delete files listed in dirty_files" )

	options, args = parser.parse_args()
	reader = util.initReader( BACKEND_MLDB, args )

	# Get an mlog object from the reader. If it does not exist then
	# MessageLogger is not configured correctly for MLDB.
	try:
		mlog = reader.logDB
	except:
		log.error( "Unable to access mlog object. "
				"MessageLogger may not be configured for MLDB.")
		return 1

	if options.dirty:
		deleteDirty( mlog )
		return 0

	if options.all:
		users = sorted( mlog.getUsers().items(), key = lambda (x,y): y )
	else:
		options.uid = util.getUserUID( options, reader )
		users = [(mlog.getUserLog( options.uid ).username, options.uid)]

	if options.hours:
		seconds = 60 * 60 * options.hours
	else:
		seconds = 60 * 60 * 24 * options.days

	activeFiles = set( ["%s/%s" % (mlog.logDirectory, f)
						for f in mlog.getActiveFiles()] )

	for username, uid in users:
		delete( mlog, uid, seconds, activeFiles )

	return 0


def unlink( fname ):
	try:
		os.unlink( fname )
		log.info( "Deleted %s", fname )
		return True
	except Exception, e:
		log.error( "Coudln't delete %s: %s", fname, e )
		return False


def delete( mlog, uid, seconds, activeFiles ):
	"""
	Delete all log segments from this log that we terminated more than the given
	number of seconds ago.  Files listed in activeFiles will not be touched.
	"""

	ulog = mlog.getUserLog( uid )
	segcount = len( ulog.getSegments() )

	for seg in ulog.getSegments():
		if time.time() - seg.end >= seconds:
			for prefix in ("entries","args","text","metadata"):

				fname = "%s/%s/%s.%s" % \
						(mlog.logDirectory, ulog.username, prefix, seg.suffix)

				if fname not in activeFiles and os.path.exists( fname ):
					unlink( fname )

			segcount -= 1

	# If we just removed all of this guy's log segments, blow away his entire
	# log directory
	if segcount == 0:
		log.info( "Removing empty log directory for %s", ulog.username )
		os.system( "rm -rf %s/%s" % (mlog.logDirectory, ulog.username) )


def deleteDirty( mlog ):
	"""
	Delete all files listed in dirty_files, as well as dirty_files itself.
	"""

	path = "%s/dirty_files" % mlog.logDirectory
	if not os.path.exists( path ):
		return True

	for fname in pycommon.util.chomp( open( path ).readlines() ):
		unlink( "%s/%s" % (mlog.logDirectory, fname) )

	unlink( path )

if __name__ == "__main__":
	sys.exit( main() )
