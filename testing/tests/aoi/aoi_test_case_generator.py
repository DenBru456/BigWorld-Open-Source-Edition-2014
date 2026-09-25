from aoi_test_case import AoITestCase
from bwtest import TestCase, TestSuite

def generateTypeName( witnessFirst, singleCell, entityAppeal, witnessAppeal, moveEntities ):
	"""
	Generate a unique class name for a generated AoITestCase
	"""
	if witnessFirst:
		firstSpawn = "Witness"
		firstKind = ""
		if witnessAppeal > 0:
			firstKind = "Appealing"
		secondSpawn = "Entities"
		secondKind = ""
		if entityAppeal > 0:
			secondKind = "Appealing"
	else:
		firstSpawn = "Entities"
		firstKind = ""
		if entityAppeal > 0:
			firstKind = "Appealing"
		secondSpawn = "Witness"
		secondKind = ""
		if witnessAppeal > 0:
			secondKind = "Appealing"
	if moveEntities:
		activity = "MoveEntities"
	else :
		activity = "DestroyEntities"
	if singleCell:
		cellStyle = "Locally"
	else:
		cellStyle = "Remotely"

	# e.g. SpawnAppealingWitnessThenEntitiesOnTheSameCellThenDestroyEntities
	return "Spawn%s%sThen%s%s%sThen%s" % (
		firstKind, firstSpawn, secondKind, secondSpawn, cellStyle, activity )


def generateName( witnessFirst, singleCell, entityAppeal, witnessAppeal, moveEntities ):
	"""
	Generate the one-line description of a generated AoITestCase
	"""
	if witnessFirst:
		firstSpawn = "witness"
		firstKind = ""
		if witnessAppeal > 0:
			firstKind = "appeal-radius "
		secondSpawn = "entities"
		secondKind = ""
		if entityAppeal > 0:
			secondKind = "appeal-radius "
	else:
		firstSpawn = "entities"
		firstKind = ""
		if entityAppeal > 0:
			firstKind = "appeal-radius "
		secondSpawn = "witness"
		secondKind = ""
		if witnessAppeal > 0:
			secondKind = "appeal-radius "
	if moveEntities:
		activity = "move the entities"
	else:
		activity = "destroy the entities"
	if singleCell:
		cellStyle = "on the same cell"
	else:
		cellStyle = "not on the same cell"

	return "Spawn %s%s then %s%s %s then %s" % (
		firstKind, firstSpawn, secondKind, secondSpawn, cellStyle, activity )

def generateDescription( witnessFirst, singleCell, entityAppeal, witnessAppeal, moveEntities ):
	"""
	Generate the long-prose description of a generated AoITestCase
	"""
	if witnessAppeal > 0:
		witnessKind = "an appeal-radius witness"
	else:
		witnessKind =  "a witness"

	if entityAppeal > 0:
		entityKind = "appeal-radius entities at each cardinal point in each " \
					"relevant range (AoI, AppealRadius and out-of-AoI)"
	else:
		entityKind = "entities at each cardinal point in each " \
					"relevant range (AoI and out-of-AoI)"

	if witnessFirst:
		firstSpawn = witnessKind
		secondSpawn = entityKind
	else:
		firstSpawn = entityKind
		secondSpawn = witnessKind
	if moveEntities:
		activity = "move and destroy the entities"
	else:
		activity = "destroy the entities"
	if singleCell:
		cellStyle = "on the same cell"
	else:
		cellStyle = "not on the same cell"

	return "Spawn %s, spawn %s %s, and then %s." % (
		firstSpawn, secondSpawn, cellStyle, activity )

def generateInitMethod( singleCell, entityAppeal, witnessAppeal ):
	"""
	Generate an __init__ method for an AoITestCase
	"""
	def __init__( self ):
		TestCase.__init__( self )
		AoITestCase.__init__( self,
			entityAppealRadius = entityAppeal,
			witnessAppealRadius = witnessAppeal,
			singleCell = bool( singleCell ) )

	return __init__

def generateSetUpMethod():
	"""
	Generate a setUp method for an AoITestCase
	"""
	def setUp( self ):
		TestCase.setUp( self )
		AoITestCase.setUp( self )

	return setUp

def generateSpawnWitness():
	"""
	Generate a step for an AoITestCase to spawn a witness
	"""
	return AoITestCase.spawnWitness

def generateSpawnEntities():
	"""
	Generate a step for an AoITestCase to spawn all its entities
	"""
	return AoITestCase.spawnEntities

def generateMoveEntities( entityAppeal ):
	"""
	Generate a step for an AoITestCase to move Entities in and out of AoI
	"""
	if entityAppeal > 0:
		def moveEntities( self ):
			"""Move all in-AoI entities out, and all out-of-AoI entities in"""
			self.moveEntities( inAoI = 2, inAppealRadius = 1, outOfAoI = 1 )
	else:
		def moveEntities( self ):
			"""Move all in-AoI entities out, and all out-of-AoI entities in"""
			self.moveEntities( inAoI = 1, outOfAoI = 1 )
	return moveEntities

def generateDestroyEntities():
	"""
	Generate a step for an AoITestCase to destroy all entities except the witness
	"""
	return AoITestCase.destroyEntities

def generateTestCase( witnessFirst, singleCell, entityAppeal, witnessAppeal, moveEntities ):
	"""
	Build a TestCase instance to test the given collection of adjustable parameters
	"""
	
	testCaseTypeName = generateTypeName( witnessFirst, singleCell, entityAppeal, witnessAppeal, moveEntities )

	testCaseName = generateName( witnessFirst, singleCell, entityAppeal, witnessAppeal, moveEntities )

	testCaseDescription = generateDescription( witnessFirst, singleCell, entityAppeal, witnessAppeal, moveEntities )

	testCaseDict = {}
	testCaseDict[ "tags" ] = []
	testCaseDict[ "name" ] = testCaseName
	testCaseDict[ "description" ] = testCaseDescription
	testCaseDict[ "__init__" ] = generateInitMethod( singleCell, entityAppeal, witnessAppeal )
	testCaseDict[ "setUp" ] = generateSetUpMethod()

	class StepAdder( object ):
		def __init__( self, target ):
			self.__step = 1
			self.__target = target

		def __call__( self, method ):
			self.__target[ "step%d" % ( self.__step, ) ] = method
			self.__step += 1

	addStep = StepAdder( testCaseDict )

	if witnessFirst:
		addStep( generateSpawnWitness() )
		addStep( generateSpawnEntities() )
	else:
		addStep( generateSpawnEntities() )
		addStep( generateSpawnWitness() )

	if moveEntities:
		addStep( generateMoveEntities( entityAppeal ) )

	addStep( generateDestroyEntities() )

	testCaseClass = type( testCaseTypeName, ( AoITestCase, TestCase ), testCaseDict )

	return testCaseClass


def generateTestCases():
	"""
	Generator function for test case classes
	"""
	for witnessFirst in True, False:
		for singleCell in True, False:
			for entityAppeal in 0, 500:
				for witnessAppeal in 0, 500:
					for moveEntities in True, False:
						yield generateTestCase( witnessFirst, singleCell, entityAppeal, witnessAppeal, moveEntities )


class GeneratedAoITestCases:
	name = "Generated AoI Test Cases"
	description = "Generates and runs tests of the AoI Range-Trigger system"

	tags = []

	def __init__( self ):
		# Doing this will bypass bwtest's filtering, and cause all
		# test cases to be always run
		# self.addCases( [( x() for x in generateTestCases )] )
		self.addCasesToModule( generateTestCases() )

	def addCasesToModule( self, cases ):
		"""
		bwtest relies on all TestCases being in the module and the TestSuites
		being otherwise empty, for filtering purposes.
		"""
		for case in cases:
			name = case.__name__
			globals()[ name ] = case


generatedSuite = GeneratedAoITestCases()
