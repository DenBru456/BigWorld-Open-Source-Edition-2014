#!/usr/bin/env python
"""   Fetches all Python and C++ profiles from the specified server processes
   and display them in a tabular format.

   Command Options:
    -s,--sort <sortkey>  Sort output according to a particular column of output.
                         Supported values for <col> are:
                          'SORT_BY_NAME'
                          'SORT_BY_TIME'
                          'SORT_BY_NUMCALLS'
                         The default is 'SORT_BY_TIME'.

    -e,--exclusive      Calculate exclusive times

    --json-dump <n>      Dump the following <n> ticks to a JSON file which can
                         which can be opened within Google Chromes profiler
                         (chrome://tracing). This will be stored with the
                         server binaries."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

import os
import sys
import time

# Enable importing from pycommon
sys.path.append( os.path.dirname( __file__ ) + "/../.." )

import logging
log = logging.getLogger( __name__ )


def setupTerminal():
	global oldterm, oldflags
	import termios, fcntl
	fd = sys.stdin.fileno()

	oldterm = termios.tcgetattr( fd )
	newattr = termios.tcgetattr( fd )
	newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr( fd, termios.TCSANOW, newattr )

	oldflags = fcntl.fcntl( fd, fcntl.F_GETFL )
	fcntl.fcntl( fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK )

	# Preserve screen
	print "\033[?1049h\033[H"

def cleanupTerminal():
	import termios, fcntl
	# restore Screen
	print "\033[?1049l"

	fd = sys.stdin.fileno()
	termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

def getWindowSize():
	import fcntl, termios, struct
	return struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ, '1234'))

def tickDisplay( proc, sort, jsonDumpCount, jsonDumpIndex ):
	os.system( "clear" )
	stats = proc.getWatcherData( "profiler/statistics" )
	if not stats:
		log.error( "Couldn't get profile data on %s", proc.label() )
		return False

	infolines = []

	if jsonDumpCount > 0 and jsonDumpIndex != None:
		dumpPercentage = ( jsonDumpIndex * 100 ) / jsonDumpCount
		infolines.append( "\n\nJSON dump percentage: %d%%\n\n" % \
				dumpPercentage )

	infolines.append( "\nPress Ctrl+C to stop profiling" )
	infolines.append( "\nPress P to step through profile modes" )
	infolines.append( "\nPress I to toggle inclusive/exclusive "
								"timing information" )
	infolines.append( "\nPress , and . to switch to categories" )
	if sort == "HIERARCHICAL":
		infolines.append( "\nPress [ and ] to move to entries" )
		infolines.append( "\nPress Enter to toggle the current entry" )

	totalLinesToOutput = getWindowSize()[0] - len(infolines) - 1
	couldPrintAll = True

	for line in stats:
		if totalLinesToOutput == 0:
			couldPrintAll = False
			break
		sys.stdout.write( line.value )
		totalLinesToOutput = totalLinesToOutput - 1

	if not couldPrintAll:
		sys.stdout.write("\nCould not display all output")

	for line in infolines:
		sys.stdout.write( line )

	return True

def handleKeyInput( proc, sortIdx, sortTypes, exclusive ):
	try:
		c = sys.stdin.read(1)
		if c == 'P' or c == 'p':
			sortIdx = (sortIdx + 1) % len(sortTypes)
			sort = sortTypes[sortIdx]
			proc.setWatcherValue( "profiler/sortMode", sort )
		elif c == 'I' or c == 'i':
			exclusive = not exclusive
			proc.setWatcherValue( "profiler/exclusive",
				repr( exclusive ) )
		elif c == '[':
			proc.setWatcherValue( "profiler/controls/prevEntry", "True" )
		elif c == ']':
			proc.setWatcherValue( "profiler/controls/nextEntry", "True" )
		elif c == '\n':
			proc.setWatcherValue( "profiler/controls/toggleEntry", "True" )
		elif c == '<' or c == ',':
			proc.setWatcherValue( "profiler/controls/prevCategory", "True" )
		elif c == '>' or c == '.':
			proc.setWatcherValue( "profiler/controls/nextCategory", "True" )

		# Get all other keys, makes it feel more responsive
		sys.stdin.read(1024)
	except IOError: pass

	return (sortIdx, exclusive)
	
def profile( proc, sort, exclusive, jsondump, updateRate ):
	"""
	Implements the 'profile' command.
	"""

	# How many profiles we want to generate
	sortTypes = ["SORT_BY_NAME", "SORT_BY_TIME", "SORT_BY_NUMCALLS", "HIERARCHICAL"]

	if sort not in sortTypes:
		log.warning( "Invalid sort type, reverting to SORT_BY_TIME" )
		sort = "SORT_BY_TIME"

	sortIdx = sortTypes.index( sort )

	# Make sure this process supports profiling
	if not proc.getWatcherData( "profiler/enable" ):
		log.error( "%s doesn't support profiling", proc.label() )
		return False

	# Set exclusive
	if not exclusive:
		exclusive = False

	# Enable profiling
	if not proc.setWatcherValues( [
				( "profiler/enabled", "true" ),
				( "profiler/sortMode", sort ),
				( "profiler/exclusive", repr( exclusive ) )
			] ):
		log.error( "Couldn't enable profiling on %s", proc.label() )
		return False

	if jsondump > 0:
		# Set dump frame count
		if not proc.setWatcherValues( [
					( "profiler/dumpFrameCount", jsondump ),
					( "profiler/dumpProfile", "true" )
				] ):
			log.error( "Couldn't set JSON dump frame count on %s", proc.label() )
			return False

	log.info( "Starting profiling" )

	setupTerminal()

	hasFinished = False
	dumpFilePath = None
	jsonDumpIndex = None 
	try:
		while not hasFinished:
			if jsondump > 0:
				# get the JSON dump file path
				dumpFileData = proc.getWatcherData( "profiler/dumpFilePath" )

				if dumpFileData:
					dumpFilePath = dumpFileData.value

				# get the JSON dump index (num of ticks that have been dumped)
				dumpIndexData = proc.getWatcherData( "profiler/dumpFrameIndex" )
				newJsonDumpIndex = dumpIndexData.value

				# The index will become 0 when the dump is finished
				if not ( newJsonDumpIndex == 0 and jsonDumpIndex > 0 ):
					jsonDumpIndex = newJsonDumpIndex

				# Check profiling on all procs
				wd = proc.getWatcherData( "profiler/dumpProfile" )
				if not wd:
					log.error( "Couldn't check if profiling finished on %s", proc.label() )
					hasFinished = False
					break

				hasFinished = wd.value == False

			if not tickDisplay( proc, sort, jsondump, jsonDumpIndex ):
				break

			sortIdx, exclusive = handleKeyInput( proc,
					sortIdx, sortTypes, exclusive )

			sort = sortTypes[sortIdx]

			time.sleep( updateRate )

	except KeyboardInterrupt:
		log.info( "Aborted. Disabling profiling on all processes." )
	except:
		import traceback
		exception = traceback.format_exc()
		# Restore screen
		cleanupTerminal()
		log.error( exception )
		return 1
		

	# Restore screen
	cleanupTerminal()

	if jsondump > 0:
		if hasFinished:
			log.info( "Successfully dumped JSON to file: %s" % dumpFilePath )
		else:
			log.error( "Failed to dump JSON file" )

	log.info( "Finished profiling" )

	# Disable profiling
	proc.setWatcherValue( "profiler/enabled", "false" )

	return not hasFinished


def getUsageStr():
	return \
"""   profile  <process> [-s|--sort <sortkey>]
                        [--json-dump <n>] [-e|--exclusive]"""


def getHelpStr():
	return __doc__


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-s", "--sort", default = "SORT_BY_TIME" )
	sopt.add_option( "-e", "--exclusive", action = "store_true" )
	sopt.add_option( "-u", "--update-rate", type = "float", default = 0.25 )
	sopt.add_option( "--json-dump", type = "int", default = 0 )

	return sopt


def run( args, env ):
	from pycommon import command_util

	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	processFilters = parsedArgs[:1]
	processes = env.getSelectedProcesses( processFilters )

	if not processes: 
		return env.usageError(
			"You must specify one process to profile", getUsageStr )
	elif len( processes ) != 1:
		return env.usageError(
			"You must only specify one process to profile", getUsageStr )

	return profile( processes[0], options.sort, options.exclusive,
						options.json_dump, options.update_rate )


if __name__ == "__main__":
	from pycommon.command_util import runCommand
	from pycommon.util import setUpBasicCleanLogging

	setUpBasicCleanLogging()
	sys.exit( runCommand( run ) )

# profile.py
