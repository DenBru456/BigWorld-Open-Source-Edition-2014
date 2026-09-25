#!/usr/bin/env python
"""   Displays the current state of the server for the active user."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "display"


def getHelpStr():
	return __doc__


def run( args, env ):
	status = True

	processFilters = args

	if not processFilters:
		user = env.getUser( refreshEnv = True, fetchVersion = True )
		if env.isVerbose:
			print( "Binary set version: %s" % user.version )
		user.ls()
	else:
		processes = env.getSelectedProcesses( processFilters )

		if not processes:
			status = False
		else:
			for process in processes:
				env.info( process )

	return status


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# display.py
