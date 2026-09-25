import time
from bwtest import TestCase
from helpers.cluster import ClusterController

class BackUpUndefinedPropertiesTest( TestCase ):
	
	
	name = "BackUpUndefinedProperties"
	description = "Tests functionality of backUpUndefinedProperties"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "baseApp/backUpPeriod", "10" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		default = self.cc.getConfig( "baseApp/backUpUndefinedProperties" )
		self.assertTrue( default == "false",
						"backUpUndefinedProperties didn't default to false" )
		self.cc.setConfig( "baseApp/backUpUndefinedProperties", "true" )
		self.cc.start()
		snippet = """
		e = BigWorld.createEntity( "PersistentEntity" )
		e.myProp = 15
		srvtest.finish( e.id )
		"""
		entityid = self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		
		self.cc.startProc( "baseapp", 1 )
		time.sleep( 10 )
		self.cc.retireProc( "baseapp", 1 )
		time.sleep( 5 )
		snippet2 = """
		e = BigWorld.entities[ %s ]
		srvtest.assertTrue( hasattr( e, "myProp" ), "Entity didn't backup myProp" )
		srvtest.assertTrue( e.myProp == 15, "Entity stored wrong value for myProp" )
		srvtest.finish()
		""" % entityid
		self.cc.sendAndCallOnApp( "baseapp", 2, snippet )


class ExternalPortsTest( TestCase ):
	
	
	name = "ExternalPorts"
	description = "Tests functionality of externalPorts"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		def addExternalPorts(input, output):
			for line in input.readlines():
				output.write( line )
				if line.strip() == "<root>":
					output.write("""
					<baseApp>
						<externalPorts>
							<port>1</port>
							<port>12010</port>
							<port>12011</port>
							<port>12012</port>
							<port>12013</port>
						</externalPorts>
					</baseApp>
					""")
		self.cc.mangleResTreeFile( "server/bw.xml", addExternalPorts )
		self.cc.start()
		self.cc.startProc( "baseapp", 2 )
		for i in range( 1, 4 ):
			port = self.cc.getWatcherValue( "nubExternal/address", 
											"baseapp", i ).split(":")[1]
			self.assertTrue( int(port) in [12010, 12011, 12012, 12013],
							"baseApp did not bind to any of the defined ports")


class ShouldResolveMailBoxesTest( TestCase ):
	
	
	name = "ShouldResolveMaliBoxes"
	description = "Tests functionality of shouldResolveMailBoxes"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.setConfig( "baseApp/shouldResolveMailBoxes", "false" )
		self.cc.setConfig( "cellApp/shouldResolveMailBoxes", "false" )
		self.cc.start()
		self.cc.startProc( "cellapp", 1 )
		self.cc.startProc( "baseapp", 1 )
		
		snippet = """
		e = BigWorld.createEntity( "PersistentEntity" )
		BigWorld.globalData["testBase"] = e
		srvtest.finish( e.id )
		"""	
		entityid = self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		snippet = """
		e = BigWorld.createEntity( "PersistentEntity", 2, (0, 0, 0), (0, 0, 0) )
		BigWorld.globalData["testCell"] = e
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		
		snippet = """
		srvtest.assertEqual( str( type( BigWorld.globalData["testBase"] ) ),
							"<type 'BaseEntityMailBox'>" )
		srvtest.assertEqual( str( type( BigWorld.globalData["testCell"] ) ),
							"<type 'CellEntityMailBox'>" )
		srvtest.finish()
		"""
		for app, procOrd in [("baseapp", 1), ("baseapp", 2),
							 ("cellapp", 1), ("cellapp", 2)]:
			self.cc.sendAndCallOnApp( app, procOrd, snippet )