import itertools
import constants

# Classes to represent preferences

# -----------------------------------------------------------------------------
# Section: Base class
# -----------------------------------------------------------------------------

class Pref:
	def __init__( self, name, dbId ):
		self.dbId = dbId
		self.name = name
		self.parent = None

	def setParent( self, parent ):
		self.parent = parent

# -----------------------------------------------------------------------------
# Section: PrefTree
# -----------------------------------------------------------------------------

class PrefTree:
	def __init__( self ):
		self.procPrefs = {}
		self.procOrder = []

		self.machineStatPrefs = {}
		self.machineStatOrder = []
		self.machineStatPrefsById = {}

		self.allProcStatPrefs = {}
		self.allProcStatOrder = []
		self.allProcStatPrefsById = {}

		# window prefs are ordered
		self.windowPrefs = []

	def addProcPref( self, procPref ):
		self.procPrefs[ procPref.name ] = procPref
		procPref.setParent( self )
		self.procOrder.append( procPref.name )

	def addWindowPref( self, windowPref ):
		self.windowPrefs.append( windowPref )
		windowPref.setParent( self )

	def addMachineStatPref( self, statPref ):
		self.machineStatPrefs[ statPref.name ] = statPref
		self.machineStatOrder.append( statPref.name )
		if statPref.dbId != None:
			self.machineStatPrefsById[ statPref.dbId ] = statPref
		statPref.setParent( self )

	def procPrefByName( self, processPrefName ):
		return self.procPrefs[processPrefName]

	def addAllProcStatPref( self, statPref ):
		self.allProcStatPrefs[ statPref.name ] = statPref
		self.allProcStatPrefsById[ statPref.dbId ] = statPref
		self.allProcStatOrder.append( statPref.name )
		statPref.setParent( self )

	def allProcStatPrefById( self, dbId ):
		return self.allProcStatPrefsById[ dbId ]

	def allProcStatPrefByName( self, name ):
		return self.allProcStatPrefs[ name ]

	def iterAllProcStatPrefs( self ):
		return iter( self.allProcStatPrefs[statName]
			for statName in self.allProcStatOrder )

	def iterProcPrefs( self ):
		return iter( self.procPrefs[procName] for procName in self.procOrder )

	def iterMachineStatPrefs( self ):
		return iter( self.machineStatPrefs[statName]
			for statName in self.machineStatOrder )

	def machineStatPrefByName( self, name ):
		return self.machineStatPrefs[name]

	def machineStatPrefById( self, dbId ):
		return self.machineStatPrefsById[ dbId ]

	def display( self ):
		print str( self )

	def __str__( self ):
		out = ''
		out += "=========================================\n"
		out += "    Printing preference tree\n"
		out += "=========================================\n"
		for p in self.iterProcPrefs():
			out += "  Process \"%s\"\n" % (p.name)
			for s in p.iterStatPrefs():
				out += "    Statistic \"%s\"\n\n" % (s.name)
		out += "Special process class: <Machines>\n"
		for s in self.iterMachineStatPrefs():
			out += "   Statistic \"%s\"\n" % (s.name)
		out += "Special process class: <All Processes>\n"
		for s in self.iterAllProcStatPrefs():
			out += "   Statistic \"%s\"\n" % (s.name)
		out += "=========================================\n"
		out += "        End preference tree\n"
		out += "=========================================\n\n"
		return out

# -----------------------------------------------------------------------------
# Section: Pref implementations
# -----------------------------------------------------------------------------
class ProcessPref( Pref ):
	def __init__( self, name, matchtext, dbId = None ):
		Pref.__init__( self, name, dbId )
		self.matchtext = matchtext
		self.statPrefs = {}
		self.idsToPrefs = {}
		self.statOrder = []
		self.tableName = None

	def statPrefById( self, dbId ):
		if self.idsToPrefs.has_key( dbId ):
			return self.idsToPrefs[ dbId ]
		return self.parent.allProcStatPrefById( dbId )

	def statPrefByName( self, name ):
		if not self.statPrefs.has_key( name ):
			return self.parent.allProcStatPrefByName( name )
		return self.statPrefs[name]

	def addStatPref( self, statPref ):
		self.statPrefs[ statPref.name ] = statPref
		self.idsToPrefs[ statPref.dbId ] = statPref
		self.statOrder.append( statPref.name )
		statPref.setParent( self )

	def iterStatPrefs( self ):
		return iter( self.statPrefs[statName] for statName in self.statOrder )

	def iterAllStatPrefs( self ):
		if self.parent:
			return itertools.chain(
				self.parent.iterAllProcStatPrefs(),
				self.iterStatPrefs()
			)
		else:
			raise Exception(
				"Process preference not attached to preference tree!" )

	def __str__( self ):

		return '{' + \
			", ".join( str( statPref )
				for statPref in self.statPrefs.values() ) + \
		'}'

class StatPref( Pref ):
	def __init__( self, name, valueAt, maxAt, consolidate,
			dbId = None, colour = None, show = None, description = None,
			type = "FLOAT", fetchFromSingleInstance = False ):
		Pref.__init__( self, name, dbId )
		self.valueAt = valueAt
		self.maxAt = maxAt
		self.type = type
		self.consolidate = consolidate
		self.colour = colour
		self.show = show
		self.description = description
		self.columnName = None
		self.fetchFromSingleInstance = fetchFromSingleInstance

	def consolidateColumn( self, tableName=None ):
		if tableName:
			tableName += "."
		else:
			tableName = ""

		if self.consolidate == constants.CONSOLIDATE_AVG:
			return "AVG( %s%s ) AS avg_%s" % \
				(tableName, self.columnName, self.columnName)
		elif self.consolidate == constants.CONSOLIDATE_MAX:
			return "MAX( %s%s ) AS max_%s" % \
				(tableName, self.columnName, self.columnName)
		elif self.consolidate == constants.CONSOLIDATE_MIN:
			return "MIN( %s%s ) AS min_%s" % \
				(tableName, self.columnName, self.columnName)
		else:
			raise ValueError, "invalid consolidate function"


class WindowPref( Pref ):
	"""
	Preference class for aggregation windows, defined by the number of tick
	samples held and the number of base ticks between the ticks in this window.
	"""
	def __init__( self, samples, samplePeriodTicks, dbId = None ):
		Pref.__init__( self, None, dbId )
		self.samples = samples
		self.samplePeriodTicks = samplePeriodTicks
		self.parent = None

	def setParent( self, parent ):
		self.parent = parent

	def __str__( self ):
		return "<wp%d>" % (self.samplePeriodTicks)

	__repr__ = __str__

# -----------------------------------------------------------------------------
# Section: General options
# -----------------------------------------------------------------------------
class DatabaseStoreConfig( object ):
	def __init__( self, enabled, host, port, user, password, prefix ):
		self.enabled = enabled		
		self.host = host
		self.port = port		
		self.user = user
		self.password = password		
		self.prefix = prefix


class CarbonStoreConfig( object ):
	def __init__( self, enabled, host, port, prefix, decoupleUserStatistics ):
		self.enabled = enabled
		self.host = host
		self.port = port
		self.prefix = prefix
		self.decoupleUserStatistics = decoupleUserStatistics
		

class Options:	
	def __init__( self ):
		self.setDefaults()

	def setDefaults( self ):
		self.sampleTickInterval = 2000
		self.dbStoreConfig = DatabaseStoreConfig( enabled = True,
									host = "localhost",
									user = "bigworld", 
									password = "bigworld",
									port = 3306,
									prefix = "bw_stat_log_data" )
											
		self.carbonStoreConfig = CarbonStoreConfig( enabled = False, 
											host = "localhost",
											port = 2004,
											prefix = "stat_logger",
											decoupleUserStatistics = False )

	def display( self ):
		print "====================================="
		print "    Global options"
		print "====================================="
		print "sampleTickInterval: %d" % self.sampleTickInterval
		print "uid: %s" % self.dbStoreConfig.uid
		print "Database Store"
		print "  enabled: %s" % self.dbStoreConfig.enabled
		print "  Host: %s" % self.dbStoreConfig.host
		print "  User: %s" % self.dbStoreConfig.user
		print "  Pass: %s" % self.dbStoreConfig.password
		print "  Port: %s" % self.dbStoreConfig.port		
		print "  Prefix: %s" % self.dbStoreConfig.prefix
		print "Carbon Store"
		print "  enabled: %s" % self.carbonStoreConfig.enabled
		print "  Host: %s" % self.carbonStoreConfig.host
		print "  Port: %s" % self.carbonStoreConfig.port
		print "  Prefix: %s" % self.carbonStoreConfig.prefix



# prefclasses.py
