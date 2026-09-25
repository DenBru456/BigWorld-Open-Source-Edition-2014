#!/usr/bin/env python
"""   Kill and then restart a process on the same machine."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return "restartproc <process>"


def getHelpStr():
	return __doc__


def run( args, env ):
	status = True

	if not args:
		return env.usageError( "You must select a process", getUsageStr )

	processFilters = args
	processList = env.getSelectedProcesses( processFilters )

	if not processList:
		env.error( "Unable to find process type '%s'", args[0] )
		return False

	if len( processList ) != 1:
		return env.usageError( "You must select a single process", getUsageStr )

	process = processList[0]
	processName = process.name
	machine = process.machine

	if not machine.killProc( process ):
		env.error( "Unable to shut down %s", process.label() )
		status = False

	if not machine.startProc( processName, env.getUser().uid ):
		env.error( "Unable to restart process %s", processName )
		status = False

	return status


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# restartproc.py
