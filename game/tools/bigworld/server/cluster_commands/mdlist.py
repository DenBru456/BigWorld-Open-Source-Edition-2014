#!/usr/bin/env python
"""   Display a comma separated list of hosts running machined on the local
    network, useful for passing to pdsh's -w option.

   Command Options:
    -d|--delim <D>:  Separator to use when displaying machines list.
    -i|--ip:         Return a list of IP addresses, instead of hostnames
                     (useful when DNS mapping is incomplete)"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-i", "--ip", action = "store_true" )
	sopt.add_option( "-d", "--delim", default = "," )

	return sopt


def getUsageStr():
	return "mdlist [<machines>] [options]"


def getHelpStr():
	return __doc__


def run( args, env ):
	from pycommon import util

	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	status = True

	# machineList = command_util.selectMachines( self.cluster, parsedArgs )
	machineList = env.getSelectedMachines( parsedArgs )
	if machineList:
		if options.ip:
			sortedMachines = sorted( [m.ip for m in machineList],
									util.cmpAddr )
		else:
			sortedMachines = sorted( [m.name for m in machineList] )

		env.info( options.delim.join( sortedMachines ) )

	else:
		status = False

	return status


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# mdlist.py
