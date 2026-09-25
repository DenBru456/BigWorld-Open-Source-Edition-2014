#!/usr/bin/env python
import sys
import os
from xml.dom.minidom import *
import pychecker.checker
import pychecker.warn
import sre

try:
	MF_ROOT = os.environ[ 'MF_ROOT' ] + '/'
except:
	MF_ROOT = "/mf/"

RES_PATH	= MF_ROOT + "bigworld/res/entities/"
CLIENT_PATH	= MF_ROOT + "bigworld/src/client/"
CELL_PATH	= MF_ROOT + "bigworld/src/server/cell/"

sys.path.append( RES_PATH + "common" )

ENTITY_FILE		= CLIENT_PATH + "entity.cpp"
BIGWORLD_FILE	= CLIENT_PATH + "script_bigworld.cpp"
GUI_FILES		= \
	( MF_ROOT + "src/lib/ashes/script_gui.cpp",
	  CLIENT_PATH + "script_gui_extensions.cpp" )

CELLAPP_FILE	= CELL_PATH + "cellapp.cpp"

# -----------------
# Client input data
# -----------------
CLIENT_MODULE_DIRS = (
	MF_ROOT + "src/lib/ashes",
	MF_ROOT + "src/lib/romp",
	MF_ROOT + "src/lib/camera",
	MF_ROOT + "src/lib/sound",
	MF_ROOT + "src/lib/input",
   	CLIENT_PATH )

CLIENT_OLD_STYLE_MODULES = \
	(( "BigWorld", BIGWORLD_FILE ), )

# ---------------
# Cell input data
# ---------------
CELL_MODULE_DIRS = ()

CELL_OLD_STYLE_MODULES = \
	(( "CellApp", CELLAPP_FILE ), )


ENTITIES_FILE	= RES_PATH + "entities.xml"



# ------------------------------------------------------------------------------
# Section: Utils
# ------------------------------------------------------------------------------

def isClientEntity( entity ):
	"This checks if the entity type is one that clients see."

	doc = parse( RES_PATH + "defs/" + entity + ".def" )
	for node in doc.getElementsByTagName( "InstantiationType" )[0].childNodes:
		if node.nodeType == Node.TEXT_NODE:
			return node.data.strip() != "NEVER"
	
	return 0


def blacklist( fileName ):
	"Returns a list of the modules in the blacklist."
	string = ""

	file = open( fileName, 'r' )
	for line in file.readlines():
		if line.find( '# Blacklist: ') == 0:
			string += line[ 12: ]

	return string

# ------------------------------------------------------------------------------
# Section: BigWorld module
# ------------------------------------------------------------------------------

def writeEntityClass( f, entity, forServer = 0 ):
	"""This function writes a dummy entity class based on the def file of the
	entity type passed in."""

	f.write( "\nclass Entity:\n" )
	f.write( "	def __init__( self ):\n" )
	writeDefProperties( f, entity, forServer )
	writeEntityProperties( f )
	f.write( "\n" )
	writeEntityFunctions( f )
	f.write( "\n" )


def createDefProperties( entityName, dict = None ):
	"This reads the properties from the def file."

	if not dict:
		dict = {}
	doc = parse( RES_PATH + "defs/" + entityName + ".def" )

	props = map( lambda x : x.tagName,
				filter( lambda node : node.nodeType == Node.ELEMENT_NODE,
					doc.getElementsByTagName( "Properties" )[0].childNodes ) )

	for prop in props:
		dict[ prop ] = 0

	bases = doc.getElementsByTagName( "Parent" )
	for base in bases:
		for node in base.childNodes:
			if node.nodeType == Node.TEXT_NODE:
				createDefProperties( node.data.strip(), dict )

	return dict



def writeDefProperties( f, entityName, forServer ):
	"This writes the properties from the def file."

	f.write( "\n		# Properties from " + entityName + "\n" )
	doc = parse( RES_PATH + "defs/" + entityName + ".def" )

	# TODO: Should not include server properties when checking client.
	props = map( lambda x : x.tagName,
				filter( lambda node : node.nodeType == Node.ELEMENT_NODE,
					doc.getElementsByTagName( "Properties" )[0].childNodes ) )

	for prop in props:
		f.write( "		self." + prop + " = 0\n" )

	bases = doc.getElementsByTagName( "Parent" )
	for base in bases:
		for node in base.childNodes:
			if node.nodeType == Node.TEXT_NODE:
				writeDefProperties( f, node.data.strip(), forServer )

	f.write( "\n" )


def writeEntityFunctions( f ):
	entityFile = open( ENTITY_FILE, 'r' )

	while entityFile.readline().strip() != "PY_BEGIN_METHODS( Entity )":
		pass

	finished = 0

	while not finished:
		currLine = entityFile.readline()

		if currLine.find( "PY_END_METHODS" ) != -1:
			finished = 1
		else:
			split = currLine.split()
			if split[0] == "PY_METHOD(":
				f.write( "	def " + split[1] + "( self, *args ): pass\n" )
	entityFile.close()


def writeEntityProperties( f ):
	f.write( "		# Properties from Entity\n" )
	entityFile = open( ENTITY_FILE, 'r' )

	while entityFile.readline().strip() != "PY_BEGIN_ATTRIBUTES( Entity )":
		pass

	finished = 0

	while not finished:
		currLine = entityFile.readline()

		if currLine.find( "PY_END_ATTRIBUTES" ) != -1:
			finished = 1
		else:
			split = currLine.split()
			if split[0] == "PY_ATTRIBUTE(":
				f.write( "		self." + currLine.split()[1] + " = 0\n" )
	entityFile.close()


# ------------------------------------------------------------------------------
# Section: Module
# ------------------------------------------------------------------------------

def writeModules( inputDirs, modules ):
	# We want the cpp files
	cppFilter		= sre.compile( "^.*\.cpp$" )
	namedFactory	= sre.compile( "^PY_FACTORY_NAMED\(.*" )
	factoryFilter	= sre.compile( "^PY_FACTORY\(.*" )
	methodFilter	= sre.compile( "^PY_MODULE_STATIC_METHOD\(.*" )
	functionFilter	= sre.compile( "^PY_MODULE_FUNCTION\(.*" )

	for currDir in inputDirs:
		files = filter( cppFilter.match, os.listdir( currDir ) )

		for filename in files:
			currFile = open( currDir + "/" + filename )

			# Process the lines with PY_FACTORY_NAMED

			for line in filter( namedFactory.match, currFile.readlines() ):
				try:
					bits = line.split()
					moduleName = bits[3]

					if not modules.has_key( moduleName ):
						modules[ moduleName ] = []

					modules[ moduleName ].append( bits[2][1:-2] )
				except:
					print "In file", currDir + "/" + filename, "- bad line:" 
					print line

			# Process the lines with PY_FACTORY
			currFile.seek( 0 )

			for line in filter( factoryFilter.match, currFile.readlines() ):
				try:
					bits = line.split()
					moduleName = bits[2]

					if not modules.has_key( moduleName ):
						modules[ moduleName ] = []

					modules[ moduleName ].append( bits[1][:-1] )
				except:
					print "In file", currDir + "/" + filename, "- bad line:" 
					print line

			# Process the lines with PY_MODULE_STATIC_METHOD
			currFile.seek( 0 )

			for line in filter( methodFilter.match, currFile.readlines() ):
				try:
					bits = line.split()
					moduleName = bits[3]

					if not modules.has_key( moduleName ):
						modules[ moduleName ] = []

					modules[ moduleName ].append( bits[2][:-1] )
				except:
					print "In file", currDir + "/" + filename, "- bad line:" 
					print line

			# Process the lines with PY_MODULE_FUNCTION
			currFile.seek( 0 )

			for line in filter( functionFilter.match, currFile.readlines() ):
				try:
					bits = line.split()
					moduleName = bits[2]

					if not modules.has_key( moduleName ):
						modules[ moduleName ] = []

					modules[ moduleName ].append( bits[1][:-1] )
				except:
					print "In file", currDir + "/" + filename, "- bad line:" 
					print line

	outputModules( modules )

def outputModules( modules ):
	for moduleName in modules.keys():
		outFile = open( moduleName + ".py", 'w' )

		for entry in modules[ moduleName ]:
			outFile.write( "def " + entry + "( *args ): pass\n" )

		outFile.close()

def findMethods( inFile ):
	list = []

	finished = 0
	foundPMD = 0

	while not finished:
		line = inFile.readline()
		if not line: finished = 1

		if not foundPMD:
			if line.find( "PyMethodDef" ) == -1: foundPMD = 1
		else:
			split = line.split()

			if len(split) >= 2 and split[0] == '{':
				if split[1] == "NULL,":
					finished = 1
				else:
					list.append( split[1][1: -2] )

	return list


def createOldStyleModules( list, modules ):
	for entry in list:
		(moduleName, fileName) = entry

		try:
			file = open( fileName, "r" )
		except:
			print "Error: Could not open", fileName
			continue

		if not modules.has_key( moduleName ):
			modules[ moduleName ] = []

		modules[ moduleName ] += findMethods( file )



# ------------------------------------------------------------------------------
# Section: class OutputWriter
# ------------------------------------------------------------------------------

class OutputWriter:
	def __init__( self, *args ):
		self.outFiles = args

	def write( self, str ):
		for file in self.outFiles:
			file.write( str )

# ------------------------------------------------------------------------------
# Section: main
# ------------------------------------------------------------------------------

def main():
	if len( sys.argv ) != 3 or not sys.argv[1] in ("client", "cell"):
		print >>sys.stderr, "Usage: python check_script.py [client|cell] entity"
		return

	return checkEntity( sys.argv[1], sys.argv[2] )

def checkEntity( component, entity ):
	global ENTITY_FILE
	result = 0

	try:
		# A map of modules names to a list of their methods.
		createdModules = {}

		if component == "client":
			if not isClientEntity( entity ):
				print "Not a client entity"
				return

			# Need to do some of the Math stuff by hand
			createdModules[ "Math" ] = [ "Vector2", "Vector3", "Vector4", "Matrix" ]
			createdModules[ "ResMgr" ] = [  "openSection", "save", "DataSection" ]
			createdModules[ "BigWorld" ] = [ "stamina", "combat", "musicMgr" ]
			
			writeModules( CLIENT_MODULE_DIRS, createdModules )

			f = open( "BigWorld.py", "a" )
			writeEntityClass( f, entity )
			f.close()
		else:
			ENTITY_FILE		= MF_ROOT + "bigworld/src/server/cell/entity.cpp"

			createOldStyleModules( CELL_OLD_STYLE_MODULES, createdModules )
			writeModules( CELL_MODULE_DIRS, createdModules )

			f = open( "CellApp.py", "a" )
			f.write( "entities = []\n" )
			writeEntityClass( entity, 1 )
			f.close()

		scriptFile = RES_PATH + component + "/" + entity + ".py"
		checkedFile = scriptFile + ".checked"

		outFile = open( checkedFile, 'w' )
		pychecker.warn.outFile = OutputWriter( outFile, sys.stdout )

		os.environ[ 'ENTITY_BLACKLIST' ] = blacklist( scriptFile )
		result = pychecker.checker.main( ('dummy', scriptFile ) )
		del os.environ[ 'ENTITY_BLACKLIST' ]

		try:
			for moduleName in createdModules.keys():
				os.remove( moduleName + ".py" )

				# If we run it twice quickly, the timestamp on the pyc may not
				# have changed.
				try:
					os.remove( moduleName + ".pyc" )
				except:
					pass
		except:
			print >>sys.stderr, "Trouble deleting a file"
	except IOError, e:
		print "Error processing", e.filename
		print e.strerror

	if result == 1:
		outFile.close()
		if os.path.exists( checkedFile ):
			os.remove( checkedFile )

	return result

if __name__ == "__main__":
	sys.exit( main() )
