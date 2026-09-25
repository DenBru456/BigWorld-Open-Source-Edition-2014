#!/usr/bin/env python
"""   Show information about active users on the cluster.

   When used in conjunction with the -v option the processes being run by the
   user is also displayed."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "users"


def getHelpStr():
	return __doc__


def run( args, env ):
	if args:
		env.warning( "Extra arguments given - %s", ', '.join( args ) )

	env.getCluster().lsUsers()
	return True


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# users.py
