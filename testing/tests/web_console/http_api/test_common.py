import sys

from primitives import WebConsoleAPI

from pycommon import command_util
from pycommon import watcher_constants as Constants

from bwtest import TestSuite, TestCase
from bwtest import config
from bwtest import log

from helpers.cluster import ClusterController

# This file contains things common to all test suites
# that test WebConsoleAPI functionality.

# constants

SIGINT = 2
cc = None

def StartWebConsoleAPI():
	return WebConsoleAPI.WebConsoleAPI()


class TestCommon( object ):

	@staticmethod
	def _getCC():
		global cc
		if cc:
			return cc
		cc = ClusterController( [ "simple_space/res" ], 
									user = config.WCAPI_USER )
		return cc

	@staticmethod
	def getUserObj():
		env = command_util.CommandEnvironment( config.WCAPI_USER )
		return env.getUser()

	@staticmethod
	def getMachine():
		return config.CLUSTER_MACHINES[0]

	@staticmethod
	def stopServer():
		TestCommon._getCC().stop() 
		return True
	
	@staticmethod
	def clean():
		global cc
		TestCommon._getCC().clean()
		cc = None

	@staticmethod
	def startServer():
		TestCommon._getCC().start()
		ret = TestCommon._getCC().waitForServerSettle()
		return ret

	@staticmethod
	def restartServer():	
		TestCommon._getCC().stop() 
		TestCommon._getCC().start()
		ret = TestCommon._getCC().waitForServerSettle()
		return ret
	
	@staticmethod
	def startProc( procType, procOrd ):
		return TestCommon._getCC().startProc( procType, procOrd )
		
	
	@staticmethod
	def getProcs( filterByProcName = None, filterByProcPid = None ):
		return TestCommon._getCC().getProcs( filterByProcName, filterByProcPid )
	
	@staticmethod
	def getPids( procType, machine = None ):
		return TestCommon._getCC().getPids( procType, machine )
	
	@staticmethod
	def getWatcher( pid, path ):
		return TestCommon._getCC().getWatcherByPid( pid, path )


