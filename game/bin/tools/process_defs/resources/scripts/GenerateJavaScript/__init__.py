import logging
import optparse
import os
import re
import sys

from jinja2 import Template, Environment, FileSystemLoader

OUTPUT_DIRECTORY = "GeneratedSource"

GENERATE_TEMPLATES = False
TEMPLATE_EXTENSION_NAME = "%sGameLogic"

def includePathJoin( *args ):
	return "/".join( args )

templateEnv = Environment( 
	loader = FileSystemLoader( os.path.join( os.path.dirname( __file__ ), 
		"templates" ) ) )

fixedDictTypes = set()
arrayTypes = set()
allowNoneTypes = set()
anonymousFixedDictNextIndex = 0


DATA_TYPES = dict(
	FLOAT32 		= "float",
	FLOAT64 		= "double",
	INT8 			= "BW::int8",
	INT16			= "BW::int16",
	INT32			= "BW::int32",
	INT64			= "BW::int64",
	UINT8			= "BW::uint8",
	UINT16			= "BW::uint16",
	UINT32 			= "BW::uint32",
	UINT64 			= "BW::uint64",
	STRING 			= "BW::string",
	BLOB 			= "BW::string",
	UNICODE_STRING 	= "BW::string",
	UDO_REF 		= "BW::UniqueID",
	VECTOR2 		= "BW::Vector2",
	VECTOR3 		= "BW::Vector3",
	VECTOR4 		= "BW::Vector4" )


def dataType( name ):
	def wrapper( f ):
		DATA_TYPES[name] = f
		return f
	return wrapper

def jinjaFilter( name ):
	def wrapper( f ):
		templateEnv.filters[name] = f
		return f
	return wrapper


@jinjaFilter( "entityToTemplateExtension" )
def filter_entityToTemplateExtension( s ):
	return TEMPLATE_EXTENSION_NAME % s

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

@dataType( "ARRAY" )
@dataType( "TUPLE" )
def convertArray( desc ):
	typeName, remainder = desc.split( ' ', 1 )
	size = None

	first, remainder = remainder.split( ' ', 1 )
	while first != 'of':
		if first == "size":
			first, remainder = remainder.split( ' ', 1 )
			size = int( first )

		first, remainder = remainder.split( ' ', 1 )

	elementDesc = remainder[1:-1]
	elementType = DataType.get( elementDesc )

	arrayType = ArrayType( elementType, desc, size )
	arrayTypes.add( arrayType )
	return arrayType


@dataType( "FIXED_DICT" )
def convertFixedDict( description ):
	matches = re.match( r'FIXED_DICT (?:name:(\w+))?' + 
			r'(?: *\[Implemented by [^]]+\])?' + 
			r'( *\[None Allowed\])? *'+ 
			r'props (.*)', 
		description )

	if not matches:
		raise ValueError, "Invalid description %r" % description

	typeName, allowNone, rest = matches.groups()

	if not typeName:
		global anonymousFixedDictNextIndex

		typeName = "FixedDict%03d" % anonymousFixedDictNextIndex
		anonymousFixedDictNextIndex += 1

		logging.warning( "FIXED_DICT type is not named, "
				"name set to %s: %r", 
			typeName, description )

	dataType = FixedDictType( typeName, description )

	isDone = False
	while not isDone:
		memberName, rest = rest.split( ':', 1 )
		memberDesc, rest = splitFixedDictMember( rest )
		isDone = not rest.startswith( ',' )
		rest = rest[1:].strip()

		memberType = DataType.get( memberDesc )
		dataType.addMember( memberName, memberType )

	fixedDictTypes.add( dataType )

	if allowNone:
		# Wrap the generated type
		dataType = AllowNoneType( dataType )
		allowNoneTypes.add( dataType )

	return dataType 


class DataType( object ):
	dataTypes = {}

	def __init__( self, desc ):
		self.desc = desc

		if desc in self.dataTypes:
			raise ValueError( "Duplicate type for '%s'" % desc )
		self.dataTypes[desc] = self


	def childTypes( self ):
		return []

	def toCType( self ):
		return DATA_TYPES[self.desc]

	@classmethod
	def get( klass, desc ):
		if desc in klass.dataTypes:
			return klass.dataTypes[desc]
		else:
			return klass.createDataType( desc )

	@property
	def dependantTypes( self ):
		seenTypes = set()
		for child in self.childTypes():
			for descendant in child.dependantTypes:
				if not descendant in seenTypes:
					seenTypes.add( descendant )
					yield descendant
			if isinstance( child, FixedDictType ) and not child in seenTypes:
				seenTypes.add( child )
				yield child


	@classmethod
	def createDataType( klass, desc ):
		parts = desc.split( ' ', 1 )
		try:
			entry = DATA_TYPES[ parts[0] ]
			if callable( entry ):
				dataType = entry( desc )
			else:
				dataType = DataType( desc )
		except KeyError:
			logging.error( "Unknown type '%s'", desc )
			dataType = UnknownType( desc )

		return dataType


	@classmethod
	def sortedDataTypes( klass ):
		typesLeft = list( klass.dataTypes.items() )
		sortedTypes = []

		while typesLeft:	
			typesToAdd = []
			for i, dataTypeMapping in enumerate( typesLeft ):
				dataTypeName, dataType = dataTypeMapping
				shouldAddToSorted = True

				for childType in dataType.childTypes():
					if not childType in sortedTypes:
						shouldAddToSorted = False

				if shouldAddToSorted:
					typesLeft.pop( i )
					typesToAdd.append( (dataTypeName, dataType) )


			if not typesToAdd:
				raise ValueError( "Circular reference" )
			# Sort on name
			typesToAdd.sort( lambda x, y: cmp( x[0], y[0] ) )
			for name, typeToAdd in typesToAdd:
				sortedTypes.append( typeToAdd )

		return sortedTypes

	def __repr__( self ):
		return "<" + self.__class__.__name__ + ": " + self.desc + ">"


class UnknownType( DataType ):
	def __init__( self, desc ):
		DataType.__init__( self, desc )

	def toCType( self ):
		return "UnknownType< " + self.desc + " >"


class FixedDictType( DataType ):
	def __init__( self, className, desc ):
		self.className = className
		self.members = []
		DataType.__init__( self, desc )

	def addMember( self, memberName, memberType ):
		self.members.append( (memberName, memberType) )

	def childTypes( self ):
		for memberName, memberType in self.members:
			yield memberType

	def toCType( self ):
		return self.className

	def __repr__( self ):
		return self.className


class ArrayType( DataType ):
	def __init__( self, elementType, desc, size ):
		self.elementType = elementType
		self.size = size
		DataType.__init__( self, desc )


	def childTypes( self ):
		return [self.elementType]


	def toCType( self ):
		elementCType = self.elementType.toCType()
		if self.size is not None:
			return "BW::SequenceValueType< {}, {} >".format( 
				elementCType, self.size )
		
		return "BW::SequenceValueType< {} >".format( elementCType )


class AllowNoneType( DataType ):
	def __init__( self, wrappedType ):
		DataType.__init__( self, wrappedType.name )
		self.wrappedType = wrappedType

	def childTypes( self ):
		return self.wrappedType.childTypes()

	def toCType( self ):
		return "ValueOrNull< {} >".format( self.wrappedType.toCType() )


@jinjaFilter( "ctype" )
def convertToCType( typeName ):
	try:
		dataType = DataType.get( typeName )
		return dataType.toCType()
	except KeyError: 
		return "UnknownType /* " + typeName + "*/"


class Generator( object ):
	"""
	This class generates the source files.
	"""
	def __init__( self, entityDescriptions, constants,
			outputDirectoryCPP, outputDirectoryJS, extensionsPath, entityPath,
			entityTemplateSourceExtension ):
		self.entityDescriptions = \
			[e for e in entityDescriptions if e["canBeOnClient"]]
		self.constants = constants
		self.digest = constants[ "digest" ]
		self.outputDirectoryCPP = outputDirectoryCPP
		self.outputDirectoryJS = outputDirectoryJS

		self.extensionsPath = extensionsPath
		self.entityPath = entityPath
		self.entityMailBoxPath = includePathJoin( self.entityPath, 
			"MailBoxes" )

		self.entityTemplateSourceExtension = entityTemplateSourceExtension
		self.shouldCheckDefsDigest = True

		self.sourceFiles = []
		self.headerFiles = []


	def generate( self ):
		# This is done here because the rest of the build process should not
		# depend on this file, so we can safely generate it here without
		# triggering a rebuild.
		self.generateEntityExtensionFactoryJS()

		if self.shouldCheckDefsDigest and \
				self.defsDigestMatches():
			if not self.isQuiet:
				logging.info( "Defs digest matches: not regenerating" )
			return

		self.removeExistingGeneratedSources()

		for entity in self.entityDescriptions:
			entity['hasBaseMailBox'] = self.entityHasBaseMailBox( entity )
			entity['hasCellMailBox'] = self.entityHasCellMailBox( entity )
			self.generateFilesFor( entity )

		self.generateGlobalFiles()

		self.generateMakefile()
		self.generateCMakeInclude()


	def defsDigestMatches( self ):
		defsDigestPath = includePathJoin( self.outputDirectoryCPP,
			"DefsDigest." + self.entityTemplateSourceExtension )

		if not os.path.exists( defsDigestPath ):
			return False

		with open( defsDigestPath ) as defsDigestFile:
			defsDigestContents = defsDigestFile.read()

		return self.digest in defsDigestContents


	def removeExistingGeneratedSources( self ):
		for filename in os.listdir( self.outputDirectoryCPP ):
			if filename.endswith( '.' + 
						self.entityTemplateSourceExtension ) or \
					filename.endswith( '.hpp' ):
				os.unlink( os.path.join( self.outputDirectoryCPP, filename ) )


	def generateFilesFor( self, entity ):
		logging.info( "Generating for %s\n" % entity[ "name" ] )

		self.generateExtension( entity )

		self.generateModel( entity )


	def generateBaseMailBoxFor( self, entity ):
		return self.generateMailBoxFor( entity, entity[ "baseMethods" ], 
			"Base" )


	def generateCellMailBoxFor( self, entity ):
		return self.generateMailBoxFor( entity, entity[ "cellMethods" ], 
			"Cell" )


	@staticmethod
	def entityHasBaseMailBox( entity ):
		methods = entity['baseMethods']
		return bool( methods and [m for m in methods if m[ "isExposed" ]] )

	@staticmethod
	def entityHasCellMailBox( entity ):
		methods = entity['cellMethods']
		return bool( methods and [m for m in methods if m[ "isExposed" ]] )

	def generateMailBoxFor( self, entity, methods, component ):
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

		if entity['hasBaseMailBox']:
			self.generateBaseMailBoxFor( entity )

		if entity['hasCellMailBox']:
			self.generateCellMailBoxFor( entity )

		fileHead = includePathJoin( self.entityPath, entity[ 'name' ] )

		self.render_hpp_file( fileHead, "EntityTemplate.hpp", values )
		self.render_cpp_file( fileHead, "EntityTemplate.cpp", values )


	def generateGlobalFiles( self ):
		self.generateGlobalTypes()
		self.generateEntityFactory()
		self.generateEntityExtensionFactoryCPP()
		self.generateDigest()


	def generateDigest( self ):
		self.render_hpp_file( "DefsDigest", "DefsDigest.hpp", self.__dict__ )
		self.render_cpp_file( "DefsDigest", "DefsDigest.cpp", self.__dict__ )


	def generateGlobalTypes( self ):
		values = dict( 
			fixedDictTypes = [t for t in DataType.sortedDataTypes() 
				if t in fixedDictTypes],
			arrayElementCTypes = set( [t.elementType.toCType() 
				for t in DataType.sortedDataTypes() 
				if t in arrayTypes] ),
			dataTypes = DataType.sortedDataTypes(), 
			extensionsPath = self.extensionsPath )
		self.render_hpp_file( "GeneratedTypes", "GeneratedTypes.hpp", values )
		self.render_cpp_file( "GeneratedTypes", "GeneratedTypes.cpp", values )
		self.render_hpp_file( "GeneratedTypeBindings", 
			"GeneratedTypeBindings.hpp", values )
		self.render_cpp_file( "GeneratedTypeBindings", 
			"GeneratedTypeBindings.cpp", values )


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

		return self.render_to_file( "%s.%s" % 
			(filename, self.entityTemplateSourceExtension), *args )

	def generateEntityFactory( self ):
		values = self.__dict__
		self.render_hpp_file( "EntityFactory", "EntityFactory.hpp", values )
		self.render_cpp_file( "EntityFactory", "EntityFactory.cpp", values )


	def generateEntityExtensionFactoryJS( self ):
		values = dict( self.__dict__ )
		self.render_to_file( "EntityExtensionFactory.js",
			"EntityExtensionFactory.js", values )


	def generateEntityExtensionFactoryCPP( self ):
		values = dict( self.__dict__ )
		values[ "templateExtensionName" ] = TEMPLATE_EXTENSION_NAME

		self.render_hpp_file( "EntityExtensionFactory",
			"EntityExtensionFactory.hpp", values )

		self.render_hpp_file( "EntityExtensionFactoryJS",
			"EntityExtensionFactoryJS.hpp", values )

		self.render_cpp_file( "EntityExtensionFactoryJS",
			"EntityExtensionFactoryJS.cpp", values )

		if GENERATE_TEMPLATES:
			className = (TEMPLATE_EXTENSION_NAME % "Entity") + "Factory"
			values[ "className" ] = className

			self.render_to_file( "templates/" + className + ".hpp",
				"EntityExtensionFactoryImpl.hpp", values )
			self.render_to_file( "templates/" + className + "." + 
				self.entityTemplateSourceExtension,
				"EntityExtensionFactoryImpl.cpp", values )


	def pathFor( self, filename ):
		outputDir = self.outputDirectoryCPP
		if filename.endswith( ".js" ):
			outputDir = self.outputDirectoryJS
		return os.path.join( outputDir, filename )


def createOptionParser():
	parser = optparse.OptionParser()
	parser.add_option( "-o", "--output-cpp",
			dest = "outputDirectoryCPP",
			help = "Directory to output generated files. Defaults to "
				"\"%default\".",
			default = OUTPUT_DIRECTORY, metavar = "OUTPUT_CPP" )

	parser.add_option( "--output-js",
			dest = "outputDirectoryJS",
			help = "Directory to output generated files. Defaults to "
				"\"%default\".",
			default = OUTPUT_DIRECTORY, metavar = "OUTPUT_JS" )

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

	for outputDirectory in \
			[options.outputDirectoryCPP, options.outputDirectoryJS]:
		if not os.path.exists( outputDirectory ):
			os.makedirs( outputDirectory )

	generator = Generator( entityDescriptions, description[ "constants" ],
			options.outputDirectoryCPP, options.outputDirectoryJS,
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
	sys.stdout.write( parser.format_option_help( parser.formatter ) + "\n" )

	return True

# ProcessDefs.py
