"""
Module for validating a logging database's structure.
"""

import constants

def validateLogDb( cursor ):
	"""
	Validate a database table.

	Cursor should be a database cursor
		e.g. MySQLdb.connection.cursor.

	Assume the cursor is already connected to the database we want to validate.

	This function basically compares the table structure of the database
	against the data stored in the pref tables (in the same database).
	"""

	errors = []
	errors.extend( findOrphanStats( cursor ) )
	errors.extend( findDuplicates( cursor ) )
	errors.extend( checkStructure( cursor ) )
	return errors


def findOrphanStats( cursor ):
	"""
	Search for statistics which don't belong to a process (and thus wouldn't be
	used in logging).
	"""

	errors = []

	# Find orphan stats
	cursor.execute("""
SELECT statPref.name, statPref.processPref
FROM %s statPref LEFT JOIN %s procPref
ON statPref.processPref = procPref.id
WHERE statPref.processPref NOT IN (%s, %s)
	AND procPref.id IS NULL""" %
			(constants.tblPrefStatistics,
			constants.tblPrefProcesses,
			constants.ID_MACHINES,
			constants.ID_ALLPROCESSES) )

	for r in cursor.fetchall():
		errors.append(
			"Orphan statistic \"%s\" references nonexisting process with "\
			"database ID of %d" % (r[0], r[1]) )

	return errors


def findDuplicates( cursor ):
	""" Find duplicate table and column names. """

	errors = []
	# Find duplicate table usage
	duplicateTableNames = {}
	cursor.execute("SELECT tableName " \
					"FROM %s GROUP BY tableName " \
					"HAVING ( COUNT(tableName) > 1 )" \
					% constants.tblPrefProcesses )
	for r in cursor.fetchall():
		cursor.execute("SELECT name FROM %s WHERE tableName = %%s" % \
				(constants.tblPrefProcesses), r[0])
		# Add name to dictionary
		duplicateTableNames[ r[0] ] = None
		for r2 in cursor.fetchall():
			errors.append( "Duplicate table name \"%s\" "\
					"used by process \"%s\"" % \
				(r[0], r2[0]) )


	# Find duplicate column usage
	duplicateColumnNames = {}
	cursor.execute("SELECT columnName " \
					"FROM %s GROUP BY columnName " \
					"HAVING ( COUNT(columnName) > 1 )" \
					% constants.tblPrefStatistics )
	for r in cursor.fetchall():
		cursor.execute("SELECT name FROM %s WHERE columnName = %%s" % \
				(constants.tblPrefStatistics), r[0])
		# Add name to dictionary
		duplicateColumnNames[ r[0] ] = None
		for r2 in cursor.fetchall():
			errors.append( "Duplicate column name \"%s\" "\
					"used by statistic \"%s\"" % \
				(r[0], r2[0]) )

	# Find duplicate statistic names
	cursor.execute("SELECT name " \
					"FROM %s GROUP BY name " \
					"HAVING ( COUNT(name) > 1 )" \
					% constants.tblPrefStatistics )
	for r in cursor.fetchall():
		errors.append( "Duplicate statistic name \"%s\"" % r[0] )

	# Find duplicate process names
	cursor.execute("SELECT name " \
					"FROM %s GROUP BY name " \
					"HAVING ( COUNT(name) > 1 )" \
					% constants.tblPrefProcesses )
	for r in cursor.fetchall():
		errors.append( "Duplicate process name \"%s\"" % r[0] )

	return errors


def checkStructure( cursor ):
	""" Check the database structure for existence of tables and columns. """
	errors = []
	prefTree = MiniPrefTree()


	# Grab window prefs
	cursor.execute( "SELECT id, samples, samplePeriodTicks FROM %s" % \
		constants.tblStdWindows )
	for (dbId, samples, samplePeriodTicks) in cursor.fetchall():
		prefTree.addWindowPref( dbId, samples, samplePeriodTicks )

	# Grab process prefs
	cursor.execute( "SELECT name, id, tableName FROM %s" % \
		constants.tblPrefProcesses )
	for r in cursor.fetchall():
		prefTree.addPref( r[0], r[1], r[2] )

	# Grab statistic prefs
	for procPref in prefTree.procPrefs.itervalues():
		cursor.execute( "SELECT name, id, columnName FROM %s "\
				"WHERE processPref = %s"\
			% (constants.tblPrefStatistics, procPref.dbId) )
		for r in cursor.fetchall():
			procPref.addStat( r[0], r[1], r[2] )

	# Grab machine stats
	cursor.execute( "SELECT name, id, columnName FROM %s "\
			"WHERE processPref = %s" \
		% (constants.tblPrefStatistics, constants.ID_MACHINES) )
	for r in cursor.fetchall():
		prefTree.addMachineStat( r[0], r[1], r[2] )

	# Grab all process stats
	cursor.execute( "SELECT name, id, columnName FROM %s "\
			"WHERE processPref = %s" \
		% (constants.tblPrefStatistics, constants.ID_ALLPROCESSES) )
	for r in cursor.fetchall():
		prefTree.addAllProcStat( r[0], r[1], r[2] )

	# Grab list of tables
	tableList = {}
	cursor.execute( "SHOW TABLES" )
	for r in cursor.fetchall():
		tableList[ r[0] ] = None

	# Check generated table names and structures
	for procPref in prefTree.procPrefs.itervalues():
		for windowPref in prefTree.windowPrefs:
			tableName = "%s_lvl_%03d" % (procPref.tableName, windowPref.dbId)
			if tableList.has_key( tableName ):

				# First, grab list of columns in this table
				columnList = {}
				cursor.execute( "DESCRIBE %s" % (tableName,) )

				for r in cursor.fetchall():
					# Result tuple: ( Field, Type, Null, Key, Default, Extra )
					columnList[r[0]] = r[1]

				# Note: Won't be verifying types for now, may not ever have to
				for statPref in procPref.statPrefs.values() + \
						prefTree.allProcStatPrefs.values():
					if not columnList.has_key( statPref.columnName ):
						errors.append("Expected column \"%s\" in "
								"table \"%s\" not found" % \
							(statPref.columnName, tableName,)
						)
			else:
				errors.append("Expected table \"%s\" not found" % \
					(tableName,) )

	# Special case: machine values
	for windowPref in prefTree.windowPrefs:
		tableName = "%s_lvl_%03d" % (constants.tblStatMachines, windowPref.dbId)
		if tableList.has_key( tableName ):
			columnList = {}
			cursor.execute( "DESCRIBE %s" % \
				(tableName,) )

			for r in cursor.fetchall():
				# Result tuple: ( Field, Type, Null, Key, Default, Extra )
				columnList[r[0]] = r[1]

			for stat in prefTree.machineStatPrefs.itervalues():
				if not columnList.has_key( stat.columnName ):
					errors.append("Expected column \"%s\" in "\
							"table \"%s\" not found" % \
						(stat.columnName, tableName,)
					)
		else:
			errors.append("Expected table \"%s\" not found" % \
				(tableName,) )

	return errors


def addStatToDict( dict, name, dbId, columnName ):
	dict[ name ] = MiniStatPref( name, dbId, columnName )

def addProcToDict( dict, name, dbId, tableName ):
	dict[ name ] = MiniProcPref( name, dbId, tableName )

# =============================================================================
# Section: Helper class for validateLogDb
# =============================================================================

class MiniPrefTree:
	"""
	A mini version of the real preference tree used for logging.
	"""
	def __init__( self ):
		self.procPrefs = {}
		self.allProcStatPrefs = {}
		self.machineStatPrefs = {}
		self.windowPrefs = []

	def addPref( self, name, dbId, tableName ):
		addProcToDict( self.procPrefs, name, dbId, tableName )

	def addAllProcStat( self, name, dbId, columnName ):
		addStatToDict( self.allProcStatPrefs, name, dbId, columnName )

	def addMachineStat( self, name, dbId, columnName ):
		addStatToDict( self.machineStatPrefs, name, dbId, columnName )

	def addWindowPref( self, dbId, samples, samplePeriodTicks ):
		self.windowPrefs.append(
			MiniWindowPref( dbId, samples, samplePeriodTicks ) )

class MiniProcPref:
	def __init__( self, name, dbId, tableName ):
		self.statPrefs = {}
		self.name = name
		self.dbId = dbId
		self.tableName = tableName

	def addStat( self, name, dbId, tableName ):
		addStatToDict( self.statPrefs, name, dbId, tableName )

class MiniStatPref:
	def __init__( self, name, dbId, columnName ):
		self.name = name
		self.dbId = dbId
		self.columnName = columnName

class MiniWindowPref:
	def __init__( self, dbId, samples, samplePeriodTicks ):
		self.dbId = dbId
		self.samples = samples
		self.samplePeriodTicks = samplePeriodTicks
