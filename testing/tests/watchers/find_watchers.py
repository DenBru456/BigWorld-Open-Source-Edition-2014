import re

from bwtest import TestCase
from test_common import TestCommon

import baseapp
import baseappmgr
import cellapp
import cellappmgr
import dbapp
import loginapp
import serviceapp

patternTest = \
"""
for pattern in %s.watcherPatterns:
	match = re.search( pattern, watcher )
	if match:
		break
else:
	untestedWatchers.append( (process, watcher) )

"""
class TestFindWatchers( TestCommon, TestCase ):
	
	
	tags = []
	name = "Find watchers"
	description = "Find list of watchers available and test that they have\
				   an existing test case"

	processes = ["baseapp", 
				"baseappmgr", 
				"cellapp", 
				"cellappmgr", 
				"dbapp", 
				"loginapp", 
				"serviceapp"]


	def getWatcherNames( self, process, path = "", depth = 5 ):
		if depth == 0:
			return []

		if path.startswith("entities/") or \
			path.startswith("nubExternal/interfaceByID/") or \
			path.startswith("nubExternal/interfaceByName/") or \
			path.startswith("nub/interfaceByID/") or \
			path.startswith("nub/interfaceByName/"):
			return []

		watcherData = self._cc.getWatcherData(path, process, None)
		if not watcherData.isDir():
			return [watcherData.path]
		else:
			ret = []
			for w in watcherData.getChildren():
				ret.extend( self.getWatcherNames( process, w.path, depth-1 ) )
			return ret
		
	def runTest( self ):
		watchers = {}
		for process in self.processes:
			watchers[ process ] = self.getWatcherNames( process )
		
		untestedWatchers = []
		for process, watcherList in watchers.items():
			for watcher in watcherList:
				try:
					exec( patternTest % process )
				except:
					untestedWatchers.append( (process, watcher) )
		self.assertTrue( len( untestedWatchers ) == 0, "Found untested watchers:\n %s" 
						 % "\n".join( "(%s, %s)" % tup for tup in untestedWatchers ) )
