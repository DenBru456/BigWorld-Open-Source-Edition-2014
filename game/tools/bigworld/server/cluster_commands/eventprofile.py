#!/usr/bin/env python
"""   Profile communication to Clients from server processes.

   Fetch the count and sizes of events (script calls, property value changes)
   that are sent to a client over a period of time.

   Reports are generated for three different event counter types:

    publicClientEvents
      This includes a count and sizes of individual public methods and property
      changes that will be pushed to all/other clients within an entity's AoI.

    privateClientEvents
      This only includes private methods calls and property changes that are
      pushed to an entity's own client.  Includes bandwidth to clients in
      bytes per second.

    totalPublicClientEvents
      Total count and sizes of all public methods and property changes that
      were actually pushed to all/other clients in each entity's AoI.
      Includes bandwidth to clients in bytes per second.

   Command Options:
    -f,--force           Force a profile to run even if another event profile
                         is running.
    -s,--sort <sortkey>  Sort output according to a particular column of output.
                         Supported values for <sortkey> are:
                          'avgsize'
                          'bandwidth'
                          'count'
                          'totalsize'
                         The default is 'bandwidth'.

    -t,--time <secs>     Total time (in seconds) in which sampling will occur
                         to generate profile output. Defaults to 10 seconds."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

import time
import logging

log = logging.getLogger( __name__ )


class EventStat( object ):
	def __init__( self, name, count, size, period ):
		self.name = name
		self.count = count
		self.size = size
		self.period = period

	def avgSizePerCount( self ):
		return float( self.size ) / float( self.count )

	def avgBytesPerSecond( self ):
		return float( self.size ) / float( self.period )

	def __str__( self ):
		format = "%-30s %10d %10d %10.03f %10.03f"
		args = (self.name, self.count, self.size, self.avgSizePerCount(), self.avgBytesPerSecond())

		out = ""
		if len( self.name ) > 30:
			args = ("",) + args[1:]
			out = self.name + "\n"

		out += format % args
		return out





EVENTPROFILE_SORT_TYPES = {
	"bandwidth":
		lambda y, x: cmp( x.avgBytesPerSecond(), y.avgBytesPerSecond() ),
	"count":
		lambda y, x: cmp( x.count, y.count ),
	"totalsize":
		lambda y, x: cmp( x.size, y.size ),
	"avgsize":
		lambda y, x: cmp( x.avgSizePerCount(), y.avgSizePerCount() )
}


def eventprofile( procs, secs, sortType="bandwidth", force=False ):
	# turn event tracking profiling off then on to reset counters

	if sortType not in EVENTPROFILE_SORT_TYPES:
		log.error( "Not a valid sort type: %s", sortType )
		return False

	# Check what profiles are supported on these app types
	watcherData = procs[ 0 ].getWatcherData( "eventProfiles" )
	if not watcherData.isDir():
		log.error( "Unable to query supported event profiles" )
		return False

	supportedProfileTypes = []
	for entry in watcherData:
		supportedProfileTypes.append( entry.name )

	if not supportedProfileTypes:
		log.error( "Unable to determine supported event profiles" )
		return False

	# check that profiles aren't running, or disable them if we are forced to
	for p in procs:
		for eventType in supportedProfileTypes:
			if not force:
				enabledData = p.getWatcherData( "eventProfiles/" + eventType +
					"/enabled" )

				if enabledData.value:
					log.error( "Event profiles are already running "
							"(check %s on %s is disabled, or use --force)",
						eventType, p.label() )
					return False
			else:
				p.setWatcherValue( "eventProfiles/" + eventType + "/enabled",
					False )

	# activate the profiles
	for p in procs:
		for eventType in supportedProfileTypes:
			p.setWatcherValue( "eventProfiles/" + eventType + "/enabled",
				True )

	print "Waiting %.1f secs for sample data ..." % secs
	time.sleep( secs )

	# turn them off
	for p in procs:
		for eventType in supportedProfileTypes:
			p.setWatcherValue( "eventProfiles/" + eventType + "/enabled", False )
	# get the counts and sizes
	for p in procs:
		print "**** %s ****" % p.label()
		for eventType in supportedProfileTypes:
			eventCounts = {}
			eventSizes = {}

			eventStats = []
			countsData = p.getWatcherData(
				"eventProfiles/" + eventType + "/counts" )
			for countData in countsData.getChildren():
				eventCounts[ countData.name ] = int( countData.value )

			sizesData = p.getWatcherData(
				"eventProfiles/" + eventType + "/sizes" )
			for sizeData in sizesData.getChildren():
				eventSizes[ sizeData.name ] = int( sizeData.value )

			for name in eventCounts:
				count = eventCounts[ name ]
				size = eventSizes[ name ]
				eventStats.append( EventStat( name, count, size, secs ) )

			eventStats.sort( cmp=EVENTPROFILE_SORT_TYPES[ sortType ] )

			print "\nEvent Type: %s\n" % eventType


			if eventStats:
				print "%-30s %10s %10s %10s %10s\n" % \
					("Name", "#", "Size", "AvgSize", "Bandwidth")

				for stat in eventStats:
					print str( stat )

			else:
				print "No events"

			print
	
	return True


def getUsageStr():
	return "eventprofile [-s|--sort <sortkey>] [-t|--time <secs>] <processes>"


def getHelpStr():
	return __doc__


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-f", "--force", default = False, action = "store_true" )
	sopt.add_option( "-s", "--sort",  default = "bandwidth" )
	sopt.add_option( "-t", "--time",  default = 10.0, type = "float" )

	return sopt


def run( args, env ):
	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	status = True

	processFilters = parsedArgs

	if not processFilters:
		processFilters = ["cellapps"]

	processes = env.getSelectedProcesses( processFilters )

	if not processes:
		env.error( "No processes found, or no server running" )
		status = False
	else:
		status = eventprofile( processes, options.time,
					options.sort, options.force )

	return status


if __name__ == "__main__":
	import sys
	from pycommon.command_util import runCommand
	from pycommon.util import setUpBasicCleanLogging

	setUpBasicCleanLogging()
	sys.exit( runCommand( run ) )

# eventprofile.py
