from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


callBackScript = """
# Log FantasyDemo event callbacks and event listener callbacks
import sys
import functools
import BigWorld
from bwdebug import *
space = sys.modules[ __name__ ]

def _hookEvents():
    for cbName in [
        'onAppReady',
        'onDBAppReady',
        'onInit',
        'onFini',
    ]:
        if hasattr( space, cbName ):
            oldCB = getattr( space, cbName )
            def personalityCallback( eventName, oldCB, *args, **kwargs ):
                DEBUG_MSG( "Event: simple_space.%s: ( %s, %s )" % ( eventName, args, kwargs ) )
                oldCB( *args, **kwargs )
            setattr( space, cbName, functools.partial( personalityCallback, cbName, oldCB ) )
        else:
            def personalityCallback( eventName, *args, **kwargs ):
                DEBUG_MSG( "Event: simple_space.%s: ( %s, %s )" % ( eventName, args, kwargs ) )
            setattr( space, cbName, functools.partial( personalityCallback, cbName ) )

        def eventListener( eventName, *args, **kwargs ):
            DEBUG_MSG( "Event: %s: ( %s, %s )" % ( eventName, args, kwargs ) )
        BigWorld.addEventListener( cbName, functools.partial( eventListener, cbName ) )

_hookEvents()

# Clean up circular reference
del space
"""


class DBAppEventCallBacksTest( TestCase ):
	
	
	name = "DBAppEventCallBacks"
	description = "Tests the ability to define callbacks on dbapp"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

		
	def runTest( self ):
		def addCallBackScripts( input, output ):
			output.write( input.read() )
			output.write( "\n" )
			output.write( callBackScript )
		self.cc.mangleResTreeFile( "scripts/db/BWPersonality.py",
									addCallBackScripts )
		
		self.cc.start()
		self.cc.waitForServerSettle()
		checkLog( self, "onInit",  "\( \(False,\), \{\} \)", 1 )
		checkLog( self, "onAppReady", "\( \(\), \{\} \)", 1 )
		checkLog( self, "onDBAppReady", "\( \(\), \{\} \)", 1 )
		
		self.cc.stop()
		checkLog( self, "onFini", "\( \(\), \{\} \)", 1 )
		
		