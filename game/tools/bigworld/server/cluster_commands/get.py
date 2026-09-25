#!/usr/bin/env python
"""   Queries the specified watcher path on all processes of the specified type
   currently active in the cluster.

   If no watcher path is specified, the root directory will be listed.

   See also: 'set'"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return "get <processes> [watcher-path]"


def getHelpStr():
	return __doc__


def run( args, env ):
	from pycommon import util

	if len( args ) < 1:
		return env.usageError( "Insufficient arguments", getUsageStr )

	# Use the provided watcher path, otherwise assume the root path
	watcherPath = ""
	if len( args ) > 1:
		watcherPath = args.pop()

	# TODO: Should this be done generally in getWatcherData?
	if watcherPath.endswith( '/' ):
		watcherPath = watcherPath[:-1]

	if not args:
		return env.usageError( "No processes specified", getUsageStr )

	processList = env.getSelectedProcesses( args )
	if not processList:
		env.error( "No processes selected" )
		return False

	processList.sort( lambda x, y: cmp( x.label(), y.label() ) )

	for process in processList:
		wd = process.getWatcherData( watcherPath )
		util.printNow( "%-12s on %-8s -> " \
			% (process.label(), process.machine.name) )

		if wd.isDir():
			env.info( "<DIR>" )
			for entry in wd:
				env.info( "\t%s" % entry )
		else:
			env.info( wd )

	return True


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# get.py
