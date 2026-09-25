#!/usr/bin/env python

# This is a simple script that traverses a direction to find all .cdata files
# and strips out the specified sections
# e.g. to strip all terrain2 and lighting sections:
# ./strip_cdata.py /home/paulm/mf/fantasydemo/res terrain2 lighting

import os
import sys

print os.path.abspath( __file__ )

RES_PACKER = \
	os.path.dirname( os.path.abspath( __file__ ) ) + os.sep + "res_packer"
# BW_RES_PATH = "/home/paulm/mf/fantasydemo/res"

def printUsage( argv ):
	print "Usage: %s pathToConvert sectionName(s)" % (argv[0],)

def stripCData( resPath, sectionNames ):
	# We can get away with setting the BW_RES_PATH to the conversion path
	BW_RES_PATH = resPath

	args = [RES_PACKER, "--res", BW_RES_PATH]
	for sectionName in sectionNames:
		args += [ "--strip", sectionName ]

	for path, dirs, files in os.walk( resPath ):
		for cdataPath in [path + os.sep + cdataFile
							for cdataFile in files
							if cdataFile.endswith( ".cdata" ) ]:
			tmpFile = cdataPath + ".tmp"
			os.spawnv( os.P_WAIT, RES_PACKER, args + [cdataPath, tmpFile] )
			os.rename( tmpFile, cdataPath )


if __name__ == "__main__":
	if len( sys.argv ) >= 3:
		stripCData( sys.argv[1], sys.argv[2:] )
	else:
		printUsage( sys.argv )
