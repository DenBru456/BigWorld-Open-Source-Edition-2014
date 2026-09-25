#!/usr/bin/env python

REMOVE_TEMP_DIR = True

from lib.rpm_builder import RPMBuilder

import logging
import os
import optparse

if __name__ == "__main__":
	import pycommon.util
	pycommon.util.setUpBasicCleanLogging()

log = logging.getLogger( 'generate' )

def main():

	opt = optparse.OptionParser( add_help_option = True )
	opt.add_option( "-i", "--indie", dest = "isIndie",
					action = "store_true", default = False,
					help = "Append '-indie' to the RPM name in binary_rpms" )
	opt.add_option( "-d", "--delete", dest = "deleteTempRPM",
					action = "store_true", default = False,
					help = "Delete the temporary RPM packages after they"
					" have been copied to binary_rpms directory." )
	opt.add_option( "-o", "--output", dest = "output_directory",
					default = "binary_rpms",
					help = "Directory to output RPMs into" )
	opt.add_option( "-c", "--create-package-version",
					dest = "createPackageVersion",
					action = "store_true", default = False,
					help = "Create a version file in the package directory" )
	options, args = opt.parse_args()

	absDir =  os.path.dirname( os.path.abspath( __file__ ) )
	bwRoot =  os.path.abspath( absDir + "/../../../../.." )
	
	bwInstallDir = os.environ.get( "BW_INSTALL_DIR", None )
	os.chdir( absDir )

	if len( args ) != 1:
		raise ValueError, "Invalid command line arguments"

	packageDir = args[0]

	print '-' * 80
	print "Starting RPM build for %s" % packageDir
	print '-' * 80

	builder = RPMBuilder( bwRoot, packageDir, options.isIndie, bwInstallDir,
						  options.createPackageVersion )

	if not builder.build( options.output_directory, REMOVE_TEMP_DIR,
					options.deleteTempRPM ):
		sys.exit( 1 )


if __name__ == "__main__":
	import sys

	if os.getuid() == 0:
		log.critical( "This script must not be executed by the root user." )
		sys.exit( 1 )
	main()

# generate.py
