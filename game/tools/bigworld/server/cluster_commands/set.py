#!/usr/bin/env python
"""   Set a watcher to a new value for the specified processes.

   See also: 'get'"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return "set <processes> <watcher-path> <new-value>"


def getHelpStr():
	return __doc__


def run( args, env ):
	if len( args ) < 3:
		return env.usageError( "Insufficient arguments", getUsageStr )

	watcherPath, watcherValue = args[-2:]
	processFilters = args[:-2]

	if not processFilters:
		return env.usageError( "No processes specified", getUsageStr )


	processList = env.getSelectedProcesses( processFilters )

	if not processList:
		env.error( "No processes selected" )
		return False

	status = True

	for process in processList:
		if not process.setWatcherValue( watcherPath, watcherValue ):
			env.error( "Failed to set new value for %s (%s)",
					   process.name, process.machine.name )
			status = False

	return status


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# set.py
