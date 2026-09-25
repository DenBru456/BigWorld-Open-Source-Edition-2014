import prefclasses
import constants

# Type of logDb is db.DbConnection (might move that
# class in here, but it makes more sense to leave
# it in db.py for readability
def generatePrefTreeFromLogDb( cursor ):
	prefTree = prefclasses.PrefTree( )

	c = cursor

	# add process statistics prefs
	c.execute( "SELECT name, matchtext, id, tableName FROM %s" \
			% (constants.tblPrefProcesses) )
	for procRow in c.fetchall():
		(name, matchtext, dbId, tableName) = procRow
		procPref = prefclasses.ProcessPref( name, matchtext, int(dbId) )
		procPref.tableName = tableName
		c.execute( """
SELECT id, name, valueAt, maxAt, type,
	consolidate, columnName
FROM %s WHERE processPref = %d"""  % (constants.tblPrefStatistics, dbId) )
		for statRow in c.fetchall():
			statPref = generateStatPrefFromDbRow( statRow )
			procPref.addStatPref( statPref )

		prefTree.addProcPref( procPref )

	# add machine prefs
	c.execute("""
SELECT id, name, valueAt, maxAt, type,
	consolidate, columnName
FROM %s WHERE processPref = %d""" % (constants.tblPrefStatistics,
		constants.ID_MACHINES) )
	for machineStatRow in c.fetchall():
		machineStatPref = generateStatPrefFromDbRow( machineStatRow )
		prefTree.addMachineStatPref( machineStatPref )

	# add <All> statistic prefs
	c.execute(\
"""SELECT id, name, valueAt, maxAt, type,
	consolidate, columnName
FROM %s WHERE processPref = %d""" % (constants.tblPrefStatistics,
		constants.ID_ALLPROCESSES) )

	for allProcStatRow in c.fetchall():
		allProcStatPref = generateStatPrefFromDbRow( allProcStatRow )
		prefTree.addAllProcStatPref( allProcStatPref )

	# add window prefs
	c.execute( \
			"SELECT id, samples, samplePeriodTicks "\
			"FROM %s ORDER BY id" % (constants.tblStdWindows)
	)
	for windowRow in c.fetchall():
		(id, samples, samplePeriodTicks) = windowRow
		windowPref = prefclasses.WindowPref(
			samples, samplePeriodTicks, dbId = id )
		prefTree.addWindowPref( windowPref )


	# prefTree.display()
	return prefTree


def generateStatPrefFromDbRow( statRow ):
	dbId, name, valueAt, maxAt, type, consolidate, \
		columnName = statRow
	statisticPref = prefclasses.StatPref( name, valueAt, maxAt, consolidate,
		int( dbId ), type )
	statisticPref.columnName = columnName
	return statisticPref
