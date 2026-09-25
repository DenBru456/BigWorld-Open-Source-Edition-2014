import bwtest
import time
import math

from bwtest import log
from bwtest import config
from bwtest import manual

from helpers.cluster import ClusterController
from helpers.timer import runTimer

from template_reader import TemplateReader


def approxEqual(a, b, tolerance = 0.00001):
	return abs(a - b) < tolerance


class LoadBalanceBase( object ):

	def getSpaces( self ):
		""" This method returns a list of spaces in the cluster """
		cc = self._cc

		def getSpaces():
			spaces = []
			dirs = cc.getWatcherData( "spaces", "cellappmgr", None )
			for space in dirs:
				for elem in space:
					if elem.name == "id":
						spaces.append( elem.value )

			return spaces

		spaces = runTimer( getSpaces, lambda spaces: bool( spaces ) )

		return spaces


	def populateSpace( self,
					spaceID,
					layout = None,
					layoutParam = None,
					fixedLoad = None,
					randomVariation = None ):
		snippet = """
import random
entities = []
loads = {loads}

xStep = 20
if {layout} == "cross" or {layout} == "doublecross":
	xStep = 5

if {layout} == "horn":
	xStep = 10

for x in xrange( -200, 200, xStep ):
	idx = 0
	for ld in loads:
		posStep = idx - len( loads ) / 2

		if {layout} == "cross" and x != 0 and posStep != 0:
			idx += 1
			continue

		if {layout} == "doublecross" and x != 0 and posStep !=0 \
						 and posStep != {layoutParam}:
			idx += 1
			continue

		if {layout} == "horn":
			if posStep < 0:
				pass
			if posStep % 2 != 0:
				idx += 1
				continue

		eload = ld

		if {layout} == "heavy" and x != 0 and abs( posStep ) < 10:
			idx += 1
			continue
		if {layout} == "heavy" and x == 0 and posStep == 0:
			eload = ld * 100.0

		if {layout} == "single" and (x != 0 or posStep != 0):
			idx += 1
			continue

		e = BigWorld.createEntity( "TestEntity" )
		entities.append( (e.id, eload) )
#		e.artificialMinLoad = ld

		dx = 0.0
		dz = 0.0
		if {randomVariation}:
			dx = (random.random() - 0.5) * {randomVariation} * 2.0
			dz = (random.random() - 0.5) * {randomVariation} * 2.0

		pos = (x + dx, 0,  posStep * {step} + dz)

		e.cellData[ "spaceID" ] = {spaceID}
		e.cellData[ "position" ] = pos
		e.createCellEntity()

		idx += 1

srvtest.finish( entities )
		"""

		def loadOfIdx( idx ):
			base = 0.0001
			step = base / 10.0
			factor = 1.1
			return (base + idx * step) * factor

		loads = None

		if fixedLoad:
			loads = [ fixedLoad for l in xrange( 100 ) ]
		else:
			loads = [ loadOfIdx( l )  for l in xrange( 100 ) ]

		totalLoad = sum( loads )
		currLoad = 0
		idx = 0
		for l in loads:
			currLoad += l
			if currLoad >= totalLoad / 2:
				break
			idx += 1

		step = 400.0 / len( loads )

		pairs = self._cc.sendAndCallOnApp( "baseapp", 1, snippet,
				loads = loads, spaceID = spaceID, step = step,
				layout = layout, layoutParam = layoutParam,
				randomVariation = randomVariation )

		boundary = (idx - len( loads ) / 2.0) * step

		return (loads, pairs, boundary)


class LoadBalanceTest( LoadBalanceBase, bwtest.TestCase ):
	name = "Load balance test" 
	description = """
	Test two-cell balance with entities with artificial load
	"""
	tags = [  ]


	RES_PATH = "simple_space/res"
	
	NUM_ENTITIES = 2001

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )

		xmlPath = config.TEST_ROOT + "/tests/load_balance/layout.xml"
		# self._cc.start( 
		#	layoutXML = TemplateReader( xmlPath, machine=self._cc._machines[0] ) )

		self._cc.start()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def step1( self ):
		"""
		Create grid of entities
		"""

		# spaceID = self._cc.callOnApp( "cellapp", 1, "snippetWaitForSpace" )

		spaces = self.getSpaces()

		self.assertTrue( spaces, "No spaces found in the cluster" )

		spaceID = spaces[ 0 ]

		time.sleep ( 2 )

		self._loads, self._pairs, boundary = self.populateSpace( spaceID )

		time.sleep( 1 )

		snippet = """
pairs = {pairs}
for pair in pairs:
	e = BigWorld.entities[ pair[0] ]
	e.artificialMinLoad = pair[1]

srvtest.finish()
		"""

		self._cc.sendAndCallOnApp( "cellapp", 1, snippet,
				 loads = self._loads, pairs = self._pairs )

		self._cc.startProc( "cellapp" )

		time.sleep( 5 )

		numCells = self._cc.getWatcherValue( "spaces/%d/numCells" % spaceID,
									  "cellappmgr", None )

		self.assertTrue( numCells == 2, "Failed to get two cells in the space. "
				  "This is not a feature failure yet. "
				   "Try running the test again." )

		#manual.input( "Now watch for balance, boundary should be around %f" % 
		#   			boundary )
		#return

		def getBoundaryPos():
			return self._cc.getWatcherValue(
					"spaces/%d/bsp/position" % spaceID,
					 "cellappmgr", None )

		# attempt to wait for boundary to settle
		for i in xrange( 20 ):
			if abs( getBoundaryPos() - boundary ) < boundary * 0.5:
				break
			time.sleep( 1 )

		positions = []
		for i in xrange( 20 ):
			currPos = getBoundaryPos()
			positions.append( currPos )
			time.sleep( 1 )

		boundaryAvg = sum( positions ) / len( positions )

		self.assertTrue( abs(boundary - boundaryAvg) < boundary * 0.15,
				 "average boundary pos (%f) is too far from "
				  "expected value (%f), positions = %r" % 
				  	(boundaryAvg, boundary, positions) )
		
		#Check that entities get moved as expected when adding/removing cellapps
		def checkEntitiesCount( num_apps ):
			sum = 0
			for i in range( 1, num_apps+1 ):
				sum += int( self._cc.getWatcherValue( "stats/numRealEntities",
										"cellapp", i ) )
			self.assertTrue( sum == self.NUM_ENTITIES,
						"Real entities count for %s cellapps was %s, not %s" % \
							 ( num_apps, sum, self.NUM_ENTITIES ) )
		
		checkEntitiesCount( 2 )
		self._cc.startProc( "cellapp" )
		time.sleep( 1 )
		for i in range( 10 ):
			checkEntitiesCount( 3 )
			time.sleep( 1 )
		self._cc.killProc( "cellapp", 3 )
		time.sleep( 1 )
		for i in range( 10 ):
			checkEntitiesCount( 2 )
			time.sleep( 1 )
		self._cc.killProc( "cellapp", 2 )
		time.sleep( 1 )
		for i in range( 10 ):
			checkEntitiesCount( 1 )
			time.sleep( 1 )
		
			


class CellAppWatcherGetter( object ):

	def getCellAppData( self, numCellApps ):
		""" This method returns space data from cellapps """
		cc = self._cc

		def getAppData( cellAppOrd ):
			spaces = []
			dirs = cc.getWatcherData( "spaces", "cellapp", cellAppOrd )
			for space in dirs:
				spaceID = 0
				numEntitites = 0
				for elem in space:
					if elem.name == "id":
						spaceID = elem.value
					if elem.name == "numEntities":
						numEntities = elem.value
				spaces.append( {'id': spaceID, 'numEntities': numEntities} )

			load = cc.getWatcherValue( "load", "cellapp", cellAppOrd )

			return {'spaces': spaces, 'load': load}


		apps = {} 
		for app in xrange( 1, numCellApps + 1 ):
			apps[ app ] = getAppData( app )

		return apps
	 

class MultiSpaceBalanceTest( LoadBalanceBase, CellAppWatcherGetter, bwtest.TestCase ):
	name = "Multi-space load balance test" 
	description = """
	Test multi-space load balance with artificial load on spaces
	"""

	tags = [ 'STAGED' ]

	NUM_SPACES = 32
	NUM_CELLAPPS = 8

	RES_PATH = [ "simple_space_multiple_spaces/res", "simple_space/res" ]


	def setArtificialLoadOnSpaces( self, spaces, load, numCellApps ):
		snippet = """
spaces = {spaces}
for e in BigWorld.entities.values():
	if e.spaceID in spaces:
		BigWorld.setSpaceArtificialMinLoad( e.spaceID, {load} )
		spaces.remove( e.spaceID )
srvtest.finish()
		"""

		for ord in xrange( 1, numCellApps + 1 ):
			self._cc.sendAndCallOnApp( "cellapp", ord , snippet,
				 spaces = spaces, load = load )

	def startCluster( self ):
		xmlPath = config.TEST_ROOT + "/tests/load_balance/layout.xml"
		self._cc.start( 
			layoutXML = TemplateReader( xmlPath, machine=self._cc._machines[0] ) )


	def stopCluster( self ):
		self._cc.stop()


	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		self.startCluster()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def getStandardDeviation( self ):
		expectation = float( self.NUM_SPACES ) / self.NUM_CELLAPPS
		apps = self.getCellAppData( self.NUM_CELLAPPS )
		deviation = 0.0
		for appOrd, data in apps.iteritems():
			deviation += (len( data['spaces'] ) - expectation) ** 2
		deviation = math.sqrt( deviation / len( apps ) )
		return deviation


	def runAndGetDeviation( self, artificialLoad, 
							prePopulateSpace = False,
							postPopulateSpace = True ):

		if prePopulateSpace:
			time.sleep( 5 )
			spaces = self.getSpaces()
			self.populateSpace( spaces[0] )

		snippet = """
for i in xrange( {numSpacesToAdd} ):
	BigWorld.createBaseLocally( "Space", spaceDir = "spaces/main" )

srvtest.finish()
		"""

		self._pairs = self._cc.sendAndCallOnApp( "baseapp", 1, snippet,
				 numSpacesToAdd = self.NUM_SPACES - 1 )


		time.sleep ( 2 )

		spaces = self.getSpaces()

		# print "found spaces: %r" % spaces

		self.assertEqual( len( spaces ), self.NUM_SPACES, 
				   			"No spaces found in the cluster" )

		time.sleep ( 2 )

		if postPopulateSpace:
			self.populateSpace( spaces[0] )

		if artificialLoad > 0.0:
			self.setArtificialLoadOnSpaces( spaces, artificialLoad,
								 		self.NUM_CELLAPPS )

		time.sleep ( 30 ) # wait for cells to settle

		return self.getStandardDeviation()

		res = True
		while res:
			apps = self.getCellAppData( self.NUM_CELLAPPS )
			for appOrd, data in apps.iteritems():
				log.info( "cellapp%02d: %r\n",
			 			appOrd, data )
				log.info( "std deviation: %f\n",
			 			self.getStandardDeviation() )

			res = manual.input_yesno( "Now watch for balance. "
										"Re-read the space data?" )

		return self.getStandardDeviation()



	def step1( self ):
		"""
		Get deviation from cluster with artificial load
		"""

		self._deviationWithArtificialLoad = self.runAndGetDeviation( 0.1 )

		self.stopCluster()


	def step2( self ):
		"""
		Get deviation from cluster without artificial load
		"""

		self.startCluster()

		self._deviationWithoutArtificialLoad = self.runAndGetDeviation( 0.0 )

		strDev = "Deviation with artificial load: %f, without: %f" % \
					(self._deviationWithArtificialLoad,
						self._deviationWithoutArtificialLoad)

		log.info( strDev )

		self.assertTrue( self._deviationWithArtificialLoad <
				  			self._deviationWithoutArtificialLoad,
				  		strDev )

		self.stopCluster()


	def step3( self ):
		"""
		Get deviation from cluster with high estimated initial cell load
		"""

		self._cc.setConfig( "cellAppMgr/estimatedInitialCellLoad", str( 0.1 ) )

		self.startCluster()

		self._deviationWithHighEstimatedLoad = self.runAndGetDeviation( 0.0, True, False )

		self.stopCluster()


	def step4( self ):
		"""
		Get deviation from cluster with zero estimated initial cell load
		"""

		self._cc.setConfig( "cellAppMgr/estimatedInitialCellLoad", str( 0.0 ) )

		self.startCluster()

		self._deviationWithZeroEstimatedLoad = self.runAndGetDeviation( 0.0, True, False )

		strDev = "Deviation with high load: %f, with zero load: %f" % \
					(self._deviationWithHighEstimatedLoad,
						self._deviationWithZeroEstimatedLoad)

		log.info( strDev )

		self.assertTrue( self._deviationWithHighEstimatedLoad <
				  			self._deviationWithZeroEstimatedLoad,
				  		strDev )



class EdgeEntityOffloadTestBase( LoadBalanceBase ):

	RES_PATH = "simple_space/res"

	numCellApps = 2

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH )
		self._cc.setConfig( "balance/numCPUOffloadLevels", str( 5 ) )

		# xmlPath = config.TEST_ROOT + "/tests/load_balance/layout.xml"
		# self._cc.start( 
		#	layoutXML = TemplateReader( xmlPath, machine=self._cc._machines[0] ) )

		self._cc.start()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def step1( self ):
		"Populating space with specified entity layout, checking balance"

		self.checkBalance()


	def checkBalance( self ):
		"""
		Create grid of entities
		"""

		# spaceID = self._cc.callOnApp( "cellapp", 1, "snippetWaitForSpace" )

		spaces = self.getSpaces()

		self.assertTrue( spaces, "No spaces found in the cluster" )

		spaceID = spaces[ 0 ]

		time.sleep ( 2 )

		self._loads, self._pairs, boundary = self.populate( spaceID )

		time.sleep( 1 )

		snippet = """
pairs = {pairs}
for pair in pairs:
	e = BigWorld.entities[ pair[0] ]
	e.artificialMinLoad = pair[1]

srvtest.finish()
		"""

		self._cc.sendAndCallOnApp( "cellapp", 1, snippet,
				 loads = self._loads, pairs = self._pairs )

		self._cc.startProc( "cellapp", self.numCellApps - 1 )

		time.sleep( 5 )

		def getNumCells():
			numCells = self._cc.getWatcherValue( "spaces/%d/numCells" % spaceID,
										  "cellappmgr", None )
			return numCells >= 2

		runTimer( getNumCells )

		def getBoundaryPos():
			return self._cc.getWatcherValue(
					"spaces/%d/bsp/position" % spaceID,
					 "cellappmgr", None )

		if self.MANUAL:
			res = True
			while res:
				boundary = getBoundaryPos()
				print "boundary pos: %r\n" % boundary

				res = manual.input_yesno( "Now watch for balance. "
											"Re-read the boundary position?" )

			return

		boundary = getBoundaryPos()
		prevBoundary = boundary
		timeCount = 0.0
		equalityCount = 0
		while timeCount <= 60.0 * 3: # 3 minutes should be fine
			SLEEP_TIME = 0.5
			time.sleep( SLEEP_TIME )
			prevBoundary = boundary
			boundary = getBoundaryPos()
#			print "boundary pos: %r\n" % boundary
			if approxEqual( prevBoundary, boundary ):
				equalityCount += 1
				if equalityCount >= 5.0 / SLEEP_TIME:
					break
			else:
				equalityCount = 0

			timeCount += SLEEP_TIME

		self.assertTrue( approxEqual( prevBoundary, boundary ),
			 		"Failed to stabilise cell boundary" )

		timeCount = 0.0
		while timeCount <= 30.0:
			time.sleep( 0.3 )
			currBoundary = getBoundaryPos()
#			print "stable boundary pos: %r\n" % currBoundary
			self.assertTrue( approxEqual( currBoundary, boundary ),
						"Detected boundary wobbling. "
						"Boundary positions before and after: (%f, %f)" %
							(boundary, currBoundary) )

			timeCount += 0.3

		return


class EdgeEntityOffloadTest( EdgeEntityOffloadTestBase, bwtest.TestCase ):
	name = "Entity offload test" 
	description = """
	Test reduced entity offload and partition oscillations when group of entities
	is close to the partition line between cells
	"""
	tags = [ 'MANUAL' ]


	RES_PATH = "simple_space/res"

	MANUAL = True # Switches this test to manual mode

	def populate( self, spaceID ):
#		return self.populateSpace( spaceID, "doublecross", 25, 0.001, 0.10 )
		return self.populateSpace( spaceID, "doublecross", -25, 0.001, 0.00 )
#		return self.populateSpace( spaceID, "cross", None, 0.001, 0.10 )
#		return self.populateSpace( spaceID, "heavy", None, 0.001, 0.10 )
#		return self.populateSpace( spaceID, "single", None, 0.5, 0.00 )
#		self.numCellApps = 5
#		return self.populateSpace( spaceID, "horn", 20, 0.002, 5.0 )


class EntityOffloadTestWithLayout( EdgeEntityOffloadTestBase ):
	name = "Entity offload test with various layouts" 
	description = """
	Test reduced entity offload and partition oscillations when group of entities
	is close to the partition line between cells
	"""
	tags = []


	MANUAL = False

	def populate( self, spaceID ):
		return self.populateSpace( spaceID,
							self.layoutName,
							self.layoutParam, 
							self.layoutDefEntityLoad,
							self.layoutEntityScattering )


parameters = [
	{
		'layoutName': "doublecross",
		'numCellApps': 2,
  		'layoutParam': 25,
  		'layoutDefEntityLoad': 0.001,
  		'layoutEntityScattering': 0.10
 	},
	{
		'layoutName': "doublecross",
		'numCellApps': 2,
  		'layoutParam': -25,
  		'layoutDefEntityLoad': 0.001,
  		'layoutEntityScattering': 0.10
 	},
	{
		'layoutName': "cross",
		'numCellApps': 2,
  		'layoutParam': None,
  		'layoutDefEntityLoad': 0.001,
  		'layoutEntityScattering': 0.10
 	},
	{
		'layoutName': "heavy",
		'numCellApps': 2,
  		'layoutParam': None,
  		'layoutDefEntityLoad': 0.001,
  		'layoutEntityScattering': 0.10
 	},
	{
		'layoutName': "single",
		'numCellApps': 2,
  		'layoutParam': None,
  		'layoutDefEntityLoad': 0.5,
  		'layoutEntityScattering': 0.0
 	},
	{
		'layoutName': "horn",
		'numCellApps': 5,
  		'layoutParam': 20,
  		'layoutDefEntityLoad': 0.001,
  		'layoutEntityScattering': 0.0
 	},
	{
		'layoutName': "horn",
		'numCellApps': 5,
  		'layoutParam': 20,
  		'layoutDefEntityLoad': 0.001,
  		'layoutEntityScattering': 5.00
 	}
	]

bwtest.addParameterizedTestCases( EntityOffloadTestWithLayout, parameters )



class TestHighLoadBalanceWithGuardsManual( CellAppWatcherGetter, bwtest.TestCase ):
	name = "High load with guards"
	description = """
	Testing cluster with many apps and many walking guards.
	This test uses fantasydemo resource tree.
	"""

	tags = ["MANUAL"]


	NUM_CELLAPPS = 8

	GUARDS_TO_ADD_AT_ONCE = 500

	RES_PATH = config.CLUSTER_BW_ROOT + "/game/res/fantasydemo"
	# log.debug( "RES_PATH=%s" % RES_PATH )

	def setUp( self ):
		self._cc = ClusterController( self.RES_PATH, load = True )


	def tearDown( self ):
		self.stopCluster()

		self._cc.clean()


	def startCluster( self ):
		cc = self._cc

		cc.start()

		cc.startProc( "baseapp", 1, 0 )
		cc.startProc( "baseapp", 2, 1 )
		cc.startProc( "cellapp", self.NUM_CELLAPPS / 2 - 1, 0 )
		cc.startProc( "cellapp", self.NUM_CELLAPPS / 2, 1 )
		#cc.startProc( "bots", 1, 0 )
		#cc.startProc( "bots", 1, 1 )

		cc.waitForApp( "baseapp", 1 )
		cc.waitForApp( "baseapp", 2 )
		cc.waitForApp( "baseapp", 3 )
		cc.waitForApp( "baseapp", 4 )


	def stopCluster( self ):
		# if stopping fails, there was likely a crashed app
		cc = self._cc

		cc.stop()

	def addGuards( self, numGuards ):
		cc = self._cc

		numBaseApps = 4

		guardsPerApp = numGuards / numBaseApps

		snippet = """
import util
util.addGuards( {num} )
srvtest.finish()
"""
		for appOrd in range( 1, numBaseApps ):
			cc.sendAndCallOnApp( "baseapp", appOrd, snippet,
					  	num = guardsPerApp )


	def getStandardDeviation( self, apps ):
		loads = []
		for appOrd, data in apps.iteritems():
			loads.append( data['load'] )
		deviation = 0.0
		expectation = sum( loads ) / float( len( loads ) )
		for load in loads:
			deviation += (load - expectation) ** 2
		deviation = math.sqrt( deviation / len( loads ) )
		return deviation


	def runTest( self ):
		"""Create many guards and check the cluster is stable"""

		self.startCluster()

		numGuardsToAdd = 3000

		numAdds = int(numGuardsToAdd / self.GUARDS_TO_ADD_AT_ONCE) 
		for i in range( numAdds ):
			log.debug( "adding %d guards for %d/%d time", 
			 				self.GUARDS_TO_ADD_AT_ONCE, i + 1, numAdds )
			self.addGuards( self.GUARDS_TO_ADD_AT_ONCE  )
			time.sleep( 15 )

		
		res = True		
		while res:
			apps = self.getCellAppData( self.NUM_CELLAPPS )
			deviation = self.getStandardDeviation( apps )
			
			resStr = "" 
			for appOrd, data in apps.iteritems():
				resStr += "cellapp%02d: %r\n" % \
			 			 ( appOrd, data )
			
			resStr += "std deviation: %f\n" % \
					( deviation )

			res = manual.input_yesno( resStr + "\nNow watch for balance. "
								"Re-read the space data ('n' to finish the test)?" )

		# manual.input( "Now check the balance. Press <Enter> to finish the test" )
