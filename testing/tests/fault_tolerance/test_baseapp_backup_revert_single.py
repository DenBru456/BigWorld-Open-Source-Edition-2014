from bwtest import config
from bwtest import log
from bwtest import TestCase

from helpers.cluster import ClusterController
from helpers.timer import runTimer
import time

from template_reader import TemplateReader

class TestBaseAppBackupRevertSingle( TestCase ):
    
    name = "Test BaseApp Backup upon reversion to single machine config"
    description = """
	This test addresses issue BWT-24757. 
	This test will start in a multi-machine BaseApp backup configuration 
	and will then revert to a single-machine BaseApp backup configuration
	and test that it works as expected.
	"""
    
    tags = []
    
    ARCHIVE_PERIOD = 15
    NEEDED_CONFIGS = {"baseApp/archivePeriod": str( ARCHIVE_PERIOD )}
    RES_PATH = "simple_space/res"

    def setUp( self ):
        self._cc = ClusterController( self.RES_PATH )
        for path, value in self.NEEDED_CONFIGS.items():
            self._cc.setConfig( path, value )

    def tearDown( self ):
        self._cc.stop()
        self._cc.clean()

    def startCluster( self ):

        xmlPath = config.TEST_ROOT + \
        		"/tests/fault_tolerance/base_revert_single_layout.xml"
        self.assertTrue( len(self._cc._machines) == 2,
             "You need to define 2 machines in user_config.xml for this test" )
        
        layoutXML = TemplateReader( xmlPath, machine1=self._cc._machines[0],
                                  machine2=self._cc._machines[1] )
        
        self._cc.start( layoutXML )

    def runTest( self ):
        
        self.startCluster()
        
        createEntitySnippet = """
		import random
		for x in range ( 0, 100 ):
			e = BigWorld.createBaseAnywhere( \
				"PersistentEntity", spaceID = 2, position = ( 0, 0, 0 ) )
		srvtest.finish()
		"""
        for x in range( 1, 5):
            self._cc.sendAndCallOnApp( "baseapp", x, createEntitySnippet )
        
        # We need to sleep long enough for the server to fully
        # load entities and spaces
        log.progress( "Sleeping for archive period * 2 value of: %d",
                      self.ARCHIVE_PERIOD * 2 )
        time.sleep( self.ARCHIVE_PERIOD * 2 )
        
        procs = self._cc.findProcsByMachine( "baseapp", self._cc._machines[0] )
        
        log.debug( "Number of procs returned is: %d", len( procs ) )
        
        baseAppID = "%02d" % procs[0].id
        
        log.progress( "Retiring BaseApp%s on %s",
                baseAppID, procs[0].machine.name )
                
        procs[0].retireApp()
        
        log.progress( "Checking if BaseApp%s has retired", baseAppID )
        
        # We want to keep checking to see if the app retired.
        runTimer( self._cc.findProc, lambda result: result == None,
						timeout = 40, procType = "baseapp", 
						procOrd = baseAppID )
        
        log.progress( "Retiring a second BaseApp" )
        
        procs = self._cc.findProcsByMachine( "baseapp", self._cc._machines[1] )
        
        baseAppID = "%02d" % procs[0].id
        
        log.progress( "Retiring BaseApp%s on %s",
                baseAppID, procs[0].machine.name )
        
        procs[0].retireApp()
        
        log.progress( "Checking if BaseApp%s has retired", baseAppID )
        # We want to keep checking to see if the app retired.
        try:
            runTimer( self._cc.findProc, lambda result: result == None, 
							timeout = 40, procType = "baseapp", 
							procOrd = baseAppID )
        except:
            self.fail( ( "BaseApp%s would not retire!",
                       baseAppID ) )
