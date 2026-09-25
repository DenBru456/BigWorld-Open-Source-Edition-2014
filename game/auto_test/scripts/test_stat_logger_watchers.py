#!/usr/bin/env python

import sys

import pycommon_loader

from pycommon import command_util

from stat_logger import prefxml


def main():

	env = command_util.CommandEnvironment()
	user = env.getUser()

	if not user.serverIsRunning():
		print "Server not running"
		return False

	testStatus = True

	options, preferences = prefxml.loadPrefsFromXMLFile(
							"stat_logger_preferences.xml" )

	for procType in preferences.iterProcPrefs():
		process = user.getProc( procType.name.lower() )
		if not process:
			print "Failed to locate process:", procType.name.lower()
			testStatus = False

		else:

			for statPref in procType.statPrefs.values():
				watcherPath = statPref.valueAt.encode()
				watcherPath = watcherPath[1:] # trim the leading /
				val = process.getWatcherValue( watcherPath )
				if val == None:
					print "Failed to get watcher '%s' on '%s'" % \
						(watcherPath, procType.name)
					testStatus = False

	return testStatus



if __name__ == "__main__":
	sys.exit( int( not main() ) )
