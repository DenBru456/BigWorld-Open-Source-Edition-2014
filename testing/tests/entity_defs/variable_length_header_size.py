from bwtest import TestCase
from helpers.cluster import ClusterController, ClusterControllerError
from primitives import locallog

# Enough to exhaust low ID range in headers
FIXED_ID_RANGE = 200

STUB_PROP = """
<stubProp%s>
    <Type> STRING </Type>
    <Flags> OTHER_CLIENTS </Flags>
</stubProp%s>
"""

STUB_METHOD = """
<stubMethod%s>
    <Args>
        <s> STRING </s>
    </Args>
</stubMethod%s>
"""

TEST_PROPS = """
<oneByteHeaderProp>
    <Type> STRING </Type>
    <Flags> OTHER_CLIENTS </Flags>
    <VariableLengthHeaderSize> 1 </VariableLengthHeaderSize>
</oneByteHeaderProp>
<twoByteHeaderProp>
    <Type> STRING </Type>
    <Flags> OTHER_CLIENTS </Flags>
    <VariableLengthHeaderSize> 2 </VariableLengthHeaderSize>
</twoByteHeaderProp>
"""

TEST_METHODS = """
<oneByteHeaderMethod>
    <Args>
		<s> STRING </s>
	</Args>
	<VariableLengthHeaderSize> 1 </VariableLengthHeaderSize>
</oneByteHeaderMethod>
<twoByteHeaderMethod>
    <Args>
		<s> STRING </s>
	</Args>
	<VariableLengthHeaderSize> 2 </VariableLengthHeaderSize>
</twoByteHeaderMethod>
"""

WATCHER_PATHS = [
	"entityTypes/TestEntity/properties/oneByteHeaderProp/oversizeWarnLevel",
	"entityTypes/TestEntity/properties/twoByteHeaderProp/oversizeWarnLevel",
	"entityTypes/TestEntity/methods/clientMethods/oneByteHeaderMethod/oversizeWarnLevel",
	"entityTypes/TestEntity/methods/clientMethods/twoByteHeaderMethod/oversizeWarnLevel",
	]


LOG_PATTERN = "MemberDescription::checkForOversizeLength"
STACK_PATTERN = "Python stack trace"

class VariableLengthHeaderSizeTest( TestCase ):


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )

		self.cc.mangleResTreeFile(
				"scripts/entity_defs/TestEntity.def", self.addTestProps )

		self.cc.start()

		# Add a bot
		self.cc.startProc( "bots", 1 )
		self.cc.bots.add( 1 )

		# Stop the bot so TestEntity below remains in the AoI
		snippet = """
		bot = BigWorld.bots.values()[0]
		bot.autoMove = False
		srvtest.finish( bot.id )
		"""
		botID = self.cc.sendAndCallOnApp( "bots", None, snippet )

		# Create TestEntity within the bot's AoI
		snippet = """
		bot = BigWorld.entities[%s]
		entity = BigWorld.createEntity(
			"TestEntity", bot.spaceID, bot.position, bot.direction )
		srvtest.finish( entity.id )
		""" % botID
		self.entityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.sendValue = ord( 'a' )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def addTestProps( self, input, output ):
		"""
		Adds test methods and properties
		"""
		properties = ""
		methods = ""

		for i in xrange( FIXED_ID_RANGE ):
			properties += STUB_PROP % (i, i)
			methods += STUB_METHOD % (i, i)

		properties += TEST_PROPS
		methods += TEST_METHODS

		for line in input.readlines():
			output.write( line )
			if line.strip() == "<Properties>":
				output.write( properties )
			elif line.strip() == "<ClientMethods>":
				output.write( methods )


	def sendVarLenMembers( self, warnLevel ):
		"""
		This methods calls snippets on the CellApp that trigger sending
		of the variable length properties and methods to a client entity.

		@return	Tuple (log_count, py_stack_count, py_expcetion_count)
		"""

		# Set warn level
		for path in WATCHER_PATHS:
			self.cc.setWatcher( path, warnLevel, "cellapp", 1 )

		# Generate snippets
		snippet = """
		BigWorld.entities[%s].%%s
		srvtest.finish()
		""" % self.entityID

		# Must be different otherwise property is not updated to client
		sendChar = chr( self.sendValue )
		self.sendValue += 1 

		snippets = [ 
			snippet % ("oneByteHeaderProp = '%s'*300" % sendChar),
			snippet % ("twoByteHeaderProp = '%s'*300" % sendChar),
			snippet % ("allClients.oneByteHeaderMethod( '%s'*300 )" % sendChar),
			snippet % ("allClients.twoByteHeaderMethod( '%s'*300 )" % sendChar)]

		exceptions = []

		# Invoke sending of var length properties and methods
		for snippet in snippets:
			try:
				self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
			except ClusterControllerError, e:
				exceptions.append( e )

		logs = locallog.grepLastServerLog( LOG_PATTERN ).split( "\n" )
		stacks = locallog.grepLastServerLog( STACK_PATTERN ).split( "\n" )

		logs = filter( lambda line: line, logs )
		stacks = filter( lambda line: line, stacks )

		return len( logs ), len( stacks ), len( exceptions )



	def runTest( self ):

		# Check default WarnLevel is "log"
		for path in WATCHER_PATHS:
			warnLevel = self.cc.getWatcherValue( path, "cellapp", 1 )
			self.assertEqual( warnLevel, "log" )

		# Check WarnLevel "none"
		logs, stacks, exceptions = self.sendVarLenMembers( "none" )
		self.assertEqual( logs, 0 )
		self.assertEqual( stacks, 0 )
		self.assertEqual( exceptions, 0 )

		# Check WarnLevel "log": +2 warnings
		logs, stacks, exceptions = self.sendVarLenMembers( "log" )
		self.assertEqual( logs, 3 )
		self.assertEqual( stacks, 0 )
		self.assertEqual( exceptions, 0 )

		# Check WarnLevel "callstack": +2 warnings, +2 callstacks
		logs, stacks, exceptions = self.sendVarLenMembers( "callstack" )
		self.assertEqual( logs, 6 )
		self.assertEqual( stacks, 3 )
		self.assertEqual( exceptions, 0 )

		# Check WarnLevel "exception": +2 warnings, +2 exceptions
		logs, stacks, exceptions = self.sendVarLenMembers( "exception" )
		self.assertEqual( logs, 9 )
		self.assertEqual( stacks, 3 )
		self.assertEqual( exceptions, 3 )
