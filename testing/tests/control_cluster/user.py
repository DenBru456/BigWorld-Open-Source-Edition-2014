from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *
import xmlconf

class UserTest( TestCase ):
	
	
	name = "Control Cluster -u"
	description = "Tests control_cluster.py -u option"
	tags = []
	
	
	def setUp( self ):
		self.user = config.CLUSTER_USERNAME_2
		self.uid = config.CLUSTER_UID_2
		clusterConfigFileName = "user_config/server/bw_%s.xml" % self.user 
		clusterConfigName =  config.TEST_ROOT + "/" + clusterConfigFileName
		res = {}
	
		try:
			success = xmlconf.readConf( clusterConfigName, res,
			{
				'db/mysql/databaseName':	 'dbname',
			} )

		except IOError:
			import traceback
			traceback.print_exc()
		self.cc = ClusterController( "simple_space/res", 
											user = self.user,
											db = res["dbname"] )
		
	
	def tearDown( self ):
		if hasattr( self, 'cc'):
			self.cc.stop()
			self.cc.clean()
		
	
	def runTest( self ):
		run_cc_command( "start", [config.CLUSTER_MACHINES[0]],
						ccParams = ["-u", self.user])
		self.cc.waitForServerSettle()
		run_cc_command( "stop", [], ccParams = ["-u", self.user])
		self.cc.waitForServerShutdown()
		
		run_cc_command( "start", [config.CLUSTER_MACHINES[0]],
						ccParams = ["-u", str(self.uid)])
		self.cc.waitForServerSettle()
		run_cc_command( "stop", [], ccParams = ["-u",  str(self.uid)])
		self.cc.waitForServerShutdown()
		