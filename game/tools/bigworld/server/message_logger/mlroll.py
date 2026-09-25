#!/usr/bin/env python

"""
Utility to roll logs.

Compatibility
-------------

This utility is specific to the MLDB backend and requires MLDB-specific
functionality that exists only within the MessageLog class. It will therefore
continue to use the original MessageLog class.
"""

import os
import sys
import signal
import time

import bwsetup; bwsetup.addPath( ".." )
import util
import pycommon.util
from pycommon.log_storage_interface.log_db_constants import BACKEND_MLDB

import logging
pycommon.util.setUpBasicCleanLogging()
log = logging.getLogger( __name__ )


USAGE = "%prog [options] [logdir]\n" + __doc__.rstrip()


def main():
	parser = util.getBasicOptionParser( USAGE )
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

	# Make sure the log is currently being written to
	if not os.path.exists( "%s/pid_lock" % mlog.logDirectory ):
		log.warning( "Not sending SIGHUP - no logger currently writing to %s",
					 mlog.logDirectory )
		return 0

	# Send HUP to the logger process
	os.kill( int( open( "%s/pid_lock" % mlog.logDirectory ).read() ), signal.SIGHUP )

	# Wait a little bit to allow the select() loop in message_logger to cycle
	time.sleep( 1 )

	return 0


if __name__ == "__main__":
	sys.exit( main() )
