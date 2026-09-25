#!/usr/bin/env python
"""   Show network statistics for a set of machines.

   If no machines are specified, network information from all machines in the
   server cluster will be displayed."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "netinfo [<machines>]"


def getHelpStr():
	return __doc__


def run( args, env ):
	machineList = args

	if machineList:
		# machines = command_util.selectMachines( self.cluster, machineList )
		machines = env.getSelectedMachines( machineList )
	else:
		machines = env.getCluster().getMachines()

	for machine in machines:
		env.info( machine.getFormattedStr() )
		for ifname, stats in sorted( machine.ifStats.items() ):
			if stats is not None:
				env.info( "\t%s" % stats )
		env.info( "\tloss: %d/%d" % (machine.inDiscards, machine.outDiscards) )

	return True


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# netinfo.py
