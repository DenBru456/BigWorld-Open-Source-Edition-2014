from bwtest import TestCase
from bwtest import config
from bwtest import log

from helpers.cluster import ClusterController
import time

class TestGetWatcherDir( TestCase ):
    
    name = "getWatcherDir Test"
    description = """
    Test that calling getWatcherDir doesn't cause a CellApp crash.
    See BWT-21406 for the issue that spawned this test.
    """
    
    RES_PATH = "simple_space/res"
    
    tags = []
    
    def setUp( self ):
        self._cc = ClusterController( self.RES_PATH )
        self._cc.start()
        self._cc.waitForServerSettle()
        
    def tearDown( self ):
        self._cc.stop()
        self._cc.clean()
    
    def runTest( self ):
        
        watcherCheckSnippet = """
e = BigWorld.createEntity( "PersistentEntity", 2, ( 0, 0, 0 ), ( 0, 0, 0 ))
id = e.id
watcherPath = "entities/" + str(id) + "/properties"
BigWorld.getWatcherDir( watcherPath )
srvtest.finish()
"""    
        log.progress( "Running getWatcherDir snippet on CellApp01 ")
        result = self._cc.sendAndCallOnApp( "cellapp", 1, watcherCheckSnippet )
        
        time.sleep( 10 )
        
        self.assertNotEqual( self._cc.findProc( "cellapp", "01" ), None,
                         "CellApp has gone down after using getWatcherDir")