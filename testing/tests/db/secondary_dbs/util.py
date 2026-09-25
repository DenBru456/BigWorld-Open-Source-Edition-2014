import os

import bwtest
from helpers.cluster import ClusterController
import xmlconf

from bwtest import config, log
from primitives import mysql


class TestBase( object ):

	BACKUP_PERIOD = 5
	ARCHIVE_PERIOD = 5


	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.setConfig( "db/secondaryDB/enable", "true" )
		self._cc.setConfig( "baseApp/archivePeriod", str( self.ARCHIVE_PERIOD ) )
		self._cc.setConfig( "baseApp/backupPeriod", str( self.BACKUP_PERIOD ) )

		self._cc.cleanSecondaryDBs();

		self._cc.start()


	def tearDown( self ):
		self._cc.stop()

		self._cc.clean()

