#!/usr/bin/env python
"""   Queries the specified watcher path on all processes of the specified type
   currently active in the cluster. The path can contain '*' wildcards."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import watcher_tree_filter
from pycommon import command_util


def getUsageStr():
	return """getmany <processes> [watcher-path]"""


def getHelpStr():
	return __doc__


def run( args, env ):
	processFilters = args[:1]
	processes = env.getSelectedProcesses( processFilters )

	if not processes:
		return env.usageError(
			"You must specify at least one process to profile", getUsageStr )

	if len( args ) < 2:
		return env.usageError( "You must specify a path to query", getUsageStr )

	path = args[1]

	try:
		table = watcher_tree_filter.getFilteredTree( path, processes )
	except watcher_tree_filter.Error, e:
		env.error( e.msg )
		return False

	table.write()

	return True


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# getmany.py
