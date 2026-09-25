import time
from bwtest import TestCase
from helpers.cluster import ClusterController


class ThrottledMethodsTest( TestCase ):
	
	name = "ThrottledMethods"
	tags = []
	description = """Test the ability for the server to protect against hacking by
	throttling methods that get called too frequently
	"""
	
	parameterDefs = [ ( "throttledBase", "baseapp" ), 
					( "throttledOwnCell", "cellapp" ),
					( "throttledAllCells", "cellapp" ) ]

	def setUp( self ):
		self.cc = ClusterController( ["throttled_methods/res", "simple_space/res"] )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def checkMethodCalls( self ):
		snippet = """
		avatars = [e for e in BigWorld.entities.values()\
					 if e.__class__.__name__ == 'Avatar']
		if len( avatars ) > 0:
			srvtest.finish( avatars[0].%s )
		else:
			srvtest.finish( 0 )
		"""
		counts = []
		for param, proc in self.parameterDefs:
			count = self.cc.sendAndCallOnApp( proc, 1, snippet % param )
			counts.append( ( param, count ) )
		return counts
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots", 1 )
		
		oldCounts = self.checkMethodCalls()
		self.assertTrue( [x[1] for x in oldCounts if x[1] != 0] == [], 
						"Method calls happened before bots added" )
		self.cc.bots.add( 1 )
		
		startTime = time.time()
		started = set()
		stopped = set()
		
		while (time.time() - startTime < 120 ):
			newCounts = self.checkMethodCalls()
			for param, count in newCounts:
				if param not in started and count != 0:
					started.add( param )
				if param in started and param not in stopped:
					for oldparam, oldcount in oldCounts:
						if oldparam == param and oldcount == count:
							stopped.add( param )
			oldCounts = newCounts
			time.sleep( 10 )

		for param, proc in self.parameterDefs:
			self.assertTrue( param in started, 
						"ThrottledMethod calls for %s never happened on %s" % \
						( param, proc ) )
			self.assertTrue( param in stopped, 
					"ThrottledMethod calls for %s were never throttled on %s" % \
					( param, proc ))
						
					
		
		
		