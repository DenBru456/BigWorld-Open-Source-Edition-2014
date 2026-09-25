#!/usr/bin/env python
"""   Stop the specified processes gracefully.

   Attempts to shutdown the specified process in a manner that will not
   adversely effect the behaviour of an operational server.

   For CellApps, new entities are not accepted into existing cells and cells
   are slowly reduced in size until all cells have been removed at which point
   the CellApp is allowed to fully terminate.

   This command is deprecated and will be removed in a future version.

   See also: 'killproc'"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return "stopproc <processes>"


def getHelpStr():
	return __doc__


def run( args, env ):
	env.warning( 'This command is deprecated and will be removed in a future' + 
					' version.' )

	processFilters = args

	if not processFilters:
		return env.usageError( "No processes specified", getUsageStr )

	processes = env.getSelectedProcesses( processFilters )

	if not processes:
		env.error( "No processes found, or no server running" )
		return False

	for process in processes:
		process.stopNicely()

	return True


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# stopproc.py
