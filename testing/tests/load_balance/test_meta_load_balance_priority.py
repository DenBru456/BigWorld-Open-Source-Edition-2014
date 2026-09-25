import os, re

from bwtest import TestCase, config
from helpers.cluster import ClusterController
from helpers.timer import runTimer
from template_reader import TemplateReader
from primitives import locallog

class MetaLoadBalancePriorityBase( TestCase ):
	
	
	description = "Tests the ability to control meta load balance priority"
	tags = []
	
	def setUp( self ):
		self.cc = ClusterController( "stress/res" )
		self.cc.setConfig( "cellAppMgr/shouldShowMetaLoadBalanceDebug", "True" )
		xmlPath = os.path.join( config.TEST_ROOT, 
								"tests/load_balance/layout_meta.xml" )
		self.template = TemplateReader( xmlPath, machine1=self.cc._machines[0],
										machine2=self.cc._machines[1] )
	
	def tearDown( self ):
		if hasattr( self, "cc" ):
			self.cc.stop()
			self.cc.clean()


	def createSpace( self ):
		snippet = """
		e=BigWorld.createBaseAnywhere( "SpaceCreator",
		spaceDir = "/spaces/30x30" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", None, snippet )
		
		def checkSpacesLoadedOnAllCellApps():
			spacesFullyLoaded = 0
			for appID, proc in enumerate( self.cc.getProcs( "cellapp" ) ):
				num = int( self.cc.getWatcherValue( 
								"numSpacesFullyLoaded", "cellapp", appID+1 ) )
				spacesFullyLoaded += num
			return spacesFullyLoaded != 0
		runTimer( checkSpacesLoadedOnAllCellApps, timeout = 60 )

	
	def getAppScores( self, output, pattern ):
		appScores = []
		for line in output.split( "\n" ):
			m = re.search( pattern, line )
			if not m:
				continue
			appId = int( m.group(1) )
			score = float( m.group(2) )
			appScores.append( (appId, score ) )
			appId = int( m.group(3) )
			score = float( m.group(4) )
			appScores.append( (appId, score ) )
		return appScores
	
	
	def checkCellAddedAppropriately( self, appScores ):
		winningScore = None
		winningAppId = 0
		oldScore = None
		maybeWinningAppId = None
		#Check that highest score ends up handling the space
		#To explain the maybeWinningAppId logic, which can be confusing:
		#The logs can show two scores that appear as identical because of
		#limiting the length of the output, but the underlying value in the C++
		#code is different. It is therefore correct behavior for two apparently
		#identical scores to act differently in different test runs
		for appId, score in appScores:
			if not winningScore:
				winningScore = score
				winningAppId = appId
			if not oldScore:
				oldScore = score
				if winningScore != score:
					output = locallog.grepLastServerLog( 
							"Space::addCell: Space [0-9]\. CellApp %s" % \
							winningAppId )
					if len( output ) == 0 and maybeWinningAppId:
						output = locallog.grepLastServerLog( 
							"Space::addCell: Space [0-9]\. CellApp %s" % \
							maybeWinningAppId )
					self.assertTrue( len(output) > 0, 
							"Expected cell wasn't added to space")
					winningScore = score
					maybeWinningAppId = None
				elif maybeWinningAppId == appId:
					winningAppId = appId
					maybeWinningAppId = None
				continue
			if winningScore < score:
				winningScore = score
				winningAppId = appId
			elif winningScore == score:
				maybeWinningAppId = appId
			oldScore = None

		
	def checkCorrectCombinationOfScorers( self, types ):
		pattern = "compareCellApps\( ([A-Za-z]+) \).+"\
				"Old \(App ([0-9]).+Score (-?[0-9.]+)\).+"\
				"New \(App ([0-9]).+Score (-?[0-9.]+)"
		output = locallog.grepLastServerLog( pattern )

		appScores = []
		for line in output.split( "\n" ):
			m = re.search( pattern, line )
			if not m:
				continue
			scorerType = m.group(1)
			oldAppId = int( m.group(2) )
			oldScore = float( m.group(3) )
			newAppId = int( m.group(4) )
			newScore = float( m.group(5) )
			appScores.append( 
						(scorerType, oldAppId, oldScore, newAppId, newScore ) )

		scorerTypeIndex = 0
		winningScore = None
		winningAppId = 0
		
		for scorerType, oldAppId, oldScore , newAppId, newScore in appScores:
			self.assertTrue( scorerType == types[ scorerTypeIndex ],
							"Unexpected type %s. Expecting %s" % \
							(scorerType, types[ scorerTypeIndex ] ) )
			if ( oldScore == newScore ) and ( scorerTypeIndex < len(types) - 1 ):
				scorerTypeIndex += 1
			else:
				scorerTypeIndex = 0

	
	def addPriorityConfig( self, configTypes ):
		def addConfig( input, output ):
			for line in input.readlines():
				for subline in line.strip().split(">"):
					if subline and subline.strip() != line.strip():
						subline += ">" 
						output.write( subline + "\n" )
						if subline.strip() == "<cellAppMgr>":
							output.write( "<metaLoadBalancePriority>\n" )
							for c in configTypes:
								output.write( "<%s/>\n" % c )
							output.write( "</metaLoadBalancePriority>\n" )
					elif subline and subline.strip() == line.strip():
						output.write( line )
		self.cc.mangleResTreeFile( "server/bw_%s.xml" % \
									config.CLUSTER_USERNAME, addConfig )

class TestBaseCellTrafficScorer( MetaLoadBalancePriorityBase ):

	def runTest( self ):
		"""Tests that load-balancing prioritises choosing machines based on 
		reducing communication between baseapps and cellapps"""
		self.cc.setConfig( 
					"cellAppMgr/metaLoadBalancePriority/baseCellTraffic", "" )
		self.cc.start( layoutXML = self.template )
		self.createSpace()
		pattern = "BaseCellTrafficScorer.+"\
				"Old \(App ([0-9]).+Score ([0-9.]+)\).+"\
				"New \(App ([0-9]).+Score ([0-9.]+)"
		output = locallog.grepLastServerLog( pattern )
		appScores = self.getAppScores( output, pattern )
		
		desiredAppIds = [x.id for x in self.cc.findProcsByMachine( "cellapp", 
												self.cc._machines[0] ) ]
		
		for appId, score in appScores:
			if appId in desiredAppIds:
				self.assertTrue( score == 1,
					"Cellapp on same machine as baseapp wasn't scored higher" )
			else:
				self.assertTrue( score == 0,
					"Cellapp on different machine as baseapp was scored higher" )
		


class TestCellCellTrafficScorer( MetaLoadBalancePriorityBase ):
	
	def runTest( self ):
		"""Tests that load-balancing prioritises choosing machines based on 
		reducing communication between cellapps and cellapps"""
		self.cc.setConfig( 
					"cellAppMgr/metaLoadBalancePriority/cellCellTraffic", "" )
		self.cc.start( layoutXML = self.template )
		self.createSpace()

		pattern = "CellCellTrafficScorer.+"\
				"Old \(App ([0-9]).+Score ([0-9.]+)\).+"\
				"New \(App ([0-9]).+Score ([0-9.]+)"
		output = locallog.grepLastServerLog( pattern )
		appScores = self.getAppScores( output, pattern )
		
		desiredAppIds = [x.id for x in self.cc.findProcsByMachine( "cellapp", 
												self.cc._machines[0] ) ]
		old = None
		new = None
		for appId, score in appScores:
			if old == None:
				old = (appId, score)
				continue
			if ( old[1] == score ) and ( score == 0.0 ):
				old = None
				continue
			if ( appId in desiredAppIds ) != ( old[0] in desiredAppIds ):
				self.assertTrue( score != old[1], 
						"Cellapps on different machines had the same score" )
			else:
				self.assertTrue( score == old[1],
						"Cellapps on same machine had a different score" )
			old = None



class TestCellAppGroupLoadScorer( MetaLoadBalancePriorityBase ):
	
	def runTest( self ):
		self.cc.setConfig( 
					"cellAppMgr/metaLoadBalancePriority/groupLoad", "" )
		self.cc.start( layoutXML = self.template )
		self.createSpace()

		pattern = "CellAppGroupLoadScorer.+"\
				"Old \(App ([0-9]).+Score (-?[0-9.]+)\).+"\
				"New \(App ([0-9]).+Score (-?[0-9.]+)"
		output = locallog.grepLastServerLog( pattern )
		appScores = self.getAppScores( output, pattern )
		
		self.checkCellAddedAppropriately( appScores )


class TestCellAppLoadScorer( MetaLoadBalancePriorityBase ):
	
	def runTest( self ):
		self.cc.setConfig( 
					"cellAppMgr/metaLoadBalancePriority/cellAppLoad", "" )
		self.cc.start( layoutXML = self.template )
		self.createSpace()
		
		pattern = "CellAppLoadScorer.+"\
				"Old \(App ([0-9]).+Score (-?[0-9.]+)\).+"\
				"New \(App ([0-9]).+Score (-?[0-9.]+)"
		output = locallog.grepLastServerLog( pattern )
		appScores = self.getAppScores( output, pattern )
		
		self.checkCellAddedAppropriately( appScores )


class TestDefaultScorerCombination( MetaLoadBalancePriorityBase ):
	
	def runTest( self ):
		#Not setting config as we are using default set-up
		self.cc.start( layoutXML = self.template )
		self.createSpace()
		
		types = [ "CellAppGroupLoadScorer", "CellAppLoadScorer"]
		self.checkCorrectCombinationOfScorers( types )

		

class TestVariousScorerCombinations( MetaLoadBalancePriorityBase ):
			
	def runTest( self ):
		typeLists = []
		typeLists.append( [("baseCellTraffic", "BaseCellTrafficScorer"), 
						("cellAppLoad", "CellAppLoadScorer") ] )
		typeLists.append( [("baseCellTraffic", "BaseCellTrafficScorer"), 
						("baseCellTraffic", "BaseCellTrafficScorer"), 
						("cellAppLoad", "CellAppLoadScorer")] )
	
		for typeList in typeLists:
			self.addPriorityConfig( [t[0] for t in typeList] )
			self.cc.start( layoutXML = self.template )
			self.createSpace()
			self.checkCorrectCombinationOfScorers( [t[1] for t in typeList] )
			self.cc.stop()