#!/usr/bin/env python

import re
import subprocess
import sys


def _discoverLineStartingWith( prefix, pipe ):

	output = ""
	desiredLine = None

	while pipe.poll() is None:
		output += pipe.stdout.read()
	output += pipe.stdout.read()

	lines = output.split( "\n" )
	if len( lines ) > 1:
		results = [ line for line in lines if line.startswith( prefix ) ]
		if results:
			desiredLine = re.sub( "%s *" % prefix, "", results[ 0 ] )

	if pipe.wait() != 0:
		raise Exception( "Failed to discover SVN repo: " + output )

	return desiredLine


def latestRevision( bwRoot ):

	# Extract the REV from local copy.
	cmd = [ "svn", "info", "--non-interactive", bwRoot ]

	try:
		pipe = subprocess.Popen( cmd,
				stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
	except OSError:
		print "Failed to execute '%s'" % " ".join( cmd )
		return str( 0 )

	try:
		revision = _discoverLineStartingWith( "Revision:", pipe )
	except:
		# return an empty revision string so the build will still proceed.
		return str( 0 )

	return revision


# svn_assistant.py
