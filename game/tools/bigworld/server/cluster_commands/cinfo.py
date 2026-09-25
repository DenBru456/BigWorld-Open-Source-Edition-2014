#!/usr/bin/env python
"""   Show information about machines in a server cluster.

   If no machines are specified, information from all machines in the server
   cluster will be displayed.

   Command Options:
    -p,--show-platform:   Also fetch and display the platform information.
"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util
from pycommon.machine import Machine


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-p", "--show-platform", action = "store_true",
					dest="showPlatform", default = False )

	return sopt

def getUsageStr():
	return "cinfo [-p|--show-platform] [<machines>]"


def getHelpStr():
	return __doc__


def run( args, env ):
	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	shouldRetrievePlatformInfo = options.showPlatform

	machineList = parsedArgs 
	if machineList:
		machines = env.getSelectedMachines( machineList, 
											shouldRetrievePlatformInfo )
	else:
		machines =  env.getCluster( shouldRetrievePlatformInfo ).getMachines()
		machines.sort( Machine.cmpByHostDigits )

	if not machines:
		return False
	
	for machine in machines:
		env.info( machine.getFormattedStr( shouldRetrievePlatformInfo ) )

	# no machines are specified, output the total number of machines
	if not machineList and machines:
		env.info( "%d machines total" % len( machines ) )

	return True


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# cinfo.py
