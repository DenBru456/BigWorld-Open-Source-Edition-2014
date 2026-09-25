from bwtest import TestCase
from helpers.cluster import ClusterController
from helpers.timer import runTimer
from test_common import *

callBackScript = """
# Log event callbacks and event listener callbacks
import sys
import functools
space = sys.modules[ __name__ ]

from bwdebug import *

def _hookEvents():
    for cbName in [
        'onAppReady',
        'onAppShutDown',
        'onBaseAppData',
        'onBaseAppDeath',
        'onCellAppDeath',
        'onServiceAppDeath',
        'onDelBaseAppData',
        'onDelGlobalData',
        'onGlobalData',
        'onAppShuttingDown',
        'onInit',
        'onFini',
    ] + [ cb for cb in [
        'onBaseAppReady',
        'onBaseAppShuttingDown',
        'onBaseAppShutDown'
    ] if BigWorld.component == "base" ] + [ cb for cb in [
        'onServiceAppReady',
        'onServiceAppShuttingDown',
        'onServiceAppShutDown'
    ] if BigWorld.component == "service" ]:
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

class BaseAppEventCallBacksTest( TestCase ):
	
	
	name = "BaseAppEventCallBacks"
	description = "Tests the ability to define callbacks on baseapps and serviceapps"
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
		self.cc.mangleResTreeFile( "scripts/base/BWPersonality.py",
									addCallBackScripts )
		self.cc.mangleResTreeFile( "scripts/service/BWPersonality.py",
									addCallBackScripts )
		
		self.cc.start()
		self.cc.startProc( "baseapp", 1 )
		self.cc.startProc( "cellapp", 1 )
		self.cc.startProc( "serviceapp", 1 )

		checkLog( self, "onInit",  "\( \(False,\), \{\} \)", 4 )
		checkLog( self, "onAppReady", "\( \(True, False\), \{\} \)", 1 )
		checkLog( self, "onAppReady",  "\( \(False, False\), \{\} \)", 3 )
		checkLog( self, "onBaseAppReady", "\( \(True, False\), \{\} \)", 1 )
		checkLog( self, "onBaseAppReady", "\( \(False, False\), \{\} \)", 1 )
		checkLog( self, "onServiceAppReady", "\( \(False, False\), \{\} \)", 2 )
		
		snippet = """
		BigWorld.baseAppData["BaseAppDataKey"]="BaseAppDataValue"
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		checkLog( self, "onBaseAppData", "\( \('BaseAppDataKey', 'BaseAppDataValue'\), \{\} \)", 4 )
		
		snippet = """
		del BigWorld.baseAppData["BaseAppDataKey"]
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		checkLog( self, "onDelBaseAppData", "\( \('BaseAppDataKey',\), \{\} \)", 4)
		
		snippet = """
		BigWorld.globalData["GlobalDataKey"]="GlobalDataValue"
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		checkLog( self, "onGlobalData", "\( \('GlobalDataKey', 'GlobalDataValue'\), \{\} \)", 4 )
		
		snippet = """
		del BigWorld.globalData["GlobalDataKey"]
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		checkLog( self, "onDelGlobalData", "\( \('GlobalDataKey',\), \{\} \)", 4)
		
		self.cc.retireProc( "cellapp", 1 )
		runTimer( self.cc.findProc, lambda res: res == None, 
				procType = "cellapp", procOrd = "01" )
		checkLog( self, "onCellAppDeath", "\( \('[0-9\.:]+',\), \{\} \)", 4 )
		
		self.cc.retireProc( "serviceapp", 1 )
		runTimer( self.cc.findProc, lambda res: res == None, 
				procType = "serviceapp", procOrd = "01" )
		checkLog( self, "onFini", "\( \(\), \{\} \)", 1 )
		checkLog( self, "onServiceAppDeath", "\( \(\('[0-9\.:]+', [0-9]+\),\), \{\} \)", 3 )
		
		self.cc.retireProc( "baseapp", 1 )
		runTimer( self.cc.findProc, lambda res: res == None, 
				procType = "baseapp", procOrd = "01" )
		checkLog( self, "onFini", "\( \(\), \{\} \)", 2 )
		checkLog( self, "onBaseAppDeath", "\( \(\('[0-9\.:]+', [0-9]+\),\), \{\} \)", 2 )
		
		self.cc.stop()
		checkLog( self, "onAppShuttingDown", "\( \([0-9\.]+,\), \{\} \)", 2 )
		checkLog( self,  "onBaseAppShuttingDown", "\( \([0-9\.]+,\), \{\} \)", 1 )
		checkLog( self,  "onServiceAppShuttingDown", "\( \([0-9\.]+,\), \{\} \)", 1 )
		checkLog( self, "onAppShutDown", "\( \([0-2],\), \{\} \)", 6 )
		checkLog( self, "onBaseAppShutDown", "\( \([0-2],\), \{\} \)", 3 )
		checkLog( self, "onServiceAppShutDown", "\( \([0-2],\), \{\} \)", 3 )
		checkLog( self, "onFini", "\( \(\), \{\} \)", 4 )
		
		
		
		
		