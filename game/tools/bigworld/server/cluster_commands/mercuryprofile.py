#!/usr/bin/env python

"""
Mercury profile module.

This module contains logic for retrieving and displaying per-message-type
statistics from processes.

See the printProfile() module function below.
"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import messages
from pycommon import watcher_data_message

class _FieldType( object ):
	"""
	This class represents a field type object, which defines one of the
	columns in the resulting table output.
	"""
	def __init__( self, name, short, format ):
		self.name = name
		self.short = short
		self.format = format

FIELD_TYPES = {}
FIELD_ORDER = []


def _declareFieldType( name, short, format="%s" ):
	"""
	Declare a field type.

	@param name 	the name of the watcher value
	@param short 	a short name for the field, this is displayed as part
					of the header when printing out stats
	@param format 	the format string which is used to print the value
	"""
	FIELD_ORDER.append( name )
	FIELD_TYPES[name] = _FieldType( name, short, format )

# Mercury message type statistic field declarations

_declareFieldType( "id", "id", "%d" )
_declareFieldType( "name", "name", "%s" )
_declareFieldType( "bytesReceived", "br", "%d" )
_declareFieldType( "messagesReceived", "mr", "%d" )
_declareFieldType( "maxBytesReceived", "max br", "%d" )
_declareFieldType( "avgMessageLength", "aml", "%.01f" )
_declareFieldType( "avgBytesPerSecond", "abps", "%.01f")
_declareFieldType( "avgMessagesPerSecond", "amps", "%.01f" )

def _collectNubStatistics( proc, nubPath, skipUnused=True ):
	"""
	Collect nub statistics for a path, return them as a list (indexed by
	interface ID) of dictionaries containing mappings of statistic names
	to values.

	@param proc 		the process
	@param nubPath 		the watcher path to the nub watcher directory
	@param skipUnused 	skip the unused interfaces (those that have not
						received any messages)
	"""

	outStats = []
	maxFieldLens = dict( [(fieldName, len( fieldType.short ))
		for fieldName, fieldType in FIELD_TYPES.items()] )


	for ifaceID in xrange( 256 ):
		# batch up the interface statistics watcher directory retrieval
		paths = [nubPath + "/interfaceByID/" + str( ifaceID ) + "/" + fieldName
			for fieldName in FIELD_ORDER]

		results = watcher_data_message.WatcherDataMessage.batchQuery( paths, [proc], 1.0 )

		# need to process the results into a more useful form, dictionary of
		# the field names to their values
		results = dict( [(path[path.rindex( "/" ) + 1:] , valueInfo[0][1])
			for path, valueInfo in results[proc].items()] )

		# skip unused interfaces if we can
		if skipUnused and not results["messagesReceived"]:
			continue

		ifaceStats = dict( id=ifaceID )
		for fieldName, fieldType in FIELD_TYPES.items():
			fieldValue = results[fieldName]
			# id can be mangled, e.g. for script message ifaces
			if fieldName == "id":
				fieldValue = ifaceID
			ifaceStats[fieldName] = fieldValue

			formatted = fieldType.format % fieldValue
			maxFieldLens[fieldName] = max( len( formatted ),
				maxFieldLens.get( fieldName, len( fieldType.short ) ) )

		outStats.append( (ifaceID, ifaceStats) )

	return outStats, maxFieldLens

def _sortNubStatistics( fieldName, stats, descending=True ):
	"""
	Sort the statistics list in-place according to the given field name.

	@param fieldName 	the field name of the sort key
	@param stats 		the list of stats to sort
	@param descending 	if True, do descending sort otherwise ascending
	"""

	def cmpFn( v1, v2 ):
		ifaceID1, ifaceStats1 = v1
		ifaceID2, ifaceStats2 = v2
		out = cmp( ifaceStats1[fieldName], ifaceStats2[fieldName] )
		if descending:
			return -out
		else:
			return out

	stats.sort( cmpFn )


def getProcStats( processes, skipUnused = False ):
	"""
	Retrieve a list of process statistics for the given processes.

	@param processes 	a list of processes to profile
	@return 			a list of tuples of the form:
							(process, nubLabel, (ifaceStats, maxFieldLens))
						where
							process is a Process object,
							nubLabel is the string label of the nub on that
							process (either "Internal Nub" or "External Nub",
							ifaceStats is an ordered list of interface
							statistics, indexed by interface ID, each is a
							dictionary with keys corresponding to entries in
							FIELD_TYPES,
							maxFieldLens is a dictionary with an entry for each
							type in FIELD_TYPES, and the maximum string length
							of the statistic as formatted by the type in
							FIELD_TYPES.
	"""
	procStats = []
	for proc in processes:
		procStats.append( (proc, "Internal Nub",
			_collectNubStatistics( proc, "nub", skipUnused )) )

		# if it's external, there are two nubs to collect from
		if proc.name in ["baseapp", "loginapp"]:
			procStats.append( (proc, "External Nub",
				_collectNubStatistics( proc, "nubExternal", skipUnused )) )
	return procStats


def printProfile( processes, sortBy, descending, skipUnused ):
	"""
	Mercury profile console output function.

	@param processes 	a list of processes to profile
	@param sortBy 		sort key to use, must be one of FIELD_ORDER
	@param descending 	use descending sort
	@param skipUnused 	skip unused interfaces (those that have not received
						any messages)
	"""
	if sortBy not in FIELD_ORDER:
		raise ValueError, "sort must be one of %s" % ", ".join( FIELD_ORDER )

	procStats = getProcStats( processes, skipUnused )

	for proc, label, (stats, maxFieldLens) in procStats:
		print "%(name)s - %(nubName)s\n" % \
			dict( name=proc.label(), nubName=label )

		_sortNubStatistics( sortBy, stats, descending )

		# print the header
		print " ".join( ["%*s" %
				(maxFieldLens[fieldName], FIELD_TYPES[fieldName].short)
			for fieldName in FIELD_ORDER] )
		for ifaceID, ifaceStats in stats:
			print " ".join( [("%*" + FIELD_TYPES[fieldName].format[1:]) %
					(maxFieldLens[fieldName], ifaceStats[fieldName] )
				for fieldName in FIELD_ORDER] )
		print

	return True


def getUsageStr():
	return """mercuryprofile [-r|--reverse] [-s|--sort <sortkey>]
               [--no-skip-unused] <processes>"""


def getHelpStr():
	return """   Profile network messages from server processes.

   Fetch the statistics for received network messages by message type for the
   given processes. By default, it skips any messages that have not been used
   to send on, this can be overridden by the '--no-skip-unused' option.

   Output may be sorted according to the following:
     'id'                    Message ID.
     'name'                  Message name.
     'messagesReceived'      Total count of received messages for this
                             message type.
     'bytesReceived'         Bytes received for this message type.
     'maxBytesReceived'      Maximum bytes ever received for a single message
                             for this message type.
     'avgBytesPerSecond'     Average bytes per second for this message type.
     'avgMessageLength'      Average message length for this message type.
     'avgMessagesPerSecond'  Average number of messages received for this
                             message type.

   Command Options:
    --no-skip-unused     Include results for network messages that haven't been
                         used during the sampling period.

    -r,--reverse         Reverse the sort order of results.

    -s,--sort <sortkey>  Sort output according to a particular column of output.
                         Supported values for <sortkey> are as described above.
                         The default is 'id'."""


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-u", "--no-skip-unused", dest = "skipUnused",
					default = True, action = "store_false" )
	sopt.add_option( "-s", "--sort",     default = "id" )
	sopt.add_option( "-r", "--reverse",  default = False,
					action = "store_true" )

	return sopt


def run( args, env ):
	from pycommon import command_util

	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	processFilters = parsedArgs[:1]
	processes = env.getSelectedProcesses( processFilters )

	if not processes:
		return env.usageError(
			"You must specify at least one process to profile", getUsageStr )

	return printProfile( processes,
					options.sort, options.reverse, options.skipUnused )


if __name__ == "__main__":
	import sys
	from pycommon.command_util import runCommand
	from pycommon.util import setUpBasicCleanLogging

	setUpBasicCleanLogging()
	sys.exit( runCommand( run ) )

# mercuryprofile.py
