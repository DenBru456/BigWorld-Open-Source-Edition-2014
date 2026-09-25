import logging
import os
import re

from expiring_cache import ExpiringCache

log = logging.getLogger( __name__ )

# Set up (or read) all the static data first
PROC_PID_STAT_PATH = "/proc/%d/stat"
PROC_CPUINFO_PATH = "/proc/cpuinfo"
PROC_STAT_PATH = "/proc/stat"
PROC_MEMINFO_PATH = "/proc/meminfo"

processorRegex = re.compile( "^processor[^\S\n]+:[^\S\n](\S+)", re.MULTILINE )
cpuRegex = re.compile( "^cpu" )
memTotalRegex = re.compile( "^MemTotal:[^\S\n]+(\S+) kB" )


def _readFile( filePath ):
	""" Opens, reads, closes, and returns all lines of the specified file """

	fileText = None

	fp = None
	try:
		fp = open( filePath, "r" )
	except Exception, ex:
		log.error( "Couldn't open %s: %s", filePath, str( ex ) )
		return None

	try:
		fileText = fp.read()
	finally:
		fp.close()

	return fileText
# _readFile


def readNoOfCpus():
	""" Reads the number of processors from cpuinfo """
	processors = []
	try:
		fileText = _readFile( PROC_CPUINFO_PATH )
		processors = processorRegex.findall( fileText )
	except Exception, ex:
		log.error( "Unable to read no of CPUs: %s", str( ex ) )
		return None

	return len( processors )
# readNoOfCpus


def readProcessStats( pid ):
	""" Reads and returns useful /proc/<pid>/stat data """

	processJiffies = None
	childJiffies = None
	try:
		fileText = _readFile( PROC_PID_STAT_PATH % pid )
		pidStats = fileText.split()

		processJiffies = int( pidStats[13] ) + \
						 int( pidStats[14] )
		childJiffies = int( pidStats[15] ) + \
					   int( pidStats[16] )
	except Exception, ex:
		log.error( "Unable to read process CPU usage: %s", str( ex ) )

	affinity = int( pidStats[22] )
	vsize = None
	try:
		vsize = float( pidStats[22] ) / 1024
	except Exception, ex:
		log.error( "Unable to read process memory usage: %s", str( ex ) )

	return dict( processJiffies = processJiffies,
				 childJiffies = childJiffies,
				 affinity = affinity,
				 vsize = vsize )
# readProcessStats


def readSystemStats():
	cpuData = None
	fp = None
	try:
		fp = open( PROC_STAT_PATH, "r" )
	except Exception, ex:
		log.error( "Couldn't open %s: %s", PROC_STAT_PATH, str( ex ) )
		return None

	try:
		line = fp.readline()
		try:
			if not line.startswith( "cpu" ):
				raise RuntimeError( "Unable to find cpu line." )

			values = line.split()

			totalWorked = int( values[1] ) + int( values[2] ) + \
				int( values[3] )
			totalIdle = int( values[4] )
			totalWait = 0

			# attempt to get extended stats
			try:
				totalWait += int( values[5] )
				totalWait += int( values[6] )
				totalWait += int( values[7] )
			except:
				pass

			cpuData = { 'totalWorked': totalWorked,
						'totalIdle': totalIdle,
						'totalWait': totalWait }
		except Exception, ex:
			log.error( "Invalid cpu data in %s: %s. Error: %s",
				PROC_STAT_PATH, line, str( ex ) )
	finally:
		fp.close()

	return cpuData
# readSystemStats


def readMemTotal():
	""" Returns the total memory in use """

	memTotal = None
	fp = None
	try:
		fp = open( PROC_MEMINFO_PATH, "r" )
	except Exception, ex:
		log.error( "Couldn't open %s: %s", filePath, str( ex ) )
		return None
	
	try:
		for line in fp:
			result = memTotalRegex.match( line )
			try:
				memTotal = result.groups()[0]
				break
			except:
				pass

		if memTotal is None:
			log.warning( "Unable to get Total Memory usage from %s.",
				PROC_MEMINFO_PATH )
			return None
	finally:
		fp.close()

	return int( memTotal )
# readMemTotal


class StatsCacheObject( object ):
	def __init__( self, **kw ):
		# cache the process stats
		self.processStats = readProcessStats( kw.get( "pid" ) )
		self.systemStats = readSystemStats()
		self.memTotal = readMemTotal()
	# __init__
# StatsCacheObject


# Prepare the Cache for future use.
statsCache = ExpiringCache( StatsCacheObject )

# nCpus should never change, read it first
nCpus = readNoOfCpus()
