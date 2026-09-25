#!/usr/bin/env python

import unittest
import bwsetup
bwsetup.addPath( ".." )
bwsetup.addPath( "../.." )

import os

class CommandConformanceTestCase( unittest.TestCase ):
	def setUp( self ):
		thisDir = os.path.dirname( os.path.abspath( __file__ ) )
		commandDir = os.path.abspath( thisDir + "/.." )

		names = [name[:-3] for name in os.listdir( commandDir )
			if name.endswith( ".py" ) ]

		self.modules = [(name, __import__( name )) for name in names
			if name not in ("bwsetup", "__init__") ]

	def testRunnable( self ):
		self.checkModulesFor( "run" )

	def testHelpStr( self ):
		self.checkModulesFor( "getHelpStr" )

	def testUsageStr( self ):
		self.checkModulesFor( "getUsageStr" )

	def checkModulesFor( self, member ):
		for name, module in self.modules:
			assert hasattr( module, member ), \
				"%s has no '%s' member" % (name, member)
			assert callable( getattr( module, member ) ), \
				"Member '%s' of %s is not callable" % (member, name)

if __name__ == '__main__':
	from pycommon import util
	util.setUpBasicCleanLogging()

	unittest.main()

# command_conformance.py
