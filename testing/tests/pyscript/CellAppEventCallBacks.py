import time 
from bwtest import TestCase
from helpers.cluster import ClusterController
from helpers.timer import runTimer
from primitives import locallog
from test_common import *


callBackScript = """
# Log FantasyDemo event callbacks and event listener callbacks
import sys
import functools
space = sys.modules[ __name__ ]

from bwdebug import *

def _hookEvents():
    for cbName in [
        'onAllSpaceGeometryLoaded',
        'onAppReady',
        'onAppShuttingDown',
        'onBaseAppDeath',
        'onCellAppData',
        'onCellAppReady',
        'onCellAppShuttingDown',
        'onDelCellAppData',
        'onDelGlobalData',
        'onGlobalData',
        'onServiceAppDeath',
        'onSpaceData',
        'onSpaceGeometryLoaded',
        'onRecordingStarted',
        'onRecordingTickData',
        'onRecordingStopped',
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


class CellAppEventCallBacksTest( TestCase ):
	
	
	name = "CellAppEventCallBacks"
	description = "Tests the ability to define callbacks on cellapps"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "debugging/shouldLoadBalance", "False" )
		self.cc.setConfig( "debugging/shouldMetaLoadBalance", "False" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def countTicks( self ):
		output = locallog.grepLastServerLog( 
					"personalityCallback: Event: simple_space.onRecordingTickData" )
		return len( output.split( "\n" ) )

		
	def runTest( self ):
		def addCallBackScripts( input, output ):
			output.write( input.read() )
			output.write( "\n" )
			output.write( callBackScript )
		self.cc.mangleResTreeFile( "scripts/cell/BWPersonality.py",
									addCallBackScripts )
		self.cc.start()
		self.cc.startProc( "baseapp", 1 )
		self.cc.startProc( "cellapp", 1 )
		self.cc.startProc( "serviceapp", 1 )
		checkLog( self, "onInit",  "\( \(False,\), \{\} \)", 2 )
		checkLog( self, "onSpaceGeometryLoaded", "\( \(2, 'main'\), \{\} \)", 1)
		checkLog( self, "onAllSpaceGeometryLoaded", "\( \(2, 1, 'spaces/main'\), \{\} \)", 1)
		
		snippet = """
		BigWorld.cellAppData["CellAppDataKey"]="CellAppDataValue"
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		checkLog( self, "onCellAppData", "\( \('CellAppDataKey', 'CellAppDataValue'\), \{\} \)", 2 )
		
		snippet = """
		del BigWorld.cellAppData["CellAppDataKey"]
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		checkLog( self, "onDelCellAppData", "\( \('CellAppDataKey',\), \{\} \)", 2)
		
		snippet = """
		BigWorld.globalData["GlobalDataKey"]="GlobalDataValue"
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		checkLog( self, "onGlobalData", "\( \('GlobalDataKey', 'GlobalDataValue'\), \{\} \)", 2 )
		
		snippet = """
		del BigWorld.globalData["GlobalDataKey"]
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		checkLog( self, "onDelGlobalData", "\( \('GlobalDataKey',\), \{\} \)", 2 )
		
		snippet = """
		BigWorld.setSpaceData( 2, 32000, "SpaceData 32000 in space 2" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		checkLog( self, "onSpaceData", "\( \(2, \([0-9]+, [0-9]+\), 32000, 'SpaceData 32000 in space 2'\), \{\} \)", 1 )
		
		snippet = """
		BigWorld.startRecording( 2, 'ServerScriptTest.replay', False )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		time.sleep( 1 )
		checkLog( self, "onRecordingStarted", "\( \(2, 'ServerScriptTest.replay'\), \{\} \)", 1 )
		count = self.countTicks()
		time.sleep( 5 )
		count2 = self.countTicks()
		self.assertTrue( count2 > count,
						"onRecordingTickData are not happening" )
		
		snippet = """
		BigWorld.stopRecording( 2 )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		checkLog( self, "onRecordingStopped", "\( \(2, 'ServerScriptTest.replay'\), \{\} \)", 1 )
		count = self.countTicks()
		time.sleep( 5 )
		count2 = self.countTicks()
		self.assertTrue( count2 == count,
						"onRecordingTickData are happening after stopped recording" )
		
		self.cc.retireProc( "serviceapp", 1 )
		runTimer( self.cc.findProc, lambda res: res == None, 
				procType = "serviceapp", procOrd = "01" )
		checkLog( self, "onServiceAppDeath", "\( \(\('[0-9\.:]+', [0-9]+\),\), \{\} \)", 2 )
		
		self.cc.retireProc( "baseapp", 1 )
		runTimer( self.cc.findProc, lambda res: res == None, 
				procType = "baseapp", procOrd = "01" )
		checkLog( self, "onBaseAppDeath", "\( \(\('[0-9\.:]+', [0-9]+\),\), \{\} \)", 2 )
		
		self.cc.stop()
		checkLog( self, "onAppShuttingDown", "\( \([0-9\.]+,\), \{\} \)", 2 )
		checkLog( self,  "onCellAppShuttingDown", "\( \([0-9\.]+,\), \{\} \)", 2 )
		checkLog( self, "onFini", "\( \(\), \{\} \)", 2 )
		
		