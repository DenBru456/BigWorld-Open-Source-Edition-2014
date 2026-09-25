#! /usr/bin/env python

import os
import sys
import unittest

from optparse import OptionParser

from helpers import command

from bwtest import loader
from bwtest import config

from bwtest import log


def run():

	runCount = 0
	while True:
		options, requiredTags, excludedTags, testCases, topdir, verbosity = setup()
		topsuite = loader.discover( topdir, requiredTags, excludedTags, testCases )

		if options.xml:
			import xmlrunner
			testRunner = xmlrunner.XMLTestRunner( output = options.xml )
		else:
			testRunner = unittest.TextTestRunner( verbosity = verbosity )

		result = testRunner.run( topsuite )
		runCount += 1
		if not options.repeat or \
		   (options.repeat > 0 and runCount == options.repeat) \
		   or not result.wasSuccessful():
			print "Ran the suite %s times" % runCount
			sys.exit( not result.wasSuccessful() )


def setup():
	config.DEBUGMODE = False

	usageStr = """usage: %prog [options] PATH|NAME

  PATH		OS path to test suite
  NAME		dot-separated module name

typical examples:
  runtests tests/db		run all auto test cases in db test suite
  runtests -tMANUAL tests	run manual test cases
  runtests -v tests -cMyCase	run test case with MyCase class name
  runtests tests.db.python_api	run python_api test suite by name
"""

	tagsStr = """
tags supported:
	%s""" 
	tagsStr = tagsStr % \
  		', '.join( config.SUPPORTED_TAGS )
	usageStr = usageStr + tagsStr 


	parser = OptionParser( usage = usageStr )

	parser.add_option( "-t", "--tag", action="append", dest="requiredTags",
		help="Run only tests that supply given tag. May be specified "
				"multiple times", metavar="TAG" )

	parser.add_option("-T", "--exclude_tag", action="append",  dest="excludedTags",
		help="Run tests that do not supply given tag. May be specified "
				"multiple times", metavar="EXCLUDED_TAG")

	parser.add_option( "-c", "--case", action="append", dest="testCases",
		help="Test case class name to run. Several cases may be specified. "
				"This option disables -t and -T", 
		metavar="CASE_CLASS_NAME" )

	parser.add_option( "-l", "--level", action="store", dest="logLevel",
		choices = [ "debug", "info", "warning", "progress", "error", "critical" ],
		default = "warning",
		help="Log level", metavar="LOG_LEVEL" )

	parser.add_option( "-q", "--quiet", action="store_const", dest="logLevel",
		const = "critical",
		help="Quiet output: set log level to 'info'" )

	parser.add_option( "-v", "--verbose", action="store_const", dest="logLevel",
		const = "info",
		help="Verbose output: set log level to 'info'" )

	parser.add_option( "-d", "--debug", action="store_const", dest="logLevel",
		const = "debug",
		help="Debug output: set log level to 'debug'" )

	parser.add_option( "-x", "--xml", dest="xml",
		help="Produce xml output to specified directory", metavar="XML")	

	parser.add_option( "-y", "--dry", action="store_true", dest="dryRun",
		default = False,
		help="Dry test running: test cases will be iterated through but "
			"not executed. This option also enables -v" )

	parser.add_option( "-a", "--archive-server-logs", action="store",
		dest="serverLogDir", default=None, metavar="SERVER_LOG_DIR",
		help="Archive all test case related server logs to given log directory" )


	def repeat_callback(option, opt, value, parser):
		try:
			if parser.rargs and not parser.rargs[0].startswith('-'):
				parser.values.repeat = int( parser.rargs[0] )
				parser.rargs.pop(0)
			else:
				parser.values.repeat = -1
		except:
			parser.values.repeat = -1

	parser.add_option( "-r", "--repeat", 
		action="callback", callback = repeat_callback, dest = "repeat",
		help="Repeat the suite until a failure occurs." 
			"Provide an integer value to restrict"
			" the total number of runs. Provide nothing "
			"to run forever." 
			"Use this to help "
			"track down sporadically failing tests.")
	parser.add_option( "-p", "--platform", action="store", dest="platform",
		help="Defines the platform that the tests will be running on,"
			" default is centos5" )

	parser.add_option( "-o", "--oldbin", action="store_true", dest="oldbin",
		default = False,
		help="Specifies that the build tested uses the old"
			"binary folder structure and thus should look for binaries there")

	options, args = parser.parse_args()

	topdir = '.'
	if args:
		topdir = args[0]

	requiredTags = []
	if options.requiredTags:
		requiredTags = options.requiredTags


	excludedTags = []
	if options.excludedTags:
		excludedTags.extend( options.excludedTags )

	for tag in requiredTags:
		if tag in excludedTags:
			excludedTags.remove( tag )

	testCases = []
	if options.testCases:
		testCases = options.testCases 

	if options.platform:
		config.SERVER_BINARY_FOLDER = "bin/server/%s/server" % options.platform
		config.TOOLS_BINARY_FOLDER = "bin/server/%s/tools" % options.platform
		if "debug" in options.platform:
			config.BW_CONFIG = "debug"

	if options.oldbin:
		config.SERVER_BINARY_FOLDER = "bin/Hybrid64"
		config.TOOLS_BINARY_FOLDER = "tools/server/bin/Hybrid64"


	# support for framework debugging
	logLevel = log.choicesMap[ options.logLevel ]
	log.setLevel( logLevel )

	config.DRY_RUN = options.dryRun

	if config.DRY_RUN:
		if logLevel > log.WARNING:
			logLevel = log.WARNING
			log.setLevel( logLevel )

	config.SERVER_LOG_DIR = None
	if options.serverLogDir is not None:
		config.SERVER_LOG_DIR = os.path.abspath( options.serverLogDir )
		command.mkdir( config.SERVER_LOG_DIR )

	verbosity = 0

	if logLevel > log.ERROR: 
		verbosity = 1


	# Test levels in the logging system
	# These are just commented out because you cannot use
	# levels in logging system to disable tests for levels
	# in logging system!
#	log.debug( "testing log.debug() %s", "test" )
#	log.info( "testing log.info() %s", "test" )
#	log.warning( "testing log.warning() %s", "test" )
#	log.progress( "testing log.progress() %s", "test" )
#	log.error( "testing log.error() %s", "test" )
#	log.critical( "testing log.critical() %s", "test" )

	if testCases:
		names = ', '.join( testCases )
		log.progress( "Test Cases: %s", names )
	else:
		if requiredTags:
			names = ', '.join( requiredTags )
			log.progress( "Tags required: %s", names )
		if excludedTags:
			names = ', '.join( excludedTags )
			log.progress( "Tags excluded: %s", names )

	if config.DRY_RUN:
		log.progress( "Running tests in the Dry Run mode!" )


	return (options, requiredTags, excludedTags, testCases, topdir, verbosity)



# Just run this thing
try:
	run()
except KeyboardInterrupt:
	log.error( "Exiting from user interrupt" )

