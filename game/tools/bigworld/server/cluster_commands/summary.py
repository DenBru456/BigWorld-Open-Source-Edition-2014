#!/usr/bin/env python
"""   Show summarised information about the current user's server."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "summary"


def getHelpStr():
	return __doc__


def run( args, env ):
	if args:
		env.warning( "Extra arguments given - %s", ', '.join( args ) )

	env.getUser( fetchVersion = True ).lsSummary()
	return True


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# summary.py
