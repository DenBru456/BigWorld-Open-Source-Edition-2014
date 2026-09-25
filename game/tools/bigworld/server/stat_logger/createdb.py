import re
import time
import utilities
import constants

def generateInfoDb( cursor ):
	cursor.execute( "CREATE DATABASE %s" % (constants.infoDbName))
	cursor.execute( "USE %s" % (constants.infoDbName))
	generateInfoTable( cursor )


def generateInfoTable( cursor ):
	cursor.execute(\
"""CREATE TABLE %s (
   name VARCHAR(255) PRIMARY KEY
);""" % (constants.tblInfo) )


def generateLogDb( cursor, name, prefTree, sampleTickInterval ):
	cursor.execute( "CREATE DATABASE %s" % (name) )
	cursor.execute( "USE %s" % (name) )
	generateAggregationWindowTable( cursor, prefTree )
	generateTables( cursor, prefTree )
	populateTables( cursor, prefTree, sampleTickInterval )
	updateInfoDb( cursor, name )


def generateAggregationWindowTable( cursor, prefTree ):
	"""Add the aggregation window preference table."""
	c = cursor
	c.execute("""\
CREATE TABLE %s
(
	id INT AUTO_INCREMENT PRIMARY KEY,
	samples INT NOT NULL,
	samplePeriodTicks INT NOT NULL
)""" % (constants.tblStdWindows) )

	for window in prefTree.windowPrefs:
		#print "  Adding window: %d @ %d tick-interval" % \
		#	(window.samples, window.samplePeriodTicks)
		c.execute( """
INSERT INTO %s\
( samples, samplePeriodTicks ) VALUES( %%s, %%s )
""" \
				% (constants.tblStdWindows),
			(window.samples, window.samplePeriodTicks)
		)
		window.dbId = c.connection.insert_id()


def updateInfoDb( cursor, name ):
	now = utilities.convertFloatTime( time.time() )

	# Hohoho, hacky times ahoy with the double
	# percentage sign
	cursor.execute( "USE %s" % (constants.infoDbName) )
	cursor.execute( "DELETE IGNORE FROM %s WHERE name = %%s" % \
		(constants.tblInfo), name )
	cursor.execute( "INSERT INTO %s(name) VALUES(%%s)" %\
		(constants.tblInfo), (name) )

	cursor.execute( "USE %s" % (name) )


def generateTables( cursor, prefTree ):
	# If we're creating a database from the preferences,
	# we'll need to create the database table and
	# column names, so we populate the provided prefTree with
	# database names
	#
	# Tough luck if they've already been created, although
	# generally, there's no situation in which that will
	# happen
	generateDbNames( prefTree )

	c = cursor

	c.execute("""\
CREATE TABLE %s
(
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	matchtext VARCHAR(255) NOT NULL,
	tableName VARCHAR(255) NOT NULL
)""" % (constants.tblPrefProcesses) )

	c.execute("""\
CREATE TABLE %s
(
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	valueAt VARCHAR(255) NOT NULL,
	maxAt VARCHAR(255) NOT NULL,
	columnName VARCHAR(255) NOT NULL,
	type ENUM('INT', 'FLOAT') NOT NULL,
	consolidate INT NOT NULL,
	processPref INT NOT NULL
	-- Because we use the values -1 and -2 for the processPref
	-- column to represent special process classes, we can't
	-- make it a foreign key, hence line below is commented
	-- out...not that MySQL really has foreign key checking.
	-- FOREIGN KEY (processPref) REFERENCES %s(id)
)""" % (constants.tblPrefStatistics, constants.tblPrefProcesses) )

	c.execute("""\
CREATE TABLE %s
(
	id INT AUTO_INCREMENT PRIMARY KEY,
	startTime INTEGER NOT NULL,
	endTime INTEGER DEFAULT NULL
)""" % (constants.tblStdSessionTimes) )

	c.execute("""\
CREATE TABLE %s
(
	sampleTickInterval FLOAT NOT NULL,
	version VARCHAR(255) NOT NULL
)""" % (constants.tblStdInfo) )

	c.execute("""\
CREATE TABLE %s
(
	id INT PRIMARY KEY,
	time BIGINT NOT NULL,
	INDEX(time, id)
)""" % (constants.tblStdTickTimes) )

	c.execute("""\
CREATE TABLE %s
(
	touchTime INT UNSIGNED NOT NULL
)""" % (constants.tblStdTouchTime) )

	# Maybe add more to this table later
	c.execute("""\
CREATE TABLE %s
(
	ip INT UNSIGNED PRIMARY KEY,
	hostname VARCHAR(255)
)""" % (constants.tblSeenMachines) )

	c.execute("""\
CREATE TABLE %s
(
	uid INT UNSIGNED PRIMARY KEY,
	name VARCHAR(255)
)""" % (constants.tblSeenUsers) )


	c.execute("""\
CREATE TABLE %s
(
	id INT AUTO_INCREMENT PRIMARY KEY,
	userid INT NOT NULL,
	machine INT UNSIGNED NOT NULL,
	name VARCHAR(255) NOT NULL,
	processPref INT NOT NULL,
	pid INT NOT NULL
	-- FOREIGN KEY (machine) REFERENCES %s(id),
	-- FOREIGN KEY (processPref) REFERENCES %s(id)
)""" % (constants.tblSeenProcesses, constants.tblSeenMachines, \
	constants.tblPrefProcesses) )


	# Now for entering the table structures
	# ===============================================
	standardColumns = []
	standardColumns.append( "id INT AUTO_INCREMENT PRIMARY KEY" )
	standardColumns.append( "tick INT NOT NULL" )
	standardColumns.append( "process INT NOT NULL" )
	#standardColumns.append( "FOREIGN KEY (process) REFERENCES "\
	#	"%s(id)" % (constants.tblSeenProcesses) )
	#standardColumns.append( "FOREIGN KEY (tick) REFERENCES "\
	#	"%s(id)" % (constants.tblStdTickTimes))
	standardColumns.append( "INDEX tickproc (tick, process)" )

	for proc in prefTree.iterProcPrefs():

		# Construct SQL statement
		columns = []
		for stat in proc.iterStatPrefs():
			column = "%s %s" % (stat.columnName, stat.type)
			columns.append( column )

		# Ok, now we add columns belonging to the "All processes" class
		for stat in prefTree.iterAllProcStatPrefs():
			column = "%s %s" % (stat.columnName, stat.type)
			columns.append( column )

		for windowPref in prefTree.windowPrefs:
			createTableSql = "CREATE TABLE %s_lvl_%03d ( %s )" % \
				(proc.tableName, windowPref.dbId,
				", ".join( standardColumns + columns)
			)

			c.execute( createTableSql )

	# Now do the machine table
	columns = []
	for stat in prefTree.iterMachineStatPrefs():
		column = "%s %s" % (stat.columnName, stat.type)
		columns.append( column )

	for windowPref in prefTree.windowPrefs:
		c.execute("""\
			CREATE TABLE %s_lvl_%03d
			(
				id INT AUTO_INCREMENT PRIMARY KEY,
				tick INT NOT NULL,
				machine INT UNSIGNED NOT NULL,
				-- FOREIGN KEY (machine) REFERENCES %s(id),
				-- FOREIGN KEY (tick) REFERENCES %s(id),
				INDEX tickmac (tick, machine),
				-- Columns go here
				%s
			)""" % (constants.tblStatMachines, windowPref.dbId,
			constants.tblSeenMachines,
			constants.tblStdTickTimes,
			", ".join( columns ))
		)


def populateTables( cursor, prefTree, sampleTickInterval ):

	# In the SQL statements below, note the use of doubled percentage marks
	# because substitution occurs twice

	c = cursor

	# Add the process statistics preferences
	for proc in prefTree.iterProcPrefs():
		# print " Adding process %d: %s" % (proc.id, proc.name)
		c.execute("""
INSERT INTO %s(name, matchtext, tableName)
VALUES (%%s, %%s, %%s)
""" % (constants.tblPrefProcesses),
			(proc.name, proc.matchtext, proc.tableName) )

		proc.dbId = c.connection.insert_id()

		statColumns = ['name', 'valueAt', 'maxAt', 'columnName', 'type',
			'consolidate', 'processPref']
		columnsText = ", ".join( statColumns )
		interpolatePlaceholders = ", ".join( ["%s"] * len( statColumns ) )
		for stat in proc.iterStatPrefs():
			# print "  Adding statistic %d: %s belonging to process %d" % \
			#	(stat.id, stat.name, proc.id)
			c.execute( """
INSERT INTO %s
(%s)
VALUES (%s)""" %
					(constants.tblPrefStatistics,
						columnsText, interpolatePlaceholders),
				(stat.name, stat.valueAt, stat.maxAt,
					stat.columnName, stat.type, stat.consolidate,
					proc.dbId)
			)
			stat.dbId = c.connection.insert_id()


	# Add the <All> processes' statistics preferences
	for stat in prefTree.iterAllProcStatPrefs():
		# print "  Adding statistic %d: %s belonging to special "\
		#	"process class <All> % (stat.id, stat.name)
		c.execute( """
INSERT INTO %s
(%s)
VALUES (%s)""" % \
				(constants.tblPrefStatistics,
					columnsText, interpolatePlaceholders),
			(stat.name, stat.valueAt, stat.maxAt,
				stat.columnName, stat.type, stat.consolidate,
				constants.ID_ALLPROCESSES)
		)
		stat.dbId = c.connection.insert_id()


	# Add the machine statistics preferences
	for stat in prefTree.iterMachineStatPrefs():
		# print "  Adding statistic %d: %s belonging to special "\
		#	"process class <Machine>" % (stat.id, stat.name)
		c.execute( """
INSERT INTO %s
(%s)
VALUES (%s)""" %
				(constants.tblPrefStatistics,
					columnsText, interpolatePlaceholders),
			(stat.name, stat.valueAt, stat.maxAt,
				stat.columnName, stat.type, stat.consolidate,
				constants.ID_MACHINES) )
		stat.dbId = c.connection.insert_id()
	c.execute( """
INSERT INTO %s (sampleTickInterval, version)
VALUES (%%s, %%s)""" %
			(constants.tblStdInfo),
		(sampleTickInterval, constants.dbVersion) )


# end populateTables()

def generateLogDbName( cursor, dbPrefix ):
	c = cursor

	c.execute( "USE %s" % constants.infoDbName )

	# Finds all databases of the format: "nameNUM" where name is the
	# name root of the name (i.e. "bwlogData") and NUM is any number
	# with any amount of digits. This list is taken from the info table.
	# e.g. "bwlogData32"
	c.execute( "SELECT name FROM %s WHERE name REGEXP '%s[[:digit:]]+'" \
			% (constants.tblInfo, dbPrefix) )
	results = c.fetchall()

	# Compile the regexp, we'll be using it a bit now...
	regexp = re.compile( '%s(\d+)' % (dbPrefix) )

	# Get the number to append to the end of the database
	appendNum = None
	if len(results) == 0:
		appendNum = 1
	else:
		max = -1
		for r in results:
			m = regexp.match(r[0])
			num = int(m.group(1))
			if num > max:
				max = num
		appendNum = max + 1

	# Now we have the number, now to get the list of databases actually in the
	# server
	c.execute("SHOW DATABASES LIKE '%s%%'" % (dbPrefix) )
	results = c.fetchall()

	# We're just finding and storing the list of numbers appended to
	# logDbNameRoot (e.g. the 3 in "bwlogData3").
	actualNumList = []
	if len(results) > 0:
		for r in results:
			m = regexp.match(r[0])
			if not m:
				continue
			actualNumList.append(int(m.group(1)))
		actualNumList.sort()

	# print "ActualNumList: %s" % ( actualNumList )

	# Now find a number which isn't taken
	for n in actualNumList:
		if n < appendNum:
			continue
		elif n > appendNum:
			break
		else:
			appendNum += 1

	# YES! We have our new database name!
	return "%s%d" % (dbPrefix, appendNum)


# Create table and column names (used if we're creating
# a new db log from the preferences file)
def generateDbNames( prefTree ):
	columnNamer = utilities.DbNamer()
	tableNamer  = utilities.DbNamer()
	tableNamer.setPrefix( constants.statPrefix )

	# Table "stat_machines" is the only table that might conflict with a
	# generated table name, given other process statistic tables also begin
	# with the same prefix "stat_" (e.g. "stat_cellAppManager")
	tableNamer.addUsed( constants.tblStatMachines )

	for procPref in prefTree.iterProcPrefs():
		# Generate a table name for the process
		procPref.tableName = tableNamer.makeName( procPref.name )

		for statPref in procPref.iterStatPrefs():
			# Generate a column name for the process
			# Note: Every column name is unique, even between tables.
			statPref.columnName = columnNamer.makeName( statPref.name )

	for statPref in prefTree.iterAllProcStatPrefs():
		statPref.columnName = columnNamer.makeName( statPref.name )

	for statPref in prefTree.iterMachineStatPrefs():
		statPref.columnName = columnNamer.makeName( statPref.name )

# createdb.py
