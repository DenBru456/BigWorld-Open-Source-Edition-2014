from xml.dom import minidom
import prefclasses
import utilities
import constants
import random
import re
import sys
import logging

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

	import pycommon.util
	pycommon.util.setUpBasicCleanLogging()

log = logging.getLogger( __name__ )

class StatLoggerPrefError( Exception ):
	"stat_logger preference configuration error. "
	pass

# ================================================================
# Dump a collection preference tree to an XML node
# ================================================================

def dumpStatPrefListToNode( statList, listName, doc ):
	statListNode = doc.createElement( listName )
	for statPref in statList:
		node = dumpStatPrefToXMLNode( statPref, doc )
		utilities.xmlAddComment( doc, statListNode,
			"Statistic \"%s\"" % (statPref.name) )
		statListNode.appendChild( node )
	return statListNode


def dumpStatPrefToXMLNode( statPref, doc ):
	statNode = doc.createElement( "statistic" )
	utilities.xmlAddValue( doc, statNode, "name", statPref.name )
	utilities.xmlAddValue( doc, statNode, "valueAt", statPref.valueAt )
	utilities.xmlAddValue( doc, statNode, "maxAt", statPref.maxAt )
	utilities.xmlAddValue( doc, statNode, "type", statPref.type )
	utilities.xmlAddValue( doc, statNode, "consolidate",
		consolidateToString( statPref.consolidate ) )
	utilities.xmlAddValue( doc, statNode, "fetchFromSingleInstance", 
		statPref.fetchFromSingleInstance )

	utilities.xmlAddComment( doc, statNode, "Default display preferences" )
	displayNode = doc.createElement( "display" )
	statNode.appendChild( displayNode )
	utilities.xmlAddValue( doc, displayNode, "colour",
		"#%06X" % statPref.colour )
	if statPref.show:
		utilities.xmlAddValue( doc, displayNode, "show", "true" )
	else:
		utilities.xmlAddValue( doc, displayNode, "show", "false" )

	utilities.xmlAddValue( doc, displayNode, "description",
		statPref.description )
	return statNode

def dumpProcPrefToXMLNode( procPref, doc ):
	procNode = doc.createElement( "process" )
	utilities.xmlAddValue( doc, procNode, "name", procPref.name )
	utilities.xmlAddValue( doc, procNode, "matchtext", procPref.matchtext )
	statListNode = dumpStatPrefListToNode( procPref.iterStatPrefs(),
		"statisticList", doc )
	utilities.xmlAddComment( doc, procNode,
		"List of statistics under the \"%s\" process class" % (procPref.name) )
	procNode.appendChild( statListNode )
	return procNode

def dumpWindowPrefsToNode( windowPrefs, options, doc ):
	windowPrefsNode = doc.createElement( "aggregation" )
	for windowPref in windowPrefs:

		if windowPref.samplePeriodTicks == 1:
			nthText = ""
		else:
			nthText = "%d%s " % (windowPref.samplePeriodTicks,
				utilities.getOrdinalSuffix( windowPref.samplePeriodTicks ))
		utilities.xmlAddComment( doc, windowPrefsNode,
			"Keep every %ssample (%d seconds) in the most recent %d samples" % \
			(nthText,
			windowPref.samplePeriodTicks * options.sampleTickInterval,
			windowPref.samples * windowPref.samplePeriodTicks) )
		windowPrefNode = doc.createElement( "window" )
		utilities.xmlAddValue( doc, windowPrefNode,
			"samples", windowPref.samples )
		utilities.xmlAddValue( doc, windowPrefNode,
			"samplePeriodTicks", windowPref.samplePeriodTicks )
		windowPrefsNode.appendChild( windowPrefNode );
	return windowPrefsNode


def dumpPrefTreeCollectToXMLNode( prefTree, options, doc ):
	collectNode = doc.createElement( "collect" )
	utilities.xmlAddComment( doc, collectNode,
		"Aggregation window settings" )
	windowPrefsNode = dumpWindowPrefsToNode(
		prefTree.windowPrefs, options, doc )
	collectNode.appendChild( windowPrefsNode )

	allProcStatListNode = dumpStatPrefListToNode(
		prefTree.iterAllProcStatPrefs(),
		"allProcessStatisticList", doc )

	procListNode = doc.createElement( "processList" )
	utilities.xmlAddComment( doc, collectNode, "List of processes" )
	collectNode.appendChild( procListNode )

	for procPref in prefTree.iterProcPrefs():
		node = dumpProcPrefToXMLNode( procPref, doc )
		utilities.xmlAddComment( doc, procListNode,
			"Process \"%s\"" % (procPref.name) )
		procListNode.appendChild( node )

	utilities.xmlAddComment( doc, procListNode,
		"List of statistics applicable to all processes" )
	collectNode.appendChild( allProcStatListNode )

	machineStatListNode = dumpStatPrefListToNode(
		prefTree.iterMachineStatPrefs(), "machineStatisticList", doc )
	utilities.xmlAddComment( doc, collectNode,
		"List of machine specific statistics" )
	collectNode.appendChild( machineStatListNode )


	return collectNode


# ================================================================
# Read a collection preference tree from an XML node
# ================================================================

def _randomColour():
	return random.randint( 0, 0xFFFFFF )

def getConsolidateFromString( consolidateString ):
	try:
		consolidate = eval( "constants.CONSOLIDATE_" + consolidateString )
	except NameError:
		consolidate = constants.CONSOLIDATE_AVG
	return consolidate

def consolidateToString( consolidate ):
	if not constants.CONSOLIDATE_NAMES.has_key( consolidate ):
		consolidate = constants.CONSOLIDATE_AVG
	return constants.CONSOLIDATE_NAMES[consolidate]

def generateStatPrefFromXMLNode( statNode ):
	nodeDict = utilities.xmlNodeToDict( statNode )
	name = nodeDict["name"]
	valueAt = nodeDict["valueAt"]
	maxAt = nodeDict["maxAt"]
	consolidate = getConsolidateFromString( nodeDict["consolidate"] )
	
	fetchFromSingleInstance = False
	if nodeDict.has_key( "fetchFromSingleInstance" ):
		fetchFromSingleInstance = nodeDict["fetchFromSingleInstance"]

	# get the default display preferences
	displayNode = utilities.xmlFindChildElement( statNode, "display" )

	# default default display preferences if no display element defined
	colour = _randomColour()
	show = True
	description = "Description not available."
	if displayNode:
		displayNodeDict = utilities.xmlNodeToDict( displayNode )

		# get the colour default display preference
		if displayNodeDict.has_key( "colour" ):
			colourString = displayNodeDict["colour"]
			if colourString.startswith( "#" ):
				colour = int( colourString[1:], 16 )
			else:
				colour = int( colourString, 16 )
		# get the show default display preference
		if displayNodeDict.has_key( "show" ):
			showString = displayNodeDict["show"]
			matches = re.match( "\s*(true|false)\s*", showString.lower() )
			if matches.groups()[0] == "true":
				show = True
			elif matches.groups()[0] == "false":
				show = False

		# get the description default display preference
		if "description" in displayNodeDict:
			description = displayNodeDict["description"]

			# remove tab chars and replace '\n's with spaces as these
			# are removed when serialised by pyamf.
			description = ' '.join( d.strip() for d in description.split( '\n' ) )
			description = description.replace( "\t", " " )

	statPref = prefclasses.StatPref( name, valueAt, maxAt,
		consolidate, colour=colour, show=show, description=description,
		fetchFromSingleInstance=fetchFromSingleInstance )

	return statPref

def generateProcPrefFromXMLNode( procNode ):
	nodeDict = utilities.xmlNodeToDict( procNode )
	name = nodeDict["name"]
	matchtext = nodeDict["matchtext"]

	procPref = prefclasses.ProcessPref( name, matchtext )
	for statPref in utilities.xmlMapList( procNode, "statisticList",
			"statistic", generateStatPrefFromXMLNode ):
		procPref.addStatPref( statPref )
	return procPref

def generateAggWinPrefFromXMLNode( procNode ):
	nodeDict = utilities.xmlNodeToDict( procNode )
	samples = nodeDict['samples']
	samplePeriodTicks = nodeDict['samplePeriodTicks']
	return prefclasses.WindowPref( int(samples), int(samplePeriodTicks) )

def generatePrefTreeFromXMLNode( node ):
	prefTree = prefclasses.PrefTree()
	collectNode = utilities.xmlFindChildElement( node, "collect" )


	# check aggregation window validity
	lastSamplePeriodTicks = 1
	lastRangeTicks = 0
	for i, windowPref in enumerate( utilities.xmlMapList( collectNode,
			"aggregation", "window", generateAggWinPrefFromXMLNode ) ):

		# check fatal errors
		if i == 0 and windowPref.samplePeriodTicks != 1:
			raise StatLoggerPrefError, "First aggregation window must " \
				"have a samplePeriodTicks value of 1"

		if i > 1 and windowPref.samplePeriodTicks < lastSamplePeriodTicks:
			raise StatLoggerPrefError, "Aggregation windows must be in order "\
				"of increasing samplePeriodTicks (window %d: %d is less than "\
				"previous window's samplePeriodTicks of %d)" % \
					(i + 1, windowPref.samplePeriodTicks, lastSamplePeriodTicks)

		if i > 1 and windowPref.samplePeriodTicks * windowPref.samples < \
				lastRangeTicks:
			raise StatLoggerPrefError, "Aggregation windows must be in order "\
				"of increasing effective log range (window %d: %d is less "\
				"than the previous window's range of %d" %\
					(i + 1, windowPref.samples * windowPref.samplePeriodTicks,
						lastRangeTicks)

		# check non-fatal errors
		if i > 1 and windowPref.samplePeriodTicks % lastSamplePeriodTicks:
			print "WARNING: window %d has %d ticks per sample period which is "\
				"not a multiple of the previous window's ticks per sample "\
				"period of %d" % (i + 1, windowPref.samplePeriodTicks,
					lastSamplePeriodTicks)

		prefTree.addWindowPref( windowPref )

		lastSamplePeriodTicks = windowPref.samplePeriodTicks
		lastRangeTicks = windowPref.samples * windowPref.samplePeriodTicks



	for procPref in utilities.xmlMapList( collectNode, "processList",
			"process", generateProcPrefFromXMLNode ):
		prefTree.addProcPref( procPref )

	for statPref in utilities.xmlMapList( collectNode,
			"machineStatisticList", "statistic", generateStatPrefFromXMLNode ):
		prefTree.addMachineStatPref( statPref )

	for statPref in  utilities.xmlMapList( collectNode,
			"allProcessStatisticList", "statistic",
			generateStatPrefFromXMLNode ):
		prefTree.addAllProcStatPref( statPref )

	return prefTree

# ================================================================
# Dump general options to an XML node
# ================================================================

def dumpOptionsToXMLNode( options, doc ):
	optionNode = doc.createElement( "options" )
	utilities.xmlAddValue( doc, optionNode, "sampleTickInterval",
		options.sampleTickInterval )
	if options.uid:
		utilities.xmlAddValue( doc, optionNode, "uid", options.uid )
			
	dataStoreNode = doc.createElement( "dataStore" )
	if options.dbStoreConfig:
		dbNode = doc.createElement( "database" ) 
		utilities.xmlAddValue( doc, dbNode, "enable",
						options.dbStoreConfig.enabled )
		utilities.xmlAddValue( doc, dbNode, "host", options.dbStoreConfig.host )
		utilities.xmlAddValue( doc, dbNode, "user", options.dbStoreConfig.user )
		utilities.xmlAddValue( doc, dbNode, "password", 
						options.dbStoreConfig.password )
		utilities.xmlAddValue( doc, dbNode, "port", options.dbStoreConfig.port )
		utilities.xmlAddValue( doc, dbNode, "prefix", 
						options.dbStoreConfig.prefix )
		
		dataStoreNode.appendChild( dbNode )
	
	if options.carbonStoreConfig:
		carbonNode = doc.createElement( "carbon" ) 
		utilities.xmlAddValue( doc, carbonNode, "enable",
						options.carbonStoreConfig.enabled )
		utilities.xmlAddValue( doc, carbonNode, "host",
						options.carbonStoreConfig.host )
		utilities.xmlAddValue( doc, carbonNode, "port",
						options.carbonStoreConfig.port )
		utilities.xmlAddValue( doc, carbonNode, "prefix",
						options.carbonStoreConfig.prefix )
		utilities.xmlAddValue( doc, carbonNode, "decoupleUserStatistics",
						options.carbonStoreConfig.decoupleUserStatistics )

		dataStoreNode.appendChild( carbonNode )
	
	optionNode.appendChild( dataStoreNode )

	return optionNode

def generateOptionsFromXMLNode( node ):
	options = prefclasses.Options()
	
	optionNode = utilities.xmlFindChildElement( node, "options" )
	if not optionNode:
		log.error( "No options node is found in preference file. Exiting." )
		sys.exit( 1 )
		
	nodeDict = utilities.xmlNodeToDict( optionNode )
	options.sampleTickInterval = float ( nodeDict[ "sampleTickInterval" ] )
	if nodeDict.has_key( "uid" ):
		options.uid = int(nodeDict[ "uid" ])
	else:
		options.uid = None
					
	dataStoreNode = utilities.xmlFindChildElement( optionNode, "dataStore" )
	if not dataStoreNode:
		log.error( "No dataStore node is found in preference file. Exiting." )
		sys.exit( 1 )
	
	# parse out configuration of ENABLED data stores
	dbNode = utilities.xmlFindChildElement( dataStoreNode, "database" )
	options.dbStoreConfig = parseDbNode( dbNode )
	
	carbonNode = utilities.xmlFindChildElement( dataStoreNode, "carbon" )
	options.carbonStoreConfig = parseCarbonNode( carbonNode )

	return options
# generateOptionsFromXMLNode


def parseDbNode( dbNode ):
	if not dbNode:
		return None

	nodeDict = utilities.xmlNodeToDict( dbNode )

	enabled = False
	if ( nodeDict[ "enable" ].upper() == "TRUE" 
			or nodeDict[ "enable" ].upper() == "YES"
			or nodeDict[ "enable" ] == "1" 
		):
		enabled = True

	host = nodeDict[ "host" ]
	port = int( nodeDict[ "port" ] )
	user = nodeDict[ "user" ]
	password = nodeDict[ "password" ]
	prefix = nodeDict[ "prefix" ]

	return  prefclasses.DatabaseStoreConfig( 
								enabled = enabled, 
								host = host,
								port = port,
								user = user,
								password = password,								
								prefix = prefix )
# parseDbNode		


def parseCarbonNode( carbonNode ): 
	if not carbonNode:
		return None

	nodeDict = utilities.xmlNodeToDict( carbonNode )

	enabled = False
	if ( nodeDict[ "enable" ].upper() == "TRUE"
			or nodeDict[ "enable" ].upper() == "YES"
			or nodeDict[ "enable" ] == "1"
		):
		enabled = True

	host = nodeDict[ "host" ]
	port = int( nodeDict[ "port" ] )
	prefix = nodeDict[ "prefix" ]
	
	decoupleUserStatistics = False
	if ( nodeDict[ "decoupleUserStatistics" ].upper() == "TRUE"
			or nodeDict[ "decoupleUserStatistics" ].upper() == "YES"
			or nodeDict[ "decoupleUserStatistics" ] == "1"
		):
		decoupleUserStatistics = True

	return prefclasses.CarbonStoreConfig( 
							enabled = enabled,
							host = host,
							port = port,
							prefix = prefix,
							decoupleUserStatistics = decoupleUserStatistics )
# parseCarbonNode			
				
				
# ================================================================
# File reading stuff
# ================================================================
def loadPrefsFromXMLFile( filename ):
	doc = minidom.parse( filename )
	topNode = doc.documentElement
	prefTree = generatePrefTreeFromXMLNode( topNode )
	options = generateOptionsFromXMLNode( topNode )
	doc.unlink()

	return options, prefTree

def loadOptionsFromXMLFile( filename ):
	doc = minidom.parse( filename )
	topNode = doc.documentElement
	options = generateOptionsFromXMLNode( topNode )
	doc.unlink()
	return options

def writePrefsToXMLFile( filename, options, prefTree ):
	impl = minidom.getDOMImplementation()
	doc = impl.createDocument( "", "preferences", None )
	top = doc.documentElement

	utilities.xmlAddComment( doc, top, "General options" )
	optionsNode = dumpOptionsToXMLNode( options, doc )
	top.appendChild( optionsNode )

	utilities.xmlAddComment( doc, top, "Collection settings" )
	prefTreeCollectNode = dumpPrefTreeCollectToXMLNode( prefTree, options, doc )
	top.appendChild( prefTreeCollectNode )

	file = open( filename, "w")
	doc.writexml( file, "", "\t", "\n" )
	file.close()
	doc.unlink()

# ================================================================
# Testing function, do not use
# ================================================================

def main():
	import sys
	from xml.dom import minidom

	if len( sys.argv ) != 3:
		print "Preference XML read and write test"
		print "Usage: %s <input> <output>" % sys.argv[0]
		return
	inputFilename = sys.argv[1]
	outputFilename = sys.argv[2]

	# Load from the XML file
	options, prefTree = loadPrefsFromXMLFile( inputFilename )

	# Print it out
	prefTree.display()

if __name__=="__main__":
    main()

# prefxml.py
