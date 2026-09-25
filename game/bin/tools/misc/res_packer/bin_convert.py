#!/usr/bin/env python

# Creates a new resource tree from and existing resource tree with all the
# XML files in the tree converted into packed sections, and other processing
# done by res_packer.
#
# Usage: python bin_convert.py [-y] [--res search_paths] [src_dir] [dest_dir] [base_dir]
#        If -y is specified, all errors are ignored and processing continues.
#        If search_paths is specified, it overrides paths.xml of res_packer.
#        If src_dir is not specified, then the current directory is used.
#        If dest_dir is not specified, then it is src_dir + "_bin".
#        If base_dir is not specified, the dest_dir is used as the base dir.
#
# Note: Please note that drive letters must be supplied for both src and dest.
#
# Full example:
#     python bin_convert.py --res /mf/fantasydemo/res;/mf/bigworld/res c:/mf/fantasydemo/res c:/mf/fantasydemo/res_packed /mf/fantasydemo/res_packed
#

from os.path import join, getsize
import os
import stat
import sys
import shutil
import time
import distutils.util
import traceback

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
#Names chosen not to collide with EXIT_SUCCESSFUL, EXIT_FAILURE macros from C
SUCCESSFUL_EXIT = 0
FAILURE_EXIT = 1
#-------------------------------------------------------------------------------
# customisable functions, used to override the default res_packer behaviour.
#-------------------------------------------------------------------------------


# Return 'False' here for files you want to exclude from the final package
def isFileValid( name, srcPath ):
	if (name[-14:-3] == ".thumbnail." or name[-13:] == "thumbnail.dds") and name[-19:] != "space.thumbnail.dds":
		return False	# filter out thumbnails, but keep space.thumbnails.dds as it's used by the minimap

	if name[0:2] == ".#":
		return False	# filter out CVS-generated files

	if name[-4:] == ".pyc":
		# only copy .pyc files if they don't have a corresponding .py file.
		try:
			file = os.open( join( srcPath, name[0:-1] ), os.O_RDONLY )
			os.close( file )
			# .py file exists, so skip to make sure we don't copy the old .pyc
			return False
		except:
			# .py file doesn't exist, so copy the pyc as it exists in the src.
			return True

	if name[-5:] == ".deps":
		return False	# filter out asset pipeline dependency files

	return True


# Return 'True' here for files that we only want to copy, without res_packer
# processing
def processCopyOnly( name, srcPath ):
	if name[-5:] == ".html" or name[-4:] == ".htm" or name[-3:] == ".js" or \
		srcPath.find( "web_resources" ) != -1 or srcPath.find( "gui\\web" ) != -1:
		# Skip HTML content so images are not converted to DDS, HTML files are not
		# converted to packed XML sections, etc.
		return True

	if srcPath.find( "system\\animations" ) != -1:
		# Animations don't get copied normally because they are packed into ANCA
		# files when the model that uses it is processed, but there are some
		# animations that are used without a model, so just copy them directly.
		return True
		
	return False  # use the normal processing for this one.


# Remove here directories from 'dirs' you want to exclude from the final package
def stripUnwantedDirs( root, dirs ):
	# don't visit CVS directories
	try:
		dirs.remove('CVS')
	except:
		pass

	# don't visit SVN directories
	try:
		dirs.remove('.svn')
	except:
		pass

	# don't visit Asset Locator's thumbnail directories
	try:
		dirs.remove('.bwthumbs')
	except:
		pass

	# don't visit animation(s) directories, only the system's stand-alone
	# animations
	if root[-6:] != "system":
		try:
			dirs.remove('animation')
		except:
			pass
		try:
			dirs.remove('animations')
		except:
			pass

	# don't visit scripts/editor directories
	try:
		if root[-7:] == "scripts":
			dirs.remove('editor')
	except:
		pass

	if os.name == "nt":
		# in the client, don't visit scripts/cell and entities/base directories
		try:
			if root[-7:] == "scripts":
				dirs.remove('cell')
				dirs.remove('base')
				dirs.remove('bot')
				dirs.remove('server_common')
		except:
			pass


# custom handler that compiles .py files and copies .pyc to the destination path
# discarding the original .py file.
def pythonHandlerClient( dirname, filename, srcPath, dstPath,
		basePath, resPaths ):
	inFile = join( srcPath, dirname, filename )
	outFile = join( dstPath, dirname, filename )
	# copy the originmal .py file to the destination path
	shutil.copy2( inFile, outFile )

	# compile
	print "Compiling python file " + outFile + "..."
	error = False
	try:
		distutils.util.byte_compile( [ outFile.replace( '\\', '/' ) ], prefix=basePath.replace( '\\', '/' ) )
	except:
		error = True

	# check if the compiled file exists (.pyc)
	try:
		file = os.open( outFile + "c", os.O_RDONLY )
		os.close( file )
	except:
		error = True

	# done, so leave the .pyc file, remove original .py source file. Note that
	# we need to make sure this file is read-write in order to remove it.
	try:
		st = os.stat( outFile )
		mode = stat.S_IMODE( st.st_mode )
		os.chmod( outFile, mode | stat.S_IWRITE | stat.S_IREAD )
		os.remove( outFile )
	except:
		print "WARNING: could not remove source .py file from destination"
	
	# check for errors
	if error:
		print "...failed"
		return

	print "...succeeded"


# this if-else can set up custom handlers per-platform.
if os.name == "nt":
	# commented example of a custom handler:
	# handlers = { "chunk" : chunkHandlerClient }
	handlers = { "py" : pythonHandlerClient }
else:
	handlers = {}



#-------------------------------------------------------------------------------
# core bin_convert functions
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# commented the use of the MF_ROOT variable, as it was causing problems that are
# very hard to track down (i.e. using another res_packer executable)
#MF_ROOT = "/mf"

#try:
#	MF_ROOT = os.environ[ "MF_ROOT" ]
#except:
#	print "MF_ROOT is defaulting to", MF_ROOT

#res_packer_path = join( MF_ROOT, "bigworld/tools/misc/res_packer" )
#-------------------------------------------------------------------------------

# global to specify whether to ignore errors
g_ignoreErrors = False

# assume res_packer is in the same directory as bin_convert
res_packer_path = os.path.dirname( os.path.abspath(__file__) )

if os.name == "nt":
	res_packer = join( res_packer_path, "res_packer.exe" )
else:
	res_packer = join( res_packer_path, "res_packer" )
	
g_assetListFile = open( "asset_list.txt", "w" )


def defaultHandler( dirname, filename, srcPath, dstPath, basePath, resPaths ):
	if processCopyOnly( filename, dirname ):
		# We must copy this file straight, and don't add it for processing.
		inFile = join( srcPath, dirname, filename )
		outFile = join( dstPath, dirname, filename )
		# copy the original .py file to the destination path
		print "Direct copying file " + outFile + "..."
		shutil.copy2( inFile, outFile )	
		# check if the copied file exists
		try:
			file = os.open( outFile, os.O_RDONLY )
			os.close( file )
			print "...succeeded"
		except:
			print "...failed"
			
		return
		
	if (dirname != ""):
		g_assetListFile.write( dirname + "\\" + filename + "\n" );
	else:
		g_assetListFile.write( filename + "\n" );


def convert( srcPath, dstPath, basePath, resPaths, errorFile ):
	start = time.time()
	print "Clearing destination folder " + dstPath
	def rmtreeErr(func, path, exc_info):
		if os.access(path, os.F_OK) and not os.access(path, os.W_OK):
			os.chmod(path, stat.S_IWUSR)
			func(path)
	shutil.rmtree( dstPath, False, rmtreeErr )
	print "...done"

	count = 0

	print "Packing assets..."
	appDir = os.getcwd()
	os.chdir( srcPath )
	for root, dirs, files in os.walk( "." ):
		newPath = join( dstPath, root )

		if not os.path.isdir( newPath ):
			os.makedirs( newPath )

		# remove the preceding "./" to create cleaner paths
		if root[0:2] == ".\\" or root[0:2] == "./":
			root = root[2:]
		elif root == ".":
			root = ""

		for name in files:
			if isFileValid( name, srcPath ):
				ext = name.split( "." )[-1]
				handler = handlers.get( ext, defaultHandler )
				handler( root, name, srcPath, dstPath, basePath, resPaths )
				count += 1

		if root == "":
			fullRoot = dstPath[1:]
		else:
			fullRoot = join( dstPath, root )
		stripUnwantedDirs( fullRoot, dirs )
		
	g_assetListFile.close()
	os.chdir( appDir )

	resCmd = ""
	if resPaths != "":
		resCmd = "--res"
		resPaths = "\"%s\"" % resPaths

	try:
		execResult = os.spawnl( os.P_WAIT, res_packer, "\"%s\"" % res_packer,
								resCmd, resPaths,
								"--list", "\"asset_list.txt\"",
								"--in", "\"%s\"" % srcPath,
								"--out", "\"%s\"" % dstPath,
								"--err", "%s" % errorFile)
	except Exception, e:
		print "os.spawnl failed (%s) with command: '%s %s %s --list asset_list.txt --in %s --out %s --err %s'" % ( e, res_packer, resCmd, resPaths, srcPath, dstPath, errorFile )
		return FAILURE_EXIT
		
	#Check ResPacker exit condition
	if execResult != SUCCESSFUL_EXIT:
		print "packing failed with errorlevel %d with command: '%s %s %s --list asset_list --in %s --out %s --err errors.log'" \
			% ( execResult, res_packer, resCmd, resPaths, srcPath, dstPath )
		return execResult
	else:
		print "...done. %d assets packed in %.2f seconds." % \
		(count, time.time() - start)
		return SUCCESSFUL_EXIT
		
	


#-------------------------------------------------------------------------------
# bin_convert main
#-------------------------------------------------------------------------------

def doMain():
	global g_ignoreErrors
	i = 1
	resPaths = ""
	errorFile = "errors.log"
	if len(sys.argv) > 1:
		while True:
			try:
				if sys.argv[i] == "--res" or sys.argv[i] == "-r":
					# set res paths
					resPaths = sys.argv[i+1]
					i = i + 2
				elif sys.argv[i] == "-y":
					# say "Yes to All" to errors, to continue processing
					i = i + 1
					g_ignoreErrors = True
				elif sys.argv[i] == "-e":
					# set error file
					errorFile = sys.argv[i+1]
					i = i + 2
				elif sys.argv[i][0] == "-":
					print "Invalid option ", sys.argv[i]
					sys.exit(FAILURE_EXIT)
				else:
					break
			except IndexError:
				print "Missing or Invalid argument(s)"
				traceback.print_exc()
				sys.exit(FAILURE_EXIT)

	srcPath = '.'
	try:
		srcPath = sys.argv[i]
		if not os.path.exists(srcPath):
			print "Cannot find source path " + srcPath
			sys.exit(FAILURE_EXIT)
	except IndexError:
		pass

	dstPath = os.path.abspath( srcPath ) + "_bin"
	try:
		dstPath = sys.argv[i+1]
	except IndexError:
		pass

	basePath = dstPath
	try:
		basePath = sys.argv[i+2]
	except IndexError:
		pass

	execRes = FAILURE_EXIT

	if not os.path.exists(res_packer):
		print
		print "ERROR: Couldn't find res_packer file:", res_packer
		print "Please make sure this file has been compiled correctly and placed in the location above."
	else:
		execRes = convert( srcPath, dstPath, basePath, resPaths, errorFile )
	sys.exit(execRes)


if __name__ == "__main__":
	doMain()
# bin_convert.py
