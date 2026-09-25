#!/usr/bin/env python

"""
Display a listing of the segments in a user's message log.

Compatibility
-------------

This utility is specific to the MLDB backend and requires MLDB-specific
functionality that exists only within the MessageLog class. It will therefore
continue to use the original MessageLog class.
"""

import sys

import util
import message_log

import bwsetup; bwsetup.addPath( ".." )
import pycommon.util
from pycommon.log_storage_interface.log_db_constants import BACKEND_MLDB

import logging
log = logging.getLogger( __name__ )

USAGE = "%prog [options] [logdir]\n" + __doc__.rstrip()


def main():
	parser = util.getBasicOptionParser( USAGE )
	parser.add_option( "-a", "--all", action = "store_true",
					   help = "List segments for all users" )

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

	if options.all:
		users = sorted( mlog.getUsers().items(), key = lambda (x,y): y )
	else:
		options.uid = util.getUserUID( options, reader )
		users = [(mlog.getUserLog( options.uid ).uid, options.uid)]

	for username, uid in users:

		if len( users ) > 1:
			print "* %s (%d) *" % (username, uid)

		ls( mlog, uid )

		if len( users ) > 1:
			print

	return 0


def ls( mlog, uid, number = False ):

	segments = mlog.getUserLog( uid ).getSegments()
	totalSize = totalEntries = 0
	i = 0
	if segments:
		if number:
			print "  # ",
		print message_log.Segment.FMT % ("Time", "Duration", "Entries", "Size")
		for seg in segments:
			if number:
				print ("%3d " % i),
			print seg
			totalSize += seg.entriesSize + seg.argsSize
			totalEntries += seg.nEntries
			i += 1

		if not number:
			print "%d entries, %s total" % (totalEntries,
											pycommon.util.fmtBytes( totalSize ))

	return segments


if __name__ == "__main__":
	pycommon.util.setUpBasicCleanLogging()

	sys.exit( main() )
