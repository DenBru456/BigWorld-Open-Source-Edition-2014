import constants

def comparePrefTreesWithError( ourTree, theirTree, showMatches = False ):
	# Compare xml file preferences to that stored in the db
	procErrors, statErrors, windowErrors = \
		comparePrefTrees( ourTree, theirTree )

	if len( procErrors ) or len( statErrors ) or len( windowErrors ):
		raise PrefMatchError( procErrors, statErrors, windowErrors )

# Compare our preference tree to another tree
# Check everything, including column and table names
# Output is three dictionaries containing id->result pairs
# If the showMatches argument is false, then only
# elements which aren't equal between the two trees will
# be placed into these dictionaries.
def comparePrefTrees( ourTree, theirTree, showMatches = False ):
	# Result values:
	# - found same category in both trees = COMPARE_MATCH
	# - found same category id in both trees, but differs? = COMPARE_MISMATCH
	# - found same category only in our tree = COMPARE_FIRST_ONLY
	# - found same category only in other tree = -COMPARE_SECOND_ONLY
	procResults = {}	# Process id   -> results
	statResults = {}	# Statistic id -> results
	windowResults = {}  # window order -> results

	# Iterate through their tree's processes and
	# compare to our. 
	for ourProcId in ourTree.procPrefs.iterkeys():
		procResults[ourProcId] = constants.COMPARE_FIRST_ONLY
	# Next iterate through other category and compare processes
	# inside to ours
	for theirProcName, theirProc in theirTree.procPrefs.iteritems():
		if not ourTree.procPrefs.has_key( theirProcName ):
			procResults[theirProcName] = constants.COMPARE_SECOND_ONLY
			continue
		ourProc = ourTree.procPrefs[theirProcName]
		if not equalProcPrefs( ourProc, theirProc ):
			procResults[theirProcName] = constants.COMPARE_MISMATCH
		else:
			if showMatches:
				procResults[theirProcName] = constants.COMPARE_MATCH
			else:
				del procResults[theirProcName]
			# Processes are equal! Now do stats in this category
			statResults.update( compareStatDict(
				ourProc.statPrefs, theirProc.statPrefs,
				showMatches ) )

	# Iterate through special machine statistics
	statResults.update( compareStatDict(
		ourTree.machineStatPrefs, theirTree.machineStatPrefs,
		showMatches ) )

	# Iterate through special all processes statistics
	statResults.update( compareStatDict(
		ourTree.allProcStatPrefs, theirTree.allProcStatPrefs,
		showMatches ) )

	# Iterate through the aggregation window preferences
	windowResults = compareWindowList(
		ourTree.windowPrefs, theirTree.windowPrefs,
		showMatches )
	return (procResults, statResults, windowResults)


# Helper function that compares the setup of the aggregation windows with those
# set in the database.
def compareWindowList( ourList, theirList, showMatches = False ):
	windowResults = {}

	for i, ourWindowPref in enumerate( ourList ):
		if i >= len( theirList ):
			break

		theirWindowPref = theirList[i]
		if ourWindowPref.samples == theirWindowPref.samples and \
				ourWindowPref.samplePeriodTicks == \
					theirWindowPref.samplePeriodTicks:
			if showMatches:
				windowResults[i] = constants.COMPARE_MATCH
		else:
			windowResults[i] = constants.COMPARE_MISMATCH

	# Checks for values only in first list. (No-op if ourList not longer).
	for i in range( len( theirList ), len( ourList ) ):
		windowResults[ i ] = constants.COMPARE_FIRST_ONLY

	# Checks for values only in first list. (No-op if theirList not longer).
	for i in range( len( ourList ), len( theirList ) ):
		windowResults[ i ] = constants.COMPARE_SECOND_ONLY

	return windowResults


# Helper function which compares statistic dictionaries.
# Compares "ourDict" to "theirDict" and then
# puts the results in the "statResults" dictionary
# This function is used below
def compareStatDict( ourDict, theirDict, showMatches = False ):
	statResults = {}
	for ourStatName in ourDict.iterkeys():
		statResults[ourStatName] = constants.COMPARE_FIRST_ONLY
	for theirStatName, theirStat in theirDict.iteritems():
		if not ourDict.has_key( theirStatName ):
			statResults[theirStatName] = constants.COMPARE_SECOND_ONLY
		else:
			ourStat = ourDict[theirStatName]
			if not equalStatPrefs( ourStat, theirStat ):
				statResults[theirStatName] = constants.COMPARE_MISMATCH
			else:
				if showMatches:
					statResults[theirStatName] = constants.COMPARE_MATCH
				else:
					del statResults[theirStatName]
	return statResults


def equalProcPrefs( ourProcPref, theirProcPref ):
	return ourProcPref.name == theirProcPref.name and \
			ourProcPref.matchtext == theirProcPref.matchtext


def equalStatPrefs( ourStatPref, theirStatPref ):
	return ourStatPref.name == theirStatPref.name and \
			ourStatPref.valueAt == theirStatPref.valueAt and \
			ourStatPref.maxAt == theirStatPref.maxAt and \
			ourStatPref.type == theirStatPref.type

def makeErrorString( result, prefName, prefType, firstSource, secondSource ):
	firstSourceL = firstSource.lower()
	firstSourceC = firstSource.capitalize()

	secondSourceL = secondSource.lower()
	secondSourceC = secondSource.capitalize()

	prefTypeL = prefType.lower()
	prefTypeC = prefType.capitalize()

	if result == constants.COMPARE_FIRST_ONLY:
		return "%s has %s \"%s\" which doesn't exist in the %s" %  \
			( firstSourceC, prefTypeL, prefName, secondSourceL )
	elif result == constants.COMPARE_SECOND_ONLY:
		return "%s has %s \"%s\" which doesn't exist in the %s" %  \
			( secondSourceC, prefTypeL, prefName, firstSourceL )
	elif result == constants.COMPARE_MISMATCH:
		return "%s \"%s\" exists in both %s and %s "\
				"but have different attributes" % \
			( prefTypeC, prefName, firstSourceL, secondSourceL )
	elif result == constants.COMPARE_MISMATCH:
		return "%s \"%s\" is matched in both %s and %s." % \
			( prefTypeC, prefName, firstSourceL, secondSourceL )

def convertErrorsToStrings( procResults, statResults, windowResults ):
	strings = []

	for name, result in procResults.iteritems():
		strings.append( makeErrorString( result, name, "Process",
			"preference file", "database" ) )

	for name, result in statResults.iteritems():
		strings.append( makeErrorString( result, name, "statistic",
			"preference file", "database" ) )

	for window, result in windowResults.iteritems():
		strings.append( makeErrorString( result, str( window ),
			"window", "preference file", "database" ) )

	return strings


class PrefMatchError( Exception ):
	def __init__( self, procErrors, statErrors, windowErrors ):
		Exception.__init__( self )
		self.procErrors = procErrors
		self.statErrors = statErrors
		self.windowErrors = windowErrors

	def printErrors( self, prefix ):
		errorStrs = convertErrorsToStrings( self.procErrors,
				self.statErrors, self.windowErrors )
		for e in errorStrs:
			print "%s%s" % (prefix, e)

# comparepref.py
