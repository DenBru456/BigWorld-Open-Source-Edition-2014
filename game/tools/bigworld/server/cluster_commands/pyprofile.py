#!/usr/bin/env python
"""   ERROR:  The 'pyprofile' command has been deprecated. Please use 'profile'
instead"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

import os
import sys

# Enable importing from pycommon
sys.path.append( os.path.dirname( __file__ ) + "/../.." )


def getUsageStr():
	return __doc__


def getHelpStr():
	return __doc__


def run( args, env ):
	return env.error( "The 'pyprofile' command has been deprecated please use "
		"'profile' instead." )


if __name__ == "__main__":
	from pycommon.command_util import runCommand
	from pycommon.util import setUpBasicCleanLogging

	setUpBasicCleanLogging()
	sys.exit( runCommand( run ) )

# pyprofile.py
