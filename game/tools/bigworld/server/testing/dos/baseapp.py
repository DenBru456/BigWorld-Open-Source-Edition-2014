#!/usr/bin/python

import sys
import os

from test import *
import loginapp

# BigWorld includes
try:
	sys.path.append(
		os.environ[ "MF_ROOT" ] +
			"/bigworld/tools/server/pycommon".replace( '/', os.sep ) )
except KeyError:
	print "Warning: MF_ROOT is not set"

def basic():
	return loginapp.basic()

def ok( sock, process, component ):
	return alive( component )
