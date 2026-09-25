#!/usr/bin/env python
"""
Discover the buddy ring on the network and verify its correctness and response
time.
"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "pingring"


def getHelpStr():
	return __doc__


def run( args, env ):
	if args:
		env.warning( "No arguments expected" )

	from pycommon import ping_ring
	return ping_ring.pingRing()


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# pingring.py
