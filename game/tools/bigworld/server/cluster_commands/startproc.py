#!/usr/bin/env python
"""   Start an instance of the given process each machine specified.

   Command Options:
   -n:           More than one process of the specified type may be started on
    			 each specified machine using this option.
   --bwConfig:   Choose to start process on debug or hybrid mode."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return "startproc <process name> <machines> [-n|--number <number>]"


def getHelpStr():
	return	__doc__


def _buildOptionsParser():
	import optparse
	from pycommon.cluster_constants	import BW_SUPPORTED_CONFIGS, \
			BW_CONFIG_HYBRID

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-n", "--number", type = "int", default = 1 )
	sopt.add_option( "--bwConfig", type = "choice", action = "store",
			choices = BW_SUPPORTED_CONFIGS, default = BW_CONFIG_HYBRID )

	return sopt


def run( args, env ):
	status = True

	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	if len( parsedArgs ) < 2:
		return env.usageError(
					"You must pass a process type and the machine to start on.",
					getUsageStr )
	else:
		processName = parsedArgs[0]
		machineNames = parsedArgs[1:]

		status = command_util.startProcess( env.getCluster(), env.getUser(),
								processName, machineNames, options.number,
								bwConfig = options.bwConfig )
		if status:
			env.getUser( fetchVersion = True ).ls()

	return status


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# startproc.py
