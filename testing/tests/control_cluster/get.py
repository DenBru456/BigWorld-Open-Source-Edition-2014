from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class GetTest( TestCase ):
	
	
	name = "Control Cluster Get"
	description = "Tests control_cluster.py get command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		machine = config.CLUSTER_MACHINES[0]
		ret, output = run_cc_command( "get", ["cellapp01"] )
		patterns = [( 'cellapp01( )*on %s( )*->( )*<DIR>' % machine, 1 ),
					('\scellAppMgr = <DIR>', 1),
					('\sconfig = <DIR>', 1),
					('\snub = <DIR>', 1),
					('\sid = 1', 1)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected out from get cellapp01: %s" % output )
		
		ret, output = run_cc_command( "get", ["cellapp01", "id"] )
		patterns = [( 'cellapp01( )*on %s( )*->( )*id = 1' % machine, 1)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected out from get cellapp01 id: %s" % output )
		
		ret, output = run_cc_command( "get", ["cellapp01", "nub"] )
		patterns = [( 'cellapp01( )*on %s( )*->( )*<DIR>' % machine, 1),
					( 'artificialLoss = <DIR>', 1 ),
					( 'receiving = <DIR>', 1),
					('isVerbose = True', 1)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected out from get cellapp01 nub: %s" % output )
		
		ret, output = run_cc_command( "get", ["cellapp01", "nub/address"] )
		patterns = [( 'cellapp01( )*on %s( )*->( )*address = \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+' % machine, 1)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected out from get cellapp01 nub/address: %s" % output )
		
		self.cc.startProc( "cellapp", 2 )
		ret, output = run_cc_command( "get", ["cellapps", "nub/address"] )
		patterns = [( 'cellapp\d{1,2}( )*on %s( )*->( )*address = \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+' % machine, 3)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected out from get cellapp01 nub/address: %s" % output )
		
		