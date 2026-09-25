
import time
from datetime import datetime

from pycommon import command_util

from helpers.cluster import ClusterController
from primitives import mysql


from bwtest.bwharness import TestSuite, TestCase
from bwtest import config

cc = None

class TestCommon( object ):

	@staticmethod
	def _getCC():
		global cc
		if cc:
			return cc

		cc = ClusterController( [ "simple_space/res" ] )
		return cc


	@staticmethod
	def getUserObj():
		env = command_util.CommandEnvironment( config.CLUSTER_USERNAME )
		return env.getUser()

	@staticmethod
	def getMachine():
		global cc
		ret = None
		if cc:
			ret = cc._machines[0]
		return ret


	@staticmethod
	def stopServer():
		TestCommon._getCC().stop() 
		return True


	@staticmethod
	def startServer():
		TestCommon._getCC().start()
		ret = TestCommon._getCC().waitForServerSettle( TestCommon.getUserObj() )
		return ret


	@staticmethod
	def restartServer():	
		TestCommon._getCC().stop() 
		TestCommon._getCC().start()
		ret = TestCommon._getCC().waitForServerSettle( TestCommon.getUserObj() )
		return ret



