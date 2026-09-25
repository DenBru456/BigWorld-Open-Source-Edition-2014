"""Offline compilation script for BigWorld shaders.

Usage: python RebuildShaders.py [options]

Options:
    -h, --help              shows this help
    -a, --all               forces a rebuild of all shaders
    -d, --debug             shows debug information
    -x, --xml               output in XML format
    -f, --file [filename]   compile only a specific shader
    -s, --stop-on-error     stop compilation on the first error that occurs

Note: You can take advantage of multi-core systems by running multiple
instances of this script (each subsequent instance will run on a different
CPU core).
"""

import time
import sys
import getopt
import random

SHADER_SEARCH_PATHS = [
	# BigWorld standard paths
	"shaders/bloom/",
	"shaders/decal/",
	"shaders/environment/",
	"shaders/flora/",
	"shaders/speedtree/",
	"shaders/std_effects/",
	"shaders/std_effects/shadows/",
	"shaders/std_effects/shimmer/",
	"shaders/std_effects/stipple/",
	"shaders/terrain/",
	"shaders/water/",
	"shaders/post_processing/",
	"system/materials/",

	# Fantasy Demo paths
	"sets/dungeon/materials/",
	"objects/models/fx/",
	"materials/",

	# World Editor paths
	"tools/worldeditor/resources/shaders/",
	"tools/worldeditor/resources/models/",
	"tools/worldeditor/resources/materials/",
]


sys.path.append("../asset_processor")
import AssetProcessorSystem

import ResMgr

class XMLOutputter:
	def __init__( self ):
		self.debug = False
		self.tags = []

	def pushTag( self, tagName ):
		self.outputLeadingTabs()
		print "<" + tagName + ">"
		self.tags.append( tagName )

	def popTag( self ):
		tagName = self.tags.pop()
		self.outputLeadingTabs()
		print "</" + tagName + ">"

	def dataTag( self, tagName, tagData ):
		self.outputLeadingTabs()

		if type(tagData) is bool:
			tagData = 1 if tagData else 0

		print "<" + tagName + ">\t" + str(tagData) + "\t</" + tagName + ">"

	def outputLeadingTabs( self ):
		for i in range( len(self.tags) ):
			print "\t",

	def begin( self, forceAll, debug ):
		self.debug = debug
		self.pushTag( "ShaderBuild" )

		self.pushTag( "Options" )
		self.dataTag( "RebuildAll", forceAll )
		self.dataTag( "Debug", debug )
		self.popTag()

	def finish( self, totalTime ):
		global numUpToDate
		global numSuccesses
		global numFailures

		self.pushTag( "Results" )
		self.dataTag( "NumSuccesses", numSuccesses )
		self.dataTag( "NumFailures", numFailures )
		self.dataTag( "NumUpToDate", numUpToDate )
		self.dataTag( "TotalTime", ("%.2f" % totalTime) )
		self.popTag()

		self.popTag()

	def beginGenFileList( self ):
		pass

	def endGenFileList( self, fileList ):
		pass

	def enterPath( self, path, success ):
		pass

	def beginShader( self, resourceID ):
		self.pushTag( "Shader" )
		self.dataTag( "Source", resourceID )

	def endShader( self, result ):
		self.popTag()

	def beginCombo( self, currentCombo ):
		self.pushTag( "Combo" )
		self.dataTag( "Flags", "".join( [str(x) for x in currentCombo] ) )

	def endCombo( self, success, reasonStr ):
		self.pushTag( "Result" )
		self.dataTag( "Success", success )
		self.dataTag( "Detail", reasonStr )
		self.popTag()

		self.popTag()


class TXTOutputter:

	def __init__( self ):
		self.debug = False

	def begin( self, forceAll, debug ):
		self.debug = debug

		if self.debug:
			print "Macros (infixed in this order):"
			macros = AssetProcessorSystem.getShaderMacros()
			for macro in macros:
				print ("\t" + str(macro[0]) + " (" + str(macro[1]) + " possible settings)")

			print

		if forceAll:
			print "Forcing rebuild."
			print

	def finish( self, totalTime ):
		global numUpToDate
		global numSuccesses
		global numFailures

		print
		print "Build complete: %d succeeded, %d failed, %d up-to-date (%.2f seconds)." % \
				(numSuccesses, numFailures, numUpToDate, (totalTime))

	def beginGenFileList( self ):
		print "Generating file list..."

	def endGenFileList( self, fileList ):
		print "%d shaders need building." % len(fileList)
		print

	def enterPath( self, path, success ):
		if success:
			if self.debug:
				print path
		else:
			print "ERROR: Failed to enter path '" + path + "'."

	def beginShader( self, resourceID ):
		print resourceID

	def endShader( self, result ):
		pass

	def beginCombo( self, currentCombo ):
		print "\t[" + "".join( [str(x) for x in currentCombo] ) + "]: ...",

	def endCombo( self, success, reasonStr ):
		print reasonStr


numUpToDate = 0
numSuccesses = 0
numFailures = 0
outputter = TXTOutputter()


def compileShaderCombinationsRecursive( resourceID, force, currentCombo=[] ):
	global outputter

	macros = AssetProcessorSystem.getShaderMacros()

	if len( currentCombo ) == len( macros ):
		if force or AssetProcessorSystem.shaderNeedsRecompile( resourceID, tuple(currentCombo) ):
			outputter.beginCombo( currentCombo )
			result, resultString = AssetProcessorSystem.compileShader( resourceID, tuple(currentCombo), force )
			outputter.endCombo( bool(result), resultString )

			if not result:
				return False # Bail out early for this shader if we failed (don't try other combos)
	else:
		macroName, macroSettingCount = macros[ len(currentCombo) ]
		for i in range( macroSettingCount ):
			currentCombo.append( i )
			result = compileShaderCombinationsRecursive( resourceID, force, currentCombo )
			currentCombo.pop()
			if not result:
				return False

	return True


def checkNeedsRecompileCombinationsRecursive( resourceID, currentCombo=[] ):
	macros = AssetProcessorSystem.getShaderMacros()

	if len( currentCombo ) == len( macros ):
		return AssetProcessorSystem.shaderNeedsRecompile( resourceID, tuple(currentCombo) )
	else:
		macroName, macroSettingCount = macros[ len(currentCombo) ]
		for i in range( macroSettingCount ):
			currentCombo.append( i )
			res = checkNeedsRecompileCombinationsRecursive( resourceID, currentCombo )
			currentCombo.pop()
			if res:
				return True

	return False


def needsRecompile( resourceID ):
	return checkNeedsRecompileCombinationsRecursive( resourceID )


def compileShader( resourceID, force ):
	global numSuccesses
	global numFailures
	global outputter

	if force or checkNeedsRecompileCombinationsRecursive( resourceID ):
		outputter.beginShader( resourceID )
		result = compileShaderCombinationsRecursive( resourceID, force )
		outputter.endShader( result )
		if result:
			numSuccesses += 1
		else:
			numFailures += 1


def build( forceAll, specificFiles, stopOnError ):
	global numUpToDate
	global outputter

	files = []

	if specificFiles is None:
		outputter.beginGenFileList()

		for path in SHADER_SEARCH_PATHS:
			pathSection = ResMgr.openSection( path )
			outputter.enterPath( path, pathSection is not None )
			if not pathSection:
				continue

			for name in pathSection.keys():
				fullName = path + name
				if name.endswith( ".fx" ):
					if forceAll or needsRecompile( fullName ):
						files.append( fullName )
					else:
						numUpToDate += 1

		outputter.endGenFileList( files )
	else:
		files = [ f for f in specificFiles if forceAll or needsRecompile( f ) ]

	random.shuffle(files)

	for filename in files:
		compileShader( filename, forceAll )
		if stopOnError and numFailures > 0:
			break


def usage():
	print __doc__


def doExit(status=0):
	AssetProcessorSystem.fini()
	sys.exit(status)


def main(argv):
	global outputter

	try:
		opts, args = getopt.getopt(sys.argv[1:], "haxsdf:", ["help", "all", "xml", "stop-on-error", "debug", "file="])
	except getopt.GetoptError, err:
		print str(err)
		doExit(2)

	debug = False
	forceAll = False
	specificFiles = None
	stopOnError = False

	for o,a in opts:
		if o in ("-h", "--help"):
			usage()
			doExit()
		elif o in ("-a", "--all"):
			forceAll = True
		elif o in ("-s", "--stop-on-error"):
			stopOnError = True
		elif o in ("-d", "--debug"):
			debug = True
		elif o in ("-x", "--xml"):
			outputter = XMLOutputter()
		elif o in ("-f", "--file"):
			if specificFiles is None:
				specificFiles = []

			specificFiles.append( a )


	outputter.debug = debug
	outputter.begin( forceAll, debug )

	startTime = time.clock()
	build( forceAll, specificFiles, stopOnError )
	endTime = time.clock()

	outputter.finish( endTime-startTime )

	doExit( 1 if numFailures > 0 else 0 )



if __name__ == "__main__":
	main(sys.argv[1:])

