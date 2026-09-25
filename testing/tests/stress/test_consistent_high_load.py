import time
import os
from bwtest import config
from bwtest import log
from bwtest import manual
from bwtest import TestCase

from helpers.cluster import ClusterController
from helpers.timer import runTimer

from template_reader import TemplateReader


class TestConsistentHighLoad( TestCase ):

	name = "Test Consistent High Load Stress Test"
	description = """
	Test whether the server can perform consistently and remain stable under
	high cell load
	"""

	# Number of entities to add per loop
	NORMAL_LOAD_ENTITIES_TO_ADD_AT_ONCE = 1500
	# The average CellApp load we want to sit at
	AVERAGE_UPPER_LOAD_THRESHOLD = 0.70
	# The load at which we count a CellApp as overloaded
	MAX_LOAD_THRESHOLD = 0.80
	# The number of max load checks before we give up trying to reach
	# average load
	MAX_LOAD_ATTEMPTS = 5
	# Max time until giving up trying to reach the average (in minutes)
	LOAD_EXPIRY_TIME = 60 * 20
	# Soak time of 8 hours
	TOTAL_SOAK_TIME = 60 * 60 * 8
	# Number of fragments to create from total time
	NUM_OF_FRAGMENTS = 10
	# Divide soak time by 10
	SOAK_FRAGMENT_TIME = TOTAL_SOAK_TIME / NUM_OF_FRAGMENTS
	#Do we want to fail on first process failure?
	SENSITIVE_RUN = False 

	tags = [ "MANUAL" ]

	RES_PATH = "stress/res"

	def setUp( self ):
		self._cc = ClusterController ( self.RES_PATH, load = True )

	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()

	def startCluster( self ):
		cc = self._cc

		xmlPath = os.path.join( config.TEST_ROOT, 
							"tests/stress/layouts/consistent_high_load.xml" )

		self.assertTrue( len(self._cc._machines) == 4,
			 "You need to define 4 machines in user_config.xml for this test" )

		layoutXML = TemplateReader( xmlPath, machine1=self._cc._machines[0],
                                  machine2=self._cc._machines[1], 
                                  machine3=self._cc._machines[2],
                                  machine4=self._cc._machines[3] )

		self._layoutPath = os.path.join( cc._tempTree, "stressLayout.xml" )

		f = open( self._layoutPath , "w" )
		f.write( layoutXML.read() )
		f.close()

		self._cc.start( layoutXML )


	def step1( self ):
		"""
		Create loadEntity's until average CellApp load reaches the set average
		"""

		log.progress( "NOTE: This test will sleep for a total of %d hour(s). " \
				"This does not include the time it takes to reach avg load",
				self.TOTAL_SOAK_TIME / 60 / 60 )
	
		self.startCluster()

		createSpaceSnippet = """
		e =BigWorld.createBaseAnywhere( "SpaceCreator", 
									spaceDir = "/spaces/30x30" )
		srvtest.finish( e.id )
		"""
		createEntitySnippet = """
		import random
		for x in range ( 0, {numGuards} ):
			startPos = ( random.randrange(-1500, 1500) , 0, 
						random.randrange(-1500, 1500) )
			spaceBounds = { 'minX': -1500, 'maxX': 1500, 
							'minY': -1500, 'maxY': 1500 }
			e = BigWorld.createBaseAnywhere( "NormalLoadEntity", 
				spaceID = 2, position = startPos,
				spaceBounds = spaceBounds )
		srvtest.finish()
		"""


		runTimer( self._cc.getUser().verifyLayoutIsRunning, 
				timeout = 20, file = self._layoutPath )

		# Create a single 30x30 space to create entities on
		entityId = self._cc.sendAndCallOnApp( "baseapp", 1, createSpaceSnippet )
		
		log.debug( "Created space" )
		time.sleep( 5 )
		
		averageLoad = self._cc.getWatcherValue( "cellAppLoad/average", 
											"cellappmgr", None )
		maxLoad = self._cc.getWatcherValue( "cellAppLoad/max", 
										"cellappmgr", None )

		log.info( "Average load check: %f", averageLoad )
		log.info( "Max load check: %f", maxLoad )

		numGuardsToAdd = self.NORMAL_LOAD_ENTITIES_TO_ADD_AT_ONCE

		maxLoadCounter = 0
		startTime = time.time()
	

		# Loop until we reach desired average load
		while( averageLoad < self.AVERAGE_UPPER_LOAD_THRESHOLD ):

			# Fail if could not reach average before timeout.
			# This deals with the scenario that the watchers
			# are broken/report incorrect values
			if( time.time() > startTime + self.LOAD_EXPIRY_TIME  ):
				self.fail( "Could not reach the average load in time" )
		
			if maxLoad < self.MAX_LOAD_THRESHOLD:
				self._cc.sendAndCallOnApp( "baseapp", 1, 
										createEntitySnippet, 
										numGuards = numGuardsToAdd )
				maxLoadCounter = 0
			else:
				maxLoadCounter += 1
				log.info( "A CellApp has hit max load threshold. " \
					"%d checks remaining before we give up and soak",
					 self.MAX_LOAD_ATTEMPTS - maxLoadCounter )

			if maxLoadCounter >= self.MAX_LOAD_ATTEMPTS:
				log.info( "Max load attempts exhausted, giving " \
					"up on reaching average load, proceeding" )
				break

			time.sleep( 30 )
			
			averageLoad = self._cc.getWatcherValue( "cellAppLoad/average", 
												"cellappmgr", None )
			maxLoad = self._cc.getWatcherValue( "cellAppLoad/max", 
											"cellappmgr", None )

			log.info( "Average load check: %f", averageLoad )
			log.info( "Max load check: %f", maxLoad )

		log.progress( "I will now sleep for a total of %d hour(s), I will wake up " \
				"every %d minute(s) to check server status, goodnight!", 
				( ( self.TOTAL_SOAK_TIME / 60 ) / 60 ),
				( ( self.SOAK_FRAGMENT_TIME / 60 ) ) )
		
		fragmentCounter = 1

		# Will sleep in fragments, checking for process deaths in between
		while( fragmentCounter <= self.NUM_OF_FRAGMENTS ):

			log.progress( "Starting sleep for fragment %d. I will sleep for %d minute(s)",
					fragmentCounter, self.SOAK_FRAGMENT_TIME / 60 )
			time.sleep( self.SOAK_FRAGMENT_TIME )
			log.progress( "Sleep for fragment %d complete", fragmentCounter )

			self._correctLayout = self._cc.getUser().verifyLayoutIsRunning( 
				self._layoutPath )

			if not self._correctLayout:
				log.error( "Processes were lost since last sleep" )

				# In this case if sensitive run is enabled,
				# we want the test to fail as soon as a process
				# goes down
				if self.SENSITIVE_RUN:
					self.assertTrue( self._correctLayout, "Sensitive run " \
					"is enabled and we have lost at least one process, " \
					"test fails right now" )
			fragmentCounter += 1

		self.assertTrue( self._correctLayout, "Test finished with processes missing")
