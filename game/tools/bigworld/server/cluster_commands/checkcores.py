#!/usr/bin/env python
"""   Checks whether the user has any core files or assertions.

   Command Options:
    -a,--show-asserts:   Show assertion logs (if they exist)"""

import time

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "checkcores"


def getHelpStr():
	return __doc__


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-a", "--show-asserts", action = "store_true" )

	return sopt

def run( args, env ):
	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	user = env.getUser( checkCoreDumps = True )

	numCores = len( user.coredumps )

	extra = ""
	if numCores >= 10:
		extra = " (or more)"

	bwRootInfo = ""
	if numCores > 0:
		bwRootInfo = " in %s" % user.mfroot

	env.info( "%d%s core files for %s%s on %s" %
		(numCores, extra, user, bwRootInfo, user._queryMachineName) )

	if numCores == 0:
		return 0

	coreList = user.getCoresSortedByTime()
	for corefile, assertMsg, timeStamp in coreList:
		prettyTime = time.ctime( timeStamp )
		env.info( "%s: %s", prettyTime, corefile )

		if options.show_asserts and assertMsg:
			env.info( assertMsg )

	return 1


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil
	
	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# checkcores.py
