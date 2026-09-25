#!/usr/bin/env python

""" Check the server is running for a specific user, and output to conform
    to Nagios's plugin API.

    For remote machines, you can install NRPE, and configure it like this:

    command[check_bw]=<BIGWORLD_PATH>/bigworld/tools/server/control_cluster.py -u <USER> nagios  --num-baseapps-warning=2 --num-cellapps-warning=2

    You can then use Nagios's check_nrpe plugin command:

    define command {
        command_name    check_bigworld
        command_line    /usr/lib/nagios/plugins/check_nrpe -H '$HOSTADDRESS$' -c check_bw
    }

    define service {
        use                     generic-service
        host_name               bigworld-server
        service_description     BigWorld
        check_command           check_bigworld
    }

"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

import sys
import traceback

from pycommon import command_util
from pycommon.process import Process

from pycommon import user as user_module

class NagiosStatus( object ):
	def __init__( self, description, statusCode ):
		self.description = description
		self.statusCode = statusCode

	def __str__( self ):
		return self.description

NAGIOS_OK		= NagiosStatus( "OK", 0 )
NAGIOS_WARNING  = NagiosStatus( "WARNING", 1 )
NAGIOS_CRITICAL = NagiosStatus( "CRITICAL", 2 )
NAGIOS_UNKNOWN  = NagiosStatus( "UNKNOWN", 3 )


def getUsageStr():
	return \
"""nagios [-w|--load-warning <load_threshold>] [-c|--load-critical <load_threshold>] 
   [--num-baseapps-critical <num>] [--num-cellapps-critical <num>]
   [--num-baseapps-warning <num>] [--num-cellapps-warning <num>]"""


def getHelpStr():
	return __doc__ + "\n" + _buildOptionsParser().format_help()


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( usage="", add_help_option = True )

	sopt.add_option( "-w", "--load-warning", dest = "loadWarningThreshold", 
		default = 0.8, type = "float",
		metavar="LOAD_THRESHOLD",
		help = "Warn if either BaseApp or CellApp load goes above "
			"this" )
	sopt.add_option( "-c", "--load-critical", 
		dest = "loadCriticalThreshold",
		default = 1.0, type = "float",
		metavar="LOAD_THRESHOLD",
		help = "Critical if either BaseApp or CellApp load goes above "
			"this" )
	sopt.add_option( "--num-baseapps-critical", 
		dest = "numBaseAppsCriticalThreshold", 
		default = 1, type = "int",
		metavar="NUM_BASEAPPS",
		help = "Critical if the number of running BaseApps is less "
			"than this" )

	sopt.add_option( "--num-cellapps-critical", 
		dest = "numCellAppsCriticalThreshold", 
		default = 1, type = "int",
		metavar="NUM_CELLAPPS",
		help = "Critical if the number of running CellApps is less "
			"than this" )

	sopt.add_option( "--num-serviceapps-critical", 
		dest = "numServiceAppsCriticalThreshold", 
		default = 1, type = "int",
		metavar="NUM_SERVICEAPPS",
		help = "Critical if the number of running ServiceApps is less "
			"than this" )

	sopt.add_option( "--num-dbapps-critical", 
		dest = "numDBAppsCriticalThreshold", 
		default = 1, type = "int",
		metavar="NUM_DBAPPS",
		help = "Critical if the number of running DBApps is less "
			"than this" )

	sopt.add_option( "--num-baseapps-warning", 
		dest = "numBaseAppsWarningThreshold", 
		default = 1, type = "int",
		metavar="NUM_BASEAPPS",
		help = "Warn if the number of running BaseApps is less "
			"than this" )

	sopt.add_option( "--num-cellapps-warning", 
		dest = "numCellAppsWarningThreshold", 
		default = 1, type = "int",
		metavar="NUM_CELLAPPS",
		help = "Warn if the number of running CellApps is less "
			"than this" )

	sopt.add_option( "--num-serviceapps-warning", 
		dest = "numServiceAppsWarningThreshold", 
		default = 1, type = "int",
		metavar="NUM_SERVICEAPPS",
		help = "Warn if the number of running ServiceApps is less "
			"than this" )

	sopt.add_option( "--num-dbapps-warning", 
		dest = "numDBAppsWarningThreshold", 
		default = 1, type = "int",
		metavar="NUM_DBAPPS",
		help = "Warn if the number of running DBApps is less "
			"than this" )

	return sopt


def sysExitWithNagiosStatus( f ):
	def wrapped( *args ):
		try:
			status = f( *args )
		except SystemExit:
			return
		except user_module.UserError:
			raise
		except Exception, e:
			status = NAGIOS_UNKNOWN
			print "%s occurred: %s|" % (e.__class__.__name__, e)
			traceback.print_exc()

		sys.exit( status.statusCode )

	return wrapped

@sysExitWithNagiosStatus
def run( args, env ):
	user = env.getUser( refreshEnv = True, fetchVersion = True )
	status = NAGIOS_OK

	sopt = _buildOptionsParser()
	options, parsedArgs = sopt.parse_args( args )

	procs = user.getServerProcs()

	if not procs:
		print "BIGWORLD CRITICAL: No server running"
		return NAGIOS_CRITICAL

	missingProcs = set( Process.types.required( user.version ).keys() )
	for proc in procs:
		if proc.name in missingProcs:
			missingProcs.remove( proc.name )

	if missingProcs:
		print "BIGWORLD CRITICAL: Missing processes: %s" % ", ".join( missingProcs )
		return NAGIOS_CRITICAL

	baseAppLoadAvg = user.getLoad( "baseapp" ).avg
	cellAppLoadAvg = user.getLoad( "cellapp" ).avg
	numBaseApps = len( user.getProcs( "baseapp" ) )
	numCellApps = len( user.getProcs( "cellapp" ) )
	numServiceApps = len( user.getProcs( "serviceapp" ) )
	numDBApps = len( user.getProcs( "dbapp" ) )

	appNumChecks = [
		(numBaseApps, options.numBaseAppsCriticalThreshold,
			options.numBaseAppsWarningThreshold),
		(numCellApps, options.numCellAppsCriticalThreshold,
			options.numCellAppsWarningThreshold),
		(numServiceApps, options.numServiceAppsCriticalThreshold,
			options.numServiceAppsWarningThreshold),
		(numDBApps, options.numDBAppsCriticalThreshold,
			options.numDBAppsWarningThreshold),
		# These are inverted below so we can compare loadAvg > threshold
		# instead.
		(-baseAppLoadAvg, -options.loadCriticalThreshold,
			-options.loadWarningThreshold),
		(-cellAppLoadAvg, -options.loadCriticalThreshold,
			-options.loadWarningThreshold)
	]

	for stat, criticalThreshold, warnThreshold in appNumChecks:
		if stat < criticalThreshold:
			status = NAGIOS_CRITICAL
			break
		if stat < warnThreshold:
			status = NAGIOS_WARNING
			break

	data = dict( status = status,
		numProcesses = len( procs ), 
		numProxies = user.getNumProxies(),
		numCellEntities = user.getNumEntities(),
		numBaseApps = numBaseApps,
		numCellApps = numCellApps,
		numServiceApps = numServiceApps,
		numDBApps = numDBApps,
		cellAppLoadAvg = cellAppLoadAvg,
		baseAppLoadAvg = baseAppLoadAvg )

	serviceOutput = ["num_processes=%(numProcesses)d",
			"baseapps=%(numBaseApps)d",
			"cellapps=%(numCellApps)d",
			"serviceapps=%(numServiceApps)d",
			"dbapps=%(numDBApps)d",
			"cellapp_load_avg=%(cellAppLoadAvg).03f",
			"baseapp_load_avg=%(baseAppLoadAvg).03f"]

	perfData = ["num_proxies=%(numProxies)d",
		"num_cell_entities=%(numCellEntities)d",
		"num_cellapps=%(numCellApps)d",
		"num_baseapps=%(numBaseApps)d",
		"num_serviceapps=%(numServiceApps)d",
		"num_dbapps=%(numDBApps)d"]

	longServiceOutput = serviceOutput + perfData

	print ("BIGWORLD %(status)s: " + "; ".join( serviceOutput )) % data + \
		"|" + perfData[0] % data + " "
	print "\n".join( map( lambda x: x % data, longServiceOutput ) ) + "|"
	print "\n".join( map( lambda x: x % data, perfData[1:] ) )

	return status

if __name__ == "__main__":
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# nagios.py
