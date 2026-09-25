#!/usr/bin/env python

import unittest
import optparse
import re

import bwunittest
import writetodb_ts
import secondary_db_ts
import secondary_db_misc_ts
import restore_entity_ts
import backgroundtask_ts

import bwsetup
bwsetup.addPath( "../../" )

from pycommon import util as pyutil

USAGE = "usage: %prog [options]"

OPTIONS = [	( ["-p", "--pattern"], {"type": "string",
			  	"help": "restrict to test cases matching regex pattern"} ),
			( ["-g", "--group"], {"type": "string",
			  	"help": "restrict to machines in this group"} ),
			( ["-l", "--list"], {"action": "store_true",
			  	"help": "list available test cases"} ), 
			( ["-r", "--restore"], {"action": "store_true",
			  	"help": "restore modified and injected resource files"} ) ]

TEST_SUITES = [	writetodb_ts.WriteToDBTestSuite,
				secondary_db_ts.SecondaryDBTestSuite,
				secondary_db_misc_ts.SecondaryDBMiscTestSuite,
				restore_entity_ts.RestoreEntityTestSuite, 
				backgroundtask_ts.BackgroundTaskTestSuite ]


def main():
	print "This is currently not maintained. " \
		"It is hope to make use of this in the future."
	return

	# Parse command line
	parser = optparse.OptionParser( USAGE )
	for switches, kwargs in OPTIONS:
		parser.add_option( *switches, **kwargs )

	(options, args) = parser.parse_args()

	pattern = ".*"
	if options.pattern:
		pattern = options.pattern

	if options.group:
		bwunittest.GROUP = options.group

	if options.restore:
		bwunittest.restoreServer()
		return

	if options.list:
		for test in parseTestSuites():
			print test
		return

	run( pattern )


def run( pattern ) :
	print "==== Unit Tests ===="

	tests = parseTestSuites()
	tests = [ test for test in tests if re.match( pattern, test[0] ) ]
	tests.sort()

	numPasses = 0
   	numErrors = 0
   	numFailures = 0
	numTests = len( tests )

	for i in range( 0, numTests ):
		testCase = tests[i][1]

		result = unittest.TestResult()

		try: 
			testCase.run( result )
		finally:
			bwunittest.stopServer()

		label = "(%s/%s) %s" % ( i+1, numTests, str( testCase ) )

		if result.errors:
			print "ERROR   : %s\n%s" % ( label, result.errors[0][1] )
			numErrors += 1
		elif result.failures:
			print "FAILURE : %s\n%s" % ( label, result.failures[0][1] )
			numFailures += 1
		else:
			print "OK      : %s" % label
			numPasses += 1

	print "\nPasses=%d, Errors=%d, Fails=%d" %	\
			(numPasses, numErrors, numFailures )


def parseTestSuites():
	tests = []

	for suite in TEST_SUITES:
		for test in unittest.makeSuite( suite, 'test' )._tests:
			# Convert 'Function (script_file.Class)' into 'script_file.Function'
			name = str( test )
			name = name.split( "(" )[1].split( "." )[0] + "." + name.split()[0]
			tests.append( ( name,test ) )

	return tests


if __name__ == '__main__':
	pyutil.setUpBasicCleanLogging()

	main()
