import optparse
import os
import pprint
import re
import sys

from jinja2 import Template, Environment, FileSystemLoader

OUTPUT_DIRECTORY = "GeneratedSource"

GENERATE_TEMPLATES = True
TEMPLATE_EXTENSION_NAME = "%sGameLogic"

def includePathJoin( *args ):
	return "/".join( args )

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
		result.append( "%s const %s & %s" % \
				(padding, convertToCType( arg[1] ), argName ) )
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

	type_name = convertToCType( remainder )

	if size != 0:
		return "BW::SequenceValueType< %s, %s >" % (type_name, size)
	else:
		return "BW::SequenceValueType< %s >" % (type_name)

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
		cType = convertToCType( memberType )
		members.append( dict( type = cType, name = member ) )

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
		typeName = 'BW::ValueOrNull< %s >' % typeName

	existingFixedDictTypes[ description ] = typeName

	return typeName


def convertFixedDict( remainder ):
	try:
		return existingFixedDictTypes[ remainder ]
	except KeyError:
		pass

	return generateFixedDictType( remainder )


DATA_TYPES = dict(
	FLOAT32 = "float",
	FLOAT64 = "double",
	INT8 = "BW::int8",
	INT16 = "BW::int16",
	INT32 = "BW::int32",
	INT64 = "BW::int64",
	UINT8 = "BW::uint8",
	UINT16 = "BW::uint16",
	UINT32 = "BW::uint32",
	UINT64 = "BW::uint64",
	STRING = "BW::string",
	BLOB = "BW::string",
	UNICODE_STRING = "BW::string",
	UDO_REF = "BW::UniqueID",
	VECTOR2 = "BW::Vector2",
	VECTOR3 = "BW::Vector3",
	VECTOR4 = "BW::Vector4",
	ARRAY = convertArray,
	TUPLE = convertArray,
	FIXED_DICT = convertFixedDict )


@jinjaFilter( "ctype" )
def convertToCType( typeName ):
	parts = typeName.split( ' ', 1 )

	try:
		entry = DATA_TYPES[ parts[0] ]
	except KeyError:
		print "ERROR: Unknown type '%s'" % typeName
		return typeName

	if callable( entry ):
		entry = entry( parts[1] )

	return entry


class Generator( object ):
	"""
	This class generates the source files.
	"""
	def __init__( self, entityDescriptions, constants,
			outputDirectory, extensionsPath, entityPath,
			entityTemplateSourceExtension ):
		self.entityDescriptions = \
			[e for e in entityDescriptions if e["canBeOnClient"]]
		self.constants = constants
		self.digest = constants[ "digest" ]
		self.outputDirectory = outputDirectory

		self.extensionsPath = extensionsPath
		self.entityPath = entityPath
		self.entityMailBoxPath = includePathJoin( self.entityPath, 
			"MailBoxes" )

		self.entityTemplateSourceExtension = entityTemplateSourceExtension
		self.shouldCheckDefsDigest = True

		self.sourceFiles = []
		self.headerFiles = []

	def generate( self ):
		if self.shouldCheckDefsDigest and self.defsDigestMatches():
			if not self.isQuiet:
				print "Defs digest matches: not regenerating"
			return

		self.removeExistingGeneratedSources()

		for entity in self.entityDescriptions:
			self.generateFilesFor( entity )

		self.generateGlobalFiles()

		self.generateMakefile()
		self.generateCMakeInclude()

	def defsDigestMatches( self ):
		defsDigestPath = includePathJoin( self.outputDirectory, 
			"DefsDigest." + self.entityTemplateSourceExtension )

		if not os.path.exists( defsDigestPath ):
			return False

		with open( defsDigestPath ) as defsDigestFile:
			defsDigestContents = defsDigestFile.read()

		return self.digest in defsDigestContents

	def removeExistingGeneratedSources( self ):
		for filename in os.listdir( self.outputDirectory ):
			if filename.endswith( '.' + 
						self.entityTemplateSourceExtension ) or \
					filename.endswith( '.hpp' ):
				os.unlink( includePathJoin( self.outputDirectory, filename ) )

	def generateFilesFor( self, entity ):
		sys.stderr.write( "Generating for %s\n" % entity[ "name" ] )

		self.generateExtension( entity )

		self.generateModel( entity )


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

		filename = includePathJoin( self.entityMailBoxPath, 
			"%s_%sMB" % (className, component) )

		self.render_hpp_file( filename,
				"EntityMailBoxTemplate.hpp",
				dict( entity = entity,
					methods = methods,
					component = component,
					isForBase = (component == "Base"),
					className = className,
					entityPath = self.entityPath,
					entityMailBoxPath = self.entityMailBoxPath,
					extensionsPath = self.extensionsPath ) )
		self.render_cpp_file( filename,
				"EntityMailBoxTemplate.cpp",
				dict( entity = entity,
					methods = methods,
					component = component,
					isForBase = (component == "Base"),
					className = className,
					entityPath = self.entityPath,
					entityMailBoxPath = self.entityMailBoxPath,
					extensionsPath = self.extensionsPath ) )

		return True


	def generateExtension( self, entity ):
		className = entity[ "name" ] + "Extension"

		self.render_hpp_file( includePathJoin( self.extensionsPath, className ),
				"EntityExtensionTemplate.hpp",
				dict( entity = entity,
					className = className,
					entityPath = self.entityPath,
					extensionsPath = self.extensionsPath ) )

		if GENERATE_TEMPLATES:
			className = TEMPLATE_EXTENSION_NAME % entity[ "name" ]

			values = dict( entity = entity,
						className = className,
						extensionsPath = self.extensionsPath,
						entityTemplateSourceExtension =
							self.entityTemplateSourceExtension )

			self.render_to_file( includePathJoin( "templates", 
						self.extensionsPath, "%s.%s" % 
						(className, self.entityTemplateSourceExtension) ),
					"EntityExtensionImpl.cpp",
					values )

			self.render_to_file( includePathJoin( "templates", 
						self.extensionsPath, "%s.hpp" % className ),
					"EntityExtensionImpl.hpp",
					values )


	def generateModel( self, entity ):
		values = dict( self.__dict__ )
		values[ "entity" ] = entity

		values[ "hasBaseMailbox" ] = self.generateBaseMailboxFor( entity )
		values[ "hasCellMailbox" ] = self.generateCellMailboxFor( entity )

		fileHead = includePathJoin( self.entityPath, entity[ 'name' ] )

		self.render_hpp_file( fileHead, "EntityTemplate.hpp", values )
		self.render_cpp_file( fileHead, "EntityTemplate.cpp", values )


	def generateGlobalFiles( self ):
		self.generateGlobalTypes()
		self.generateEntityFactory()
		self.generateEntityExtensionFactory()
		self.generateDigest()


	def generateDigest( self ):
		self.render_hpp_file( "DefsDigest", "DefsDigest.hpp", self.__dict__ )
		self.render_cpp_file( "DefsDigest", "DefsDigest.cpp", self.__dict__ )


	def generateGlobalTypes( self ):
		values = dict( fixedDictTypes = fixedDictTypes, 
					extensionsPath = self.extensionsPath )
		self.render_hpp_file( "GeneratedTypes", "GeneratedTypes.hpp", values )
		self.render_cpp_file( "GeneratedTypes", "GeneratedTypes.cpp", values )


	def generateMakefile( self ):
		self.render_to_file( "Makefile.rules", "Makefile.rules",
				dict( sourceFiles = self.sourceFiles ) )


	def generateCMakeInclude( self ):
		values = dict( sourceFiles = self.sourceFiles,
					headerFiles = self.headerFiles )
		self.render_to_file( "GeneratedSource.cmake", "GeneratedSource.cmake",
			values )


	def render_to_file( self, filename, template_name, dictionary ):
		fullPath = self.pathFor( filename )
		dirname = os.path.dirname( fullPath )

		if dirname and not os.path.exists( dirname ):
			os.makedirs( dirname )

		f = open( fullPath, 'w' )

		f.write( render_to_string( template_name, dictionary ) )

	def render_hpp_file( self, filename, *args ):
		self.headerFiles.append( filename )

		return self.render_to_file( filename + ".hpp", *args )

	def render_cpp_file( self, filename, *args ):
		self.sourceFiles.append( filename )

		return self.render_to_file(
				"%s.%s" % (filename, self.entityTemplateSourceExtension), 
				*args )

	def generateEntityFactory( self ):
		values = self.__dict__
		self.render_hpp_file( "EntityFactory", "EntityFactory.hpp", values )
		self.render_cpp_file( "EntityFactory", "EntityFactory.cpp", values )


	def generateEntityExtensionFactory( self ):
		self.render_hpp_file( "EntityExtensionFactory",
			"EntityExtensionFactory.hpp", self.__dict__ )

		if GENERATE_TEMPLATES:
			className = (TEMPLATE_EXTENSION_NAME % "Entity") + "Factory"
			values = dict( self.__dict__ )
			values[ "className" ] = className
			values[ "templateExtensionName" ] = TEMPLATE_EXTENSION_NAME

			self.render_to_file( "templates/" + className + ".hpp",
				"EntityExtensionFactoryImpl.hpp", values )
			self.render_to_file( "templates/" + className + "." + 
					self.entityTemplateSourceExtension,
				"EntityExtensionFactoryImpl.cpp", values )


	def pathFor( self, filename ):
		return includePathJoin( self.outputDirectory, filename )


def createOptionParser():
	parser = optparse.OptionParser()
	parser.add_option( "-o", "--output",
			dest = "outputDirectory",
			help = "Directory to output generated files. Defaults to "
				"\"%default\".",
			default = OUTPUT_DIRECTORY, metavar = "FILE" )

	parser.add_option( "--extensions-path", 
			dest = "extensionsPath",
			help = "This indicates the directory of where to find the "
				"generated sources, and is used for generating the #include "
				"lines for generated headers. Defaults to \"%default\".",
			default = 'EntityExtensions',
			metavar="HEADERPATH" )

	parser.add_option( "--entity-path",
			dest = "entityPath",
			help = "This indicates the directory of where to find your entity "
				"class header files, and is used for generating the #include "
				"lines for entity header files. Defaults to \"%default\".",
			default = 'Entities',
			metavar = "HEADERPATH" )

	parser.add_option( "--entity-template-source-extension",
			dest = "entityTemplateSourceExtension",
			help = "Specifies the extension suffix given to generated entity "
				"stub and template C++ source files. Defaults to \"%default\".",
			default = "cpp",
			metavar = "EXT" )

	parser.add_option( "--no-defs-digest-check",
			dest = "shouldCheckDefsDigest",
			help = "Whether to skip the check for matching defs digests (by "
				"default generation is skipped if defs digest match).",
			action = "store_false",
			default = True )

	parser.add_option( "--quiet",
			dest = "isQuiet",
			help = "Specifies whether to be quieter with log output",
			action = "store_true",
			default = False )

	return parser


def process( description ):
	entityDescriptions = description[ "entityTypes" ]

	parser = createOptionParser()
	(options, args) = parser.parse_args()

	if not os.path.exists( options.outputDirectory ):
		os.makedirs( options.outputDirectory )

	generator = Generator( entityDescriptions, description[ "constants" ],
			options.outputDirectory, 
			options.extensionsPath,
			options.entityPath,
			options.entityTemplateSourceExtension )

	generator.shouldCheckDefsDigest = options.shouldCheckDefsDigest
	generator.isQuiet = options.isQuiet

	generator.generate()

	return True

def help():
	parser = createOptionParser()
	sys.stdout.write( "\nScript " )
	print parser.format_option_help( parser.formatter )

	return True

# ProcessDefs.py
