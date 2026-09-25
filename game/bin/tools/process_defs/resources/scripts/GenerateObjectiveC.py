import optparse
import os
import pprint
import sys

OUTPUT_DIRECTORY = "GeneratedObjectiveC"
BASE_CLASS = "BWEntity"
CLASS_NAME_FORMAT = "%s_Stub"

def writePropertyMembers( f, properties ):
	f.write(
		"// Properties stored in BWEntity.serverProperties dictionary\n" )
	f.write( "#if 0\n" )
	for property in properties:
		f.write( "\tid /*%(type)s*/ %(name)s;\n" % property )
	f.write( "#endif\n" )

def writePropertyAccessors( f, properties ):
	for property in properties:
		f.write( "@property (nonatomic, readonly) id /*%(type)s*/ %(name)s;\n" %
				property )

def writePropertyImplementations( f, properties ):
	for property in properties:
		f.write( "@dynamic %(name)s;\n" % property )

def writeMethod( f, method ):
	if method[ "isExposed" ]:
		f.write( "- (void) %s" % method[ "name" ] )
		padding = ""
		for i, arg in enumerate( method[ "args" ] ):
			argName = arg[0]
			if not argName:
				argName = "arg%d" % i
			f.write( "%s: (id)/*%s*/ %s" % (padding, arg[1], argName) )
			padding = "\n                "
		f.write( ";\n\n" )

def writeMailbox( f, methods, component, entityName ):
	if methods:
		f.write( """

// -----------------------------------------------------------------------------
// This describes the interface to the %s part of the entity.
// -----------------------------------------------------------------------------

@protocol %s_%sEntity\n\n""" % (component, entityName, component) )

		for method in methods:
			writeMethod( f, method )

		f.write( "@end\n" )


class Generator( object ):
	def __init__( self, outputDirectory, baseClass, classNameFormat ):
		self.outputDirectory = outputDirectory
		self.baseClass = baseClass
		self.classNameFormat = classNameFormat

	def generateFilesFor( self, entity ):
		sys.stderr.write( "Generating for %s\n" % entity[ "name" ] )

		self.generateHeaderFile( entity )
		self.generateImplementationFile( entity )

	def generateHeaderFile( self, entity ):
		entityName = entity[ "name" ]
		className = self.classNameFormat % entityName
		f = open( self.pathFor( className + ".h" ), 'w' )

		f.write( '#import "%s.h"\n' % self.baseClass )

		writeMailbox( f, entity[ "baseMethods" ], "Base", entityName )
		writeMailbox( f, entity[ "cellMethods" ], "Cell", entityName )
		writeMailbox( f, entity[ "clientMethods" ], "Client", entityName )

		f.write( """

// -----------------------------------------------------------------------------
// This is the base class for %s.
// -----------------------------------------------------------------------------

@interface %s_Stub : %s\n{\n""" % (entityName, entityName, self.baseClass) )
		writePropertyMembers( f, entity[ "clientProperties" ] )
		f.write( "}\n\n" )
		writePropertyAccessors( f, entity[ "clientProperties" ] )
		f.write( "\n@end\n" )

	def generateImplementationFile( self, entity ):
		entityName = entity[ "name" ]
		className = self.classNameFormat % entityName
		f = open( self.pathFor( className + ".mm" ), 'w' )

		f.write( '#import "%s.h"\n\n' % className )

		f.write( "@implementation %s\n\n" % className )

		writePropertyImplementations( f, entity[ "clientProperties" ] )

		f.write( "\n@end\n" )

	def pathFor( self, filename ):
		return os.path.join( self.outputDirectory, filename )


def createOptionParser():
	parser = optparse.OptionParser()
	parser.add_option( "-o", "--output", dest = "outputDir",
			help = "Directory to output generated files",
			default = OUTPUT_DIRECTORY, metavar = "FILE" )

	parser.add_option( "-b", "--base-class", dest = "baseClass",
			help = "The base class for generated entity classes",
			default = BASE_CLASS, metavar = "CLASS_NAME" )

	return parser

def process( description ):
	entityDescriptions = description[ "entityTypes" ]

	parser = createOptionParser()
	(options, args) = parser.parse_args()

	print "options", options
	print "args", args

	outputDirectory = options.outputDir
	baseClass = options.baseClass
	classNameFormat = CLASS_NAME_FORMAT

	print "argv:", sys.argv

	if not os.path.exists( outputDirectory ):
		os.makedirs( outputDirectory )

	generator = Generator( outputDirectory, baseClass, classNameFormat )

	for entity in entityDescriptions:
		if entity[ "canBeOnClient" ]:
			generator.generateFilesFor( entity )

	return True

def help():
	parser = createOptionParser()
	sys.stdout.write( "\nScript " )
	print parser.format_option_help( parser.formatter )

	return True

# GenerateObjectiveC.py
