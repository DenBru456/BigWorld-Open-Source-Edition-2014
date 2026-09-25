#!/usr/bin/env python

import sys
import os
import optparse
import sys

import bw_generate_res_trees

from bw_generate_res_trees import BASE_PATH

RUN_BAT = \
r"""@ECHO OFF
REM This script launches the game

REM Change to the correct folder
cd /D %~dp0

REM The path to your resources
SET RES_PATH=%~dp0res

REM The path to the BigWorld resources
SET BW_RES_PATH=..\..\..\bigworld\res

SET EXE_NAME=..\bigworld\bin\win32\bwclient.exe

START %EXE_NAME% --res %RES_PATH%;%BW_RES_PATH% %*
"""


USAGE = \
"""Usage %s <output directory name>
	This script creates an empty project directory with a skeleton project."""

def main():
	if len( sys.argv ) != 2:
		print USAGE % sys.argv[0]
		return 1

	outputDirectory = os.path.join( BASE_PATH, "..", sys.argv[1] )
	createNewProject( outputDirectory )

	return 0

def createNewProject( outputDir ):
	outputDir = os.path.normpath( outputDir )
	print "Creating new project at %s" % outputDir

	if os.path.exists( outputDir ):
		print "Error: %s already exists" % outputDir
		sys.exit( 1 )

	# Create the directory
	os.makedirs( outputDir )

	bw_generate_res_trees.generateDefaultRes( os.path.join( outputDir, "res" ) )

	# copy the run.bat
	run_bat_filename = os.path.join( outputDir, "run.bat" )
	print "Writing", run_bat_filename
	run_bat = open( run_bat_filename, 'w' )
	run_bat.write( RUN_BAT )
	run_bat.close()

if __name__ == "__main__":
	sys.exit( main() )

# create_new_project.py
