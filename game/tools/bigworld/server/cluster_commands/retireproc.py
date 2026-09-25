#!/usr/bin/env python
"""   Retire processes (only applicable to BaseApps and CellApps)."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return "retireproc <process>"


def getHelpStr():
	return __doc__


def run( args, env ):
	# TODO: This should also be applicable to CellApp as well, but need to
	# check this. It would definitely not be hooked up to command/retireApp
	# command watcher.

	processFilters = args

	if not processFilters:
		return env.usageError( "No processes specified", getUsageStr )

	processes = env.getSelectedProcesses( processFilters )

	if not processes:
		env.error( "No processes selected" )
		return False

	for process in processes:
		if not hasattr( process, "retireApp" ):
			return env.usageError(
				"Process %s is not a retire-able process\n" % process.label(),
				getUsageStr )

	for process in processes:
		process.retireApp()

	return True


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# retireproc.py
