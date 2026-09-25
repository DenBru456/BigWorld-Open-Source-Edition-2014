import optparse
import os
import pprint
import re
import sys

from jinja2 import Template, Environment, FileSystemLoader
from array import array

OUTPUT_DIRECTORY = "GeneratedCSharp"
BASE_EXTENSION_CLASS = "IEntityExtension"
GENERATED_NAMESPACE = "BW"

templateEnv = Environment( 
	loader = FileSystemLoader( os.path.join( os.path.dirname( __file__ ), 
		"templates" ) ) )

existingFixedDictTypes = {}
fixedDictTypes = []
anonymousFixedDictNextIndex = 0

def jinjaFilter( name ):
	def wrapper( f ):
		templateEnv.filters[name] = f
		return f
	return wrapper


@jinjaFilter( "ljust" )
def filter_ljust( s, width ):
	return str( s ).ljust( int( width ) )


@jinjaFilter( "rjust" )
def filter_rjust( s, width ):
	return str( s ).rjust( int( width ) )


@jinjaFilter( "methodDeclaration" )
def filter_methodDeclaration( method, classLabel = "" ):
	result = []

	if classLabel:
		classLabel += "::"

	result.append( "void %s%s(" % (classLabel, method[ "name" ]) )

	padding = ""
	for i, arg in enumerate( method[ "args" ] ):
		argName = arg[0]
		if not argName:
			argName = "arg%d" % i
		
		result.append( "%s %s %s" % \
				(padding, convertToCSType( arg[1] ), argName ) )
		padding = ",\n                "

	result.append( " )" )

	return ''.join( result )


def render_to_string( template_name, dictionary=None ):
	template = templateEnv.get_template( template_name )
	return template.render( **dictionary )


def convertArrayWithSize( remainder ):
	first, remainder = remainder.split( ' ', 1 )

	size = 0

	while first != 'of':
		if first == "size":
			first, remainder = remainder.split( ' ', 1 )
			size = int( first )

		first, remainder = remainder.split( ' ', 1 )

	remainder = remainder[1:-1]

	type = convertToCSType( remainder )
	
	if size != 0:
		return "FixedSizeSequence< " + type + " >", size
	else:
		if type != "string":
			return "StreamList< " + type + " >", 0
		else:
			return "StringList", 0

def convertArray( description ):
	return convertArrayWithSize( description )

def splitFixedDictMember( rest ):
	count = 0
	start = 0

	for i, c in enumerate( rest ):
		if c == '(':
			if count == 0:
				start = i
			count += 1
		elif c == ')':
			count -= 1
			if count == 0:
				return rest[ start+1: i ], rest[ i+1: ]


def generateFixedDictType( description ):
	global anonymousFixedDictNextIndex

	matches = re.match( r'(?:name:(\w+))?' + 
			r'(?: *\[Implemented by [^]]+\])?' + 
			r'( *\[None Allowed\])? *'+ 
			r'props (.*)', 
		description )

	if not matches:
		raise ValueError, "Invalid description %r" % description

	typeName, allowNone, rest = matches.groups()

	isDone = False
	fixedDict = {}
	members = []
	while not isDone:
		member, rest = rest.split( ':', 1 )
		memberType, rest = splitFixedDictMember( rest )
		isDone = not rest.startswith( ',' )
		rest = rest[1:].strip()
		type, shouldRef, arraySize = convertToCSType( memberType, True )
		members.append( dict( type = type, 
							arraySize = arraySize,
							name = member, 
							shouldRef = shouldRef ) )

	fixedDict[ "members" ] = members


	if not typeName:
		typeName = "FixedDict%d" % anonymousFixedDictNextIndex
		anonymousFixedDictNextIndex += 1

		print "WARNING: FIXED_DICT type is not named, name set to %s: %r" % \
			(typeName, description)

	fixedDict[ "name" ] = typeName

	fixedDictTypes.append( fixedDict )

	if allowNone:
		# Wrap the generated type
		typeName = 'ValueOrNull< %s >' % typeName
	
	existingFixedDictTypes[ description ] = typeName

	return typeName

	
def convertFixedDict( remainder ):
	try:
		return existingFixedDictTypes[ remainder ], 0
	except KeyError:
		pass

	return generateFixedDictType( remainder ), 0

# In a tuple, first value is a C# type and the second is
# the type of referencing when reading from the stream:
# True = 'ref' keyword needed, False = not needed
DATA_TYPES = dict(
	FLOAT32 = ( "float", True ),
	FLOAT64 = ( "double", True ),
	INT8 = ( "sbyte", True ),
	INT16 = ( "short", True ),
	INT32 = ( "int", True ),
	INT64 = ( "long", True ),
	UINT8 = ( "byte", True ),
	UINT16 = ( "ushort", True ),
	UINT32 = ( "uint", True ),
	UINT64 = ( "ulong", True ),
	STRING = ( "string", True ),
	BLOB = ( "Blob", True ),
	UNICODE_STRING = ( "string", True ),
	UDO_REF = ( "UniqueID", True ),
	VECTOR2 = ( "Vector2", True ),
	VECTOR3 = ( "Vector3", True ),
	VECTOR4 = ( "Vector4", True ),
	ARRAY = ( convertArray, False ),
	TUPLE = ( convertArray, False ),
	FIXED_DICT = ( convertFixedDict, False ) )

C_SHARP_KEYWORDS = set( [
	"abstract",
	"event",
	"new",
	"struct",
	"as",
	"explicit",
	"null",
	"switch",
	"base",
	"extern",
	"object",
	"this",
	"bool",
	"false",
	"operator",
	"throw",
	"break",
	"finally",
	"out",
	"true",
	"byte",
	"fixed",
	"override",
	"try",
	"case",
	"float",
	"params",
	"typeof",
	"catch",
	"for",
	"private",
	"uint",
	"char",
	"foreach",
	"protected",
	"ulong",
	"checked",
	"goto",
	"public",
	"unchecked",
	"class",
	"if",
	"readonly",
	"unsafe",
	"const",
	"implicit",
	"ref",
	"ushort",
	"continue",
	"in",
	"return",
	"using",
	"decimal",
	"int",
	"sbyte",
	"virtual",
	"default",
	"interface",
	"sealed",
	"volatile",
	"delegate",
	"internal",
	"short",
	"void",
	"do",
	"is",
	"sizeof",
	"while",
	"double",
	"lock",
	"stackalloc",
	"else",
	"long",
	"static", 	 
	"enum",
	"namespace",
	"string" ] )
	
@jinjaFilter( "ctype" )
def convertToCSType( typeName, withProps = False ):
	parts = typeName.split( ' ', 1 )

	try:
		entry, shouldRef = DATA_TYPES[ parts[0] ]
	except KeyError:
		print "ERROR: Unknown type '%s'" % typeName
		if not withProps:
			return typeName
		else:
			return typeName, shouldRef, 0

	size = 0
	if callable( entry ):
		entry, size = entry( parts[1] )

	if not withProps:
		return entry
	else:
		return entry, shouldRef, size

@jinjaFilter( "cshouldRef" )
def filterShouldRef( typeName ):
	entry, shouldRef, size = convertToCSType( typeName, True )
	return shouldRef

@jinjaFilter( "carraySize" )
def filterFixedArraySize( typeName ):
	entry, shouldRef, size = convertToCSType( typeName, True )
	return size

	
def writePropertyMembers( f, properties ):
	for property in properties:
		if property[ "isClientServerData" ]:
			propType = convertToCSType( property[ "type" ] ) + " &"
			propName = property[ "name" ]
			methodProto = propName + "() const"
			f.write( "\tconst %-15s %-20s { return %s_; }\n" % \
					(propType, methodProto, propName) )

	f.write( "\nprivate:\n" )
	for property in properties:
		if property[ "isClientServerData" ]:
			f.write( "\t%-20s %s_;\n" % \
					(convertToCSType( property[ "type" ] ), property[ "name" ]) )


def writePropertyAccessors( f, properties ):
	for property in properties:
		f.write( "@property (nonatomic, readonly) id /*%(type)s*/ %(name)s;\n" %
				property )


def writeMethod( f, method, isVirtual = False ):
	if isVirtual:
		virtualPrefix = "virtual "
		virtualSuffix = " = 0"
	else:
		virtualPrefix = ""
		virtualSuffix = ""

	if method[ "isExposed" ]:
		f.write( "\t%svoid %s(" % (virtualPrefix, method[ "name" ]) )
		padding = ""
		for i, arg in enumerate( method[ "args" ] ):
			argName = arg[0]
			if not argName:
				argName = "arg%d" % i
			f.write( "%s const %s & %s" % \
					(padding, convertToCSType( arg[1] ), argName )[0] )
			padding = ",\n                "
		f.write( " )%s;\n" % virtualSuffix )


def writeMethods( f, methods, isVirtual = False ):
	for method in methods:
		writeMethod( f, method, isVirtual )


def writeMailbox( f, methods, component, entityName ):
	if methods:
		f.write( """

// -----------------------------------------------------------------------------
// This describes the interface to the %s part of the entity.
// -----------------------------------------------------------------------------

class %s_%sEntity : public RemoteEntity
{
public:
""" % \
	(component, entityName, component) )

		writeMethods( f, methods )
		f.write( "};\n" )


class Generator( object ):
	"""
	This class generates the source files.
	"""
	def __init__( self, entityDescriptions, constants,
			outputDirectory, baseExtensionClass,
			entityTemplateSourceExtension, 
			generatedNamespace ):
		self.entityDescriptions = \
			[e for e in entityDescriptions if e["canBeOnClient"]]
		self.constants = constants
		self.digest = constants[ "digest" ]
		self.outputDirectory = outputDirectory
		self.baseExtensionClass = baseExtensionClass
		self.generatedNamespace = generatedNamespace
		
		self.entityTemplateSourceExtension = entityTemplateSourceExtension
		self.shouldCheckDefsDigest = True

		for entity in self.entityDescriptions:
			for property in entity[ "clientProperties" ]:
				if property[ "name" ] in C_SHARP_KEYWORDS:
					property[ "name" ] = "prop_" + property.name
			for method in entity[ "clientMethods" ]:
				if method[ "name" ] in C_SHARP_KEYWORDS:
					method[ "name" ] = "call_" + method[ "name" ]
				argsLen = len( method[ "args" ] )
				for argIdx in range( argsLen ):
					arg = method[ "args" ][ argIdx ]
					if arg[ 0 ] in C_SHARP_KEYWORDS:
						arg = ( "arg_" + arg[ 0 ], ) + arg[ 1: ] 
						tempList = list( method[ "args" ] )
						tempList[ argIdx ] = arg
						method[ "args" ] = tuple( tempList )

	def generate( self ):
		if self.shouldCheckDefsDigest and self.defsDigestMatches():
			print "Defs digest matches: not regenerating"
			return

		self.removeExistingGeneratedSources()

		for entity in self.entityDescriptions:
			self.generateFilesFor( entity )

		self.generateGlobalFiles()

	def defsDigestMatches( self ):
		defsDigestPath = os.path.join( self.outputDirectory, "DefsDigest.cs" )

		if not os.path.exists( defsDigestPath ):
			return False

		with open( defsDigestPath ) as defsDigestFile:
			defsDigestContents = defsDigestFile.read()

		return self.digest in defsDigestContents

	def removeExistingGeneratedSources( self ):
		for filename in os.listdir( self.outputDirectory ):
			if filename.endswith( '.cs' ):
				os.unlink( os.path.join( self.outputDirectory, filename ) )

	def generateFilesFor( self, entity ):
		sys.stderr.write( "Generating for %s\n" % entity[ "name" ] )

		self.generateEntities( entity )

		self.generateEntityExtensions( entity )

	def generateBaseMailboxFor( self, entity ):
		return self.generateMailboxFor( entity, entity[ "baseMethods" ], 
			"Base" )


	def generateCellMailboxFor( self, entity ):
		return self.generateMailboxFor( entity, entity[ "cellMethods" ], 
			"Cell" )


	def generateMailboxFor( self, entity, methods, component ):
		if not methods or not [m for m in methods if m[ "isExposed" ]]:
			return False

		className = entity[ "name" ]

		fileName = "Entities/MailBoxes/" + \
				"%s_%sMailBox.cs" % (className, component)
		self.render_to_file( fileName,
				"EntityMailBoxTemplate.cs",
				dict( entity = entity,
					methods = methods,
					component = component,
					isForBase = (component == "Base"),
					className = className ) )

		return True


	def generateEntities( self, entity ):
		className = entity[ "name" ]

		hasBaseMailbox = self.generateBaseMailboxFor( entity )
		hasCellMailbox = self.generateCellMailboxFor( entity )

		fileName = "Entities/" + entity[ 'name' ] + ".cs"
		self.render_to_file( fileName,
				"EntityTemplate.cs",
				dict( entity = entity,
					className = className,
					extensionName = "I" + className + "Extension",
					hasBaseMailbox = hasBaseMailbox,
					hasCellMailbox = hasCellMailbox ) )

	def generateEntityExtensions( self, entity ):
		values = dict( self.__dict__ )
		values.update( entity )
		className = entity[ "name" ] + "Extension"
		values[ "className" ] = className
		values[ "parentName" ] = entity[ "name" ]
		values[ "baseExtensionClass" ] = self.baseExtensionClass

		fileName = "EntityExtensions/" + className + ".cs"
		self.render_to_file( fileName, "EntityExtensionTemplate.cs", values )

	def generateGlobalFiles( self ):
		self.generateGlobalTypes()
		self.generateEntityFactory()
		self.generateEntityExtensionFactory()
		self.generateDigest()


	def generateDigest( self ):
		self.render_to_file( "DefsDigest.cs", "DefsDigest.cs",
			self.__dict__ )

	def generateGlobalTypes( self ):
		self.render_to_file( "GeneratedTypes.cs",
				"GeneratedTypes.cs", 
				dict( fixedDictTypes = fixedDictTypes ) )

	def render_to_file( self, filename, template_name, dictionary ):
		fullPath = self.pathFor( filename )
		dirname = os.path.dirname( fullPath )

		dictionary[ "generatedNamespace" ] = self.generatedNamespace
		
		if dirname and not os.path.exists( dirname ):
			os.makedirs( dirname )

		f = open( fullPath, 'w' )

		f.write( render_to_string( template_name, dictionary ) )


	def generateEntityFactory( self ):
		values = dict( self.__dict__ )
		self.render_to_file( "EntityFactory." + self.entityTemplateSourceExtension,
			"EntityFactory.cs", values )

	def generateEntityExtensionFactory( self ):
		values = dict( self.__dict__ )
		self.render_to_file( "EntityExtensionFactory.cs", 
								"EntityExtensionFactory.cs", values )

	def pathFor( self, filename ):
		return os.path.join( self.outputDirectory, filename )


def createOptionParser():
	parser = optparse.OptionParser()
	parser.add_option( "-o", "--output",
			dest = "outputDirectory",
			help = "Directory to output generated files. Defaults to "
				"\"%default\".",
			default = OUTPUT_DIRECTORY, metavar = "FILE" )

	parser.add_option( "-b", "--base-extension-class", 
			dest = "baseExtensionClass",
			help = "The base class for generated entity classes. Defaults to "
				"\"%default\".",
			default = BASE_EXTENSION_CLASS, metavar = "CLASS_NAME" )

	parser.add_option( "--entity-template-source-extension",
			dest = "entityTemplateSourceExtension",
			help = "Specifies the extension suffix given to generated entity "
				"stub and template CS source files. Defaults to \"%default\".",
			default = "cs",
			metavar = "EXT" )

	parser.add_option( "--generated-namespace",
			dest = "generatedNamespace",
			help = "Specifies the namespace for generated classes/entities. Defaults to \"%default\".",
			default = GENERATED_NAMESPACE,
			metavar = "NAMESPACE" )

	parser.add_option( "--no-defs-digest-check",
			dest = "shouldCheckDefsDigest",
			help = "Whether to skip the check for matching defs digests (by "
				"default generation is skipped if defs digest match).",
			action = "store_false",
			default = True )

	return parser


def process( description ):
	entityDescriptions = description[ "entityTypes" ]

	parser = createOptionParser()
	(options, args) = parser.parse_args()

	if not os.path.exists( options.outputDirectory ):
		os.makedirs( options.outputDirectory )

	generator = Generator( entityDescriptions, description[ "constants" ],
			options.outputDirectory, 
			options.baseExtensionClass, 
			options.entityTemplateSourceExtension,
			options.generatedNamespace )

	generator.shouldCheckDefsDigest = options.shouldCheckDefsDigest

	generator.generate()

	return True

def help():
	parser = createOptionParser()
	sys.stdout.write( "\nScript " )
	print parser.format_option_help( parser.formatter )

	return True

# ProcessDefs.py
