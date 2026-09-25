#!/usr/bin/env python

DELAYED_ERROR = None
try:
	import os
	import sys
	import time
	import tempfile
	import socket
	import optparse
	import popen2
	import re
	import platform

	from common import *
	from pycommon import util
except Exception, e:
	DELAYED_ERROR = str( e )

UPDATE_CMD = "svn update"
MAKE_CMD = "make -s DO_NOT_BELL=1 USE_MYSQL=1"
CONFIGS = ()

if platform.machine() == 'x86_64':
	architecture = '64';
else:
	architecture = '';

for config in ("Hybrid", "Debug", "Release")[:2]:
	CONFIGS += config + architecture,

UPDATE_DIRS = ["bigworld", "src", "fantasydemo"]
DO_UPDATE = True
DO_CLEAN = True
OUTPUT_MAKE = ""

def main():

	# Show status info
	echo( util.border( "Building on %s, %s" % (HOSTNAME, time.ctime()) ) )
	echo( "Logging to %s" % LOGFILE )
	echo( "Compiler version: %s" % os.popen( "g++ --version" ).readline().rstrip() )
	echo()

	# Do `make clean` if required
	if DO_CLEAN:
		os.chdir( "%s/bigworld/src/server" % MF_ROOT )
		echo( util.border( "Starting `make clean` in %s" % os.getcwd() ) )
		for config in CONFIGS:
			if not run( "%s MF_CONFIG=%s clean" % (MAKE_CMD, config) )[0]:
				fail()
		echo()

		echo( util.border( "Starting `make clean` in res_packer" ) )
		for config in CONFIGS:
			echo( "MF_CONFIG=%s %s -C %s/bigworld/src/tools/res_packer clean" %
					(config, MAKE_CMD, MF_ROOT) )
			if not run( "MF_CONFIG=%s %s -C %s/bigworld/src/tools/res_packer clean" %
					(config, MAKE_CMD, MF_ROOT) )[0]:
				fail()
		echo()
	# Do repository update if required
	if DO_UPDATE:
		echo( util.border( "Starting repository update in %s (using %s)" %
						   (MF_ROOT, UPDATE_CMD) ) )
		os.chdir( MF_ROOT )

		# If an output file has been specified, push the SVN status into
		# it in case svn fails. Otherwise reporting may fail silently.
		REDIRECTION = ""
		if len( OUTPUT_MAKE ):
			REDIRECTION = "2>&1 | tee %s" % OUTPUT_MAKE

                (success, outputs) = run( "%s %s %s" % (UPDATE_CMD, " ".join( UPDATE_DIRS ), REDIRECTION), True)
		if not success:
			fail()
		else:
                        for line in outputs:
				# if output line start with svn or C (conflict) we should fail the build and check.
                                if line.startswith('svn') or line.startswith('C'):
                                        fail()

		echo()

	# Check for coredumps
	os.chdir( "%s/bigworld/bin/Hybrid%s" % (MF_ROOT, architecture) )
	binfiles = [ x for x in os.listdir( "." ) if not x.startswith( "." ) ]
	corefiles = [ x for x in binfiles if x.startswith( "core." ) ]
	if corefiles:
		archfiles = [ x for x in binfiles if os.path.isfile( x ) and
					  (re.search( "(core\..*|assert\..*)", x ) or
					   os.stat( x ).st_mode & 0111) ]
		archive = "coredumps-%s.tar.gz" % time.strftime( "%Y-%m-%d-%H-%M" )
		echo( util.border( "Coredumps found, archiving to %s" % archive ) )
		for core in corefiles:
			echo( core )
			assrt = re.sub( "core\.(.*)", "assert.\\1.log", core )
			if os.path.isfile( assrt ):
				echo( "\n" + open( assrt ).read() )
		echo()
		os.system( "tar czf %s --remove-files %s" %
				   (archive, " ".join( archfiles )) )

	# Build
	REDIRECTION = ""
	if len( OUTPUT_MAKE ):
		REDIRECTION = " > \"%s\" 2>&1" % OUTPUT_MAKE

	os.chdir( "%s/bigworld/src/server" % MF_ROOT )
	echo( util.border( "Building configurations: %s" % " ".join( CONFIGS ) ) )
	for config in CONFIGS:
		if not run( "MF_CONFIG=%s %s %s" % (config, MAKE_CMD, REDIRECTION) )[0]:
			fail()

	os.chdir( "%s/bigworld/src/tools/res_packer" % MF_ROOT )
	echo( util.border( "Building res_packer configurations: %s" % " ".join( CONFIGS ) ) )
	for config in CONFIGS:
		if not run( "MF_CONFIG=%s %s %s" % (config, MAKE_CMD, REDIRECTION) )[0]:
			fail()

	# Build the unit tests 
	os.chdir( "%s/bigworld/src/lib" % MF_ROOT )
	echo( util.border( "Building test  configurations: %s" % " ".join( CONFIGS ) ) )
	for config in CONFIGS:
		if not run( "MF_CONFIG=%s %s unit_tests %s" % (config, MAKE_CMD, REDIRECTION) )[0]:
			fail()

	echo( "Build successful at %s" % time.ctime() )
	return 0

if __name__ == "__main__":
	util.setUpBasicCleanLogging()

	opt = optparse.OptionParser()
	opt.add_option( "--no-update", dest = "noupdate", action = "store_true",
					help = "Don't do a repository update" )
	opt.add_option( "--no-clean", dest = "noclean", action = "store_true",
					help = "Don't `make clean` before building" )
	opt.add_option( "--output-make", "--om", 
					dest = "output_make", action = "store",
					metavar = "FILE", default = "",
					help = "Redirect output from make to FILE" )
	opt.add_option( "--update-exclude", metavar = "EXCLUDELIST",
					dest = "update_exclude", action = "store",
					help = "Comma seperated list of directories to update" )
	options, args = opt.parse_args()

	DO_UPDATE = not options.noupdate
	DO_CLEAN = not options.noclean
	OUTPUT_MAKE = options.output_make

	# If there was an early error attempt to notify the user now and bail
	if DELAYED_ERROR != None:

		fd = open( OUTPUT_MAKE, "a" )
		fd.write( "Script error:\n" )
		fd.write( DELAYED_ERROR )
		fd.write( "\n" )
		fd.close()
		sys.exit( 1 )


	if options.update_exclude:
		for exclude in 	options.update_exclude.split( "," ):
			try:
				UPDATE_DIRS.remove( exclude )
			except:
				print "Failed to remove element '%s'" % exclude
				pass

	sys.exit( main() )
